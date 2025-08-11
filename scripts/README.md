# Municipal Permit Scraper System

Production-ready Playwright scraping system for Southern California grading permits tracking, implementing all specifications from `.claude/agents/web-scraper.md`.

## Overview

This scraping system extracts all 15 required data fields from municipal permit portals:

### Core Permit Information
- Site Number (permit record number)
- Status (permit approval status)
- Project City (municipality location)
- Notes (additional project information)

### Contact Information
- Project Company (contractor/applicant company)
- Project Contact (primary contact person)
- Project Phone Number (standardized format)
- Project Email (validated)

### Material and Quantity Data
- Quantity (material volume/amount)
- Material Description (type of construction material)

### Pricing Calculation Fields
- Dump Fee, Trucking Price/Load, LDP Fee, Total Price Per Load
- (Populated by business logic system)

## Features

- **Intelligent Tool Selection**: Playwright as primary tool with fallback capabilities
- **Anti-Detection Measures**: Randomized user agents, delays, and human-like behavior
- **Contact Information Processing**: Phone standardization and email validation
- **Material Extraction**: NLP-based material type and quantity extraction
- **Data Validation**: Comprehensive validation rules for all extracted fields
- **Multi-Portal Support**: Configurable for different municipal systems

## Installation

1. **Install Python Dependencies**
```bash
pip install -r requirements.txt
```

2. **Install Playwright Browsers**
```bash
playwright install chromium
```

3. **Configure Environment** (optional)
```bash
# Create .env file for sensitive configurations
echo "SCRAPING_DELAY_MIN=3" > .env
echo "SCRAPING_DELAY_MAX=7" >> .env
```

## Quick Start

### Basic Usage

```python
import asyncio
from san_diego_county_scraper import SanDiegoCountyScraper

async def basic_scraping():
    scraper = SanDiegoCountyScraper()
    
    search_criteria = {
        'permit_type': 'grading',
        'date_from': '2024-01-01',
        'date_to': '2024-12-31'
    }
    
    permits = await scraper.scrape_permits(search_criteria, max_permits=10)
    
    for permit in permits:
        print(f"Permit: {permit.site_number}")
        print(f"Status: {permit.status}")
        print(f"Company: {permit.project_company}")
        print(f"Contact: {permit.project_contact} ({permit.project_phone})")
        print(f"Material: {permit.material_description} ({permit.quantity} CY)")
        print("-" * 50)

asyncio.run(basic_scraping())
```

### Advanced Usage with Orchestrator

```python
import asyncio
from example_usage import PermitScrapingOrchestrator

async def advanced_scraping():
    orchestrator = PermitScrapingOrchestrator()
    
    search_criteria = {
        'permit_type': 'grading',
        'date_from': '2024-01-01',
        'max_permits': 100
    }
    
    # Scrape all configured portals
    results = await orchestrator.scrape_all_portals(search_criteria)
    
    # Generate summary report
    summary = orchestrator.generate_summary_report(results)
    
    print(f"Total permits: {summary['total_permits']}")
    print(f"Data completeness: {summary['data_completeness']}")

asyncio.run(advanced_scraping())
```

## Configuration

### Portal Configuration

Each municipal portal is configured in `scraper_config.py`:

```python
from scraper_config import load_portal_config

# Load configuration for specific portal
config = load_portal_config('san_diego_county')
print(f"Portal: {config.name}")
print(f"Type: {config.portal_type}")
print(f"Rate limit: {config.rate_limit_delay}")
```

### Adding New Portals

1. **Create Portal Configuration**
```python
def get_new_city_config() -> PortalConfig:
    return PortalConfig(
        name="New City",
        base_url="https://newcity.gov",
        search_url="https://newcity.gov/permits",
        portal_type="accela",  # or "etrakiT" or "custom"
        selectors={
            'site_number': ['#permit_number', '.permit-id'],
            'status': ['#status', '.permit-status'],
            # ... other selectors
        },
        search_form={
            'permit_type_selector': '#permit_type',
            'search_button': '#search_btn'
        },
        rate_limit_delay=(3, 7)
    )
```

2. **Create Scraper Class**
```python
class NewCityScraper(SanDiegoCountyScraper):
    def __init__(self):
        super().__init__()
        self.config = load_portal_config('new_city')
        self.base_url = self.config.base_url
        self.search_url = self.config.search_url
```

## Data Validation

The system includes comprehensive validation for all extracted fields:

### Phone Number Validation
- Standardizes to `(XXX) XXX-XXXX` format
- Validates 10-digit US phone numbers
- Handles various input formats

### Email Validation
- Validates email format using regex
- Checks for valid domain structure
- Normalizes to lowercase

### Material Classification
- Uses NLP patterns to identify material types
- Maps municipal terminology to standard classifications
- Supports: Clean Fill, Clay, Grading, Stockpile, Export, Import

### Quantity Extraction
- Extracts quantities from project descriptions
- Supports various units: CY, cubic yards, tons
- Handles formatted numbers: 70,000 CY, 70K cy

## Output Format

Extracted data matches the database schema from `.claude/agents/database-architect.md`:

```json
{
  "site_number": "PDS2025-RESALT-005999",
  "status": "Final",
  "project_city": "San Diego County",
  "project_company": "ABC Construction LLC",
  "project_contact": "John Smith",
  "project_phone": "(619) 555-0123",
  "project_email": "john@abcconstruction.com",
  "quantity": 70000.0,
  "material_description": "Clean Fill",
  "notes": "Onsite precise grading for residential development",
  "source_portal": "San Diego County",
  "scraped_at": "2024-01-15T10:30:00",
  "raw_data": {...}
}
```

## Error Handling

The scraper includes robust error handling:

- **Network Errors**: Automatic retries with exponential backoff
- **Selector Failures**: Multiple selector fallbacks for each field
- **Data Validation**: Validation errors logged but don't stop processing
- **Rate Limiting**: Intelligent delays to respect server limits

## Monitoring and Logging

All scraping activities are logged:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
```

Log files include:
- Scraping progress and results
- Validation errors and warnings
- Performance metrics
- Error details for debugging

## Production Deployment

### Recommended Settings

```python
# Production configuration
HEADLESS_MODE = True
MAX_CONCURRENT_SCRAPERS = 3
RATE_LIMIT_DELAY = (5, 10)  # More conservative delays
RETRY_ATTEMPTS = 3
TIMEOUT_SECONDS = 30
```

### Scheduling

Use cron or task scheduler for regular scraping:

```bash
# Daily scraping at 6 AM
0 6 * * * /usr/bin/python3 /path/to/scripts/example_usage.py daily
```

### Database Integration

Connect to PostgreSQL/Supabase database:

```python
import psycopg2
from supabase import create_client

# Save permits to database
def save_to_database(permits):
    # PostgreSQL connection
    conn = psycopg2.connect(
        host="your-host",
        database="permits_db",
        user="username",
        password="password"
    )
    
    # Insert permits using schema from database-architect.md
    # ... implementation
```

## Troubleshooting

### Common Issues

1. **Selector Not Found**: Update selectors in portal configuration
2. **Rate Limiting**: Increase delay between requests
3. **Authentication Required**: Implement login flow for protected portals
4. **Data Validation Failures**: Check extraction patterns and validation rules

### Debug Mode

Enable debug mode for detailed logging:

```python
import logging
logging.getLogger().setLevel(logging.DEBUG)

# Run scraper with debug output
scraper = SanDiegoCountyScraper()
permits = await scraper.scrape_permits(criteria, max_permits=1)
```

## Contributing

When adding new features:

1. Follow specifications in `.claude/agents/web-scraper.md`
2. Ensure all 15 required fields are extracted
3. Add comprehensive validation rules
4. Include error handling and logging
5. Update configuration files
6. Add tests for new functionality

## License

This scraping system is designed for legitimate municipal permit research and compliance with terms of service of target websites.
