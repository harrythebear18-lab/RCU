# 🔧 Admin Auto-Configuration Guide

## Overview

The Homelab Tools now include automatic configuration for admin-level systems, providing one-click setup with optimal port allocation, authentication bypass, and performance optimization.

## 🚀 Quick Start

### For Admin Systems (Recommended)

```bash
# Clone and navigate to the repository
git clone https://github.com/harrythebear18-lab/Homelab-Tools.git
cd Homelab-Tools

# Run admin auto-configuration
cd "Core Services"
python admin_auto_config.py

# Launch with admin settings
python admin_startup.py
```

## 🔧 Features

### Automatic Port Configuration
- **Smart Port Allocation**: Automatically finds available ports
- **Conflict Resolution**: Handles port conflicts gracefully
- **Service Mapping**: Maps optimal ports for each service
- **Firewall Setup**: Automatically configures Windows firewall rules

### Admin Authentication
- **Bypass Authentication**: No login required for admin systems
- **Session Management**: Extended session timeouts (24 hours)
- **Anonymous Access**: Allow anonymous connections on trusted networks
- **Multi-Session Support**: Up to 100 concurrent sessions

### Performance Optimization
- **Auto-Detection**: Detects CPU cores, memory, and hardware
- **Thread Pool Sizing**: Optimizes worker threads automatically
- **Cache Configuration**: Sets optimal cache sizes (1GB default)
- **Resource Limits**: Configures appropriate resource limits

## 📊 Default Port Configuration

| Service | Default Port | Auto-Configured |
|---------|--------------|-----------------|
| Homelab Portal | 8080 | ✅ |
| REST API | 8081 | ✅ |
| Unified Dashboard | 8082 | ✅ |
| Network Monitor | 8083 | ✅ |
| CPU Monitor | 8084 | ✅ |
| GPU Monitor | 8085 | ✅ |
| Subnet Portal | 8090 | ✅ |
| RDMA Portal | 8091 | ✅ |
| Backup System | 8092 | ✅ |
| Media Server | 8093 | ✅ |
| VPN Gateway | 8094 | ✅ |
| Web Dashboard | 8095 | ✅ |

## 🔐 Security Settings

### Admin Configuration
```json
{
  "auth_levels": {
    "default_level": "admin",
    "require_auth": false,
    "allow_anonymous": true,
    "session_timeout": 86400,
    "max_sessions": 100
  },
  "security": {
    "firewall_rules": "allow_all",
    "ssl_required": false,
    "encryption": "optional",
    "api_key_required": false
  }
}
```

### Network Configuration
```json
{
  "network": {
    "bind_all_interfaces": true,
    "auto_discovery": true,
    "p2p_enabled": true,
    "lan_broadcast": true
  }
}
```

## 🖥️ System Detection

The auto-configuration system detects:

- **Operating System**: Windows 10/11 with version details
- **Hardware**: CPU, memory, disk space, network interfaces
- **Admin Privileges**: Automatic detection of admin rights
- **Python Version**: Compatibility checking
- **Available Ports**: Real-time port availability scanning

## 📝 Configuration Files

### Generated Files
- `admin_config.json` - Main configuration file
- `admin_startup.py` - Optimized startup script
- `unified_config.json` - Unified configuration for all services
- `admin_auto_config.log` - Configuration log

### Service Updates
- `homelab_portal.py` - Updated with new port
- `rest_api.py` - Updated with new port
- All service configurations automatically updated

## 🚀 Usage Examples

### Basic Admin Setup
```python
from admin_auto_config import AdminAutoConfig

# Create auto-config instance
auto_config = AdminAutoConfig()

# Run full configuration
config = auto_config.run_auto_configuration()

# Access configuration
print(f"Portal Port: {config['ports']['homelab_portal']}")
print(f"API Port: {config['ports']['rest_api']}")
```

### Custom Port Configuration
```python
# Override default ports
custom_config = {
    'ports': {
        'homelab_portal': 9000,
        'rest_api': 9001
    }
}

auto_config = AdminAutoConfig()
auto_config.config.update(custom_config)
config = auto_config.run_auto_configuration()
```

## 🔍 Troubleshooting

### Port Conflicts
- System automatically detects port conflicts
- Finds next available port in range
- Updates all configuration files accordingly

### Admin Privileges
- Run as Administrator for full functionality
- Some features limited without admin rights
- Firewall configuration requires admin access

### Service Startup
- Check `admin_auto_config.log` for errors
- Verify port availability with `netstat -an`
- Ensure all dependencies are installed

## 📈 Performance Monitoring

The admin configuration includes:
- **Real-time Monitoring**: CPU, memory, network, disk usage
- **Performance Metrics**: Historical data and trends
- **Resource Optimization**: Automatic resource allocation
- **Health Checks**: Service health monitoring

## 🔄 Updates and Maintenance

### Re-running Configuration
```bash
# Re-run to update settings
python admin_auto_config.py

# Restart services with new config
python admin_startup.py
```

### Configuration Reset
```bash
# Reset to defaults
del admin_config.json
python admin_auto_config.py
```

## 📚 API Integration

### REST API Endpoints
```python
import requests

# Get system status
response = requests.get('http://localhost:8081/api/system/status')
status = response.json()

# Get configuration
response = requests.get('http://localhost:8081/api/config')
config = response.json()
```

### WebSocket Connections
```javascript
// Connect to real-time updates
const ws = new WebSocket('ws://localhost:8081/ws/system');
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('System update:', data);
};
```

## 🎯 Best Practices

1. **Run as Administrator**: For full functionality
2. **Check Logs**: Monitor `admin_auto_config.log`
3. **Verify Ports**: Ensure ports are available
4. **Test Services**: Verify all services start correctly
5. **Monitor Performance**: Use built-in monitoring tools
6. **Regular Updates**: Re-run configuration after updates

## 📞 Support

For issues with admin auto-configuration:
1. Check the log files
2. Verify admin privileges
3. Test port availability
4. Review configuration files
5. Consult the main documentation

---

**Note**: Admin auto-configuration is designed for trusted network environments. Ensure proper security measures are in place for production deployments.
