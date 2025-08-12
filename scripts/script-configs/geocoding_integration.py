#!/usr/bin/env python3
"""
Geocoding Integration for San Diego County Permit Data
Converts addresses to coordinates for distance calculations and mapping
"""

import json
import requests
import logging
import time
from typing import List, Dict, Optional, Tuple
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeocodingService:
    """Handles address to coordinate conversion using multiple geocoding services"""
    
    def __init__(self, google_api_key: str = None):
        """
        Initialize geocoding service
        
        Args:
            google_api_key: Google Maps API key (can be set via environment variable GOOGLE_MAPS_API_KEY)
        """
        self.google_api_key = google_api_key or os.getenv('GOOGLE_MAPS_API_KEY')
        self.rate_limit_delay = 0.1  # 100ms delay between requests
        
        if not self.google_api_key:
            logger.warning("⚠️ Google Maps API key not provided. Will use free OpenStreetMap service.")
    
    def geocode_with_google(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Geocode address using Google Maps API
        
        Args:
            address: Full address string
            
        Returns:
            Tuple of (latitude, longitude) or None if failed
        """
        if not self.google_api_key:
            return None
        
        try:
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                "address": address,
                "key": self.google_api_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data["status"] == "OK" and data["results"]:
                location = data["results"][0]["geometry"]["location"]
                return (location["lat"], location["lng"])
            else:
                logger.warning(f"⚠️ Google geocoding failed for '{address}': {data.get('status', 'Unknown error')}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error geocoding with Google: {e}")
            return None
    
    def geocode_with_openstreetmap(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Geocode address using free OpenStreetMap Nominatim service
        
        Args:
            address: Full address string
            
        Returns:
            Tuple of (latitude, longitude) or None if failed
        """
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                "q": address,
                "format": "json",
                "limit": 1,
                "addressdetails": 1
            }
            
            headers = {
                "User-Agent": "SanDiegoCountyPermitScraper/1.0 (contact@ldpquotesheet.com)"
            }
            
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if data:
                result = data[0]
                return (float(result["lat"]), float(result["lon"]))
            else:
                logger.warning(f"⚠️ OpenStreetMap geocoding failed for '{address}': No results")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error geocoding with OpenStreetMap: {e}")
            return None
    
    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Geocode address using available services (Google first, then OpenStreetMap)
        
        Args:
            address: Full address string
            
        Returns:
            Tuple of (latitude, longitude) or None if failed
        """
        if not address or address.strip() == "":
            return None
        
        # Clean up address
        address = address.strip()
        
        # Try Google Maps first (if API key available)
        if self.google_api_key:
            coords = self.geocode_with_google(address)
            if coords:
                logger.info(f"✅ Google geocoded '{address}' -> {coords}")
                time.sleep(self.rate_limit_delay)
                return coords
        
        # Fallback to OpenStreetMap
        coords = self.geocode_with_openstreetmap(address)
        if coords:
            logger.info(f"✅ OpenStreetMap geocoded '{address}' -> {coords}")
        else:
            logger.warning(f"❌ Failed to geocode '{address}' with all services")
        
        time.sleep(self.rate_limit_delay)
        return coords
    
    def calculate_distance(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """
        Calculate distance between two coordinates using Haversine formula
        
        Args:
            coord1: (latitude, longitude) of first point
            coord2: (latitude, longitude) of second point
            
        Returns:
            Distance in miles
        """
        import math
        
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth radius in miles
        r = 3956
        
        return c * r
    
    def estimate_drive_time(self, distance_miles: float) -> int:
        """
        Estimate drive time in minutes based on distance
        
        Args:
            distance_miles: Distance in miles
            
        Returns:
            Estimated drive time in minutes (roundtrip)
        """
        # Assume average speed of 35 mph for local driving
        # Add 10 minutes for loading/unloading time
        one_way_minutes = (distance_miles / 35) * 60
        roundtrip_minutes = (one_way_minutes * 2) + 10
        
        return int(roundtrip_minutes)

def add_geocoding_to_permits(permits: List[Dict], depot_address: str = "San Diego, CA") -> List[Dict]:
    """
    Add geocoding information to permit data
    
    Args:
        permits: List of permit dictionaries
        depot_address: Address of the depot/base location for distance calculations
        
    Returns:
        Updated permits with geocoding information
    """
    geocoder = GeocodingService()
    
    # Geocode depot location
    depot_coords = geocoder.geocode_address(depot_address)
    if not depot_coords:
        logger.error(f"❌ Failed to geocode depot address: {depot_address}")
        return permits
    
    logger.info(f"📍 Depot location: {depot_address} -> {depot_coords}")
    
    updated_permits = []
    
    for i, permit in enumerate(permits, 1):
        logger.info(f"🗺️ Processing permit {i}/{len(permits)}: {permit.get('site_number', 'unknown')}")
        
        address = permit.get('address')
        if not address:
            logger.warning(f"⚠️ No address found for permit {permit.get('site_number', 'unknown')}")
            updated_permits.append(permit)
            continue
        
        # Geocode permit address
        permit_coords = geocoder.geocode_address(address)
        
        if permit_coords:
            # Calculate distance and drive time
            distance = geocoder.calculate_distance(depot_coords, permit_coords)
            drive_time = geocoder.estimate_drive_time(distance)
            
            # Add geocoding data to permit
            permit['coordinates'] = {
                'latitude': permit_coords[0],
                'longitude': permit_coords[1]
            }
            permit['distance_from_depot_miles'] = round(distance, 2)
            permit['estimated_roundtrip_minutes'] = drive_time
            
            # Calculate trucking price using LDP formula: (Roundtrip Minutes × 1.83) + Added Minutes
            trucking_price = (drive_time * 1.83) + 0  # No added minutes for now
            permit['trucking_price_per_load'] = round(trucking_price, 2)
            
            logger.info(f"✅ Added geocoding: {distance:.1f} miles, {drive_time} min, ${trucking_price:.2f}")
        else:
            logger.warning(f"❌ Failed to geocode address: {address}")
        
        updated_permits.append(permit)
    
    return updated_permits

def main():
    """Main function for testing geocoding integration"""
    logger.info("🗺️ Testing Geocoding Integration")
    
    # Load permits from JSON file
    try:
        with open("san_diego_permits.json", 'r') as f:
            permits = json.load(f)
        logger.info(f"📁 Loaded {len(permits)} permits")
    except Exception as e:
        logger.error(f"❌ Error loading permits: {e}")
        return
    
    # Add geocoding information
    updated_permits = add_geocoding_to_permits(permits)
    
    # Save updated permits
    try:
        with open("san_diego_permits_with_geocoding.json", 'w') as f:
            json.dump(updated_permits, f, indent=2)
        logger.info("💾 Saved permits with geocoding to san_diego_permits_with_geocoding.json")
    except Exception as e:
        logger.error(f"❌ Error saving permits: {e}")
    
    # Display summary
    geocoded_count = sum(1 for p in updated_permits if 'coordinates' in p)
    logger.info(f"📊 Geocoding Summary: {geocoded_count}/{len(updated_permits)} permits geocoded")

if __name__ == "__main__":
    main()
