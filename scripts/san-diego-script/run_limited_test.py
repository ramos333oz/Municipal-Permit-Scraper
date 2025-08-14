#!/usr/bin/env python3
"""
Simple runner for the limited geocoding test workflow
Sets up environment properly and runs the test
"""

import os
import sys
import asyncio

# Set up environment variables BEFORE importing other modules
os.environ['SUPABASE_URL'] = 'https://tellxlrnkwooikljwlhc.supabase.co'
os.environ['SUPABASE_ANON_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRlbGx4bHJua3dvb2lrbGp3bGhjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ4OTYyNzQsImV4cCI6MjA3MDQ3MjI3NH0.8qHGO5Iew5qL9-npMJNNdRZklZBJQPwEiDLuPZH7Nsk'
os.environ['GEOCODIO_API_KEY'] = '806d6c98688b022ff79c7dc6d08b662c897bfdb'

print("🔧 Environment configured:")
print(f"   SUPABASE_URL: {os.environ['SUPABASE_URL']}")
print(f"   SUPABASE_ANON_KEY: {os.environ['SUPABASE_ANON_KEY'][:20]}...")
print(f"   GEOCODIO_API_KEY: {os.environ['GEOCODIO_API_KEY'][:20]}...")
print()

# Now import and run the workflow
from limited_geocoding_test_workflow import LimitedGeocodingTestWorkflow

async def main():
    """Run the test workflow with proper environment setup"""
    workflow = LimitedGeocodingTestWorkflow()
    result = await workflow.run_complete_test_workflow()
    
    # Generate comprehensive report
    report = await workflow.generate_test_report(result)
    
    # Save report to file
    from datetime import datetime
    import json
    
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
