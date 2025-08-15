/**
 * Distance Calculation API Route - LDP Pricing Calculation
 * 
 * Implementation following:
 * - Context7 MCP Research: Next.js 15 API route patterns and TypeScript integration
 * - Exa MCP Research: Construction industry pricing API best practices
 * - Docs/distance-calculation-system/README.md and technical-specifications.md
 * - .augment/agents/business-logic-agent.md (exact LDP pricing formula)
 * 
 * Features:
 * - Exact LDP pricing formula: (Roundtrip Minutes × 1.83) + Added Minutes
 * - Total calculation: Dump Fee + Trucking Price/Load + LDP Fee
 * - Permit database updates via Supabase integration
 * - Comprehensive validation and error handling
 * - Integration with Phase 1 distance calculation infrastructure
 */

import { NextRequest, NextResponse } from 'next/server';
import { createPricingCalculationService } from '@/lib/pricing-calculation-service';
import type { PricingCalculationRequest } from '@/lib/pricing-calculation-service';

// Types following technical-specifications.md
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

/**
 * POST /api/distance/pricing
 * 
 * Calculate LDP pricing based on distance calculations
 * 
 * Following Context7 MCP research: Next.js 15 async processing and validation
 * Following Exa MCP research: Construction industry pricing calculation standards
 */
export async function POST(request: NextRequest): Promise<NextResponse<PricingCalculationResponse>> {
  const startTime = Date.now();
  
  try {
    // Parse and validate request body
    let body: PricingCalculationRequest;
    
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

    // Validate pricing calculation request
    const validationError = validatePricingCalculationRequest(body);
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

    // Initialize pricing calculation service
    const pricingService = createPricingCalculationService();

    // Log pricing calculation start
    console.log(`💰 Starting LDP pricing calculation for permit ${body.site_number}...`);

    // Calculate pricing with error handling
    const result = await pricingService.updatePermitPricing(body);

    const processingTime = Date.now() - startTime;

    // Log successful pricing calculation
    console.log(`✅ LDP pricing calculation completed (${processingTime}ms):`, {
      site_number: result.site_number,
      trucking_price: result.trucking_price_per_load,
      total_price: result.total_price_per_load,
      permit_updated: result.permit_updated,
    });

    return NextResponse.json(
      {
        success: true,
        data: result,
        processing_time_ms: processingTime,
      },
      { status: 200 }
    );

  } catch (error) {
    const processingTime = Date.now() - startTime;
    
    // Log error for monitoring
    console.error('❌ LDP pricing calculation failed:', error);

    // Handle specific error types
    if (error instanceof Error) {
      // Distance calculation errors
      if (error.message.includes('Distance calculation failed') || 
          error.message.includes('Unable to calculate distance')) {
        return NextResponse.json(
          {
            success: false,
            error: 'Unable to calculate distance for pricing. Please verify coordinates.',
            processing_time_ms: processingTime,
          },
          { status: 422 }
        );
      }

      // Pricing formula errors
      if (error.message.includes('Roundtrip minutes') || 
          error.message.includes('Added minutes') ||
          error.message.includes('pricing components')) {
        return NextResponse.json(
          {
            success: false,
            error: error.message,
            processing_time_ms: processingTime,
          },
          { status: 400 }
        );
      }

      // Database update errors
      if (error.message.includes('Failed to update permit') || 
          error.message.includes('Database update failed')) {
        return NextResponse.json(
          {
            success: false,
            error: 'Pricing calculated successfully but permit update failed. Please try again.',
            processing_time_ms: processingTime,
          },
          { status: 207 } // Multi-status: partial success
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
      if (error.message.includes('coordinates must be provided') ||
          error.message.includes('Invalid')) {
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
        error: 'Internal server error occurred during pricing calculation',
        processing_time_ms: processingTime,
      },
      { status: 500 }
    );
  }
}

/**
 * GET /api/distance/pricing
 * 
 * Get LDP pricing formula information and calculation capabilities
 * Following Exa MCP research: API documentation and capability discovery
 */
export async function GET(): Promise<NextResponse> {
  try {
    return NextResponse.json(
      {
        success: true,
        service: 'LDP Pricing Calculation API',
        formula: {
          trucking_price: '(Roundtrip Minutes × 1.83) + Added Minutes',
          total_price: 'Dump Fee + Trucking Price/Load + LDP Fee',
          description: 'Exact LDP pricing formula for construction industry workflows',
        },
        parameters: {
          roundtrip_minutes: {
            description: 'Calculated from drive time duration (seconds / 60 * 2)',
            type: 'number',
            minimum: 0,
          },
          added_minutes: {
            description: 'Additional minutes for loading/unloading operations',
            type: 'number',
            minimum: 0,
            maximum: 30,
            default: 0,
          },
          dump_fee: {
            description: 'Fee charged by dump site',
            type: 'number',
            minimum: 0,
            default: 0,
          },
          ldp_fee: {
            description: 'LDP (Load Delivery Point) fee',
            type: 'number',
            minimum: 0,
            default: 0,
          },
        },
        capabilities: {
          distance_integration: true,
          permit_updates: true,
          batch_processing: false, // Future enhancement
          real_time_calculation: true,
        },
        examples: {
          basic_calculation: {
            roundtrip_minutes: 60,
            added_minutes: 10,
            trucking_price: '(60 × 1.83) + 10 = 119.8',
          },
          full_pricing: {
            dump_fee: 25.0,
            trucking_price: 119.8,
            ldp_fee: 15.0,
            total_price: '25.0 + 119.8 + 15.0 = 159.8',
          },
        },
        timestamp: new Date().toISOString(),
      },
      { status: 200 }
    );
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        service: 'LDP Pricing Calculation API',
        status: 'unhealthy',
        error: 'Service information retrieval failed',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    );
  }
}

/**
 * Validate pricing calculation request
 * Following Exa MCP research: Construction industry data validation patterns
 */
function validatePricingCalculationRequest(body: any): string | null {
  // Check if body exists
  if (!body || typeof body !== 'object') {
    return 'Request body is required and must be a valid object';
  }

  // Validate site_number (required)
  if (!body.site_number || typeof body.site_number !== 'string') {
    return 'Site number is required and must be a string';
  }

  if (body.site_number.trim().length === 0) {
    return 'Site number cannot be empty';
  }

  // Validate pricing_params (required)
  if (!body.pricing_params || typeof body.pricing_params !== 'object') {
    return 'Pricing parameters are required';
  }

  // Validate added_minutes if provided
  if (body.pricing_params.added_minutes !== undefined) {
    if (typeof body.pricing_params.added_minutes !== 'number') {
      return 'Added minutes must be a number';
    }
    if (body.pricing_params.added_minutes < 0 || body.pricing_params.added_minutes > 30) {
      return 'Added minutes must be between 0 and 30';
    }
  }

  // Validate dump_fee if provided
  if (body.pricing_params.dump_fee !== undefined) {
    if (typeof body.pricing_params.dump_fee !== 'number') {
      return 'Dump fee must be a number';
    }
    if (body.pricing_params.dump_fee < 0) {
      return 'Dump fee cannot be negative';
    }
  }

  // Validate ldp_fee if provided
  if (body.pricing_params.ldp_fee !== undefined) {
    if (typeof body.pricing_params.ldp_fee !== 'number') {
      return 'LDP fee must be a number';
    }
    if (body.pricing_params.ldp_fee < 0) {
      return 'LDP fee cannot be negative';
    }
  }

  // Validate distance data source (either coordinates or distance_data required)
  const hasCoordinates = body.origin && body.destination;
  const hasDistanceData = body.distance_data;

  if (!hasCoordinates && !hasDistanceData) {
    return 'Either origin/destination coordinates or distance_data must be provided';
  }

  // Validate coordinates if provided
  if (hasCoordinates) {
    // Validate origin
    if (typeof body.origin.lat !== 'number' || typeof body.origin.lng !== 'number') {
      return 'Origin coordinates must have numeric lat and lng properties';
    }
    if (body.origin.lat < -90 || body.origin.lat > 90) {
      return 'Origin latitude must be between -90 and 90';
    }
    if (body.origin.lng < -180 || body.origin.lng > 180) {
      return 'Origin longitude must be between -180 and 180';
    }

    // Validate destination
    if (typeof body.destination.lat !== 'number' || typeof body.destination.lng !== 'number') {
      return 'Destination coordinates must have numeric lat and lng properties';
    }
    if (body.destination.lat < -90 || body.destination.lat > 90) {
      return 'Destination latitude must be between -90 and 90';
    }
    if (body.destination.lng < -180 || body.destination.lng > 180) {
      return 'Destination longitude must be between -180 and 180';
    }
  }

  // Validate distance_data if provided
  if (hasDistanceData) {
    if (typeof body.distance_data.duration_seconds !== 'number' || 
        body.distance_data.duration_seconds <= 0) {
      return 'Distance data duration_seconds must be a positive number';
    }
    if (typeof body.distance_data.distance_meters !== 'number' || 
        body.distance_data.distance_meters <= 0) {
      return 'Distance data distance_meters must be a positive number';
    }
  }

  // Validate update_permit if provided
  if (body.update_permit !== undefined && typeof body.update_permit !== 'boolean') {
    return 'Update permit flag must be a boolean';
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
