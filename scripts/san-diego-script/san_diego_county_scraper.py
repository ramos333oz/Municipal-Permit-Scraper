#!/usr/bin/env python3
"""
San Diego County Accela Portal Scraper
Production-ready Playwright script for extracting all 15 required permit fields

Based on specifications from .claude/agents/web-scraper.md
Targets: San Diego County Accela-based permit portal
Extracts: All 15 required fields for LDP Quote Sheet system
"""

import asyncio
import re
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from dataclasses import dataclass, asdict
import random

# Import our integration modules
try:
    from supabase_direct_integration import SupabaseDirectIntegration
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

# Enhanced geocoding service (RECOMMENDED)
try:
    from enhanced_geocoding_service import EnhancedGeocodingService
    ENHANCED_GEOCODING_AVAILABLE = True
except ImportError:
    ENHANCED_GEOCODING_AVAILABLE = False
    # Fallback to basic geocoding
    try:
        from geocoding_integration import add_geocoding_to_permits
        BASIC_GEOCODING_AVAILABLE = True
    except ImportError:
        BASIC_GEOCODING_AVAILABLE = False

# Optional Airtable integration (for business users who need it)
try:
    from airtable_integration import AirtableIntegration
    AIRTABLE_AVAILABLE = True
except ImportError:
    AIRTABLE_AVAILABLE = False

# Configure enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('san_diego_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Set debug level for more detailed output during testing
logger.setLevel(logging.DEBUG)

@dataclass
class PermitData:
    """Data structure matching database schema for all 15 required fields"""
    # Core permit information
    site_number: Optional[str] = None           # Permit record number
    status: Optional[str] = None                # Permit approval status
    project_city: Optional[str] = None          # Municipality location
    notes: Optional[str] = None                 # Additional project information
    
    # Contact information
    project_company: Optional[str] = None       # Contractor/applicant company
    project_contact: Optional[str] = None       # Primary contact person
    project_phone: Optional[str] = None         # Phone number (formatted)
    project_email: Optional[str] = None         # Email address
    
    # Material and quantity information
    quantity: Optional[float] = None            # Material volume/amount
    material_description: Optional[str] = None  # Type of construction material

    # Enhanced fields from CSV analysis (critical for comprehensive data collection)
    opened_date: Optional[str] = None           # Permit opening date (Opened Date)
    project_name: Optional[str] = None          # Project name (Project Name)
    address: Optional[str] = None               # Full address (Address) - CRITICAL for geocoding
    short_notes: Optional[str] = None           # Short notes (Short Notes)

    # Pricing calculation fields (populated by business logic)
    dump_fee: Optional[float] = None            # Disposal cost
    trucking_price_per_load: Optional[float] = None  # Calculated transportation cost
    ldp_fee: Optional[float] = None             # Additional regulatory fee
    total_price_per_load: Optional[float] = None     # Total calculated cost

    # Metadata
    source_portal: str = "San Diego County"
    scraped_at: str = None
    raw_data: Optional[Dict] = None

class SanDiegoCountyScraper:
    """Production-ready scraper for San Diego County Accela portal"""
    
    def __init__(self):
        self.base_url = "https://publicservices.sandiegocounty.gov"
        self.search_url = "https://publicservices.sandiegocounty.gov/CitizenAccess/Cap/CapHome.aspx?module=LUEG-PDS"
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        
        # Anti-detection settings
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
        ]
    
    async def initialize_browser(self) -> None:
        """Initialize Playwright browser with anti-detection measures"""
        playwright = await async_playwright().start()
        
        # Browser configuration for anti-detection
        self.browser = await playwright.chromium.launch(
            headless=False,  # Set to True for production
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-features=VizDisplayCompositor',
                '--disable-web-security',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection'
            ]
        )
        
        # Create context with randomized fingerprint
        self.context = await self.browser.new_context(
            user_agent=random.choice(self.user_agents),
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='America/Los_Angeles'
        )
        
        # Add stealth measures
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        
        logger.info("Browser initialized with anti-detection measures")
    
    async def search_permits(self, search_criteria: Dict[str, str]) -> List[str]:
        """Search for permits and return list of permit URLs"""
        page = await self.context.new_page()

        try:
            # Navigate directly to PDS search page (no iframe needed)
            logger.info(f"Navigating to: {self.search_url}")
            await page.goto(self.search_url, wait_until='networkidle')
            await self.random_delay(3, 5)

            # Debug: Check page title and URL
            page_title = await page.title()
            current_url = page.url
            logger.info(f"Page loaded: {page_title} at {current_url}")

            # Wait for form elements to be fully loaded
            logger.info("Waiting for search form to load...")
            await page.wait_for_selector('text="Record Type:"', timeout=15000)
            await self.random_delay(2, 3)

            # Select record type for grading permits with robust fallback strategies
            record_type = search_criteria.get('permit_type', 'Grading Perm')
            logger.info(f"Attempting to select record type: {record_type}")

            # Strategy 1: Wait for and use the exact dropdown selector
            try:
                await page.wait_for_selector('select[name*="ddlGSRecordType"]', timeout=10000)
                await page.select_option('select[name*="ddlGSRecordType"]', record_type)
                logger.info("Successfully selected record type using Strategy 1")
            except Exception as e1:
                logger.warning(f"Strategy 1 failed: {e1}")

                # Strategy 2: Use JavaScript to find and set the dropdown
                try:
                    await page.evaluate(f"""
                        const dropdown = document.querySelector('select[name*="ddlGSRecordType"]') ||
                                       document.querySelector('select[id*="ddlGSRecordType"]') ||
                                       document.querySelector('combobox[aria-label*="Record Type"]');
                        if (dropdown) {{
                            dropdown.value = '{record_type}';
                            dropdown.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        }}
                    """)
                    logger.info("Successfully selected record type using Strategy 2 (JavaScript)")
                except Exception as e2:
                    logger.warning(f"Strategy 2 failed: {e2}")

                    # Strategy 3: Click-based selection
                    try:
                        # Find all select elements and try each one
                        selects = await page.locator('select').all()
                        for select in selects:
                            try:
                                options = await select.locator('option').all()
                                for option in options:
                                    text = await option.text_content()
                                    if text and record_type in text:
                                        await select.select_option(value=await option.get_attribute('value'))
                                        logger.info("Successfully selected record type using Strategy 3 (click-based)")
                                        break
                                else:
                                    continue
                                break
                            except:
                                continue
                    except Exception as e3:
                        logger.error(f"All strategies failed: Strategy 3 error: {e3}")

            await self.random_delay(1, 2)

            # Set date range if provided with robust handling
            if 'date_from' in search_criteria:
                logger.info(f"Setting date from: {search_criteria['date_from']}")
                try:
                    await page.wait_for_selector('input[name*="txtGSDateFrom"]', timeout=5000)
                    await page.fill('input[name*="txtGSDateFrom"]', '')
                    await page.fill('input[name*="txtGSDateFrom"]', search_criteria['date_from'])
                    logger.info("Successfully set 'from' date")
                except Exception as e:
                    logger.warning(f"Failed to set 'from' date: {e}")
                await self.random_delay(1, 2)

            if 'date_to' in search_criteria:
                logger.info(f"Setting date to: {search_criteria['date_to']}")
                try:
                    await page.wait_for_selector('input[name*="txtGSDateTo"]', timeout=5000)
                    await page.fill('input[name*="txtGSDateTo"]', '')
                    await page.fill('input[name*="txtGSDateTo"]', search_criteria['date_to'])
                    logger.info("Successfully set 'to' date")
                except Exception as e:
                    logger.warning(f"Failed to set 'to' date: {e}")
                await self.random_delay(1, 2)

            # Submit search using robust ASP.NET postback handling
            logger.info("Attempting to submit search...")
            search_submitted = False

            # Strategy 1: Click the search link
            try:
                await page.wait_for_selector('a[href*="btnNewSearch"]', timeout=5000)
                await page.click('a[href*="btnNewSearch"]')
                search_submitted = True
                logger.info("Search submitted using Strategy 1 (link click)")
            except Exception as e1:
                logger.warning(f"Strategy 1 failed: {e1}")

                # Strategy 2: Find and click any element with "Search" text
                try:
                    await page.click('text="Search"')
                    search_submitted = True
                    logger.info("Search submitted using Strategy 2 (text search)")
                except Exception as e2:
                    logger.warning(f"Strategy 2 failed: {e2}")

                    # Strategy 3: Execute JavaScript postback directly
                    try:
                        await page.evaluate("""
                            // Look for the search button and trigger its postback
                            const searchLink = document.querySelector('a[href*="btnNewSearch"]') ||
                                             document.querySelector('a[id*="btnNewSearch"]') ||
                                             document.querySelector('input[value*="Search"]');
                            if (searchLink) {
                                if (searchLink.href && searchLink.href.includes('javascript:')) {
                                    eval(searchLink.href.replace('javascript:', ''));
                                } else {
                                    searchLink.click();
                                }
                            }
                        """)
                        search_submitted = True
                        logger.info("Search submitted using Strategy 3 (JavaScript execution)")
                    except Exception as e3:
                        logger.error(f"All search strategies failed: {e3}")

            if search_submitted:
                await page.wait_for_load_state('networkidle', timeout=30000)
                await self.random_delay(5, 8)
                logger.info("Search completed, waiting for results...")
            else:
                logger.error("Failed to submit search form")

            # Extract permit URLs from results table with robust handling
            permit_urls = []

            try:
                # Wait for results to load - use a more flexible approach
                await page.wait_for_selector('table', timeout=15000)
                await self.random_delay(2, 3)

                # Look for permit links directly
                permit_links = await page.locator('a[href*="CapDetail.aspx"]').all()

                if len(permit_links) > 0:
                    logger.info(f"Results found! Found {len(permit_links)} permit links")

                    for link in permit_links:
                        try:
                            href = await link.get_attribute('href')
                            if href and ('Record' in href or 'Cap' in href or 'Detail' in href):
                                # Convert relative URLs to absolute
                                if href.startswith('/'):
                                    href = self.base_url + href
                                elif href.startswith('../'):
                                    href = self.base_url + '/CitizenAccess/' + href.replace('../', '')
                                elif not href.startswith('http'):
                                    href = self.base_url + '/CitizenAccess/' + href
                                permit_urls.append(href)
                                logger.debug(f"Found permit URL: {href}")
                        except Exception as e:
                            logger.warning(f"Error processing link: {e}")
                            continue
                else:
                    # Check for "no results" message
                    no_results = await page.locator('text="No records found", text="No results", text="0 records"').count()
                    if no_results > 0:
                        logger.info("No permits found matching search criteria")
                    else:
                        logger.warning("Results table not found, checking page content...")
                        # Debug: Log page content to understand structure
                        page_content = await page.content()
                        if 'GridView' in page_content:
                            logger.info("GridView found in page content but not accessible via selector")
                        else:
                            logger.warning("No GridView found in page content")

            except Exception as e:
                logger.error(f"Error extracting results: {e}")

            logger.info(f"Found {len(permit_urls)} permits in search results")
            return permit_urls

        except Exception as e:
            logger.error(f"Error searching permits: {str(e)}")
            return []
        finally:
            await page.close()
    
    async def extract_permit_data(self, permit_url: str) -> Optional[PermitData]:
        """Extract all 15 required fields from a single permit page"""
        page = await self.context.new_page()
        permit_data = PermitData()

        try:
            # Navigate to permit detail page
            await page.goto(permit_url, wait_until='networkidle')
            await self.random_delay(3, 5)

            # Extract core permit information using enhanced selectors
            permit_data.site_number = await self.safe_extract_text(page, [
                'h1:has-text("Record ID")',
                'span[id*="RecordNumber"]',
                'td:has-text("Record Number") + td',
                '[id*="lblRecordNumber"]',
                'span[id*="PermitNumber"]'
            ])

            # Extract status from the page header
            permit_data.status = await self.safe_extract_text(page, [
                'h1:has-text("Record Status:")',
                'span[id*="RecordStatus"]',
                'td:has-text("Status") + td',
                '[id*="lblStatus"]',
                'span[id*="PermitStatus"]'
            ])

            # Clean up status text (remove "Record Status:" prefix)
            if permit_data.status and "Record Status:" in permit_data.status:
                permit_data.status = permit_data.status.replace("Record Status:", "").strip()

            permit_data.project_city = "San Diego County"  # Default for this portal

            # Extract contact information
            permit_data.project_company = await self.safe_extract_text(page, [
                'span[id*="ApplicantName"]',
                'td:has-text("Applicant") + td',
                '[id*="lblApplicant"]',
                'span[id*="CompanyName"]'
            ])

            permit_data.project_contact = await self.safe_extract_text(page, [
                'span[id*="ContactName"]',
                'td:has-text("Contact") + td',
                '[id*="lblContact"]',
                'span[id*="PrimaryContact"]'
            ])

            # Extract and standardize phone number
            raw_phone = await self.safe_extract_text(page, [
                'span[id*="Phone"]',
                'td:has-text("Phone") + td',
                '[id*="lblPhone"]',
                'span[id*="ContactPhone"]'
            ])
            permit_data.project_phone = self.standardize_phone(raw_phone)

            permit_data.project_email = await self.safe_extract_text(page, [
                'span[id*="Email"]',
                'td:has-text("Email") + td',
                '[id*="lblEmail"]',
                'span[id*="ContactEmail"]'
            ])

            # Extract address information (critical for geocoding)
            address = await self.safe_extract_text(page, [
                'span[id*="Address"]',
                'td:has-text("Address") + td',
                '[id*="lblAddress"]',
                'span[id*="SiteAddress"]',
                'span[id*="ProjectAddress"]'
            ])

            # Store address in the raw_data for now, will be processed later
            if address:
                permit_data.raw_data = permit_data.raw_data or {}
                permit_data.raw_data['address'] = address

            # Extract project description for material and quantity analysis
            project_description = await self.safe_extract_text(page, [
                'span[id*="WorkDescription"]',
                'td:has-text("Work Description") + td',
                '[id*="lblDescription"]',
                'span[id*="ProjectDescription"]',
                'h1:has-text("Project Description:")'
            ])

            permit_data.notes = project_description

            # Extract material type and quantity using NLP patterns
            if project_description:
                permit_data.material_description = self.extract_material_type(project_description)
                permit_data.quantity = self.extract_quantity(project_description)

            # Set metadata
            permit_data.scraped_at = datetime.now().isoformat()
            permit_data.raw_data = {
                'url': permit_url,
                'page_title': await page.title(),
                'extraction_timestamp': permit_data.scraped_at
            }

            logger.info(f"Successfully extracted data for permit: {permit_data.site_number}")
            return permit_data

        except Exception as e:
            logger.error(f"Error extracting permit data from {permit_url}: {str(e)}")
            return None
        finally:
            await page.close()
    
    async def safe_extract_text(self, page: Page, selectors: List[str]) -> Optional[str]:
        """Safely extract text using multiple selector fallbacks"""
        for selector in selectors:
            try:
                element = page.locator(selector).first
                if await element.count() > 0:
                    text = await element.text_content()
                    if text and text.strip():
                        return text.strip()
            except Exception:
                continue
        return None

    async def safe_extract_text_iframe(self, iframe, selectors: List[str]) -> Optional[str]:
        """Safely extract text from iframe using multiple selector fallbacks"""
        for selector in selectors:
            try:
                element = iframe.locator(selector).first
                if await element.count() > 0:
                    text = await element.text_content()
                    if text and text.strip():
                        return text.strip()
            except Exception:
                continue
        return None
    
    def standardize_phone(self, phone_text: Optional[str]) -> Optional[str]:
        """Standardize phone number to (XXX) XXX-XXXX format"""
        if not phone_text:
            return None
            
        # Extract digits only
        digits = re.sub(r'\D', '', phone_text)
        
        # Validate and format 10-digit US phone number
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        else:
            return phone_text  # Return original if can't standardize
    
    def extract_material_type(self, description: str) -> Optional[str]:
        """Extract material type using NLP and pattern matching"""
        if not description:
            return None
            
        description_lower = description.lower()
        
        # Material classification patterns from web scraper agent
        material_patterns = {
            'Clean Fill': ['clean fill', 'cf', 'fill material', 'import fill'],
            'Clay': ['clay', 'clay soil', 'cl', 'clay material'],
            'Grading': ['grading', 'grade', 'rough grading', 'fine grading'],
            'Stockpile': ['stockpile', 'stock pile', 'temporary storage'],
            'Export': ['export', 'removal', 'haul away'],
            'Import': ['import', 'bring in', 'delivery']
        }
        
        for material_type, patterns in material_patterns.items():
            if any(pattern in description_lower for pattern in patterns):
                return material_type
        
        return 'Other'  # Default classification
    
    def extract_quantity(self, description: str) -> Optional[float]:
        """Extract quantity from project description"""
        if not description:
            return None
            
        # Quantity extraction patterns from web scraper agent
        patterns = [
            r'(\d{1,3}(?:,\d{3})*)\s*(?:CY|cy|cubic yards?|yards?)',  # 70,000 CY
            r'(\d+[Kk])\s*(?:CY|cy)',  # 70K cy
            r'(\d+)\s*(?:tons?)',  # 50 tons
            r'(\d+[,\d]*)\s*(?:cubic|cu)',  # 50,000 cubic
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                quantity_str = match.group(1)
                
                # Handle K notation (70K -> 70000)
                if quantity_str.endswith(('K', 'k')):
                    return float(quantity_str[:-1]) * 1000
                
                # Remove commas and convert to float
                return float(quantity_str.replace(',', ''))
        
        return None  # No quantity found
    
    async def random_delay(self, min_seconds: float, max_seconds: float) -> None:
        """Add random delay to mimic human behavior"""
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)
    
    async def scrape_permits(self, search_criteria: Dict[str, str], max_permits: int = 50) -> List[PermitData]:
        """Main scraping method - extract permits based on search criteria"""
        try:
            await self.initialize_browser()
            
            # Search for permits
            permit_urls = await self.search_permits(search_criteria)
            
            if not permit_urls:
                logger.warning("No permits found matching search criteria")
                return []
            
            # Limit number of permits to scrape
            permit_urls = permit_urls[:max_permits]
            
            # Extract data from each permit
            extracted_permits = []
            for i, url in enumerate(permit_urls, 1):
                logger.info(f"Processing permit {i}/{len(permit_urls)}: {url}")
                
                permit_data = await self.extract_permit_data(url)
                if permit_data and permit_data.site_number:
                    extracted_permits.append(permit_data)
                
                # Add delay between requests
                await self.random_delay(3, 7)
            
            logger.info(f"Successfully extracted {len(extracted_permits)} permits")
            return extracted_permits
            
        except Exception as e:
            logger.error(f"Error in scrape_permits: {str(e)}")
            return []
        finally:
            await self.cleanup()
    
    async def cleanup(self) -> None:
        """Clean up browser resources"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        logger.info("Browser cleanup completed")

async def main():
    """Enhanced testing of the San Diego County scraper"""
    logger.info("=== Starting San Diego County Permit Scraper Test ===")
    scraper = SanDiegoCountyScraper()

    # Define search criteria for comprehensive data collection (2023 to present)
    search_criteria = {
        'permit_type': 'Grading Perm',  # Updated to use correct Accela value
        'date_from': '01/01/2023',     # MM/DD/YYYY format for Accela - comprehensive historical data
        'date_to': '08/11/2025'        # Current date range
    }

    logger.info(f"Search criteria: {search_criteria}")

    try:
        # Scrape permits (comprehensive collection - all available permits)
        logger.info("Starting comprehensive permit scraping process...")
        permits = await scraper.scrape_permits(search_criteria, max_permits=50)  # Increased limit for comprehensive data

        if permits:
            logger.info(f"✅ SUCCESS: Found {len(permits)} permits!")
            for i, permit in enumerate(permits, 1):
                logger.info(f"Permit {i}: {permit.site_number} - {permit.status}")
        else:
            logger.warning("⚠️ No permits found - this could be normal if no permits match criteria")

    except Exception as e:
        logger.error(f"❌ FAILED: Error during scraping: {e}")
        raise
    
    # Output results
    if permits:
        print(f"\nExtracted {len(permits)} permits:")
        for permit in permits:
            print(f"- {permit.site_number}: {permit.status} ({permit.material_description})")
            
        # Save to JSON file
        output_data = [asdict(permit) for permit in permits]
        with open('san_diego_permits.json', 'w') as f:
            json.dump(output_data, f, indent=2, default=str)

        print(f"\nData saved to san_diego_permits.json")

        # Enhanced integrations - Recommended: Direct to Supabase
        if SUPABASE_AVAILABLE:
            logger.info("🔗 Starting Supabase direct integration (RECOMMENDED)...")

            try:
                # Add geocoding information using enhanced service
                logger.info("🗺️ Adding enhanced geocoding information...")

                if ENHANCED_GEOCODING_AVAILABLE:
                    # Use enhanced multi-tiered geocoding service
                    geocoder = EnhancedGeocodingService()
                    geocoded_permits = []

                    for permit in output_data:
                        address = permit.get('address')
                        if address:
                            result = geocoder.geocode_address(address, min_confidence=0.7)
                            if result:
                                permit['coordinates'] = {
                                    'latitude': result.latitude,
                                    'longitude': result.longitude
                                }
                                permit['geocoding_accuracy'] = result.accuracy
                                permit['geocoding_confidence'] = result.confidence
                                permit['geocoding_source'] = result.source
                                permit['formatted_address'] = result.formatted_address

                                # Calculate distance and pricing if coordinates available
                                if result.latitude and result.longitude:
                                    # San Diego County depot coordinates (approximate)
                                    depot_lat, depot_lng = 32.7157, -117.1611

                                    # Calculate distance using Haversine formula
                                    from math import radians, sin, cos, sqrt, atan2
                                    lat1, lon1 = radians(depot_lat), radians(depot_lng)
                                    lat2, lon2 = radians(result.latitude), radians(result.longitude)

                                    dlat = lat2 - lat1
                                    dlon = lon2 - lon1
                                    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                                    c = 2 * atan2(sqrt(a), sqrt(1-a))
                                    distance_miles = 3956 * c  # Earth radius in miles

                                    # Calculate drive time and pricing
                                    roundtrip_minutes = int((distance_miles / 35) * 60 * 2 + 10)
                                    trucking_price = roundtrip_minutes * 1.83

                                    permit['distance_from_depot_miles'] = round(distance_miles, 2)
                                    permit['estimated_roundtrip_minutes'] = roundtrip_minutes
                                    permit['trucking_price_per_load'] = round(trucking_price, 2)

                        geocoded_permits.append(permit)

                    # Get geocoding statistics
                    stats = geocoder.get_statistics()
                    logger.info(f"🎯 Enhanced Geocoding Stats: {stats}")

                elif BASIC_GEOCODING_AVAILABLE:
                    # Fallback to basic geocoding
                    logger.info("⚠️ Using basic geocoding (enhanced service not available)")
                    geocoded_permits = add_geocoding_to_permits(output_data)
                else:
                    logger.warning("⚠️ No geocoding service available")
                    geocoded_permits = output_data

                # Save geocoded data
                with open('san_diego_permits_with_geocoding.json', 'w') as f:
                    json.dump(geocoded_permits, f, indent=2, default=str)
                logger.info("💾 Saved geocoded data to san_diego_permits_with_geocoding.json")

                # Upload directly to Supabase (RECOMMENDED APPROACH)
                logger.info("📤 Uploading directly to Supabase...")
                supabase = SupabaseDirectIntegration()
                results = supabase.batch_upsert_permits(geocoded_permits)

                logger.info("📊 Supabase Integration Summary:")
                logger.info(f"   🗺️ Geocoded: {sum(1 for p in geocoded_permits if 'coordinates' in p)}/{len(geocoded_permits)} permits")
                logger.info(f"   📤 Supabase upserts: {results['success']} success, {results['failed']} failed")

                # Optional: Also upload to Airtable for business users (if available)
                if AIRTABLE_AVAILABLE:
                    logger.info("📤 Optional: Also uploading to Airtable for business users...")
                    airtable = AirtableIntegration()
                    airtable_results = airtable.batch_upload_permits(geocoded_permits)
                    logger.info(f"   📤 Airtable uploads: {airtable_results['success']} success, {airtable_results['failed']} failed")

            except Exception as e:
                logger.error(f"❌ Integration error: {e}")
        else:
            logger.info("⚠️ Supabase integration not available. Install supabase client: pip install supabase")
    else:
        print("No permits extracted")

if __name__ == "__main__":
    asyncio.run(main())
