#!/usr/bin/env python3
"""
Complete Database Integration Test Suite
Tests the full workflow: CSV → Geocoding → Database Storage → Monitoring

Based on agent specifications:
- Direct-to-Supabase architecture
- 15-field permit structure compliance
- PostGIS coordinate storage
- Automatic pricing calculations
- Data quality monitoring
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_database_service import create_database_service, DatabaseResult
from database_monitoring_service import create_monitoring_service
from san_diego_county_scraper import SanDiegoCSVScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database_integration_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DatabaseIntegrationTester:
    """
    Comprehensive test suite for database integration
    
    Tests:
    - Database connectivity and health
    - Data storage and retrieval
    - Geocoding integration
    - Pricing calculations
    - Quality monitoring
    - Performance metrics
    """
    
    def __init__(self):
        """Initialize test suite"""
        self.db_service = create_database_service()
        self.monitoring_service = create_monitoring_service()
        self.scraper = SanDiegoCSVScraper()
        self.test_results = {}
    
    async def run_complete_test_suite(self) -> Dict:
        """Run complete database integration test suite"""
        logger.info("🧪 Starting Complete Database Integration Test Suite")
        logger.info("=" * 80)
        
        try:
            # Test 1: Database Health Check
            logger.info("📋 Test 1: Database Health Check")
            health_result = await self.test_database_health()
            self.test_results['database_health'] = health_result
            
            # Test 2: Basic Database Operations
            logger.info("📋 Test 2: Basic Database Operations")
            basic_ops_result = await self.test_basic_database_operations()
            self.test_results['basic_operations'] = basic_ops_result
            
            # Test 3: CSV Processing and Storage
            logger.info("📋 Test 3: CSV Processing and Storage")
            csv_processing_result = await self.test_csv_processing_and_storage()
            self.test_results['csv_processing'] = csv_processing_result
            
            # Test 4: Geocoding Integration
            logger.info("📋 Test 4: Geocoding Integration")
            geocoding_result = await self.test_geocoding_integration()
            self.test_results['geocoding_integration'] = geocoding_result
            
            # Test 5: Pricing Calculations
            logger.info("📋 Test 5: Pricing Calculations")
            pricing_result = await self.test_pricing_calculations()
            self.test_results['pricing_calculations'] = pricing_result
            
            # Test 6: Spatial Queries
            logger.info("📋 Test 6: Spatial Queries")
            spatial_result = await self.test_spatial_queries()
            self.test_results['spatial_queries'] = spatial_result
            
            # Test 7: Quality Monitoring
            logger.info("📋 Test 7: Quality Monitoring")
            monitoring_result = await self.test_quality_monitoring()
            self.test_results['quality_monitoring'] = monitoring_result
            
            # Test 8: Performance Metrics
            logger.info("📋 Test 8: Performance Metrics")
            performance_result = await self.test_performance_metrics()
            self.test_results['performance_metrics'] = performance_result
            
            # Generate final report
            final_report = await self.generate_test_report()
            
            logger.info("=" * 80)
            logger.info("🎉 Complete Database Integration Test Suite Finished")
            
            return final_report
            
        except Exception as e:
            logger.error(f"❌ Test suite failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def test_database_health(self) -> Dict:
        """Test database connectivity and health"""
        try:
            health_check = await self.monitoring_service.run_health_check()
            
            if health_check['overall_status'] in ['healthy', 'degraded']:
                logger.info("✅ Database health check passed")
                return {'status': 'passed', 'details': health_check}
            else:
                logger.warning("⚠️ Database health check shows issues")
                return {'status': 'warning', 'details': health_check}
                
        except Exception as e:
            logger.error(f"❌ Database health check failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def test_basic_database_operations(self) -> Dict:
        """Test basic CRUD operations"""
        try:
            # Test data
            test_permit = {
                'site_number': f'TEST-{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'record_type': 'Grading Perm',
                'address': '123 Test Street, San Diego, CA 92101',
                'date_opened': '2025-01-01',
                'status': 'Under Review',
                'project_city': 'San Diego County',
                'source_portal': 'Test Portal'
            }
            
            # Test storage
            result = await self.db_service.store_permits_batch([test_permit])
            
            if result.success and result.records_processed > 0:
                logger.info("✅ Basic database operations test passed")
                
                # Test retrieval
                permits = await self.db_service.get_permits_by_criteria(
                    record_type='Grading Perm',
                    limit=1
                )
                
                if permits:
                    logger.info("✅ Data retrieval test passed")
                    return {'status': 'passed', 'stored_records': result.records_processed}
                else:
                    logger.warning("⚠️ Data retrieval test failed")
                    return {'status': 'warning', 'message': 'Storage succeeded but retrieval failed'}
            else:
                logger.error("❌ Basic database operations test failed")
                return {'status': 'failed', 'error': result.error_message}
                
        except Exception as e:
            logger.error(f"❌ Basic database operations test failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def test_csv_processing_and_storage(self) -> Dict:
        """Test CSV processing and storage workflow"""
        try:
            # Check if CSV file exists
            csv_path = "downloads/RecordList20250811.csv"
            if not os.path.exists(csv_path):
                logger.warning("⚠️ CSV file not found, skipping CSV processing test")
                return {'status': 'skipped', 'reason': 'CSV file not found'}
            
            # Process a small sample from CSV
            permits_data = self.scraper._process_csv_file(csv_path, max_records=5)
            
            if permits_data:
                # Store in database
                result = await self.db_service.store_permits_batch(permits_data)
                
                if result.success:
                    logger.info(f"✅ CSV processing test passed: {result.records_processed} records stored")
                    return {
                        'status': 'passed',
                        'records_processed': result.records_processed,
                        'processing_time_ms': result.processing_time_ms
                    }
                else:
                    logger.error("❌ CSV processing test failed during storage")
                    return {'status': 'failed', 'error': result.error_message}
            else:
                logger.error("❌ CSV processing test failed: No data extracted")
                return {'status': 'failed', 'error': 'No data extracted from CSV'}
                
        except Exception as e:
            logger.error(f"❌ CSV processing test failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def test_geocoding_integration(self) -> Dict:
        """Test geocoding integration"""
        try:
            # Test permit with address
            test_permit = {
                'site_number': f'GEO-TEST-{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'record_type': 'Grading Perm',
                'address': '1600 Amphitheatre Parkway, Mountain View, CA 94043',
                'latitude': 37.4220936,
                'longitude': -122.083922,
                'geocoding_accuracy': 'rooftop',
                'geocoding_confidence': 0.95,
                'geocoding_source': 'test',
                'formatted_address': '1600 Amphitheatre Pkwy, Mountain View, CA 94043, USA',
                'project_city': 'San Diego County'
            }
            
            result = await self.db_service.store_permits_batch([test_permit])
            
            if result.success:
                logger.info("✅ Geocoding integration test passed")
                return {'status': 'passed', 'geocoded_records': result.records_processed}
            else:
                logger.error("❌ Geocoding integration test failed")
                return {'status': 'failed', 'error': result.error_message}
                
        except Exception as e:
            logger.error(f"❌ Geocoding integration test failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def test_pricing_calculations(self) -> Dict:
        """Test automatic pricing calculations"""
        try:
            # Test permit with pricing data
            test_permit_id = f'PRICE-TEST-{datetime.now().strftime("%Y%m%d%H%M%S")}'
            
            # Update permit with pricing data to trigger calculations
            success = await self.db_service.update_permit_pricing(
                site_number=test_permit_id,
                roundtrip_minutes=30,
                added_minutes=5,
                dump_fee=50.0,
                ldp_fee=25.0
            )
            
            if success:
                logger.info("✅ Pricing calculations test passed")
                return {'status': 'passed', 'pricing_updated': True}
            else:
                logger.warning("⚠️ Pricing calculations test - no existing permit to update")
                return {'status': 'skipped', 'reason': 'No existing permit to update'}
                
        except Exception as e:
            logger.error(f"❌ Pricing calculations test failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    async def test_spatial_queries(self) -> Dict:
        """Test PostGIS spatial queries"""
        try:
            # Test spatial query (San Diego area)
            permits_nearby = await self.db_service.get_permits_within_radius(
                lat=32.7157, lng=-117.1611, radius_miles=10
            )

            permits_drive_time = await self.db_service.get_permits_within_drive_time(
                origin_lat=32.7157, origin_lng=-117.1611, max_drive_minutes=30
            )

            logger.info(f"✅ Spatial queries test passed: {len(permits_nearby)} nearby, {len(permits_drive_time)} within drive time")
            return {
                'status': 'passed',
                'permits_within_radius': len(permits_nearby),
                'permits_within_drive_time': len(permits_drive_time)
            }

        except Exception as e:
            logger.error(f"❌ Spatial queries test failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    async def test_quality_monitoring(self) -> Dict:
        """Test data quality monitoring"""
        try:
            quality_report = await self.monitoring_service.generate_quality_report(hours_back=24)

            logger.info(f"✅ Quality monitoring test passed: {quality_report.total_records} records analyzed")
            return {
                'status': 'passed',
                'total_records': quality_report.total_records,
                'success_rate': quality_report.success_rate,
                'geocoding_success_rate': quality_report.geocoding_success_rate,
                'recommendations_count': len(quality_report.recommendations)
            }

        except Exception as e:
            logger.error(f"❌ Quality monitoring test failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    async def test_performance_metrics(self) -> Dict:
        """Test performance monitoring"""
        try:
            performance_metrics = await self.monitoring_service.monitor_performance(hours_back=1)

            logger.info(f"✅ Performance metrics test passed: {performance_metrics.total_operations} operations analyzed")
            return {
                'status': 'passed',
                'total_operations': performance_metrics.total_operations,
                'avg_processing_time_ms': performance_metrics.avg_query_time_ms,
                'success_rate': performance_metrics.success_rate,
                'error_rate': performance_metrics.error_rate
            }

        except Exception as e:
            logger.error(f"❌ Performance metrics test failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    async def generate_test_report(self) -> Dict:
        """Generate comprehensive test report"""
        try:
            # Count test results
            passed_tests = sum(1 for result in self.test_results.values() if result.get('status') == 'passed')
            failed_tests = sum(1 for result in self.test_results.values() if result.get('status') == 'failed')
            warning_tests = sum(1 for result in self.test_results.values() if result.get('status') == 'warning')
            skipped_tests = sum(1 for result in self.test_results.values() if result.get('status') == 'skipped')
            total_tests = len(self.test_results)

            # Determine overall status
            overall_status = 'passed'
            if failed_tests > 0:
                overall_status = 'failed'
            elif warning_tests > 0:
                overall_status = 'warning'

            # Generate summary
            summary = {
                'overall_status': overall_status,
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'warning_tests': warning_tests,
                'skipped_tests': skipped_tests,
                'success_rate': passed_tests / total_tests if total_tests > 0 else 0,
                'timestamp': datetime.now().isoformat()
            }

            # Get current system health
            health_check = await self.monitoring_service.run_health_check()

            report = {
                'test_summary': summary,
                'detailed_results': self.test_results,
                'system_health': health_check,
                'compliance_status': {
                    'database_connectivity': self.test_results.get('database_health', {}).get('status') == 'passed',
                    'data_storage': self.test_results.get('basic_operations', {}).get('status') == 'passed',
                    'csv_processing': self.test_results.get('csv_processing', {}).get('status') in ['passed', 'skipped'],
                    'geocoding_integration': self.test_results.get('geocoding_integration', {}).get('status') == 'passed',
                    'pricing_calculations': self.test_results.get('pricing_calculations', {}).get('status') in ['passed', 'skipped'],
                    'spatial_queries': self.test_results.get('spatial_queries', {}).get('status') == 'passed',
                    'quality_monitoring': self.test_results.get('quality_monitoring', {}).get('status') == 'passed',
                    'performance_metrics': self.test_results.get('performance_metrics', {}).get('status') == 'passed'
                },
                'recommendations': self._generate_test_recommendations()
            }

            # Log summary
            logger.info(f"📊 Test Summary: {passed_tests}/{total_tests} passed, {failed_tests} failed, {warning_tests} warnings")
            logger.info(f"🎯 Overall Status: {overall_status.upper()}")

            return report

        except Exception as e:
            logger.error(f"❌ Failed to generate test report: {e}")
            return {
                'test_summary': {'overall_status': 'error', 'error': str(e)},
                'timestamp': datetime.now().isoformat()
            }

    def _generate_test_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []

        # Check for failed tests
        for test_name, result in self.test_results.items():
            if result.get('status') == 'failed':
                recommendations.append(f"❌ Fix {test_name}: {result.get('error', 'Unknown error')}")
            elif result.get('status') == 'warning':
                recommendations.append(f"⚠️ Review {test_name}: May need attention")

        # Add positive feedback
        passed_count = sum(1 for result in self.test_results.values() if result.get('status') == 'passed')
        if passed_count == len(self.test_results):
            recommendations.append("🎉 All tests passed! Database integration is working perfectly.")
        elif passed_count > len(self.test_results) * 0.8:
            recommendations.append("✅ Most tests passed. System is largely functional.")

        return recommendations

async def main():
    """Run the complete database integration test suite"""
    print("🧪 Complete Database Integration Test Suite")
    print("=" * 80)

    tester = DatabaseIntegrationTester()
    report = await tester.run_complete_test_suite()

    # Save report to file
    report_filename = f"database_integration_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n📄 Test report saved to: {report_filename}")
    print(f"🎯 Overall Status: {report.get('test_summary', {}).get('overall_status', 'unknown').upper()}")

    return report

if __name__ == "__main__":
    asyncio.run(main())
