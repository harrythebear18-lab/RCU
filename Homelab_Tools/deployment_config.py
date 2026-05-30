#!/usr/bin/env python3
"""
Homelab Deployment Configuration
Optimized for Windows 10 Host + Windows 11 Client setup
"""

import json
import os
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class HostConfig:
    """Windows 10 Host Configuration"""
    os: str = "Windows 10"
    cpu: str = "Intel i7-8700K"
    cpu_cores: int = 6
    cpu_threads: int = 12
    ram_gb: int = 32
    gpu: str = "GTX 1050"
    gpu_memory_gb: int = 4
    storage: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.storage is None:
            self.storage = {
                "ssd_drives": [
                    {"type": "NVMe", "size_gb": 512, "purpose": "OS/Applications"},
                    {"type": "SATA", "size_gb": 1024, "purpose": "Games/Active Data"}
                ],
                "hdd_drives": [
                    {"type": "SATA", "size_gb": 2048, "purpose": "Archive/Backup"},
                    {"type": "SATA", "size_gb": 4096, "purpose": "Media/Storage"}
                ]
            }

@dataclass
class ClientConfig:
    """Windows 11 Client Configuration"""
    os: str = "Windows 11"
    cpu: str = "Intel i5 (Newer Gen)"
    cpu_cores: int = 6
    cpu_threads: int = 12
    ram_gb: int = 16
    gpu: str = "RTX 5060"
    gpu_memory_gb: int = 8
    storage: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.storage is None:
            self.storage = {
                "ssd_drives": [
                    {"type": "NVMe", "size_gb": 512, "purpose": "OS/Applications"}
                ],
                "limited_storage": True
            }

@dataclass
class NetworkConfig:
    """Network Configuration"""
    port: int = 25565  # Minecraft compatible
    protocol: str = "TCP"
    bandwidth_mbps: int = 1000  # 1Gbps network recommended
    latency_optimization: bool = True
    compression: bool = True

@dataclass
class ComputeConfig:
    """Distributed Computing Configuration"""
    # Host (Windows 10) - CPU + Memory focus
    host_role: str = "compute_server"
    host_cpu_allocation: float = 0.8  # 80% of i7-8700K for compute
    host_ram_allocation_gb: int = 24  # 24GB of 32GB for sharing
    host_storage_role: str = "storage_server"
    
    # Client (Windows 11) - GPU + Local processing
    client_role: str = "compute_client"
    client_gpu_allocation: float = 0.9  # 90% of RTX 5060 for compute
    client_ram_usage_gb: int = 8  # 8GB of 16GB for local processing
    client_remote_ram_gb: int = 16  # 16GB from host
    
    # Hybrid compute optimization
    cpu_tasks: List[str] = None
    gpu_tasks: List[str] = None
    
    def __post_init__(self):
        if self.cpu_tasks is None:
            self.cpu_tasks = [
                "data_processing",
                "compression",
                "encryption",
                "file_operations",
                "background_computing"
            ]
        
        if self.gpu_tasks is None:
            self.gpu_tasks = [
                "machine_learning",
                "rendering",
                "gaming",
                "video_processing",
                "ai_inference"
            ]

@dataclass
class StorageConfig:
    """Storage Configuration for Mixed Setup"""
    # Host storage optimization
    host_storage_pools: Dict[str, Any] = None
    client_storage_caching: bool = True
    remote_storage_mount: bool = True
    
    def __post_init__(self):
        if self.host_storage_pools is None:
            self.host_storage_pools = {
                "fast_pool": {
                    "drives": ["NVMe OS", "NVMe Data"],
                    "purpose": "active_compute",
                    "cache_size_gb": 256
                },
                "bulk_pool": {
                    "drives": ["SATA SSD", "HDD Archive", "HDD Media"],
                    "purpose": "bulk_storage",
                    "compression": True
                }
            }

class HomelabDeployment:
    """Main deployment configuration manager"""
    
    def __init__(self):
        self.host = HostConfig()
        self.client = ClientConfig()
        self.network = NetworkConfig()
        self.compute = ComputeConfig()
        self.storage = StorageConfig()
        
        # Performance targets
        self.performance_targets = {
            "rdma_latency_us": 5.0,  # Ultra-low latency target
            "memory_bandwidth_gbps": 25.6,  # DDR4-3200 dual channel
            "gpu_compute_tflops": 12.7,  # RTX 5060 FP32
            "storage_throughput_mbps": 3500,  # NVMe SSD
            "network_throughput_mbps": 940  # Real-world 1Gbps
        }
    
    def generate_host_config(self) -> Dict[str, Any]:
        """Generate configuration for Windows 10 host"""
        config = {
            "system": {
                "role": "host",
                "os": self.host.os,
                "hardware": {
                    "cpu": {
                        "model": self.host.cpu,
                        "cores": self.host.cpu_cores,
                        "threads": self.host.cpu_threads,
                        "base_clock_ghz": 3.7,
                        "boost_clock_ghz": 4.7
                    },
                    "memory": {
                        "total_gb": self.host.ram_gb,
                        "speed_mhz": 3200,
                        "type": "DDR4",
                        "channels": 2
                    },
                    "gpu": {
                        "model": self.host.gpu,
                        "memory_gb": self.host.gpu_memory_gb,
                        "compute_capability": 6.1
                    },
                    "storage": self.host.storage
                },
                "services": {
                    "compute_server": {
                        "enabled": True,
                        "cpu_cores": int(self.host.cpu_cores * self.compute.host_cpu_allocation),
                        "ram_gb": self.compute.host_ram_allocation_gb,
                        "port": self.network.port
                    },
                    "memory_server": {
                        "enabled": True,
                        "shared_ram_gb": 16,
                        "port": self.network.port + 1
                    },
                    "storage_server": {
                        "enabled": True,
                        "export_pools": list(self.storage.host_storage_pools.keys()),
                        "port": self.network.port + 2
                    },
                    "rdma_server": {
                        "enabled": True,
                        "device_path": os.getenv('RDMA_DEVICE_PATH', r'\\.\UltraDMA'),  # Windows-compatible
                        "port": self.network.port + 3
                    }
                }
            }
        }
        
        return config
    
    def generate_client_config(self) -> Dict[str, Any]:
        """Generate configuration for Windows 11 client"""
        config = {
            "system": {
                "role": "client",
                "os": self.client.os,
                "hardware": {
                    "cpu": {
                        "model": self.client.cpu,
                        "cores": self.client.cpu_cores,
                        "threads": self.client.cpu_threads,
                        "base_clock_ghz": 2.5,
                        "boost_clock_ghz": 4.5
                    },
                    "memory": {
                        "total_gb": self.client.ram_gb,
                        "local_usage_gb": self.compute.client_ram_usage_gb,
                        "remote_usage_gb": self.compute.client_remote_ram_gb,
                        "speed_mhz": 4800,
                        "type": "DDR5"
                    },
                    "gpu": {
                        "model": self.client.gpu,
                        "memory_gb": self.client.gpu_memory_gb,
                        "compute_capability": 8.9,
                        "tensor_cores": True,
                        "rt_cores": True
                    },
                    "storage": self.client.storage
                },
                "connections": {
                    "host_address": os.getenv('HOMELAB_HOST_IP', '192.168.1.100'),  # Configurable IP
                    "compute_client": {
                        "enabled": True,
                        "host_port": self.network.port,
                        "gpu_acceleration": True,
                        "hybrid_mode": True
                    },
                    "memory_client": {
                        "enabled": True,
                        "host_port": self.network.port + 1,
                        "remote_ram_gb": self.compute.client_remote_ram_gb
                    },
                    "storage_client": {
                        "enabled": True,
                        "host_port": self.network.port + 2,
                        "mount_point": "Z:\\",
                        "cache_enabled": True
                    },
                    "rdma_client": {
                        "enabled": True,
                        "host_port": self.network.port + 3,
                        "ultra_low_latency": True
                    }
                }
            }
        }
        
        return config
    
    def generate_optimization_settings(self) -> Dict[str, Any]:
        """Generate optimization settings for this specific setup"""
        return {
            "host_optimizations": {
                "cpu": {
                    "priority": "HIGH",
                    "affinity": "cores 0-5",
                    "realtime_threads": 4,
                    "power_plan": "High Performance"
                },
                "memory": {
                    "large_pages": True,
                    "numa_optimization": True,
                    "prefetch_optimization": True
                },
                "storage": {
                    "ssd_optimization": True,
                    "write_caching": True,
                    "defrag_disabled": True,
                    "trim_enabled": True
                },
                "network": {
                    "rdma_enabled": True,
                    "jumbo_frames": True,
                    "interrupt_affinity": True
                }
            },
            "client_optimizations": {
                "gpu": {
                    "power_mode": "PREFER_PERFORMANCE",
                    "cuda_optimization": True,
                    "direct_storage": True,
                    "ray_tracing": True
                },
                "memory": {
                    "swap_optimization": True,
                    "compression": True,
                    "remote_caching": True
                },
                "storage": {
                    "local_cache_gb": 32,
                    "prefetch_enabled": True,
                    "write_behind": True
                }
            }
        }
    
    def generate_deployment_script(self) -> str:
        """Generate deployment script for both systems"""
        script = f'''#!/bin/bash
# Homelab Deployment Script
# Optimized for Windows 10 Host + Windows 11 Client Setup

echo "Starting Homelab Deployment..."

# Host Configuration (Windows 10)
HOST_CONFIG="{json.dumps(self.generate_host_config(), indent=2)}"

# Client Configuration (Windows 11)  
CLIENT_CONFIG="{json.dumps(self.generate_client_config(), indent=2)}"

# Optimization Settings
OPTIMIZATION_CONFIG="{json.dumps(self.generate_optimization_settings(), indent=2)}"

echo "Configuration files generated"
echo "Performance Targets:"
echo "   - RDMA Latency: {self.performance_targets['rdma_latency_us']} μs"
echo "   - Memory Bandwidth: {self.performance_targets['memory_bandwidth_gbps']} GB/s"
echo "   - GPU Compute: {self.performance_targets['gpu_compute_tflops']} TFLOPS"
echo "   - Storage Throughput: {self.performance_targets['storage_throughput_mbps']} MB/s"
echo "   - Network Throughput: {self.performance_targets['network_throughput_mbps']} Mbps"

echo "Deployment ready for:"
echo "   Host: Windows 10, i7-8700K, 32GB RAM, GTX 1050, Mixed SSD/HDD"
echo "   Client: Windows 11, i5, 16GB RAM, RTX 5060, Limited Storage"
'''
        
        return script
    
    def save_configurations(self, output_dir: str = "deployment_configs"):
        """Save all configurations to files"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save host config
        host_config = self.generate_host_config()
        with open(f"{output_dir}/host_config.json", 'w') as f:
            json.dump(host_config, f, indent=2)
        
        # Save client config
        client_config = self.generate_client_config()
        with open(f"{output_dir}/client_config.json", 'w') as f:
            json.dump(client_config, f, indent=2)
        
        # Save optimization settings
        optimization_config = self.generate_optimization_settings()
        with open(f"{output_dir}/optimization_config.json", 'w') as f:
            json.dump(optimization_config, f, indent=2)
        
        # Save deployment script
        script = self.generate_deployment_script()
        with open(f"{output_dir}/deploy.sh", 'w', encoding='utf-8') as f:
            f.write(script)
        
        print(f"Configurations saved to {output_dir}/")
        return {
            "host_config": f"{output_dir}/host_config.json",
            "client_config": f"{output_dir}/client_config.json",
            "optimization_config": f"{output_dir}/optimization_config.json",
            "deployment_script": f"{output_dir}/deploy.sh"
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for this setup"""
        return {
            "theoretical_performance": {
                "host": {
                    "cpu_compute": f"{self.host.cpu_cores * 8} GFLOPS (approx)",
                    "memory_bandwidth": f"{self.performance_targets['memory_bandwidth_gbps']} GB/s",
                    "storage_speed": "Up to 3500 MB/s (NVMe)",
                    "gpu_compute": "2.1 TFLOPS (GTX 1050)"
                },
                "client": {
                    "cpu_compute": f"{self.client.cpu_cores * 10} GFLOPS (approx)",
                    "memory_bandwidth": f"{76.8} GB/s (DDR5-4800)",
                    "storage_speed": "Up to 7000 MB/s (NVMe)",
                    "gpu_compute": f"{self.performance_targets['gpu_compute_tflops']} TFLOPS (RTX 5060)"
                }
            },
            "distributed_benefits": {
                "total_available_ram": f"{self.host.ram_gb + self.client.ram_gb} GB",
                "total_gpu_memory": f"{self.host.gpu_memory_gb + self.client.gpu_memory_gb} GB",
                "hybrid_compute": "i7-8700K CPU + RTX 5060 GPU",
                "storage_capacity": "8TB+ (mixed SSD/HDD)",
                "ultra_low_latency": f"{self.performance_targets['rdma_latency_us']} μs"
            },
            "use_cases": [
                "Gaming with RTX 5060 + remote CPU processing",
                "AI/ML inference with RTX 5060 + large datasets from host",
                "Content creation with remote storage + local GPU rendering",
                "Development with remote compilation + local GPU testing",
                "Data processing with distributed compute + GPU acceleration"
            ]
        }

def main():
    """Generate deployment configuration"""
    deployment = HomelabDeployment()
    
    # Save configurations
    config_files = deployment.save_configurations()
    
    # Print performance summary
    summary = deployment.get_performance_summary()
    print("\nHomelab Performance Summary:")
    print(json.dumps(summary, indent=2))
    
    print(f"\nConfiguration files created:")
    for name, path in config_files.items():
        print(f"   {name}: {path}")

if __name__ == "__main__":
    main()
