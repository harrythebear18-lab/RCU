# 🏗️ Core Services Architecture Guide

Complete documentation of the unified core services architecture implemented in Phase 1.

## 📋 Overview

The Homelab Core Services architecture provides a unified foundation for all homelab components, addressing the critical gaps identified in the system audit. This architecture eliminates system isolation, provides unified user experience, and enables enterprise-grade functionality.

## 🎯 Architecture Goals

### **Critical Gaps Addressed**
- ✅ **Central Event Bus** - Inter-service communication
- ✅ **Unified Configuration** - Centralized settings management
- ✅ **Authentication Service** - SSO with role-based access
- ✅ **Data Persistence** - Historical metrics storage
- ✅ **Unified Monitoring** - Intelligent alerting system

### **Benefits Achieved**
- 🔄 **Unified Data Flow** - Real-time data sharing between components
- 🔐 **Enterprise Security** - Centralized authentication and authorization
- 📊 **Historical Analysis** - Persistent data storage and trends
- 🚨 **Intelligent Alerting** - Threshold-based monitoring system
- ⚙️ **Configuration Management** - Centralized settings with validation
- 🎨 **Consistent UI** - Unified user experience across tools

## 🏛️ Core Services Components

### **1. Event Bus (`event_bus.py`)**
**Purpose**: Central communication hub for all system events

**Features**:
- 🔄 **Priority-based event processing** (LOW, MEDIUM, HIGH, CRITICAL)
- 📦 **Event categorization** (SYSTEM, MONITORING, NETWORK, SECURITY, etc.)
- 📊 **Event history tracking** with configurable retention
- ⚡ **Asynchronous processing** with performance monitoring
- 🛡️ **Error handling and recovery**

**Usage Example**:
```python
from Core Services.event_bus import get_event_bus, EventType

# Get event bus instance
bus = get_event_bus()

# Subscribe to events
def handle_monitoring_event(event):
    print(f"Monitoring event: {event.data}")

bus.subscribe(EventType.MONITORING, handle_monitoring_event)

# Publish events
await bus.publish(EventType.SYSTEM, "MyComponent", {"status": "running"})
```

### **2. Configuration Manager (`config_manager.py`)**
**Purpose**: Centralized configuration with validation and persistence

**Features**:
- ⚙️ **Hierarchical configuration** (system, user, secure)
- 🔒 **Secure credential storage** with encryption
- 🔄 **Hot-reload capability** for runtime updates
- ✅ **Configuration validation** with error reporting
- 💾 **Automatic backup and restore**

**Configuration Structure**:
```json
{
  "system": {
    "name": "Homelab System",
    "version": "1.0.0",
    "debug": false
  },
  "network": {
    "server_ip": "192.168.1.186",
    "client_ip": "192.168.1.132"
  },
  "ram_sharing": {
    "enabled": true,
    "ram_size_gb": 4,
    "auto_connect": true
  }
}
```

**Usage Example**:
```python
from Core Services.config_manager import get_config_manager

# Get configuration manager
config = get_config_manager()

# Get configuration value
ram_size = config.get('ram_sharing.ram_size_gb', 4)

# Set configuration value
config.set('ram_sharing.ram_size_gb', 8, 'storage', 'RAM disk size')

# Get secure configuration
api_key = config.get_secure('credentials.api_key')
```

### **3. Authentication Service (`auth_service.py`)**
**Purpose**: Centralized authentication with role-based access control

**Features**:
- 👤 **User management** with roles and permissions
- 🔐 **Session management** with automatic cleanup
- 🛡️ **Security auditing** and event logging
- 🔑 **Password hashing** with salt
- 📱 **Single Sign-On (SSO)** support

**Role-Based Access Control**:
- **admin**: Full system administrator access
- **operator**: System management and monitoring
- **viewer**: Read-only monitoring access
- **guest**: Limited guest access

**Usage Example**:
```python
from Core Services.auth_service import get_auth_service

# Get authentication service
auth = get_auth_service()

# Authenticate user
session_id = auth.authenticate('admin', 'password123', '192.168.1.100', 'MyApp')

# Validate session
user = auth.validate_session(session_id)

# Check permissions
if auth.has_permission(user, 'system.admin'):
    # Perform admin action
    pass
```

### **4. Data Persistence (`data_persistence.py`)**
**Purpose**: Unified data storage for metrics, events, and system state

**Features**:
- 💾 **SQLite database** with automatic schema management
- 📊 **Metrics storage** with tagging and metadata
- 📋 **Event logging** with priority and categorization
- 🧹 **Automatic cleanup** based on retention policies
- 📈 **Data aggregation** and historical analysis

**Database Schema**:
```sql
-- Metrics table
CREATE TABLE metrics (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME,
    source TEXT,
    metric_type TEXT,
    value REAL,
    unit TEXT,
    tags TEXT,
    metadata TEXT
);

-- Events table
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    event_id TEXT UNIQUE,
    event_type TEXT,
    source TEXT,
    timestamp DATETIME,
    data TEXT,
    priority INTEGER
);
```

**Usage Example**:
```python
from Core Services.data_persistence import get_data_persistence

# Get data persistence
dp = get_data_persistence()

# Store metrics
dp.store_metric('cpu_monitor', 'cpu_usage', 75.5, 'percent', 
                tags={'core': '0'}, metadata={'process_count': 42})

# Store events
dp.store_event('cpu_alert_001', 'performance', 'cpu_monitor', 
               {'cpu_usage': 95.2, 'alert': 'high'})

# Retrieve metrics
metrics = dp.get_metrics(source='cpu_monitor', metric_type='cpu_usage')
```

### **5. Unified Monitoring (`unified_monitoring.py`)**
**Purpose**: Intelligent monitoring with threshold-based alerting

**Features**:
- 📊 **Real-time metrics collection** from all sources
- 🚨 **Intelligent alerting** with threshold rules
- 📈 **Performance analytics** and trend analysis
- 🔔 **Multi-severity alerts** (INFO, WARNING, ERROR, CRITICAL)
- 📱 **Alert acknowledgment** and resolution tracking

**Default Threshold Rules**:
```python
# CPU thresholds
ThresholdRule("cpu_usage", ">", 80.0, AlertSeverity.WARNING, "High CPU usage")
ThresholdRule("cpu_usage", ">", 95.0, AlertSeverity.ERROR, "Critical CPU usage")

# Memory thresholds
ThresholdRule("memory_usage", ">", 85.0, AlertSeverity.WARNING, "High memory usage")
ThresholdRule("memory_usage", ">", 95.0, AlertSeverity.ERROR, "Critical memory usage")
```

**Usage Example**:
```python
from Core Services.unified_monitoring import get_unified_monitoring, AlertSeverity

# Get monitoring service
monitoring = get_unified_monitoring()

# Create custom alert
alert_id = monitoring.create_alert(
    "Custom Alert", 
    "This is a custom alert", 
    AlertSeverity.INFO, 
    "my_component"
)

# Get active alerts
alerts = monitoring.get_active_alerts(AlertSeverity.WARNING)
```

## 🎨 Unified Dashboard (`unified_dashboard.py`)

**Purpose**: Modern GUI interface integrating all core services

**Features**:
- 🔐 **Secure login** with session management
- 📊 **Real-time dashboard** with auto-refresh
- 🚨 **Alert management** with acknowledgment and resolution
- ⚙️ **Configuration management** interface
- 👥 **User management** and session monitoring
- 📈 **Metrics visualization** and historical data

**Dashboard Sections**:
1. **📊 Overview** - System status and key metrics
2. **⚡ System Status** - Core services health
3. **🚨 Alerts** - Active alert management
4. **⚙️ Configuration** - Settings management
5. **📈 Metrics** - Historical data viewer
6. **👥 Users** - User and session management
7. **🔐 Security** - Security event monitoring
8. **📋 Events** - System event log

## 🚀 Getting Started

### **Quick Start**
```batch
# Launch unified system
Launch_Unified_System.bat

# Option 1: Launch dashboard (recommended)
# Option 2: Start core services only
# Option 3: Test services integration
# Option 4: System status check
```

### **Python Integration**
```python
# Import core services
from Core Services import initialize_core_services

# Initialize all services
services = initialize_core_services()

# Access individual services
event_bus = services['event_bus']
config = services['config_manager']
auth = services['auth_service']
data = services['data_persistence']
monitoring = services['unified_monitoring']
```

### **Configuration**
```python
# Set configuration
config.set('my_component.setting', 'value', 'category', 'description')

# Get configuration
value = config.get('my_component.setting', 'default_value')

# Validate configuration
validation = config.validate_config()
```

## 🔧 Integration with Existing Tools

### **Step 1: Import Core Services**
```python
# Add to your existing tool
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from Core Services.event_bus import get_event_bus, EventType
from Core Services.config_manager import get_config_manager
from Core Services.data_persistence import get_data_persistence
```

### **Step 2: Publish Events**
```python
# Get services
event_bus = get_event_bus()
data_persistence = get_data_persistence()

# Publish monitoring events
event_bus.publish_sync(
    EventType.MONITORING,
    'MyTool',
    {
        'metric_type': 'cpu_usage',
        'value': 75.5,
        'unit': 'percent'
    }
)

# Store metrics
data_persistence.store_metric('MyTool', 'cpu_usage', 75.5, 'percent')
```

### **Step 3: Use Configuration**
```python
# Get configuration manager
config = get_config_manager()

# Use unified configuration
update_interval = config.get('monitoring.update_interval_seconds', 5)
ram_size = config.get('ram_sharing.ram_size_gb', 4)
```

### **Step 4: Add Authentication (Optional)**
```python
# Add authentication to your tool
from Core Services.auth_service import get_auth_service

auth = get_auth_service()
session_id = auth.authenticate(username, password, ip_address, user_agent)

if session_id:
    user = auth.validate_session(session_id)
    if auth.has_permission(user, 'system.monitor'):
        # Tool functionality
        pass
```

## 📊 Performance Considerations

### **Event Bus Performance**
- **Async Processing**: Events processed asynchronously to avoid blocking
- **Priority Queues**: Critical events processed first
- **Batch Processing**: Events batched for efficiency
- **Memory Management**: Automatic cleanup of old events

### **Database Performance**
- **Indexes**: Optimized indexes for common queries
- **Connection Pooling**: Efficient database connections
- **Automatic Cleanup**: Old data automatically removed
- **Aggregation**: Pre-computed aggregations for fast queries

### **Memory Usage**
- **Lazy Loading**: Services loaded on first use
- **Resource Cleanup**: Automatic cleanup of expired sessions
- **Efficient Data Structures**: Optimized for low memory usage

## 🔒 Security Considerations

### **Authentication Security**
- **Password Hashing**: Salted SHA-256 hashing
- **Session Management**: Automatic session expiration
- **Failed Login Protection**: Account lockout after failed attempts
- **Security Auditing**: All security events logged

### **Data Security**
- **Secure Configuration**: Sensitive data encrypted
- **Access Control**: Role-based permissions
- **Audit Logging**: All configuration changes logged
- **Input Validation**: All inputs validated and sanitized

## 🛠️ Troubleshooting

### **Common Issues**

**Service Not Starting**:
```python
# Check service availability
from Core Services import initialize_core_services
services = initialize_core_services()
print(services.keys())
```

**Events Not Processing**:
```python
# Check event bus statistics
bus = get_event_bus()
stats = bus.get_statistics()
print(f"Events processed: {stats['total_events']}")
```

**Configuration Not Loading**:
```python
# Validate configuration
config = get_config_manager()
validation = config.validate_config()
print(f"Config valid: {validation['valid']}")
if validation['issues']:
    print("Issues:", validation['issues'])
```

**Database Issues**:
```python
# Check database stats
dp = get_data_persistence()
stats = dp.get_database_stats()
print(f"Database size: {stats['database_size_mb']}MB")
print(f"Metrics count: {stats['metrics_count']}")
```

## 📈 Future Enhancements

### **Phase 2 Planning**
- 🌐 **REST API Layer** - Programmatic access to all services
- 📱 **Mobile Interface** - Responsive web interface
- 🤖 **Automation Framework** - Workflow automation engine
- 📊 **Advanced Analytics** - ML-based insights and predictions

### **Phase 3 Planning**
- ☁️ **Cloud Integration** - Hybrid cloud capabilities
- 🔗 **Service Mesh** - Advanced inter-service communication
- 🧪 **Testing Framework** - Comprehensive testing suite
- 📚 **Documentation Portal** - Interactive documentation

## 🎯 Success Metrics

### **Phase 1 Achievements**
- ✅ **5 Core Services** implemented and integrated
- ✅ **100% Critical Gaps** from audit addressed
- ✅ **Unified Dashboard** with full functionality
- ✅ **Enterprise Security** with role-based access
- ✅ **Historical Data Storage** with automatic cleanup
- ✅ **Real-time Monitoring** with intelligent alerting

### **Performance Targets**
- 🚀 **Event Processing**: < 10ms average processing time
- 💾 **Database Queries**: < 100ms average response time
- 🔐 **Authentication**: < 50ms login time
- 📊 **Dashboard Load**: < 2 seconds initial load

---

**Phase 1 Complete**: The homelab system now has a solid, enterprise-grade foundation that addresses all critical architectural gaps and provides a unified platform for future development.
