# Municipal Grading Permit Scraper & Mapping System
## Project Planning & Development Roadmap

### Project Objective
Build a custom solution that scrapes grading permits from approximately 35–40 Southern California city websites (San Diego County, Orange County, and the Inland Empire), and visualizes them on a dynamic map-based interface with drive-time and distance calculations between sites.

### Target Scope
- **Geographic Coverage**: San Diego County (18+ portals), Orange County, Inland Empire
- **Target Cities**: San Diego, Ontario, Riverside, Rancho Cucamonga, and others
- **Portal Types**: Accela, eTRAKiT, and other municipal systems
- **Data Types**: Grading permits, grants, stockpile permits, and related municipal permits
- **Historical Data**: January 1, 2023 to present

### Technical Requirements
- **Web Scraping**: Primary tools (Playwright, FireCrawl, AgentQL) with fallback options (BeautifulSoup, Selenium, Scrapy)
- **Frontend**: Next.js as primary framework, with React/Vue as alternatives if needed
- **Database**: PostgreSQL with Supabase integration as primary solution, Firebase as fallback option
- **Backend**: Flask, Node.js, Django, or similar frameworks
- **Mapping**: Leaflet, Google Maps API, Mapbox for geospatial visualization
- **APIs**: Google Maps API for drive-time/distance calculations

### Technology Stack Hierarchy

#### Primary Technologies (First Choice)
- **Web Scraping**: Playwright, FireCrawl, AgentQL for modern, sophisticated scraping capabilities
- **Frontend Framework**: Next.js for optimal performance, SEO, and developer experience
- **Database**: PostgreSQL with Supabase integration for advanced geospatial capabilities and real-time features
- **Mapping**: Leaflet, Google Maps API, Mapbox integrated with Next.js ecosystem

#### Fallback Technologies (Contingency Options)
- **Web Scraping**: BeautifulSoup, Selenium, Scrapy when primary tools encounter limitations
- **Frontend Framework**: React + Vite or Vue.js if Next.js limitations are encountered
- **Database**: Firebase if PostgreSQL/Supabase integration faces specific constraints
- **Backend**: Flask, Node.js, Django as flexible framework options

### Core Features Required
1. **Web Scraping System**
   - Utilize primary scraping tools (Playwright, FireCrawl, AgentQL) for optimal performance
   - Maintain fallback capabilities (BeautifulSoup, Selenium, Scrapy) for reliability
   - Scrape permit data from city portals (Accela, eTRAKiT, and custom systems)
   - Handle various municipal website structures and formats
   - Implement proper rate limiting and error handling
   - Extract permits, grants, grading permits, stockpile data

2. **Data Processing & Storage**
   - Leverage PostgreSQL with Supabase integration for primary data storage
   - Utilize PostGIS for advanced geospatial data handling
   - Maintain Firebase as fallback database option if needed
   - Normalize scraped data across different city formats
   - Handle address standardization and geocoding
   - Maintain data quality and validation

3. **Interactive Map Visualization**
   - Build with Next.js as primary frontend framework for optimal performance
   - Create visual map of all active jobs using Leaflet, Google Maps API, or Mapbox
   - Display permit locations with relevant details
   - Implement filtering, sorting, and viewing options
   - Support permit type, location, and timeline-based filtering
   - Leverage Next.js features (SSR, SSG, API routes) for enhanced user experience

4. **Drive-Time & Distance Calculations**
   - Calculate drive-time between points on the map
   - Integrate with Google Maps API or similar service
   - Provide distance calculations for route planning
   - Support multiple destination calculations

5. **Manual Data Management**
   - Allow manual entry of new job sites discovered in person
   - Enable marking jobs as "inactive" when no longer valid
   - Provide admin access for data editing and management
   - Support manual data corrections and updates

6. **Ongoing Maintenance & Updates**
   - Weekly updates to scrape new permits (2–4 hrs/week)
   - System for handling bug fixes and UI improvements
   - Automated data refresh and synchronization
   - Historical data import from January 1, 2023

### Development Approach

#### Initial Development Focus
- Research and analyze target city websites and portal systems
- Implement web scraping for major cities (San Diego, Ontario, Riverside, Rancho Cucamonga)
- Build data extraction and normalization pipeline
- Create database structure for permit storage

#### Core System Development
- Develop map-based visualization interface
- Implement drive-time and distance calculation features
- Build filtering, sorting, and search capabilities
- Create admin interface for manual data entry and management

#### Data Integration & Historical Import
- Import historical permit data from January 1, 2023 to present
- Implement data validation and quality assurance
- Set up automated weekly scraping processes
- Test system reliability and data accuracy

#### Production Deployment & Maintenance
- Deploy system for live use
- Establish ongoing maintenance procedures
- Implement monitoring and error handling
- Provide admin access and training for manual operations

### Required Skills & Technologies
- **Web Scraping**: Advanced tools (Playwright, FireCrawl, AgentQL) with traditional Python fallbacks (BeautifulSoup, Selenium, Scrapy)
- **Municipal Systems**: Familiarity with Accela and eTRAKiT systems
- **Frontend Development**: Next.js expertise as primary framework, with React/Vue knowledge as alternatives
- **Database Management**: PostgreSQL with Supabase integration, PostGIS for geospatial data, Firebase as fallback
- **Backend Development**: Flask, Node.js, Django, or similar frameworks
- **Mapping & Geospatial**: Leaflet, Google Maps API, Mapbox integration with Next.js
- **UI/UX Design**: Responsive dashboards and user interface design optimized for Next.js
- **Code Quality**: Clean code, good communication, and reliability

### Success Criteria
- Successful scraping from approximately 35-40 Southern California city websites
- Accurate data normalization and storage across different municipal formats
- Functional map visualization with drive-time calculations
- Reliable weekly update system for new permits
- Admin capabilities for manual data entry and job status management
- Historical data integration from January 1, 2023 to present

### Ongoing Support Requirements
Once the system is live:
- **Weekly Maintenance**: 2–4 hours per week for scraping new permits
- **Bug Fixes**: Occasional fixes and UI improvements as needed
- **Admin Access**: Full administrative capabilities for manual data management
- **System Reliability**: Consistent performance and data accuracy