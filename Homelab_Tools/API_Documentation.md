# Homelab Portal REST API Documentation

## **Overview**

The Homelab Portal REST API provides comprehensive programmatic access to all portal functionality, including screen sharing, GPU sharing, RAM sharing, file transfer, and hardware optimization for Intel+NVIDIA+DDR4 systems.

**Base URL:** `http://localhost:8080`  
**API Version:** `1.0.0`  
**Authentication:** API Key required for protected endpoints  

---

## **🔧 Core Services Endpoints**

### **Health Check**
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-05-13T20:00:00.000Z",
  "version": "1.0.0",
  "services": {
    "event_bus": "running",
    "config_manager": "running",
    "auth_service": "running",
    "data_persistence": "running",
    "unified_monitoring": "running",
    "resource_sharing": "running",
    "portal": "running",
    "gpu_sharing": "running",
    "ram_sharing": "running",
    "screen_sharing": "running",
    "hardware_optimizer": "running"
  }
}
```

---

## **🌐 Portal Management Endpoints**

### **Get Portal Status**
```http
GET /api/portal/status
```

**Response:**
```json
{
  "status": "active",
  "node_id": "abc123def456",
  "hostname": "Homelab-PC",
  "ip_address": "192.168.1.100",
  "port": 30000,
  "hardware_info": {
    "cpu": {
      "name": "Intel(R) Core(TM) i7-10700K",
      "is_intel": true
    },
    "gpu": {
      "name": "NVIDIA GeForce RTX 3080",
      "is_nvidia": true
    },
    "windows_version": "Windows 11",
    "memory_info": {
      "total_gb": 32.0,
      "available_gb": 24.5
    },
    "ram_modules": [
      {
        "capacity_gb": 16,
        "speed_mhz": 3200,
        "is_ddr4": true
      }
    ]
  },
  "active_nodes_count": 1,
  "active_sessions_count": 0,
  "capabilities": ["screen", "sound", "file", "resource", "clipboard"],
  "timestamp": "2026-05-13T20:00:00.000Z"
}
```

### **Get Active Nodes**
```http
GET /api/portal/nodes
```

**Response:**
```json
{
  "nodes": [
    {
      "node_id": "abc123def456",
      "hostname": "Homelab-PC",
      "ip_address": "192.168.1.100",
      "port": 30000,
      "capabilities": ["screen", "sound", "file", "resource"],
      "status": "active",
      "last_seen": "2026-05-13T20:00:00.000Z",
      "metadata": {}
    }
  ],
  "count": 1,
  "timestamp": "2026-05-13T20:00:00.000Z"
}
```

### **Get Active Sessions**
```http
GET /api/portal/sessions
```

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "sess123abc456",
      "source_node": "abc123def456",
      "target_node": "def456abc123",
      "share_type": "screen",
      "status": "active",
      "created_at": "2026-05-13T20:00:00.000Z",
      "metadata": {}
    }
  ],
  "count": 1,
  "timestamp": "2026-05-13T20:00:00.000Z"
}
```

### **Connect to Node**
```http
POST /api/portal/connect
```

**Request Body:**
```json
{
  "target_ip": "192.168.1.101",
  "target_port": 30000
}
```

**Response:**
```json
{
  "success": true,
  "message": "Connected to 192.168.1.101:30000",
  "timestamp": "2026-05-13T20:00:00.000Z"
}
```

### **Share File**
```http
POST /api/portal/share/file
```

**Request Body:**
```json
{
  "file_path": "C:\\Users\\User\\Documents\\test.txt",
  "target_node": "def456abc123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "File shared with def456abc123",
  "file_path": "C:\\Users\\User\\Documents\\test.txt",
  "timestamp": "2026-05-13T20:00:00.000Z"
}
```

### **Start Screen Share**
```http
POST /api/portal/share/screen
```

**Request Body:**
```json
{
  "target_node": "def456abc123"
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "screen123abc456",
  "message": "Screen sharing started with def456abc123",
  "timestamp": "2026-05-13T20:00:00.000Z"
}
```

### **Start Sound Share**
```http
POST /api/portal/share/sound
```

**Request Body:**
```json
{
  "target_node": "def456abc123"
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "sound123abc456",
  "message": "Sound sharing started with def456abc123",
  "timestamp": "2026-05-13T20:00:00.000Z"
}
```

---

## **🎮 GPU Sharing Endpoints**

### **Get GPU Status**
```http
GET /api/gpu/status
```

**Response:**
```json
{
  "gpu_status": {
    "gpu_info": {
      "available": true,
      "name": "NVIDIA GeForce RTX 3080",
      "memory_total": 10240,
      "memory_used": 2048,
      "memory_free": 8192,
      "utilization": 25,
      "temperature": 65,
      "power_usage": 220.5,
      "driver_version": "511.23",
      "cuda_version": "11.6"
    },
    "is_nvidia_available": true,
    "active_sessions": 0,
    "shared_processes": 0,
    "total_memory_allocated": 0
  },
  "timestamp": "2026-05-13T20:00:00.000Z"
}
```

### **Share GPU Compute**
```http
POST /api/gpu/share
```

**Request Body:**
```json
{
  "target_node": "def456abc123",
  "compute_task": {
    "type": "matrix_multiply",
    "requirements": {
      "memory_mb": 512,
      "compute_units": 1000
    },
    "priority": "normal",
    "timeout": 300
  }
}
```

**Available Task Types:**
- `matrix_multiply` - Matrix multiplication operations
- `image_processing` - Image processing and filtering
- `neural_network` - Neural network inference
- `video_encoding` - Video encoding/decoding
- `general` - General GPU compute tasks

**Response:**
```json
{
  "success": true,
  "session_id": "gpu123abc456",
  "message": "GPU compute shared with def456abc123",
  "timestamp": "2026-05-13T20:00:00.000Z"
}
```

### **Monitor GPU Performance**
```http
GET /api/gpu/monitor
```

**Response:**
```json
{
  "gpu_performance": {
    "name": "NVIDIA GeForce RTX 3080",
    "memory_total": 10240,
    "memory_used": 2048,
    "memory_free": 8192,
    "gpu_utilization": 25,
    "memory_utilization": 20,
    "temperature": 65,
    "power_usage": 220.5,
    "graphics_clock": 1665,
    "sm_clock": 1665,
    "memory_clock": 9501,
    "timestamp": 1652472000.0
  },
  "timestamp": "2026-05-13T20:00:00.000Z"
}
```

---

## **💾 RAM Sharing Endpoints**

### **Get RAM Status**
```http
GET /api/ram/status
```

**Response:**
```json
{
  "ram_status": {
    "ram_info": {
      "total_gb": 32.0,
      "available_gb": 24.5,
      "used_gb": 7.5,
      "speed_mhz": 3200,
      "memory_type": "DDR4",
      "modules": [
        {
          "capacity_gb": 16,
          "speed_mhz": 3200,
          "is_ddr4": true
        }
      ]
    },
    "is_ddr4": true,
    "shared_regions": 0,
    "remote_sessions": 0,
    "total_shared_mb": 0,
    "total_shared_gb": 0.0
  },
  "timestamp": "2026-05-13T20:00:00.000Z"
}
```

### **Share RAM Region**
```http
POST /api/ram/share
```

**Request Body:**
```json
{
  "target_node": "def456abc123",
  "size_mb": 1024,
  "region_name": "shared_buffer"
}
```

**Response:**
```json
{
  "success": true,
  "region_id": "ram123abc456",
  "message": "RAM region shared with def456abc123",
  "size_mb": 1024,
  "timestamp": "2026-05-13T20:00:00.000Z"
}
```

### **Access Shared RAM**
```http
POST /api/ram/access
```

**Request Body:**
```json
{
  "source_node": "def456abc123",
  "region_id": "ram123abc456",
  "operation": "read",
  "data": {
    "offset": 0,
    "size": 1024
  }
}
```

**Available Operations:**
- `read` - Read data from shared RAM
- `write` - Write data to shared RAM
- `benchmark` - Benchmark RAM access performance

**Response:**
```json
{
  "success": true,
  "result": {
    "data": "base64_encoded_data",
    "read_time": 0.001,
    "ddr4_optimized": true,
    "burst_transfer": true
  },
  "timestamp": "2026-05-13T20:00:00.000Z"
}
```

---

## **🖥️ Screen Sharing Endpoints**

### **Get Screen Status**
```http
GET /api/screen/status
```

**Response:**
```json
{
  "screen_status": {
    "screen_info": {
      "resolution": "1920x1080",
      "width": 1920,
      "height": 1080,
      "color_depth": 32,
      "refresh_rate": 60,
      "gpu_accelerated": true
    },
    "is_nvidia_available": true,
    "is_ddr4": true,
    "active_shares": 0,
    "remote_shares": 0,
    "total_frames_sent": 0,
    "total_frames_received": 0
  },
  "timestamp": "2026-05-13T20:00:00.000Z"
}
```

### **Benchmark Screen Capture**
```http
GET /api/screen/benchmark
```

**Response:**
```json
{
  "screen_benchmarks": {
    "powershell_capture": {
      "avg_time_seconds": 0.050,
      "fps": 20.0,
      "iterations": 10
    },
    "nvidia_capture": {
      "avg_time_seconds": 0.025,
      "fps": 40.0,
      "iterations": 10,
      "gpu_accelerated": true
    },
    "ddr4_memory": {
      "avg_time_seconds": 0.010,
      "operations_per_second": 100000,
      "frame_size_bytes": 6220800,
      "ddr4_optimized": true
    }
  },
  "timestamp": "2026-05-13T20:00:00.000Z"
}
```

---

## **⚙️ Hardware Optimization Endpoints**

### **Get Hardware Info**
```http
GET /api/hardware/info
```

**Response:**
```json
{
  "hardware_info": {
    "cpu": {
      "name": "Intel(R) Core(TM) i7-10700K",
      "max_clock_speed": 4800,
      "cores": 8,
      "logical_processors": 16,
      "is_intel": true
    },
    "gpu": {
      "name": "NVIDIA GeForce RTX 3080",
      "memory": 10240,
      "is_nvidia": true
    },
    "windows_version": "Windows 11",
    "memory_info": {
      "total_gb": 32.0,
      "available_gb": 24.5,
      "used_gb": 7.5
    },
    "ram_modules": [
      {
        "capacity_gb": 16,
        "speed_mhz": 3200,
        "is_ddr4": true
      }
    ]
  },
  "timestamp": "2026-05-13T20:00:00.000Z"
}
```

### **Get Hardware Benchmarks**
```http
GET /api/hardware/benchmarks
```

**Response:**
```json
{
  "hardware_benchmarks": {
    "cpu_benchmark": {
      "score": 78498,
      "time_seconds": 2.5,
      "primes_per_second": 31399
    },
    "gpu_benchmark": {
      "gpu_utilization": 25,
      "memory_used_mb": 2048,
      "memory_total_mb": 10240,
      "memory_utilization": 20
    },
    "network_benchmark": {
      "latency_ms": 15.5,
      "status": "connected"
    },
    "memory_benchmark": {
      "time_seconds": 0.8,
      "operations_per_second": 125000,
      "total": 100000000
    }
  },
  "timestamp": "2026-05-13T20:00:00.000Z"
}
```

### **Optimize Hardware**
```http
POST /api/hardware/optimize
```

**Response:**
```json
{
  "success": true,
  "message": "Hardware optimization completed",
  "timestamp": "2026-05-13T20:00:00.000Z"
}
```

### **Check Hardware Compatibility**
```http
POST /api/hardware/compatibility
```

**Request Body:**
```json
{
  "remote_system_info": {
    "cpu": {
      "name": "Intel(R) Core(TM) i7-10700K",
      "is_intel": true
    },
    "gpu": {
      "name": "NVIDIA GeForce RTX 3080",
      "is_nvidia": true
    },
    "windows_version": "Windows 10",
    "ram_modules": [
      {
        "is_ddr4": true
      }
    ]
  }
}
```

**Response:**
```json
{
  "compatibility": {
    "cpu_compatible": true,
    "gpu_compatible": true,
    "windows_compatible": true,
    "network_compatible": true,
    "ram_compatible": true,
    "overall_compatible": true,
    "differences": []
  },
  "timestamp": "2026-05-13T20:00:00.000Z"
}
```

---

## **🔐 Authentication Endpoints**

### **Login**
```http
POST /api/auth/login
```

**Request Body:**
```json
{
  "username": "admin",
  "password": "password"
}
```

**Response:**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": "admin",
  "expires_at": "2026-05-13T21:00:00.000Z"
}
```

### **Generate API Key**
```http
POST /api/auth/generate-key
```

**Request Body:**
```json
{
  "user_id": "admin",
  "permissions": ["read", "write", "admin"]
}
```

**Response:**
```json
{
  "success": true,
  "api_key": "hk_abc123def456ghi789",
  "user_id": "admin",
  "permissions": ["read", "write", "admin"],
  "created_at": "2026-05-13T20:00:00.000Z"
}
```

---

## **📊 Monitoring Endpoints**

### **Get System Metrics**
```http
GET /api/monitoring/metrics
```

**Response:**
```json
{
  "metrics": {
    "cpu": {
      "usage_percent": 25.5,
      "temperature": 45.0,
      "frequency_mhz": 3200
    },
    "memory": {
      "total_gb": 32.0,
      "used_gb": 7.5,
      "available_gb": 24.5,
      "usage_percent": 23.4
    },
    "gpu": {
      "utilization": 25,
      "memory_used_mb": 2048,
      "temperature": 65
    },
    "network": {
      "bytes_sent": 1048576,
      "bytes_received": 2097152,
      "connections": 5
    }
  },
  "timestamp": "2026-05-13T20:00:00.000Z"
}
```

### **Get Alerts**
```http
GET /api/monitoring/alerts
```

**Query Parameters:**
- `severity` - Filter by severity (low, medium, high, critical)
- `status` - Filter by status (active, resolved)
- `limit` - Maximum number of alerts to return

**Response:**
```json
{
  "alerts": [
    {
      "alert_id": "alert123abc456",
      "severity": "medium",
      "status": "active",
      "title": "High CPU Usage",
      "message": "CPU usage is above 80%",
      "source": "cpu_monitor",
      "created_at": "2026-05-13T20:00:00.000Z"
    }
  ],
  "count": 1,
  "timestamp": "2026-05-13T20:00:00.000Z"
}
```

---

## **🔧 Rate Limiting**

The API implements rate limiting to prevent abuse:
- **Window:** 60 seconds
- **Maximum Requests:** 100 requests per minute per IP
- **Response Headers:** 
  - `X-RateLimit-Limit`: Maximum requests per window
  - `X-RateLimit-Remaining`: Remaining requests in current window
  - `X-RateLimit-Reset`: Time when rate limit window resets

**Rate Limit Exceeded Response:**
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please try again later.",
  "retry_after": 45
}
```

---

## **🛡️ Security Features**

### **API Key Authentication**
Include API key in request header:
```
Authorization: Bearer hk_abc123def456ghi789
```

### **CORS Support**
Cross-Origin Resource Sharing is enabled for all endpoints.

### **Input Validation**
All input data is validated and sanitized.

### **Error Handling**
Standardized error responses:
```json
{
  "error": "Error description",
  "message": "Detailed error message",
  "timestamp": "2026-05-13T20:00:00.000Z"
}
```

---

## **📱 Usage Examples**

### **Python Example**
```python
import requests
import json

# Base URL
base_url = "http://localhost:8080"

# Get portal status
response = requests.get(f"{base_url}/api/portal/status")
status = response.json()
print(f"Portal Status: {status['status']}")

# Start screen sharing
share_data = {
    "target_node": "def456abc123"
}
response = requests.post(
    f"{base_url}/api/portal/share/screen",
    json=share_data,
    headers={"Authorization": "Bearer hk_abc123def456ghi789"}
)
result = response.json()
print(f"Screen Share Session: {result['session_id']}")
```

### **JavaScript Example**
```javascript
// Get portal status
fetch('http://localhost:8080/api/portal/status')
  .then(response => response.json())
  .then(data => {
    console.log('Portal Status:', data.status);
    console.log('Active Nodes:', data.active_nodes_count);
  });

// Share file
const shareData = {
  file_path: 'C:\\Users\\User\\Documents\\test.txt',
  target_node: 'def456abc123'
};

fetch('http://localhost:8080/api/portal/share/file', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer hk_abc123def456ghi789'
  },
  body: JSON.stringify(shareData)
})
.then(response => response.json())
.then(data => {
  console.log('File Share Result:', data.success);
});
```

### **cURL Example**
```bash
# Get portal status
curl -X GET http://localhost:8080/api/portal/status

# Start screen sharing
curl -X POST http://localhost:8080/api/portal/share/screen \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer hk_abc123def456ghi789" \
  -d '{"target_node": "def456abc123"}'

# Get GPU status
curl -X GET http://localhost:8080/api/gpu/status \
  -H "Authorization: Bearer hk_abc123def456ghi789"
```

---

## **🚀 Getting Started**

1. **Start the API Server:**
   ```bash
   python Core Services/rest_api.py
   ```

2. **Generate API Key:**
   ```bash
   curl -X POST http://localhost:8080/api/auth/generate-key \
     -H "Content-Type: application/json" \
     -d '{"user_id": "admin", "permissions": ["read", "write"]}'
   ```

3. **Test API:**
   ```bash
   curl -X GET http://localhost:8080/api/health \
     -H "Authorization: Bearer YOUR_API_KEY"
   ```

---

## **📚 Additional Resources**

- **Portal GUI:** Use `Launch_Homelab_Portal.bat` for graphical interface
- **Configuration:** Modify `config.json` for custom settings
- **Logs:** Check `/logs` directory for detailed logs
- **Troubleshooting:** Run `comprehensive_test_suite.py` for system verification

---

**API Documentation Version:** 1.0.0  
**Last Updated:** 2026-05-13  
**Compatible with:** Homelab Portal v1.0.0+
