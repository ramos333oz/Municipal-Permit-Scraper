# Geocoding API Setup Guide for Municipal Permit Addresses

## Overview

This guide implements a **multi-tiered geocoding strategy** based on comprehensive research to convert municipal permit addresses to coordinates for distance calculations and route planning.

## Research-Based Recommendations

### **Multi-Tiered Architecture**
1. **Primary: Geocodio** - US-focused, rooftop accuracy, data enrichment
2. **Secondary: Google Maps** - Global coverage, edge cases
3. **Fallback: OpenCage** - Cost-effective backup
4. **Free Fallback: Nominatim** - OpenStreetMap data

## API Service Comparison

| Service | Free Tier | Paid Pricing | Accuracy | Best For |
|---------|-----------|--------------|----------|----------|
| **Geocodio** ⭐ | 2,500/day | $0.50/1K | 70% rooftop | US municipal addresses |
| **Google Maps** | 40,000/month | $5/1K | High | Global coverage, edge cases |
| **OpenCage** | 2,500/day | $50/100K | Good | Cost-effective backup |
| **Nominatim** | Free | Free | Variable | Open source fallback |

## Setup Instructions

### 1. API Key Registration

#### Geocodio (Primary - Recommended)
1. Go to [geocod.io](https://www.geocod.io)
2. Sign up for free account (2,500 requests/day)
3. Get API key from dashboard
4. **Benefits**: US-focused, rooftop accuracy, data enrichment (Census, ZIP+4)

#### Google Maps (Secondary)
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Enable Geocoding API
3. Create API key with Geocoding API access
4. **Benefits**: 40,000 free requests/month, excellent edge case handling

#### OpenCage (Fallback)
1. Go to [opencagedata.com](https://opencagedata.com)
2. Sign up for free account (2,500 requests/day)
3. Get API key from dashboard
4. **Benefits**: Cost-effective, permissive terms

### 2. Environment Configuration

Create or update your `.env` file:
```bash
# Primary geocoding service (RECOMMENDED)
GEOCODIO_API_KEY=your_geocodio_api_key_here

# Secondary service for edge cases
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here

# Fallback service
OPENCAGE_API_KEY=your_opencage_api_key_here

# Existing Supabase configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
```

### 3. Install Dependencies

```bash
# Install required packages
pip install requests
pip install python-dotenv
pip install dataclasses-json  # For structured data handling
```

## Implementation Integration

### 1. Update Main Scraper

Modify your existing scraper to use the enhanced geocoding service:

```python
# In your main scraper file
from enhanced_geocoding_service import EnhancedGeocodingService

# Initialize geocoding service
geocoder = EnhancedGeocodingService()

# Process permits with geocoding
def add_geocoding_to_permits(permits_data):
    geocoded_permits = []
    
    for permit in permits_data:
        address = permit.get('address')
        if address:
            # Use multi-tiered geocoding
            result = geocoder.geocode_address(address, min_confidence=0.7)
            
            if result:
                permit['coordinates'] = {
                    'latitude': result.latitude,
                    'longitude': result.longitude
                }
                permit['geocoding_accuracy'] = result.accuracy
                permit['geocoding_confidence'] = result.confidence
                permit['geocoding_source'] = result.source
                permit['formatted_address'] = result.formatted_address
                
                # Add data enrichment from Geocodio
                if result.additional_data:
                    permit['enrichment_data'] = result.additional_data
        
        geocoded_permits.append(permit)
    
    return geocoded_permits
```

### 2. Update Supabase Schema

Add geocoding fields to your permits table:

```sql
-- Add geocoding columns to existing permits table
ALTER TABLE permits ADD COLUMN IF NOT EXISTS geocoding_accuracy VARCHAR(50);
ALTER TABLE permits ADD COLUMN IF NOT EXISTS geocoding_confidence DECIMAL(3,2);
ALTER TABLE permits ADD COLUMN IF NOT EXISTS geocoding_source VARCHAR(20);
ALTER TABLE permits ADD COLUMN IF NOT EXISTS formatted_address TEXT;
ALTER TABLE permits ADD COLUMN IF NOT EXISTS enrichment_data JSONB;

-- Create index for geocoding quality filtering
CREATE INDEX IF NOT EXISTS idx_permits_geocoding_confidence 
ON permits (geocoding_confidence) WHERE geocoding_confidence IS NOT NULL;

-- Create index for geocoding source analysis
CREATE INDEX IF NOT EXISTS idx_permits_geocoding_source 
ON permits (geocoding_source) WHERE geocoding_source IS NOT NULL;
```

### 3. Enhanced Distance Calculations

Update your distance calculation functions:

```python
def calculate_enhanced_distance_metrics(permit_coords, depot_coords):
    """Calculate enhanced distance metrics with geocoding quality"""
    from math import radians, sin, cos, sqrt, atan2
    
    # Haversine formula for distance
    lat1, lon1 = radians(permit_coords[0]), radians(permit_coords[1])
    lat2, lon2 = radians(depot_coords[0]), radians(depot_coords[1])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    # Earth radius in miles
    distance_miles = 3956 * c
    
    # Estimate drive time (35 mph average + 10 min loading)
    roundtrip_minutes = int((distance_miles / 35) * 60 * 2 + 10)
    
    # LDP pricing formula
    trucking_price = roundtrip_minutes * 1.83
    
    return {
        'distance_miles': round(distance_miles, 2),
        'roundtrip_minutes': roundtrip_minutes,
        'trucking_price_per_load': round(trucking_price, 2)
    }
```

## Usage Examples

### 1. Basic Geocoding

```python
from enhanced_geocoding_service import EnhancedGeocodingService

# Initialize service
geocoder = EnhancedGeocodingService()

# Geocode single address
address = "145 HANNALEI DR, VISTA CA 92083"
result = geocoder.geocode_address(address)

if result:
    print(f"Coordinates: {result.latitude}, {result.longitude}")
    print(f"Accuracy: {result.accuracy}")
    print(f"Confidence: {result.confidence}")
    print(f"Source: {result.source}")
```

### 2. Batch Processing

```python
# Batch geocode multiple addresses
addresses = [
    "145 HANNALEI DR, VISTA CA 92083",
    "14024 PEACEFUL VALLEY RANCH RD, JAMUL CA 91935",
    "1600 Amphitheatre Parkway, Mountain View, CA"
]

results = geocoder.batch_geocode_addresses(addresses, min_confidence=0.7)

# Process results
for result in results:
    if result['geocoded']:
        print(f"✅ {result['original_address']} -> {result['latitude']}, {result['longitude']}")
    else:
        print(f"❌ Failed: {result['original_address']}")
```

### 3. Integration with Permit Processing

```python
# Load permits from CSV/Excel
import pandas as pd

# Read downloaded permit data
permits_df = pd.read_csv('RecordList20250811.csv')

# Extract addresses
addresses = permits_df['Address'].dropna().tolist()

# Batch geocode
geocoding_results = geocoder.batch_geocode_addresses(addresses)

# Merge back with permit data
for i, result in enumerate(geocoding_results):
    if result['geocoded']:
        # Add coordinates to permit data
        permits_df.loc[permits_df['Address'] == result['original_address'], 'latitude'] = result['latitude']
        permits_df.loc[permits_df['Address'] == result['original_address'], 'longitude'] = result['longitude']
        permits_df.loc[permits_df['Address'] == result['original_address'], 'geocoding_source'] = result['source']
```

## Cost Management

### Monthly Cost Estimates (50,000 permits)

| Scenario | Geocodio | Google | OpenCage | Total |
|----------|----------|--------|----------|-------|
| **Geocodio Primary** | $25 | $0 | $0 | $25/month |
| **Mixed Usage** | $15 | $10 | $5 | $30/month |
| **Google Primary** | $0 | $250 | $0 | $250/month |

### Cost Optimization Strategies

1. **Use Geocodio as primary** for US addresses (best value)
2. **Cache successful results** to avoid re-geocoding
3. **Implement confidence thresholds** to reduce unnecessary fallbacks
4. **Monitor API usage** through service dashboards

## Quality Assurance

### Accuracy Validation

```python
def validate_geocoding_quality(results):
    """Analyze geocoding quality metrics"""
    total = len(results)
    successful = sum(1 for r in results if r['geocoded'])
    
    # Accuracy distribution
    accuracy_counts = {}
    confidence_scores = []
    
    for result in results:
        if result['geocoded']:
            accuracy = result['accuracy']
            accuracy_counts[accuracy] = accuracy_counts.get(accuracy, 0) + 1
            confidence_scores.append(result['confidence'])
    
    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
    
    print(f"📊 Geocoding Quality Report:")
    print(f"   Success Rate: {successful}/{total} ({successful/total*100:.1f}%)")
    print(f"   Average Confidence: {avg_confidence:.2f}")
    print(f"   Accuracy Distribution: {accuracy_counts}")
```

### Error Handling

```python
def robust_geocoding_with_retry(address, max_retries=3):
    """Geocoding with exponential backoff retry"""
    import time
    
    for attempt in range(max_retries):
        try:
            result = geocoder.geocode_address(address)
            if result:
                return result
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                time.sleep(wait_time)
                continue
            else:
                logger.error(f"Failed after {max_retries} attempts: {e}")
    
    return None
```

## Monitoring and Analytics

### Service Usage Tracking

```python
# Get service statistics
stats = geocoder.get_statistics()
print(f"Service Usage: {stats}")

# Monitor success rates by service
success_rate_geocodio = stats['geocodio_success'] / stats['total_requests'] * 100
success_rate_google = stats['google_success'] / stats['total_requests'] * 100
```

### Performance Optimization

1. **Batch processing** for large datasets
2. **Parallel requests** (respecting rate limits)
3. **Local caching** of successful geocodes
4. **Database indexing** on coordinates for spatial queries

## Integration with Existing Workflow

Update your main scraper workflow:

```python
# Enhanced workflow with geocoding
async def enhanced_permit_scraping_workflow():
    # 1. Scrape permits (existing)
    permits = await scrape_municipal_permits()
    
    # 2. Add geocoding (NEW)
    geocoded_permits = add_geocoding_to_permits(permits)
    
    # 3. Calculate distances and pricing (ENHANCED)
    for permit in geocoded_permits:
        if permit.get('coordinates'):
            metrics = calculate_enhanced_distance_metrics(
                permit['coordinates'], depot_coordinates
            )
            permit.update(metrics)
    
    # 4. Store in Supabase (existing)
    supabase_client.upsert_permits(geocoded_permits)
```

This geocoding integration provides accurate, cost-effective address-to-coordinate conversion optimized for construction industry municipal permit applications.
