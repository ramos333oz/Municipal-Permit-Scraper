#!/usr/bin/env python3
"""
San Diego County CSV-Based Permit Scraper
Updated to match actual CSV structure: Record Number, Type, Address, Date Opened, Status

Workflow: Browser → Form → Search → CSV Download → Data Processing → Geocoding → Database Storage
"""

import asyncio
import pandas as pd
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# Enhanced geocoding service
try:
    from enhanced_geocoding_service import EnhancedGeocodingService
    ENHANCED_GEOCODING_AVAILABLE = True
except ImportError:
    ENHANCED_GEOCODING_AVAILABLE = False

# Supabase integration
try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SanDiegoCSVScraper:
    """CSV-based scraper following proven workflow from agent documentation"""
    
    def __init__(self):
        self.base_url = "https://publicservices.sandiegocounty.gov/CitizenAccess/Cap/CapHome.aspx?module=LUEG-PDS&TabName=LUEG-PDS"
        self.download_dir = Path("downloads")
        self.download_dir.mkdir(exist_ok=True)
        
        # Initialize services
        if ENHANCED_GEOCODING_AVAILABLE:
            self.geocoder = EnhancedGeocodingService()
            logger.info("✅ Enhanced geocoding service initialized")
        else:
            self.geocoder = None
            logger.warning("⚠️ Enhanced geocoding service not available")
        
        if SUPABASE_AVAILABLE:
            self.supabase_url = os.getenv('SUPABASE_URL')
            self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
            if self.supabase_url and self.supabase_key:
                self.supabase = create_client(self.supabase_url, self.supabase_key)
                logger.info("✅ Supabase client initialized")
            else:
                self.supabase = None
                logger.warning("⚠️ Supabase credentials not found")
        else:
            self.supabase = None
            logger.warning("⚠️ Supabase not available")
    
    async def download_csv_data(self, date_from="01/01/2023", date_to=None):
        """
        Download CSV data from San Diego County portal
        Following proven workflow: Browser → Form → Search → CSV Download
        """
        if date_to is None:
            date_to = datetime.now().strftime("%m/%d/%Y")
        
        logger.info(f"🚀 Starting CSV download from {date_from} to {date_to}")
        
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                accept_downloads=True,
                download_path=str(self.download_dir)
            )
            page = await context.new_page()
            
            try:
                # Step 1: Navigate to portal
                logger.info("📍 Navigating to San Diego County portal...")
                await page.goto(self.base_url, wait_until="networkidle")
                await page.wait_for_timeout(3000)
                
                # Step 2: Fill search form
                logger.info("📝 Filling search form...")
                
                # Select "Grading Perm" from record type dropdown
                await page.click('select[name*="RecordType"]')
                await page.select_option('select[name*="RecordType"]', label="Grading Perm")
                logger.info("✅ Selected 'Grading Perm' record type")
                
                # Set date range
                await page.fill('input[name*="DateFrom"]', date_from)
                await page.fill('input[name*="DateTo"]', date_to)
                logger.info(f"✅ Set date range: {date_from} to {date_to}")
                
                # Step 3: Execute search
                logger.info("🔍 Executing search...")
                await page.click('input[type="submit"][value*="Search"]')
                await page.wait_for_load_state("networkidle")
                await page.wait_for_timeout(5000)
                
                # Step 4: Download CSV file
                logger.info("📥 Downloading CSV file...")
                
                # Look for download/export button
                download_selectors = [
                    'a[href*="Export"]',
                    'input[value*="Export"]',
                    'a[href*="Download"]',
                    'input[value*="Download"]',
                    'a:has-text("Export")',
                    'a:has-text("Download")'
                ]
                
                download_started = False
                for selector in download_selectors:
                    try:
                        if await page.locator(selector).count() > 0:
                            logger.info(f"🎯 Found download button: {selector}")
                            
                            # Start download
                            async with page.expect_download() as download_info:
                                await page.click(selector)
                            
                            download = await download_info.value
                            
                            # Save downloaded file
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            csv_filename = f"san_diego_permits_{timestamp}.csv"
                            csv_path = self.download_dir / csv_filename
                            
                            await download.save_as(csv_path)
                            logger.info(f"✅ CSV downloaded: {csv_path}")
                            
                            download_started = True
                            break
                    except Exception as e:
                        logger.debug(f"Download selector {selector} failed: {e}")
                        continue
                
                if not download_started:
                    logger.error("❌ Could not find download button")
                    return None
                
                return csv_path
                
            except Exception as e:
                logger.error(f"❌ Error during CSV download: {e}")
                return None
            
            finally:
                await browser.close()
    
    def extract_csv_data(self, csv_path):
        """
        Extract data from CSV file using actual column structure
        Columns: Record Number, Type, Address, Date Opened, Status
        """
        logger.info(f"📊 Extracting data from CSV: {csv_path}")
        
        try:
            # Read CSV file
            df = pd.read_csv(csv_path)
            logger.info(f"📈 Loaded {len(df)} records from CSV")
            
            # Validate expected columns
            expected_columns = ['Record Number', 'Type', 'Address', 'Date Opened', 'Status']
            missing_columns = [col for col in expected_columns if col not in df.columns]
            
            if missing_columns:
                logger.warning(f"⚠️ Missing expected columns: {missing_columns}")
                logger.info(f"📋 Available columns: {list(df.columns)}")
            
            # Extract permits data
            permits = []
            for _, row in df.iterrows():
                permit = {
                    'site_number': row.get('Record Number', ''),
                    'record_type': row.get('Type', ''),
                    'address': row.get('Address', ''),
                    'date_opened': row.get('Date Opened', ''),
                    'status': row.get('Status', ''),
                    'project_city': 'San Diego County',
                    'source_portal': 'San Diego County',
                    'raw_csv_data': row.to_dict(),
                    'scraped_at': datetime.now().isoformat()
                }
                permits.append(permit)
            
            logger.info(f"✅ Extracted {len(permits)} permits from CSV")
            
            # Analyze data completeness
            address_count = sum(1 for p in permits if p['address'] and p['address'].strip())
            logger.info(f"📍 Addresses available: {address_count}/{len(permits)} ({address_count/len(permits)*100:.1f}%)")
            
            return permits
            
        except Exception as e:
            logger.error(f"❌ Error extracting CSV data: {e}")
            return []
    
    def add_geocoding(self, permits_data):
        """
        Add geocoding using Geocodio (PRIMARY) for Address field
        Use addresses exactly as they appear in CSV
        """
        if not self.geocoder:
            logger.warning("⚠️ No geocoding service available")
            return permits_data
        
        logger.info("🗺️ Starting geocoding process...")
        
        geocoded_permits = []
        for i, permit in enumerate(permits_data, 1):
            address = permit.get('address', '').strip()
            
            if address:
                logger.info(f"📍 Geocoding {i}/{len(permits_data)}: {address}")
                
                # Use enhanced geocoding service
                result = self.geocoder.geocode_address(address, min_confidence=0.7)
                
                if result:
                    permit['coordinates'] = {
                        'latitude': result.latitude,
                        'longitude': result.longitude
                    }
                    permit['geocoding_accuracy'] = result.accuracy
                    permit['geocoding_confidence'] = result.confidence
                    permit['geocoding_source'] = result.source
                    permit['formatted_address'] = result.formatted_address
                    
                    # Calculate distance from San Diego County depot
                    depot_lat, depot_lng = 32.7157, -117.1611
                    distance_miles = self.calculate_distance(
                        depot_lat, depot_lng, result.latitude, result.longitude
                    )
                    
                    # Calculate drive time and pricing
                    roundtrip_minutes = int((distance_miles / 35) * 60 * 2 + 10)
                    trucking_price = roundtrip_minutes * 1.83
                    
                    permit['distance_from_depot_miles'] = round(distance_miles, 2)
                    permit['estimated_roundtrip_minutes'] = roundtrip_minutes
                    permit['trucking_price_per_load'] = round(trucking_price, 2)
                    
                    logger.info(f"✅ Geocoded: {result.latitude}, {result.longitude} ({result.source})")
                else:
                    logger.warning(f"❌ Geocoding failed for: {address}")
            else:
                logger.warning(f"⚠️ No address for permit {permit.get('site_number', 'Unknown')}")
            
            geocoded_permits.append(permit)
        
        # Get geocoding statistics
        if hasattr(self.geocoder, 'get_statistics'):
            stats = self.geocoder.get_statistics()
            logger.info(f"📊 Geocoding Statistics: {stats}")
        
        return geocoded_permits
    
    def calculate_distance(self, lat1, lng1, lat2, lng2):
        """Calculate distance between two points using Haversine formula"""
        from math import radians, sin, cos, sqrt, atan2
        
        lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return 3956 * c  # Earth radius in miles
    
    def store_in_supabase(self, permits_data):
        """Store permits data in Supabase database"""
        if not self.supabase:
            logger.warning("⚠️ Supabase not available")
            return False
        
        try:
            logger.info(f"💾 Storing {len(permits_data)} permits in Supabase...")
            
            # Upsert permits data
            result = self.supabase.table("permits").upsert(
                permits_data, on_conflict="site_number"
            ).execute()
            
            logger.info(f"✅ Successfully stored permits in Supabase")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error storing in Supabase: {e}")
            return False
    
    async def run_complete_workflow(self, date_from="01/01/2023", date_to=None):
        """
        Run complete CSV-based workflow:
        Browser → Form → Search → CSV Download → Data Processing → Geocoding → Database Storage
        """
        logger.info("🚀 Starting complete CSV-based workflow...")
        
        try:
            # Step 1: Download CSV data
            csv_path = await self.download_csv_data(date_from, date_to)
            if not csv_path:
                logger.error("❌ CSV download failed")
                return False
            
            # Step 2: Extract data from CSV
            permits_data = self.extract_csv_data(csv_path)
            if not permits_data:
                logger.error("❌ Data extraction failed")
                return False
            
            # Step 3: Add geocoding
            geocoded_permits = self.add_geocoding(permits_data)
            
            # Step 4: Save processed data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"san_diego_permits_processed_{timestamp}.json"
            
            with open(output_file, 'w') as f:
                json.dump(geocoded_permits, f, indent=2, default=str)
            logger.info(f"💾 Saved processed data: {output_file}")
            
            # Step 5: Store in Supabase
            if self.supabase:
                self.store_in_supabase(geocoded_permits)
            
            logger.info("🎉 Complete workflow finished successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Workflow failed: {e}")
            return False

async def main():
    """Test the CSV-based scraper"""
    scraper = SanDiegoCSVScraper()
    
    # Run complete workflow
    success = await scraper.run_complete_workflow(
        date_from="01/01/2023",
        date_to="08/12/2025"
    )
    
    if success:
        logger.info("✅ CSV-based scraping completed successfully!")
    else:
        logger.error("❌ CSV-based scraping failed!")

if __name__ == "__main__":
    asyncio.run(main())
