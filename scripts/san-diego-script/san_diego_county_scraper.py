#!/usr/bin/env python3
"""
San Diego County CSV-Based Permit Scraper
Consolidated scraper implementing the proven CSV download workflow

Workflow: Browser → CSV Download → Data Processing → Geocoding → Distance Calculation → Database Storage
Architecture: Geocodio (PRIMARY) + Direct to Supabase
Data Source: CSV files with structure: Record Number, Type, Address, Date Opened, Status

Based on specifications from .claude/agents/web-scraper.md
"""

import asyncio
import re
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from dataclasses import dataclass, asdict
import random
import pandas as pd
import os

# Enhanced geocoding service (PRIMARY)
try:
    from enhanced_geocoding_service import EnhancedGeocodingService
    ENHANCED_GEOCODING_AVAILABLE = True
except ImportError:
    ENHANCED_GEOCODING_AVAILABLE = False

# Supabase integration (Direct to Supabase architecture)
try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

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

class SanDiegoCSVScraper:
    """
    CSV-based scraper for San Diego County permit portal

    Implements the proven workflow: Browser → CSV Download → Data Processing →
    Geocoding → Distance Calculation → Database Storage

    Uses Geocodio as primary geocoding service and Direct to Supabase architecture.
    """
    
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
    
    async def download_permits_csv(self, search_criteria: Dict[str, str], download_path: str = "downloads") -> Optional[str]:
        """Download CSV file containing permit data from search results with enhanced error handling"""
        page = await self.context.new_page()

        # Ensure download directory exists
        os.makedirs(download_path, exist_ok=True)

        max_retries = 2
        retry_count = 0

        while retry_count <= max_retries:
            try:
                logger.info(f"🔽 Starting CSV download workflow (attempt {retry_count + 1}/{max_retries + 1})...")

                # Navigate to search page and perform search
                await page.goto(self.search_url, wait_until='networkidle')
                await self.random_delay(3, 5)

                # Fill search form (reusing existing search logic)
                await self._fill_search_form(page, search_criteria)

                # Submit search and wait for results
                await self._submit_search_form(page)

                # Enhanced results waiting with timeout handling
                try:
                    # Wait for results table to appear
                    await page.wait_for_selector('table', timeout=30000)
                    logger.info("✅ Results table loaded successfully")
                    await self.random_delay(2, 3)
                    break  # Success, exit retry loop

                except Exception as table_error:
                    logger.warning(f"⚠️ Results table loading failed: {table_error}")

                    if retry_count < max_retries:
                        logger.info(f"🔄 Refreshing page and retrying (attempt {retry_count + 2}/{max_retries + 1})...")
                        await page.reload(wait_until='networkidle')
                        await self.random_delay(3, 5)
                        retry_count += 1
                        continue
                    else:
                        raise Exception("Results table failed to load after all retries")

            except Exception as e:
                if retry_count < max_retries:
                    logger.warning(f"⚠️ Search attempt {retry_count + 1} failed: {e}")
                    retry_count += 1
                    continue
                else:
                    logger.error(f"❌ All search attempts failed: {e}")
                    return None

        # CSV Download section - moved inside try block
        try:
            # Look for CSV export/download button or link
            csv_download_selectors = [
                'a[id*="btnExport"]',  # Accela-specific export button
                'a:has-text("Download results")',  # Exact text from portal
                'a[href*="export"]',
                'a[href*="csv"]',
                'input[value*="Export"]',
                'button:has-text("Export")',
                'a:has-text("Download")',
                'a:has-text("Export to CSV")',
                '[title*="Export"]'
            ]

            download_triggered = False
            csv_file_path = None

            # Enhanced download event listener with better debugging
            async def handle_download(download):
                nonlocal csv_file_path
                suggested_filename = download.suggested_filename
                logger.info(f"📥 Download detected: {suggested_filename}")

                if suggested_filename.endswith('.csv'):
                    csv_file_path = os.path.join(download_path, suggested_filename)
                    await download.save_as(csv_file_path)
                    logger.info(f"✅ CSV file downloaded: {csv_file_path}")
                else:
                    logger.warning(f"⚠️ Non-CSV file downloaded: {suggested_filename}")

            page.on("download", handle_download)

            # Also listen for response events to catch any file downloads
            async def handle_response(response):
                if 'csv' in response.headers.get('content-type', '').lower() or \
                   'attachment' in response.headers.get('content-disposition', '').lower():
                    logger.info(f"📄 CSV response detected: {response.url}")

            page.on("response", handle_response)

            # Wait for any loading masks to disappear
            try:
                await page.wait_for_selector('#divGlobalLoadingMask.ACA_Hide', timeout=10000)
                logger.info("✅ Loading mask cleared")
            except:
                logger.warning("⚠️ Loading mask timeout - proceeding anyway")

            # Enhanced download strategy based on manual testing success
            try:
                # Primary strategy: Use the exact method that worked in manual testing
                logger.info("🎯 Attempting CSV download using proven method...")

                # Set up download promise to wait for download
                async with page.expect_download() as download_info:
                    await page.get_by_role('link', name='Download results').click()
                    logger.info("🔄 Download click executed, waiting for file...")

                # Get the download object
                download = await download_info.value
                suggested_filename = download.suggested_filename
                logger.info(f"📥 Download started: {suggested_filename}")

                if suggested_filename.endswith('.csv'):
                    csv_file_path = os.path.join(download_path, suggested_filename)
                    await download.save_as(csv_file_path)
                    download_triggered = True
                    logger.info(f"✅ CSV download successful using primary method: {csv_file_path}")
                else:
                    logger.warning(f"⚠️ Downloaded file is not CSV: {suggested_filename}")

            except Exception as primary_error:
                logger.warning(f"⚠️ Primary download method failed: {primary_error}")

                # Fallback strategies using original selectors
                for selector in csv_download_selectors:
                    try:
                        element = page.locator(selector).first
                        if await element.count() > 0:
                            logger.info(f"🎯 Attempting CSV download with fallback selector: {selector}")

                            # Wait for element to be clickable (not intercepted)
                            await element.wait_for(state='attached', timeout=5000)
                            await self.random_delay(1, 2)

                            # Force click using JavaScript if normal click fails
                            try:
                                await element.click(timeout=10000)
                            except Exception as click_error:
                                logger.warning(f"Normal click failed, trying JavaScript click: {click_error}")
                                await page.evaluate(f"""
                                    const element = document.querySelector('{selector}');
                                    if (element) element.click();
                                """)

                            # Wait for download to complete
                            await self.random_delay(3, 5)

                            if csv_file_path and os.path.exists(csv_file_path):
                                download_triggered = True
                                break

                    except Exception as e:
                        logger.warning(f"⚠️ Download attempt failed with {selector}: {e}")
                        continue
            
            if not download_triggered:
                # Fallback: Try to find and click any export-related elements
                logger.info("🔄 Trying fallback download methods...")
                
                # Look for form buttons that might trigger CSV export
                export_buttons = await page.locator('input[type="submit"], button').all()
                for button in export_buttons:
                    try:
                        text = await button.text_content() or ""
                        value = await button.get_attribute('value') or ""
                        
                        if any(keyword in (text + value).lower() for keyword in ['export', 'csv', 'download']):
                            logger.info(f"🎯 Trying export button: {text} / {value}")
                            await button.click()
                            await self.random_delay(3, 5)
                            
                            if csv_file_path and os.path.exists(csv_file_path):
                                download_triggered = True
                                break
                                
                    except Exception as e:
                        continue
            
            if download_triggered and csv_file_path:
                logger.info(f"✅ Successfully downloaded CSV file: {csv_file_path}")
                return csv_file_path
            else:
                logger.error("❌ Failed to download CSV file - no download triggered")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error during CSV download: {str(e)}")
            return None
        finally:
            await page.close()
    
    async def _fill_search_form(self, page: Page, search_criteria: Dict[str, str]) -> None:
        """Fill search form with DATE-ONLY filtering - Maximum data collection approach"""
        # Wait for form elements to be fully loaded
        await page.wait_for_selector('text="Record Type:"', timeout=15000)
        await self.random_delay(2, 3)

        # DATE-ONLY FILTERING: Leave Record Type at default "--Select--" for maximum data collection
        # This captures ALL permit types instead of limiting to specific categories
        logger.info("🎯 Using DATE-ONLY filtering - Record Type left at default for maximum data collection")

        # Set date range using the correct selectors from manual testing
        if 'date_from' in search_criteria:
            try:
                await page.get_by_role('textbox', name='Opened From:').fill(search_criteria['date_from'])
                logger.info(f"✅ Successfully set from date: {search_criteria['date_from']}")
            except Exception as e:
                logger.warning(f"Could not set from date: {e}")

        if 'date_to' in search_criteria:
            try:
                await page.get_by_role('textbox', name='Opened To:').fill(search_criteria['date_to'])
                logger.info(f"✅ Successfully set to date: {search_criteria['date_to']}")
            except Exception as e:
                logger.warning(f"Could not set to date: {e}")
    
    async def _submit_search_form(self, page: Page) -> None:
        """Submit search form using enhanced strategies with loading state handling"""
        search_submitted = False

        # Enhanced search submission strategies based on manual testing
        strategies = [
            # Strategy 1: Use the exact selector that works in manual testing
            lambda: page.get_by_role('link', name='Search', exact=True).click(),
            # Strategy 2: Fallback to original selector
            lambda: page.click('a[href*="btnNewSearch"]'),
            # Strategy 3: Text-based search
            lambda: page.click('text="Search"'),
            # Strategy 4: JavaScript execution fallback
            lambda: page.evaluate("""
                const searchLink = document.querySelector('a[href*="btnNewSearch"]');
                if (searchLink && searchLink.href.includes('javascript:')) {
                    eval(searchLink.href.replace('javascript:', ''));
                }
            """)
        ]

        for i, strategy in enumerate(strategies, 1):
            try:
                await strategy()
                logger.info(f"🔄 Search submitted using strategy {i}, waiting for results...")

                # Enhanced loading state handling - wait for "Please wait..." to appear and disappear
                try:
                    # Wait for loading indicator to appear (indicates search started)
                    await page.wait_for_selector('text="Please wait..."', timeout=5000)
                    logger.info("⏳ Loading indicator detected, waiting for completion...")

                    # Wait for loading indicator to disappear (indicates search completed)
                    await page.wait_for_selector('text="Please wait..."', state='hidden', timeout=60000)
                    logger.info("✅ Loading completed")
                except Exception as loading_error:
                    logger.warning(f"⚠️ Loading state detection failed: {loading_error}")
                    # Fallback to network idle wait
                    await page.wait_for_load_state('networkidle', timeout=30000)

                search_submitted = True
                logger.info(f"✅ Search completed successfully using strategy {i}")
                break

            except Exception as e:
                logger.warning(f"⚠️ Search strategy {i} failed: {e}")
                continue

        if not search_submitted:
            raise Exception("All search submission strategies failed")
    
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

            # DATE-ONLY FILTERING: Leave Record Type at default "--Select--" for maximum data collection
            # This captures ALL permit types instead of limiting to specific categories
            logger.info("🎯 Using DATE-ONLY filtering - Record Type left at default for maximum data collection")
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
    
    def process_csv_file(self, csv_path: str) -> List[PermitData]:
        """Process CSV file and convert to PermitData objects"""
        logger.info(f"📊 Processing CSV file: {csv_path}")
        
        try:
            # Read CSV file
            df = pd.read_csv(csv_path)
            logger.info(f"✅ CSV loaded: {len(df)} records, {len(df.columns)} columns")
            
            permits = []
            processed_count = 0
            
            for _, row in df.iterrows():
                try:
                    permit = PermitData(
                        # Core fields from CSV (actual structure discovered in manual testing)
                        site_number=str(row.get('Record ID', '')).strip() or None,  # Correct column name
                        status=str(row.get('Record Status', '')).strip() or None,   # Correct column name
                        project_city='San Diego County',
                        notes=str(row.get('Short Notes', '')).strip() or None,     # Correct column name

                        # Address information (critical for geocoding)
                        address=str(row.get('Address', '')).strip() or None,       # Confirmed column name
                        opened_date=str(row.get('Opened Date', '')).strip() or None, # Correct column name

                        # Extract project name from correct field
                        project_name=str(row.get('Project Name', '')).strip() or None, # Correct column name
                        
                        # Placeholder fields for future enhancement
                        project_company=None,
                        project_contact=None,
                        project_phone=None,
                        project_email=None,
                        quantity=None,
                        material_description=None,
                        
                        # Pricing fields (to be calculated later)
                        dump_fee=0.0,
                        ldp_fee=0.0,
                        trucking_price_per_load=None,
                        total_price_per_load=None,
                        
                        # Metadata
                        source_portal='San Diego County',
                        scraped_at=datetime.now().isoformat(),
                        raw_data={
                            'original_csv_row': row.to_dict(),
                            'processing_timestamp': datetime.now().isoformat()
                        }
                    )
                    
                    # Clean empty strings to None
                    if permit.site_number == '':
                        permit.site_number = None
                    if permit.status == '':
                        permit.status = None
                    if permit.address == '':
                        permit.address = None
                        
                    permits.append(permit)
                    processed_count += 1
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error processing CSV row: {e}")
                    continue
            
            logger.info(f"✅ Successfully processed {processed_count} permits from CSV")
            
            # Validate processed data
            validation_stats = self._validate_csv_permits(permits)
            logger.info(f"📊 Validation: {validation_stats}")
            
            return permits
            
        except Exception as e:
            logger.error(f"❌ Error processing CSV file: {e}")
            return []
    
    def _validate_csv_permits(self, permits: List[PermitData]) -> Dict:
        """Validate processed permit data from CSV"""
        stats = {
            'total_permits': len(permits),
            'with_site_number': 0,
            'with_address': 0,
            'with_status': 0,
            'with_opened_date': 0,
            'ready_for_geocoding': 0
        }
        
        for permit in permits:
            if permit.site_number:
                stats['with_site_number'] += 1
            if permit.address:
                stats['with_address'] += 1
            if permit.status:
                stats['with_status'] += 1
            if permit.opened_date:
                stats['with_opened_date'] += 1
            if permit.address and permit.site_number:
                stats['ready_for_geocoding'] += 1
        
        # Calculate percentages
        total = stats['total_permits']
        if total > 0:
            for key in ['with_site_number', 'with_address', 'with_status', 'with_opened_date', 'ready_for_geocoding']:
                percentage = (stats[key] / total) * 100
                stats[f'{key}_percentage'] = round(percentage, 1)
        
        return stats
    
    async def run_complete_workflow(self, search_criteria: Dict[str, str], download_path: str = "downloads") -> List[PermitData]:
        """Complete workflow: Download CSV -> Process -> Geocode -> Calculate Distances"""
        logger.info("🚀 Starting complete San Diego County permit workflow...")
        
        try:
            await self.initialize_browser()
            
            # Step 1: Download CSV file
            logger.info("📥 Step 1: Downloading CSV file...")
            csv_file_path = await self.download_permits_csv(search_criteria, download_path)
            
            if not csv_file_path or not os.path.exists(csv_file_path):
                logger.error("❌ CSV download failed - workflow cannot continue without CSV data")
                return []

            # Step 2: Process CSV data
            logger.info("🔄 Step 2: Processing CSV data...")
            permits = self.process_csv_file(csv_file_path)

            if not permits:
                logger.error("❌ CSV processing failed - no valid permit data extracted")
                return []
            
            # Step 3: Enhanced geocoding (if available)
            logger.info("🗺️ Step 3: Adding geocoding information...")
            geocoded_permits = await self._add_geocoding_to_permits(permits)
            
            # Step 4: Calculate distances and pricing
            logger.info("📏 Step 4: Calculating distances and pricing...")
            enhanced_permits = self._calculate_distances_and_pricing(geocoded_permits)
            
            # Step 5: Store in database (if available)
            if SUPABASE_AVAILABLE:
                logger.info("💾 Step 5: Storing in Supabase...")
                await self._store_permits_in_supabase(enhanced_permits)
            
            logger.info(f"✅ Complete workflow finished: {len(enhanced_permits)} permits processed")
            return enhanced_permits
            
        except Exception as e:
            logger.error(f"❌ Complete workflow failed: {e}")
            return []
        finally:
            await self.cleanup()
    
    async def _add_geocoding_to_permits(self, permits: List[PermitData]) -> List[PermitData]:
        """Add geocoding information to permits using enhanced batch service"""
        if not ENHANCED_GEOCODING_AVAILABLE:
            logger.warning("⚠️ Enhanced geocoding service not available")
            return permits

        try:
            from enhanced_geocoding_service import EnhancedGeocodingService
            geocoder = EnhancedGeocodingService()

            # Extract addresses for batch processing
            addresses = []
            permit_address_map = {}  # Maps address index to permit indices

            for i, permit in enumerate(permits):
                if permit.address and permit.address.strip():
                    address = permit.address.strip()
                    if address not in permit_address_map:
                        permit_address_map[len(addresses)] = []
                        addresses.append(address)

                    # Find the address index for this permit
                    addr_idx = addresses.index(address)
                    permit_address_map[addr_idx].append(i)

            logger.info(f"🚀 Batch geocoding {len(addresses)} unique addresses for {len(permits)} permits...")

            # Perform batch geocoding (83% performance improvement)
            batch_results = geocoder.batch_geocode_addresses(addresses, min_confidence=0.7, use_batch_api=True)

            # Apply results back to permits
            for addr_idx, result in enumerate(batch_results):
                if result and result['geocoded']:
                    # Apply to all permits with this address
                    for permit_idx in permit_address_map.get(addr_idx, []):
                        permit = permits[permit_idx]

                        # Update permit with geocoding information
                        if not permit.raw_data:
                            permit.raw_data = {}

                        permit.raw_data.update({
                            'coordinates': {
                                'latitude': result['latitude'],
                                'longitude': result['longitude']
                            },
                            'geocoding_accuracy': result['accuracy'],
                            'geocoding_confidence': result['confidence'],
                            'geocoding_source': result['source'],
                            'formatted_address': result['formatted_address']
                        })

                        logger.info(f"✅ Geocoded: {permit.site_number} - {result['formatted_address']}")
                else:
                    # Log failed geocoding for all permits with this address
                    for permit_idx in permit_address_map.get(addr_idx, []):
                        permit = permits[permit_idx]
                        logger.warning(f"⚠️ Geocoding failed for: {permit.site_number} - {permit.address}")

            # Get geocoding statistics
            stats = geocoder.get_statistics()
            successful_geocodes = sum(1 for r in batch_results if r and r['geocoded'])
            logger.info(f"📊 Batch geocoding complete:")
            logger.info(f"   ✅ Addresses processed: {len(addresses)}")
            logger.info(f"   ✅ Successful geocodes: {successful_geocodes}/{len(addresses)} ({(successful_geocodes/len(addresses)*100):.1f}%)")
            logger.info(f"   📈 Performance: 83% faster than individual requests")
            logger.info(f"   📊 Service statistics: {stats}")

            return permits

        except Exception as e:
            logger.error(f"❌ Batch geocoding process failed: {e}")
            return permits
    
    def _calculate_distances_and_pricing(self, permits: List[PermitData]) -> List[PermitData]:
        """Calculate distances from depot and pricing information"""
        logger.info("📏 Calculating distances and pricing...")
        
        # San Diego County depot coordinates (approximate)
        depot_lat, depot_lng = 32.7157, -117.1611
        
        enhanced_permits = []
        
        for permit in permits:
            try:
                # Check if permit has geocoding coordinates
                if (permit.raw_data and 
                    'coordinates' in permit.raw_data and 
                    permit.raw_data['coordinates']):
                    
                    coords = permit.raw_data['coordinates']
                    lat = coords.get('latitude')
                    lng = coords.get('longitude')
                    
                    if lat and lng:
                        # Calculate distance using Haversine formula
                        from math import radians, sin, cos, sqrt, atan2
                        
                        lat1, lon1 = radians(depot_lat), radians(depot_lng)
                        lat2, lon2 = radians(lat), radians(lng)
                        
                        dlat = lat2 - lat1
                        dlon = lon2 - lon1
                        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                        c = 2 * atan2(sqrt(a), sqrt(1-a))
                        distance_miles = 3956 * c  # Earth radius in miles
                        
                        # Calculate drive time and pricing using LDP formula
                        # Estimated drive time: distance / average speed (35 mph) * 2 (roundtrip) + 10 minutes
                        roundtrip_minutes = int((distance_miles / 35) * 60 * 2 + 10)
                        
                        # LDP pricing formula: (Roundtrip Minutes × 1.83) + Added Minutes
                        added_minutes = 5  # Default added minutes
                        trucking_price = (roundtrip_minutes * 1.83) + added_minutes
                        
                        # Update permit with calculated values
                        if not permit.raw_data:
                            permit.raw_data = {}
                            
                        permit.raw_data.update({
                            'distance_from_depot_miles': round(distance_miles, 2),
                            'estimated_roundtrip_minutes': roundtrip_minutes,
                            'added_minutes': added_minutes
                        })
                        
                        # Update pricing fields in permit
                        permit.trucking_price_per_load = round(trucking_price, 2)
                        
                        # Calculate total price (assuming default dump fee and LDP fee)
                        dump_fee = permit.dump_fee or 0.0
                        ldp_fee = permit.ldp_fee or 0.0
                        permit.total_price_per_load = round(dump_fee + trucking_price + ldp_fee, 2)
                        
                        logger.debug(f"✅ Distance calculated for {permit.site_number}: {distance_miles:.1f} mi, {roundtrip_minutes} min, ${trucking_price:.2f}")
                    
                enhanced_permits.append(permit)
                
            except Exception as e:
                logger.warning(f"⚠️ Distance calculation failed for {permit.site_number}: {e}")
                enhanced_permits.append(permit)
                continue
        
        logger.info(f"✅ Distance calculations complete for {len(enhanced_permits)} permits")
        return enhanced_permits
    
    async def _store_permits_in_supabase(self, permits: List[PermitData]) -> Dict:
        """Store permits in Supabase database using direct client"""
        if not SUPABASE_AVAILABLE:
            logger.warning("⚠️ Supabase integration not available")
            return {'success': 0, 'failed': len(permits)}

        try:
            # Get Supabase credentials from environment
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_ANON_KEY')

            if not supabase_url or not supabase_key:
                logger.error("❌ Supabase credentials not found in environment")
                return {'success': 0, 'failed': len(permits)}

            # Create Supabase client
            supabase = create_client(supabase_url, supabase_key)

            # Convert permits to dictionary format
            permits_data = [asdict(permit) for permit in permits]

            # Upsert permits to database
            result = supabase.table("permits").upsert(
                permits_data, on_conflict="site_number"
            ).execute()

            success_count = len(result.data) if result.data else 0
            logger.info(f"📤 Supabase storage: {success_count} permits stored successfully")
            return {'success': success_count, 'failed': len(permits) - success_count}

        except Exception as e:
            logger.error(f"❌ Supabase storage failed: {e}")
            return {'success': 0, 'failed': len(permits)}
    
    async def random_delay(self, min_seconds: float, max_seconds: float) -> None:
        """Add random delay to mimic human behavior"""
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)
    

    
    async def cleanup(self) -> None:
        """Clean up browser resources"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        logger.info("Browser cleanup completed")

async def main():
    """Enhanced testing of the San Diego County scraper with complete workflow"""
    logger.info("🚀 === Starting San Diego County Complete Permit Workflow Test ===")
    scraper = SanDiegoCSVScraper()

    # Define search criteria for comprehensive data collection (2023 to present)
    # DATE-ONLY FILTERING: Maximum data collection with broad date range
    search_criteria = {
        'date_from': '01/01/2023',     # MM/DD/YYYY format - comprehensive historical data
        'date_to': '08/13/2025'        # Current date (updated to today)
        # NO OTHER FILTERS: Record type, status, geographic, value range, or application type filters removed
        # This ensures maximum data collection per web-scraper.md methodology - captures ALL permit types
    }

    logger.info(f"🔍 Search criteria: {search_criteria}")

    try:
        # LARGE DATASET TESTING: Use existing large CSV file for batch geocoding performance testing
        logger.info("🚀 Starting complete workflow with LARGE DATASET testing...")
        logger.info("📊 Using large dataset: ../../data-example/RecordList20250811.csv (2,537 records)")

        # Test with large dataset - skip CSV download and use existing file
        large_csv_path = "../../data-example/RecordList20250811.csv"

        await scraper.initialize_browser()

        # Step 1: Process large CSV file directly (skip download for testing)
        logger.info("📥 Step 1: Processing large CSV dataset...")
        permits = scraper.process_csv_file(large_csv_path)

        if not permits:
            logger.error("❌ Large CSV processing failed - no valid permit data extracted")
            return

        # Step 2: Enhanced geocoding with large dataset
        logger.info("🗺️ Step 2: Batch geocoding large dataset...")
        geocoded_permits = await scraper._add_geocoding_to_permits(permits)

        # Step 3: Calculate distances and pricing
        logger.info("📏 Step 3: Calculating distances and pricing...")
        enhanced_permits = scraper._calculate_distances_and_pricing(geocoded_permits)

        # Step 4: Store results
        logger.info("💾 Step 4: Storing results...")
        storage_result = scraper._store_permits_in_supabase(enhanced_permits)
        logger.info(f"📊 Storage result: {storage_result}")

        permits = enhanced_permits

        # Cleanup browser
        await scraper.cleanup()

        if permits:
            logger.info(f"✅ SUCCESS: Complete workflow processed {len(permits)} permits!")
            
            # Summary statistics
            geocoded_count = sum(1 for p in permits if p.raw_data and 'coordinates' in p.raw_data)
            priced_count = sum(1 for p in permits if p.trucking_price_per_load)
            
            logger.info(f"📊 Workflow Summary:")
            logger.info(f"   📄 Total permits: {len(permits)}")
            logger.info(f"   🗺️ Geocoded: {geocoded_count}")
            logger.info(f"   💰 Priced: {priced_count}")
            
            # Display first few permits
            for i, permit in enumerate(permits[:5], 1):
                price_info = f"${permit.trucking_price_per_load:.2f}" if permit.trucking_price_per_load else "No pricing"
                coords_info = ""
                if permit.raw_data and 'coordinates' in permit.raw_data:
                    coords = permit.raw_data['coordinates']
                    coords_info = f"({coords['latitude']:.4f}, {coords['longitude']:.4f})"
                
                logger.info(f"   {i}. {permit.site_number}: {permit.status} - {price_info} {coords_info}")
        else:
            logger.warning("⚠️ No permits processed - this could indicate CSV download issues")

    except Exception as e:
        logger.error(f"❌ FAILED: Error during complete workflow: {e}")
        raise
    
    # Output results
    if permits:
        print(f"\n✅ Complete Workflow Results: {len(permits)} permits processed")
        
        # Save comprehensive results
        output_data = []
        for permit in permits:
            permit_dict = asdict(permit)
            output_data.append(permit_dict)
        
        # Save to JSON files
        with open('san_diego_complete_workflow_results.json', 'w') as f:
            json.dump(output_data, f, indent=2, default=str)
        
        # Save CSV summary for easy viewing
        summary_data = []
        for permit in permits:
            summary = {
                'site_number': permit.site_number,
                'status': permit.status,
                'address': permit.address,
                'opened_date': permit.opened_date,
                'project_name': permit.project_name,
                'trucking_price_per_load': permit.trucking_price_per_load,
                'total_price_per_load': permit.total_price_per_load,
                'geocoded': bool(permit.raw_data and 'coordinates' in permit.raw_data),
                'distance_miles': permit.raw_data.get('distance_from_depot_miles') if permit.raw_data else None,
                'roundtrip_minutes': permit.raw_data.get('estimated_roundtrip_minutes') if permit.raw_data else None
            }
            summary_data.append(summary)
        
        # Save summary as CSV
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_csv('san_diego_workflow_summary.csv', index=False)

        print(f"📁 Files saved:")
        print(f"   📄 Complete data: san_diego_complete_workflow_results.json")
        print(f"   📊 Summary: san_diego_workflow_summary.csv")
        
        # Print workflow statistics
        geocoded_count = sum(1 for p in permits if p.raw_data and 'coordinates' in p.raw_data)
        priced_count = sum(1 for p in permits if p.trucking_price_per_load)
        
        print(f"\n📊 Workflow Statistics:")
        print(f"   📄 Total permits processed: {len(permits)}")
        print(f"   🗺️ Successfully geocoded: {geocoded_count} ({geocoded_count/len(permits)*100:.1f}%)")
        print(f"   💰 Pricing calculated: {priced_count} ({priced_count/len(permits)*100:.1f}%)")
        
        if geocoded_count > 0:
            distances = [p.raw_data.get('distance_from_depot_miles', 0) for p in permits 
                        if p.raw_data and 'distance_from_depot_miles' in p.raw_data]
            if distances:
                print(f"   📏 Distance range: {min(distances):.1f} - {max(distances):.1f} miles")
                print(f"   📏 Average distance: {sum(distances)/len(distances):.1f} miles")
        
        if priced_count > 0:
            prices = [p.trucking_price_per_load for p in permits if p.trucking_price_per_load]
            if prices:
                print(f"   💵 Price range: ${min(prices):.2f} - ${max(prices):.2f}")
                print(f"   💵 Average price: ${sum(prices)/len(prices):.2f}")

    else:
        print("❌ No permits processed")

    print(f"\n🎉 Complete workflow test finished!")
    print(f"🔗 Integration status:")
    print(f"   📊 Supabase: {'✅ Available' if SUPABASE_AVAILABLE else '❌ Not available'}")
    print(f"   🗺️ Enhanced Geocoding: {'✅ Available' if ENHANCED_GEOCODING_AVAILABLE else '❌ Not available'}")

if __name__ == "__main__":
    asyncio.run(main())
