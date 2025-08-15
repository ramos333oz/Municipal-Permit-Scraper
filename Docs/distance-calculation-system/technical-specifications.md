# Distance Calculation System - Technical Specifications

## Database Schema Specifications

### **Distance Calculations Table**
```sql
CREATE TABLE distance_calculations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    origin_lat DECIMAL(10,8) NOT NULL,
    origin_lng DECIMAL(11,8) NOT NULL,
    destination_lat DECIMAL(10,8) NOT NULL,
    destination_lng DECIMAL(11,8) NOT NULL,
    distance_meters INTEGER NOT NULL,
    duration_seconds INTEGER NOT NULL,
    duration_in_traffic_seconds INTEGER,
    api_response JSONB,
    cache_expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '30 days'),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_coordinates CHECK (
        origin_lat BETWEEN -90 AND 90 AND
        origin_lng BETWEEN -180 AND 180 AND
        destination_lat BETWEEN -90 AND 90 AND
        destination_lng BETWEEN -180 AND 180
    ),
    CONSTRAINT positive_values CHECK (
        distance_meters >= 0 AND
        duration_seconds >= 0 AND
        (duration_in_traffic_seconds IS NULL OR duration_in_traffic_seconds >= 0)
    ),
    
    -- Unique constraint for caching
    CONSTRAINT unique_route UNIQUE (
        ROUND(origin_lat::numeric, 6),
        ROUND(origin_lng::numeric, 6),
        ROUND(destination_lat::numeric, 6),
        ROUND(destination_lng::numeric, 6)
    )
);

-- Performance indexes
CREATE INDEX idx_distance_calc_origin ON distance_calculations USING GIST(
    ST_Point(origin_lng, origin_lat)
);

CREATE INDEX idx_distance_calc_destination ON distance_calculations USING GIST(
    ST_Point(destination_lng, destination_lat)
);

CREATE INDEX idx_distance_calc_expires ON distance_calculations(cache_expires_at);

-- Cleanup function for expired cache entries
CREATE OR REPLACE FUNCTION cleanup_expired_distance_cache()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM distance_calculations 
    WHERE cache_expires_at < NOW();
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;
```

### **Route Optimizations Table**
```sql
CREATE TABLE route_optimizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    permit_ids UUID[] NOT NULL,
    origin_coordinates GEOMETRY(POINT, 4326),
    optimized_route JSONB NOT NULL,
    total_distance_meters INTEGER NOT NULL,
    total_duration_seconds INTEGER NOT NULL,
    optimization_type VARCHAR(50) DEFAULT 'shortest_time',
    fuel_cost_estimate DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_optimization_type CHECK (
        optimization_type IN ('shortest_time', 'shortest_distance', 'cost_optimized', 'priority_based')
    ),
    CONSTRAINT positive_totals CHECK (
        total_distance_meters >= 0 AND
        total_duration_seconds >= 0 AND
        (fuel_cost_estimate IS NULL OR fuel_cost_estimate >= 0)
    )
);

CREATE INDEX idx_route_opt_permits ON route_optimizations USING GIN(permit_ids);
CREATE INDEX idx_route_opt_origin ON route_optimizations USING GIST(origin_coordinates);
CREATE INDEX idx_route_opt_type ON route_optimizations(optimization_type);
```

### **Permits Table Extensions**
```sql
-- Add distance-related fields to existing permits table
ALTER TABLE permits ADD COLUMN IF NOT EXISTS roundtrip_minutes INTEGER;
ALTER TABLE permits ADD COLUMN IF NOT EXISTS added_minutes INTEGER DEFAULT 0;
ALTER TABLE permits ADD COLUMN IF NOT EXISTS distance_to_depot_meters INTEGER;
ALTER TABLE permits ADD COLUMN IF NOT EXISTS last_distance_update TIMESTAMP WITH TIME ZONE;
ALTER TABLE permits ADD COLUMN IF NOT EXISTS depot_coordinates GEOMETRY(POINT, 4326);

-- Add constraints for new fields
ALTER TABLE permits ADD CONSTRAINT valid_minutes CHECK (
    (roundtrip_minutes IS NULL OR roundtrip_minutes >= 0) AND
    added_minutes >= 0
);

ALTER TABLE permits ADD CONSTRAINT valid_distance CHECK (
    distance_to_depot_meters IS NULL OR distance_to_depot_meters >= 0
);

-- Indexes for performance
CREATE INDEX idx_permits_roundtrip ON permits(roundtrip_minutes) WHERE roundtrip_minutes IS NOT NULL;
CREATE INDEX idx_permits_distance_update ON permits(last_distance_update);
CREATE INDEX idx_permits_depot ON permits USING GIST(depot_coordinates) WHERE depot_coordinates IS NOT NULL;
```

## API Specifications

### **Distance Calculation Endpoints**

#### **POST /api/distance/calculate**
Calculate distance between two points.

**Request Body:**
```typescript
interface CalculateDistanceRequest {
  origin: {
    lat: number;
    lng: number;
  };
  destination: {
    lat: number;
    lng: number;
  };
  options?: {
    use_cache?: boolean;
    traffic_model?: 'best_guess' | 'pessimistic' | 'optimistic';
    departure_time?: string; // ISO 8601 format
  };
}
```

**Response:**
```typescript
interface CalculateDistanceResponse {
  success: boolean;
  data?: {
    distance_meters: number;
    duration_seconds: number;
    duration_in_traffic_seconds?: number;
    cached: boolean;
    cache_age_minutes?: number;
  };
  error?: string;
  processing_time_ms: number;
}
```

#### **POST /api/distance/batch**
Calculate distances for multiple routes.

**Request Body:**
```typescript
interface BatchDistanceRequest {
  routes: Array<{
    id?: string;
    origin: { lat: number; lng: number };
    destination: { lat: number; lng: number };
    permit_id?: string;
  }>;
  options?: {
    use_cache?: boolean;
    max_concurrent?: number; // Default: 5
    traffic_model?: 'best_guess' | 'pessimistic' | 'optimistic';
  };
}
```

**Response:**
```typescript
interface BatchDistanceResponse {
  success: boolean;
  data?: {
    results: Array<{
      id?: string;
      permit_id?: string;
      distance_meters: number;
      duration_seconds: number;
      duration_in_traffic_seconds?: number;
      cached: boolean;
      status: 'success' | 'error';
      error_message?: string;
    }>;
    summary: {
      total_processed: number;
      successful: number;
      failed: number;
      cache_hits: number;
      api_calls: number;
      total_cost_estimate: number; // USD
    };
  };
  error?: string;
  processing_time_ms: number;
}
```

#### **POST /api/distance/pricing**
Calculate LDP pricing based on distance.

**Request Body:**
```typescript
interface PricingCalculationRequest {
  site_number: string;
  origin?: { lat: number; lng: number };
  destination?: { lat: number; lng: number };
  distance_data?: {
    duration_seconds: number;
    distance_meters: number;
  };
  pricing_params: {
    added_minutes?: number; // Default: 0
    dump_fee?: number; // Default: 0
    ldp_fee?: number; // Default: 0
  };
  update_permit?: boolean; // Default: true
}
```

**Response:**
```typescript
interface PricingCalculationResponse {
  success: boolean;
  data?: {
    site_number: string;
    roundtrip_minutes: number;
    added_minutes: number;
    trucking_price_per_load: number;
    total_price_per_load: number;
    pricing_breakdown: {
      dump_fee: number;
      trucking_price: number;
      ldp_fee: number;
    };
    distance_data: {
      distance_meters: number;
      duration_seconds: number;
      cached: boolean;
    };
    permit_updated: boolean;
  };
  error?: string;
  processing_time_ms: number;
}
```

#### **GET /api/distance/cache/stats**
Get caching statistics and performance metrics.

**Response:**
```typescript
interface CacheStatsResponse {
  success: boolean;
  data?: {
    cache_stats: {
      total_entries: number;
      cache_hit_rate_24h: number;
      cache_hit_rate_7d: number;
      expired_entries: number;
      storage_size_mb: number;
    };
    api_usage: {
      calls_today: number;
      calls_this_month: number;
      estimated_cost_today: number;
      estimated_cost_month: number;
      savings_from_cache: number;
    };
    performance: {
      avg_response_time_ms: number;
      avg_cache_lookup_ms: number;
      avg_api_call_ms: number;
    };
  };
  error?: string;
}
```

## Service Class Specifications

### **DistanceCalculationService**
```typescript
class DistanceCalculationService {
  private googleMapsClient: Client;
  private supabaseClient: SupabaseClient;
  private cacheService: DistanceCacheService;
  private rateLimiter: RateLimiter;

  constructor(options?: {
    apiKey?: string;
    rateLimit?: number; // requests per second
    cacheEnabled?: boolean;
  });

  // Core distance calculation
  async calculateDistance(
    origin: Coordinates,
    destination: Coordinates,
    options?: DistanceOptions
  ): Promise<DistanceResult>;

  // Batch processing
  async batchCalculateDistances(
    routes: RouteRequest[],
    options?: BatchOptions
  ): Promise<BatchDistanceResult>;

  // Route optimization
  async optimizeRoute(
    permits: PermitLocation[],
    depot: Coordinates,
    options?: OptimizationOptions
  ): Promise<OptimizedRoute>;

  // Cache management
  async clearExpiredCache(): Promise<number>;
  async getCacheStats(): Promise<CacheStats>;
  async warmCache(routes: RouteRequest[]): Promise<void>;
}
```

### **PricingCalculationService**
```typescript
class PricingCalculationService {
  private distanceService: DistanceCalculationService;
  private supabaseClient: SupabaseClient;

  constructor(distanceService: DistanceCalculationService);

  // LDP pricing calculations
  calculateTruckingPrice(
    roundtripMinutes: number,
    addedMinutes?: number
  ): number;

  calculateTotalPrice(
    dumpFee: number,
    truckingPrice: number,
    ldpFee: number
  ): number;

  // Permit pricing updates
  async updatePermitPricing(
    siteNumber: string,
    pricingParams: PricingParams
  ): Promise<PricingResult>;

  async batchUpdatePricing(
    permits: PermitPricingRequest[]
  ): Promise<BatchPricingResult>;

  // Quote generation
  async generateQuoteSheet(
    permits: string[],
    depot: Coordinates,
    options?: QuoteOptions
  ): Promise<QuoteSheet>;
}
```

## Performance Specifications

### **Response Time Requirements**
- **Single Distance Calculation**: < 2 seconds (95th percentile)
- **Batch Operations (≤25 routes)**: < 10 seconds (95th percentile)
- **Cache Lookup**: < 100ms (99th percentile)
- **Database Updates**: < 500ms (95th percentile)
- **Route Optimization**: < 30 seconds for 25 permits (95th percentile)

### **Throughput Requirements**
- **Concurrent Calculations**: Support 10+ simultaneous requests
- **Daily API Calls**: Handle 1,000+ distance calculations
- **Batch Processing**: Process 100+ permits in single operation
- **Cache Operations**: 1,000+ cache lookups per minute

### **Reliability Requirements**
- **Uptime**: 99.9% availability
- **Error Rate**: < 1% for production operations
- **Cache Hit Rate**: > 80% for cost optimization
- **Data Accuracy**: ± 2% for construction industry standards

### **Cost Optimization Targets**
- **API Cost Reduction**: > 75% through intelligent caching
- **Monthly API Budget**: < $50 for typical construction workflows
- **Cache Efficiency**: > 80% hit rate for frequently accessed routes
- **Storage Optimization**: < 100MB cache storage per 10,000 calculations

## Security Specifications

### **API Key Management**
- Google Maps API key stored in environment variables
- Rate limiting to prevent API abuse
- Request validation and sanitization
- Error handling without exposing sensitive information

### **Data Protection**
- Coordinate data encryption in transit
- Cache data retention policies (30-day expiration)
- Audit logging for distance calculations
- Access control for administrative functions

### **Input Validation**
- Coordinate range validation (-90 to 90 lat, -180 to 180 lng)
- Request size limits for batch operations
- Rate limiting per client/IP address
- SQL injection prevention for database operations

## Monitoring and Alerting

### **Key Metrics**
- API response times and error rates
- Cache hit rates and storage usage
- Google Maps API usage and costs
- Database performance and query times

### **Alert Conditions**
- Response time > 5 seconds for single calculations
- Error rate > 5% over 5-minute window
- Cache hit rate < 70% over 1-hour window
- Daily API cost > $10 threshold

### **Logging Requirements**
- All API requests and responses
- Cache hits/misses and performance
- Error conditions and stack traces
- Cost tracking and optimization metrics

This technical specification provides the detailed implementation requirements for the Distance Calculation System following established agent patterns and architectural standards.
