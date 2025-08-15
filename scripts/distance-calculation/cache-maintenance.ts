#!/usr/bin/env tsx
/**
 * Distance Cache Maintenance Script
 * 
 * Automated cache optimization and cleanup for the Distance Calculation System
 * 
 * Implementation following:
 * - Docs/distance-calculation-system/README.md
 * - Docs/distance-calculation-system/technical-specifications.md
 * 
 * Features:
 * - Automated expired cache cleanup
 * - Cache performance monitoring
 * - Cache warming for frequent routes
 * - Cost optimization reporting
 */

import { createDistanceCacheService } from '../../src/lib/distance-cache-service';
import { createClient } from '../../src/lib/supabase';

interface MaintenanceReport {
  timestamp: string;
  expired_entries_cleaned: number;
  total_cache_entries: number;
  cache_hit_rate: number;
  storage_size_mb: number;
  estimated_monthly_savings: number;
  recommendations: string[];
}

/**
 * Cache Maintenance Service
 * 
 * Implements automated cache optimization following cost optimization targets
 */
class CacheMaintenanceService {
  private cacheService = createDistanceCacheService();
  private supabaseClient = createClient();

  /**
   * Run complete cache maintenance cycle
   */
  async runMaintenance(): Promise<MaintenanceReport> {
    console.log('🔧 Starting cache maintenance cycle...');
    const startTime = Date.now();

    const report: MaintenanceReport = {
      timestamp: new Date().toISOString(),
      expired_entries_cleaned: 0,
      total_cache_entries: 0,
      cache_hit_rate: 0,
      storage_size_mb: 0,
      estimated_monthly_savings: 0,
      recommendations: [],
    };

    try {
      // Step 1: Clean up expired entries
      console.log('🧹 Cleaning up expired cache entries...');
      report.expired_entries_cleaned = await this.cacheService.cleanupExpiredCache();

      // Step 2: Get cache statistics
      console.log('📊 Gathering cache statistics...');
      const stats = await this.cacheService.getCacheStats();
      report.total_cache_entries = stats.total_entries;
      report.cache_hit_rate = stats.cache_hit_rate_24h;
      report.storage_size_mb = stats.storage_size_mb;

      // Step 3: Calculate cost savings
      console.log('💰 Calculating cost savings...');
      const performance = this.cacheService.getCachePerformance();
      const monthlySavings = this.calculateMonthlySavings(performance.hit_rate, performance.total_lookups);
      report.estimated_monthly_savings = monthlySavings;

      // Step 4: Generate recommendations
      console.log('💡 Generating optimization recommendations...');
      report.recommendations = this.generateRecommendations(stats, performance);

      // Step 5: Warm cache with frequent routes
      console.log('🔥 Warming cache with frequent routes...');
      await this.warmFrequentRoutes();

      const duration = Date.now() - startTime;
      console.log(`✅ Cache maintenance completed in ${duration}ms`);

      return report;
    } catch (error) {
      console.error('❌ Cache maintenance failed:', error);
      throw error;
    }
  }

  /**
   * Calculate estimated monthly savings from caching
   */
  private calculateMonthlySavings(hitRate: number, totalLookups: number): number {
    // Google Maps API cost: $5 per 1,000 requests
    const apiCostPer1000 = 5;
    const estimatedMonthlyLookups = totalLookups * 30; // Extrapolate daily to monthly
    const savedRequests = (estimatedMonthlyLookups * hitRate) / 100;
    const savings = (savedRequests / 1000) * apiCostPer1000;
    
    return Math.round(savings * 100) / 100; // Round to 2 decimal places
  }

  /**
   * Generate optimization recommendations based on cache performance
   */
  private generateRecommendations(stats: any, performance: any): string[] {
    const recommendations: string[] = [];

    // Cache hit rate recommendations
    if (performance.hit_rate < 80) {
      recommendations.push(
        `Cache hit rate (${performance.hit_rate.toFixed(1)}%) is below target (80%). Consider cache warming for frequent routes.`
      );
    } else {
      recommendations.push(
        `Excellent cache hit rate (${performance.hit_rate.toFixed(1)}%). Cost optimization target achieved.`
      );
    }

    // Storage optimization
    if (stats.storage_size_mb > 100) {
      recommendations.push(
        `Cache storage (${stats.storage_size_mb.toFixed(1)}MB) is high. Consider reducing cache expiration time.`
      );
    }

    // Expired entries
    if (stats.expired_entries > stats.total_entries * 0.1) {
      recommendations.push(
        `High number of expired entries (${stats.expired_entries}). Increase cleanup frequency.`
      );
    }

    // Performance recommendations
    if (performance.total_lookups > 1000) {
      recommendations.push(
        `High lookup volume (${performance.total_lookups}). Consider implementing cache warming strategies.`
      );
    }

    return recommendations;
  }

  /**
   * Warm cache with frequently accessed routes
   */
  private async warmFrequentRoutes(): Promise<void> {
    if (!this.supabaseClient) {
      console.warn('⚠️ Supabase client not available. Skipping cache warming.');
      return;
    }

    try {
      // Get permits with coordinates for cache warming
      const { data: permits, error } = await this.supabaseClient
        .from('permits')
        .select('latitude, longitude, project_city')
        .not('latitude', 'is', null)
        .not('longitude', 'is', null)
        .limit(50); // Top 50 permits for warming

      if (error || !permits) {
        console.warn('⚠️ Failed to get permits for cache warming:', error);
        return;
      }

      // Create route pairs for common depot locations
      const commonDepots = [
        { lat: 32.7157, lng: -117.1611 }, // San Diego
        { lat: 34.0522, lng: -118.2437 }, // Los Angeles
        { lat: 33.6846, lng: -117.8265 }, // Orange County
      ];

      const routes = [];
      for (const permit of permits) {
        for (const depot of commonDepots) {
          routes.push({
            origin: depot,
            destination: { lat: permit.latitude, lng: permit.longitude },
          });
        }
      }

      await this.cacheService.warmCache(routes);
      console.log(`🔥 Cache warming completed for ${routes.length} routes`);
    } catch (error) {
      console.warn('⚠️ Cache warming failed:', error);
    }
  }

  /**
   * Generate detailed maintenance report
   */
  async generateDetailedReport(): Promise<void> {
    const report = await this.runMaintenance();
    
    console.log('\n📋 CACHE MAINTENANCE REPORT');
    console.log('================================');
    console.log(`Timestamp: ${report.timestamp}`);
    console.log(`Expired entries cleaned: ${report.expired_entries_cleaned}`);
    console.log(`Total cache entries: ${report.total_cache_entries}`);
    console.log(`Cache hit rate: ${report.cache_hit_rate.toFixed(1)}%`);
    console.log(`Storage size: ${report.storage_size_mb.toFixed(1)}MB`);
    console.log(`Estimated monthly savings: $${report.estimated_monthly_savings}`);
    console.log('\n💡 RECOMMENDATIONS:');
    report.recommendations.forEach((rec, index) => {
      console.log(`${index + 1}. ${rec}`);
    });
    console.log('================================\n');
  }
}

/**
 * CLI interface for cache maintenance
 */
async function main() {
  const args = process.argv.slice(2);
  const command = args[0] || 'maintenance';

  const maintenanceService = new CacheMaintenanceService();

  try {
    switch (command) {
      case 'maintenance':
      case 'run':
        await maintenanceService.generateDetailedReport();
        break;
      
      case 'cleanup':
        console.log('🧹 Running cache cleanup only...');
        const cacheService = createDistanceCacheService();
        const cleaned = await cacheService.cleanupExpiredCache();
        console.log(`✅ Cleaned up ${cleaned} expired entries`);
        break;
      
      case 'stats':
        console.log('📊 Getting cache statistics...');
        const statsService = createDistanceCacheService();
        const stats = await statsService.getCacheStats();
        const performance = statsService.getCachePerformance();
        
        console.log('\n📊 CACHE STATISTICS');
        console.log('==================');
        console.log(`Total entries: ${stats.total_entries}`);
        console.log(`Cache hit rate (24h): ${stats.cache_hit_rate_24h.toFixed(1)}%`);
        console.log(`Expired entries: ${stats.expired_entries}`);
        console.log(`Storage size: ${stats.storage_size_mb.toFixed(1)}MB`);
        console.log(`Session hits: ${performance.hits}`);
        console.log(`Session misses: ${performance.misses}`);
        console.log(`Session hit rate: ${performance.hit_rate.toFixed(1)}%`);
        console.log('==================\n');
        break;
      
      default:
        console.log('Usage: tsx cache-maintenance.ts [command]');
        console.log('Commands:');
        console.log('  maintenance, run  - Run complete maintenance cycle (default)');
        console.log('  cleanup          - Clean up expired entries only');
        console.log('  stats           - Show cache statistics');
        break;
    }
  } catch (error) {
    console.error('❌ Cache maintenance failed:', error);
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  main();
}

export { CacheMaintenanceService };
