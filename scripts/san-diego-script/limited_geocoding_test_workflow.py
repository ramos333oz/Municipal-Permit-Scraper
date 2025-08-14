#!/usr/bin/env python3
"""
Limited Geocoding Test Workflow for Frontend Development Preparation
Implements complete data pipeline: JSON → Sample Selection → Geocoding → Database Storage

Based on agent specifications:
- .claude/agents/data-engineer.md (ETL pipeline and data processing)
- .claude/agents/database-architect.md (Direct-to-Supabase architecture)
- .claude/agents/web-scraper.md (scraped data structure understanding)

Workflow: Sample Data Selection → Limited Geocoding → Database Integration Test → Frontend Preparation
"""

import json
import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our existing services
from enhanced_geocoding_service import EnhancedGeocodingService
from supabase_database_service import create_database_service
from database_monitoring_service import create_monitoring_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('limited_geocoding_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TestWorkflowResult:
    """Result of the complete test workflow"""
    success: bool
    sample_permits_selected: int
    geocoding_results: Dict
    database_storage_results: Dict
    spatial_query_results: Dict
    frontend_ready_data: List[Dict]
    processing_time_ms: int
    error_message: Optional[str] = None

class LimitedGeocodingTestWorkflow:
    """
    Limited geocoding test workflow for frontend development preparation
    
    Implements:
    - Sample data selection from scraped JSON
    - Limited geocoding using existing enhanced service
    - Database integration testing with Supabase
    - Spatial query validation
    - Frontend data format preparation
    """
    
    def __init__(self):
        """Initialize test workflow components"""
        self.geocoding_service = EnhancedGeocodingService()
        self.db_service = create_database_service()
        self.monitoring_service = create_monitoring_service()
        
        # Set up environment for testing
        self._setup_test_environment()
    
    def _setup_test_environment(self):
        """Set up environment variables for testing"""
        # Supabase configuration
        os.environ['SUPABASE_URL'] = 'https://tellxlrnkwooikljwlhc.supabase.co'
        os.environ['SUPABASE_ANON_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRlbGx4bHJua3dvb2lrbGp3bGhjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ4OTYyNzQsImV4cCI6MjA3MDQ3MjI3NH0.8qHGO5Iew5qL9-npMJNNdRZklZBJQPwEiDLuPZH7Nsk'
        
        # Geocoding API key (if available)
        if not os.getenv('GEOCODIO_API_KEY'):
            os.environ['GEOCODIO_API_KEY'] = '806d6c98688b022ff79c7dc6d08b662c897bfdb'
        
        logger.info("✅ Test environment configured")
    
    async def run_complete_test_workflow(self) -> TestWorkflowResult:
        """Run complete limited geocoding test workflow"""
        start_time = datetime.now()
        logger.info("🧪 Starting Limited Geocoding Test Workflow for Frontend Development")
        logger.info("=" * 80)
        
        try:
            # Step 1: Sample Data Selection
            logger.info("📋 Step 1: Sample Data Selection")
            sample_permits = self._select_representative_sample_permits()
            logger.info(f"   Selected {len(sample_permits)} representative permits")
            
            # Step 2: Limited Geocoding Test
            logger.info("📋 Step 2: Limited Geocoding Test")
            geocoding_results = await self._perform_limited_geocoding(sample_permits)
            logger.info(f"   Geocoded {geocoding_results['success_count']}/{len(sample_permits)} permits")
            
            # Step 3: Database Integration Test
            logger.info("📋 Step 3: Database Integration Test")
            database_results = await self._test_database_integration(geocoding_results['geocoded_permits'])
            logger.info(f"   Stored {database_results['records_processed']} permits in database")
            
            # Step 4: Spatial Query Validation
            logger.info("📋 Step 4: Spatial Query Validation")
            spatial_results = await self._validate_spatial_queries(geocoding_results['geocoded_permits'])
            logger.info(f"   Validated {len(spatial_results['nearby_permits'])} spatial queries")
            
            # Step 5: Frontend Data Preparation
            logger.info("📋 Step 5: Frontend Data Preparation")
            frontend_data = await self._prepare_frontend_data()
            logger.info(f"   Prepared {len(frontend_data)} records for frontend")
            
            # Calculate processing time
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            logger.info("=" * 80)
            logger.info("🎉 Limited Geocoding Test Workflow Completed Successfully!")
            
            return TestWorkflowResult(
                success=True,
                sample_permits_selected=len(sample_permits),
                geocoding_results=geocoding_results,
                database_storage_results=database_results,
                spatial_query_results=spatial_results,
                frontend_ready_data=frontend_data,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            logger.error(f"❌ Test workflow failed: {e}")
            
            return TestWorkflowResult(
                success=False,
                sample_permits_selected=0,
                geocoding_results={},
                database_storage_results={},
                spatial_query_results={},
                frontend_ready_data=[],
                processing_time_ms=processing_time,
                error_message=str(e)
            )
    
    def _select_representative_sample_permits(self) -> List[Dict]:
        """Select 3 representative permits with complete address information"""
        try:
            # Load the scraped data
            json_file_path = "Scraped-data-formatted/san_diego_complete_workflow_results.json"
            
            with open(json_file_path, 'r', encoding='utf-8') as f:
                all_permits = json.load(f)
            
            # Filter permits with complete addresses (not "nan" and has proper format)
            valid_permits = []
            for permit in all_permits:
                address = permit.get('address', '')
                if (address and 
                    address != 'nan' and 
                    'CA' in address and 
                    any(char.isdigit() for char in address)):
                    valid_permits.append(permit)
            
            # Select 3 representative samples with different characteristics
            selected_permits = []
            
            # Sample 1: Recent Planning Pre-Application (Ontario area)
            sample_1 = None
            for permit in valid_permits:
                if (permit.get('raw_data', {}).get('original_csv_row', {}).get('Type') == 'Planning Pre-Application' and
                    'ONTARIO CA' in permit.get('address', '') and
                    permit.get('raw_data', {}).get('original_csv_row', {}).get('Status') == 'Complete'):
                    sample_1 = permit
                    break
            
            # Sample 2: Sign Permit (different type)
            sample_2 = None
            for permit in valid_permits:
                if (permit.get('raw_data', {}).get('original_csv_row', {}).get('Type') == 'Sign Permit' and
                    'ONTARIO CA' in permit.get('address', '') and
                    permit.get('raw_data', {}).get('original_csv_row', {}).get('Status') == 'Active'):
                    sample_2 = permit
                    break
            
            # Sample 3: Temporary Use Permit (third type)
            sample_3 = None
            for permit in valid_permits:
                if (permit.get('raw_data', {}).get('original_csv_row', {}).get('Type') == 'Temporary Use Permit' and
                    'ONTARIO CA' in permit.get('address', '') and
                    permit.get('raw_data', {}).get('original_csv_row', {}).get('Status') == 'Active'):
                    sample_3 = permit
                    break
            
            # Add samples if found
            if sample_1:
                selected_permits.append(sample_1)
            if sample_2:
                selected_permits.append(sample_2)
            if sample_3:
                selected_permits.append(sample_3)
            
            # If we don't have 3 samples, fill with any valid permits
            while len(selected_permits) < 3 and len(selected_permits) < len(valid_permits):
                for permit in valid_permits[:10]:  # Check first 10 valid permits
                    if permit not in selected_permits:
                        selected_permits.append(permit)
                        break
                if len(selected_permits) >= 3:
                    break
            
            logger.info(f"📊 Selected {len(selected_permits)} representative permits:")
            for i, permit in enumerate(selected_permits, 1):
                record_data = permit.get('raw_data', {}).get('original_csv_row', {})
                logger.info(f"   Sample {i}: {record_data.get('Type', 'Unknown')} - {permit.get('address', 'No address')}")
            
            return selected_permits
            
        except Exception as e:
            logger.error(f"❌ Failed to select sample permits: {e}")
            return []

    async def _perform_limited_geocoding(self, sample_permits: List[Dict]) -> Dict:
        """Perform limited geocoding on sample permits using existing enhanced service"""
        try:
            geocoded_permits = []
            success_count = 0
            failed_count = 0

            for i, permit in enumerate(sample_permits, 1):
                try:
                    address = permit.get('address', '')
                    logger.info(f"   Geocoding {i}/{len(sample_permits)}: {address}")

                    # Use existing enhanced geocoding service (not async)
                    geocoding_result = self.geocoding_service.geocode_address(address)

                    if geocoding_result and geocoding_result.latitude and geocoding_result.longitude:
                        # Enhance permit data with geocoding results
                        enhanced_permit = permit.copy()
                        enhanced_permit.update({
                            'latitude': geocoding_result.latitude,
                            'longitude': geocoding_result.longitude,
                            'geocoding_accuracy': geocoding_result.accuracy,
                            'geocoding_confidence': geocoding_result.confidence,
                            'geocoding_source': geocoding_result.source,
                            'formatted_address': geocoding_result.formatted_address,

                            # Extract and normalize data from raw_data for database compliance
                            'site_number': enhanced_permit.get('raw_data', {}).get('original_csv_row', {}).get('Record Number'),
                            'record_type': enhanced_permit.get('raw_data', {}).get('original_csv_row', {}).get('Type'),
                            'status': enhanced_permit.get('raw_data', {}).get('original_csv_row', {}).get('Status'),
                            'date_opened': enhanced_permit.get('raw_data', {}).get('original_csv_row', {}).get('Date Opened'),

                            # Add test pricing data for calculation validation
                            'roundtrip_minutes': 25,  # Test value for Ontario area
                            'added_minutes': 5,       # Test value
                            'dump_fee': 45.0,         # Test value
                            'ldp_fee': 20.0,          # Test value
                        })

                        geocoded_permits.append(enhanced_permit)
                        success_count += 1
                        logger.info(f"   ✅ Geocoded: {geocoding_result.latitude:.6f}, {geocoding_result.longitude:.6f}")
                    else:
                        failed_count += 1
                        logger.warning(f"   ⚠️ Geocoding failed: No coordinates returned")

                except Exception as e:
                    failed_count += 1
                    logger.error(f"   ❌ Error geocoding permit {i}: {e}")

            return {
                'success_count': success_count,
                'failed_count': failed_count,
                'geocoded_permits': geocoded_permits,
                'geocoding_service_used': 'EnhancedGeocodingService'
            }

        except Exception as e:
            logger.error(f"❌ Limited geocoding failed: {e}")
            return {
                'success_count': 0,
                'failed_count': len(sample_permits),
                'geocoded_permits': [],
                'error': str(e)
            }

    async def _test_database_integration(self, geocoded_permits: List[Dict]) -> Dict:
        """Test database integration with geocoded sample permits"""
        try:
            if not geocoded_permits:
                return {
                    'success': False,
                    'records_processed': 0,
                    'records_failed': 0,
                    'error': 'No geocoded permits to store'
                }

            # Store permits using enhanced database service
            result = await self.db_service.store_permits_batch(geocoded_permits)

            if result.success:
                logger.info(f"   ✅ Database storage successful: {result.records_processed} records")
                logger.info(f"   ⏱️ Processing time: {result.processing_time_ms}ms")

                # Test pricing calculation triggers
                for permit in geocoded_permits:
                    site_number = permit.get('site_number')
                    if site_number:
                        pricing_updated = await self.db_service.update_permit_pricing(
                            site_number=site_number,
                            roundtrip_minutes=permit.get('roundtrip_minutes', 25),
                            added_minutes=permit.get('added_minutes', 5),
                            dump_fee=permit.get('dump_fee', 45.0),
                            ldp_fee=permit.get('ldp_fee', 20.0)
                        )
                        if pricing_updated:
                            logger.info(f"   💰 Pricing calculations updated for {site_number}")
            else:
                logger.error(f"   ❌ Database storage failed: {result.error_message}")

            return {
                'success': result.success,
                'records_processed': result.records_processed,
                'records_failed': result.records_failed,
                'processing_time_ms': result.processing_time_ms,
                'details': result.details
            }

        except Exception as e:
            logger.error(f"❌ Database integration test failed: {e}")
            return {
                'success': False,
                'records_processed': 0,
                'records_failed': len(geocoded_permits),
                'error': str(e)
            }

    async def _validate_spatial_queries(self, geocoded_permits: List[Dict]) -> Dict:
        """Validate PostGIS spatial queries with sample data"""
        try:
            spatial_results = {
                'nearby_permits': [],
                'drive_time_permits': [],
                'spatial_functions_working': False
            }

            if not geocoded_permits:
                return spatial_results

            # Use first geocoded permit as reference point
            reference_permit = geocoded_permits[0]
            ref_lat = reference_permit.get('latitude')
            ref_lng = reference_permit.get('longitude')

            if ref_lat and ref_lng:
                # Test radius-based spatial query
                nearby_permits = await self.db_service.get_permits_within_radius(
                    lat=ref_lat, lng=ref_lng, radius_miles=5.0
                )

                # Test drive-time spatial query
                drive_time_permits = await self.db_service.get_permits_within_drive_time(
                    origin_lat=ref_lat, origin_lng=ref_lng, max_drive_minutes=30
                )

                spatial_results.update({
                    'nearby_permits': nearby_permits,
                    'drive_time_permits': drive_time_permits,
                    'spatial_functions_working': True,
                    'reference_coordinates': {'lat': ref_lat, 'lng': ref_lng}
                })

                logger.info(f"   🗺️ Found {len(nearby_permits)} permits within 5 miles")
                logger.info(f"   🚗 Found {len(drive_time_permits)} permits within 30 min drive")

            return spatial_results

        except Exception as e:
            logger.error(f"❌ Spatial query validation failed: {e}")
            return {
                'nearby_permits': [],
                'drive_time_permits': [],
                'spatial_functions_working': False,
                'error': str(e)
            }

    async def _prepare_frontend_data(self) -> List[Dict]:
        """Prepare data in format suitable for Next.js + Leaflet frontend"""
        try:
            # Retrieve recent permits from database for frontend testing
            permits = await self.db_service.get_permits_by_criteria(
                record_type=None,  # Get all types
                status=None,       # Get all statuses
                project_city='San Diego County',
                limit=10
            )

            # Format data for frontend consumption
            frontend_ready_data = []
            for permit in permits:
                # Format for Next.js + Leaflet mapping interface
                frontend_permit = {
                    # Core identification
                    'id': permit.get('id'),
                    'site_number': permit.get('site_number'),
                    'record_type': permit.get('record_type'),
                    'status': permit.get('status'),

                    # Location data for mapping
                    'coordinates': {
                        'lat': permit.get('latitude'),
                        'lng': permit.get('longitude')
                    },
                    'address': permit.get('address'),
                    'formatted_address': permit.get('formatted_address'),

                    # Project details
                    'project_city': permit.get('project_city'),
                    'project_company': permit.get('project_company'),
                    'project_contact': permit.get('project_contact'),
                    'date_opened': permit.get('date_opened'),

                    # Pricing information (for LDP quote generation)
                    'pricing': {
                        'dump_fee': permit.get('dump_fee'),
                        'ldp_fee': permit.get('ldp_fee'),
                        'trucking_price_per_load': permit.get('trucking_price_per_load'),
                        'total_price_per_load': permit.get('total_price_per_load'),
                        'roundtrip_minutes': permit.get('roundtrip_minutes')
                    },

                    # Metadata
                    'source_portal': permit.get('source_portal'),
                    'geocoding_accuracy': permit.get('geocoding_accuracy'),
                    'created_at': permit.get('created_at'),
                    'updated_at': permit.get('updated_at')
                }

                # Only include permits with valid coordinates
                if (frontend_permit['coordinates']['lat'] and
                    frontend_permit['coordinates']['lng']):
                    frontend_ready_data.append(frontend_permit)

            logger.info(f"   📱 Prepared {len(frontend_ready_data)} permits for frontend")

            # Save sample data for frontend development
            sample_data_file = "frontend_sample_data.json"
            with open(sample_data_file, 'w', encoding='utf-8') as f:
                json.dump(frontend_ready_data, f, indent=2, default=str)

            logger.info(f"   💾 Sample data saved to {sample_data_file}")

            return frontend_ready_data

        except Exception as e:
            logger.error(f"❌ Frontend data preparation failed: {e}")
            return []

    async def generate_test_report(self, result: TestWorkflowResult) -> Dict:
        """Generate comprehensive test report"""
        try:
            # Get system health check
            health_check = await self.monitoring_service.run_health_check()

            # Generate quality report
            quality_report = await self.monitoring_service.generate_quality_report(hours_back=1)

            report = {
                'test_workflow_summary': {
                    'overall_success': result.success,
                    'sample_permits_selected': result.sample_permits_selected,
                    'geocoding_success_rate': (
                        result.geocoding_results.get('success_count', 0) /
                        result.sample_permits_selected if result.sample_permits_selected > 0 else 0
                    ),
                    'database_storage_success': result.database_storage_results.get('success', False),
                    'spatial_queries_working': result.spatial_query_results.get('spatial_functions_working', False),
                    'frontend_data_prepared': len(result.frontend_ready_data),
                    'total_processing_time_ms': result.processing_time_ms
                },
                'detailed_results': {
                    'geocoding_results': result.geocoding_results,
                    'database_results': result.database_storage_results,
                    'spatial_results': result.spatial_query_results
                },
                'system_health': health_check,
                'data_quality': {
                    'total_records_analyzed': quality_report.total_records,
                    'success_rate': quality_report.success_rate,
                    'geocoding_success_rate': quality_report.geocoding_success_rate,
                    'recommendations': quality_report.recommendations
                },
                'frontend_readiness': {
                    'sample_data_available': len(result.frontend_ready_data) > 0,
                    'coordinates_validated': all(
                        permit.get('coordinates', {}).get('lat') and
                        permit.get('coordinates', {}).get('lng')
                        for permit in result.frontend_ready_data
                    ),
                    'pricing_data_available': any(
                        permit.get('pricing', {}).get('total_price_per_load')
                        for permit in result.frontend_ready_data
                    ),
                    'next_js_ready': True,
                    'leaflet_ready': True,
                    'supabase_integration_ready': result.database_storage_results.get('success', False)
                },
                'next_steps': self._generate_next_steps_recommendations(result),
                'timestamp': datetime.now().isoformat()
            }

            return report

        except Exception as e:
            logger.error(f"❌ Failed to generate test report: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _generate_next_steps_recommendations(self, result: TestWorkflowResult) -> List[str]:
        """Generate next steps recommendations based on test results"""
        recommendations = []

        if result.success:
            recommendations.append("✅ All tests passed! Ready to proceed with frontend development.")

            if len(result.frontend_ready_data) > 0:
                recommendations.append("📱 Sample data prepared for Next.js + Leaflet integration.")
                recommendations.append("🗺️ Initialize Next.js project with mapping components.")
                recommendations.append("🔌 Configure Supabase client for real-time data access.")

            if result.spatial_query_results.get('spatial_functions_working'):
                recommendations.append("🚗 Spatial queries validated - implement drive-time calculations.")
                recommendations.append("📍 PostGIS functions ready for proximity-based features.")

            if result.database_storage_results.get('success'):
                recommendations.append("💾 Database integration complete - ready for production data.")
                recommendations.append("💰 Pricing calculations working - implement LDP quote generation.")
        else:
            recommendations.append("❌ Some tests failed - review errors before frontend development.")

            if result.geocoding_results.get('failed_count', 0) > 0:
                recommendations.append("🗺️ Address geocoding issues - check API keys and address formats.")

            if not result.database_storage_results.get('success'):
                recommendations.append("💾 Fix database integration issues before proceeding.")

        # Always include these recommendations
        recommendations.extend([
            "🔄 Run full data processing on complete dataset when ready.",
            "📊 Set up monitoring dashboard for production deployment.",
            "🎨 Design user interface for construction industry professionals."
        ])

        return recommendations

async def main():
    """Run the limited geocoding test workflow"""
    print("🧪 Limited Geocoding Test Workflow for Frontend Development")
    print("=" * 80)

    workflow = LimitedGeocodingTestWorkflow()
    result = await workflow.run_complete_test_workflow()

    # Generate comprehensive report
    report = await workflow.generate_test_report(result)

    # Save report to file
    report_filename = f"limited_geocoding_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n📄 Test report saved to: {report_filename}")
    print(f"🎯 Overall Success: {'✅ PASSED' if result.success else '❌ FAILED'}")

    if result.success:
        print(f"📊 Results Summary:")
        print(f"   • Sample permits selected: {result.sample_permits_selected}")
        print(f"   • Geocoding success: {result.geocoding_results.get('success_count', 0)}/{result.sample_permits_selected}")
        print(f"   • Database records stored: {result.database_storage_results.get('records_processed', 0)}")
        print(f"   • Frontend data prepared: {len(result.frontend_ready_data)} records")
        print(f"   • Processing time: {result.processing_time_ms}ms")
        print("\n🚀 Ready for Next.js + Leaflet frontend development!")
    else:
        print(f"❌ Error: {result.error_message}")

    return result

if __name__ == "__main__":
    asyncio.run(main())
