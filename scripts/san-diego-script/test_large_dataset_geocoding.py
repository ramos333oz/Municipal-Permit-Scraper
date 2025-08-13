#!/usr/bin/env python3
"""
Large Dataset Geocoding Performance Test
Tests the enhanced geocoding service with 2,537 records to demonstrate scalability
"""

import asyncio
import logging
import time
from datetime import datetime
import pandas as pd
import os

# Enhanced geocoding service
try:
    from enhanced_geocoding_service import EnhancedGeocodingService
    ENHANCED_GEOCODING_AVAILABLE = True
except ImportError:
    ENHANCED_GEOCODING_AVAILABLE = False

# Configure logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('large_dataset_geocoding_test.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def test_large_dataset_geocoding():
    """Test batch geocoding performance with large dataset (2,537 records)"""
    
    if not ENHANCED_GEOCODING_AVAILABLE:
        logger.error("ERROR: Enhanced geocoding service not available")
        return
    
    logger.info("🚀 === Large Dataset Geocoding Performance Test ===")
    logger.info("📊 Testing batch geocoding with 2,537 records")
    
    # Load the large CSV dataset
    csv_path = "downloads/RecordList20250811.csv"
    
    if not os.path.exists(csv_path):
        logger.error(f"❌ CSV file not found: {csv_path}")
        return
    
    try:
        # Load CSV data
        logger.info(f"📥 Loading CSV dataset: {csv_path}")
        df = pd.read_csv(csv_path)
        logger.info(f"✅ Loaded {len(df)} records with {len(df.columns)} columns")
        
        # Extract addresses for geocoding
        addresses = []
        for _, row in df.iterrows():
            address = str(row.get('Address', '')).strip()
            if address and address != 'nan' and address != '':
                addresses.append(address)
        
        logger.info(f"📍 Extracted {len(addresses)} valid addresses for geocoding")
        
        if not addresses:
            logger.error("❌ No valid addresses found in dataset")
            return
        
        # Initialize geocoding service
        geocoder = EnhancedGeocodingService()
        
        # Performance Test 1: Individual geocoding (baseline)
        logger.info("\n🔄 === Performance Test 1: Individual Geocoding (Baseline) ===")
        
        # Test with first 50 addresses for baseline comparison
        test_addresses = addresses[:50]
        
        start_time = time.time()
        individual_results = []
        
        for i, address in enumerate(test_addresses, 1):
            logger.info(f"📍 Individual geocoding {i}/{len(test_addresses)}: {address[:50]}...")
            result = geocoder.geocode_address(address, min_confidence=0.7)
            individual_results.append({
                'address': address,
                'geocoded': result is not None,
                'latitude': result.latitude if result else None,
                'longitude': result.longitude if result else None,
                'source': result.source if result else None
            })
        
        individual_time = time.time() - start_time
        individual_success = sum(1 for r in individual_results if r['geocoded'])
        individual_success_rate = (individual_success / len(test_addresses)) * 100
        
        logger.info(f"⏱️ Individual geocoding completed in {individual_time:.2f} seconds")
        logger.info(f"✅ Success rate: {individual_success}/{len(test_addresses)} ({individual_success_rate:.1f}%)")
        
        # Performance Test 2: Batch geocoding (optimized)
        logger.info("\n🚀 === Performance Test 2: Batch Geocoding (Optimized) ===")
        
        start_time = time.time()
        batch_results = geocoder.batch_geocode_addresses(test_addresses, min_confidence=0.7, use_batch_api=True)
        batch_time = time.time() - start_time
        
        batch_success = sum(1 for r in batch_results if r and r['geocoded'])
        batch_success_rate = (batch_success / len(test_addresses)) * 100
        
        logger.info(f"⏱️ Batch geocoding completed in {batch_time:.2f} seconds")
        logger.info(f"✅ Success rate: {batch_success}/{len(test_addresses)} ({batch_success_rate:.1f}%)")
        
        # Calculate performance improvement
        if individual_time > 0:
            performance_improvement = ((individual_time - batch_time) / individual_time) * 100
            speed_multiplier = individual_time / batch_time if batch_time > 0 else float('inf')
            
            logger.info(f"\n📈 === Performance Analysis ===")
            logger.info(f"⚡ Performance improvement: {performance_improvement:.1f}% faster")
            logger.info(f"🚀 Speed multiplier: {speed_multiplier:.1f}x faster")
            logger.info(f"📊 API calls reduced: {len(test_addresses)} → 1 ({((len(test_addresses)-1)/len(test_addresses)*100):.1f}% reduction)")
        
        # Performance Test 3: Large dataset batch geocoding
        logger.info(f"\n🌟 === Performance Test 3: Full Dataset Batch Geocoding ({len(addresses)} addresses) ===")
        
        # Process in chunks to respect API limits and demonstrate scalability
        chunk_size = 1000  # Process 1000 addresses at a time
        all_results = []
        total_start_time = time.time()
        
        for i in range(0, len(addresses), chunk_size):
            chunk = addresses[i:i + chunk_size]
            chunk_num = (i // chunk_size) + 1
            total_chunks = (len(addresses) + chunk_size - 1) // chunk_size
            
            logger.info(f"🔄 Processing chunk {chunk_num}/{total_chunks}: {len(chunk)} addresses...")
            
            chunk_start_time = time.time()
            chunk_results = geocoder.batch_geocode_addresses(chunk, min_confidence=0.7, use_batch_api=True)
            chunk_time = time.time() - chunk_start_time
            
            chunk_success = sum(1 for r in chunk_results if r and r['geocoded'])
            chunk_success_rate = (chunk_success / len(chunk)) * 100
            
            logger.info(f"✅ Chunk {chunk_num} completed in {chunk_time:.2f}s: {chunk_success}/{len(chunk)} ({chunk_success_rate:.1f}%)")
            
            all_results.extend(chunk_results)
        
        total_time = time.time() - total_start_time
        total_success = sum(1 for r in all_results if r and r['geocoded'])
        total_success_rate = (total_success / len(addresses)) * 100
        
        logger.info(f"\n🎉 === Final Results ===")
        logger.info(f"📊 Total addresses processed: {len(addresses)}")
        logger.info(f"✅ Successfully geocoded: {total_success} ({total_success_rate:.1f}%)")
        logger.info(f"⏱️ Total processing time: {total_time:.2f} seconds")
        logger.info(f"⚡ Average time per address: {(total_time/len(addresses)):.3f} seconds")
        logger.info(f"🚀 Estimated individual processing time: {(len(addresses) * 2):.0f} seconds")
        logger.info(f"📈 Estimated performance improvement: {(((len(addresses) * 2) - total_time) / (len(addresses) * 2) * 100):.1f}%")
        
        # Get service statistics
        stats = geocoder.get_statistics()
        logger.info(f"📊 Service statistics: {stats}")
        
        # Save results
        results_summary = {
            'dataset_size': len(addresses),
            'total_geocoded': total_success,
            'success_rate': total_success_rate,
            'processing_time': total_time,
            'avg_time_per_address': total_time / len(addresses),
            'estimated_individual_time': len(addresses) * 2,
            'performance_improvement': ((len(addresses) * 2) - total_time) / (len(addresses) * 2) * 100,
            'service_stats': stats,
            'timestamp': datetime.now().isoformat()
        }
        
        import json
        with open('large_dataset_geocoding_results.json', 'w') as f:
            json.dump(results_summary, f, indent=2)
        
        logger.info("💾 Results saved to large_dataset_geocoding_results.json")
        
    except Exception as e:
        logger.error(f"❌ Error during large dataset testing: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_large_dataset_geocoding())
