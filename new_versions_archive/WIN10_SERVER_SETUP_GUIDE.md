# 🖥️ Windows 10 Homelab Server Setup Guide

## 📋 Overview

This guide will help you set up your Windows 10 machine as a homelab server to host shared resources (eRAM, eGPU, eCPU, etc.) for Windows 11 clients.

## 🎯 Architecture

```
┌─────────────────┐    HTTP/REST API    ┌─────────────────┐
│  Windows 10     │◄───────────────────▶│  Windows 11     │
│  Server (Host)   │                    │  Client (Guest)  │
│                 │                    │                 │
│ • eRAM Hosting  │                    │ • Resource      │
│ • eGPU Passthrough│                   │   Allocation    │
│ • eCPU Sharing  │                    │ • Remote        │
│ • Storage Pool  │                    │   Monitoring    │
│ • Network Share │                    │ • Auto-Connect  │
└─────────────────┘                    └─────────────────┘
```

## 🚀 Quick Start

### 1. On Windows 10 Server Machine

1. **Install Dependencies**
   ```bash
   pip install psutil requests sqlite3 wmi GPUtil
   ```

2. **Start Server Launcher**
   ```bash
   python win10_server_launcher.py
   ```

3. **Click "Start Server"** in the launcher

### 2. On Windows 11 Client Machine

1. **Install Dependencies**
   ```bash
   pip install psutil requests sqlite3
   ```

2. **Connect to Server**
   ```bash
   python win11_homelab_client.py
   ```

## 📋 Detailed Setup Instructions

### 🔧 Prerequisites

#### Windows 10 Server Requirements
- **OS**: Windows 10 Home/Pro/Enterprise
- **RAM**: 8GB+ recommended (for hosting eRAM)
- **GPU**: NVIDIA/AMD GPU with 2GB+ VRAM (optional)
- **CPU**: Multi-core processor
- **Network**: Stable Ethernet connection
- **Storage**: 50GB+ free space
- **Python**: 3.8+ with required packages

#### Windows 11 Client Requirements
- **OS**: Windows 11 Home/Pro
- **RAM**: 4GB+ minimum
- **Network**: Connection to Windows 10 server
- **Python**: 3.8+ with required packages

### 🖥️ Windows 10 Server Setup

#### 1. Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv win10_homelab_env
win10_homelab_env\Scripts\activate

# Install required packages
pip install psutil requests sqlite3 wmi GPUtil
pip install flask flask-cors schedule
```

#### 2. Configure Server Settings

Edit `win10_server_settings.json`:

```json
{
  "server_name": "Windows 10 Homelab Server",
  "max_clients": 5,
  "session_timeout": 3600,
  "allocation_timeout": 7200,
  "resource_check_interval": 60,
  "enable_authentication": true,
  "max_eram_allocation_gb": 16,
  "enable_egpu_passthrough": true,
  "enable_load_balancing": true,
  "win10_optimizations": true,
  "compatibility_mode": true
}
```

#### 3. Start the Server

**Method 1: Using the Launcher (Recommended)**
```bash
python win10_server_launcher.py
```
- Click "Start Server" button
- Monitor server status in the GUI
- Use "Test Connection" to verify

**Method 2: Direct Server Start**
```bash
python win10_homelab_server.py
```

#### 4. Verify Server Status

The server will start on `http://YOUR_IP:8080` by default. You can:
- Access the REST API
- View server status at `/api/v1/server/status`
- Monitor resources at `/api/v1/resources`

#### 5. Configure Windows Firewall

Open port 8080 for incoming connections:

1. **Windows Defender Firewall**:
   - Go to Control Panel → Windows Defender Firewall
   - Click "Advanced settings"
   - Click "Inbound Rules" → "New Rule"
   - Select "Port" → "TCP" → "Specific local ports: 8080"
   - Allow the connection
   - Name: "Windows 10 Homelab Server"

2. **Third-party Firewall**:
   - Allow inbound connections on port 8080
   - Allow Python executable

### 💻 Windows 11 Client Setup

#### 1. Install Client Dependencies

```bash
# Same virtual environment or new one
pip install psutil requests sqlite3
```

#### 2. Configure Client Settings

Edit `win11_client_settings.json`:

```json
{
  "server_url": "http://WIN10_IP:8080",
  "heartbeat_interval": 30,
  "resource_check_interval": 60,
  "auto_reconnect": true,
  "preferred_resources": {
    "eram": "win10_eram_medium",
    "egpu": "win10_egpu_0",
    "ecpu": "win10_ecpu_medium"
  },
  "win11_optimizations": true,
  "enhanced_performance": true
}
```

#### 3. Connect to Server

**Method 1: Direct Client Start**
```bash
python win11_homelab_client.py
```

**Method 2: Using the Dashboard**
```bash
python homelab_dashboard.py
# Enter Windows 10 server IP and click "Connect Client"
```

## 🔌 Resource Management

### Available Resource Types on Windows 10

| Resource Type | Description | Typical Capacity |
|---------------|-------------|-----------------|
| **eRAM** | Shared memory pools | 2GB, 4GB, 8GB |
| **eGPU** | GPU passthrough | Full GPU memory |
| **eCPU** | Virtual CPU cores | 1-4 cores |
| **eStorage** | Network storage | 50% of free space |
| **eNetwork** | Network bandwidth | Interface speed |

### Resource Allocation Examples

#### Automatic Allocation (Windows 11 Client)
```python
# Auto-allocate preferred resources
allocations = client.auto_allocate_resources()
print(f"Allocated: {len(allocations)} resources")
```

#### Manual Allocation
```python
# Allocate 4GB of eRAM from Windows 10
eram_allocation = client.allocate_eram(4.0)

# Allocate full GPU
gpu_allocation = client.allocate_egpu()

# Allocate 2 CPU cores
cpu_allocation = client.allocate_ecpu(2.0)
```

#### Resource Release
```python
# Release specific allocation
client.release_resource(allocation_id)

# Release all allocations
client.release_all_resources()
```

## 🛡️ Security Configuration

### Basic Security

1. **API Key Authentication**
   - Each client gets unique API key
   - Keys are generated automatically on registration
   - Keys are stored securely in database

2. **Client Registration**
   - Clients must register with server
   - System information is collected for identification
   - MAC address binding optional

### Network Security

1. **Firewall Configuration**
   - Only open port 8080 to trusted networks
   - Consider VPN for remote access
   - Monitor connection logs

2. **Access Control**
   ```json
   {
     "enable_authentication": true,
     "max_clients": 5,
     "session_timeout": 3600
   }
   ```

## 📊 Monitoring and Management

### Server Monitoring

The Windows 10 server provides:

- **Resource Usage**: Real-time CPU, RAM, GPU monitoring
- **Client Status**: Connected clients and their allocations
- **Allocation Tracking**: Who is using what resources
- **Performance Metrics**: Server performance and health

### Client Monitoring

The Windows 11 client provides:

- **Connection Status**: Server connectivity and health
- **Resource Status**: Current allocations and availability
- **Performance Metrics**: Local system performance
- **Usage Statistics**: Resource usage over time

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/server/status` | GET | Server status and metrics |
| `/api/v1/resources` | GET | List available resources |
| `/api/v1/clients/register` | POST | Register new client |
| `/api/v1/allocations` | GET | List allocations |
| `/api/v1/monitoring/metrics` | GET | System metrics |

## 🎮 Use Cases

### 1. Gaming Enhancement
- **Windows 10 Server**: Host powerful gaming GPU
- **Windows 11 Client**: Lightweight laptop/desktop
- **Benefit**: Play high-end games on basic hardware

### 2. Content Creation
- **Windows 10 Server**: High-end CPU + GPU + RAM
- **Windows 11 Client**: Basic workstation
- **Benefit**: Video editing, 3D rendering on client

### 3. Development Environment
- **Windows 10 Server**: Development server with resources
- **Windows 11 Client**: Multiple development machines
- **Benefit**: Shared development resources

### 4. Machine Learning
- **Windows 10 Server**: NVIDIA GPU with CUDA
- **Windows 11 Client**: Basic workstation
- **Benefit**: Run ML models without local GPU

## 🔧 Advanced Configuration

### Custom Resource Pools

Edit `win10_homelab_server.py` resource initialization:

```python
# Custom eRAM pools for specific use case
eram_pools = [
    {
        'id': 'win10_eram_gaming',
        'name': 'Win10 eRAM Gaming Pool',
        'capacity': 8,
        'properties': {
            'pool_size': 'gaming',
            'priority': 'high',
            'max_allocation_gb': 8,
            'optimized_for': 'gaming'
        }
    }
]
```

### Performance Optimization

#### Server Optimization
```json
{
  "resource_check_interval": 30,
  "enable_load_balancing": true,
  "win10_optimizations": true,
  "compatibility_mode": true
}
```

#### Client Optimization
```json
{
  "heartbeat_interval": 30,
  "enable_local_cache": true,
  "win11_optimizations": true,
  "enhanced_performance": true
}
```

## 🚨 Troubleshooting

### Common Issues

#### Server Won't Start
```bash
# Check dependencies
pip list | grep -E "(psutil|wmi|GPUtil)"

# Check port usage
netstat -an | grep :8080

# Check logs
type win10_homelab_server.log
```

#### Client Can't Connect
```bash
# Test server connectivity
ping WIN10_IP

# Test HTTP connection
curl -I http://WIN10_IP:8080/api/v1/server/status

# Check client logs
type win11_homelab_client.log
```

#### Resource Allocation Fails
```bash
# Check resource availability
curl -H "X-API-Key: KEY" http://WIN10_IP:8080/api/v1/resources

# Check client permissions
# Verify API key has 'allocate' permission
```

#### Performance Issues
- Check network latency between machines
- Reduce resource allocation amounts
- Monitor server resource usage
- Check for network congestion

### Windows 10 Specific Issues

#### WMI Access Denied
- Run server as Administrator
- Check Windows Management Instrumentation service
- Verify WMI permissions

#### GPU Detection Issues
- Install latest GPU drivers
- Install GPUtil: `pip install GPUtil`
- Check if GPU is properly recognized

#### Firewall Blocking
- Add Python to Windows Firewall exceptions
- Check third-party antivirus/firewall
- Test with firewall temporarily disabled

## 📈 Performance Tips

### Server Optimization

1. **Resource Monitoring**
   - Monitor CPU and RAM usage
   - Don't over-allocate resources
   - Keep 20% headroom for system

2. **Network Optimization**
   - Use wired Ethernet connection
   - Enable QoS for homelab traffic
   - Monitor network bandwidth

3. **Storage Optimization**
   - Use SSD for better performance
   - Regular cleanup of temporary files
   - Monitor disk space usage

### Client Optimization

1. **Local Caching**
   ```json
   {
     "enable_local_cache": true,
     "cache_timeout": 300
   }
   ```

2. **Connection Management**
   - Enable auto-reconnect
   - Use appropriate heartbeat intervals
   - Monitor connection quality

## 🔄 Maintenance

### Regular Tasks

#### Server Maintenance (Daily)
- Check resource usage
- Monitor client connections
- Review allocation logs

#### Server Maintenance (Weekly)
- Clean expired allocations
- Update resource pools
- Check system health

#### Client Maintenance (Daily)
- Verify connection status
- Check resource allocations
- Monitor local performance

### Backup and Recovery

#### Server Backup
```python
# Backup database
import shutil
shutil.copy2('win10_homelab_server.db', f'backup_{datetime.now().strftime("%Y%m%d")}.db')

# Backup configuration
shutil.copy2('win10_server_settings.json', 'backup_settings.json')
```

#### Client Recovery
```python
# Reset client configuration
os.remove('win11_client_settings.json')
# Client will re-register on next start
```

## 📚 API Reference

### Authentication

```python
# Register client (automatic)
POST /api/v1/clients/register
{
  "name": "Win11-Client",
  "hostname": "WIN11-PC",
  "os_version": "Windows 11",
  "ip_address": "192.168.1.100",
  "mac_address": "00:11:22:33:44:55"
}

# Response includes API key
{
  "client_id": "win10_client_12345",
  "api_key": "generated_api_key_here",
  "status": "registered"
}
```

### Resource Management

```python
# List resources
GET /api/v1/resources

# Allocate resource
POST /api/v1/resources/{resource_id}/allocate
{
  "client_id": "win10_client_12345",
  "amount": 4.0,
  "properties": {"win11_client": true}
}

# Release resource
POST /api/v1/resources/{resource_id}/release
{
  "client_id": "win10_client_12345",
  "allocation_id": "alloc_12345"
}
```

## 🎯 Best Practices

### Security
1. Use strong network security
2. Monitor client connections
3. Regular security updates
4. Limit resource allocations

### Performance
1. Monitor resource usage
2. Don't over-allocate resources
3. Use wired connections
4. Regular system maintenance

### Reliability
1. Enable auto-reconnect
2. Monitor system health
3. Regular backups
4. Test failover procedures

## 🆘 Support

### Getting Help

1. **Check Logs**: `win10_homelab_server.log`, `win11_homelab_client.log`
2. **Verify Configuration**: Check JSON settings files
3. **Test Connectivity**: Use curl to test API endpoints
4. **Monitor Resources**: Check system resource usage

### Common Solutions

- **Port 8080 blocked**: Configure Windows Firewall
- **WMI errors**: Run as Administrator
- **GPU not detected**: Install drivers and GPUtil
- **Connection refused**: Check server is running
- **High latency**: Use wired connection

---

## 🎉 Congratulations!

Your Windows 10 machine is now ready to serve as a homelab server! 

### ✅ What You Have:
- **Windows 10 Server**: Hosting shared resources
- **Resource Management**: eRAM, eGPU, eCPU, storage, network
- **Security**: API authentication and client management
- **Monitoring**: Real-time resource tracking
- **Easy Setup**: GUI launcher for simple management

### 🚀 Next Steps:
1. Start the Windows 10 server using the launcher
2. Connect Windows 11 clients to the server
3. Allocate resources as needed
4. Monitor performance and usage
5. Enjoy your homelab resource sharing!

Your Windows 10 homelab server is ready to boost your Windows 11 experience! 🚀
