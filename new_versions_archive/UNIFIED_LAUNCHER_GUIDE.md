# 🚀 Unified Homelab Launcher Guide

## 📋 Overview

The Unified Homelab Launcher provides a single, easy-to-use interface for connecting to all homelab dashboards and tools, or running them in solo mode. It seamlessly integrates the streamlined homelab system, PC authentication, and legacy Homelab Tools into one cohesive launcher.

## 🎯 Key Features

### **🔧 Easy Mode Switching**
- **Dashboard Mode**: Start all dashboard tools for complete management
- **Solo Mode**: Run individual tools in standalone mode
- **Integrated Mode**: Full system with authentication
- **Auth Mode**: Authentication tools only
- **Legacy Mode**: Original Homelab Tools compatibility

### **📊 Tool Management**
- **Automatic Discovery**: Discovers all available homelab tools
- **Status Monitoring**: Real-time tool status and health checks
- **Dependency Management**: Automatic dependency resolution
- **Process Management**: Start, stop, and monitor tool processes

### **🌐 Easy Connection**
- **One-Click Launch**: Start tools with a single click
- **URL Management**: Automatic URL opening for web interfaces
- **Port Management**: Automatic port allocation and conflict resolution
- **Configuration Management**: Centralized settings management

## 🚀 Quick Start

### Installation

1. **Navigate to the homelab directory**
   ```bash
   cd "C:\Users\htsou\Desktop\Ram clean up"
   ```

2. **Install Dependencies**
   ```bash
   pip install psutil tkinter webbrowser
   ```

3. **Start the Launcher GUI**
   ```bash
   python launcher_gui.py
   ```

### First Run

1. **Launch the GUI**: Run `python launcher_gui.py`
2. **Select Mode**: Choose your preferred operation mode
3. **Start Tools**: Click on tools to start them
4. **Monitor Status**: Watch the status monitoring section

## 🔧 Operation Modes

### Dashboard Mode

**Purpose**: Complete homelab management with all dashboard tools

**Tools Started**:
- Streamlined Dashboard (main interface)
- PC Authentication GUI (peer management)

**Use Case**: Full homelab management with visual interface

**Configuration**:
```json
{
  "dashboard_mode_tools": [
    "streamlined_dashboard",
    "pc_auth_gui"
  ]
}
```

### Solo Mode

**Purpose**: Run individual tools in standalone mode

**Tools Started**:
- Streamlined Homelab System (core system)
- PC Authentication System (authentication backend)

**Use Case**: Lightweight operation without GUI overhead

**Configuration**:
```json
{
  "solo_mode_tools": [
    "streamlined_homelab",
    "pc_auth_system"
  ]
}
```

### Integrated Mode

**Purpose**: Full system with authentication and resource sharing

**Tools Started**:
- PC Authentication System (authentication backend)
- Streamlined Homelab System (core system)
- Integrated Homelab with Auth (full integration)

**Use Case**: Complete homelab with secure PC-to-PC communication

**Startup Order**:
1. PC Authentication System
2. Streamlined Homelab System
3. Integrated Homelab with Auth

### Auth Mode

**Purpose**: Authentication and peer management only

**Tools Started**:
- PC Authentication System (backend)
- PC Authentication GUI (management interface)

**Use Case**: Manage PC authentication without resource sharing

### Legacy Mode

**Purpose**: Compatibility with original Homelab Tools

**Tools Available**:
- Homelab Tools Launcher
- Homelab Portal
- Auto RAM Connect
- Other legacy tools

**Use Case**: Use existing Homelab Tools alongside new system

## 📊 Tool Registry

### Core Tools

| Tool ID | Name | Mode | Description | Port | GUI |
|---------|------|------|-------------|------|-----|
| `streamlined_dashboard` | Streamlined Dashboard | Dashboard | Main dashboard interface | 8080 | ✅ |
| `streamlined_homelab` | Streamlined Homelab System | Solo | Core homelab system | - | ❌ |
| `pc_auth_gui` | PC Authentication GUI | Auth | Authentication management | 8081 | ✅ |
| `pc_auth_system` | PC Authentication System | Solo | Authentication backend | 8083 | ❌ |
| `integrated_homelab` | Integrated Homelab with Auth | Integrated | Full integrated system | - | ❌ |

### Legacy Tools

| Tool ID | Name | Mode | Description | Status |
|---------|------|------|-------------|--------|
| `homelab_launcher` | Homelab Tools Launcher | Legacy | Original launcher | ✅ |
| `homelab_portal` | Homelab Portal | Legacy | Main portal system | ✅ |
| `auto_ram_connect` | Auto RAM Connect | Legacy | RAM sharing tool | ✅ |

## 🖥️ GUI Interface

### Main Sections

#### 1. Mode Selection
- **Mode Buttons**: Large buttons for each operation mode
- **Mode Descriptions**: Clear descriptions of what each mode does
- **Visual Indicators**: Current mode highlighted
- **One-Click Switching**: Easy mode switching

#### 2. Tool Management
- **Current Mode Tools**: Tools relevant to current mode
- **All Tools**: Complete tool registry
- **Running Tools**: Currently running tools
- **Tool Actions**: Start, stop, open URL

#### 3. Status Monitoring
- **Real-time Status**: Live system status updates
- **Tool Status**: Individual tool status information
- **Event Logging**: Recent events and activities
- **Export Function**: Export status reports

### Tool Actions

#### Start Tool
- **Dependency Check**: Automatically starts dependencies
- **Process Management**: Tracks process ID and status
- **Port Allocation**: Automatic port assignment
- **URL Generation**: Creates web interface URLs

#### Stop Tool
- **Graceful Shutdown**: Attempts graceful termination
- **Force Kill**: Force kills if graceful fails
- **Cleanup**: Cleans up resources and processes
- **Status Update**: Updates tool status

#### Open URL
- **Web Interface**: Opens web-based tools in browser
- **Automatic Detection**: Detects available URLs
- **Port Resolution**: Uses correct port for URL
- **Error Handling**: Handles missing URLs gracefully

## ⚙️ Configuration

### Settings File

**Location**: `launcher_settings.json`

**Default Settings**:
```json
{
  "default_mode": "dashboard",
  "auto_start_tools": [],
  "auto_discover": true,
  "check_dependencies": true,
  "health_check_interval": 30,
  "max_concurrent_tools": 5,
  "tool_timeout": 60,
  "preferred_ports": {
    "streamlined_dashboard": 8080,
    "pc_auth_gui": 8081,
    "streamlined_homelab": 8082,
    "pc_auth_system": 8083
  },
  "solo_mode_tools": ["streamlined_homelab", "pc_auth_system"],
  "dashboard_mode_tools": ["streamlined_dashboard", "pc_auth_gui"],
  "legacy_tools_path": "C:/Users/htsou/Desktop/Homelab Tools"
}
```

### Port Configuration

**Default Ports**:
- Streamlined Dashboard: 8080
- PC Authentication GUI: 8081
- Streamlined Homelab: 8082
- PC Authentication System: 8083

**Port Management**:
- **Automatic Allocation**: Automatically assigns free ports
- **Conflict Resolution**: Detects and resolves port conflicts
- **Custom Ports**: Override default ports in settings
- **Port Range**: Uses 8080-8090 range by default

### Tool Dependencies

**Dependency Types**:
- **Core Dependencies**: Required for tool operation
- **Optional Dependencies**: Enhanced functionality
- **GUI Dependencies**: Required for GUI tools
- **Authentication Dependencies**: Required for auth tools

**Dependency Resolution**:
- **Automatic Start**: Automatically starts dependencies
- **Order Management**: Starts in correct order
- **Failure Handling**: Handles dependency failures
- **Circular Detection**: Prevents circular dependencies

## 🔄 Usage Examples

### Example 1: Dashboard Mode

**Scenario**: Full homelab management

**Steps**:
1. Launch `python launcher_gui.py`
2. Click "Dashboard Mode" button
3. Click "▶️ Start Selected" on Streamlined Dashboard
4. Click "▶️ Start Selected" on PC Authentication GUI
5. Monitor status in the monitoring section

**Result**: Complete homelab management interface

### Example 2: Solo Mode

**Scenario**: Lightweight operation

**Steps**:
1. Launch `python launcher_gui.py`
2. Click "Solo Mode" button
3. Tools start automatically in background
4. Monitor status in monitoring section

**Result**: Lightweight homelab system running

### Example 3: Integrated Mode

**Scenario**: Full system with authentication

**Steps**:
1. Launch `python launcher_gui.py`
2. Click "Integrated Mode" button
3. Wait for all tools to start (automatic)
4. Monitor status and check authentication

**Result**: Complete integrated system with PC authentication

### Example 4: Tool Management

**Scenario**: Start specific tool

**Steps**:
1. Launch `python launcher_gui.py`
2. Go to "All Tools" tab
3. Select desired tool
4. Click "▶️ Start Selected"
5. Monitor tool status

**Result**: Individual tool running

## 📊 Status Monitoring

### Tool Status Types

| Status | Description | Color |
|--------|-------------|-------|
| **Running** | Tool is actively running | 🟢 Green |
| **Stopped** | Tool is not running | ⚪ Gray |
| **Error** | Tool encountered error | 🔴 Red |
| **Available** | Tool is available to start | 🔵 Blue |
| **Unknown** | Tool status unknown | 🟡 Yellow |

### Status Information

**Tool Details**:
- **Process ID**: Running process ID
- **Port**: Assigned port number
- **URL**: Web interface URL
- **Last Run**: Last execution time
- **Dependencies**: Required dependencies

**System Status**:
- **Total Tools**: Number of registered tools
- **Running Tools**: Number of currently running tools
- **Tools by Mode**: Tool count per mode
- **System Settings**: Current configuration

### Event Logging

**Event Types**:
- **Start**: Tool started successfully
- **Stop**: Tool stopped successfully
- **Error**: Tool encountered error
- **Mode Switch**: Operation mode changed
- **Status Update**: System status updated

**Log Format**:
```
[HH:MM:SS] 🔄 Launcher status updated
[HH:MM:SS] ▶️ Tool started successfully
[HH:MM:SS] 📊 3 tools running
```

## 🔧 Advanced Features

### Auto-Start Configuration

**Setting Up Auto-Start**:
```json
{
  "auto_start_tools": [
    "streamlined_homelab",
    "pc_auth_system"
  ]
}
```

**Auto-Start Behavior**:
- Tools start automatically when launcher launches
- Dependencies are resolved automatically
- Failed tools are logged but don't block others

### Health Monitoring

**Health Checks**:
- **Process Monitoring**: Checks if processes are running
- **Port Availability**: Checks if ports are accessible
- **Dependency Status**: Verifies dependencies are running
- **Resource Usage**: Monitors system resource usage

**Health Check Interval**:
- **Default**: 30 seconds
- **Configurable**: Adjustable in settings
- **Real-time**: Updates status in real-time

### Tool Discovery

**Automatic Discovery**:
- **Directory Scanning**: Scans for tool scripts
- **Legacy Detection**: Finds legacy Homelab Tools
- **Path Resolution**: Resolves script paths
- **Tool Registration**: Registers discovered tools

**Manual Registration**:
- **Custom Tools**: Add custom tools to registry
- **External Tools**: Register external applications
- **Configuration**: Configure tool properties
- **Dependencies**: Set up tool dependencies

## 🛡️ Security Features

### Process Management

**Process Isolation**:
- **Separate Processes**: Each tool runs in separate process
- **Resource Limits**: Limits per-tool resource usage
- **Permission Management**: Controls tool permissions
- **Cleanup**: Proper cleanup on tool shutdown

**Security Considerations**:
- **Script Validation**: Validates tool scripts before execution
- **Path Security**: Secures tool file paths
- **Network Access**: Controls network access per tool
- **Data Protection**: Protects sensitive configuration data

### Authentication Integration

**PC Authentication**:
- **Peer Discovery**: Discovers authenticated peers
- **Trust Management**: Manages trusted peer relationships
- **Session Management**: Handles authentication sessions
- **Resource Access**: Controls resource access based on auth

### Access Control

**Tool Access**:
- **User Permissions**: Controls who can access tools
- **Tool Restrictions**: Restricts certain tools
- **Time Limits**: Sets time-based access limits
- **Audit Logging**: Logs all tool access

## 🔧 Troubleshooting

### Common Issues

#### Tool Won't Start

**Symptoms**:
- Tool shows "Error" status
- Process starts but immediately stops
- No error message shown

**Solutions**:
1. **Check Dependencies**: Ensure all dependencies are running
2. **Check Script Path**: Verify script file exists and is executable
3. **Check Port**: Ensure port is not already in use
4. **Check Permissions**: Verify Python script has execution permissions

#### Port Conflicts

**Symptoms**:
- Tool starts but can't bind to port
- Multiple tools trying to use same port
- URL not accessible

**Solutions**:
1. **Check Port Usage**: Use `netstat -an | findstr :8080` to check port usage
2. **Change Port**: Modify preferred_ports in settings
3. **Kill Conflicting Process**: Kill process using the port
4. **Restart Tool**: Restart tool after port is free

#### GUI Not Responding

**Symptoms**:
- GUI freezes or becomes unresponsive
- Status updates stop
- Buttons don't work

**Solutions**:
1. **Check System Resources**: Monitor CPU and memory usage
2. **Restart Launcher**: Close and restart the launcher
3. **Check for Errors**: Look for error messages in status
4. **Reduce Concurrent Tools**: Reduce number of running tools

### Debug Mode

**Enable Debug Logging**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run launcher with debug output
python launcher_gui.py
```

**Check Tool Logs**:
```bash
# Check individual tool logs
type streamlined_homelab.log
type pc_auth.log
type integrated_homelab.log
```

**Database Inspection**:
```bash
# Check launcher database
sqlite3 unified_launcher.db ".tables"
sqlite3 unified_launcher.db "SELECT * FROM tools"
sqlite3 unified_launcher.db "SELECT * FROM launcher_events"
```

## 📚 Best Practices

### Tool Management

**Best Practices**:
- **Start Dependencies First**: Always start dependencies before main tools
- **Monitor Resource Usage**: Keep an eye on system resources
- **Stop Tools Gracefully**: Use the stop button instead of killing processes
- **Regular Status Checks**: Monitor tool status regularly

### Configuration Management

**Best Practices**:
- **Backup Settings**: Regularly backup launcher settings
- **Document Changes**: Document any custom configurations
- **Version Control**: Keep track of configuration changes
- **Test Changes**: Test configuration changes in safe environment

### Security Practices

**Best Practices**:
- **Regular Updates**: Keep tools and dependencies updated
- **Monitor Access**: Monitor tool access and usage
- **Secure Configuration**: Secure configuration files
- **Audit Logs**: Regularly review audit logs

## 🎯 Use Cases

### 1. Home Lab Management

**Scenario**: Managing a home lab with multiple PCs

**Configuration**:
- **Mode**: Integrated Mode
- **Tools**: All tools with authentication
- **Auto-Start**: Core system tools

**Benefits**:
- Complete homelab management
- Secure PC-to-PC communication
- Resource sharing across PCs
- Centralized monitoring

### 2. Development Environment

**Scenario**: Development workstation with multiple tools

**Configuration**:
- **Mode**: Solo Mode
- **Tools**: Development-specific tools
- **Auto-Start**: Development dependencies

**Benefits**:
- Lightweight operation
- Fast startup
- Minimal resource usage
- Focused toolset

### 3. Testing Environment

**Scenario**: Testing homelab configurations

**Configuration**:
- **Mode**: Dashboard Mode
- **Tools**: Testing and monitoring tools
- **Auto-Start**: None (manual control)

**Benefits**:
- Visual interface for testing
- Manual tool control
- Real-time monitoring
- Easy tool switching

### 4. Legacy Integration

**Scenario**: Using existing Homelab Tools

**Configuration**:
- **Mode**: Legacy Mode
- **Tools**: Original Homelab Tools
- **Auto-Start**: Legacy launcher

**Benefits**:
- Compatibility with existing tools
- Gradual migration path
- Side-by-side operation
- Legacy tool support

## 🎉 Conclusion

The Unified Homelab Launcher provides a comprehensive, easy-to-use interface for managing all your homelab tools and dashboards. With multiple operation modes, automatic dependency management, and real-time monitoring, it simplifies homelab management while providing powerful features for advanced users.

### Key Benefits

- **🚀 Easy to Use**: Intuitive GUI with one-click tool launching
- **🔄 Mode Switching**: Easy switching between different operation modes
- **📊 Real-time Monitoring**: Live status updates and health checks
- **🔧 Tool Management**: Comprehensive tool registry and management
- **🌐 Web Integration**: Automatic URL opening for web interfaces
- **⚙️ Configuration**: Centralized settings management
- **🛡️ Security**: Secure process management and access control

### Next Steps

1. **Launch the GUI**: Run `python launcher_gui.py`
2. **Choose Your Mode**: Select the operation mode that fits your needs
3. **Start Tools**: Use the launcher to start your homelab tools
4. **Monitor Status**: Keep an eye on tool status and system health
5. **Customize Settings**: Adjust configuration to match your preferences

Your homelab now has a **unified, easy-to-use launcher** that makes managing all your tools and dashboards simple and efficient! 🚀
