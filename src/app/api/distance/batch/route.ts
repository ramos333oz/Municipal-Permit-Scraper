/**
 * Distance Calculation API Route - Batch Distance Calculation
 * 
 * Implementation following:
 * - Context7 MCP Research: Next.js 15 API route patterns and concurrent processing
 * - Exa MCP Research: Current industry best practices for batch processing and performance optimization
 * - Docs/distance-calculation-system/README.md and technical-specifications.md
 * - .augment/agents/backend-api-developer.md patterns
 * 
 * Features:
 * - Batch processing with 25-route Google Maps API limits
 * - Concurrent processing with configurable limits
 * - Progress tracking and cost optimization
 * - Comprehensive error handling and validation
 * - Integration with Phase 1 core infrastructure
 */

import { NextRequest, NextResponse } from 'next/server';
import { createDistanceCalculationService } from '@/lib/distance-calculation-service';
import type { RouteRequest, BatchOptions } from '@/lib/distance-calculation-service';

// Types following technical-specifications.md
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

/**
 * POST /api/distance/batch
 * 
 * Calculate distances for multiple routes with batch processing optimization
 * 
 * Following Context7 MCP research: Next.js 15 async processing and error handling
 * Following Exa MCP research: Industry best practices for batch API design and performance
 */
export async function POST(request: NextRequest): Promise<NextResponse<BatchDistanceResponse>> {
  const startTime = Date.now();
  
  try {
    // Parse and validate request body
    let body: BatchDistanceRequest;
    
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

    // Validate batch request
    const validationError = validateBatchDistanceRequest(body);
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

    // Convert request format to service format
    const routes: RouteRequest[] = body.routes.map(route => ({
      id: route.id,
      origin: route.origin,
      destination: route.destination,
      permit_id: route.permit_id,
    }));

    const batchOptions: BatchOptions = {
      use_cache: body.options?.use_cache,
      max_concurrent: body.options?.max_concurrent || 5,
      traffic_model: body.options?.traffic_model || 'best_guess',
    };

    // Log batch processing start
    console.log(`🚀 Starting batch distance calculation for ${routes.length} routes...`);

    // Execute batch calculation with error handling
    const result = await distanceService.batchCalculateDistances(routes, batchOptions);

    const processingTime = Date.now() - startTime;

    // Log successful batch processing
    console.log(`✅ Batch distance calculation completed (${processingTime}ms):`, {
      total_routes: routes.length,
      successful: result.summary.successful,
      failed: result.summary.failed,
      cache_hits: result.summary.cache_hits,
      api_calls: result.summary.api_calls,
      cost_estimate: result.summary.total_cost_estimate,
    });

    return NextResponse.json(
      {
        success: true,
        data: {
          results: result.results,
          summary: result.summary,
        },
        processing_time_ms: processingTime,
      },
      { status: 200 }
    );

  } catch (error) {
    const processingTime = Date.now() - startTime;
    
    // Log error for monitoring
    console.error('❌ Batch distance calculation failed:', error);

    // Handle specific error types
    if (error instanceof Error) {
      // Rate limiting errors
      if (error.message.includes('rate limit') || error.message.includes('quota')) {
        return NextResponse.json(
          {
            success: false,
            error: 'Service temporarily unavailable due to rate limiting. Please reduce batch size or try again later.',
            processing_time_ms: processingTime,
          },
          { status: 429 }
        );
      }

      // Timeout errors
      if (error.message.includes('timeout')) {
        return NextResponse.json(
          {
            success: false,
            error: 'Batch processing timed out. Please reduce batch size and try again.',
            processing_time_ms: processingTime,
          },
          { status: 408 }
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
        error: 'Internal server error occurred during batch distance calculation',
        processing_time_ms: processingTime,
      },
      { status: 500 }
    );
  }
}

/**
 * GET /api/distance/batch
 * 
 * Get batch processing capabilities and limits
 * Following Exa MCP research: API capability discovery patterns
 */
export async function GET(): Promise<NextResponse> {
  try {
    return NextResponse.json(
      {
        success: true,
        service: 'Batch Distance Calculation API',
        capabilities: {
          max_routes_per_batch: 100, // Recommended limit
          max_concurrent_processing: 10,
          supported_traffic_models: ['best_guess', 'pessimistic', 'optimistic'],
          caching_enabled: true,
          cost_estimation: true,
        },
        limits: {
          google_maps_batch_size: 25, // Google Maps API limit
          recommended_batch_size: 50, // For optimal performance
          max_processing_time_seconds: 300, // 5 minutes
        },
        pricing: {
          google_maps_cost_per_1000_requests: 5.0, // USD
          estimated_cache_hit_rate: 80, // Percentage
        },
        timestamp: new Date().toISOString(),
      },
      { status: 200 }
    );
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        service: 'Batch Distance Calculation API',
        status: 'unhealthy',
        error: 'Service capability check failed',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    );
  }
}

/**
 * Validate batch distance request
 * Following Exa MCP research: Comprehensive batch validation patterns
 */
function validateBatchDistanceRequest(body: any): string | null {
  // Check if body exists
  if (!body || typeof body !== 'object') {
    return 'Request body is required and must be a valid object';
  }

  // Validate routes array
  if (!body.routes || !Array.isArray(body.routes)) {
    return 'Routes array is required';
  }

  if (body.routes.length === 0) {
    return 'At least one route is required';
  }

  if (body.routes.length > 100) {
    return 'Maximum 100 routes allowed per batch request';
  }

  // Validate each route
  for (let i = 0; i < body.routes.length; i++) {
    const route = body.routes[i];
    
    if (!route || typeof route !== 'object') {
      return `Route ${i + 1} must be a valid object`;
    }

    // Validate origin
    if (!route.origin || typeof route.origin !== 'object') {
      return `Route ${i + 1}: Origin coordinates are required`;
    }

    if (typeof route.origin.lat !== 'number' || typeof route.origin.lng !== 'number') {
      return `Route ${i + 1}: Origin coordinates must have numeric lat and lng properties`;
    }

    if (route.origin.lat < -90 || route.origin.lat > 90) {
      return `Route ${i + 1}: Origin latitude must be between -90 and 90`;
    }

    if (route.origin.lng < -180 || route.origin.lng > 180) {
      return `Route ${i + 1}: Origin longitude must be between -180 and 180`;
    }

    // Validate destination
    if (!route.destination || typeof route.destination !== 'object') {
      return `Route ${i + 1}: Destination coordinates are required`;
    }

    if (typeof route.destination.lat !== 'number' || typeof route.destination.lng !== 'number') {
      return `Route ${i + 1}: Destination coordinates must have numeric lat and lng properties`;
    }

    if (route.destination.lat < -90 || route.destination.lat > 90) {
      return `Route ${i + 1}: Destination latitude must be between -90 and 90`;
    }

    if (route.destination.lng < -180 || route.destination.lng > 180) {
      return `Route ${i + 1}: Destination longitude must be between -180 and 180`;
    }

    // Validate optional fields
    if (route.id && typeof route.id !== 'string') {
      return `Route ${i + 1}: ID must be a string`;
    }

    if (route.permit_id && typeof route.permit_id !== 'string') {
      return `Route ${i + 1}: Permit ID must be a string`;
    }
  }

  // Validate options if provided
  if (body.options && typeof body.options !== 'object') {
    return 'Options must be a valid object';
  }

  if (body.options?.max_concurrent && 
      (typeof body.options.max_concurrent !== 'number' || 
       body.options.max_concurrent < 1 || 
       body.options.max_concurrent > 10)) {
    return 'Max concurrent must be a number between 1 and 10';
  }

  if (body.options?.traffic_model && 
      !['best_guess', 'pessimistic', 'optimistic'].includes(body.options.traffic_model)) {
    return 'Traffic model must be one of: best_guess, pessimistic, optimistic';
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
