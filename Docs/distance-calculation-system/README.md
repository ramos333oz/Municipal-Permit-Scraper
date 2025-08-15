# Distance Calculation System Implementation Documentation

## Overview

This document provides comprehensive implementation guidance for the Distance Calculation System, the highest priority component identified in the Municipal Permit System gap analysis. This system enables drive-time calculations essential for the LDP pricing formula and construction industry route optimization.

## Architecture Alignment

### **Direct-to-Supabase Integration** ⭐ **ESTABLISHED STANDARD**
- **Database**: PostgreSQL/PostGIS for spatial calculations and caching
- **Real-time**: Supabase subscriptions for live distance updates
- **Performance**: PostGIS spatial indexing for optimized queries
- **Cost Efficiency**: Intelligent caching to minimize Google Maps API costs

### **MCP Tool Integration Requirements**
- **Supabase MCP**: Primary database operations and real-time subscriptions
- **Google Maps Distance Matrix API**: Core distance calculation service
- **Context7 MCP**: Access to latest Google Maps API documentation
- **IDE MCP**: Development quality monitoring and performance tracking

## Technical Architecture

### **Core Components**
1. **Distance Calculation Service** (`src/lib/distance-calculation-service.ts`)
   - Google Maps Distance Matrix API integration
   - Intelligent rate limiting and error handling
   - Batch processing capabilities for route optimization

2. **Caching Layer** (`src/lib/distance-cache-service.ts`)
   - PostgreSQL-backed caching for cost optimization
   - 30-day cache expiration for traffic pattern changes
   - >80% cache hit rate target

3. **Pricing Calculation Engine** (`src/lib/pricing-calculation-service.ts`)
   - Exact LDP formula: (Roundtrip Minutes × 1.83) + Added Minutes
   - Total calculation: Dump Fee + Trucking Price/Load + LDP Fee
   - Manual adjustment support for Added Minutes (5-30 minutes)

4. **API Routes** (`src/app/api/distance/`)
   - `/calculate` - Single distance calculation
   - `/batch` - Batch processing for multiple routes
   - `/pricing` - LDP pricing calculations
   - `/cache` - Cache management operations

5. **Route Optimization Engine** (`src/lib/route-optimization-service.ts`)
   - Multi-point route optimization algorithms
   - Construction workflow priority (HOT permits first)
   - Cost-optimized routing for fuel and time efficiency

## Implementation Phases

### **Phase 1: Core Infrastructure** ⭐ **IMMEDIATE PRIORITY**

#### **Task 1.1: Database Schema Extensions**
**Responsibility**: Database Architect Agent
**Files**: Database migration scripts
**Dependencies**: Existing Supabase database service

```sql
-- Distance calculations caching table
CREATE TABLE distance_calculations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    origin_lat DECIMAL(10,8) NOT NULL,
    origin_lng DECIMAL(11,8) NOT NULL,
    destination_lat DECIMAL(10,8) NOT NULL,
    destination_lng DECIMAL(11,8) NOT NULL,
    distance_meters INTEGER,
    duration_seconds INTEGER,
    duration_in_traffic_seconds INTEGER,
    api_response JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    -- Composite index for cache lookups
    CONSTRAINT unique_route UNIQUE (origin_lat, origin_lng, destination_lat, destination_lng)
);

-- Spatial index for performance
CREATE INDEX idx_distance_calc_origin ON distance_calculations USING GIST(
    ST_Point(origin_lng, origin_lat)
);
CREATE INDEX idx_distance_calc_destination ON distance_calculations USING GIST(
    ST_Point(destination_lng, destination_lat)
);

-- Route optimization results
CREATE TABLE route_optimizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    permit_ids UUID[] NOT NULL,
    optimized_route JSONB NOT NULL,
    total_distance_meters INTEGER,
    total_duration_seconds INTEGER,
    optimization_type VARCHAR(50) DEFAULT 'shortest_time',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Extend permits table for distance-related fields
ALTER TABLE permits ADD COLUMN IF NOT EXISTS roundtrip_minutes INTEGER;
ALTER TABLE permits ADD COLUMN IF NOT EXISTS added_minutes INTEGER DEFAULT 0;
ALTER TABLE permits ADD COLUMN IF NOT EXISTS distance_to_depot_meters INTEGER;
ALTER TABLE permits ADD COLUMN IF NOT EXISTS last_distance_update TIMESTAMP WITH TIME ZONE;
```

#### **Task 1.2: Google Maps Distance Matrix Service**
**Responsibility**: Backend API Developer Agent
**File**: `src/lib/distance-calculation-service.ts`
**Dependencies**: Google Maps API key, existing geocoding service

**Implementation Pattern** (Following backend-api-developer.md):
```typescript
import { Client } from '@googlemaps/google-maps-services-js';
import { createClient } from '@/lib/supabase';

interface DistanceResult {
  distance_meters: number;
  duration_seconds: number;
  duration_in_traffic_seconds?: number;
  status: 'OK' | 'ZERO_RESULTS' | 'MAX_ROUTE_LENGTH_EXCEEDED' | 'INVALID_REQUEST';
  cached: boolean;
}

interface RouteRequest {
  origin: { lat: number; lng: number };
  destination: { lat: number; lng: number };
  permit_id?: string;
}

class DistanceCalculationService {
  private googleMapsClient: Client;
  private supabaseClient: any;
  private cacheService: DistanceCacheService;

  constructor() {
    this.googleMapsClient = new Client({});
    this.supabaseClient = createClient();
    this.cacheService = new DistanceCacheService();
  }

  async calculateDistance(
    origin: { lat: number; lng: number },
    destination: { lat: number; lng: number }
  ): Promise<DistanceResult> {
    // Check cache first (cost optimization)
    const cached = await this.cacheService.getCachedDistance(origin, destination);
    if (cached) {
      return { ...cached, cached: true };
    }

    // Google Maps Distance Matrix API call
    try {
      const response = await this.googleMapsClient.distancematrix({
        params: {
          origins: [`${origin.lat},${origin.lng}`],
          destinations: [`${destination.lat},${destination.lng}`],
          mode: 'driving',
          units: 'metric',
          departure_time: 'now',
          traffic_model: 'best_guess',
          key: process.env.GOOGLE_MAPS_API_KEY!,
        },
      });

      const element = response.data.rows[0]?.elements[0];
      if (!element || element.status !== 'OK') {
        throw new Error(`Distance calculation failed: ${element?.status}`);
      }

      const result: DistanceResult = {
        distance_meters: element.distance.value,
        duration_seconds: element.duration.value,
        duration_in_traffic_seconds: element.duration_in_traffic?.value,
        status: 'OK',
        cached: false,
      };

      // Cache the result
      await this.cacheService.cacheDistance(origin, destination, result);

      return result;
    } catch (error) {
      console.error('Distance calculation error:', error);
      throw error;
    }
  }

  async batchCalculateDistances(routes: RouteRequest[]): Promise<BatchDistanceResult> {
    // Implement batch processing with rate limiting
    // Maximum 25 origins or destinations per request (Google Maps limit)
    const batchSize = 25;
    const results: DistanceResult[] = [];
    
    for (let i = 0; i < routes.length; i += batchSize) {
      const batch = routes.slice(i, i + batchSize);
      const batchResults = await this.processBatch(batch);
      results.push(...batchResults);
      
      // Rate limiting: 50 requests per second max
      if (i + batchSize < routes.length) {
        await new Promise(resolve => setTimeout(resolve, 100));
      }
    }

    return {
      results,
      total_processed: results.length,
      cache_hits: results.filter(r => r.cached).length,
      api_calls: results.filter(r => !r.cached).length,
    };
  }
}
```

#### **Task 1.3: Intelligent Caching Mechanism**
**Responsibility**: Backend API Developer Agent
**File**: `src/lib/distance-cache-service.ts`
**Dependencies**: Supabase database service

**Caching Strategy**:
- Cache based on coordinate pairs (rounded to 6 decimal places for ~100m accuracy)
- 30-day cache expiration for traffic pattern changes
- Intelligent cache warming for frequently accessed routes
- Cost optimization target: >80% cache hit rate

### **Phase 2: API Integration** ⭐ **CORE FUNCTIONALITY**

#### **Task 2.1: Next.js API Routes**
**Responsibility**: Backend API Developer Agent
**Files**: 
- `src/app/api/distance/calculate/route.ts`
- `src/app/api/distance/batch/route.ts`
- `src/app/api/distance/pricing/route.ts`
- `src/app/api/distance/cache/route.ts`

**Pattern**: Following backend-api-developer.md Supabase integration patterns

#### **Task 2.2: LDP Pricing Formula Implementation**
**Responsibility**: Business Logic Agent
**File**: `src/lib/pricing-calculation-service.ts`
**Dependencies**: Distance calculation service, business logic patterns

**Exact Formula Implementation**:
```typescript
class PricingCalculationService {
  /**
   * Calculate trucking price using exact LDP formula
   * Formula: (Roundtrip Minutes × 1.83) + Added Minutes
   */
  calculateTruckingPrice(
    roundtripMinutes: number, 
    addedMinutes: number = 0
  ): number {
    return (roundtripMinutes * 1.83) + addedMinutes;
  }
  
  /**
   * Calculate total price per load
   * Formula: Dump Fee + Trucking Price/Load + LDP Fee
   */
  calculateTotalPrice(
    dumpFee: number,
    truckingPrice: number,
    ldpFee: number
  ): number {
    return dumpFee + truckingPrice + ldpFee;
  }

  /**
   * Update permit pricing based on distance calculations
   */
  async updatePermitPricing(
    siteNumber: string,
    distanceResult: DistanceResult,
    addedMinutes: number = 0,
    dumpFee: number = 0,
    ldpFee: number = 0
  ): Promise<boolean> {
    const roundtripMinutes = Math.ceil(distanceResult.duration_seconds / 60) * 2;
    const truckingPrice = this.calculateTruckingPrice(roundtripMinutes, addedMinutes);
    const totalPrice = this.calculateTotalPrice(dumpFee, truckingPrice, ldpFee);

    // Update permit in database using Supabase MCP
    const supabase = createClient();
    const { error } = await supabase
      .table('permits')
      .update({
        roundtrip_minutes: roundtripMinutes,
        added_minutes: addedMinutes,
        trucking_price_per_load: truckingPrice,
        total_price_per_load: totalPrice,
        last_distance_update: new Date().toISOString(),
      })
      .eq('site_number', siteNumber);

    return !error;
  }
}
```

### **Phase 3: Integration & Optimization** ⭐ **ADVANCED FEATURES**

#### **Task 3.1: Enhanced Geocoding Integration**
**Responsibility**: Data Engineer Agent
**File**: Extension of `scripts/san-diego-script/geocoding-scripts/enhanced_geocoding_service.py`
**Dependencies**: Existing geocoding service, distance calculation service

**Integration Pattern**:
- Add distance calculation pipeline to existing geocoding workflow
- Unified coordinate → distance → pricing pipeline
- Batch processing optimization for construction workflows

#### **Task 3.2: Route Optimization Engine**
**Responsibility**: Business Logic Agent
**File**: `src/lib/route-optimization-service.ts`
**Dependencies**: Distance calculation service, permit management

**Features**:
- Multi-point route optimization for construction workflows
- Priority-based routing (HOT permits first)
- Cost-optimized routing algorithms considering fuel and time
- Export capabilities for construction planning

## Prerequisites and Dependencies

### **Environment Variables Required**
```env
# New requirements for Distance Calculation System
GOOGLE_MAPS_API_KEY=your_distance_matrix_api_key

# Existing (already configured)
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
GEOCODIO_API_KEY=your_geocodio_key
```

### **API Quotas and Cost Management**
- **Google Maps Distance Matrix API**: $5 per 1,000 requests
- **Target Cache Hit Rate**: >80% to minimize costs
- **Estimated Monthly Cost**: $25-50 for typical construction workflows
- **Rate Limiting**: 50 requests per second maximum

### **Database Schema Modifications**
- Extend existing `permits` table with distance-related fields
- Add PostGIS spatial indexes for performance optimization
- Create caching and optimization tables

## Integration Points

### **Existing Service Integration**
1. **Enhanced Geocoding Service**: Extend for unified coordinate → distance pipeline
2. **Supabase Database Service**: Add distance calculation storage methods
3. **Frontend Components**: Real-time distance display integration
4. **Permit Management**: Automatic pricing updates via database triggers

### **Agent Coordination Requirements**
- **Database Architect**: Schema design and PostGIS optimization
- **Backend API Developer**: Google Maps integration and API routes
- **Business Logic Agent**: LDP pricing formula and permit workflows
- **Data Engineer**: Geocoding service integration and batch processing

## Performance Requirements

### **Response Time Targets**
- **Single Distance Calculation**: Sub-2 seconds
- **Batch Operations**: Sub-10 seconds (up to 25 permits)
- **Cache Lookup**: Sub-100ms
- **Database Updates**: Sub-500ms

### **Optimization Targets**
- **Cache Hit Rate**: >80% for cost optimization
- **API Cost Reduction**: >75% through intelligent caching
- **Concurrent Processing**: Support 10+ simultaneous calculations
- **Error Rate**: <1% for production reliability

## Testing Strategy

### **Validation Requirements**
- **Distance Accuracy**: Within construction industry standards (±2%)
- **LDP Formula Accuracy**: Exact implementation validation
- **Performance Benchmarks**: Meet all response time targets
- **Cost Optimization**: Achieve cache hit rate targets

### **Test Coverage Areas**
- Unit tests for distance calculations and pricing formulas
- Integration tests with Google Maps API and Supabase
- Performance tests for batch processing and caching
- End-to-end workflow validation from geocoding to pricing

## Success Criteria

✅ **Functional Requirements**:
- Accurate distance calculations between permit sites
- Exact LDP pricing formula implementation: (Roundtrip Minutes × 1.83) + Added Minutes
- Intelligent caching with >80% hit rate for cost optimization
- Batch processing for route optimization (up to 25 permits)

✅ **Performance Requirements**:
- Sub-2 second response times for single calculations
- Sub-10 second response times for batch operations
- >80% cache hit rate for cost optimization
- Support for concurrent operations

✅ **Integration Requirements**:
- Seamless integration with existing geocoding service
- Direct-to-Supabase architecture compliance
- Real-time pricing updates via database triggers
- Frontend integration for live distance display

✅ **Business Requirements**:
- Construction industry workflow support
- Municipal permit compliance across 35-40 cities
- Route optimization for construction planning
- Export capabilities for quote sheet generation

## Implementation Notes

### **Agent Documentation References**
This implementation follows patterns established in:
- `backend-api-developer.md`: Google Maps API integration and Supabase patterns
- `business-logic-agent.md`: LDP pricing formula and construction workflows
- `database-architect.md`: PostGIS optimization and Direct-to-Supabase architecture
- `data-engineer.md`: Batch processing and geocoding integration

### **MCP Tool Integration**
- **Supabase MCP**: All database operations and real-time subscriptions
- **Google Maps API**: Distance Matrix calculations and route optimization
- **Context7 MCP**: Access to latest API documentation and best practices
- **IDE MCP**: Development quality monitoring and performance tracking

This documentation serves as the complete reference for implementing the Distance Calculation System following established agent patterns and architectural standards.
