#!/bin/bash
# Build script for Virtual DMA Kernel Driver
# Automated compilation and installation for Linux systems

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root for kernel operations
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_warning "Some operations require root privileges"
        print_info "You will be prompted for password when needed"
        return 1
    fi
    return 0
}

# Check system requirements
check_requirements() {
    print_info "Checking system requirements..."
    
    # Check if running on Linux
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        print_error "This script is designed for Linux systems"
        exit 1
    fi
    
    # Check kernel headers
    if [[ ! -d "/lib/modules/$(uname -r)/build" ]]; then
        print_error "Kernel headers not found"
        print_info "Install kernel headers with:"
        print_info "  Ubuntu/Debian: sudo apt-get install linux-headers-$(uname -r)"
        print_info "  RHEL/CentOS: sudo yum install kernel-devel-$(uname -r)"
        print_info "  Arch Linux: sudo pacman -S linux-headers"
        exit 1
    fi
    
    # Check build tools
    if ! command -v make &> /dev/null; then
        print_error "make not found"
        print_info "Install build tools with:"
        print_info "  Ubuntu/Debian: sudo apt-get install build-essential"
        print_info "  RHEL/CentOS: sudo yum groupinstall 'Development Tools'"
        print_info "  Arch Linux: sudo pacman -S base-devel"
        exit 1
    fi
    
    # Check gcc
    if ! command -v gcc &> /dev/null; then
        print_error "gcc not found"
        exit 1
    fi
    
    print_success "System requirements satisfied"
}

# Prepare build environment
prepare_build() {
    print_info "Preparing build environment..."
    
    # Clean any previous builds
    make clean 2>/dev/null || true
    
    # Remove old kernel module if loaded
    if lsmod | grep -q "virtual_dma"; then
        print_warning "Old kernel module detected, removing..."
        sudo rmmod virtual_dma_driver || true
    fi
    
    print_success "Build environment prepared"
}

# Build kernel driver
build_kernel() {
    print_info "Building Virtual DMA kernel driver..."
    
    # Build the module
    if make kernel; then
        print_success "Kernel driver built successfully"
        
        # Check if module was created
        if [[ -f "virtual_dma_driver.ko" ]]; then
            print_info "Module file: virtual_dma_driver.ko"
            ls -la virtual_dma_driver.ko
        else
            print_error "Module file not found"
            exit 1
        fi
    else
        print_error "Kernel driver build failed"
        exit 1
    fi
}

# Install kernel module
install_kernel() {
    print_info "Installing Virtual DMA kernel driver..."
    
    # Load the module
    if sudo insmod virtual_dma_driver.ko; then
        print_success "Kernel module loaded successfully"
        
        # Verify module is loaded
        if lsmod | grep -q "virtual_dma"; then
            print_info "Module is loaded in kernel"
            lsmod | grep virtual_dma
        else
            print_error "Module failed to load"
            exit 1
        fi
        
        # Create device node
        if [[ ! -e "/dev/virtual_dma" ]]; then
            print_info "Creating device node..."
            sudo mknod /dev/virtual_dma c $(awk '/virtual_dma/ {print $1}' /proc/devices) 0
            sudo chmod 666 /dev/virtual_dma
        fi
        
        # Verify device node
        if [[ -e "/dev/virtual_dma" ]]; then
            print_success "Device node created: /dev/virtual_dma"
            ls -la /dev/virtual_dma
        else
            print_error "Failed to create device node"
            exit 1
        fi
        
    else
        print_error "Failed to load kernel module"
        exit 1
    fi
}

# Test kernel module
test_kernel() {
    print_info "Testing kernel module functionality..."
    
    # Test device access
    if [[ -r "/dev/virtual_dma" ]] && [[ -w "/dev/virtual_dma" ]]; then
        print_success "Device node is accessible"
    else
        print_error "Device node is not accessible"
        exit 1
    fi
    
    # Check kernel log for driver messages
    if dmesg | grep -q "Virtual DMA Controller"; then
        print_success "Driver initialized successfully"
        print_info "Recent kernel messages:"
        dmesg | grep "Virtual DMA" | tail -5
    else
        print_warning "No driver messages found in kernel log"
    fi
}

# Create startup script
create_startup_script() {
    print_info "Creating startup script..."
    
    cat > start_virtual_dma.sh << 'EOF'
#!/bin/bash
# Startup script for Virtual DMA services

# Load kernel module
if ! lsmod | grep -q "virtual_dma"; then
    echo "Loading Virtual DMA kernel module..."
    sudo insmod virtual_dma_driver.ko
    sudo chmod 666 /dev/virtual_dma
fi

# Start userspace services
echo "Starting Virtual DMA services..."

# ZeroMQ RDMA Server
python3 zero_copy_rdmda.py server &
ZMQ_PID=$!
echo "ZeroMQ RDMA Server PID: $ZMQ_PID"

# Virtual PCIe Driver
python3 virtual_pcie_tunnel.py target &
PCIE_PID=$!
echo "Virtual PCIe Driver PID: $PCIE_PID"

# UDP Memory Bridge Server
python3 udp_memory_bridge.py server &
UDP_PID=$!
echo "UDP Memory Bridge Server PID: $UDP_PID"

# Advanced DMA Service
python3 advanced_dma_service.py server &
DMA_PID=$!
echo "Advanced DMA Service PID: $DMA_PID"

echo "All Virtual DMA services started"
echo "PIDs: ZMQ=$ZMQ_PID PCIE=$PCIE_PID UDP=$UDP_PID DMA=$DMA_PID"

# Save PIDs for cleanup
echo $ZMQ_PID > /tmp/vdma_zmq.pid
echo $PCIE_PID > /tmp/vdma_pcie.pid
echo $UDP_PID > /tmp/vdma_udp.pid
echo $DMA_PID > /tmp/vdma_dma.pid

echo "Use 'stop_virtual_dma.sh' to stop all services"
EOF
    
    chmod +x start_virtual_dma.sh
    
    cat > stop_virtual_dma.sh << 'EOF'
#!/bin/bash
# Stop script for Virtual DMA services

echo "Stopping Virtual DMA services..."

# Stop userspace services
if [[ -f "/tmp/vdma_zmq.pid" ]]; then
    PID=$(cat /tmp/vdma_zmq.pid)
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        echo "Stopped ZeroMQ RDMA Server (PID: $PID)"
    fi
    rm -f /tmp/vdma_zmq.pid
fi

if [[ -f "/tmp/vdma_pcie.pid" ]]; then
    PID=$(cat /tmp/vdma_pcie.pid)
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        echo "Stopped Virtual PCIe Driver (PID: $PID)"
    fi
    rm -f /tmp/vdma_pcie.pid
fi

if [[ -f "/tmp/vdma_udp.pid" ]]; then
    PID=$(cat /tmp/vdma_udp.pid)
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        echo "Stopped UDP Memory Bridge Server (PID: $PID)"
    fi
    rm -f /tmp/vdma_udp.pid
fi

if [[ -f "/tmp/vdma_dma.pid" ]]; then
    PID=$(cat /tmp/vdma_dma.pid)
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        echo "Stopped Advanced DMA Service (PID: $PID)"
    fi
    rm -f /tmp/vdma_dma.pid
fi

# Unload kernel module
if lsmod | grep -q "virtual_dma"; then
    echo "Unloading Virtual DMA kernel module..."
    sudo rmmod virtual_dma_driver
fi

echo "All Virtual DMA services stopped"
EOF
    
    chmod +x stop_virtual_dma.sh
    
    print_success "Startup scripts created"
    print_info "Use './start_virtual_dma.sh' to start all services"
    print_info "Use './stop_virtual_dma.sh' to stop all services"
}

# Create systemd service (optional)
create_systemd_service() {
    print_info "Creating systemd service..."
    
    if command -v systemctl &> /dev/null; then
        cat > virtual_dma.service << EOF
[Unit]
Description=Software-Defined RDMA Virtual DMA Service
After=network.target

[Service]
Type=forking
User=root
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/start_virtual_dma.sh
ExecStop=$(pwd)/stop_virtual_dma.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
        
        print_info "To install as systemd service:"
        print_info "  sudo cp virtual_dma.service /etc/systemd/system/"
        print_info "  sudo systemctl daemon-reload"
        print_info "  sudo systemctl enable virtual_dma"
        print_info "  sudo systemctl start virtual_dma"
    else
        print_warning "systemd not available, skipping systemd service creation"
    fi
}

# Main installation function
main() {
    echo "Virtual DMA Kernel Driver Build Script"
    echo "===================================="
    echo
    
    # Check if we're in the right directory
    if [[ ! -f "virtual_dma_driver.c" ]]; then
        print_error "virtual_dma_driver.c not found"
        print_info "Please run this script from the RDMA project directory"
        exit 1
    fi
    
    # Run checks
    check_requirements
    prepare_build
    
    # Build and install
    build_kernel
    install_kernel
    test_kernel
    
    # Create helper scripts
    create_startup_script
    create_systemd_service
    
    echo
    print_success "Virtual DMA kernel driver installation completed!"
    echo
    print_info "Next steps:"
    print_info "1. Test the userspace components: python3 test_suite.py"
    print_info "2. Start all services: ./start_virtual_dma.sh"
    print_info "3. Run benchmarks: make benchmark"
    print_info "4. Check documentation: README.md"
    echo
    print_info "Device node: /dev/virtual_dma"
    print_info "Kernel module: virtual_dma_driver"
    echo
    print_warning "Remember to run as root for kernel operations"
}

# Uninstall function
uninstall() {
    print_info "Uninstalling Virtual DMA kernel driver..."
    
    # Stop services
    if [[ -f "./stop_virtual_dma.sh" ]]; then
        ./stop_virtual_dma.sh
    fi
    
    # Unload module
    if lsmod | grep -q "virtual_dma"; then
        sudo rmmod virtual_dma_driver
        print_success "Kernel module unloaded"
    fi
    
    # Remove device node
    if [[ -e "/dev/virtual_dma" ]]; then
        sudo rm -f /dev/virtual_dma
        print_success "Device node removed"
    fi
    
    # Clean build
    make clean
    
    print_success "Uninstall completed"
}

# Command line argument handling
case "${1:-install}" in
    "install")
        main
        ;;
    "uninstall")
        uninstall
        ;;
    "build")
        check_requirements
        prepare_build
        build_kernel
        ;;
    "test")
        test_kernel
        ;;
    "help"|"-h"|"--help")
        echo "Virtual DMA Kernel Driver Build Script"
        echo "Usage: $0 [install|uninstall|build|test|help]"
        echo
        echo "Commands:"
        echo "  install   - Build and install kernel driver (default)"
        echo "  uninstall - Remove kernel driver and cleanup"
        echo "  build     - Build kernel driver only"
        echo "  test      - Test installed kernel driver"
        echo "  help      - Show this help"
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac
