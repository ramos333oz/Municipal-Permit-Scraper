#!/usr/bin/env python3
"""
Direct Supabase Integration for San Diego County Permit Data
Implements the recommended architecture: Scraper → Data Processing → Supabase (PostgreSQL/PostGIS)
"""

import json
import logging
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import asdict
import asyncio

# Supabase integration
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logging.warning("⚠️ Supabase client not installed. Run: pip install supabase")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseDirectIntegration:
    """Direct integration with Supabase for permit data storage and processing"""
    
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """
        Initialize Supabase direct integration
        
        Args:
            supabase_url: Supabase project URL (can be set via SUPABASE_URL env var)
            supabase_key: Supabase anon key (can be set via SUPABASE_ANON_KEY env var)
        """
        self.supabase_url = supabase_url or os.getenv('SUPABASE_URL')
        self.supabase_key = supabase_key or os.getenv('SUPABASE_ANON_KEY')
        
        if not SUPABASE_AVAILABLE:
            logger.error("❌ Supabase client not available")
            self.client = None
            return
        
        if not self.supabase_url or not self.supabase_key:
            logger.warning("⚠️ Supabase credentials not provided. Set SUPABASE_URL and SUPABASE_ANON_KEY environment variables.")
            self.client = None
            return
        
        try:
            self.client: Client = create_client(self.supabase_url, self.supabase_key)
            logger.info("✅ Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {e}")
            self.client = None
    
    def create_permits_table(self) -> bool:
        """
        Create the permits table with PostGIS support
        Note: This requires database admin privileges
        """
        if not self.client:
            logger.error("❌ Supabase client not available")
            return False
        
        create_table_sql = """
        -- Enable PostGIS extension (requires admin privileges)
        CREATE EXTENSION IF NOT EXISTS postgis;
        
        -- Create permits table with enhanced schema
        CREATE TABLE IF NOT EXISTS permits (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            site_number VARCHAR(50) UNIQUE NOT NULL,
            status VARCHAR(50),
            project_name TEXT,
            address TEXT,
            coordinates GEOMETRY(POINT, 4326), -- PostGIS geospatial
            opened_date DATE,
            material_description TEXT,
            quantity DECIMAL(10,2),
            project_city VARCHAR(100),
            project_company VARCHAR(200),
            project_contact VARCHAR(200),
            project_phone VARCHAR(20),
            project_email VARCHAR(100),
            dump_fee DECIMAL(10,2),
            ldp_fee DECIMAL(10,2),
            trucking_price_per_load DECIMAL(10,2),
            total_price_per_load DECIMAL(10,2),
            distance_from_depot_miles DECIMAL(8,2),
            estimated_roundtrip_minutes INTEGER,
            short_notes TEXT,
            notes TEXT,
            source_portal VARCHAR(100) DEFAULT 'San Diego County',
            scraped_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Create spatial index for performance
        CREATE INDEX IF NOT EXISTS idx_permits_coordinates ON permits USING GIST (coordinates);
        
        -- Create business logic indexes
        CREATE INDEX IF NOT EXISTS idx_permits_status ON permits (status);
        CREATE INDEX IF NOT EXISTS idx_permits_city ON permits (project_city);
        CREATE INDEX IF NOT EXISTS idx_permits_opened_date ON permits (opened_date);
        CREATE INDEX IF NOT EXISTS idx_permits_site_number ON permits (site_number);
        
        -- Create updated_at trigger
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        
        CREATE TRIGGER update_permits_updated_at BEFORE UPDATE ON permits
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """
        
        try:
            # Note: This requires admin privileges and may need to be run manually
            logger.info("📋 Table creation SQL generated. Run manually with admin privileges:")
            logger.info(create_table_sql)
            return True
        except Exception as e:
            logger.error(f"❌ Error creating table: {e}")
            return False
    
    def format_permit_for_supabase(self, permit_data: Dict) -> Dict:
        """
        Format permit data for Supabase insertion
        
        Args:
            permit_data: Dictionary containing permit information
            
        Returns:
            Formatted data for Supabase
        """
        # Create coordinates from latitude/longitude if available
        coordinates = None
        if permit_data.get('coordinates'):
            lat = permit_data['coordinates'].get('latitude')
            lng = permit_data['coordinates'].get('longitude')
            if lat and lng:
                # PostGIS POINT format: POINT(longitude latitude)
                coordinates = f"POINT({lng} {lat})"
        
        # Format data for Supabase
        supabase_record = {
            "site_number": permit_data.get("site_number"),
            "status": permit_data.get("status"),
            "project_name": permit_data.get("project_name"),
            "address": permit_data.get("address"),
            "coordinates": coordinates,
            "opened_date": permit_data.get("opened_date"),
            "material_description": permit_data.get("material_description"),
            "quantity": permit_data.get("quantity"),
            "project_city": permit_data.get("project_city"),
            "project_company": permit_data.get("project_company"),
            "project_contact": permit_data.get("project_contact"),
            "project_phone": permit_data.get("project_phone"),
            "project_email": permit_data.get("project_email"),
            "dump_fee": permit_data.get("dump_fee"),
            "ldp_fee": permit_data.get("ldp_fee"),
            "trucking_price_per_load": permit_data.get("trucking_price_per_load"),
            "total_price_per_load": permit_data.get("total_price_per_load"),
            "distance_from_depot_miles": permit_data.get("distance_from_depot_miles"),
            "estimated_roundtrip_minutes": permit_data.get("estimated_roundtrip_minutes"),
            "short_notes": permit_data.get("short_notes"),
            "notes": permit_data.get("notes"),
            "source_portal": permit_data.get("source_portal", "San Diego County"),
            "scraped_at": permit_data.get("scraped_at")
        }
        
        # Remove None values
        return {k: v for k, v in supabase_record.items() if v is not None}
    
    def check_existing_permit(self, site_number: str) -> Optional[str]:
        """
        Check if a permit already exists in Supabase
        
        Args:
            site_number: The permit site number to check
            
        Returns:
            Record ID if exists, None otherwise
        """
        if not self.client:
            logger.warning("⚠️ Supabase client not available")
            return None
        
        try:
            response = self.client.table("permits").select("id").eq("site_number", site_number).execute()
            
            if response.data:
                return response.data[0]["id"]
            return None
            
        except Exception as e:
            logger.error(f"❌ Error checking existing permit {site_number}: {e}")
            return None
    
    def upsert_permit(self, permit_data: Dict) -> bool:
        """
        Insert or update a permit in Supabase
        
        Args:
            permit_data: Dictionary containing permit information
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            logger.warning("⚠️ Supabase client not available - skipping upload")
            return False
        
        try:
            site_number = permit_data.get("site_number")
            if not site_number:
                logger.error("❌ No site number found in permit data")
                return False
            
            # Format data for Supabase
            supabase_data = self.format_permit_for_supabase(permit_data)
            
            # Use upsert to handle both insert and update
            response = self.client.table("permits").upsert(
                supabase_data,
                on_conflict="site_number"
            ).execute()
            
            if response.data:
                logger.info(f"✅ Successfully upserted permit {site_number}")
                return True
            else:
                logger.error(f"❌ Failed to upsert permit {site_number}: No data returned")
                return False
            
        except Exception as e:
            logger.error(f"❌ Error upserting permit {permit_data.get('site_number', 'unknown')}: {e}")
            return False
    
    def batch_upsert_permits(self, permits: List[Dict]) -> Dict[str, int]:
        """
        Batch upsert multiple permits to Supabase
        
        Args:
            permits: List of permit dictionaries
            
        Returns:
            Dictionary with success/failure counts
        """
        results = {"success": 0, "failed": 0, "skipped": 0}
        
        if not self.client:
            logger.warning("⚠️ Supabase client not available - skipping batch upload")
            results["skipped"] = len(permits)
            return results
        
        logger.info(f"🚀 Starting batch upsert of {len(permits)} permits to Supabase...")
        
        # Process in batches of 100 for optimal performance
        batch_size = 100
        for i in range(0, len(permits), batch_size):
            batch = permits[i:i + batch_size]
            logger.info(f"📤 Processing batch {i//batch_size + 1}/{(len(permits) + batch_size - 1)//batch_size}")
            
            try:
                # Format all permits in the batch
                formatted_permits = [self.format_permit_for_supabase(permit) for permit in batch]
                
                # Batch upsert
                response = self.client.table("permits").upsert(
                    formatted_permits,
                    on_conflict="site_number"
                ).execute()
                
                if response.data:
                    batch_success = len(response.data)
                    results["success"] += batch_success
                    logger.info(f"✅ Batch upserted {batch_success} permits")
                else:
                    results["failed"] += len(batch)
                    logger.error(f"❌ Batch upsert failed: No data returned")
                
            except Exception as e:
                results["failed"] += len(batch)
                logger.error(f"❌ Batch upsert error: {e}")
        
        logger.info(f"📊 Batch upsert complete: {results['success']} success, {results['failed']} failed")
        return results
    
    def get_permits_by_city(self, city: str) -> List[Dict]:
        """
        Retrieve permits by city for analysis
        
        Args:
            city: City name to filter by
            
        Returns:
            List of permit records
        """
        if not self.client:
            logger.warning("⚠️ Supabase client not available")
            return []
        
        try:
            response = self.client.table("permits").select("*").eq("project_city", city).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"❌ Error retrieving permits for city {city}: {e}")
            return []
    
    def calculate_distance_from_depot(self, depot_lat: float, depot_lng: float, max_distance_miles: float = 50) -> List[Dict]:
        """
        Find permits within a certain distance from depot using PostGIS
        
        Args:
            depot_lat: Depot latitude
            depot_lng: Depot longitude
            max_distance_miles: Maximum distance in miles
            
        Returns:
            List of permits with calculated distances
        """
        if not self.client:
            logger.warning("⚠️ Supabase client not available")
            return []
        
        try:
            # Convert miles to meters for PostGIS (1 mile = 1609.34 meters)
            max_distance_meters = max_distance_miles * 1609.34
            
            # PostGIS query to find permits within distance
            query = f"""
            SELECT *,
                   ST_Distance(
                       coordinates,
                       ST_SetSRID(ST_MakePoint({depot_lng}, {depot_lat}), 4326)::geography
                   ) / 1609.34 AS distance_miles
            FROM permits
            WHERE coordinates IS NOT NULL
              AND ST_DWithin(
                  coordinates::geography,
                  ST_SetSRID(ST_MakePoint({depot_lng}, {depot_lat}), 4326)::geography,
                  {max_distance_meters}
              )
            ORDER BY distance_miles;
            """
            
            response = self.client.rpc("execute_sql", {"sql": query}).execute()
            return response.data or []
            
        except Exception as e:
            logger.error(f"❌ Error calculating distances: {e}")
            return []

def load_permits_from_json(json_file: str) -> List[Dict]:
    """Load permits from JSON file"""
    try:
        with open(json_file, 'r') as f:
            permits = json.load(f)
        logger.info(f"📁 Loaded {len(permits)} permits from {json_file}")
        return permits
    except Exception as e:
        logger.error(f"❌ Error loading permits from {json_file}: {e}")
        return []

def main():
    """Main function for testing Supabase direct integration"""
    logger.info("🔗 Testing Supabase Direct Integration")
    
    # Initialize Supabase integration
    supabase = SupabaseDirectIntegration()
    
    if not supabase.client:
        logger.error("❌ Supabase client not available. Please check credentials.")
        return
    
    # Create table schema (requires admin privileges)
    supabase.create_permits_table()
    
    # Load permits from JSON file
    permits = load_permits_from_json("san_diego_permits_with_geocoding.json")
    
    if not permits:
        # Fallback to basic permits file
        permits = load_permits_from_json("san_diego_permits.json")
    
    if permits:
        # Upload permits to Supabase
        results = supabase.batch_upsert_permits(permits)
        
        logger.info("📋 Upload Summary:")
        logger.info(f"   ✅ Successful: {results['success']}")
        logger.info(f"   ❌ Failed: {results['failed']}")
        logger.info(f"   ⏭️ Skipped: {results['skipped']}")
        
        # Test spatial queries (if coordinates available)
        if results['success'] > 0:
            logger.info("🗺️ Testing spatial queries...")
            # San Diego County approximate center
            nearby_permits = supabase.calculate_distance_from_depot(32.7157, -117.1611, 25)
            logger.info(f"📍 Found {len(nearby_permits)} permits within 25 miles of San Diego")
    else:
        logger.warning("⚠️ No permits found to upload")

async def migrate_from_airtable_to_supabase():
    """
    Migration function to move from Airtable staging to direct Supabase
    This can be used to transition existing workflows
    """
    logger.info("🔄 Starting migration from Airtable to Supabase...")

    # Initialize both integrations
    supabase = SupabaseDirectIntegration()

    try:
        from airtable_integration import AirtableIntegration
        airtable = AirtableIntegration()

        # TODO: Implement Airtable data export
        # This would require Airtable API to export existing data
        logger.info("📤 Airtable integration available for migration")

    except ImportError:
        logger.warning("⚠️ Airtable integration not available")

    # For now, use JSON files as migration source
    permits = load_permits_from_json("san_diego_permits_with_geocoding.json")

    if permits and supabase.client:
        results = supabase.batch_upsert_permits(permits)
        logger.info(f"✅ Migration complete: {results['success']} permits migrated")
    else:
        logger.error("❌ Migration failed: No data or Supabase unavailable")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "migrate":
        asyncio.run(migrate_from_airtable_to_supabase())
    else:
        main()
