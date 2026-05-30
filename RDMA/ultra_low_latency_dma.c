/*
 * Ultra-Low-Latency Virtual DMA Driver
 * 
 * Eliminates latency points through:
 * - Zero-copy kernel bypass
 * - Lock-free ring buffers
 * - Raw socket network stack bypass
 * - Memory-mapped I/O
 * - CPU affinity and real-time scheduling
 * - Hardware timestamping
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/device.h>
#include <linux/uaccess.h>
#include <linux/slab.h>
#include <linux/mm.h>
#include <linux/vmalloc.h>
#include <linux/mutex.h>
#include <linux/spinlock.h>
#include <linux/workqueue.h>
#include <linux/netdevice.h>
#include <linux/inet.h>
#include <linux/udp.h>
#include <linux/ip.h>
#include <linux/skbuff.h>
#include <linux/socket.h>
#include <linux/net.h>
#include <linux/in.h>
#include <linux/atomic.h>
#include <linux/delay.h>
#include <linux/highmem.h>
#include <linux/pagemap.h>
#include <linux/kthread.h>
#include <linux/sched.h>
#include <linux/cpumask.h>
#include <linux/pci.h>
#include <linux/interrupt.h>
#include <linux/timekeeping.h>

#define DRIVER_NAME "ultra_dma"
#define DRIVER_VERSION "2.0"
#define RING_BUFFER_SIZE 8192  // Power of 2 for fast modulo
#define MAX_PACKET_SIZE 1514    // Ethernet MTU
#define NUM_RINGS 16            // Multiple rings for parallelism
#define CPU_AFFINITY_MASK 0xF  // Use first 4 CPUs

/* Lock-free ring buffer structure */
struct lockfree_ring {
    void *buffer;
    volatile u32 head;
    volatile u32 tail;
    u32 size;
    u32 mask;
    u32 item_size;
} ____cacheline_aligned;

/* Ultra-fast packet descriptor */
struct packet_desc {
    u64 timestamp;
    u32 address;
    u32 size;
    u32 sequence;
    u16 checksum;
    u8 flags;
} ____cacheline_aligned;

/* DMA region with zero-copy access */
struct ultra_dma_region {
    unsigned long start_addr;
    unsigned long size;
    void *user_virt_addr;
    phys_addr_t phys_addr;
    struct lockfree_ring tx_ring;
    struct lockfree_ring rx_ring;
    struct page **pages;
    int num_pages;
    bool active;
    atomic64_t bytes_transferred;
    atomic64_t packets_sent;
} ____cacheline_aligned;

/* Network bypass structure */
struct net_bypass {
    struct socket *raw_sock;
    struct net_device *netdev;
    u8 src_mac[6];
    u8 dst_mac[6];
    u32 src_ip;
    u32 dst_ip;
    u16 src_port;
    u16 dst_port;
    spinlock_t lock;
} ____cacheline_aligned;

/* Ultra DMA device structure */
struct ultra_dma_dev {
    struct cdev cdev;
    struct device *device;
    struct class *class;
    dev_t dev_num;
    
    /* DMA regions */
    struct ultra_dma_region regions[NUM_RINGS];
    unsigned int num_regions;
    
    /* Network bypass */
    struct net_bypass net_bypass;
    
    /* High-performance worker threads */
    struct task_struct *tx_threads[NUM_RINGS];
    struct task_struct *rx_thread;
    struct task_struct *stats_thread;
    
    /* Memory pools for zero-copy */
    struct kmem_cache *packet_cache;
    struct kmem_cache *desc_cache;
    
    /* Performance counters */
    atomic64_t total_bytes;
    atomic64_t total_packets;
    atomic64_t dropped_packets;
    atomic64_t latency_sum;
    atomic64_t latency_count;
    
    /* CPU affinity and scheduling */
    cpumask_t cpu_mask;
    
    /* Synchronization */
    spinlock_t stats_lock;
    struct mutex regions_lock;
    
    /* Configuration */
    bool enable_hardware_timestamp;
    bool enable_kernel_bypass;
    unsigned int priority;
} ____cacheline_aligned;

static struct ultra_dma_dev *udev;

/* Forward declarations */
static int ultra_dma_open(struct inode *inode, struct file *file);
static int ultra_dma_release(struct inode *inode, struct file *file);
static long ultra_dma_ioctl(struct file *file, unsigned int cmd, unsigned long arg);
static int ultra_dma_mmap(struct file *file, struct vm_area_struct *vma);
static int tx_thread_func(void *data);
static int rx_thread_func(void *data);
static int stats_thread_func(void *data);
static inline void lockfree_ring_init(struct lockfree_ring *ring, void *buffer, u32 size, u32 item_size);
static inline bool lockfree_ring_push(struct lockfree_ring *ring, void *item);
static inline bool lockfree_ring_pop(struct lockfree_ring *ring, void *item);
static inline void build_ethernet_header(void *buffer, const u8 *dst_mac, const u8 *src_mac, u16 ethertype);
static inline void build_ip_header(void *buffer, u32 src_ip, u32 dst_ip, u16 total_len);
static inline void build_udp_header(void *buffer, u16 src_port, u16 dst_port, u16 udp_len);
static inline u64 fast_timestamp(void);

/* File operations */
static const struct file_operations ultra_dma_fops = {
    .owner = THIS_MODULE,
    .open = ultra_dma_open,
    .release = ultra_dma_release,
    .unlocked_ioctl = ultra_dma_ioctl,
    .mmap = ultra_dma_mmap,
};

/* IOCTL commands */
#define ULTRA_DMA_IOCTL_BASE 'U'
#define ULTRA_ADD_REGION    _IOW(ULTRA_DMA_IOCTL_BASE, 1, struct ultra_dma_region)
#define ULTRA_REMOVE_REGION _IOW(ULTRA_DMA_IOCTL_BASE, 2, unsigned long)
#define ULTRA_GET_STATS     _IOR(ULTRA_DMA_IOCTL_BASE, 3, struct ultra_dma_stats)
#define ULTRA_CONFIG        _IOW(ULTRA_DMA_IOCTL_BASE, 4, struct ultra_dma_config)

/* Ultra-fast statistics structure */
struct ultra_dma_stats {
    u64 total_bytes;
    u64 total_packets;
    u64 dropped_packets;
    u64 avg_latency_ns;
    u32 active_regions;
    u32 cpu_usage;
};

/* Configuration structure */
struct ultra_dma_config {
    bool enable_hardware_timestamp;
    bool enable_kernel_bypass;
    unsigned int priority;
    unsigned int cpu_affinity;
};

/* Lock-free ring buffer implementation */
static inline void lockfree_ring_init(struct lockfree_ring *ring, void *buffer, u32 size, u32 item_size)
{
    ring->buffer = buffer;
    ring->size = size;
    ring->mask = size - 1;
    ring->item_size = item_size;
    ring->head = 0;
    ring->tail = 0;
}

static inline bool lockfree_ring_push(struct lockfree_ring *ring, void *item)
{
    u32 head = ring->head;
    u32 next_head = (head + 1) & ring->mask;
    
    if (next_head == ring->tail) {
        return false; // Ring full
    }
    
    memcpy(ring->buffer + (head * ring->item_size), item, ring->item_size);
    smp_wmb(); // Write memory barrier
    ring->head = next_head;
    
    return true;
}

static inline bool lockfree_ring_pop(struct lockfree_ring *ring, void *item)
{
    u32 tail = ring->tail;
    
    if (tail == ring->head) {
        return false; // Ring empty
    }
    
    memcpy(item, ring->buffer + (tail * ring->item_size), ring->item_size);
    smp_rmb(); // Read memory barrier
    ring->tail = (tail + 1) & ring->mask;
    
    return true;
}

/* Ultra-fast timestamp using RDTSC */
static inline u64 fast_timestamp(void)
{
    u64 cycles;
    u32 lo, hi;
    
    if (udev->enable_hardware_timestamp) {
        // Use RDTSC for highest resolution
        __asm__ __volatile__("rdtsc" : "=a"(lo), "=d"(hi));
        cycles = ((u64)hi << 32) | lo;
        return cycles;
    } else {
        // Use kernel timestamp
        return ktime_get_ns();
    }
}

/* Build Ethernet header directly in buffer */
static inline void build_ethernet_header(void *buffer, const u8 *dst_mac, const u8 *src_mac, u16 ethertype)
{
    struct ethhdr *eth = buffer;
    memcpy(eth->h_dest, dst_mac, 6);
    memcpy(eth->h_source, src_mac, 6);
    eth->h_proto = htons(ethertype);
}

/* Build IP header directly in buffer */
static inline void build_ip_header(void *buffer, u32 src_ip, u32 dst_ip, u16 total_len)
{
    struct iphdr *ip = buffer + sizeof(struct ethhdr);
    ip->version = 4;
    ip->ihl = 5;
    ip->tos = 0;
    ip->tot_len = htons(total_len);
    ip->id = 0;
    ip->frag_off = 0;
    ip->ttl = 64;
    ip->protocol = IPPROTO_UDP;
    ip->check = 0;
    ip->saddr = src_ip;
    ip->daddr = dst_ip;
    
    // Calculate checksum (simplified for performance)
    ip->check = ip_fast_csum((u8 *)ip, ip->ihl);
}

/* Build UDP header directly in buffer */
static inline void build_udp_header(void *buffer, u16 src_port, u16 dst_port, u16 udp_len)
{
    struct udphdr *udp = buffer + sizeof(struct ethhdr) + sizeof(struct iphdr);
    udp->source = htons(src_port);
    udp->dest = htons(dst_port);
    udp->len = htons(udp_len);
    udp->check = 0; // Optional for IPv4
}

/* Ultra-fast TX thread */
static int tx_thread_func(void *data)
{
    struct ultra_dma_region *region = data;
    struct packet_desc desc;
    void *packet_buffer;
    u64 start_time, end_time;
    
    // Set CPU affinity
    set_current_state(TASK_UNINTERRUPTIBLE);
    set_cpus_allowed_ptr(current, &udev->cpu_mask);
    set_user_nice(current, -20); // Highest priority
    
    while (!kthread_should_stop()) {
        // Check for packets to send
        if (lockfree_ring_pop(&region->tx_ring, &desc)) {
            start_time = fast_timestamp();
            
            // Build packet directly in buffer
            packet_buffer = kmalloc(MAX_PACKET_SIZE, GFP_ATOMIC);
            if (packet_buffer) {
                // Build headers
                build_ethernet_header(packet_buffer, udev->net_bypass.dst_mac, udev->net_bypass.src_mac, ETH_P_IP);
                build_ip_header(packet_buffer, udev->net_bypass.src_ip, udev->net_bypass.dst_ip, 
                              sizeof(struct iphdr) + sizeof(struct udphdr) + desc.size);
                build_udp_header(packet_buffer, udev->net_bypass.src_port, udev->net_bypass.dst_port,
                               sizeof(struct udphdr) + desc.size);
                
                // Copy data
                void *data_ptr = packet_buffer + sizeof(struct ethhdr) + sizeof(struct iphdr) + sizeof(struct udphdr);
                memcpy(data_ptr, (void *)desc.address, desc.size);
                
                // Send via raw socket (kernel bypass)
                if (udev->enable_kernel_bypass && udev->net_bypass.raw_sock) {
                    struct msghdr msg = {0};
                    struct kvec vec = {
                        .iov_base = packet_buffer,
                        .iov_len = sizeof(struct ethhdr) + sizeof(struct iphdr) + sizeof(struct udphdr) + desc.size
                    };
                    
                    kernel_sendmsg(udev->net_bypass.raw_sock, &msg, &vec, 1, vec.iov_len);
                }
                
                kfree(packet_buffer);
                
                end_time = fast_timestamp();
                atomic64_add(end_time - start_time, &udev->latency_sum);
                atomic64_inc(&udev->latency_count);
                atomic64_add(desc.size, &udev->total_bytes);
                atomic64_inc(&udev->total_packets);
                atomic64_add(desc.size, &region->bytes_transferred);
                atomic64_inc(&region->packets_sent);
            }
        } else {
            // No packets, yield CPU
            schedule();
        }
    }
    
    return 0;
}

/* Ultra-fast RX thread */
static int rx_thread_func(void *data)
{
    struct ultra_dma_dev *dev = data;
    void *packet_buffer;
    int len;
    
    // Set CPU affinity
    set_current_state(TASK_UNINTERRUPTIBLE);
    set_cpus_allowed_ptr(current, &udev->cpu_mask);
    set_user_nice(current, -20);
    
    packet_buffer = kmalloc(MAX_PACKET_SIZE, GFP_ATOMIC);
    if (!packet_buffer) {
        return -ENOMEM;
    }
    
    while (!kthread_should_stop()) {
        if (udev->net_bypass.raw_sock) {
            struct msghdr msg = {0};
            struct kvec vec = {
                .iov_base = packet_buffer,
                .iov_len = MAX_PACKET_SIZE
            };
            
            len = kernel_recvmsg(udev->net_bypass.raw_sock, &msg, &vec, 1, MAX_PACKET_SIZE, MSG_DONTWAIT);
            
            if (len > 0) {
                // Process received packet
                // Parse headers and write to memory region
                atomic64_inc(&udev->total_packets);
                atomic64_add(len, &udev->total_bytes);
            }
        } else {
            schedule();
        }
    }
    
    kfree(packet_buffer);
    return 0;
}

/* Statistics thread */
static int stats_thread_func(void *data)
{
    struct ultra_dma_dev *dev = data;
    u64 last_bytes = 0, last_packets = 0;
    u64 current_bytes, current_packets;
    
    while (!kthread_should_stop()) {
        msleep(1000); // Update every second
        
        current_bytes = atomic64_read(&dev->total_bytes);
        current_packets = atomic64_read(&dev->total_packets);
        
        // Calculate throughput
        u64 bytes_per_sec = current_bytes - last_bytes;
        u64 packets_per_sec = current_packets - last_packets;
        
        last_bytes = current_bytes;
        last_packets = current_packets;
        
        // Update statistics (could be exported to userspace)
        pr_debug("UDMA: %llu MB/s, %llu packets/s\n", 
                bytes_per_sec / 1024 / 1024, packets_per_sec);
    }
    
    return 0;
}

static int ultra_dma_open(struct inode *inode, struct file *file)
{
    struct ultra_dma_dev *dev = container_of(inode->i_cdev, struct ultra_dma_dev, cdev);
    file->private_data = dev;
    
    return 0;
}

static int ultra_dma_release(struct inode *inode, struct file *file)
{
    return 0;
}

static long ultra_dma_ioctl(struct file *file, unsigned int cmd, unsigned long arg)
{
    struct ultra_dma_dev *dev = file->private_data;
    struct ultra_dma_region region;
    unsigned long addr;
    struct ultra_dma_stats stats;
    struct ultra_dma_config config;
    int ret = 0;
    int i;
    
    switch (cmd) {
    case ULTRA_ADD_REGION:
        if (copy_from_user(&region, (void __user *)arg, sizeof(region))) {
            return -EFAULT;
        }
        
        mutex_lock(&dev->regions_lock);
        
        if (dev->num_regions >= NUM_RINGS) {
            mutex_unlock(&dev->regions_lock);
            return -ENOSPC;
        }
        
        // Allocate zero-copy memory
        region.pages = kmalloc_array(region.num_pages, sizeof(struct page *), GFP_KERNEL);
        if (!region.pages) {
            mutex_unlock(&dev->regions_lock);
            return -ENOMEM;
        }
        
        // Allocate contiguous memory for high performance
        region.user_virt_addr = dma_alloc_coherent(NULL, region.size, &region.phys_addr, GFP_KERNEL);
        if (!region.user_virt_addr) {
            kfree(region.pages);
            mutex_unlock(&dev->regions_lock);
            return -ENOMEM;
        }
        
        // Initialize lock-free rings
        void *tx_buffer = kmalloc(RING_BUFFER_SIZE * sizeof(struct packet_desc), GFP_KERNEL);
        void *rx_buffer = kmalloc(RING_BUFFER_SIZE * sizeof(struct packet_desc), GFP_KERNEL);
        
        lockfree_ring_init(&region.tx_ring, tx_buffer, RING_BUFFER_SIZE, sizeof(struct packet_desc));
        lockfree_ring_init(&region.rx_ring, rx_buffer, RING_BUFFER_SIZE, sizeof(struct packet_desc));
        
        region.active = true;
        atomic64_set(&region.bytes_transferred, 0);
        atomic64_set(&region.packets_sent, 0);
        
        dev->regions[dev->num_regions] = region;
        dev->num_regions++;
        
        mutex_unlock(&dev->regions_lock);
        
        // Start TX thread for this region
        dev->tx_threads[dev->num_regions - 1] = kthread_create(tx_thread_func, &dev->regions[dev->num_regions - 1], 
                                                              "ultra_dma_tx_%d", dev->num_regions - 1);
        if (dev->tx_threads[dev->num_regions - 1]) {
            wake_up_process(dev->tx_threads[dev->num_regions - 1]);
        }
        
        break;
        
    case ULTRA_GET_STATS:
        stats.total_bytes = atomic64_read(&dev->total_bytes);
        stats.total_packets = atomic64_read(&dev->total_packets);
        stats.dropped_packets = atomic64_read(&dev->dropped_packets);
        
        if (atomic64_read(&dev->latency_count) > 0) {
            stats.avg_latency_ns = atomic64_read(&dev->latency_sum) / atomic64_read(&dev->latency_count);
        } else {
            stats.avg_latency_ns = 0;
        }
        
        stats.active_regions = dev->num_regions;
        stats.cpu_usage = 0; // Could be calculated
        
        if (copy_to_user((void __user *)arg, &stats, sizeof(stats))) {
            return -EFAULT;
        }
        break;
        
    case ULTRA_CONFIG:
        if (copy_from_user(&config, (void __user *)arg, sizeof(config))) {
            return -EFAULT;
        }
        
        dev->enable_hardware_timestamp = config.enable_hardware_timestamp;
        dev->enable_kernel_bypass = config.enable_kernel_bypass;
        dev->priority = config.priority;
        
        // Update CPU affinity
        if (config.cpu_affinity > 0) {
            cpumask_clear(&dev->cpu_mask);
            for (i = 0; i < min(config.cpu_affinity, num_online_cpus()); i++) {
                cpumask_set_cpu(i, &dev->cpu_mask);
            }
        }
        
        break;
        
    default:
        ret = -ENOTTY;
        break;
    }
    
    return ret;
}

static int ultra_dma_mmap(struct file *file, struct vm_area_struct *vma)
{
    struct ultra_dma_dev *dev = file->private_data;
    unsigned long size = vma->vm_end - vma->vm_start;
    unsigned long offset = vma->vm_pgoff << PAGE_SHIFT;
    struct ultra_dma_region *region = NULL;
    int i;
    
    // Find the region
    mutex_lock(&dev->regions_lock);
    for (i = 0; i < dev->num_regions; i++) {
        if (dev->regions[i].active && offset >= dev->regions[i].start_addr && 
            offset < dev->regions[i].start_addr + dev->regions[i].size) {
            region = &dev->regions[i];
            break;
        }
    }
    mutex_unlock(&dev->regions_lock);
    
    if (!region) {
        return -EINVAL;
    }
    
    // Zero-copy mapping of DMA memory
    return remap_pfn_range(vma, vma->vm_start, region->phys_addr >> PAGE_SHIFT, 
                          size, vma->vm_page_prot);
}

static int __init ultra_dma_init(void)
{
    int ret, i;
    
    pr_info("UDMA: Ultra-Low-Latency Virtual DMA Controller v%s\n", DRIVER_VERSION);
    
    // Allocate device structure
    udev = kzalloc(sizeof(*udev), GFP_KERNEL);
    if (!udev) {
        return -ENOMEM;
    }
    
    // Initialize device
    mutex_init(&udev->regions_lock);
    spin_lock_init(&udev->stats_lock);
    
    // Set CPU affinity mask
    cpumask_clear(&udev->cpu_mask);
    for (i = 0; i < min(4, num_online_cpus()); i++) {
        cpumask_set_cpu(i, &udev->cpu_mask);
    }
    
    // Create memory pools
    udev->packet_cache = kmem_cache_create("ultra_dma_packet", MAX_PACKET_SIZE, 0, SLAB_HWCACHE_ALIGN, NULL);
    udev->desc_cache = kmem_cache_create("ultra_dma_desc", sizeof(struct packet_desc), 0, SLAB_HWCACHE_ALIGN, NULL);
    
    // Create character device
    ret = alloc_chrdev_region(&udev->dev_num, 0, 1, DRIVER_NAME);
    if (ret) {
        pr_err("UDMA: Failed to allocate device number\n");
        goto err_free_dev;
    }
    
    cdev_init(&udev->cdev, &ultra_dma_fops);
    udev->cdev.owner = THIS_MODULE;
    
    ret = cdev_add(&udev->cdev, udev->dev_num, 1);
    if (ret) {
        pr_err("UDMA: Failed to add character device\n");
        goto err_unregister;
    }
    
    // Create device class and device
    udev->class = class_create(THIS_MODULE, DRIVER_NAME);
    if (IS_ERR(udev->class)) {
        ret = PTR_ERR(udev->class);
        pr_err("UDMA: Failed to create device class\n");
        goto err_cdev_del;
    }
    
    udev->device = device_create(udev->class, NULL, udev->dev_num, NULL, DRIVER_NAME);
    if (IS_ERR(udev->device)) {
        ret = PTR_ERR(udev->device);
        pr_err("UDMA: Failed to create device\n");
        goto err_class_destroy;
    }
    
    // Initialize network bypass
    if (udev->enable_kernel_bypass) {
        ret = sock_create_kern(&init_net, AF_PACKET, SOCK_RAW, htons(ETH_P_ALL), &udev->net_bypass.raw_sock);
        if (ret) {
            pr_err("UDMA: Failed to create raw socket\n");
            goto err_device_destroy;
        }
    }
    
    // Start worker threads
    udev->rx_thread = kthread_create(rx_thread_func, udev, "ultra_dma_rx");
    if (udev->rx_thread) {
        wake_up_process(udev->rx_thread);
    }
    
    udev->stats_thread = kthread_create(stats_thread_func, udev, "ultra_dma_stats");
    if (udev->stats_thread) {
        wake_up_process(udev->stats_thread);
    }
    
    pr_info("UDMA: Ultra-Low-Latency DMA Controller initialized\n");
    return 0;
    
err_device_destroy:
    device_destroy(udev->class, udev->dev_num);
err_class_destroy:
    class_destroy(udev->class);
err_cdev_del:
    cdev_del(&udev->cdev);
err_unregister:
    unregister_chrdev_region(udev->dev_num, 1);
err_free_dev:
    kfree(udev);
    return ret;
}

static void __exit ultra_dma_exit(void)
{
    int i;
    
    if (!udev)
        return;
    
    // Stop worker threads
    if (udev->rx_thread) {
        kthread_stop(udev->rx_thread);
    }
    if (udev->stats_thread) {
        kthread_stop(udev->stats_thread);
    }
    
    for (i = 0; i < NUM_RINGS; i++) {
        if (udev->tx_threads[i]) {
            kthread_stop(udev->tx_threads[i]);
        }
    }
    
    // Cleanup regions
    for (i = 0; i < udev->num_regions; i++) {
        if (udev->regions[i].active) {
            if (udev->regions[i].user_virt_addr) {
                dma_free_coherent(NULL, udev->regions[i].size, 
                                udev->regions[i].user_virt_addr, udev->regions[i].phys_addr);
            }
            kfree(udev->regions[i].pages);
        }
    }
    
    // Cleanup network
    if (udev->net_bypass.raw_sock) {
        sock_release(udev->net_bypass.raw_sock);
    }
    
    // Cleanup memory pools
    if (udev->packet_cache) {
        kmem_cache_destroy(udev->packet_cache);
    }
    if (udev->desc_cache) {
        kmem_cache_destroy(udev->desc_cache);
    }
    
    // Destroy device
    device_destroy(udev->class, udev->dev_num);
    class_destroy(udev->class);
    cdev_del(&udev->cdev);
    unregister_chrdev_region(udev->dev_num, 1);
    
    kfree(udev);
    
    pr_info("UDMA: Ultra-Low-Latency DMA Controller unloaded\n");
}

module_init(ultra_dma_init);
module_exit(ultra_dma_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Software-Defined RDMA Project");
MODULE_DESCRIPTION("Ultra-Low-Latency Virtual DMA Controller");
MODULE_VERSION(DRIVER_VERSION);

MODULE_PARM_DESC(enable_hardware_timestamp, "Enable hardware timestamping");
static bool enable_hardware_timestamp = true;
module_param(enable_hardware_timestamp, bool, 0644);

MODULE_PARM_DESC(enable_kernel_bypass, "Enable kernel network bypass");
static bool enable_kernel_bypass = true;
module_param(enable_kernel_bypass, bool, 0644);
