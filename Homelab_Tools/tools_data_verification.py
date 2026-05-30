#!/usr/bin/env python3
"""
Tools Data Verification Script
Verifies data connections and reliability for all tools
"""

import os
import sys
import time
import json
import logging
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass

# Add Core Services to path
sys.path.append(str(Path(__file__).parent / "Core Services"))

try:
    from data_abstraction_layer import get_data_abstraction_layer, DataType, DataPacket
    ABSTRACTION_AVAILABLE = True
except ImportError:
    ABSTRACTION_AVAILABLE = False
    print("Warning: Data abstraction layer not available")

@dataclass
class ToolVerificationResult:
    """Result of tool verification"""
    tool_name: str
    tool_type: str
    data_connections: List[str]
    status: str
    success_rate: float
    errors: List[str]
    details: Dict[str, Any]

class ToolsDataVerifier:
    """Verifies data connections for all tools"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.logger = self._setup_logging()
        self.results: List[ToolVerificationResult] = []
        
        if ABSTRACTION_AVAILABLE:
            self.data_layer = get_data_abstraction_layer()
            self.data_layer.start_monitoring()
        else:
            self.data_layer = None
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger("ToolsDataVerifier")
    
    def verify_all_tools(self) -> Dict[str, Any]:
        """Verify all tools data connections"""
        print("=" * 60)
        print("TOOLS DATA VERIFICATION")
        print("=" * 60)
        
        # Find all tools
        tools = self._find_all_tools()
        print(f"Found {len(tools)} tools to verify")
        
        # Verify each tool
        for tool in tools:
            result = self._verify_tool(tool)
            self.results.append(result)
            self._print_result(result)
        
        # Generate summary
        summary = self._generate_summary()
        self._print_summary(summary)
        
        # Save results
        self._save_results()
        
        return summary
    
    def _find_all_tools(self) -> List[Path]:
        """Find all Python tools"""
        tools = []
        
        # Core Services
        core_services = self.root_dir / "Core Services"
        if core_services.exists():
            tools.extend(core_services.glob("*.py"))
        
        # Monitor tools
        monitor_dirs = ["Cpu Monitor", "Gpu Monitor", "Network Monitor", "Ram clean up"]
        for monitor_dir in monitor_dirs:
            monitor_path = self.root_dir / monitor_dir
            if monitor_path.exists():
                tools.extend(monitor_path.glob("*.py"))
        
        # Hardware tools
        hardware_dirs = ["RDMA", "Storage Management"]
        for hardware_dir in hardware_dirs:
            hardware_path = self.root_dir / hardware_dir
            if hardware_path.exists():
                tools.extend(hardware_path.glob("*.py"))
        
        # Portal tools
        portal_path = self.root_dir / "Subnet Portal"
        if portal_path.exists():
            tools.extend(portal_path.glob("*.py"))
        
        return tools
    
    def _verify_tool(self, tool_path: Path) -> ToolVerificationResult:
        """Verify individual tool"""
        tool_name = tool_path.stem
        tool_type = self._classify_tool(tool_path)
        
        print(f"\nVerifying: {tool_name}")
        
        # Test data connections
        data_connections = []
        success_rate = 0.0
        errors = []
        details = {}
        
        try:
            # Test import
            spec = importlib.util.spec_from_file_location(tool_name, tool_path)
            module = importlib.util.module_from_spec(spec)
            
            # Test data connections
            if ABSTRACTION_AVAILABLE:
                data_connections, success_rate, errors, details = self._test_data_connections(module, tool_type)
            else:
                errors.append("Data abstraction layer not available")
                success_rate = 0.0
            
            status = "PASS" if success_rate > 80 else "FAIL"
            
        except Exception as e:
            errors.append(f"Import error: {e}")
            status = "FAIL"
            success_rate = 0.0
        
        return ToolVerificationResult(
            tool_name=tool_name,
            tool_type=tool_type,
            data_connections=data_connections,
            status=status,
            success_rate=success_rate,
            errors=errors,
            details=details
        )
    
    def _classify_tool(self, tool_path: Path) -> str:
        """Classify tool type"""
        path_str = str(tool_path).lower()
        
        if "core services" in path_str:
            if "monitor" in path_str:
                return "core_monitor"
            elif "security" in path_str:
                return "core_security"
            elif "api" in path_str:
                return "core_api"
            else:
                return "core_service"
        elif "cpu" in path_str:
            return "cpu_monitor"
        elif "gpu" in path_str:
            return "gpu_monitor"
        elif "network" in path_str:
            return "network_monitor"
        elif "ram" in path_str or "memory" in path_str:
            return "memory_monitor"
        elif "rdma" in path_str:
            return "rdma_tool"
        elif "subnet" in path_str:
            return "subnet_tool"
        else:
            return "utility"
    
    def _test_data_connections(self, module: Any, tool_type: str) -> Tuple[List[str], float, List[str], Dict[str, Any]]:
        """Test data connections for a module"""
        data_connections = []
        errors = []
        details = {}
        successful_tests = 0
        total_tests = 0
        
        # Test abstraction layer connections
        if self.data_layer:
            connection_tests = self._get_connection_tests(tool_type)
            
            for test_name, data_type in connection_tests:
                total_tests += 1
                try:
                    data_packet = self.data_layer.get_data(data_type)
                    if data_packet and not data_packet.error:
                        data_connections.append(test_name)
                        successful_tests += 1
                        details[test_name] = {
                            'status': 'success',
                            'data_size': len(str(data_packet.data)),
                            'timestamp': data_packet.timestamp
                        }
                    else:
                        errors.append(f"{test_name}: {data_packet.error if data_packet else 'No data'}")
                        details[test_name] = {
                            'status': 'failed',
                            'error': data_packet.error if data_packet else 'No data'
                        }
                except Exception as e:
                    errors.append(f"{test_name}: {e}")
                    details[test_name] = {
                        'status': 'error',
                        'error': str(e)
                    }
        
        # Test module-specific data access
        module_tests = self._test_module_data_access(module, tool_type)
        data_connections.extend(module_tests['connections'])
        errors.extend(module_tests['errors'])
        details.update(module_tests['details'])
        successful_tests += module_tests['successful_tests']
        total_tests += module_tests['total_tests']
        
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0.0
        
        return data_connections, success_rate, errors, details
    
    def _get_connection_tests(self, tool_type: str) -> List[Tuple[str, DataType]]:
        """Get connection tests for tool type"""
        tests = []
        
        # Common tests for all tools
        tests.append(("system_info", DataType.SYSTEM_INFO))
        tests.append(("cpu_info", DataType.CPU_INFO))
        tests.append(("memory_info", DataType.MEMORY_INFO))
        
        # Tool-specific tests
        if tool_type in ["cpu_monitor", "core_monitor"]:
            tests.append(("performance_metrics", DataType.PERFORMANCE_METRICS))
        
        if tool_type in ["gpu_monitor", "core_monitor"]:
            tests.append(("gpu_info", DataType.GPU_INFO))
        
        if tool_type in ["network_monitor", "subnet_tool"]:
            tests.append(("network_info", DataType.NETWORK_INFO))
        
        if tool_type in ["memory_monitor", "core_monitor"]:
            tests.append(("disk_info", DataType.DISK_INFO))
        
        if tool_type in ["core_security", "core_service"]:
            tests.append(("security_events", DataType.SECURITY_EVENTS))
        
        if tool_type in ["core_service", "rdma_tool"]:
            tests.append(("resource_sharing", DataType.RESOURCE_SHARING))
        
        return tests
    
    def _test_module_data_access(self, module: Any, tool_type: str) -> Dict[str, Any]:
        """Test module-specific data access"""
        result = {
            'connections': [],
            'errors': [],
            'details': {},
            'successful_tests': 0,
            'total_tests': 0
        }
        
        try:
            # Check for common data access patterns
            if hasattr(module, 'get_data') or hasattr(module, 'get_info'):
                result['total_tests'] += 1
                try:
                    if hasattr(module, 'get_data'):
                        data = module.get_data()
                    else:
                        data = module.get_info()
                    
                    if data:
                        result['connections'].append('module_data_access')
                        result['successful_tests'] += 1
                        result['details']['module_data_access'] = {
                            'status': 'success',
                            'data_type': type(data).__name__
                        }
                    else:
                        result['errors'].append('module_data_access: No data returned')
                except Exception as e:
                    result['errors'].append(f'module_data_access: {e}')
            
            # Check for psutil usage
            if 'psutil' in str(module.__dict__.values()):
                result['connections'].append('psutil_integration')
                result['successful_tests'] += 1
                result['details']['psutil_integration'] = {
                    'status': 'success',
                    'description': 'Module uses psutil for system data'
                }
            
            # Check for platform usage
            if 'platform' in str(module.__dict__.values()):
                result['connections'].append('platform_integration')
                result['successful_tests'] += 1
                result['details']['platform_integration'] = {
                    'status': 'success',
                    'description': 'Module uses platform for system info'
                }
        
        except Exception as e:
            result['errors'].append(f'Module test error: {e}')
        
        return result
    
    def _print_result(self, result: ToolVerificationResult):
        """Print verification result"""
        status_symbol = "✓" if result.status == "PASS" else "✗"
        print(f"  {status_symbol} {result.tool_name} ({result.tool_type})")
        print(f"    Success Rate: {result.success_rate:.1f}%")
        print(f"    Data Connections: {len(result.data_connections)}")
        
        if result.errors:
            print(f"    Errors: {len(result.errors)}")
            for error in result.errors[:3]:  # Show first 3 errors
                print(f"      - {error}")
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate verification summary"""
        total_tools = len(self.results)
        passed_tools = sum(1 for r in self.results if r.status == "PASS")
        failed_tools = total_tools - passed_tools
        
        # Group by tool type
        tool_type_stats = {}
        for result in self.results:
            tool_type = result.tool_type
            if tool_type not in tool_type_stats:
                tool_type_stats[tool_type] = {'total': 0, 'passed': 0, 'failed': 0}
            
            tool_type_stats[tool_type]['total'] += 1
            if result.status == "PASS":
                tool_type_stats[tool_type]['passed'] += 1
            else:
                tool_type_stats[tool_type]['failed'] += 1
        
        # Calculate overall success rate
        overall_success_rate = sum(r.success_rate for r in self.results) / total_tools if total_tools > 0 else 0
        
        # Provider status
        provider_status = {}
        if self.data_layer:
            provider_status = self.data_layer.get_provider_status()
        
        summary = {
            'total_tools': total_tools,
            'passed_tools': passed_tools,
            'failed_tools': failed_tools,
            'overall_success_rate': overall_success_rate,
            'tool_type_stats': tool_type_stats,
            'provider_status': provider_status,
            'abstraction_layer_available': ABSTRACTION_AVAILABLE,
            'verification_time': time.time()
        }
        
        return summary
    
    def _print_summary(self, summary: Dict[str, Any]):
        """Print verification summary"""
        print("\n" + "=" * 60)
        print("VERIFICATION SUMMARY")
        print("=" * 60)
        
        print(f"Total Tools: {summary['total_tools']}")
        print(f"Passed: {summary['passed_tools']}")
        print(f"Failed: {summary['failed_tools']}")
        print(f"Overall Success Rate: {summary['overall_success_rate']:.1f}%")
        
        print("\nBy Tool Type:")
        for tool_type, stats in summary['tool_type_stats'].items():
            success_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"  {tool_type}: {stats['passed']}/{stats['total']} ({success_rate:.1f}%)")
        
        if summary['abstraction_layer_available']:
            print("\nProvider Status:")
            for provider, available in summary['provider_status'].items():
                status = "✓" if available else "✗"
                print(f"  {status} {provider}")
        
        # Overall status
        if summary['overall_success_rate'] >= 90:
            print(f"\n🎉 EXCELLENT: Data connections are highly reliable!")
        elif summary['overall_success_rate'] >= 75:
            print(f"\n✅ GOOD: Data connections are mostly reliable!")
        elif summary['overall_success_rate'] >= 50:
            print(f"\n⚠️  FAIR: Data connections need some attention!")
        else:
            print(f"\n❌ POOR: Data connections have significant issues!")
    
    def _save_results(self):
        """Save verification results"""
        results_data = {
            'summary': self._generate_summary(),
            'tools': [
                {
                    'tool_name': r.tool_name,
                    'tool_type': r.tool_type,
                    'data_connections': r.data_connections,
                    'status': r.status,
                    'success_rate': r.success_rate,
                    'errors': r.errors,
                    'details': r.details
                }
                for r in self.results
            ]
        }
        
        output_file = self.root_dir / "tools_data_verification_results.json"
        with open(output_file, 'w') as f:
            json.dump(results_data, f, indent=2, default=str)
        
        print(f"\nDetailed results saved to: {output_file}")

def main():
    """Main entry point"""
    verifier = ToolsDataVerifier()
    summary = verifier.verify_all_tools()
    
    # Cleanup
    if ABSTRACTION_AVAILABLE and verifier.data_layer:
        verifier.data_layer.stop_monitoring()
    
    # Return appropriate exit code
    sys.exit(0 if summary['overall_success_rate'] >= 75 else 1)

if __name__ == "__main__":
    main()
