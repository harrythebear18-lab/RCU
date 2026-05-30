#!/usr/bin/env python3
"""
Phase 2 Data Layer Integration Test
Verifies database integration, historical data storage, and unified monitoring
"""

import sys
import os
import asyncio
import time
from pathlib import Path
from datetime import datetime, timedelta

# Add Core Services to path
sys.path.insert(0, str(Path(__file__).parent / "Core Services"))

from data_persistence import get_data_persistence, MetricData
from unified_monitoring import get_unified_monitoring, AlertSeverity, AlertStatus
from config_manager import get_config_manager
from event_bus import get_event_bus, EventType

class Phase2IntegrationTest:
    """Comprehensive Phase 2 integration testing"""
    
    def __init__(self):
        self.test_results = []
        self.data_persistence = None
        self.unified_monitoring = None
        self.config_manager = None
        self.event_bus = None
        
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "PASS" if passed else "FAIL"
        self.test_results.append((test_name, passed, message))
        print(f"[{status}] {test_name}: {message}")
    
    async def test_database_integration(self):
        """Test database integration and schema management"""
        try:
            # Initialize data persistence
            self.data_persistence = get_data_persistence()
            
            # Test database connection
            stats = self.data_persistence.get_database_stats()
            assert stats is not None
            assert 'database_path' in stats
            
            # Test schema creation
            assert self.data_persistence.initialize_database()
            
            # Test table creation
            tables = self.data_persistence.get_table_info()
            expected_tables = ['metrics', 'events', 'alerts', 'system_state']
            for table in expected_tables:
                assert table in tables, f"Missing table: {table}"
            
            self.log_test("Database Integration", True, f"Database initialized with {len(tables)} tables")
            
        except Exception as e:
            self.log_test("Database Integration", False, str(e))
    
    async def test_historical_data_storage(self):
        """Test historical data storage and retrieval"""
        try:
            # Test metrics storage
            metric_data = MetricData(
                timestamp=datetime.now(),
                source="test_system",
                metric_type="cpu_usage",
                value=75.5,
                unit="percent",
                tags={"host": "test-host"},
                metadata={"test": True}
            )
            
            # Store metric
            success = self.data_persistence.store_metric(
                source="test_system",
                metric_type="cpu_usage", 
                value=75.5,
                unit="percent",
                tags={"host": "test-host"},
                metadata={"test": True}
            )
            assert success
            
            # Store multiple metrics for testing
            for i in range(10):
                await asyncio.sleep(0.01)  # Small delay for different timestamps
                self.data_persistence.store_metric(
                    source="test_system",
                    metric_type="memory_usage",
                    value=50.0 + i,
                    unit="percent",
                    tags={"host": f"test-host-{i}"}
                )
            
            # Test metric retrieval
            metrics = self.data_persistence.get_metrics(
                source="test_system",
                metric_type="cpu_usage",
                limit=10
            )
            assert len(metrics) > 0
            
            # Test time-based queries
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=5)
            recent_metrics = self.data_persistence.get_metrics(
                start_time=start_time,
                end_time=end_time
            )
            assert len(recent_metrics) > 0
            
            # Test data retention
            old_count = len(recent_metrics)
            self.data_persistence.cleanup_old_data(days=0)  # Should remove everything
            cleaned_metrics = self.data_persistence.get_metrics()
            assert len(cleaned_metrics) < old_count
            
            self.log_test("Historical Data Storage", True, f"Stored and retrieved {len(metrics)} metrics")
            
        except Exception as e:
            self.log_test("Historical Data Storage", False, str(e))
    
    async def test_unified_monitoring(self):
        """Test unified monitoring and alerting system"""
        try:
            # Initialize unified monitoring
            self.unified_monitoring = get_unified_monitoring()
            
            # Test alert creation
            alert_id = self.unified_monitoring.create_alert(
                title="Test Alert",
                message="This is a test alert for Phase 2 integration",
                severity=AlertSeverity.INFO,
                source="integration_test"
            )
            assert alert_id is not None
            
            # Test alert retrieval
            alerts = self.unified_monitoring.get_active_alerts()
            assert len(alerts) > 0
            
            # Test alert acknowledgment
            success = self.unified_monitoring.acknowledge_alert(alert_id, "test_user")
            assert success
            
            # Test alert resolution
            success = self.unified_monitoring.resolve_alert(alert_id, "test_user", "Test resolution")
            assert success
            
            # Test threshold monitoring
            self.unified_monitoring.set_threshold(
                metric_type="cpu_usage",
                threshold=80.0,
                operator="greater_than",
                severity=AlertSeverity.WARNING
            )
            
            # Trigger threshold check
            self.unified_monitoring.check_thresholds("test_system", {
                "cpu_usage": 85.0
            })
            
            # Check if alert was created
            threshold_alerts = self.unified_monitoring.get_alerts(
                severity=AlertSeverity.WARNING,
                status=AlertStatus.ACTIVE
            )
            
            # Test monitoring statistics
            stats = self.unified_monitoring.get_monitoring_stats()
            assert 'total_alerts' in stats
            assert 'active_alerts' in stats
            
            self.log_test("Unified Monitoring", True, f"Created {len(alerts)} alerts, stats: {stats}")
            
        except Exception as e:
            self.log_test("Unified Monitoring", False, str(e))
    
    async def test_cross_system_correlation(self):
        """Test cross-system data correlation"""
        try:
            # Store correlated data from multiple systems
            systems = ["system1", "system2", "system3"]
            
            for system in systems:
                # Store metrics
                self.data_persistence.store_metric(
                    source=system,
                    metric_type="cpu_usage",
                    value=70.0 + systems.index(system) * 5,
                    unit="percent",
                    tags={"environment": "test"}
                )
                
                self.data_persistence.store_metric(
                    source=system,
                    metric_type="memory_usage",
                    value=60.0 + systems.index(system) * 3,
                    unit="percent",
                    tags={"environment": "test"}
                )
                
                # Store events
                self.data_persistence.store_event(
                    event_type="system_check",
                    source=system,
                    data={"status": "healthy", "check_time": datetime.now().isoformat()}
                )
            
            # Test correlated queries
            correlated_metrics = self.data_persistence.get_correlated_metrics(
                metric_types=["cpu_usage", "memory_usage"],
                tags={"environment": "test"}
            )
            assert len(correlated_metrics) > 0
            
            # Test system aggregation
            system_stats = self.data_persistence.get_system_statistics(
                systems=systems,
                metric_types=["cpu_usage", "memory_usage"]
            )
            assert len(system_stats) > 0
            
            # Test time-series aggregation
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=1)
            time_series = self.data_persistence.get_time_series(
                metric_type="cpu_usage",
                start_time=start_time,
                end_time=end_time,
                aggregation="avg"
            )
            assert len(time_series) > 0
            
            self.log_test("Cross-System Correlation", True, f"Correlated {len(correlated_metrics)} data points")
            
        except Exception as e:
            self.log_test("Cross-System Correlation", False, str(e))
    
    async def test_data_retention_and_cleanup(self):
        """Test data retention policies and cleanup"""
        try:
            # Store test data with different timestamps
            base_time = datetime.now()
            
            # Store recent data (should be kept)
            for i in range(5):
                self.data_persistence.store_metric(
                    source="retention_test",
                    metric_type="test_metric",
                    value=i,
                    unit="count",
                    tags={"retention": "recent"}
                )
            
            # Store old data (should be cleaned up)
            old_time = base_time - timedelta(days=10)
            for i in range(5):
                self.data_persistence.store_metric(
                    source="retention_test", 
                    metric_type="test_metric",
                    value=i + 10,
                    unit="count",
                    tags={"retention": "old"},
                    timestamp=old_time + timedelta(minutes=i)
                )
            
            # Check data before cleanup
            all_metrics = self.data_persistence.get_metrics(source="retention_test")
            before_count = len(all_metrics)
            
            # Run cleanup with 7-day retention
            self.data_persistence.cleanup_old_data(days=7)
            
            # Check data after cleanup
            remaining_metrics = self.data_persistence.get_metrics(source="retention_test")
            after_count = len(remaining_metrics)
            
            # Should have removed old data
            assert after_count < before_count
            assert after_count == 5  # Only recent data should remain
            
            # Test archive functionality
            archive_path = self.data_persistence.archive_data(days=1)
            assert archive_path is not None
            assert Path(archive_path).exists()
            
            self.log_test("Data Retention & Cleanup", True, f"Cleaned {before_count - after_count} old records")
            
        except Exception as e:
            self.log_test("Data Retention & Cleanup", False, str(e))
    
    async def test_performance_and_scalability(self):
        """Test performance and scalability of data layer"""
        try:
            # Performance test: bulk insert
            start_time = time.time()
            
            bulk_metrics = []
            for i in range(1000):
                bulk_metrics.append({
                    'source': f'perf_test_{i % 10}',
                    'metric_type': 'cpu_usage',
                    'value': 50.0 + (i % 50),
                    'unit': 'percent',
                    'tags': {'batch': 'performance_test'}
                })
            
            # Bulk insert
            success = self.data_persistence.store_bulk_metrics(bulk_metrics)
            assert success
            
            bulk_insert_time = time.time() - start_time
            
            # Performance test: query
            start_time = time.time()
            
            queried_metrics = self.data_persistence.get_metrics(
                tags={'batch': 'performance_test'},
                limit=1000
            )
            
            query_time = time.time() - start_time
            
            # Performance assertions
            assert bulk_insert_time < 5.0, f"Bulk insert too slow: {bulk_insert_time}s"
            assert query_time < 1.0, f"Query too slow: {query_time}s"
            assert len(queried_metrics) >= 1000
            
            # Test database size and optimization
            stats = self.data_persistence.get_database_stats()
            assert 'database_size' in stats
            
            # Run optimization
            optimization_result = self.data_persistence.optimize_database()
            assert optimization_result
            
            self.log_test("Performance & Scalability", True, 
                         f"Bulk insert: {bulk_insert_time:.2f}s, Query: {query_time:.2f}s, Records: {len(queried_metrics)}")
            
        except Exception as e:
            self.log_test("Performance & Scalability", False, str(e))
    
    async def run_all_tests(self):
        """Run all Phase 2 integration tests"""
        print("Phase 2 Data Layer Integration Tests")
        print("=" * 50)
        
        tests = [
            self.test_database_integration,
            self.test_historical_data_storage,
            self.test_unified_monitoring,
            self.test_cross_system_correlation,
            self.test_data_retention_and_cleanup,
            self.test_performance_and_scalability
        ]
        
        for test in tests:
            try:
                await test()
            except Exception as e:
                self.log_test(test.__name__, False, f"Test crashed: {e}")
        
        # Cleanup
        if self.data_persistence:
            self.data_persistence.close()
        
        # Print results
        print("\n" + "=" * 50)
        print("PHASE 2 INTEGRATION TEST RESULTS")
        print("=" * 50)
        
        passed = sum(1 for _, p, _ in self.test_results if p)
        total = len(self.test_results)
        
        for test_name, passed, message in self.test_results:
            status = "PASS" if passed else "FAIL"
            print(f"[{status}] {test_name}: {message}")
        
        print(f"\nSummary: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 Phase 2 integration completed successfully!")
            print("✅ Database integration working")
            print("✅ Historical data storage functional") 
            print("✅ Unified monitoring operational")
            print("✅ Cross-system correlation enabled")
            print("✅ Data retention policies active")
            print("✅ Performance acceptable")
        else:
            print("❌ Some Phase 2 components need attention.")
        
        return passed == total

async def main():
    """Main test runner"""
    tester = Phase2IntegrationTest()
    success = await tester.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
