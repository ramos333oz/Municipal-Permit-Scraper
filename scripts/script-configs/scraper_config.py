#!/usr/bin/env python3
"""
Scraper Configuration and Utilities
Configuration settings and utility functions for municipal permit scrapers

Based on specifications from .claude/agents/web-scraper.md
Supports: Multiple municipal portals with intelligent tool selection
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import os

@dataclass
class PortalConfig:
    """Configuration for a specific municipal portal"""
    name: str
    base_url: str
    search_url: str
    portal_type: str  # 'accela', 'etrakiT', 'custom'
    selectors: Dict[str, List[str]]
    search_form: Dict[str, str]
    rate_limit_delay: tuple  # (min_seconds, max_seconds)
    requires_auth: bool = False
    auth_url: Optional[str] = None

class ScraperConfigurations:
    """Central configuration for all municipal portal scrapers"""
    
    @staticmethod
    def get_san_diego_county_config() -> PortalConfig:
        """San Diego County Accela portal configuration"""
        return PortalConfig(
            name="San Diego County",
            base_url="https://publicservices.sandiegocounty.gov",
            search_url="https://publicservices.sandiegocounty.gov/CitizenAccess/Cap/CapHome.aspx?module=LUEG-PDS",
            portal_type="accela",
            selectors={
                'site_number': [
                    'span[id*="RecordNumber"]',
                    'td:has-text("Record Number") + td',
                    '[id*="lblRecordNumber"]',
                    'span[id*="PermitNumber"]'
                ],
                'status': [
                    'span[id*="RecordStatus"]',
                    'td:has-text("Status") + td',
                    '[id*="lblStatus"]',
                    'span[id*="PermitStatus"]'
                ],
                'project_company': [
                    'span[id*="ApplicantName"]',
                    'td:has-text("Applicant") + td',
                    '[id*="lblApplicant"]',
                    'span[id*="CompanyName"]'
                ],
                'project_contact': [
                    'span[id*="ContactName"]',
                    'td:has-text("Contact") + td',
                    '[id*="lblContact"]',
                    'span[id*="PrimaryContact"]'
                ],
                'project_phone': [
                    'span[id*="Phone"]',
                    'td:has-text("Phone") + td',
                    '[id*="lblPhone"]',
                    'span[id*="ContactPhone"]'
                ],
                'project_email': [
                    'span[id*="Email"]',
                    'td:has-text("Email") + td',
                    '[id*="lblEmail"]',
                    'span[id*="ContactEmail"]'
                ],
                'project_description': [
                    'span[id*="WorkDescription"]',
                    'td:has-text("Work Description") + td',
                    '[id*="lblDescription"]',
                    'span[id*="ProjectDescription"]'
                ],
                'address': [
                    'span[id*="Address"]',
                    'td:has-text("Address") + td',
                    '[id*="lblAddress"]',
                    'span[id*="SiteAddress"]'
                ]
            },
            search_form={
                'record_type_selector': 'combobox[aria-label*="Record Type"]',
                'date_from_selector': 'input[name*="txtGSDateFrom"]',
                'date_to_selector': 'input[name*="txtGSDateTo"]',
                'search_button': 'link:has-text("Search")',
                'results_container': 'table',
                'results_text': 'text="Record results"'
            },
            rate_limit_delay=(3, 7),
            requires_auth=False
        )
    
    @staticmethod
    def get_ontario_config() -> PortalConfig:
        """Ontario Accela portal configuration"""
        return PortalConfig(
            name="Ontario",
            base_url="https://www.ontarioca.gov",
            search_url="https://www.ontarioca.gov/permits",
            portal_type="accela",
            selectors={
                'site_number': [
                    '[data-field="permit_number"]',
                    '#permitNumber',
                    '.permit-id',
                    'td:has-text("Permit ID") + td'
                ],
                'status': [
                    '[data-field="status"]',
                    '#permitStatus',
                    '.permit-status',
                    'td:has-text("Status") + td'
                ],
                'project_company': [
                    '[data-field="contractor"]',
                    '#contractor',
                    '.contractor-name',
                    'td:has-text("Contractor") + td'
                ],
                'project_contact': [
                    '[data-field="contact"]',
                    '#contactName',
                    '.contact-name',
                    'td:has-text("Contact") + td'
                ],
                'project_phone': [
                    '[data-field="phone"]',
                    '#contactPhone',
                    '.contact-phone',
                    'td:has-text("Phone") + td'
                ],
                'project_email': [
                    '[data-field="email"]',
                    '#contactEmail',
                    '.contact-email',
                    'td:has-text("Email") + td'
                ],
                'project_description': [
                    '[data-field="description"]',
                    '#workDescription',
                    '.work-description',
                    'td:has-text("Work Description") + td'
                ],
                'address': [
                    '[data-field="address"]',
                    '#projectAddress',
                    '.project-address',
                    'td:has-text("Project Address") + td'
                ]
            },
            search_form={
                'permit_type_selector': '#permitType',
                'date_from_selector': '#dateFrom',
                'date_to_selector': '#dateTo',
                'search_button': '.search-btn',
                'results_container': '.search-results'
            },
            rate_limit_delay=(2, 5),
            requires_auth=False
        )
    
    @staticmethod
    def get_orange_county_config() -> PortalConfig:
        """Orange County portal configuration (requires authentication)"""
        return PortalConfig(
            name="Orange County",
            base_url="https://www.ocpermits.com",
            search_url="https://www.ocpermits.com/search",
            portal_type="custom",
            selectors={
                'site_number': [
                    '#permit-number',
                    '.permit-id',
                    'td:has-text("Permit Number") + td'
                ],
                'status': [
                    '#permit-status',
                    '.status-field',
                    'td:has-text("Status") + td'
                ],
                'project_company': [
                    '#applicant-company',
                    '.company-field',
                    'td:has-text("Company") + td'
                ],
                'project_contact': [
                    '#applicant-name',
                    '.contact-field',
                    'td:has-text("Applicant") + td'
                ],
                'project_phone': [
                    '#contact-phone',
                    '.phone-field',
                    'td:has-text("Phone") + td'
                ],
                'project_email': [
                    '#contact-email',
                    '.email-field',
                    'td:has-text("Email") + td'
                ],
                'project_description': [
                    '#project-description',
                    '.description-field',
                    'td:has-text("Description") + td'
                ],
                'address': [
                    '#project-address',
                    '.address-field',
                    'td:has-text("Address") + td'
                ]
            },
            search_form={
                'permit_type_selector': '#permit-type',
                'date_from_selector': '#start-date',
                'date_to_selector': '#end-date',
                'search_button': '#search-submit',
                'results_container': '#search-results'
            },
            rate_limit_delay=(4, 8),
            requires_auth=True,
            auth_url="https://www.ocpermits.com/login"
        )

class MaterialClassificationPatterns:
    """Material classification patterns for NLP extraction"""
    
    PATTERNS = {
        'Clean Fill': [
            'clean fill', 'cf', 'fill material', 'import fill',
            'clean dirt', 'fill dirt', 'structural fill'
        ],
        'Clay': [
            'clay', 'clay soil', 'cl', 'clay material',
            'clay fill', 'clay dirt', 'clayey soil'
        ],
        'Grading': [
            'grading', 'grade', 'rough grading', 'fine grading',
            'site grading', 'mass grading', 'precise grading'
        ],
        'Stockpile': [
            'stockpile', 'stock pile', 'temporary storage',
            'material storage', 'soil stockpile'
        ],
        'Export': [
            'export', 'removal', 'haul away', 'excavation',
            'soil removal', 'dirt removal', 'material export'
        ],
        'Import': [
            'import', 'bring in', 'delivery', 'material import',
            'soil import', 'fill import', 'material delivery'
        ],
        'Sand': [
            'sand', 'sand fill', 'sandy soil', 'sand material'
        ],
        'Rock': [
            'rock', 'rock fill', 'crushed rock', 'stone',
            'aggregate', 'base rock', 'road base'
        ]
    }

class QuantityExtractionPatterns:
    """Quantity extraction patterns for various units"""
    
    PATTERNS = [
        # Cubic yards patterns
        r'(\d{1,3}(?:,\d{3})*)\s*(?:CY|cy|cubic yards?|yards?)',
        r'(\d+[Kk])\s*(?:CY|cy)',
        r'(\d+[,\d]*)\s*(?:cubic|cu)\s*(?:yards?|yds?)',
        
        # Tons patterns
        r'(\d+[,\d]*)\s*(?:tons?|T)',
        
        # Square feet patterns (for area calculations)
        r'(\d+[,\d]*)\s*(?:SF|sf|square feet|sq\.?\s*ft\.?)',
        
        # Acres patterns
        r'(\d+[,\d]*)\s*(?:acres?|AC|ac)',
        
        # Generic number patterns with units
        r'(\d+[,\d]*)\s*(?:units?|loads?|trips?)'
    ]

class ValidationRules:
    """Data validation rules for extracted permit data"""
    
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """Validate US phone number format"""
        import re
        if not phone:
            return False
        
        # Check for standard formats
        patterns = [
            r'^\(\d{3}\) \d{3}-\d{4}$',  # (XXX) XXX-XXXX
            r'^\d{3}-\d{3}-\d{4}$',     # XXX-XXX-XXXX
            r'^\d{10}$'                  # XXXXXXXXXX
        ]
        
        return any(re.match(pattern, phone) for pattern in patterns)
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address format"""
        import re
        if not email:
            return False
        
        pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_quantity(quantity: float) -> bool:
        """Validate quantity is within reasonable range"""
        if quantity is None:
            return True  # Optional field
        
        # Typical range for construction projects (1 to 1,000,000 CY)
        return 1 <= quantity <= 1_000_000
    
    @staticmethod
    def validate_permit_status(status: str) -> bool:
        """Validate permit status is recognized"""
        if not status:
            return False
        
        valid_statuses = {
            'open', 'hot', 'completed', 'inactive', 'final',
            'issued', 'in review', 'withdrawn', 'pending',
            'approved', 'rejected', 'expired'
        }
        
        return status.lower() in valid_statuses

def load_portal_config(portal_name: str) -> Optional[PortalConfig]:
    """Load configuration for a specific portal"""
    configs = {
        'san_diego_county': ScraperConfigurations.get_san_diego_county_config,
        'ontario': ScraperConfigurations.get_ontario_config,
        'orange_county': ScraperConfigurations.get_orange_county_config
    }
    
    config_func = configs.get(portal_name.lower().replace(' ', '_'))
    if config_func:
        return config_func()
    else:
        raise ValueError(f"Unknown portal: {portal_name}")

def save_scraping_results(permits: List[Dict], filename: str) -> None:
    """Save scraping results to JSON file"""
    output_data = {
        'timestamp': datetime.now().isoformat(),
        'total_permits': len(permits),
        'permits': permits
    }
    
    with open(filename, 'w') as f:
        json.dump(output_data, f, indent=2, default=str)

def load_scraping_results(filename: str) -> List[Dict]:
    """Load previously scraped results from JSON file"""
    if not os.path.exists(filename):
        return []
    
    with open(filename, 'r') as f:
        data = json.load(f)
        return data.get('permits', [])
