#!/usr/bin/env python3
"""
Deployment Automation and Configuration Management
Automated deployment, scaling, and configuration for Software-Defined RDMA
"""

import os
import sys
import json
import yaml
import time
import threading
import subprocess
import shutil
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import docker
import kubernetes
from jinja2 import Template
import logging
import hashlib
import requests

@dataclass
class DeploymentConfig:
    """Deployment configuration"""
    environment: str
    version: str
    replicas: int
    cpu_limit: str
    memory_limit: str
    network_mode: str
    storage_size: str
    security_enabled: bool
    monitoring_enabled: bool
    auto_scaling: bool
    min_replicas: int
    max_replicas: int
    target_cpu_utilization: int

@dataclass
class ServiceConfig:
    """Service configuration"""
    name: str
    port: int
    target_port: int
    protocol: str
    load_balancer: bool
    health_check_path: str
    health_check_interval: int

class ConfigurationManager:
    """Manages configuration templates and environment-specific settings"""
    
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        # Configuration templates
        self.templates = {}
        self.environments = {}
        
        # Load configurations
        self._load_templates()
        self._load_environments()
    
    def _load_templates(self):
        """Load configuration templates"""
        template_files = {
            'docker': 'docker-compose.yml.j2',
            'kubernetes': 'k8s-deployment.yml.j2',
            'systemd': 'dma-service.service.j2',
            'nginx': 'nginx.conf.j2',
            'haproxy': 'haproxy.cfg.j2'
        }
        
        for template_name, filename in template_files.items():
            template_path = self.config_dir / filename
            if template_path.exists():
                with open(template_path) as f:
                    self.templates[template_name] = Template(f.read())
            else:
                self.templates[template_name] = self._create_default_template(template_name)
    
    def _create_default_template(self, template_name: str) -> Template:
        """Create default template if file doesn't exist"""
        default_templates = {
            'docker': '''
version: '3.8'
services:
  dma-server:
    image: software-defined-rdma:{{ version }}
    container_name: dma-server-{{ environment }}
    restart: unless-stopped
    ports:
      - "{{ ports.zeromq }}:5555"
      - "{{ ports.pcie }}:7777"
      - "{{ ports.udp }}:9999"
    environment:
      - ENVIRONMENT={{ environment }}
      - LOG_LEVEL={{ log_level }}
      - SECURITY_ENABLED={{ security_enabled }}
    volumes:
      - dma_data:/data
      - dma_logs:/logs
    networks:
      - dma-network
    deploy:
      replicas: {{ replicas }}
      resources:
        limits:
          cpus: '{{ cpu_limit }}'
          memory: {{ memory_limit }}'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  dma-monitoring:
    image: software-defined-rdma-monitoring:{{ version }}
    container_name: dma-monitoring-{{ environment }}
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - ENVIRONMENT={{ environment }}
    volumes:
      - dma_logs:/logs:ro
    networks:
      - dma-network
    depends_on:
      - dma-server

volumes:
  dma_data:
  dma_logs:

networks:
  dma-network:
    driver: bridge
''',
            'kubernetes': '''
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dma-server
  namespace: {{ namespace }}
  labels:
    app: dma-server
    version: {{ version }}
spec:
  replicas: {{ replicas }}
  selector:
    matchLabels:
      app: dma-server
  template:
    metadata:
      labels:
        app: dma-server
        version: {{ version }}
    spec:
      containers:
      - name: dma-server
        image: software-defined-rdma:{{ version }}
        ports:
        - containerPort: 5555
          name: zeromq
        - containerPort: 7777
          name: pcie
        - containerPort: 9999
          name: udp
        env:
        - name: ENVIRONMENT
          value: "{{ environment }}"
        - name: LOG_LEVEL
          value: "{{ log_level }}"
        - name: SECURITY_ENABLED
          value: "{{ security_enabled }}"
        resources:
          requests:
            memory: "{{ memory_request }}"
            cpu: "{{ cpu_request }}"
          limits:
            memory: "{{ memory_limit }}"
            cpu: "{{ cpu_limit }}"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: dma-data
          mountPath: /data
        - name: dma-logs
          mountPath: /logs
      volumes:
      - name: dma-data
        persistentVolumeClaim:
          claimName: dma-data-pvc
      - name: dma-logs
        persistentVolumeClaim:
          claimName: dma-logs-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: dma-server-service
  namespace: {{ namespace }}
spec:
  selector:
    app: dma-server
  ports:
  - name: zeromq
    port: 5555
    targetPort: 5555
  - name: pcie
    port: 7777
    targetPort: 7777
  - name: udp
    port: 9999
    targetPort: 9999
  type: {{ service_type }}
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: dma-server-hpa
  namespace: {{ namespace }}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: dma-server
  minReplicas: {{ min_replicas }}
  maxReplicas: {{ max_replicas }}
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: {{ target_cpu_utilization }}
''',
            'systemd': '''
[Unit]
Description=Software-Defined RDMA Server
After=network.target
Wants=network.target

[Service]
Type=notify
NotifyAccess=all
User=dma
Group=dma
ExecStart=/opt/dma/bin/dma-server --config=/etc/dma/dma.conf
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=5
LimitNOFILE=65536
LimitMEMLOCK=infinity

[Install]
WantedBy=multi-user.target
''',
            'nginx': '''
upstream dma_backend {
    least_conn;
    server {{ upstream_host }}:{{ upstream_port }} max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    server_name {{ server_name }};
    
    location / {
        proxy_pass http://dma_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
    
    location /metrics {
        proxy_pass http://dma_backend/metrics;
        allow 127.0.0.1;
        allow 10.0.0.0/8;
        deny all;
    }
}
''',
            'haproxy': '''
global
    daemon
    maxconn 4096
    log stdout local0
    
defaults
    mode http
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms
    option httplog
    option dontlognull
    
frontend dma_frontend
    bind *:80
    default_backend dma_backend
    
backend dma_backend
    balance roundrobin
    option httpchk GET /health
    server dma1 {{ backend_host }}:{{ backend_port }} check
    server dma2 {{ backend_host }}:{{ backend_port }} check backup
'''
        }
        
        template_content = default_templates.get(template_name, "")
        template = Template(template_content)
        
        # Save template to file
        template_path = self.config_dir / f"{template_name}.yml.j2"
        with open(template_path, 'w') as f:
            f.write(template_content)
        
        return template
    
    def _load_environments(self):
        """Load environment-specific configurations"""
        env_files = {
            'development': 'development.yml',
            'staging': 'staging.yml',
            'production': 'production.yml'
        }
        
        for env_name, filename in env_files.items():
            env_path = self.config_dir / filename
            if env_path.exists():
                with open(env_path) as f:
                    self.environments[env_name] = yaml.safe_load(f)
            else:
                self.environments[env_name] = self._create_default_environment(env_name)
    
    def _create_default_environment(self, env_name: str) -> Dict:
        """Create default environment configuration"""
        default_configs = {
            'development': {
                'version': 'latest',
                'replicas': 1,
                'cpu_limit': '2',
                'memory_limit': '4Gi',
                'namespace': 'dma-dev',
                'log_level': 'debug',
                'security_enabled': False,
                'monitoring_enabled': True,
                'ports': {
                    'zeromq': 15555,
                    'pcie': 17777,
                    'udp': 19999
                }
            },
            'staging': {
                'version': 'v1.0.0',
                'replicas': 2,
                'cpu_limit': '4',
                'memory_limit': '8Gi',
                'namespace': 'dma-staging',
                'log_level': 'info',
                'security_enabled': True,
                'monitoring_enabled': True,
                'ports': {
                    'zeromq': 25555,
                    'pcie': 27777,
                    'udp': 29999
                }
            },
            'production': {
                'version': 'v1.0.0',
                'replicas': 3,
                'cpu_limit': '8',
                'memory_limit': '16Gi',
                'namespace': 'dma-prod',
                'log_level': 'warn',
                'security_enabled': True,
                'monitoring_enabled': True,
                'auto_scaling': True,
                'min_replicas': 3,
                'max_replicas': 10,
                'target_cpu_utilization': 70,
                'ports': {
                    'zeromq': 5555,
                    'pcie': 7777,
                    'udp': 9999
                }
            }
        }
        
        config = default_configs.get(env_name, default_configs['development'])
        
        # Save environment config
        env_path = self.config_dir / f"{env_name}.yml"
        with open(env_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        return config
    
    def render_config(self, template_name: str, environment: str, **kwargs) -> str:
        """Render configuration template"""
        if template_name not in self.templates:
            raise ValueError(f"Template {template_name} not found")
        
        if environment not in self.environments:
            raise ValueError(f"Environment {environment} not found")
        
        # Merge environment config with additional kwargs
        config = self.environments[environment].copy()
        config.update(kwargs)
        
        # Render template
        template = self.templates[template_name]
        return template.render(**config)
    
    def save_rendered_config(self, template_name: str, environment: str, 
                           output_dir: str = "deployments", **kwargs) -> str:
        """Render and save configuration to file"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        rendered = self.render_config(template_name, environment, **kwargs)
        
        # Determine output filename
        if template_name == 'docker':
            filename = 'docker-compose.yml'
        elif template_name == 'kubernetes':
            filename = 'k8s-deployment.yml'
        elif template_name == 'systemd':
            filename = 'dma-service.service'
        else:
            filename = f"{template_name}.conf"
        
        output_file = output_path / f"{environment}-{filename}"
        
        with open(output_file, 'w') as f:
            f.write(rendered)
        
        return str(output_file)

class DockerDeployment:
    """Docker-based deployment management"""
    
    def __init__(self):
        try:
            self.client = docker.from_env()
            self.client.ping()
        except docker.errors.DockerException:
            print("Docker not available or not running")
            self.client = None
    
    def build_image(self, dockerfile_path: str, context_path: str, tag: str) -> bool:
        """Build Docker image"""
        if not self.client:
            return False
        
        try:
            print(f"Building Docker image: {tag}")
            
            # Build image
            image, build_logs = self.client.images.build(
                path=context_path,
                dockerfile=dockerfile_path,
                tag=tag,
                rm=True
            )
            
            print(f"Image built successfully: {image.id}")
            return True
            
        except docker.errors.BuildError as e:
            print(f"Build failed: {e}")
            return False
    
    def push_image(self, tag: str, registry: str = None) -> bool:
        """Push Docker image to registry"""
        if not self.client:
            return False
        
        try:
            if registry:
                full_tag = f"{registry}/{tag}"
                # Tag for registry
                image = self.client.images.get(tag)
                image.tag(full_tag, tag='latest')
                tag = full_tag
            
            print(f"Pushing image: {tag}")
            push_logs = self.client.images.push(tag, stream=True, decode=True)
            
            for log in push_logs:
                if 'status' in log:
                    print(f"  {log['status']}")
                elif 'error' in log:
                    print(f"  Error: {log['error']}")
                    return False
            
            print("Image pushed successfully")
            return True
            
        except docker.errors.APIError as e:
            print(f"Push failed: {e}")
            return False
    
    def deploy_compose(self, compose_file: str) -> bool:
        """Deploy using docker-compose"""
        try:
            print(f"Deploying with docker-compose: {compose_file}")
            
            # Use docker-compose CLI
            cmd = ['docker-compose', '-f', compose_file, 'up', '-d']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("Deployment successful")
                print(result.stdout)
                return True
            else:
                print(f"Deployment failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Compose deployment error: {e}")
            return False
    
    def scale_service(self, service_name: str, replicas: int) -> bool:
        """Scale Docker service"""
        try:
            print(f"Scaling service {service_name} to {replicas} replicas")
            
            cmd = ['docker-compose', 'scale', f'{service_name}={replicas}']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("Scale successful")
                return True
            else:
                print(f"Scale failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Scale error: {e}")
            return False
    
    def get_service_status(self, service_name: str = None) -> Dict:
        """Get status of deployed services"""
        if not self.client:
            return {}
        
        try:
            containers = self.client.containers.list(all=True)
            
            status = {}
            for container in containers:
                name = container.name
                container_status = {
                    'status': container.status,
                    'image': container.image.tags[0] if container.image.tags else 'unknown',
                    'created': container.attrs['Created'],
                    'ports': container.attrs.get('NetworkSettings', {}).get('Ports', {})
                }
                
                if service_name is None or service_name in name:
                    status[name] = container_status
            
            return status
            
        except Exception as e:
            print(f"Error getting status: {e}")
            return {}

class KubernetesDeployment:
    """Kubernetes-based deployment management"""
    
    def __init__(self):
        try:
            kubernetes.config.load_kube_config()
            self.v1 = kubernetes.client.CoreV1Api()
            self.apps_v1 = kubernetes.client.AppsV1Api()
            self.autoscaling_v1 = kubernetes.client.AutoscalingV1Api()
            self.connected = True
        except Exception as e:
            print(f"Kubernetes not available: {e}")
            self.connected = False
    
    def create_namespace(self, namespace: str) -> bool:
        """Create Kubernetes namespace"""
        if not self.connected:
            return False
        
        try:
            namespace_obj = kubernetes.client.V1Namespace(
                metadata=kubernetes.client.V1ObjectMeta(name=namespace)
            )
            
            self.v1.create_namespace(body=namespace_obj)
            print(f"Namespace {namespace} created")
            return True
            
        except kubernetes.client.ApiException as e:
            if e.status == 409:
                print(f"Namespace {namespace} already exists")
                return True
            else:
                print(f"Failed to create namespace: {e}")
                return False
    
    def apply_manifest(self, manifest_file: str) -> bool:
        """Apply Kubernetes manifest"""
        if not self.connected:
            return False
        
        try:
            print(f"Applying manifest: {manifest_file}")
            
            cmd = ['kubectl', 'apply', '-f', manifest_file]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("Manifest applied successfully")
                print(result.stdout)
                return True
            else:
                print(f"Manifest application failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Manifest error: {e}")
            return False
    
    def get_deployment_status(self, namespace: str) -> Dict:
        """Get deployment status"""
        if not self.connected:
            return {}
        
        try:
            deployments = self.apps_v1.list_namespaced_deployment(namespace=namespace)
            
            status = {}
            for deployment in deployments.items:
                status[deployment.metadata.name] = {
                    'replicas': deployment.spec.replicas,
                    'ready_replicas': deployment.status.ready_replicas or 0,
                    'available_replicas': deployment.status.available_replicas or 0,
                    'conditions': [
                        {
                            'type': condition.type,
                            'status': condition.status,
                            'reason': condition.reason
                        }
                        for condition in deployment.status.conditions or []
                    ]
                }
            
            return status
            
        except Exception as e:
            print(f"Error getting deployment status: {e}")
            return {}
    
    def scale_deployment(self, namespace: str, deployment_name: str, replicas: int) -> bool:
        """Scale Kubernetes deployment"""
        if not self.connected:
            return False
        
        try:
            # Get current deployment
            deployment = self.apps_v1.read_namespaced_deployment(
                name=deployment_name, namespace=namespace
            )
            
            # Update replicas
            deployment.spec.replicas = replicas
            
            # Apply update
            self.apps_v1.patch_namespaced_deployment(
                name=deployment_name, namespace=namespace, body=deployment
            )
            
            print(f"Scaled {deployment_name} to {replicas} replicas")
            return True
            
        except Exception as e:
            print(f"Scale failed: {e}")
            return False

class DeploymentManager:
    """Main deployment manager coordinating all deployment methods"""
    
    def __init__(self):
        self.config_manager = ConfigurationManager()
        self.docker_deployment = DockerDeployment()
        self.k8s_deployment = KubernetesDeployment()
        
        # Deployment registry
        self.deployments: Dict[str, Dict] = {}
        
        # Load deployment registry
        self._load_deployment_registry()
    
    def _load_deployment_registry(self):
        """Load deployment registry"""
        registry_file = Path("deployment_registry.json")
        
        if registry_file.exists():
            with open(registry_file) as f:
                self.deployments = json.load(f)
    
    def _save_deployment_registry(self):
        """Save deployment registry"""
        with open("deployment_registry.json", 'w') as f:
            json.dump(self.deployments, f, indent=2, default=str)
    
    def deploy(self, environment: str, deployment_type: str = 'docker', 
               version: str = 'latest', **kwargs) -> bool:
        """Deploy application"""
        print(f"Deploying to {environment} using {deployment_type}")
        
        # Generate deployment ID
        deployment_id = f"{environment}-{deployment_type}-{int(time.time())}"
        
        # Create deployment record
        deployment_record = {
            'id': deployment_id,
            'environment': environment,
            'type': deployment_type,
            'version': version,
            'status': 'deploying',
            'created_at': time.time(),
            'config': kwargs
        }
        
        try:
            if deployment_type == 'docker':
                success = self._deploy_docker(environment, version, **kwargs)
            elif deployment_type == 'kubernetes':
                success = self._deploy_kubernetes(environment, version, **kwargs)
            elif deployment_type == 'systemd':
                success = self._deploy_systemd(environment, version, **kwargs)
            else:
                raise ValueError(f"Unknown deployment type: {deployment_type}")
            
            if success:
                deployment_record['status'] = 'deployed'
                deployment_record['deployed_at'] = time.time()
                print(f"Deployment {deployment_id} successful")
            else:
                deployment_record['status'] = 'failed'
                print(f"Deployment {deployment_id} failed")
            
            # Save deployment record
            self.deployments[deployment_id] = deployment_record
            self._save_deployment_registry()
            
            return success
            
        except Exception as e:
            deployment_record['status'] = 'failed'
            deployment_record['error'] = str(e)
            self.deployments[deployment_id] = deployment_record
            self._save_deployment_registry()
            
            print(f"Deployment error: {e}")
            return False
    
    def _deploy_docker(self, environment: str, version: str, **kwargs) -> bool:
        """Deploy using Docker"""
        # Generate docker-compose file
        compose_file = self.config_manager.save_rendered_config(
            'docker', environment, version=version, **kwargs
        )
        
        # Deploy with docker-compose
        return self.docker_deployment.deploy_compose(compose_file)
    
    def _deploy_kubernetes(self, environment: str, version: str, **kwargs) -> bool:
        """Deploy using Kubernetes"""
        # Create namespace
        namespace = self.config_manager.environments[environment].get('namespace', f'dma-{environment}')
        self.k8s_deployment.create_namespace(namespace)
        
        # Generate Kubernetes manifests
        k8s_file = self.config_manager.save_rendered_config(
            'kubernetes', environment, version=version, namespace=namespace, **kwargs
        )
        
        # Apply manifests
        return self.k8s_deployment.apply_manifest(k8s_file)
    
    def _deploy_systemd(self, environment: str, version: str, **kwargs) -> bool:
        """Deploy using systemd"""
        # Generate systemd service file
        service_file = self.config_manager.save_rendered_config(
            'systemd', environment, version=version, **kwargs
        )
        
        try:
            # Copy service file
            system_path = Path('/etc/systemd/system')
            if os.geteuid() == 0:  # Running as root
                shutil.copy(service_file, system_path / 'dma-server.service')
                
                # Reload systemd and start service
                subprocess.run(['systemctl', 'daemon-reload'], check=True)
                subprocess.run(['systemctl', 'enable', 'dma-server'], check=True)
                subprocess.run(['systemctl', 'start', 'dma-server'], check=True)
                
                print("Systemd service deployed and started")
                return True
            else:
                print("Systemd deployment requires root privileges")
                return False
                
        except Exception as e:
            print(f"Systemd deployment failed: {e}")
            return False
    
    def scale(self, deployment_id: str, replicas: int) -> bool:
        """Scale deployment"""
        if deployment_id not in self.deployments:
            print(f"Deployment {deployment_id} not found")
            return False
        
        deployment = self.deployments[deployment_id]
        
        try:
            if deployment['type'] == 'docker':
                return self.docker_deployment.scale_service('dma-server', replicas)
            elif deployment['type'] == 'kubernetes':
                namespace = deployment['config'].get('namespace', f'dma-{deployment["environment"]}')
                return self.k8s_deployment.scale_deployment(namespace, 'dma-server', replicas)
            else:
                print(f"Scaling not supported for {deployment['type']}")
                return False
                
        except Exception as e:
            print(f"Scale failed: {e}")
            return False
    
    def get_status(self, deployment_id: str = None) -> Dict:
        """Get deployment status"""
        if deployment_id:
            if deployment_id not in self.deployments:
                return {}
            
            deployment = self.deployments[deployment_id]
            
            # Get specific deployment status
            if deployment['type'] == 'docker':
                return self.docker_deployment.get_service_status()
            elif deployment['type'] == 'kubernetes':
                namespace = deployment['config'].get('namespace', f'dma-{deployment["environment"]}')
                return self.k8s_deployment.get_deployment_status(namespace)
            else:
                return {'status': deployment['status']}
        else:
            # Get all deployments status
            all_status = {}
            for dep_id, deployment in self.deployments.items():
                all_status[dep_id] = {
                    'environment': deployment['environment'],
                    'type': deployment['type'],
                    'version': deployment['version'],
                    'status': deployment['status'],
                    'created_at': deployment['created_at']
                }
            
            return all_status
    
    def rollback(self, deployment_id: str) -> bool:
        """Rollback deployment"""
        print(f"Rollback not implemented for deployment {deployment_id}")
        return False
    
    def cleanup(self, deployment_id: str) -> bool:
        """Cleanup deployment"""
        print(f"Cleanup not implemented for deployment {deployment_id}")
        return False

def demo_deployment_manager():
    """Demonstration of deployment manager"""
    print("Deployment Manager Demo")
    print("=" * 30)
    
    manager = DeploymentManager()
    
    # Test configuration rendering
    print("Testing configuration rendering...")
    docker_config = manager.config_manager.render_config(
        'docker', 'development', version='v1.0.0'
    )
    print("✓ Docker configuration rendered")
    
    # Test deployment (dry run)
    print("\nTesting deployment (dry run)...")
    success = manager.deploy(
        environment='development',
        deployment_type='docker',
        version='v1.0.0-test'
    )
    
    if success:
        print("✓ Deployment successful")
        
        # Get status
        status = manager.get_status()
        print(f"Deployments: {len(status)}")
        
    else:
        print("✗ Deployment failed")

if __name__ == "__main__":
    demo_deployment_manager()
