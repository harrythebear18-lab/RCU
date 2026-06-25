# 🏠 Homelab Windows 10/11 Ecosystem Setup Guide

## 📋 Overview

This guide will help you set up a complete homelab ecosystem where a Windows 11 server hosts shared resources (eRAM, eGPU, eCPU, etc.) that can be accessed by Windows 10 Home clients over the network.

## 🎯 Architecture

```
┌─────────────────┐    HTTP/REST API    ┌─────────────────┐
│  Windows 11     │◄───────────────────▶│  Windows 10     │
│  Server          │                    │  Home Client     │
│                 │                    │                 │
│ • eRAM Hosting  │                    │ • Resource      │
│ • eGPU Passthrough│                   │   Allocation    │
│ • eCPU Sharing  │                    │ • Remote        │
│ • Storage Pool  │                    │   Monitoring    │
│ • Network Share │                    │ • Auto-Connect  │
└─────────────────┘                    └─────────────────┘
```

## 🚀 Quick Start

### 1. Server Setup (Windows 11)

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Server**
   ```python
   python homelab_server.py
   ```

3. **Launch Dashboard**
   ```python
   python homelab_dashboard.py
   ```

### 2. Client Setup (Windows 10 Home)

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Connect to Server**
   ```python
   python homelab_client.py
   ```

## 📋 Detailed Setup Instructions

### 🔧 Prerequisites

#### Server Requirements (Windows 11)
- **OS**: Windows 11 Pro/Enterprise (recommended)
- **RAM**: 16GB+ (for hosting eRAM)
- **GPU**: NVIDIA/AMD GPU with 4GB+ VRAM
- **CPU**: Multi-core processor
- **Network**: Stable Ethernet connection
- **Storage**: 100GB+ free space
- **Python**: 3.8+ with required packages

#### Client Requirements (Windows 10 Home)
- **OS**: Windows 10 Home/Pro
- **RAM**: 4GB+ minimum
- **Network**: Connection to server
- **Python**: 3.8+ with required packages

### 🖥️ Server Configuration

#### 1. Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv homelab_env
homelab_env\Scripts\activate

# Install required packages
pip install flask flask-cors psutil GPUtil schedule scikit-learn
pip install matplotlib numpy pandas sqlite3
pip install pywin32 wmi nvidia-ml-py3 pynvml
```

#### 2. Configure Server Settings

Edit `server_settings.json`:

```json
{
  "server_name": "Homelab Resource Server",
  "max_clients": 10,
  "session_timeout": 3600,
  "allocation_timeout": 7200,
  "resource_check_interval": 30,
  "enable_authentication": true,
  "enable_encryption": true,
  "max_eram_allocation_gb": 32,
  "enable_egpu_passthrough": true,
  "enable_load_balancing": true
}
```

#### 3. Start the Server

```python
# Method 1: Direct server start
python homelab_server.py

# Method 2: Using the dashboard
python homelab_dashboard.py
# Click "Start Server" button
```

#### 4. Verify Server Status

The server will start on `http://localhost:8080` by default. You can:
- Access the REST API
- View server status at `/api/v1/server/status`
- Monitor resources at `/api/v1/resources`

### 💻 Client Configuration

#### 1. Install Client Dependencies

```bash
# Same virtual environment or new one
pip install flask requests psutil schedule
```

#### 2. Configure Client Settings

Edit `client_settings.json`:

```json
{
  "server_url": "http://SERVER_IP:8080",
  "heartbeat_interval": 30,
  "resource_check_interval": 60,
  "auto_reconnect": true,
  "preferred_resources": {
    "eram": "eram_medium",
    "egpu": "egpu_nvidia_0",
    "ecpu": "ecpu_medium"
  }
}
```

#### 3. Connect to Server

```python
# Method 1: Direct client start
python homelab_client.py

# Method 2: Using the dashboard
python homelab_dashboard.py
# Enter server URL and click "Connect Client"
```

## 🔌 Resource Management

### Available Resource Types

| Resource Type | Description | Typical Use Case |
|---------------|-------------|-----------------|
| **eRAM** | Shared memory pools | Applications needing extra RAM |
| **eGPU** | GPU passthrough | Gaming, ML, rendering |
| **eCPU** | Virtual CPU cores | CPU-intensive tasks |
| **eStorage** | Network storage | File sharing, backups |
| **eNetwork** | Network bandwidth | High-speed transfers |

### Resource Allocation

#### Automatic Allocation
```python
# Auto-allocate preferred resources
allocations = client.auto_allocate_resources()
```

#### Manual Allocation
```python
# Allocate 8GB of eRAM
eram_allocation = client.allocate_eram(8.0)

# Allocate full GPU
gpu_allocation = client.allocate_egpu("egpu_nvidia_0")
```

#### Resource Release
```python
# Release specific allocation
client.release_resource(allocation_id)

# Release all allocations
client.release_all_resources()
```

## 🛡️ Security Configuration

### API Authentication

1. **Generate API Keys**
   ```bash
   # Each client gets unique API key
   curl -X POST http://SERVER:8080/api/v1/auth/generate_key \
        -H "Content-Type: application/json" \
        -d '{"client_id": "client_123", "permissions": ["read", "allocate"]}'
   ```

2. **Use API Keys**
   ```python
   headers = {'X-API-Key': 'your-api-key-here'}
   response = requests.get(url, headers=headers)
   ```

### Network Security

1. **Firewall Configuration**
   - Open port 8080 on server
   - Allow client IP addresses
   - Consider VPN for remote access

2. **SSL/TLS Setup** (Optional)
   ```python
   # Configure HTTPS in server settings
   "ssl_cert": "/path/to/cert.pem",
   "ssl_key": "/path/to/key.pem"
   ```

## 📊 Monitoring and Management

### Dashboard Features

The `homelab_dashboard.py` provides:

- **Server Management**: Start/stop server, view metrics
- **Resource Overview**: Visual allocation charts
- **Client Management**: Connect/disconnect clients
- **Real-time Monitoring**: Live metrics and status

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/server/status` | GET | Server status and metrics |
| `/api/v1/resources` | GET | List available resources |
| `/api/v1/resources/{id}/allocate` | POST | Allocate resource |
| `/api/v1/resources/{id}/release` | POST | Release resource |
| `/api/v1/clients/register` | POST | Register new client |
| `/api/v1/allocations` | GET | List allocations |

### Command Line Tools

```python
# Check server status
curl http://SERVER:8080/api/v1/server/status

# List resources
curl -H "X-API-Key: KEY" http://SERVER:8080/api/v1/resources

# Allocate resource
curl -X POST -H "X-API-Key: KEY" \
     -H "Content-Type: application/json" \
     -d '{"client_id": "client_123", "amount": 8.0}' \
     http://SERVER:8080/api/v1/resources/eram_medium/allocate
```

## 🎮 Use Cases

### 1. Gaming Enhancement
- **Server**: Host powerful GPU
- **Client**: Windows 10 Home laptop
- **Benefit**: Play high-end games on low-end hardware

### 2. Machine Learning
- **Server**: NVIDIA GPU with CUDA
- **Client**: Windows 10 Home workstation
- **Benefit**: Run ML models without local GPU

### 3. Content Creation
- **Server**: High-end CPU + GPU + RAM
- **Client**: Basic laptop
- **Benefit**: Video editing, 3D rendering

### 4. Development Environment
- **Server**: Development server with resources
- **Client**: Multiple development machines
- **Benefit**: Shared development resources

## 🔧 Advanced Configuration

### Custom Resource Pools

Edit server initialization in `homelab_server.py`:

```python
# Custom eRAM pools
eram_pools = [
    {
        'id': 'eram_ultra',
        'name': 'eRAM Ultra Pool',
        'capacity': 32,
        'properties': {'priority': 'ultra', 'max_allocation_gb': 32}
    }
]
```

### Load Balancing

Enable automatic load balancing:

```json
{
  "enable_load_balancing": true,
  "load_balancing_algorithm": "round_robin",
  "max_allocations_per_client": 3
}
```

### Resource Quotas

Set per-client resource limits:

```python
# In server settings
"client_quotas": {
    "default": {"eram": 16, "egpu": 1, "ecpu": 4},
    "premium": {"eram": 32, "egpu": 2, "ecpu": 8}
}
```

## 🚨 Troubleshooting

### Common Issues

#### Server Won't Start
```bash
# Check dependencies
pip list | grep -E "(flask|psutil|GPUtil)"

# Check port usage
netstat -an | grep :8080

# Check logs
type homelab_server.log
```

#### Client Can't Connect
```bash
# Test server connectivity
ping SERVER_IP

# Test HTTP connection
curl -I http://SERVER_IP:8080/api/v1/server/status

# Check client logs
type homelab_client.log
```

#### Resource Allocation Fails
```python
# Check resource availability
curl -H "X-API-Key: KEY" http://SERVER:8080/api/v1/resources

# Check client permissions
# Verify API key has 'allocate' permission
```

### Performance Issues

#### High Latency
- Check network connection
- Reduce heartbeat interval
- Enable local caching

#### Resource Exhaustion
- Monitor server resources
- Adjust allocation limits
- Implement resource quotas

## 📈 Performance Optimization

### Server Optimization

1. **Resource Monitoring**
   ```python
   # Enable detailed monitoring
   "monitoring_interval": 10,
   "performance_logging": true
   ```

2. **Database Optimization**
   ```python
   # Configure SQLite settings
   "database_wal_mode": true,
   "database_cache_size": 10000
   ```

3. **Network Optimization**
   ```python
   # Enable compression
   "enable_compression": true,
   "compression_level": 6
   ```

### Client Optimization

1. **Local Caching**
   ```python
   "enable_local_cache": true,
   "cache_timeout": 300
   ```

2. **Batch Operations**
   ```python
   # Batch resource requests
   "batch_size": 10,
   "batch_timeout": 30
   ```

## 🔄 Maintenance

### Regular Tasks

#### Server Maintenance
1. **Daily**: Check resource usage
2. **Weekly**: Clean expired allocations
3. **Monthly**: Update resource pools
4. **Quarterly**: Review security settings

#### Client Maintenance
1. **Daily**: Verify connection status
2. **Weekly**: Clean local cache
3. **Monthly**: Update client configuration

### Backup and Recovery

#### Server Backup
```python
# Backup database
import shutil
shutil.copy2('homelab_server.db', f'backup_{datetime.now().strftime("%Y%m%d")}.db')

# Backup configuration
shutil.copy2('server_settings.json', 'backup_settings.json')
```

#### Client Recovery
```python
# Reset client configuration
os.remove('client_settings.json')
# Client will re-register on next start
```

## 📚 API Reference

### Authentication

```python
# Generate API key
POST /api/v1/auth/generate_key
{
  "client_id": "client_123",
  "permissions": ["read", "allocate", "release"]
}

# Use API key
headers = {"X-API-Key": "generated_api_key"}
```

### Resource Management

```python
# List resources
GET /api/v1/resources?type=eram

# Allocate resource
POST /api/v1/resources/{resource_id}/allocate
{
  "client_id": "client_123",
  "amount": 8.0,
  "properties": {"priority": "high"}
}

# Release resource
POST /api/v1/resources/{resource_id}/release
{
  "client_id": "client_123",
  "allocation_id": "alloc_12345"
}
```

### Monitoring

```python
# Server metrics
GET /api/v1/monitoring/metrics

# Client status
POST /api/v1/clients/{client_id}/status
{
  "status": "online",
  "local_metrics": {...}
}
```

## 🎯 Best Practices

### Security
1. Use strong API keys
2. Enable authentication
3. Monitor access logs
4. Regular security updates

### Performance
1. Monitor resource usage
2. Implement quotas
3. Use load balancing
4. Optimize network settings

### Reliability
1. Enable auto-reconnect
2. Implement health checks
3. Use redundant resources
4. Regular backups

## 🆘 Support

### Getting Help

1. **Check Logs**: `homelab_server.log`, `homelab_client.log`
2. **Verify Configuration**: Check JSON settings files
3. **Test Connectivity**: Use curl to test API endpoints
4. **Monitor Resources**: Use dashboard for real-time status

### Community

- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Check latest API documentation
- **Examples**: Review sample configurations

---

## 🎉 Congratulations!

You now have a complete homelab ecosystem with:
- ✅ Windows 11 server hosting shared resources
- ✅ Windows 10 Home clients accessing resources
- ✅ Real-time monitoring and management
- ✅ Secure authentication and authorization
- ✅ Load balancing and resource optimization
- ✅ Comprehensive dashboard and tools

Your homelab is ready for production use! 🚀
