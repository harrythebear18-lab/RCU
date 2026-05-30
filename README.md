# RCU - Resource Cleanup & Unified System

A comprehensive Windows system optimization suite integrating Resource Cleanup, RDMA (Remote Direct Memory Access), and Homelab Tools into a unified platform for advanced system management, performance optimization, and homelab automation.

## Overview

RCU is an all-in-one system optimization and management platform that combines three powerful toolsets:

- **Resource Cleanup**: Advanced RAM monitoring, cleanup, and system optimization tools
- **RDMA**: High-performance Remote Direct Memory Access tools and drivers
- **Homelab Tools**: Comprehensive homelab management, monitoring, and automation system

## Features

### Resource Cleanup (Windows 11 Resource Optimization System)

**Command-Line Tools:**
- 🧹 Comprehensive RAM cleanup (`ram_cleanup_script.py`)
- 🗑️ Clears Windows system cache
- 🔄 Closes unnecessary processes
- 📊 Memory usage reporting
- ⚡ Performance optimization
- 🖥️ CPU monitoring and optimization (`cpu_cleanup_script.py`)
- 🎮 GPU monitoring and cleanup (`gpu_cleanup_script.py`)

**GUI Applications:**
- 📈 Real-time RAM monitoring (`ram_monitor_gui.py`)
- 📊 Live memory usage graph
- 🧹 One-click cache clearing
- ⚙️ Auto-cleanup when usage >80%
- 🎨 Modern dark theme interface
- 📱 Intuitive controls
- 🖥️ CPU Monitor GUI (`cpu_monitor_gui.py`)
- 🎮 GPU Monitor GUI (`gpu_monitor_gui.py`)
- 📊 System Dashboard (`system_dashboard.py`)
- ⚡ Resource Optimizer (`resource_optimizer.py`)
- 🔧 Overclocking Dashboard (`overclocking_dashboard.py`)
- 🚀 Performance Optimizer (`performance_optimizer.py`)

### RDMA (Remote Direct Memory Access)

**High-Performance Tools:**
- 🔌 Ultra-low latency DMA operations (`ultra_low_latency_dma.c`)
- 💾 Virtual DMA driver (`virtual_dma_driver.c`)
- 🌐 Raw network bypass (`raw_network_bypass.py`)
- ⚡ Real-time CPU optimizer (`realtime_cpu_optimizer.py`)
- 📊 Performance profiler (`performance_profiler.py`)
- 🔒 Security manager (`security_manager.py`)
- 🛡️ Fault tolerance manager (`fault_tolerance_manager.py`)
- 🖥️ RDMA Desktop App (`rdma_desktop_app.py`)
- 🌐 RDMA REST API (`rdma_rest_api.py`)
- 📈 Ultra latency benchmark (`ultra_latency_benchmark.py`)

### Homelab Tools

**Management & Automation:**
- 🏠 Homelab Launcher (`homelab_launcher.py`)
- 🚀 Unified Launcher (`unified_launcher.py`)
- 🔐 PC Authentication System (`pc_auth_system.py`)
- 📊 Streamlined Dashboard (`streamlined_dashboard.py`)
- 🌐 RAM Sharing GUI (`RAM_Sharing_GUI.py`)
- 🔧 Auto Connect Launcher (`Auto_RAM_Connect.py`)
- 📋 Task Scheduler (`task_scheduler.py`)
- 💾 Backup Manager (`backup_manager.py`)
- 🌍 Internationalization (`internationalization.py`)

**Monitoring & Diagnostics:**
- 📈 System Health Scorer (`system_health_scorer.py`)
- 📊 Performance Reports (`performance_reports.py`)
- 🔍 System Audit Tools
- 🧪 Test Suites and Verification Tools
- 📝 Logging and Error Reporting

## Installation

1. **Install Python** (if not already installed):
   - Download Python 3.8+ from [python.org](https://python.org)
   - Make sure to check "Add Python to PATH" during installation

2. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

   For RDMA components, also install:
   ```bash
   pip install -r RDMA/requirements.txt
   ```

   For Homelab Tools, also install:
   ```bash
   pip install -r Homelab_Tools/requirements.txt
   ```

3. **RDMA Driver Installation** (optional, for advanced DMA operations):
   - See `RDMA/COMPLETE_INSTALLATION_GUIDE.md` for detailed instructions
   - Run `RDMA/install.py` for automated setup
   - For Windows: Use `RDMA/windows_build.bat`
   - For Linux: Use `RDMA/build_kernel_driver.sh`

## Usage

### Resource Cleanup

**Command-Line Tools:**
```bash
# RAM cleanup
python ram_cleanup_script.py

# CPU cleanup
python cpu_cleanup_script.py

# GPU cleanup
python gpu_cleanup_script.py
```

**GUI Applications:**
```bash
# RAM Monitor GUI
python ram_monitor_gui.py

# CPU Monitor GUI
python cpu_monitor_gui.py

# GPU Monitor GUI
python gpu_monitor_gui.py

# System Dashboard
python system_dashboard.py

# Resource Optimizer
python resource_optimizer.py

# Overclocking Dashboard
python overclocking_dashboard.py
```

**For best results:**
- Run as Administrator (right-click → "Run as administrator")
- Use before gaming sessions or when system feels sluggish

### RDMA Tools

**Desktop Application:**
```bash
python RDMA/rdma_desktop_app.py
```

**REST API Server:**
```bash
python RDMA/rdma_rest_api.py
```

**Performance Benchmarking:**
```bash
python RDMA/ultra_latency_benchmark.py
```

**Driver Installation:**
```bash
# Windows
RDMA/windows_build.bat

# Linux
bash RDMA/build_kernel_driver.sh
```

### Homelab Tools

**Unified Launcher:**
```bash
python unified_launcher.py
```

**Homelab Launcher:**
```bash
python Homelab_Tools/homelab_launcher.py
```

**RAM Sharing GUI:**
```bash
python Homelab_Tools/RAM_Sharing_GUI.py
```

**PC Authentication:**
```bash
python pc_auth_gui.py
```

**System Dashboard:**
```bash
python streamlined_dashboard.py
```

## System Requirements

**Minimum Requirements:**
- Windows 10/11 (recommended)
- Python 3.8 or higher
- 4GB+ RAM recommended
- Administrator privileges (for full functionality)

**RDMA Requirements:**
- Compatible network hardware (RDMA-capable NICs)
- Additional driver installation for DMA operations
- Linux kernel headers (for Linux driver compilation)

**Homelab Requirements:**
- Network connectivity for remote management
- Sufficient disk space for backups and logs
- Multiple machines for full homelab functionality

## Safety Features

**Resource Cleanup:**
- **Safe Process Termination**: Only closes non-essential processes using less than 500MB
- **Non-Destructive**: Clears only temporary files and caches
- **Reversible**: All operations are safe and don't harm system stability
- **Monitoring**: Real-time feedback on memory changes

**RDMA:**
- **Driver Safety**: Extensive testing and validation before driver deployment
- **Fault Tolerance**: Automatic recovery and error handling
- **Security Manager**: Comprehensive security checks and validations
- **Network Isolation**: Safe network bypass operations

**Homelab Tools:**
- **Authentication**: Secure PC authentication system
- **Backup System**: Automatic backup and restore functionality
- **Audit Logging**: Comprehensive logging of all operations
- **Permission Management**: Role-based access control

## Troubleshooting

### Common Issues

1. **"Access Denied" Errors**:
   - Run the script as Administrator
   - Right-click → "Run as administrator"

2. **GUI Won't Start**:
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version: `python --version` (should be 3.8+)
   - Check for missing dependencies in RDMA or Homelab Tools directories

3. **RDMA Driver Issues**:
   - Ensure compatible hardware is installed
   - Check driver installation logs
   - Run RDMA/install.py for automated setup
   - Consult RDMA/COMPLETE_INSTALLATION_GUIDE.md

4. **Homelab Connection Issues**:
   - Verify network connectivity between machines
   - Check firewall settings
   - Ensure proper authentication credentials
   - Review homelab configuration files

5. **No Memory Improvement**:
   - Some systems may already be optimized
   - Try closing applications manually before running cleanup
   - Restart your computer if memory usage remains high

### Performance Tips

**Resource Cleanup:**
- **Before Gaming**: Run the cleanup script 5-10 minutes before starting games
- **Regular Maintenance**: Use the GUI app to monitor memory usage patterns
- **Auto-cleanup**: Enable auto-cleanup for hands-free optimization
- **Monitor Trends**: Use the graph to identify memory-hungry applications

**RDMA:**
- **Network Optimization**: Use RDMA for high-throughput, low-latency applications
- **Driver Updates**: Keep RDMA drivers updated for best performance
- **Benchmarking**: Regularly run performance benchmarks to monitor DMA efficiency
- **Resource Allocation**: Properly allocate DMA resources for optimal performance

**Homelab Tools:**
- **Scheduled Tasks**: Use the task scheduler for automated maintenance
- **Regular Backups**: Schedule automatic backups of homelab configurations
- **Monitoring**: Use the dashboard to monitor all homelab components
- **Load Balancing**: Distribute workload across homelab machines for optimal performance

## Project Structure

```
RCU/
├── Resource Cleanup/          # Windows 11 Resource Optimization System
│   ├── ram_cleanup_script.py
│   ├── ram_monitor_gui.py
│   ├── cpu_monitor_gui.py
│   ├── gpu_monitor_gui.py
│   ├── system_dashboard.py
│   ├── resource_optimizer.py
│   ├── overclocking_dashboard.py
│   └── ...
├── RDMA/                     # Remote Direct Memory Access Tools
│   ├── rdma_desktop_app.py
│   ├── rdma_rest_api.py
│   ├── ultra_low_latency_dma.c
│   ├── virtual_dma_driver.c
│   ├── windows_dma_driver.cpp
│   ├── COMPLETE_INSTALLATION_GUIDE.md
│   └── ...
├── Homelab_Tools/            # Homelab Management System
│   ├── homelab_launcher.py
│   ├── RAM_Sharing_GUI.py
│   ├── pc_auth_system.py
│   ├── streamlined_dashboard.py
│   ├── task_scheduler.py
│   ├── backup_manager.py
│   └── ...
├── legacy_backup/            # Backup of original files
├── requirements.txt          # Main dependencies
└── README.md                 # This documentation file
```

## File Descriptions

### Resource Cleanup
- `ram_cleanup_script.py` - Command-line RAM cleanup utility
- `ram_monitor_gui.py` - GUI application with real-time monitoring
- `cpu_monitor_gui.py` - CPU monitoring and optimization GUI
- `gpu_monitor_gui.py` - GPU monitoring and optimization GUI
- `system_dashboard.py` - Comprehensive system monitoring dashboard
- `resource_optimizer.py` - Advanced resource optimization with dependency checking
- `overclocking_dashboard.py` - System overclocking management
- `performance_optimizer.py` - Performance optimization tools

### RDMA
- `rdma_desktop_app.py` - Desktop application for RDMA management
- `rdma_rest_api.py` - REST API for RDMA operations
- `ultra_low_latency_dma.c` - Ultra-low latency DMA driver (C)
- `virtual_dma_driver.c` - Virtual DMA driver implementation (C)
- `windows_dma_driver.cpp` - Windows DMA driver (C++)
- `performance_profiler.py` - RDMA performance profiling tools
- `security_manager.py` - RDMA security management
- `COMPLETE_INSTALLATION_GUIDE.md` - Detailed RDMA installation guide

### Homelab Tools
- `homelab_launcher.py` - Main homelab launcher application
- `RAM_Sharing_GUI.py` - RAM sharing management GUI
- `pc_auth_system.py` - PC authentication and security system
- `streamlined_dashboard.py` - Streamlined homelab dashboard
- `task_scheduler.py` - Task scheduling and automation
- `backup_manager.py` - Backup and restore management
- `internationalization.py` - Multi-language support
- `system_health_scorer.py` - System health assessment tools

### Configuration
- `requirements.txt` - Main Python package dependencies
- `README.md` - This documentation file

## Advanced Usage

### Resource Cleanup Customization

**Customizing Safe-to-Close Processes:**
Edit the `safe_to_close` list in `ram_cleanup_script.py` to add or remove processes:
```python
safe_to_close = [
    'notepad.exe', 'mspaint.exe', 'calc.exe',
    # Add your custom processes here
]
```

**Scheduling Automatic Cleanup:**
You can use Windows Task Scheduler to run the cleanup script automatically:
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., daily at specific time)
4. Action: "Start a program"
5. Program: `python`
6. Arguments: `"path\to\ram_cleanup_script.py"`

### RDMA Advanced Configuration

**Custom DMA Operations:**
Modify DMA parameters in `RDMA/ultra_low_latency_dma.c` for specific hardware configurations.

**Network Bypass Configuration:**
Configure network bypass settings in `RDMA/raw_network_bypass.py` for optimal performance.

**Performance Tuning:**
Use `RDMA/performance_profiler.py` to analyze and optimize DMA operations.

### Homelab Tools Advanced Configuration

**Custom Homelab Setup:**
Modify homelab configuration in `Homelab_Tools/homelab_config.ini` for specific network setups.

**Authentication Configuration:**
Configure PC authentication settings in `pc_auth_system.py` for enhanced security.

**Task Automation:**
Create custom tasks using `task_scheduler.py` for automated homelab management.

## Support

For issues or suggestions:
- Check the troubleshooting section above
- Ensure all dependencies are properly installed
- Verify you're running as Administrator for full functionality
- Consult component-specific documentation:
  - RDMA: See `RDMA/COMPLETE_INSTALLATION_GUIDE.md`
  - Homelab Tools: See `Homelab_Tools/README.md`
  - Resource Cleanup: See individual tool documentation

## Documentation

- **Resource Cleanup**: See individual tool documentation and inline comments
- **RDMA**: `RDMA/README.md` and `RDMA/COMPLETE_INSTALLATION_GUIDE.md`
- **Homelab Tools**: `Homelab_Tools/README.md` and various guide files
- **System Audit**: `SYSTEM_AUDIT_REPORT.md` for comprehensive system analysis

## Contributing

This is a unified project combining three major toolsets. Contributions are welcome for:
- Resource optimization algorithms
- RDMA driver improvements
- Homelab automation features
- Documentation enhancements
- Bug fixes and performance improvements

## License

See individual component directories for specific licensing information.

---

**Disclaimer**: This unified platform is designed for system optimization, high-performance networking, and homelab management. While extensive safety features are implemented, always save important work before running cleanup operations, and ensure proper backups before making system changes. RDMA operations require compatible hardware and proper driver installation. Homelab tools require network configuration and proper authentication setup.
