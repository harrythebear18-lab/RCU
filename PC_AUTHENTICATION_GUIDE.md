# 🔐 PC-to-PC Authentication System Guide

## 📋 Overview

The PC-to-PC Authentication System provides secure, same-subnet authentication and resource sharing between homelab PCs. It enables trusted communication and controlled resource allocation within your local network.

## 🎯 System Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                PC AUTHENTICATION SYSTEM                         │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │  Peer Discovery  │  │  Authentication  │  │  Resource Access │   │
│  │                 │  │                 │  │                 │   │
│  │ • Subnet Scan   │  │ • Session Tokens │  │ • Access Control │   │
│  │ • Peer Detection │  │ • Trust Mgmt     │  │ • Resource Limits│   │
│  │ • Auto Discovery │  │ • Handshake      │  │ • Allocation Auth│   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
│                                │                                 │
│                                ▼                                 │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                INTEGRATION LAYER                           │   │
│  │                                                             │   │
│  │ • Homelab Integration      • Resource Sharing Bridge        │   │
│  │ • Peer Resource Controls    • Authentication Hooks         │   │
│  │ • Access Level Management   • Security Policies             │   │
│  │ • Monitoring & Auditing     • Event Logging                 │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                │                                 │
│                                ▼                                 │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                MANAGEMENT INTERFACE                         │   │
│  │                                                             │   │
│  │ • Peer Management GUI      • Trust/Block Controls          │   │
│  │ • Resource Access Settings  • Authentication Events          │   │
│  │ • System Status Dashboard   • Security Monitoring           │   │
│  │ • Configuration Management  • Export/Import Functions        │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

**System Requirements:**
- **OS**: Windows 10/11 (all PCs in the homelab)
- **Network**: Same subnet connectivity (e.g., 192.168.1.0/24)
- **Python**: 3.8+ with required packages
- **Permissions**: Administrator privileges for network discovery

### Installation

1. **Install Dependencies**
   ```bash
   cd "C:\Users\htsou\Desktop\Ram clean up"
   pip install psutil requests tkinter sqlite3
   ```

2. **Start Authentication System**
   ```bash
   # Start PC discovery and authentication
   python pc_auth_system.py
   ```

3. **Start Management GUI**
   ```bash
   # Open peer management interface
   python pc_auth_gui.py
   ```

4. **Start Integrated System**
   ```bash
   # Start full homelab with authentication
   python integrated_homelab_with_auth.py
   ```

## 🔧 Authentication System

### Peer Discovery

**Automatic Discovery:**
- **Subnet Scanning**: Automatically scans the configured subnet for active hosts
- **Ping Detection**: Uses ICMP ping to identify reachable systems
- **Peer Identification**: Attempts to identify homelab peers on discovered hosts
- **Continuous Monitoring**: Re-scans at configurable intervals

**Manual Discovery:**
- **IP Range**: Specify custom IP ranges for discovery
- **Direct Connection**: Connect to known peers by IP address
- **Import/Export**: Share peer configurations between systems

### Authentication Protocol

**Handshake Process:**
1. **Discovery**: Peer discovers other peers on the subnet
2. **Identification**: Peers exchange system information and fingerprints
3. **Authentication**: Secure handshake with session tokens
4. **Trust Establishment**: Optional trust relationship setup
5. **Resource Access**: Controlled resource sharing based on trust level

**Security Features:**
- **Fingerprint Verification**: Unique system fingerprint for peer identification
- **Session Tokens**: Time-limited session tokens for authenticated access
- **Trust Management**: Trusted peer list with automatic expiration
- **Block List**: Blocked peers with no access to resources

### Peer Roles

| Role | Description | Capabilities | Typical Use |
|------|-------------|--------------|-------------|
| **Server** | Resource provider | Full resource sharing, authentication authority | Primary homelab server |
| **Client** | Resource consumer | Request resources, limited sharing | Workstation, laptop |
| **Peer** | Equal participant | Bidirectional sharing, peer authentication | Equal homelab systems |

## 📊 Peer Management

### Peer Information

**Peer Data:**
- **System Information**: Hostname, OS version, hardware specs
- **Network Information**: IP address, MAC address, subnet
- **Authentication Status**: Authentication state, session tokens
- **Trust Level**: Trusted, blocked, or unknown status
- **Resource Access**: Authorized resources and allocation limits

**Peer Fingerprint:**
```
Format: hostname|ip_address|mac_address|platform_info
Hash: SHA-256 (first 16 characters)
Purpose: Unique peer identification and verification
```

### Trust Management

**Trust Levels:**
- **Unknown**: Newly discovered peer, no trust established
- **Authenticated**: Peer has valid session token, limited access
- **Trusted**: Fully trusted peer, automatic resource access
- **Blocked**: Blocked peer, no access to any resources

**Trust Actions:**
- **Manual Trust**: Manually mark peer as trusted
- **Auto Trust**: Automatically trust peers in same subnet (configurable)
- **Block Peer**: Block peer from all access
- **Revoke Trust**: Remove trusted status

### Session Management

**Session Tokens:**
- **Generation**: Cryptographically secure session tokens
- **Expiration**: Time-limited tokens (configurable timeout)
- **Validation**: Real-time token validation
- **Refresh**: Token refresh for extended sessions

**Session Properties:**
```python
{
    'peer_id': 'unique_peer_identifier',
    'session_token': 'secure_token_hash',
    'created_at': '2024-01-01T12:00:00',
    'expires_at': '2024-01-01T13:00:00',
    'last_activity': '2024-01-01T12:30:00',
    'access_level': 'authenticated'
}
```

## 🔌 Resource Integration

### Resource Access Control

**Access Levels:**
- **No Access**: Peer cannot access any resources
- **Read**: Peer can view resource status and metrics
- **Read Write**: Peer can allocate and release resources
- **Full**: Peer has full control over resources

**Resource Limits:**
```json
{
  "peer_resource_limits": {
    "max_ram_gb": 4.0,
    "max_cpu_cores": 2,
    "max_gpu_gb": 2.0,
    "max_network_gbps": 1.0
  }
}
```

### Authentication Flow

**Resource Allocation with Authentication:**
1. **Peer Request**: Authenticated peer requests resource allocation
2. **Token Validation**: System validates session token
3. **Access Check**: System checks peer's resource access rights
4. **Limit Check**: System verifies allocation within limits
5. **Allocation**: Resource allocated if all checks pass
6. **Logging**: All actions logged for audit trail

**API Example:**
```python
# Authenticate peer for resource access
success = integrated_homelab.authenticate_peer_for_resources(
    peer_id='peer_12345',
    session_token='session_token_hash'
)

# Allocate resource to authenticated peer
allocation_id = integrated_homelab.allocate_resource_to_peer(
    peer_id='peer_12345',
    resource_id='ram_low_latency',
    amount=2.0,
    session_token='session_token_hash',
    properties={'purpose': 'gaming'}
)
```

## 🖥️ Management Interface

### GUI Features

**System Overview:**
- **Peer Count**: Total, trusted, blocked peers
- **Session Status**: Active authentication sessions
- **Resource Access**: Peer resource access statistics
- **Discovery Status**: Network discovery state

**Peer Management:**
- **Peer List**: Discovered peers with status indicators
- **Peer Details**: Detailed peer information and properties
- **Trust Controls**: Trust/block peer actions
- **Authentication**: Manual authentication with peers

**Resource Management:**
- **Access Control**: Configure peer resource access
- **Allocation Limits**: Set per-peer resource limits
- **Usage Monitoring**: Track peer resource usage
- **Access History**: View peer access history

**Event Monitoring:**
- **Authentication Events**: Login, logout, trust changes
- **Resource Events**: Allocation, release, access attempts
- **Security Events**: Blocked attempts, suspicious activity
- **System Events**: Discovery, configuration changes

### GUI Controls

**Main Controls:**
- **🔍 Discover**: Start/stop network discovery
- **🔄 Refresh**: Update peer list and status
- **⚙️ Settings**: Configure authentication settings
- **📊 Status**: View system status and statistics

**Peer Actions:**
- **✅ Trust**: Mark peer as trusted
- **🚫 Block**: Block peer from all access
- **🔐 Authenticate**: Authenticate with peer
- **🔗 Connect**: Establish connection to peer

## 🛡️ Security Features

### Authentication Security

**Cryptographic Security:**
- **SHA-256 Hashing**: For fingerprints and token generation
- **HMAC Verification**: For message integrity
- **Secure Random**: Cryptographically secure random number generation
- **Token Expiration**: Time-limited session tokens

**Network Security:**
- **Subnet Restriction**: Only works within configured subnet
- **IP Validation**: Validates peer IP addresses
- **Fingerprint Verification**: Unique system identification
- **Session Isolation**: Isolated sessions per peer

### Access Control

**Resource Protection:**
- **Authentication Required**: All resource access requires authentication
- **Access Levels**: Granular access control per resource type
- **Allocation Limits**: Per-peer resource allocation limits
- **Audit Logging**: Complete audit trail of all actions

**Peer Isolation:**
- **Sandboxing**: Peers isolated from each other's resources
- **Resource Quotas**: Individual resource quotas per peer
- **Time Limits**: Time-limited access and allocations
- **Revocation**: Immediate revocation of access rights

## 📈 Monitoring and Auditing

### Event Logging

**Authentication Events:**
- Peer discovery and registration
- Authentication attempts and results
- Trust relationship changes
- Session creation and expiration

**Resource Events:**
- Resource allocation and release
- Access attempts and denials
- Limit violations and warnings
- Resource usage statistics

**Security Events:**
- Blocked access attempts
- Suspicious activity detection
- Configuration changes
- System errors and warnings

### Monitoring Dashboard

**Real-time Metrics:**
- Active authentication sessions
- Peer discovery status
- Resource utilization by peer
- Network activity levels

**Historical Data:**
- Authentication success/failure rates
- Resource allocation trends
- Peer activity patterns
- Security incident history

## 🔧 Configuration

### System Settings

**Authentication Settings:**
```json
{
  "auth_enabled": true,
  "resource_sharing_enabled": true,
  "auto_trust_peers": false,
  "require_auth_for_resources": true,
  "auth_timeout": 3600,
  "session_timeout": 1800
}
```

**Network Settings:**
```json
{
  "subnet": "192.168.1.0/24",
  "discovery_enabled": true,
  "discovery_interval": 30,
  "max_peers": 20
}
```

**Resource Settings:**
```json
{
  "peer_resource_limits": {
    "max_ram_gb": 4.0,
    "max_cpu_cores": 2,
    "max_gpu_gb": 2.0,
    "max_network_gbps": 1.0
  }
}
```

### Advanced Configuration

**Custom Trust Policies:**
- Automatic trust based on MAC address
- Trust based on hostname patterns
- Time-based trust expiration
- Conditional trust rules

**Resource Allocation Policies:**
- Priority-based allocation
- Fair sharing algorithms
- Dynamic limit adjustment
- Resource reservation rules

## 🚀 Use Cases

### 1. Home Gaming Network

**Scenario**: Multiple gaming PCs sharing resources
- **Server**: High-end gaming PC (Server role)
- **Clients**: Laptops and secondary PCs (Client role)
- **Resources**: GPU RAM, CPU cores, network bandwidth
- **Trust**: Automatic trust for same subnet

### 2. Development Environment

**Scenario**: Development workstation sharing with test machines
- **Server**: Development workstation (Server role)
- **Clients**: Test and build machines (Client role)
- **Resources**: CPU cores, RAM, storage
- **Trust**: Manual trust for development team

### 3. Media Production

**Scenario**: Video editing workstation with render farm
- **Server**: Primary editing workstation (Server role)
- **Clients**: Render nodes (Peer role)
- **Resources**: GPU compute, storage, network
- **Trust**: Trusted peers with full access

### 4. Scientific Computing

**Scenario**: Research lab with computational resources
- **Server**: Main research workstation (Server role)
- **Clients**: Analysis workstations (Client role)
- **Resources**: CPU cores, RAM, RDMA networking
- **Trust**: Role-based access control

## 🔧 Troubleshooting

### Common Issues

**Discovery Not Working:**
```bash
# Check network connectivity
ping 192.168.1.1

# Check subnet configuration
python -c "import ipaddress; print(ipaddress.IPv4Network('192.168.1.0/24'))"

# Check firewall settings
# Windows Defender Firewall -> Advanced Settings -> Inbound Rules
# Allow "File and Printer Sharing (Echo Request - ICMPv4-In)"
```

**Authentication Failing:**
```bash
# Check peer status
python -c "from pc_auth_system import pc_auth_system; print(pc_auth_system.get_system_status())"

# Check session tokens
python -c "from pc_auth_system import pc_auth_system; print(list(pc_auth_system.session_tokens.keys()))"

# Check trusted peers
python -c "from pc_auth_system import pc_auth_system; print(pc_auth_system.trusted_peers)"
```

**Resource Access Denied:**
```bash
# Check peer resource access
python -c "from integrated_homelab_with_auth import integrated_homelab; print(integrated_homelab.peer_resource_access)"

# Check authentication status
python -c "from integrated_homelab_with_auth import integrated_homelab; print(integrated_homelab.authenticated_peers)"

# Check resource limits
python -c "from integrated_homelab_with_auth import integrated_homelab; print(integrated_homelab.settings['peer_resource_limits'])"
```

### Debug Mode

**Enable Debug Logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with debug output
python pc_auth_system.py
python integrated_homelab_with_auth.py
```

**Database Inspection:**
```bash
# View authentication database
sqlite3 pc_auth.db ".tables"
sqlite3 pc_auth.db "SELECT * FROM peers"

# View integrated database
sqlite3 integrated_homelab.db ".tables"
sqlite3 integrated_homelab.db "SELECT * FROM peer_resource_access"
```

## 📚 Best Practices

### Security Best Practices

**Network Security:**
- Configure firewall to allow homelab subnet only
- Use strong passwords for system accounts
- Regularly update system and security patches
- Monitor authentication logs for suspicious activity

**Authentication Security:**
- Enable session timeout for inactive peers
- Regularly review trusted peer list
- Use manual trust for unknown peers
- Block suspicious or unused peers

**Resource Security:**
- Set conservative resource limits for new peers
- Monitor resource usage patterns
- Regularly audit resource allocations
- Implement resource quotas per peer

### Performance Best Practices

**Network Optimization:**
- Use wired Ethernet for best performance
- Configure network for low latency
- Optimize subnet size for discovery
- Monitor network bandwidth usage

**Resource Optimization:**
- Balance resource allocation across peers
- Monitor resource utilization
- Implement fair sharing policies
- Optimize allocation algorithms

### Maintenance Best Practices

**Regular Tasks:**
- Daily: Check authentication logs and events
- Weekly: Review trusted peer list and resource usage
- Monthly: Update system configurations and backup data
- Quarterly: Review security policies and access controls

**Backup Procedures:**
- Backup authentication database regularly
- Export peer configurations
- Save system settings and configurations
- Document custom trust policies

## 🎉 Conclusion

The PC-to-PC Authentication System provides secure, same-subnet authentication and resource sharing for your homelab environment. With automatic discovery, secure authentication, and integrated resource management, it creates a trusted network of homelab systems.

### Key Benefits

- **🔐 Secure Authentication**: Cryptographically secure peer authentication
- **🔍 Automatic Discovery**: Automatic peer discovery within your subnet
- **🛡️ Access Control**: Granular resource access control and limits
- **📊 Monitoring**: Comprehensive monitoring and event logging
- **🔧 Integration**: Seamless integration with streamlined homelab system
- **🖥️ Management**: Easy-to-use GUI for peer and resource management

### Next Steps

1. **Deploy the authentication system** on all homelab PCs
2. **Configure network settings** for your subnet
3. **Set up trust relationships** between trusted peers
4. **Configure resource access** based on your needs
5. **Monitor system activity** and adjust settings as needed

Your homelab now has secure, authenticated PC-to-PC communication and resource sharing! 🚀
