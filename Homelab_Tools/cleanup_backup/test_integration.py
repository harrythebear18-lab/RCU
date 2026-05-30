#!/usr/bin/env python3
"""
Integration Test for Core Services
Tests all core services work together properly
"""

import sys
import os
from pathlib import Path

# Add Core Services to path
sys.path.insert(0, str(Path(__file__).parent / "Core Services"))

def test_event_bus():
    """Test Event Bus functionality"""
    try:
        from event_bus import get_event_bus, EventType
        bus = get_event_bus()
        event_id = bus.publish_sync(EventType.SYSTEM, 'test', {'test': True})
        print(f'Event Bus test: {event_id}')
        return True
    except Exception as e:
        print(f'Event Bus test failed: {e}')
        return False

def test_config_manager():
    """Test Configuration Manager"""
    try:
        from config_manager import get_config_manager
        cm = get_config_manager()
        cm.set('test.value', 42, 'test', 'Test configuration')
        value = cm.get('test.value')
        print(f'Config Manager test: {value}')
        return value == 42
    except Exception as e:
        print(f'Config Manager test failed: {e}')
        return False

def test_auth_service():
    """Test Authentication Service"""
    try:
        from auth_service import get_auth_service
        auth = get_auth_service()
        session_id = auth.authenticate('admin', 'admin123', '127.0.0.1', 'test')
        result = session_id[:16] if session_id else "Failed"
        print(f'Auth Service test: {result}')
        return session_id is not None
    except Exception as e:
        print(f'Auth Service test failed: {e}')
        return False

def test_data_persistence():
    """Test Data Persistence"""
    try:
        from data_persistence import get_data_persistence
        dp = get_data_persistence()
        success = dp.store_metric('test', 'cpu_usage', 75.5, 'percent')
        print(f'Data Persistence test: {success}')
        return success
    except Exception as e:
        print(f'Data Persistence test failed: {e}')
        return False

def test_unified_monitoring():
    """Test Unified Monitoring"""
    try:
        from unified_monitoring import get_unified_monitoring, AlertSeverity
        um = get_unified_monitoring()
        alert_id = um.create_alert('Test Alert', 'This is a test alert', AlertSeverity.INFO, 'test')
        print(f'Unified Monitoring test: {alert_id}')
        return alert_id is not None
    except Exception as e:
        print(f'Unified Monitoring test failed: {e}')
        return False

def main():
    """Run all integration tests"""
    print("Core Services Integration Tests")
    print("=" * 40)
    
    tests = [
        ("Event Bus", test_event_bus),
        ("Configuration Manager", test_config_manager),
        ("Authentication Service", test_auth_service),
        ("Data Persistence", test_data_persistence),
        ("Unified Monitoring", test_unified_monitoring)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nTesting {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 40)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All core services integration tests passed!")
        return True
    else:
        print("❌ Some tests failed. Check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
