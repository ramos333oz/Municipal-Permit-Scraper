#!/usr/bin/env python3
"""
Supabase Database Integration Service for Municipal Permit System
Implements Direct-to-Supabase architecture following agent specifications

Based on:
- .claude/agents/database-architect.md (Direct-to-Supabase architecture)
- .claude/agents/backend-api-developer.md (Supabase MCP integration patterns)
- .claude/agents/data-engineer.md (ETL pipeline and data processing)

Architecture: CSV → Data Processing → Geocoding → Supabase (PostgreSQL/PostGIS)
Data Structure: Exact 15-field permit structure with PostGIS coordinates
"""

import os
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import asyncio

# Supabase integration (Direct-to-Supabase architecture)
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logging.warning("Supabase client not available. Install with: pip install supabase")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DatabaseResult:
    """Standardized database operation result"""
    success: bool
    records_processed: int
    records_failed: int
    processing_time_ms: int
    error_message: Optional[str] = None
    details: Optional[Dict] = None

class SupabaseDatabaseService:
    """
    Enhanced Supabase database service implementing Direct-to-Supabase architecture
    
    Features:
    - Exact 15-field permit structure compliance
    - PostGIS coordinate storage and spatial queries
    - Automatic pricing calculations using LDP formula
    - Data quality monitoring and audit logging
    - Batch processing optimization
    - Error handling and recovery
    """
    
    def __init__(self, project_id: str = "tellxlrnkwooikljwlhc"):
        """Initialize Supabase database service"""
        self.project_id = project_id
        self.client: Optional[Client] = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize Supabase client with credentials"""
        if not SUPABASE_AVAILABLE:
            logger.error("❌ Supabase client not available")
            return
        
        try:
            # Get Supabase credentials from environment
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_ANON_KEY')
            
            if not supabase_url or not supabase_key:
                logger.error("❌ Supabase credentials not found in environment")
                logger.info("💡 Set SUPABASE_URL and SUPABASE_ANON_KEY environment variables")
                return
            
            # Create Supabase client
            self.client = create_client(supabase_url, supabase_key)
            logger.info("✅ Supabase client initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {e}")
    
    async def store_permits_batch(self, permits_data: List[Dict]) -> DatabaseResult:
        """
        Store permits in batch using Direct-to-Supabase architecture
        
        Implements:
        - Exact 15-field permit structure validation
        - PostGIS coordinate conversion
        - Automatic pricing calculations via triggers
        - Data quality monitoring
        - Conflict resolution on site_number
        """
        start_time = time.time()
        
        if not self.client:
            return DatabaseResult(
                success=False,
                records_processed=0,
                records_failed=len(permits_data),
                processing_time_ms=0,
                error_message="Supabase client not initialized"
            )
        
        try:
            # Validate and prepare permit data
            validated_permits = []
            failed_permits = []
            
            for permit in permits_data:
                try:
                    validated_permit = self._validate_and_prepare_permit(permit)
                    validated_permits.append(validated_permit)
                except Exception as e:
                    logger.warning(f"⚠️ Permit validation failed: {e}")
                    failed_permits.append(permit)
            
            if not validated_permits:
                return DatabaseResult(
                    success=False,
                    records_processed=0,
                    records_failed=len(permits_data),
                    processing_time_ms=int((time.time() - start_time) * 1000),
                    error_message="No valid permits to process"
                )
            
            # Batch upsert to Supabase with conflict resolution
            result = self.client.table("permits").upsert(
                validated_permits, 
                on_conflict="site_number"
            ).execute()
            
            success_count = len(result.data) if result.data else 0
            processing_time = int((time.time() - start_time) * 1000)
            
            # Log data quality metrics
            await self._log_data_quality_metrics(
                pipeline_name="municipal_permit_batch_storage",
                total_records=len(permits_data),
                passed_records=success_count,
                failed_records=len(failed_permits),
                processing_duration_ms=processing_time
            )
            
            logger.info(f"📤 Batch storage complete: {success_count} permits stored, {len(failed_permits)} failed")
            
            return DatabaseResult(
                success=True,
                records_processed=success_count,
                records_failed=len(failed_permits),
                processing_time_ms=processing_time,
                details={
                    'validated_permits': len(validated_permits),
                    'failed_validation': len(failed_permits)
                }
            )
            
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            logger.error(f"❌ Batch storage failed: {e}")
            
            return DatabaseResult(
                success=False,
                records_processed=0,
                records_failed=len(permits_data),
                processing_time_ms=processing_time,
                error_message=str(e)
            )
    
    def _validate_and_prepare_permit(self, permit_data: Dict) -> Dict:
        """
        Validate and prepare permit data for database storage
        
        Ensures compliance with exact 15-field structure:
        1. site_number, status, project_city, notes
        2. project_company, project_contact, project_phone, project_email
        3. quantity, material_description
        4. dump_fee, trucking_price_per_load, ldp_fee, total_price_per_load
        5. Additional metadata fields
        """
        # Core permit fields (from CSV)
        validated = {
            'site_number': permit_data.get('site_number'),
            'record_type': permit_data.get('record_type'),
            'address': permit_data.get('address'),
            'date_opened': permit_data.get('date_opened'),
            'status': permit_data.get('status'),
            'project_city': permit_data.get('project_city', 'San Diego County'),
            'source_portal': permit_data.get('source_portal', 'San Diego County'),
        }
        
        # Contact information fields
        validated.update({
            'project_company': permit_data.get('project_company'),
            'project_contact': permit_data.get('project_contact'),
            'project_phone': self._standardize_phone(permit_data.get('project_phone')),
            'project_email': self._validate_email(permit_data.get('project_email')),
        })
        
        # Material and quantity fields
        validated.update({
            'quantity': permit_data.get('quantity'),
            'material_description': permit_data.get('material_description'),
            'notes': permit_data.get('notes'),
        })
        
        # Pricing fields (will be calculated by database triggers)
        validated.update({
            'dump_fee': permit_data.get('dump_fee', 0),
            'ldp_fee': permit_data.get('ldp_fee', 0),
            'roundtrip_minutes': permit_data.get('roundtrip_minutes'),
            'added_minutes': permit_data.get('added_minutes', 0),
        })
        
        # Geocoding data (PostGIS coordinates)
        if permit_data.get('latitude') and permit_data.get('longitude'):
            validated.update({
                'latitude': permit_data['latitude'],
                'longitude': permit_data['longitude'],
                'geocoding_accuracy': permit_data.get('geocoding_accuracy'),
                'geocoding_confidence': permit_data.get('geocoding_confidence'),
                'geocoding_source': permit_data.get('geocoding_source'),
                'formatted_address': permit_data.get('formatted_address'),
            })
        
        # Metadata
        validated.update({
            'raw_csv_data': permit_data.get('raw_csv_data', {}),
            'scraped_at': datetime.now().isoformat(),
        })
        
        # Remove None values to use database defaults
        return {k: v for k, v in validated.items() if v is not None}
    
    def _standardize_phone(self, phone: Optional[str]) -> Optional[str]:
        """Standardize phone number to (XXX) XXX-XXXX format"""
        if not phone:
            return None
        
        import re
        digits = re.sub(r'\D', '', phone)
        
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        
        return phone  # Return original if can't standardize
    
    def _validate_email(self, email: Optional[str]) -> Optional[str]:
        """Validate email address format"""
        if not email:
            return None
        
        import re
        email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
        email_clean = email.strip().lower()
        
        return email_clean if re.match(email_pattern, email_clean) else None
    
    async def _log_data_quality_metrics(
        self, 
        pipeline_name: str,
        total_records: int,
        passed_records: int,
        failed_records: int,
        processing_duration_ms: int,
        geocoding_success_rate: Optional[float] = None
    ) -> None:
        """Log data quality metrics for monitoring"""
        if not self.client:
            return
        
        try:
            metrics = {
                'pipeline_name': pipeline_name,
                'processed_records': total_records,
                'validation_passed': passed_records,
                'validation_failed': failed_records,
                'processing_duration_ms': processing_duration_ms,
                'geocoding_success_rate': geocoding_success_rate,
            }
            
            self.client.table("data_quality_metrics").insert(metrics).execute()
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to log quality metrics: {e}")

    async def get_permits_by_criteria(
        self,
        record_type: Optional[str] = None,
        status: Optional[str] = None,
        project_city: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict]:
        """Get permits by various criteria with PostGIS support"""
        if not self.client:
            return []

        try:
            query = self.client.table("permits").select("*")

            if record_type:
                query = query.eq("record_type", record_type)
            if status:
                query = query.eq("status", status)
            if project_city:
                query = query.eq("project_city", project_city)

            result = query.limit(limit).execute()
            return result.data if result.data else []

        except Exception as e:
            logger.error(f"❌ Failed to get permits: {e}")
            return []

    async def get_permits_within_radius(
        self,
        lat: float,
        lng: float,
        radius_miles: float
    ) -> List[Dict]:
        """Get permits within radius using PostGIS spatial queries"""
        if not self.client:
            return []

        try:
            result = self.client.rpc("get_permits_within_radius", {
                "lat": lat,
                "lng": lng,
                "radius_miles": radius_miles
            }).execute()

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"❌ Failed to get permits within radius: {e}")
            return []

    async def get_permits_within_drive_time(
        self,
        origin_lat: float,
        origin_lng: float,
        max_drive_minutes: int
    ) -> List[Dict]:
        """Get permits within drive time using PostGIS calculations"""
        if not self.client:
            return []

        try:
            result = self.client.rpc("get_permits_within_drive_time", {
                "origin_lat": origin_lat,
                "origin_lng": origin_lng,
                "max_drive_minutes": max_drive_minutes
            }).execute()

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"❌ Failed to get permits within drive time: {e}")
            return []

    async def update_permit_pricing(
        self,
        site_number: str,
        roundtrip_minutes: int,
        added_minutes: int = 0,
        dump_fee: float = 0,
        ldp_fee: float = 0
    ) -> bool:
        """Update permit pricing using automatic calculation triggers"""
        if not self.client:
            return False

        try:
            result = self.client.table("permits").update({
                'roundtrip_minutes': roundtrip_minutes,
                'added_minutes': added_minutes,
                'dump_fee': dump_fee,
                'ldp_fee': ldp_fee
            }).eq('site_number', site_number).execute()

            return len(result.data) > 0 if result.data else False

        except Exception as e:
            logger.error(f"❌ Failed to update permit pricing: {e}")
            return False

    async def get_data_quality_metrics(
        self,
        pipeline_name: Optional[str] = None,
        hours_back: int = 24
    ) -> List[Dict]:
        """Get data quality metrics for monitoring"""
        if not self.client:
            return []

        try:
            query = self.client.table("data_quality_metrics").select("*")

            if pipeline_name:
                query = query.eq("pipeline_name", pipeline_name)

            # Filter by time range
            from datetime import datetime, timedelta
            cutoff_time = (datetime.now() - timedelta(hours=hours_back)).isoformat()
            query = query.gte("created_at", cutoff_time)

            result = query.order("created_at", desc=True).execute()
            return result.data if result.data else []

        except Exception as e:
            logger.error(f"❌ Failed to get quality metrics: {e}")
            return []

    async def health_check(self) -> Dict:
        """Perform database health check"""
        if not self.client:
            return {
                'status': 'error',
                'message': 'Supabase client not initialized',
                'timestamp': datetime.now().isoformat()
            }

        try:
            # Test basic connectivity
            result = self.client.table("permits").select("count", count="exact").limit(1).execute()

            # Get recent quality metrics
            recent_metrics = await self.get_data_quality_metrics(hours_back=1)

            return {
                'status': 'healthy',
                'total_permits': result.count if hasattr(result, 'count') else 0,
                'recent_operations': len(recent_metrics),
                'timestamp': datetime.now().isoformat(),
                'database_connection': 'active'
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }

# Factory function for easy integration
def create_database_service(project_id: str = "tellxlrnkwooikljwlhc") -> SupabaseDatabaseService:
    """Create and initialize Supabase database service"""
    return SupabaseDatabaseService(project_id=project_id)
