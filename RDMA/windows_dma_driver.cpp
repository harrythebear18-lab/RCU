/*
 * Windows DMA Driver - Ultra-Low-Latency Virtual DMA for Windows
 * 
 * Windows kernel driver providing the same functionality as the Linux version
 * with Windows-specific optimizations and compatibility
 */

#include <ntddk.h>
#include <wdf.h>
#include <wdm.h>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <mstcpip.h>
#include <ipexport.h>
#include <iphlpapi.h>
#include <netioapi.h>

#define DRIVER_NAME L"WindowsDMA"
#define DRIVER_VERSION "2.0"

// Windows-specific constants
#define DMA_TAG 'WMDA'
#define MAX_REGIONS 16
#define RING_BUFFER_SIZE 8192
#define MAX_PACKET_SIZE 1514

// Windows network optimization flags
#define TCP_OFFLOAD_SEND 0x00000001
#define TCP_OFFLOAD_RECV 0x00000002
#define UDP_OFFLOAD_SEND 0x00000004
#define UDP_OFFLOAD_RECV 0x00000008

// Lock-free ring buffer structure
typedef struct _LOCKFREE_RING {
    volatile ULONG Head;
    volatile ULONG Tail;
    ULONG Size;
    ULONG Mask;
    ULONG ItemSize;
    PUCHAR Buffer;
} LOCKFREE_RING, *PLOCKFREE_RING;

// DMA region structure for Windows
typedef struct _WINDOWS_DMA_REGION {
    ULONG StartAddress;
    ULONG Size;
    PVOID UserVirtualAddress;
    PHYSICAL_ADDRESS PhysicalAddress;
    LOCKFREE_RING TxRing;
    LOCKFREE_RING RxRing;
    PMDL Mdl;
    BOOLEAN Active;
    volatile LONG64 BytesTransferred;
    volatile LONG64 PacketsSent;
    volatile LONG PendingOperations;
    KSPIN_LOCK Lock;
} WINDOWS_DMA_REGION, *PWINDOWS_DMA_REGION;

// Network bypass structure for Windows
typedef struct _WINDOWS_NET_BYPASS {
    SOCKET RawSocket;
    UCHAR SourceMac[6];
    UCHAR DestMac[6];
    ULONG SourceIp;
    ULONG DestIp;
    USHORT SourcePort;
    USHORT DestPort;
    WSABUF DataBuffer;
    WSAOVERLAPPED Overlapped;
    HANDLE IoCompletionPort;
    BOOLEAN UseOffload;
} WINDOWS_NET_BYPASS, *PWINDOWS_NET_BYPASS;

// Windows DMA device structure
typedef struct _WINDOWS_DMA_DEVICE {
    WDFDEVICE Device;
    WINDOWS_DMA_REGION Regions[MAX_REGIONS];
    ULONG NumRegions;
    WINDOWS_NET_BYPASS NetBypass;
    
    // Performance counters
    volatile LONG64 TotalBytes;
    volatile LONG64 TotalPackets;
    volatile LONG64 DroppedPackets;
    volatile LONG64 LatencySum;
    volatile LONG64 LatencyCount;
    
    // Worker threads
    HANDLE TxThreads[MAX_REGIONS];
    HANDLE RxThread;
    HANDLE StatsThread;
    
    // CPU affinity and scheduling
    GROUP_AFFINITY CpuAffinity;
    BOOLEAN UseRealTimePriority;
    
    // Synchronization
    KSPIN_LOCK StatsLock;
    ERESOURCE RegionsLock;
    
    // Configuration
    BOOLEAN EnableHardwareTimestamp;
    BOOLEAN EnableKernelBypass;
    ULONG TimeoutMs;
} WINDOWS_DMA_DEVICE, *PWINDOWS_DMA_DEVICE;

// Function prototypes
DRIVER_INITIALIZE DriverEntry;
EVT_WDF_DRIVER_DEVICE_ADD WindowsDMADeviceAdd;
EVT_WDF_OBJECT_CONTEXT_CLEANUP WindowsDMADeviceCleanup;
VOID WindowsDMADriverUnload(PDRIVER_OBJECT DriverObject);
NTSTATUS WindowsDMACreateDevice(WDFDRIVER Driver, PWDFDEVICE_INIT DeviceInit);
NTSTATUS WindowsDMAQueueInitialize(WDFDEVICE Device);
VOID WindowsDMATxWorkerThread(PVOID Context);
VOID WindowsDMARxWorkerThread(PVOID Context);
VOID WindowsDMAStatsWorkerThread(PVOID Context);
BOOLEAN WindowsDMAInitializeNetworkBypass(PWINDOWS_DMA_DEVICE Device);
VOID WindowsDMACleanupNetworkBypass(PWINDOWS_DMA_DEVICE Device);
ULONG64 WindowsDMAGetRDTSC(void);
NTSTATUS WindowsDMASetThreadAffinity(HANDLE Thread, GROUP_AFFINITY Affinity);
NTSTATUS WindowsDMASetRealTimePriority(HANDLE Thread);

// Lock-free ring buffer operations
__forceinline BOOLEAN WindowsDMALockFreeRingPush(PLOCKFREE_RING Ring, PVOID Item)
{
    ULONG Head = Ring->Head;
    ULONG NextHead = (Head + 1) & Ring->Mask;
    
    if (NextHead == Ring->Tail) {
        return FALSE; // Ring full
    }
    
    RtlCopyMemory(Ring->Buffer + (Head * Ring->ItemSize), Item, Ring->ItemSize);
    KeMemoryBarrier(); // Write memory barrier
    Ring->Head = NextHead;
    
    return TRUE;
}

__forceinline BOOLEAN WindowsDMALockFreeRingPop(PLOCKFREE_RING Ring, PVOID Item)
{
    ULONG Tail = Ring->Tail;
    
    if (Tail == Ring->Head) {
        return NULL; // Ring empty
    }
    
    RtlCopyMemory(Item, Ring->Buffer + (Tail * Ring->ItemSize), Ring->ItemSize);
    KeMemoryBarrier(); // Read memory barrier
    Ring->Tail = (Tail + 1) & Ring->Mask;
    
    return TRUE;
}

// RDTSC implementation for Windows
__forceinline ULONG64 WindowsDMAGetRDTSC(void)
{
#if defined(_M_X64)
    return __rdtsc();
#else
    ULONG64 result;
    __asm {
        rdtsc
        mov dword ptr [result], eax
        mov dword ptr [result + 4], edx
    }
    return result;
#endif
}

// Set CPU affinity for Windows thread
NTSTATUS WindowsDMASetThreadAffinity(HANDLE Thread, GROUP_AFFINITY Affinity)
{
    return SetThreadGroupAffinity(Thread, &Affinity, NULL) ? STATUS_SUCCESS : STATUS_UNSUCCESSFUL;
}

// Set real-time priority for Windows thread
NTSTATUS WindowsDMASetRealTimePriority(HANDLE Thread)
{
    return SetThreadPriority(Thread, THREAD_PRIORITY_TIME_CRITICAL) ? 
           STATUS_SUCCESS : STATUS_UNSUCCESSFUL;
}

// Initialize network bypass for Windows
BOOLEAN WindowsDMAInitializeNetworkBypass(PWINDOWS_DMA_DEVICE Device)
{
    WSADATA wsaData;
    SOCKADDR_IN addr;
    int optval;
    DWORD bytesReturned;
    
    // Initialize Winsock
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        KdPrint(("WSAStartup failed\n"));
        return FALSE;
    }
    
    // Create raw socket
    Device->NetBypass.RawSocket = socket(AF_INET, SOCK_RAW, IPPROTO_RAW);
    if (Device->NetBypass.RawSocket == INVALID_SOCKET) {
        KdPrint(("Failed to create raw socket\n"));
        WSACleanup();
        return FALSE;
    }
    
    // Enable IP_HDRINCL
    optval = 1;
    if (setsockopt(Device->NetBypass.RawSocket, IPPROTO_IP, IP_HDRINCL, 
                   (char*)&optval, sizeof(optval)) != 0) {
        KdPrint(("Failed to set IP_HDRINCL\n"));
        closesocket(Device->NetBypass.RawSocket);
        WSACleanup();
        return FALSE;
    }
    
    // Set socket to non-blocking mode
    u_long mode = 1; // 1 = non-blocking
    ioctlsocket(Device->NetBypass.RawSocket, FIONBIO, &mode);
    
    // Create I/O completion port
    Device->NetBypass.IoCompletionPort = CreateIoCompletionPort(
        (HANDLE)Device->NetBypass.RawSocket, NULL, 1, 0);
    
    if (Device->NetBypass.IoCompletionPort == NULL) {
        KdPrint(("Failed to create I/O completion port\n"));
        closesocket(Device->NetBypass.RawSocket);
        WSACleanup();
        return FALSE;
    }
    
    // Initialize WSABUF
    Device->NetBypass.DataBuffer.buf = (CHAR*)ExAllocatePoolWithTag(
        NonPagedPool, MAX_PACKET_SIZE, DMA_TAG);
    Device->NetBypass.DataBuffer.len = MAX_PACKET_SIZE;
    
    // Initialize OVERLAPPED
    RtlZeroMemory(&Device->NetBypass.Overlapped, sizeof(OVERLAPPED));
    Device->NetBypass.Overlapped.hEvent = CreateEvent(NULL, FALSE, FALSE, NULL);
    
    // Get network interface information
    PIP_ADAPTER_ADDRESSES pAddresses = NULL;
    ULONG bufferSize = 0;
    
    if (GetAdaptersAddresses(AF_UNSPEC, GAA_FLAG_INCLUDE_GATEWAY, NULL, pAddresses, &bufferSize) == ERROR_BUFFER_OVERFLOW) {
        pAddresses = (PIP_ADAPTER_ADDRESSES)ExAllocatePoolWithTag(NonPagedPool, bufferSize, DMA_TAG);
        if (pAddresses) {
            if (GetAdaptersAddresses(AF_UNSPEC, GAA_FLAG_INCLUDE_GATEWAY, NULL, pAddresses, &bufferSize) == NO_ERROR) {
                // Find first suitable adapter
                PIP_ADAPTER_ADDRESSES pCurrAddresses = pAddresses;
                while (pCurrAddresses) {
                    if (pCurrAddresses->OperStatus == IfOperStatusUp && 
                        pCurrAddresses->PhysicalAddressLength == 6) {
                        
                        // Copy MAC address
                        RtlCopyMemory(Device->NetBypass.SourceMac, 
                                   pCurrAddresses->PhysicalAddress, 6);
                        break;
                    }
                    pCurrAddresses = pCurrAddresses->Next;
                }
            }
            ExFreePoolWithTag(pAddresses, DMA_TAG);
        }
    }
    
    KdPrint(("Windows network bypass initialized\n"));
    return TRUE;
}

// Cleanup network bypass
VOID WindowsDMACleanupNetworkBypass(PWINDOWS_DMA_DEVICE Device)
{
    if (Device->NetBypass.RawSocket != INVALID_SOCKET) {
        closesocket(Device->NetBypass.RawSocket);
    }
    
    if (Device->NetBypass.IoCompletionPort != NULL) {
        CloseHandle(Device->NetBypass.IoCompletionPort);
    }
    
    if (Device->NetBypass.Overlapped.hEvent != NULL) {
        CloseHandle(Device->NetBypass.Overlapped.hEvent);
    }
    
    if (Device->NetBypass.DataBuffer.buf) {
        ExFreePoolWithTag(Device->NetBypass.DataBuffer.buf, DMA_TAG);
    }
    
    WSACleanup();
}

// TX worker thread for Windows
VOID WindowsDMATxWorkerThread(PVOID Context)
{
    PWINDOWS_DMA_REGION Region = (PWINDOWS_DMA_REGION)Context;
    PWINDOWS_DMA_DEVICE Device = (PWINDOWS_DMA_DEVICE)Region->Reserved; // Store device pointer
    
    // Set CPU affinity
    WindowsDMASetThreadAffinity(GetCurrentThread(), Device->CpuAffinity);
    
    // Set real-time priority
    WindowsDMASetRealTimePriority(GetCurrentThread());
    
    KdPrint(("Windows DMA TX worker thread started\n"));
    
    while (TRUE) {
        // Check for packets to send
        PVOID packetData = ExAllocatePoolWithTag(NonPagedPool, Region->TxRing.ItemSize, DMA_TAG);
        if (packetData && WindowsDMALockFreeRingPop(&Region->TxRing, packetData)) {
            ULONG64 startTime = WindowsDMAGetRDTSC();
            
            // Build Ethernet frame
            PUCHAR ethernetFrame = (PUCHAR)Device->NetBypass.DataBuffer.buf;
            
            // Ethernet header
            RtlCopyMemory(ethernetFrame, Device->NetBypass.DestMac, 6);
            RtlCopyMemory(ethernetFrame + 6, Device->NetBypass.SourceMac, 6);
            *(USHORT*)(ethernetFrame + 12) = htons(0x0800); // IP protocol
            
            // IP header (simplified)
            ethernetFrame[14] = 0x45; // Version + IHL
            ethernetFrame[15] = 0x00; // Type of Service
            *(USHORT*)(ethernetFrame + 16) = htons(28 + Region->TxRing.ItemSize); // Total length
            *(USHORT*)(ethernetFrame + 20) = htons(0x4000); // Flags + Fragment offset
            ethernetFrame[22] = 64; // TTL
            ethernetFrame[23] = IPPROTO_UDP; // Protocol
            *(ULONG*)(ethernetFrame + 26) = Device->NetBypass.SourceIp;
            *(ULONG*)(ethernetFrame + 30) = Device->NetBypass.DestIp;
            
            // UDP header
            *(USHORT*)(ethernetFrame + 34) = htons(Device->NetBypass.SourcePort);
            *(USHORT*)(ethernetFrame + 36) = htons(Device->NetBypass.DestPort);
            *(USHORT*)(ethernetFrame + 38) = htons(8 + Region->TxRing.ItemSize); // UDP length
            
            // Copy data
            RtlCopyMemory(ethernetFrame + 42, packetData, Region->TxRing.ItemSize);
            
            // Send via raw socket
            DWORD bytesSent;
            if (WSASend(Device->NetBypass.RawSocket, &Device->NetBypass.DataBuffer, 1, 
                       &bytesSent, 0, NULL, NULL) == 0) {
                
                ULONG64 endTime = WindowsDMAGetRDTSC();
                
                // Update statistics
                InterlockedAdd64(&Region->PacketsSent, 1);
                InterlockedAdd64(&Region->BytesTransferred, Region->TxRing.ItemSize);
                InterlockedAdd64(&Device->TotalPackets, 1);
                InterlockedAdd64(&Device->TotalBytes, Region->TxRing.ItemSize);
                InterlockedAdd64(&Device->LatencySum, endTime - startTime);
                InterlockedAdd64(&Device->LatencyCount, 1);
            }
            
            ExFreePoolWithTag(packetData, DMA_TAG);
        } else {
            if (packetData) {
                ExFreePoolWithTag(packetData, DMA_TAG);
            }
            // No packets, wait briefly
            LARGE_INTEGER interval;
            interval.QuadPart = -10000; // 1ms
            KeDelayExecutionThread(KernelMode, FALSE, &interval);
        }
    }
}

// RX worker thread for Windows
VOID WindowsDMARxWorkerThread(PVOID Context)
{
    PWINDOWS_DMA_DEVICE Device = (PWINDOWS_DMA_DEVICE)Context;
    
    // Set CPU affinity
    WindowsDMASetThreadAffinity(GetCurrentThread(), Device->CpuAffinity);
    
    // Set real-time priority
    WindowsDMASetRealTimePriority(GetCurrentThread());
    
    KdPrint(("Windows DMA RX worker thread started\n"));
    
    while (TRUE) {
        DWORD bytesReceived;
        DWORD flags = 0;
        
        // Receive packet
        if (WSARecv(Device->NetBypass.RawSocket, &Device->NetBypass.DataBuffer, 1, 
                    &bytesReceived, &flags, &Device->NetBypass.Overlapped, NULL) == 0) {
            
            if (bytesReceived > 0) {
                // Process received packet
                // Parse headers and write to appropriate memory region
                
                InterlockedAdd64(&Device->TotalPackets, 1);
                InterlockedAdd64(&Device->TotalBytes, bytesReceived);
            }
        } else {
            // No packet, wait briefly
            LARGE_INTEGER interval;
            interval.QuadPart = -10000; // 1ms
            KeDelayExecutionThread(KernelMode, FALSE, &interval);
        }
    }
}

// Stats worker thread for Windows
VOID WindowsDMAStatsWorkerThread(PVOID Context)
{
    PWINDOWS_DMA_DEVICE Device = (PWINDOWS_DMA_DEVICE)Context;
    
    KdPrint(("Windows DMA stats worker thread started\n"));
    
    while (TRUE) {
        LARGE_INTEGER interval;
        interval.QuadPart = -10000000; // 1 second
        KeDelayExecutionThread(KernelMode, FALSE, &interval);
        
        // Update statistics (could be exported to userspace)
        LONG64 totalBytes = InterlockedCompareExchange64(&Device->TotalBytes, 0, 0);
        LONG64 totalPackets = InterlockedCompareExchange64(&Device->TotalPackets, 0, 0);
        
        // Log statistics (debug mode only)
        KdPrint(("DMA Stats: %lld bytes, %lld packets\n", totalBytes, totalPackets));
    }
}

// Windows DMA device add
NTSTATUS WindowsDMADeviceAdd(WDFDRIVER Driver, PWDFDEVICE_INIT DeviceInit)
{
    UNREFERENCED_PARAMETER(Driver);
    NTSTATUS status;
    WDFDEVICE device;
    PWINDOWS_DMA_DEVICE deviceContext;
    
    KdPrint(("WindowsDMADeviceAdd called\n"));
    
    // Create device
    status = WindowsDMACreateDevice(Driver, DeviceInit);
    if (!NT_SUCCESS(status)) {
        KdPrint(("WindowsDMACreateDevice failed: 0x%x\n", status));
        return status;
    }
    
    // Create device
    status = WdfDeviceCreate(&DeviceInit, WDF_NO_OBJECT_ATTRIBUTES, 
                           &WINDOWS_DMA_DEVICE_CONFIG, &device);
    if (!NT_SUCCESS(status)) {
        KdPrint(("WdfDeviceCreate failed: 0x%x\n", status));
        return status;
    }
    
    // Get device context
    deviceContext = WindowsDMAGetDeviceContext(device);
    
    // Initialize device context
    RtlZeroMemory(deviceContext, sizeof(WINDOWS_DMA_DEVICE));
    deviceContext->Device = device;
    
    // Initialize locks
    KeInitializeSpinLock(&deviceContext->StatsLock);
    ExInitializeResourceLite(&deviceContext->RegionsLock);
    
    // Set CPU affinity (use first 4 cores)
    RtlZeroMemory(&deviceContext->CpuAffinity, sizeof(GROUP_AFFINITY));
    deviceContext->CpuAffinity.Group = 0;
    deviceContext->CpuAffinity.Mask = 0xF; // First 4 CPUs
    
    // Initialize network bypass
    if (!WindowsDMAInitializeNetworkBypass(deviceContext)) {
        KdPrint(("Failed to initialize network bypass\n"));
    }
    
    // Start worker threads
    for (ULONG i = 0; i < MAX_REGIONS; i++) {
        deviceContext->TxThreads[i] = NULL;
    }
    deviceContext->RxThread = NULL;
    deviceContext->StatsThread = NULL;
    
    KdPrint(("Windows DMA device added successfully\n"));
    return STATUS_SUCCESS;
}

// Windows DMA device cleanup
VOID WindowsDMADeviceCleanup(WDFOBJECT Object)
{
    PWINDOWS_DMA_DEVICE deviceContext = WindowsDMAGetDeviceContext(Object);
    
    KdPrint(("WindowsDMADeviceCleanup called\n"));
    
    // Stop worker threads
    if (deviceContext->StatsThread) {
        TerminateThread(deviceContext->StatsThread, 0);
        CloseHandle(deviceContext->StatsThread);
    }
    
    if (deviceContext->RxThread) {
        TerminateThread(deviceContext->RxThread, 0);
        CloseHandle(deviceContext->RxThread);
    }
    
    for (ULONG i = 0; i < MAX_REGIONS; i++) {
        if (deviceContext->TxThreads[i]) {
            TerminateThread(deviceContext->TxThreads[i], 0);
            CloseHandle(deviceContext->TxThreads[i]);
        }
    }
    
    // Cleanup network bypass
    WindowsDMACleanupNetworkBypass(deviceContext);
    
    // Cleanup memory regions
    for (ULONG i = 0; i < deviceContext->NumRegions; i++) {
        PWINDOWS_DMA_REGION region = &deviceContext->Regions[i];
        if (region->Active) {
            if (region->Mdl) {
                IoFreeMdl(region->Mdl);
            }
            if (region->UserVirtualAddress) {
                MmFreePagesFromMdl(region->Mdl);
            }
            region->Active = FALSE;
        }
    }
    
    // Cleanup resources
    ExDeleteResourceLite(&deviceContext->RegionsLock);
}

// Create Windows DMA device
NTSTATUS WindowsDMACreateDevice(WDFDRIVER Driver, PWDFDEVICE_INIT DeviceInit)
{
    NTSTATUS status;
    WDF_OBJECT_ATTRIBUTES deviceAttributes;
    
    UNREFERENCED_PARAMETER(Driver);
    
    WDF_OBJECT_ATTRIBUTES_INIT_CONTEXT_TYPE(&deviceAttributes, WINDOWS_DMA_DEVICE);
    
    status = WdfDeviceCreate(&DeviceInit, &deviceAttributes, 
                           &WINDOWS_DMA_DEVICE_CONFIG, WDF_NO_HANDLE);
    
    return status;
}

// Driver entry point
NTSTATUS DriverEntry(PDRIVER_OBJECT DriverObject, PUNICODE_STRING RegistryPath)
{
    NTSTATUS status;
    WDF_DRIVER_CONFIG config;
    
    KdPrint(("Windows DMA Driver Entry - Version %s\n", DRIVER_VERSION));
    
    // Initialize driver config
    WDF_DRIVER_CONFIG_INIT(&config, WindowsDMADeviceAdd);
    
    // Set cleanup callback
    config.DriverPoolTag = DMA_TAG;
    
    // Create WDF driver
    status = WdfDriverCreate(DriverObject, RegistryPath, WDF_NO_OBJECT_ATTRIBUTES, 
                           &config, WDF_NO_HANDLE);
    
    if (!NT_SUCCESS(status)) {
        KdPrint(("WdfDriverCreate failed: 0x%x\n", status));
        return status;
    }
    
    // Set driver unload routine
    DriverObject->DriverUnload = WindowsDMADriverUnload;
    
    KdPrint(("Windows DMA Driver loaded successfully\n"));
    return STATUS_SUCCESS;
}

// Driver unload
VOID WindowsDMADriverUnload(PDRIVER_OBJECT DriverObject)
{
    KdPrint(("Windows DMA Driver Unload\n"));
    
    UNREFERENCED_PARAMETER(DriverObject);
    
    // Cleanup will be handled by WDF cleanup callbacks
}

// Windows DMA device context type definition
WDF_DECLARE_CONTEXT_TYPE_WITH_NAME(WINDOWS_DMA_DEVICE, WindowsDMAGetDeviceContext)
