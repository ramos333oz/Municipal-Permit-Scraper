#!/usr/bin/env python3
"""
Example Usage: Municipal Permit Scraper
Demonstrates complete workflow for scraping permits with all 15 required fields

Based on specifications from .claude/agents/web-scraper.md
Integrates with database schema from .claude/agents/database-architect.md
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dataclasses import asdict

# Import our scraper modules
from san_diego_county_scraper import SanDiegoCountyScraper, PermitData
from scraper_config import (
    load_portal_config, 
    save_scraping_results, 
    ValidationRules,
    MaterialClassificationPatterns,
    QuantityExtractionPatterns
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PermitScrapingOrchestrator:
    """Orchestrates permit scraping across multiple portals"""
    
    def __init__(self):
        self.scrapers = {
            'san_diego_county': SanDiegoCountyScraper(),
            # Add other scrapers as they're implemented
            # 'ontario': OntarioScraper(),
            # 'orange_county': OrangeCountyScraper()
        }
        self.validation_rules = ValidationRules()
    
    async def scrape_all_portals(self, search_criteria: Dict[str, Any]) -> Dict[str, List[PermitData]]:
        """Scrape permits from all configured portals"""
        results = {}
        
        for portal_name, scraper in self.scrapers.items():
            logger.info(f"Starting scraping for {portal_name}")
            
            try:
                permits = await scraper.scrape_permits(
                    search_criteria, 
                    max_permits=search_criteria.get('max_permits', 50)
                )
                
                # Validate extracted data
                validated_permits = self.validate_permits(permits)
                results[portal_name] = validated_permits
                
                logger.info(f"Completed {portal_name}: {len(validated_permits)} valid permits")
                
            except Exception as e:
                logger.error(f"Error scraping {portal_name}: {str(e)}")
                results[portal_name] = []
        
        return results
    
    def validate_permits(self, permits: List[PermitData]) -> List[PermitData]:
        """Validate extracted permit data using validation rules"""
        validated_permits = []
        
        for permit in permits:
            validation_errors = []
            
            # Validate required fields
            if not permit.site_number:
                validation_errors.append("Missing site number")
            
            if not permit.status:
                validation_errors.append("Missing status")
            elif not self.validation_rules.validate_permit_status(permit.status):
                validation_errors.append(f"Invalid status: {permit.status}")
            
            # Validate contact information
            if permit.project_phone and not self.validation_rules.validate_phone_number(permit.project_phone):
                validation_errors.append(f"Invalid phone number: {permit.project_phone}")
            
            if permit.project_email and not self.validation_rules.validate_email(permit.project_email):
                validation_errors.append(f"Invalid email: {permit.project_email}")
            
            # Validate quantity
            if permit.quantity and not self.validation_rules.validate_quantity(permit.quantity):
                validation_errors.append(f"Invalid quantity: {permit.quantity}")
            
            if validation_errors:
                logger.warning(f"Validation errors for permit {permit.site_number}: {validation_errors}")
                # Still include permit but log the issues
            
            validated_permits.append(permit)
        
        return validated_permits
    
    def generate_summary_report(self, results: Dict[str, List[PermitData]]) -> Dict[str, Any]:
        """Generate summary report of scraping results"""
        total_permits = sum(len(permits) for permits in results.values())
        
        # Count by status
        status_counts = {}
        material_counts = {}
        city_counts = {}
        
        for portal_permits in results.values():
            for permit in portal_permits:
                # Count statuses
                status = permit.status or 'Unknown'
                status_counts[status] = status_counts.get(status, 0) + 1
                
                # Count materials
                material = permit.material_description or 'Unknown'
                material_counts[material] = material_counts.get(material, 0) + 1
                
                # Count cities
                city = permit.project_city or 'Unknown'
                city_counts[city] = city_counts.get(city, 0) + 1
        
        # Calculate data completeness
        completeness_stats = self.calculate_data_completeness(results)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_permits': total_permits,
            'permits_by_portal': {portal: len(permits) for portal, permits in results.items()},
            'status_distribution': status_counts,
            'material_distribution': material_counts,
            'city_distribution': city_counts,
            'data_completeness': completeness_stats
        }
    
    def calculate_data_completeness(self, results: Dict[str, List[PermitData]]) -> Dict[str, float]:
        """Calculate data completeness percentages for all 15 required fields"""
        all_permits = []
        for permits in results.values():
            all_permits.extend(permits)
        
        if not all_permits:
            return {}
        
        total_permits = len(all_permits)
        field_completeness = {}
        
        # Check completeness for each of the 15 required fields
        required_fields = [
            'site_number', 'status', 'quantity', 'material_description',
            'project_city', 'project_company', 'project_contact',
            'project_phone', 'project_email', 'notes'
        ]
        
        for field in required_fields:
            complete_count = sum(1 for permit in all_permits if getattr(permit, field, None))
            field_completeness[field] = (complete_count / total_permits) * 100
        
        return field_completeness

async def example_daily_scraping():
    """Example: Daily scraping workflow"""
    logger.info("Starting daily permit scraping workflow")
    
    orchestrator = PermitScrapingOrchestrator()
    
    # Define search criteria for recent permits
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    
    search_criteria = {
        'permit_type': 'grading',
        'date_from': yesterday.strftime('%Y-%m-%d'),
        'date_to': today.strftime('%Y-%m-%d'),
        'max_permits': 100
    }
    
    # Scrape all portals
    results = await orchestrator.scrape_all_portals(search_criteria)
    
    # Generate summary report
    summary = orchestrator.generate_summary_report(results)
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save detailed results
    all_permits = []
    for portal_permits in results.values():
        all_permits.extend([asdict(permit) for permit in portal_permits])
    
    save_scraping_results(all_permits, f'daily_permits_{timestamp}.json')
    
    # Save summary report
    with open(f'daily_summary_{timestamp}.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    # Print summary
    print(f"\n=== Daily Scraping Summary ===")
    print(f"Total permits extracted: {summary['total_permits']}")
    print(f"Permits by portal: {summary['permits_by_portal']}")
    print(f"Status distribution: {summary['status_distribution']}")
    print(f"Material distribution: {summary['material_distribution']}")
    print(f"\nData completeness:")
    for field, percentage in summary['data_completeness'].items():
        print(f"  {field}: {percentage:.1f}%")
    
    return results, summary

async def example_historical_scraping():
    """Example: Historical data collection for specific date range"""
    logger.info("Starting historical permit scraping")
    
    orchestrator = PermitScrapingOrchestrator()
    
    # Define search criteria for historical data (last 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    search_criteria = {
        'permit_type': 'grading',
        'date_from': start_date.strftime('%Y-%m-%d'),
        'date_to': end_date.strftime('%Y-%m-%d'),
        'max_permits': 500  # Larger batch for historical collection
    }
    
    # Scrape all portals
    results = await orchestrator.scrape_all_portals(search_criteria)
    
    # Save historical results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    all_permits = []
    for portal_permits in results.values():
        all_permits.extend([asdict(permit) for permit in portal_permits])
    
    save_scraping_results(all_permits, f'historical_permits_{timestamp}.json')
    
    print(f"\n=== Historical Scraping Complete ===")
    print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"Total permits collected: {len(all_permits)}")
    
    return results

async def example_targeted_scraping():
    """Example: Targeted scraping for specific material types"""
    logger.info("Starting targeted material scraping")
    
    # This example shows how to filter results after scraping
    # In a real implementation, you might modify search criteria
    
    orchestrator = PermitScrapingOrchestrator()
    
    search_criteria = {
        'permit_type': 'grading',
        'date_from': '2024-01-01',
        'date_to': '2024-12-31',
        'max_permits': 200
    }
    
    results = await orchestrator.scrape_all_portals(search_criteria)
    
    # Filter for specific materials
    target_materials = ['Clean Fill', 'Clay', 'Grading']
    filtered_permits = []
    
    for portal_permits in results.values():
        for permit in portal_permits:
            if permit.material_description in target_materials:
                filtered_permits.append(permit)
    
    print(f"\n=== Targeted Material Scraping ===")
    print(f"Target materials: {target_materials}")
    print(f"Matching permits found: {len(filtered_permits)}")
    
    # Save filtered results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filtered_data = [asdict(permit) for permit in filtered_permits]
    save_scraping_results(filtered_data, f'targeted_permits_{timestamp}.json')
    
    return filtered_permits

async def main():
    """Main example demonstrating different scraping scenarios"""
    print("Municipal Permit Scraper - Example Usage")
    print("=" * 50)
    
    # Example 1: Daily scraping
    print("\n1. Running daily scraping example...")
    try:
        daily_results, daily_summary = await example_daily_scraping()
        print("✓ Daily scraping completed successfully")
    except Exception as e:
        print(f"✗ Daily scraping failed: {str(e)}")
    
    # Example 2: Historical scraping
    print("\n2. Running historical scraping example...")
    try:
        historical_results = await example_historical_scraping()
        print("✓ Historical scraping completed successfully")
    except Exception as e:
        print(f"✗ Historical scraping failed: {str(e)}")
    
    # Example 3: Targeted scraping
    print("\n3. Running targeted scraping example...")
    try:
        targeted_results = await example_targeted_scraping()
        print("✓ Targeted scraping completed successfully")
    except Exception as e:
        print(f"✗ Targeted scraping failed: {str(e)}")
    
    print("\n" + "=" * 50)
    print("Example usage completed. Check output files for results.")

if __name__ == "__main__":
    asyncio.run(main())
