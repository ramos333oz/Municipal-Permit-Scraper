#!/usr/bin/env python3
"""
Database Monitoring and Quality Assurance Service
Implements comprehensive monitoring as specified in agent documentation

Based on:
- .claude/agents/data-engineer.md (Data quality monitoring)
- .claude/agents/backend-api-developer.md (Production monitoring)
- .claude/agents/database-architect.md (Performance monitoring)

Features:
- Real-time data quality monitoring
- Performance tracking and optimization
- Audit logging and compliance
- Error detection and alerting
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import statistics

from supabase_database_service import SupabaseDatabaseService, create_database_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class QualityReport:
    """Data quality assessment report"""
    pipeline_name: str
    total_records: int
    success_rate: float
    geocoding_success_rate: float
    avg_processing_time_ms: float
    error_count: int
    recommendations: List[str]
    timestamp: str

@dataclass
class PerformanceMetrics:
    """Database performance metrics"""
    avg_query_time_ms: float
    total_operations: int
    success_rate: float
    error_rate: float
    peak_processing_time_ms: float
    recommendations: List[str]

class DatabaseMonitoringService:
    """
    Comprehensive database monitoring and quality assurance service
    
    Implements:
    - Real-time quality monitoring
    - Performance tracking
    - Audit trail analysis
    - Automated recommendations
    - Alert generation
    """
    
    def __init__(self):
        """Initialize monitoring service"""
        self.db_service = create_database_service()
        self.quality_thresholds = {
            'min_success_rate': 0.95,  # 95% minimum success rate
            'max_processing_time_ms': 5000,  # 5 second max processing time
            'min_geocoding_rate': 0.90,  # 90% minimum geocoding success
            'max_error_rate': 0.05  # 5% maximum error rate
        }
    
    async def generate_quality_report(
        self, 
        pipeline_name: str = "municipal_permit_batch_storage",
        hours_back: int = 24
    ) -> QualityReport:
        """Generate comprehensive data quality report"""
        try:
            # Get quality metrics from database
            metrics = await self.db_service.get_data_quality_metrics(
                pipeline_name=pipeline_name,
                hours_back=hours_back
            )
            
            if not metrics:
                return QualityReport(
                    pipeline_name=pipeline_name,
                    total_records=0,
                    success_rate=0.0,
                    geocoding_success_rate=0.0,
                    avg_processing_time_ms=0.0,
                    error_count=0,
                    recommendations=["No data available for analysis"],
                    timestamp=datetime.now().isoformat()
                )
            
            # Calculate aggregate statistics
            total_processed = sum(m['processed_records'] for m in metrics)
            total_passed = sum(m['validation_passed'] for m in metrics)
            total_failed = sum(m['validation_failed'] for m in metrics)
            
            success_rate = total_passed / total_processed if total_processed > 0 else 0
            
            # Calculate geocoding success rate
            geocoding_rates = [m['geocoding_success_rate'] for m in metrics if m.get('geocoding_success_rate')]
            avg_geocoding_rate = statistics.mean(geocoding_rates) if geocoding_rates else 0
            
            # Calculate processing time statistics
            processing_times = [m['processing_duration_ms'] for m in metrics if m.get('processing_duration_ms')]
            avg_processing_time = statistics.mean(processing_times) if processing_times else 0
            
            # Generate recommendations
            recommendations = self._generate_quality_recommendations(
                success_rate, avg_geocoding_rate, avg_processing_time, total_failed
            )
            
            logger.info(f"📊 Quality report generated: {total_processed} records, {success_rate:.2%} success rate")
            
            return QualityReport(
                pipeline_name=pipeline_name,
                total_records=total_processed,
                success_rate=success_rate,
                geocoding_success_rate=avg_geocoding_rate,
                avg_processing_time_ms=avg_processing_time,
                error_count=total_failed,
                recommendations=recommendations,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to generate quality report: {e}")
            return QualityReport(
                pipeline_name=pipeline_name,
                total_records=0,
                success_rate=0.0,
                geocoding_success_rate=0.0,
                avg_processing_time_ms=0.0,
                error_count=1,
                recommendations=[f"Error generating report: {e}"],
                timestamp=datetime.now().isoformat()
            )
    
    async def monitor_performance(self, hours_back: int = 1) -> PerformanceMetrics:
        """Monitor database performance metrics"""
        try:
            # Get recent quality metrics
            metrics = await self.db_service.get_data_quality_metrics(hours_back=hours_back)
            
            if not metrics:
                return PerformanceMetrics(
                    avg_query_time_ms=0.0,
                    total_operations=0,
                    success_rate=0.0,
                    error_rate=0.0,
                    peak_processing_time_ms=0.0,
                    recommendations=["No performance data available"]
                )
            
            # Calculate performance statistics
            processing_times = [m['processing_duration_ms'] for m in metrics if m.get('processing_duration_ms')]
            total_operations = len(metrics)
            
            avg_time = statistics.mean(processing_times) if processing_times else 0
            peak_time = max(processing_times) if processing_times else 0
            
            # Calculate success and error rates
            total_processed = sum(m['processed_records'] for m in metrics)
            total_passed = sum(m['validation_passed'] for m in metrics)
            total_failed = sum(m['validation_failed'] for m in metrics)
            
            success_rate = total_passed / total_processed if total_processed > 0 else 0
            error_rate = total_failed / total_processed if total_processed > 0 else 0
            
            # Generate performance recommendations
            recommendations = self._generate_performance_recommendations(
                avg_time, peak_time, success_rate, error_rate
            )
            
            return PerformanceMetrics(
                avg_query_time_ms=avg_time,
                total_operations=total_operations,
                success_rate=success_rate,
                error_rate=error_rate,
                peak_processing_time_ms=peak_time,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to monitor performance: {e}")
            return PerformanceMetrics(
                avg_query_time_ms=0.0,
                total_operations=0,
                success_rate=0.0,
                error_rate=1.0,
                peak_processing_time_ms=0.0,
                recommendations=[f"Error monitoring performance: {e}"]
            )
    
    def _generate_quality_recommendations(
        self, 
        success_rate: float, 
        geocoding_rate: float, 
        avg_processing_time: float,
        error_count: int
    ) -> List[str]:
        """Generate data quality recommendations"""
        recommendations = []
        
        if success_rate < self.quality_thresholds['min_success_rate']:
            recommendations.append(
                f"⚠️ Success rate ({success_rate:.2%}) below threshold "
                f"({self.quality_thresholds['min_success_rate']:.2%}). "
                "Review data validation rules and input data quality."
            )
        
        if geocoding_rate < self.quality_thresholds['min_geocoding_rate']:
            recommendations.append(
                f"🗺️ Geocoding success rate ({geocoding_rate:.2%}) below threshold "
                f"({self.quality_thresholds['min_geocoding_rate']:.2%}). "
                "Check address formats and geocoding service configuration."
            )
        
        if avg_processing_time > self.quality_thresholds['max_processing_time_ms']:
            recommendations.append(
                f"⏱️ Average processing time ({avg_processing_time:.0f}ms) exceeds threshold "
                f"({self.quality_thresholds['max_processing_time_ms']}ms). "
                "Consider batch size optimization or database indexing improvements."
            )
        
        if error_count > 0:
            recommendations.append(
                f"❌ {error_count} errors detected. Review error logs and implement "
                "additional validation or error handling."
            )
        
        if not recommendations:
            recommendations.append("✅ All quality metrics within acceptable thresholds.")
        
        return recommendations
    
    def _generate_performance_recommendations(
        self, 
        avg_time: float, 
        peak_time: float, 
        success_rate: float,
        error_rate: float
    ) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        if avg_time > 2000:  # 2 seconds
            recommendations.append(
                f"🐌 Average processing time ({avg_time:.0f}ms) is high. "
                "Consider optimizing batch sizes or database queries."
            )
        
        if peak_time > 10000:  # 10 seconds
            recommendations.append(
                f"📈 Peak processing time ({peak_time:.0f}ms) indicates potential bottlenecks. "
                "Review database indexes and query optimization."
            )
        
        if error_rate > self.quality_thresholds['max_error_rate']:
            recommendations.append(
                f"⚠️ Error rate ({error_rate:.2%}) exceeds threshold "
                f"({self.quality_thresholds['max_error_rate']:.2%}). "
                "Implement additional error handling and validation."
            )
        
        if success_rate > 0.98 and avg_time < 1000:
            recommendations.append("🚀 Excellent performance! System operating optimally.")
        
        return recommendations

    async def run_health_check(self) -> Dict:
        """Comprehensive database health check"""
        try:
            # Basic database health
            health_status = await self.db_service.health_check()

            # Performance metrics
            performance = await self.monitor_performance(hours_back=1)

            # Quality report
            quality = await self.generate_quality_report(hours_back=24)

            # Overall system status
            overall_status = "healthy"
            if quality.success_rate < 0.90 or performance.error_rate > 0.10:
                overall_status = "degraded"
            if quality.success_rate < 0.80 or performance.error_rate > 0.20:
                overall_status = "critical"

            return {
                'overall_status': overall_status,
                'database_health': health_status,
                'performance_metrics': {
                    'avg_processing_time_ms': performance.avg_query_time_ms,
                    'success_rate': performance.success_rate,
                    'error_rate': performance.error_rate,
                    'total_operations': performance.total_operations
                },
                'quality_metrics': {
                    'total_records': quality.total_records,
                    'success_rate': quality.success_rate,
                    'geocoding_success_rate': quality.geocoding_success_rate,
                    'error_count': quality.error_count
                },
                'recommendations': performance.recommendations + quality.recommendations,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return {
                'overall_status': 'error',
                'error_message': str(e),
                'timestamp': datetime.now().isoformat()
            }

# Factory function for easy integration
def create_monitoring_service() -> DatabaseMonitoringService:
    """Create and initialize database monitoring service"""
    return DatabaseMonitoringService()
