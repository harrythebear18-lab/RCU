# 🖥️ RAM Sharing System Documentation

Complete cross-PC RAM sharing with automatic configuration and real-time synchronization.

## 🚀 Overview

The RAM Sharing System allows you to share RAM between multiple computers in your homelab, effectively extending the memory of systems with less RAM by utilizing resources from systems with more RAM.

### Key Features
- **🤖 Intelligent Auto-Detection** - Automatically identifies server vs client roles
- **⚡ One-Click Setup** - Automatic configuration with minimal user input
- **📊 Real-Time Monitoring** - Live data synchronization and performance tracking
- **🔧 Cross-Version Compatibility** - Works between Windows 10 and Windows 11
- **🌐 Multiple Connection Methods** - SMB and iSCSI support for maximum compatibility

## 📋 System Requirements

### Minimum Requirements
- **Windows 10/11** (both systems)
- **4GB RAM** (minimum on server system)
- **Network Connection** (gigabit recommended)
- **Administrator Privileges** (for setup)

### Recommended Setup
- **Server System**: 16GB+ RAM, Windows 11
- **Client System**: Any RAM amount, Windows 10/11
- **Network**: Gigabit Ethernet or faster
- **Python 3.7+** (for GUI features, optional)

## 🎯 Quick Start

### Easiest Method (Recommended)
```batch
# Run this on BOTH systems
Quick_Auto_Connect.bat
```

This single command will:
1. Auto-detect if the system is server or client
2. Configure appropriate settings
3. Establish connection
4. Start monitoring

### GUI Method
```batch
# Interactive launcher with real-time display
Auto_Connect_Launcher.bat
```

### Python Script Method
```bash
# With GUI
python Auto_RAM_Connect.py --gui

# Console mode
python Auto_RAM_Connect.py --console

# Auto-mode (best choice)
python Auto_RAM_Connect.py
```

## 🔧 Manual Configuration

### Server Setup (PC with more RAM)
```batch
# 1. Fix compatibility issues
Fix_Windows_Compatibility.bat

# 2. Create and share RAM disk
Setup_RAM_Sharing.bat

# 3. Verify sharing
net share | findstr RamDisk
```

### Client Setup (PC with less RAM)
```batch
# 1. Test connectivity
ping 192.168.1.186

# 2. Connect to server
Map_RAM_Sharing.bat

# 3. Verify connection
dir Z:\  # Or appropriate drive letter
```

## 📊 Real-Time Monitoring

### GUI Dashboard Features
- **System Role Display** - Server/Client status
- **Connection Status** - Real-time connection state
- **RAM Disk Status** - Availability and usage
- **Performance Metrics** - CPU, memory, network latency
- **Activity Log** - Detailed event tracking

### Console Monitoring
```bash
# Real-time status updates every 2 seconds
📊 Real-Time Status - 14:30:25
🖥️  Role: SERVER
🔗 Connection: connected
💾 RAM Disk: ✅ Available
📈 CPU Usage: 15.2%
🧠 Memory Usage: 45.8%
🌐 Network: time=2ms
--------------------------------------------------
```

## 🌐 Network Configuration

### Default IP Configuration
- **Server IP**: 192.168.1.186 (Windows 11, more RAM)
- **Client IP**: 192.168.1.132 (Windows 10, less RAM)
- **Port**: 445 (SMB), 3260 (iSCSI)

### Custom IP Configuration
Edit the configuration in `Auto_RAM_Connect.py`:
```python
self.server_ip = "YOUR_SERVER_IP"
self.client_ip = "YOUR_CLIENT_IP"
```

## 🔧 Connection Methods

### SMB Sharing (Recommended)
- **Pros**: Most compatible, works on all Windows versions
- **Cons**: Slightly higher latency than iSCSI
- **Setup**: Automatic with `Setup_RAM_Sharing.bat`

### iSCSI Target (Performance)
- **Pros**: Lower latency, block-level access
- **Cons**: Requires Windows Pro/Enterprise
- **Setup**: Automatic with PowerShell scripts

## 🛠️ Troubleshooting

### Common Issues

#### "Cannot reach server"
```batch
# Test network connectivity
ping 192.168.1.186

# Check Windows Firewall
# Allow File and Printer Sharing
# Allow iSCSI Service
```

#### "Python not found"
```batch
# Use batch alternatives
Quick_Auto_Connect.bat

# Or install Python
# https://python.org/downloads/
```

#### "Access denied"
```batch
# Run as Administrator
# Right-click → Run as administrator

# Check user permissions
net user
```

#### "RAM disk not found"
```batch
# Check if server is running
dir \\192.168.1.186\RamDisk

# Restart server
Cleanup_RAM_Sharing.bat
Setup_RAM_Sharing.bat
```

### Performance Issues

#### Slow Transfer Speeds
- Check network cable (use gigabit)
- Disable power saving on network adapter
- Use iSCSI instead of SMB for better performance

#### High Latency
- Check network interference
- Use direct cable connection if possible
- Disable QoS if not needed

## 📈 Performance Expectations

### Network Performance
- **Gigabit Ethernet**: 100+ MB/s transfer speeds
- **SMB Sharing**: 80-100 MB/s typical
- **iSCSI Target**: 100+ MB/s with low latency

### System Impact
- **Server CPU**: 2-5% usage during operation
- **Client CPU**: 1-3% usage during operation
- **Network**: Utilizes available bandwidth efficiently

## 🔧 Advanced Configuration

### Custom RAM Size
Edit `Robust_RAM_Sharing.ps1`:
```powershell
# Default: 4GB
$RAMSizeGB = 8  # Change to 8GB
```

### Custom Drive Letter
```powershell
# Default: R:
$DriveLetter = "S"  # Change to S:
```

### Performance Tuning
```batch
# Optimize for performance
netsh interface tcp set global autotuninglevel=highlyrestricted
netsh interface tcp set global chimney=enabled
netsh interface tcp set global rss=enabled
```

## 🎮 Integration with Other Tools

### Homelab Launcher
The RAM sharing system is fully integrated into:
- **homelab_launcher.py** - Main dashboard with RAM sharing category
- **homelab_dashboard.py** - Monitoring dashboard with real-time stats

### Subnet Portal
Accessible through the Subnet Portal for centralized management.

## 📚 File Structure

```
Homelab Tools/
├── Auto_RAM_Connect.py              # Main auto-connection script
├── Auto_Connect_Launcher.bat        # Interactive launcher
├── Quick_Auto_Connect.bat           # One-click solution
├── Integrated_RAM_Launcher.py       # Advanced GUI launcher
├── Universal_Launcher.bat            # Universal launcher
├── Robust_RAM_Sharing.ps1           # PowerShell engine
├── Windows_Compatibility_Fix.ps1    # Compatibility fixes
├── Setup_RAM_Sharing.bat            # Server setup
├── Map_RAM_Sharing.bat              # Client connection
├── Cleanup_RAM_Sharing.bat          # Cleanup utility
├── RAM_Sharing_GUI.py               # Full GUI interface
├── RAM_Sharing_Simple_GUI.py        # Console-based GUI
└── RAM_Sharing_Documentation.md     # This file
```

## 🔄 Updates and Maintenance

### Regular Maintenance
```batch
# Check system status
Auto_Connect_Launcher.bat → Option 6 (Test Network)

# Update compatibility fixes
Fix_Windows_Compatibility.bat

# Cleanup and reset
Cleanup_RAM_Sharing.bat
```

### Version Updates
- Check GitHub repository for latest versions
- Backup configuration before updating
- Test updates on non-production systems first

## 🆘 Support

### Getting Help
1. Check this documentation first
2. Run `GUI_Troubleshooting.bat` for diagnostics
3. Check activity logs in the GUI
4. Verify network connectivity
5. Ensure administrator privileges

### Community Support
- GitHub Issues: Report bugs and request features
- Documentation: Check for updates and guides
- Community Forums: Share experiences and solutions

---

**RAM Sharing System** - Transform your homelab with distributed memory! 🚀
