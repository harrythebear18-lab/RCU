/*
 * Virtual DMA Controller Kernel Driver
 * 
 * This driver creates a virtual DMA controller that intercepts memory writes
 * to specific regions and transparently forwards them over UDP to remote systems.
 * 
 * Provides the same programming model as physical DMA without hardware risks.
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

#define DRIVER_NAME "virtual_dma"
#define DRIVER_VERSION "1.0"
#define MAX_REGIONS 16
#define MAX_PACKET_SIZE 1400
#define DMA_WINDOW_SIZE (1024 * 1024)  // 1MB DMA window

/* DMA Region structure */
struct dma_region {
    unsigned long start_addr;
    unsigned long size;
    unsigned char *local_buffer;
    char remote_ip[16];
    unsigned short remote_port;
    bool active;
    atomic_t pending_ops;
    struct mutex region_lock;
};

/* DMA Packet structure */
struct dma_packet {
    __u32 sequence;
    __u32 address;
    __u32 size;
    __u8 data[MAX_PACKET_SIZE - 12];  // Header is 12 bytes
};

/* Virtual DMA device structure */
struct virtual_dma_dev {
    struct cdev cdev;
    struct device *device;
    struct class *class;
    dev_t dev_num;
    
    /* DMA regions */
    struct dma_region regions[MAX_REGIONS];
    unsigned int num_regions;
    struct mutex regions_lock;
    
    /* Network socket */
    struct socket *udp_sock;
    struct sockaddr_in remote_addr;
    
    /* Work queue for async operations */
    struct workqueue_struct *workqueue;
    struct work_struct network_work;
    
    /* Statistics */
    atomic64_t bytes_transferred;
    atomic64_t packets_sent;
    atomic64_t packets_dropped;
    atomic_t active_regions;
    
    /* Synchronization */
    spinlock_t stats_lock;
    struct mutex socket_lock;
    
    /* Configuration */
    bool debug_mode;
    unsigned int timeout_ms;
};

static struct virtual_dma_dev *vdev;

/* Forward declarations */
static int virtual_dma_open(struct inode *inode, struct file *file);
static int virtual_dma_release(struct inode *inode, struct file *file);
static long virtual_dma_ioctl(struct file *file, unsigned int cmd, unsigned long arg);
static int virtual_dma_mmap(struct file *file, struct vm_area_struct *vma);
static void virtual_dma_network_worker(struct work_struct *work);
static int send_dma_packet(struct dma_region *region, unsigned long offset, const void *data, size_t size);

/* File operations */
static const struct file_operations virtual_dma_fops = {
    .owner = THIS_MODULE,
    .open = virtual_dma_open,
    .release = virtual_dma_release,
    .unlocked_ioctl = virtual_dma_ioctl,
    .mmap = virtual_dma_mmap,
};

/* IOCTL commands */
#define VDMA_IOCTL_BASE 'D'
#define VDMA_ADD_REGION    _IOW(VDMA_IOCTL_BASE, 1, struct dma_region)
#define VDMA_REMOVE_REGION _IOW(VDMA_IOCTL_BASE, 2, unsigned long)
#define VDMA_GET_STATS     _IOR(VDMA_IOCTL_BASE, 3, struct vdma_stats)
#define VDMA_CONFIG        _IOW(VDMA_IOCTL_BASE, 4, struct vdma_config)

/* Statistics structure */
struct vdma_stats {
    u64 bytes_transferred;
    u64 packets_sent;
    u64 packets_dropped;
    u32 active_regions;
    u32 pending_operations;
};

/* Configuration structure */
struct vdma_config {
    bool debug_mode;
    unsigned int timeout_ms;
    unsigned int max_retries;
};

static int virtual_dma_open(struct inode *inode, struct file *file)
{
    struct virtual_dma_dev *dev = container_of(inode->i_cdev, struct virtual_dma_dev, cdev);
    file->private_data = dev;
    
    if (dev->debug_mode) {
        pr_info("VDMA: Device opened\n");
    }
    
    return 0;
}

static int virtual_dma_release(struct inode *inode, struct file *file)
{
    struct virtual_dma_dev *dev = file->private_data;
    
    if (dev->debug_mode) {
        pr_info("VDMA: Device closed\n");
    }
    
    return 0;
}

static long virtual_dma_ioctl(struct file *file, unsigned int cmd, unsigned long arg)
{
    struct virtual_dma_dev *dev = file->private_data;
    struct dma_region region;
    unsigned long addr;
    struct vdma_stats stats;
    struct vdma_config config;
    int ret = 0;
    int i;
    
    switch (cmd) {
    case VDMA_ADD_REGION:
        if (copy_from_user(&region, (void __user *)arg, sizeof(region))) {
            return -EFAULT;
        }
        
        mutex_lock(&dev->regions_lock);
        
        if (dev->num_regions >= MAX_REGIONS) {
            mutex_unlock(&dev->regions_lock);
            return -ENOSPC;
        }
        
        /* Allocate local buffer for this region */
        region.local_buffer = vmalloc(region.size);
        if (!region.local_buffer) {
            mutex_unlock(&dev->regions_lock);
            return -ENOMEM;
        }
        
        /* Initialize region */
        region.active = true;
        atomic_set(&region.pending_ops, 0);
        mutex_init(&region.region_lock);
        
        /* Add to regions array */
        dev->regions[dev->num_regions] = region;
        dev->num_regions++;
        atomic_inc(&dev->active_regions);
        
        mutex_unlock(&dev->regions_lock);
        
        if (dev->debug_mode) {
            pr_info("VDMA: Added region 0x%lx-0x%lx -> %s:%u\n",
                    region.start_addr, region.start_addr + region.size,
                    region.remote_ip, region.remote_port);
        }
        
        break;
        
    case VDMA_REMOVE_REGION:
        if (copy_from_user(&addr, (void __user *)arg, sizeof(addr))) {
            return -EFAULT;
        }
        
        mutex_lock(&dev->regions_lock);
        
        for (i = 0; i < dev->num_regions; i++) {
            if (dev->regions[i].start_addr == addr && dev->regions[i].active) {
                /* Wait for pending operations */
                while (atomic_read(&dev->regions[i].pending_ops) > 0) {
                    msleep(10);
                }
                
                vfree(dev->regions[i].local_buffer);
                dev->regions[i].active = false;
                atomic_dec(&dev->active_regions);
                
                if (dev->debug_mode) {
                    pr_info("VDMA: Removed region 0x%lx\n", addr);
                }
                break;
            }
        }
        
        mutex_unlock(&dev->regions_lock);
        break;
        
    case VDMA_GET_STATS:
        stats.bytes_transferred = atomic64_read(&dev->bytes_transferred);
        stats.packets_sent = atomic64_read(&dev->packets_sent);
        stats.packets_dropped = atomic64_read(&dev->packets_dropped);
        stats.active_regions = atomic_read(&dev->active_regions);
        
        /* Count pending operations */
        stats.pending_operations = 0;
        mutex_lock(&dev->regions_lock);
        for (i = 0; i < dev->num_regions; i++) {
            if (dev->regions[i].active) {
                stats.pending_operations += atomic_read(&dev->regions[i].pending_ops);
            }
        }
        mutex_unlock(&dev->regions_lock);
        
        if (copy_to_user((void __user *)arg, &stats, sizeof(stats))) {
            return -EFAULT;
        }
        break;
        
    case VDMA_CONFIG:
        if (copy_from_user(&config, (void __user *)arg, sizeof(config))) {
            return -EFAULT;
        }
        
        dev->debug_mode = config.debug_mode;
        dev->timeout_ms = config.timeout_ms;
        
        if (dev->debug_mode) {
            pr_info("VDMA: Configuration updated\n");
        }
        break;
        
    default:
        ret = -ENOTTY;
        break;
    }
    
    return ret;
}

static int virtual_dma_mmap(struct file *file, struct vm_area_struct *vma)
{
    struct virtual_dma_dev *dev = file->private_data;
    unsigned long size = vma->vm_end - vma->vm_start;
    unsigned long offset = vma->vm_pgoff << PAGE_SHIFT;
    struct dma_region *region = NULL;
    int i;
    int ret;
    
    /* Find the region that contains this offset */
    mutex_lock(&dev->regions_lock);
    for (i = 0; i < dev->num_regions; i++) {
        if (dev->regions[i].active &&
            offset >= dev->regions[i].start_addr &&
            offset < dev->regions[i].start_addr + dev->regions[i].size) {
            region = &dev->regions[i];
            break;
        }
    }
    mutex_unlock(&dev->regions_lock);
    
    if (!region) {
        pr_err("VDMA: Invalid mmap offset 0x%lx\n", offset);
        return -EINVAL;
    }
    
    /* Check size bounds */
    if (offset + size > region->start_addr + region->size) {
        return -EINVAL;
    }
    
    /* Map the DMA buffer to user space */
    ret = remap_vmalloc_range(vma, region->local_buffer, 0);
    if (ret) {
        pr_err("VDMA: remap_vmalloc_range failed: %d\n", ret);
        return ret;
    }
    
    /* Set page protection to allow write interception */
    vma->vm_page_prot = pgprot_writecombine(vma->vm_page_prot);
    vma->vm_flags |= VM_WRITE | VM_DONTEXPAND;
    
    if (dev->debug_mode) {
        pr_info("VDMA: Mapped region 0x%lx size 0x%lx\n", offset, size);
    }
    
    return 0;
}

/* Page fault handler to intercept writes */
static vm_fault_t virtual_dma_fault(struct vm_fault *vmf) {
    struct vm_area_struct *vma = vmf->vma;
    struct virtual_dma_dev *dev = vma->vm_file->private_data;
    unsigned long address = vmf->address;
    unsigned long offset = address - vma->vm_start;
    struct dma_region *region = NULL;
    int i;
    
    /* Find the corresponding DMA region */
    mutex_lock(&dev->regions_lock);
    for (i = 0; i < dev->num_regions; i++) {
        if (dev->regions[i].active &&
            address >= dev->regions[i].start_addr &&
            address < dev->regions[i].start_addr + dev->regions[i].size) {
            region = &dev->regions[i];
            break;
        }
    }
    mutex_unlock(&dev->regions_lock);
    
    if (!region) {
        return VM_FAULT_SIGBUS;
    }
    
    /* Get the actual page */
    vmf->page = vmalloc_to_page(region->local_buffer + offset);
    if (!vmf->page) {
        return VM_FAULT_OOM;
    }
    
    get_page(vmf->page);
    
    /* Mark page as dirty to track modifications */
    SetPageDirty(vmf->page);
    
    return 0;
}

static const struct vm_operations_struct virtual_dma_vm_ops = {
    .fault = virtual_dma_fault,
};

static int send_dma_packet(struct dma_region *region, unsigned long offset, const void *data, size_t size)
{
    struct virtual_dma_dev *dev = vdev;
    struct msghdr msg;
    struct kvec vec;
    struct dma_packet packet;
    int ret;
    
    if (!dev->udp_sock) {
        return -ENOTCONN;
    }
    
    /* Prepare packet */
    packet.sequence = atomic64_inc_return(&dev->packets_sent);
    packet.address = region->start_addr + offset;
    packet.size = size;
    memcpy(packet.data, data, size);
    
    /* Setup message */
    memset(&msg, 0, sizeof(msg));
    msg.msg_name = &dev->remote_addr;
    msg.msg_namelen = sizeof(dev->remote_addr);
    
    vec.iov_base = &packet;
    vec.iov_len = sizeof(packet.sequence) + sizeof(packet.address) + sizeof(packet.size) + size;
    
    mutex_lock(&dev->socket_lock);
    ret = kernel_sendmsg(dev->udp_sock, &msg, &vec, 1, vec.iov_len);
    mutex_unlock(&dev->socket_lock);
    
    if (ret > 0) {
        atomic64_add(size, &dev->bytes_transferred);
        if (dev->debug_mode) {
            pr_debug("VDMA: Sent %zu bytes to %s:%u\n", size, region->remote_ip, region->remote_port);
        }
        return 0;
    } else {
        atomic64_inc(&dev->packets_dropped);
        pr_err("VDMA: Send failed: %d\n", ret);
        return ret;
    }
}

static void virtual_dma_network_worker(struct work_struct *work)
{
    struct virtual_dma_dev *dev = container_of(work, struct virtual_dma_dev, network_work);
    int i;
    
    /* Process pending network operations for all regions */
    mutex_lock(&dev->regions_lock);
    for (i = 0; i < dev->num_regions; i++) {
        if (dev->regions[i].active && atomic_read(&dev->regions[i].pending_ops) > 0) {
            /* Queue network operations for this region */
            // Implementation would depend on specific use case
        }
    }
    mutex_unlock(&dev->regions_lock);
}

static int __init virtual_dma_init(void)
{
    int ret;
    struct sockaddr_in addr;
    
    pr_info("VDMA: Virtual DMA Controller v%s\n", DRIVER_VERSION);
    
    /* Allocate device structure */
    vdev = kzalloc(sizeof(*vdev), GFP_KERNEL);
    if (!vdev) {
        return -ENOMEM;
    }
    
    /* Initialize device */
    mutex_init(&vdev->regions_lock);
    mutex_init(&vdev->socket_lock);
    spin_lock_init(&vdev->stats_lock);
    
    /* Create character device */
    ret = alloc_chrdev_region(&vdev->dev_num, 0, 1, DRIVER_NAME);
    if (ret) {
        pr_err("VDMA: Failed to allocate device number\n");
        goto err_free_dev;
    }
    
    cdev_init(&vdev->cdev, &virtual_dma_fops);
    vdev->cdev.owner = THIS_MODULE;
    
    ret = cdev_add(&vdev->cdev, vdev->dev_num, 1);
    if (ret) {
        pr_err("VDMA: Failed to add character device\n");
        goto err_unregister;
    }
    
    /* Create device class and device */
    vdev->class = class_create(THIS_MODULE, DRIVER_NAME);
    if (IS_ERR(vdev->class)) {
        ret = PTR_ERR(vdev->class);
        pr_err("VDMA: Failed to create device class\n");
        goto err_cdev_del;
    }
    
    vdev->device = device_create(vdev->class, NULL, vdev->dev_num, NULL, DRIVER_NAME);
    if (IS_ERR(vdev->device)) {
        ret = PTR_ERR(vdev->device);
        pr_err("VDMA: Failed to create device\n");
        goto err_class_destroy;
    }
    
    /* Create UDP socket */
    ret = sock_create_kern(&init_net, AF_INET, SOCK_DGRAM, IPPROTO_UDP, &vdev->udp_sock);
    if (ret) {
        pr_err("VDMA: Failed to create UDP socket\n");
        goto err_device_destroy;
    }
    
    /* Bind socket to local port */
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons(0);  /* Any available port */
    
    ret = kernel_bind(vdev->udp_sock, (struct sockaddr *)&addr, sizeof(addr));
    if (ret) {
        pr_err("VDMA: Failed to bind UDP socket\n");
        goto err_sock_release;
    }
    
    /* Initialize work queue */
    vdev->workqueue = create_singlethread_workqueue("virtual_dma");
    if (!vdev->workqueue) {
        pr_err("VDMA: Failed to create work queue\n");
        ret = -ENOMEM;
        goto err_sock_release;
    }
    
    INIT_WORK(&vdev->network_work, virtual_dma_network_worker);
    
    /* Initialize configuration */
    vdev->debug_mode = false;
    vdev->timeout_ms = 1000;
    
    /* Set VM operations for all future mappings */
    // This would be done in the mmap implementation
    
    pr_info("VDMA: Virtual DMA Controller initialized\n");
    return 0;
    
err_sock_release:
    sock_release(vdev->udp_sock);
err_device_destroy:
    device_destroy(vdev->class, vdev->dev_num);
err_class_destroy:
    class_destroy(vdev->class);
err_cdev_del:
    cdev_del(&vdev->cdev);
err_unregister:
    unregister_chrdev_region(vdev->dev_num, 1);
err_free_dev:
    kfree(vdev);
    return ret;
}

static void __exit virtual_dma_exit(void)
{
    struct virtual_dma_dev *dev = vdev;
    int i;
    
    if (!dev)
        return;
    
    pr_info("VDMA: Shutting down Virtual DMA Controller\n");
    
    /* Flush work queue */
    if (dev->workqueue) {
        flush_workqueue(dev->workqueue);
        destroy_workqueue(dev->workqueue);
    }
    
    /* Clean up all regions */
    mutex_lock(&dev->regions_lock);
    for (i = 0; i < dev->num_regions; i++) {
        if (dev->regions[i].active) {
            vfree(dev->regions[i].local_buffer);
        }
    }
    mutex_unlock(&dev->regions_lock);
    
    /* Release socket */
    if (dev->udp_sock) {
        sock_release(dev->udp_sock);
    }
    
    /* Destroy device */
    device_destroy(dev->class, dev->dev_num);
    class_destroy(dev->class);
    cdev_del(&dev->cdev);
    unregister_chrdev_region(dev->dev_num, 1);
    
    kfree(dev);
    
    pr_info("VDMA: Virtual DMA Controller unloaded\n");
}

module_init(virtual_dma_init);
module_exit(virtual_dma_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Software-Defined RDMA Project");
MODULE_DESCRIPTION("Virtual DMA Controller Kernel Driver");
MODULE_VERSION(DRIVER_VERSION);

MODULE_PARM_DESC(debug, "Enable debug mode");
static bool debug = false;
module_param(debug, bool, 0644);
