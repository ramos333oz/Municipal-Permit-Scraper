/**
 * Distance Calculation API Route - Single Distance Calculation
 * 
 * Implementation following:
 * - Context7 MCP Research: Next.js 15 API route patterns and TypeScript integration
 * - Exa MCP Research: Current industry best practices for error handling and validation
 * - Docs/distance-calculation-system/README.md and technical-specifications.md
 * - .augment/agents/backend-api-developer.md patterns
 * 
 * Features:
 * - Next.js 15 Route Handler with async Request APIs
 * - TypeScript integration with proper type safety
 * - Comprehensive error handling and validation
 * - Integration with Phase 1 core infrastructure
 * - Cost optimization through intelligent caching
 * - Performance monitoring and logging
 */

import { NextRequest, NextResponse } from 'next/server';
import { createDistanceCalculationService } from '@/lib/distance-calculation-service';
import type { Coordinates, DistanceOptions } from '@/lib/distance-calculation-service';

// Types following technical-specifications.md
interface CalculateDistanceRequest {
  origin: Coordinates;
  destination: Coordinates;
  options?: DistanceOptions;
}

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

/**
 * POST /api/distance/calculate
 * 
 * Calculate distance between two points using Google Maps Distance Matrix API
 * with intelligent caching for cost optimization
 * 
 * Following Context7 MCP research: Next.js 15 async Request APIs and error handling patterns
 * Following Exa MCP research: Industry best practices for API validation and response formatting
 */
export async function POST(request: NextRequest): Promise<NextResponse<CalculateDistanceResponse>> {
  const startTime = Date.now();
  
  try {
    // Parse and validate request body following Next.js 15 patterns
    let body: CalculateDistanceRequest;
    
    try {
      body = await request.json();
    } catch (error) {
      return NextResponse.json(
        {
          success: false,
          error: 'Invalid JSON in request body',
          processing_time_ms: Date.now() - startTime,
        },
        { status: 400 }
      );
    }

    // Validate required fields
    const validationError = validateCalculateDistanceRequest(body);
    if (validationError) {
      return NextResponse.json(
        {
          success: false,
          error: validationError,
          processing_time_ms: Date.now() - startTime,
        },
        { status: 400 }
      );
    }

    // Initialize distance calculation service (Phase 1 integration)
    const distanceService = createDistanceCalculationService();

    // Calculate distance with error handling
    const result = await distanceService.calculateDistance(
      body.origin,
      body.destination,
      body.options || {}
    );

    const processingTime = Date.now() - startTime;

    // Log successful calculation for monitoring
    console.log(`✅ Distance calculation successful (${processingTime}ms):`, {
      origin: body.origin,
      destination: body.destination,
      distance_meters: result.distance_meters,
      cached: result.cached,
    });

    return NextResponse.json(
      {
        success: true,
        data: {
          distance_meters: result.distance_meters,
          duration_seconds: result.duration_seconds,
          duration_in_traffic_seconds: result.duration_in_traffic_seconds,
          cached: result.cached,
          cache_age_minutes: result.cache_age_minutes,
        },
        processing_time_ms: processingTime,
      },
      { status: 200 }
    );

  } catch (error) {
    const processingTime = Date.now() - startTime;
    
    // Log error for monitoring
    console.error('❌ Distance calculation failed:', error);

    // Handle specific error types
    if (error instanceof Error) {
      // Google Maps API errors
      if (error.message.includes('Distance calculation failed')) {
        return NextResponse.json(
          {
            success: false,
            error: 'Unable to calculate distance between the specified locations',
            processing_time_ms: processingTime,
          },
          { status: 422 }
        );
      }

      // Rate limiting errors
      if (error.message.includes('rate limit') || error.message.includes('quota')) {
        return NextResponse.json(
          {
            success: false,
            error: 'Service temporarily unavailable due to rate limiting',
            processing_time_ms: processingTime,
          },
          { status: 429 }
        );
      }

      // Validation errors
      if (error.message.includes('Invalid')) {
        return NextResponse.json(
          {
            success: false,
            error: error.message,
            processing_time_ms: processingTime,
          },
          { status: 400 }
        );
      }
    }

    // Generic server error
    return NextResponse.json(
      {
        success: false,
        error: 'Internal server error occurred during distance calculation',
        processing_time_ms: processingTime,
      },
      { status: 500 }
    );
  }
}

/**
 * GET /api/distance/calculate
 * 
 * Health check endpoint for distance calculation service
 * Following Exa MCP research: API health check best practices
 */
export async function GET(): Promise<NextResponse> {
  try {
    // Check if Google Maps API key is configured
    const apiKeyConfigured = !!process.env.GOOGLE_MAPS_API_KEY;
    
    return NextResponse.json(
      {
        success: true,
        service: 'Distance Calculation API',
        status: 'healthy',
        features: {
          single_calculation: true,
          caching: true,
          rate_limiting: true,
          google_maps_api: apiKeyConfigured,
        },
        timestamp: new Date().toISOString(),
      },
      { status: 200 }
    );
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        service: 'Distance Calculation API',
        status: 'unhealthy',
        error: 'Service health check failed',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    );
  }
}

/**
 * Validate calculate distance request
 * Following Exa MCP research: Comprehensive input validation patterns
 */
function validateCalculateDistanceRequest(body: any): string | null {
  // Check if body exists
  if (!body || typeof body !== 'object') {
    return 'Request body is required and must be a valid object';
  }

  // Validate origin coordinates
  if (!body.origin || typeof body.origin !== 'object') {
    return 'Origin coordinates are required';
  }

  if (typeof body.origin.lat !== 'number' || typeof body.origin.lng !== 'number') {
    return 'Origin coordinates must have numeric lat and lng properties';
  }

  if (body.origin.lat < -90 || body.origin.lat > 90) {
    return 'Origin latitude must be between -90 and 90';
  }

  if (body.origin.lng < -180 || body.origin.lng > 180) {
    return 'Origin longitude must be between -180 and 180';
  }

  // Validate destination coordinates
  if (!body.destination || typeof body.destination !== 'object') {
    return 'Destination coordinates are required';
  }

  if (typeof body.destination.lat !== 'number' || typeof body.destination.lng !== 'number') {
    return 'Destination coordinates must have numeric lat and lng properties';
  }

  if (body.destination.lat < -90 || body.destination.lat > 90) {
    return 'Destination latitude must be between -90 and 90';
  }

  if (body.destination.lng < -180 || body.destination.lng > 180) {
    return 'Destination longitude must be between -180 and 180';
  }

  // Validate options if provided
  if (body.options && typeof body.options !== 'object') {
    return 'Options must be a valid object';
  }

  if (body.options?.traffic_model && 
      !['best_guess', 'pessimistic', 'optimistic'].includes(body.options.traffic_model)) {
    return 'Traffic model must be one of: best_guess, pessimistic, optimistic';
  }

  if (body.options?.departure_time && typeof body.options.departure_time !== 'string') {
    return 'Departure time must be a valid ISO 8601 string';
  }

  return null; // No validation errors
}

/**
 * OPTIONS handler for CORS support
 * Following Context7 MCP research: Next.js 15 CORS handling patterns
 */
export async function OPTIONS(): Promise<NextResponse> {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}
