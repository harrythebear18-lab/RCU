#!/usr/bin/env python3
"""
Abstraction Layer Integration Test
Tests Windows version abstraction, data abstraction, and frontend-backend mixer integration
"""

import sys
import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

# Add Core Services to path
sys.path.append(str(Path(__file__).parent / "Core Services"))

try:
    from windows_version_abstraction import get_windows_abstraction_layer, is_windows_11, is_windows_10, get_windows_optimizations
    from data_abstraction_layer import get_data_abstraction_layer, DataType
    from frontend_backend_mixer import get_frontend_backend_mixer, create_tkinter_frontend, create_flask_backend, start_mixer, stop_mixer
    ALL_LAYERS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some abstraction layers not available: {e}")
    ALL_LAYERS_AVAILABLE = False

class AbstractionLayerTester:
    """Tests all abstraction layers integration"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.test_results = {}
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger("AbstractionLayerTester")
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests"""
        print("=" * 60)
        print("ABSTRACTION LAYER INTEGRATION TEST")
        print("=" * 60)
        
        if not ALL_LAYERS_AVAILABLE:
            print("❌ Some abstraction layers not available - skipping tests")
            return {'status': 'failed', 'reason': 'Missing abstraction layers'}
        
        # Test Windows version abstraction
        windows_result = self.test_windows_version_abstraction()
        
        # Test data abstraction layer
        data_result = self.test_data_abstraction_layer()
        
        # Test frontend-backend mixer
        mixer_result = self.test_frontend_backend_mixer()
        
        # Test cross-layer integration
        integration_result = self.test_cross_layer_integration()
        
        # Generate summary
        summary = {
            'windows_version': windows_result,
            'data_abstraction': data_result,
            'frontend_backend_mixer': mixer_result,
            'cross_layer_integration': integration_result,
            'overall_status': self._calculate_overall_status(windows_result, data_result, mixer_result, integration_result),
            'test_time': time.time()
        }
        
        self._print_summary(summary)
        self._save_results(summary)
        
        return summary
    
    def test_windows_version_abstraction(self) -> Dict[str, Any]:
        """Test Windows version abstraction layer"""
        print("\nTesting Windows Version Abstraction...")
        
        result = {
            'status': 'unknown',
            'tests_passed': 0,
            'tests_total': 0,
            'details': {}
        }
        
        try:
            # Test Windows version detection
            result['tests_total'] += 1
            layer = get_windows_abstraction_layer()
            if layer:
                result['tests_passed'] += 1
                result['details']['version_detection'] = {
                    'status': 'pass',
                    'version': layer.version.value,
                    'build_number': layer.build_number
                }
                print(f"  ✓ Windows version detected: {layer.version.value} (Build {layer.build_number})")
            else:
                result['details']['version_detection'] = {
                    'status': 'fail',
                    'error': 'Failed to create abstraction layer'
                }
                print(f"  ✗ Failed to detect Windows version")
            
            # Test version-specific functions
            result['tests_total'] += 1
            is_win11 = is_windows_11()
            is_win10 = is_windows_10()
            if is_win11 or is_win10:
                result['tests_passed'] += 1
                result['details']['version_check'] = {
                    'status': 'pass',
                    'is_windows_11': is_win11,
                    'is_windows_10': is_win10
                }
                print(f"  ✓ Version check passed: Win10={is_win10}, Win11={is_win11}")
            else:
                result['details']['version_check'] = {
                    'status': 'fail',
                    'error': 'Version check failed'
                }
                print(f"  ✗ Version check failed")
            
            # Test optimizations
            result['tests_total'] += 1
            optimizations = get_windows_optimizations()
            if optimizations and 'system' in optimizations:
                result['tests_passed'] += 1
                result['details']['optimizations'] = {
                    'status': 'pass',
                    'has_system': 'system' in optimizations,
                    'has_performance': 'performance' in optimizations,
                    'has_network': 'network' in optimizations,
                    'has_gpu': 'gpu' in optimizations
                }
                print(f"  ✓ Optimizations available: {len(optimizations)} categories")
            else:
                result['details']['optimizations'] = {
                    'status': 'fail',
                    'error': 'Failed to get optimizations'
                }
                print(f"  ✗ Failed to get optimizations")
            
            # Test feature detection
            result['tests_total'] += 1
            if hasattr(layer, 'available_features'):
                result['tests_passed'] += 1
                result['details']['features'] = {
                    'status': 'pass',
                    'feature_count': len(layer.available_features)
                }
                print(f"  ✓ Features detected: {len(layer.available_features)} features")
            else:
                result['details']['features'] = {
                    'status': 'fail',
                    'error': 'No features detected'
                }
                print(f"  ✗ Failed to detect features")
            
            result['status'] = 'pass' if result['tests_passed'] >= 3 else 'fail'
            
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            print(f"  ✗ Error in Windows version abstraction test: {e}")
        
        return result
    
    def test_data_abstraction_layer(self) -> Dict[str, Any]:
        """Test data abstraction layer"""
        print("\nTesting Data Abstraction Layer...")
        
        result = {
            'status': 'unknown',
            'tests_passed': 0,
            'tests_total': 0,
            'details': {}
        }
        
        try:
            # Test layer creation
            result['tests_total'] += 1
            data_layer = get_data_abstraction_layer()
            if data_layer:
                result['tests_passed'] += 1
                result['details']['layer_creation'] = {
                    'status': 'pass'
                }
                print(f"  ✓ Data abstraction layer created")
            else:
                result['details']['layer_creation'] = {
                    'status': 'fail',
                    'error': 'Failed to create data layer'
                }
                print(f"  ✗ Failed to create data abstraction layer")
            
            # Test provider status
            result['tests_total'] += 1
            provider_status = data_layer.get_provider_status()
            if provider_status:
                result['tests_passed'] += 1
                result['details']['provider_status'] = {
                    'status': 'pass',
                    'providers': provider_status,
                    'available_count': sum(1 for v in provider_status.values() if v)
                }
                available_count = sum(1 for v in provider_status.values() if v)
                print(f"  ✓ Providers available: {available_count}/{len(provider_status)}")
            else:
                result['details']['provider_status'] = {
                    'status': 'fail',
                    'error': 'Failed to get provider status'
                }
                print(f"  ✗ Failed to get provider status")
            
            # Test data retrieval
            result['tests_total'] += 1
            system_data = data_layer.get_data(DataType.SYSTEM_INFO)
            if system_data and not system_data.error:
                result['tests_passed'] += 1
                result['details']['data_retrieval'] = {
                    'status': 'pass',
                    'data_size': len(str(system_data.data)),
                    'source': system_data.source
                }
                print(f"  ✓ System data retrieved: {len(system_data.data)} fields")
            else:
                result['details']['data_retrieval'] = {
                    'status': 'fail',
                    'error': system_data.error if system_data else 'No data'
                }
                print(f"  ✗ Failed to retrieve system data")
            
            # Test multiple data types
            result['tests_total'] += 1
            cpu_data = data_layer.get_data(DataType.CPU_INFO)
            memory_data = data_layer.get_data(DataType.MEMORY_INFO)
            if cpu_data and memory_data and not cpu_data.error and not memory_data.error:
                result['tests_passed'] += 1
                result['details']['multiple_data'] = {
                    'status': 'pass',
                    'cpu_data_available': True,
                    'memory_data_available': True
                }
                print(f"  ✓ Multiple data types available")
            else:
                result['details']['multiple_data'] = {
                    'status': 'fail',
                    'error': 'Failed to get multiple data types'
                }
                print(f"  ✗ Failed to get multiple data types")
            
            result['status'] = 'pass' if result['tests_passed'] >= 3 else 'fail'
            
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            print(f"  ✗ Error in data abstraction test: {e}")
        
        return result
    
    def test_frontend_backend_mixer(self) -> Dict[str, Any]:
        """Test frontend-backend mixer"""
        print("\nTesting Frontend-Backend Mixer...")
        
        result = {
            'status': 'unknown',
            'tests_passed': 0,
            'tests_total': 0,
            'details': {}
        }
        
        try:
            # Test mixer creation
            result['tests_total'] += 1
            mixer = get_frontend_backend_mixer()
            if mixer:
                result['tests_passed'] += 1
                result['details']['mixer_creation'] = {
                    'status': 'pass'
                }
                print(f"  ✓ Frontend-backend mixer created")
            else:
                result['details']['mixer_creation'] = {
                    'status': 'fail',
                    'error': 'Failed to create mixer'
                }
                print(f"  ✗ Failed to create frontend-backend mixer")
            
            # Test mixer start
            result['tests_total'] += 1
            if mixer.start_mixer():
                result['tests_passed'] += 1
                result['details']['mixer_start'] = {
                    'status': 'pass'
                }
                print(f"  ✓ Mixer started successfully")
            else:
                result['details']['mixer_start'] = {
                    'status': 'fail',
                    'error': 'Failed to start mixer'
                }
                print(f"  ✗ Failed to start mixer")
            
            # Test component creation
            result['tests_total'] += 1
            try:
                frontend = create_tkinter_frontend("test_frontend")
                backend = create_flask_backend("test_backend")
                if frontend and backend:
                    result['tests_passed'] += 1
                    result['details']['component_creation'] = {
                        'status': 'pass',
                        'frontend_created': True,
                        'backend_created': True
                    }
                    print(f"  ✓ Test components created")
                else:
                    result['details']['component_creation'] = {
                        'status': 'fail',
                        'error': 'Failed to create components'
                    }
                    print(f"  ✗ Failed to create test components")
            except Exception as e:
                result['details']['component_creation'] = {
                    'status': 'fail',
                    'error': str(e)
                }
                print(f"  ✗ Error creating components: {e}")
            
            # Test mixer status
            result['tests_total'] += 1
            status = mixer.get_mixer_status()
            if status and status.get('is_running'):
                result['tests_passed'] += 1
                result['details']['mixer_status'] = {
                    'status': 'pass',
                    'is_running': status.get('is_running'),
                    'frontend_count': len(status.get('frontend_components', [])),
                    'backend_count': len(status.get('backend_components', []))
                }
                print(f"  ✓ Mixer status: Running with components")
            else:
                result['details']['mixer_status'] = {
                    'status': 'fail',
                    'error': 'Mixer not running'
                }
                print(f"  ✗ Mixer not running properly")
            
            # Cleanup
            try:
                mixer.stop_mixer()
                print(f"  ✓ Mixer stopped")
            except:
                pass
            
            result['status'] = 'pass' if result['tests_passed'] >= 3 else 'fail'
            
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            print(f"  ✗ Error in mixer test: {e}")
        
        return result
    
    def test_cross_layer_integration(self) -> Dict[str, Any]:
        """Test cross-layer integration"""
        print("\nTesting Cross-Layer Integration...")
        
        result = {
            'status': 'unknown',
            'tests_passed': 0,
            'tests_total': 0,
            'details': {}
        }
        
        try:
            # Test Windows + Data integration
            result['tests_total'] += 1
            windows_layer = get_windows_abstraction_layer()
            data_layer = get_data_abstraction_layer()
            
            if windows_layer and data_layer:
                result['tests_passed'] += 1
                result['details']['layer_integration'] = {
                    'status': 'pass',
                    'windows_available': True,
                    'data_available': True
                }
                print(f"  ✓ Both abstraction layers available")
            else:
                result['details']['layer_integration'] = {
                    'status': 'fail',
                    'error': 'One or more layers unavailable'
                }
                print(f"  ✗ Layer integration failed")
            
            # Test data flow
            result['tests_total'] += 1
            try:
                # Get system data from data layer
                system_data = data_layer.get_data(DataType.SYSTEM_INFO)
                # Get Windows optimizations
                windows_opts = get_windows_optimizations()
                
                if system_data and windows_opts:
                    result['tests_passed'] += 1
                    result['details']['data_flow'] = {
                        'status': 'pass',
                        'system_data_available': True,
                        'windows_opts_available': True
                    }
                    print(f"  ✓ Data flow working between layers")
                else:
                    result['details']['data_flow'] = {
                        'status': 'fail',
                        'error': 'Data flow failed'
                    }
                    print(f"  ✗ Data flow failed")
            except Exception as e:
                result['details']['data_flow'] = {
                    'status': 'fail',
                    'error': str(e)
                }
                print(f"  ✗ Error in data flow: {e}")
            
            # Test version-specific data
            result['tests_total'] += 1
            try:
                # Get CPU data
                cpu_data = data_layer.get_data(DataType.CPU_INFO)
                if cpu_data and not cpu_data.error:
                    # Get Windows-specific optimizations
                    windows_cpu_opts = windows_layer.get_performance_tuning()
                    
                    result['tests_passed'] += 1
                    result['details']['version_specific'] = {
                        'status': 'pass',
                        'cpu_data_available': True,
                        'windows_opts_available': True
                    }
                    print(f"  ✓ Version-specific data available")
                else:
                    result['details']['version_specific'] = {
                        'status': 'fail',
                        'error': 'Version-specific data failed'
                    }
                    print(f"  ✗ Version-specific data failed")
            except Exception as e:
                result['details']['version_specific'] = {
                    'status': 'fail',
                    'error': str(e)
                }
                print(f"  ✗ Error in version-specific test: {e}")
            
            result['status'] = 'pass' if result['tests_passed'] >= 2 else 'fail'
            
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            print(f"  ✗ Error in cross-layer integration test: {e}")
        
        return result
    
    def _calculate_overall_status(self, *results) -> str:
        """Calculate overall test status"""
        passed = sum(1 for r in results if r.get('status') == 'pass')
        total = len(results)
        
        if passed == total:
            return 'excellent'
        elif passed >= total * 0.75:
            return 'good'
        elif passed >= total * 0.5:
            return 'fair'
        else:
            return 'poor'
    
    def _print_summary(self, summary: Dict[str, Any]) -> None:
        """Print test summary"""
        print("\n" + "=" * 60)
        print("INTEGRATION TEST SUMMARY")
        print("=" * 60)
        
        print(f"Overall Status: {summary['overall_status'].upper()}")
        
        for test_name, result in summary.items():
            if test_name in ['windows_version', 'data_abstraction', 'frontend_backend_mixer', 'cross_layer_integration']:
                status = result.get('status', 'unknown')
                passed = result.get('tests_passed', 0)
                total = result.get('tests_total', 0)
                print(f"\n{test_name.replace('_', ' ').title()}:")
                print(f"  Status: {status.upper()}")
                print(f"  Tests: {passed}/{total}")
        
        # Overall assessment
        if summary['overall_status'] == 'excellent':
            print(f"\n🎉 EXCELLENT: All abstraction layers working perfectly!")
        elif summary['overall_status'] == 'good':
            print(f"\n✅ GOOD: Abstraction layers mostly working!")
        elif summary['overall_status'] == 'fair':
            print(f"\n⚠️  FAIR: Abstraction layers need some attention!")
        else:
            print(f"\n❌ POOR: Abstraction layers have significant issues!")
    
    def _save_results(self, summary: Dict[str, Any]) -> None:
        """Save test results"""
        output_file = Path(__file__).parent / "abstraction_layer_test_results.json"
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        print(f"\nDetailed results saved to: {output_file}")

def main():
    """Main entry point"""
    tester = AbstractionLayerTester()
    summary = tester.run_all_tests()
    
    # Return appropriate exit code
    sys.exit(0 if summary['overall_status'] in ['excellent', 'good'] else 1)

if __name__ == "__main__":
    main()
