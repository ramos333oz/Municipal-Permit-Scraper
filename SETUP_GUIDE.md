# Setup Guide: Direct to Supabase Architecture

## Overview

This guide implements the **recommended architecture** from our data architecture analysis: **Direct to Supabase** with optional Airtable integration for business users.

## Architecture Benefits

✅ **Cost Efficient**: $50-75/month vs $250-475/month for Airtable staging  
✅ **High Performance**: Direct database operations, minimal latency  
✅ **Geospatial Ready**: PostGIS for spatial queries and distance calculations  
✅ **Scalable**: Handles 35-40 municipal portals efficiently  
✅ **Production Ready**: ACID transactions, robust error handling  

## Prerequisites

### 1. Supabase Account Setup
1. Go to [supabase.com](https://supabase.com) and create an account
2. Create a new project: "San Diego County Permits"
3. Note your project URL and anon key from Settings > API

### 2. Install Dependencies
```bash
# Install required packages
pip install supabase
pip install requests
pip install pandas  # For CSV analysis
pip install playwright  # For web scraping
```

### 3. Environment Variables
Create a `.env` file in your project root:
```bash
# Supabase Configuration (REQUIRED)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key

# Optional: Google Maps API for premium geocoding
GOOGLE_MAPS_API_KEY=your-google-maps-api-key

# Optional: Airtable (for business users who need collaboration)
AIRTABLE_API_KEY=your-airtable-api-key
AIRTABLE_BASE_ID=your-airtable-base-id
```

## Database Setup

### 1. Enable PostGIS Extension
In your Supabase SQL Editor, run:
```sql
-- Enable PostGIS extension for geospatial data
CREATE EXTENSION IF NOT EXISTS postgis;
```

### 2. Create Permits Table
Run the following SQL in Supabase SQL Editor:
```sql
-- Create permits table with enhanced schema
CREATE TABLE permits (
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
CREATE INDEX idx_permits_coordinates ON permits USING GIST (coordinates);

-- Create business logic indexes
CREATE INDEX idx_permits_status ON permits (status);
CREATE INDEX idx_permits_city ON permits (project_city);
CREATE INDEX idx_permits_opened_date ON permits (opened_date);
CREATE INDEX idx_permits_site_number ON permits (site_number);

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
```

### 3. Set Row Level Security (RLS)
```sql
-- Enable RLS for security
ALTER TABLE permits ENABLE ROW LEVEL SECURITY;

-- Create policy for authenticated users
CREATE POLICY "Enable all operations for authenticated users" ON permits
FOR ALL USING (auth.role() = 'authenticated');

-- Create policy for service role (for API operations)
CREATE POLICY "Enable all operations for service role" ON permits
FOR ALL USING (auth.role() = 'service_role');
```

## Usage Instructions

### 1. Basic Scraping with Supabase Integration
```bash
# Run the enhanced scraper with direct Supabase integration
python scripts/san_diego_county_scraper.py
```

This will:
- ✅ Scrape permits from San Diego County portal
- ✅ Add geocoding information (coordinates, distances, drive times)
- ✅ Calculate trucking prices using LDP formula
- ✅ Upload directly to Supabase
- ✅ Save local JSON backup

### 2. Manual Supabase Integration
```bash
# Test Supabase integration with existing data
python scripts/supabase_direct_integration.py
```

### 3. Migration from Airtable (if applicable)
```bash
# Migrate existing data from Airtable approach to Supabase
python scripts/supabase_direct_integration.py migrate
```

### 4. Geocoding Enhancement
```bash
# Add geocoding to existing permit data
python scripts/geocoding_integration.py
```

## Data Flow Architecture

```
San Diego County Portal
         ↓
    Web Scraper
         ↓
   Data Validation
         ↓
    Geocoding API
         ↓
   Pricing Calculations
         ↓
    Supabase (PostgreSQL/PostGIS)
         ↓
   Business Intelligence Dashboard
```

## Business Intelligence Queries

### 1. Find Permits Near Depot
```sql
-- Find permits within 25 miles of depot
SELECT 
    site_number,
    project_name,
    address,
    ST_Distance(
        coordinates,
        ST_SetSRID(ST_MakePoint(-117.1611, 32.7157), 4326)::geography
    ) / 1609.34 AS distance_miles
FROM permits
WHERE coordinates IS NOT NULL
  AND ST_DWithin(
      coordinates::geography,
      ST_SetSRID(ST_MakePoint(-117.1611, 32.7157), 4326)::geography,
      40233.6  -- 25 miles in meters
  )
ORDER BY distance_miles;
```

### 2. Pricing Analysis by Status
```sql
-- Analyze pricing by permit status
SELECT 
    status,
    COUNT(*) as permit_count,
    AVG(trucking_price_per_load) as avg_trucking_price,
    AVG(total_price_per_load) as avg_total_price,
    SUM(total_price_per_load) as total_revenue_potential
FROM permits
WHERE status IS NOT NULL
GROUP BY status
ORDER BY permit_count DESC;
```

### 3. Geographic Distribution
```sql
-- Analyze permit distribution by city
SELECT 
    project_city,
    COUNT(*) as permit_count,
    AVG(distance_from_depot_miles) as avg_distance,
    AVG(estimated_roundtrip_minutes) as avg_drive_time
FROM permits
WHERE project_city IS NOT NULL
GROUP BY project_city
ORDER BY permit_count DESC;
```

## Optional: Airtable Integration for Business Users

If business users need collaborative features, you can optionally set up Airtable:

### 1. Create Airtable Base
1. Go to [airtable.com](https://airtable.com)
2. Create base: "San Diego County Permits"
3. Use the schema from `scripts/airtable_integration.py`

### 2. Sync Data (One-way: Supabase → Airtable)
```bash
# Set up environment variables for Airtable
export AIRTABLE_API_KEY="your-api-key"
export AIRTABLE_BASE_ID="your-base-id"

# Run scraper with both integrations
python scripts/san_diego_county_scraper.py
```

## Monitoring and Maintenance

### 1. Database Performance
- Monitor query performance in Supabase dashboard
- Check index usage and optimize as needed
- Set up alerts for storage and API usage

### 2. Data Quality
- Review geocoding success rates
- Monitor for duplicate permits
- Validate pricing calculations

### 3. Scaling Considerations
- Current setup handles 35-40 municipal portals
- Consider read replicas for heavy analytics workloads
- Implement connection pooling for high-frequency scraping

## Cost Monitoring

### Expected Monthly Costs:
- **Supabase Pro**: $25/month + $0.32/GB storage
- **Estimated for 50,000 permits**: ~$50-75/month total
- **Google Maps API** (optional): $2-5/month for geocoding
- **Total**: $50-80/month (vs $250-475/month for Airtable staging)

## Support and Troubleshooting

### Common Issues:
1. **PostGIS not enabled**: Run `CREATE EXTENSION postgis;` in SQL Editor
2. **Permission errors**: Check RLS policies and API keys
3. **Geocoding failures**: Verify Google Maps API key or use OpenStreetMap fallback
4. **Performance issues**: Check indexes and query optimization

### Getting Help:
- Supabase Documentation: [docs.supabase.com](https://docs.supabase.com)
- PostGIS Documentation: [postgis.net](https://postgis.net)
- Project Issues: Check logs in `scripts/` directory

## Next Steps

1. ✅ **Complete setup** following this guide
2. ✅ **Test with San Diego County** data
3. ✅ **Expand to additional municipal portals**
4. ✅ **Build business intelligence dashboard**
5. ✅ **Integrate with LDP Quote Sheet system**

This architecture provides a solid foundation for scaling to 35-40 municipal portals while maintaining cost efficiency and high performance for construction industry applications.
