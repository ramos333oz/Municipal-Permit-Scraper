# Municipal Grading Permit Scraper - API Integration Guidelines

## Geocoding Strategy

### Primary Geocoding Service: Geocodio API
- **Purpose**: Address standardization and coordinate conversion
- **Usage**: Bulk geocoding of permit addresses from municipal portals
- **Advantages**: Cost-effective for large volumes, high accuracy for US addresses
- **Implementation**: Batch process scraped addresses to obtain latitude/longitude coordinates

### Secondary Geocoding Service: Google Maps Geocoding API
- **Purpose**: Fallback for failed Geocodio API requests
- **Usage**: Handle addresses that Geocodio cannot process
- **Implementation**: Automatic fallback when Geocodio returns low confidence or fails

### Geocoding Workflow
1. Scrape permit addresses from municipal portals
2. Standardize addresses using data processing pipeline
3. Submit to Geocodio API for coordinate conversion
4. For failed requests, retry with Google Maps Geocoding API
5. Store coordinates in PostGIS database with accuracy metadata

## Distance Calculations

### Service: Google Maps Distance Matrix API
- **Purpose**: Calculate drive times and distances between permit site coordinates
- **Usage**: Real-time distance calculations for route planning
- **Implementation**: Batch requests for multiple destinations from single origin point

### Distance Calculation Workflow
1. User selects origin permit site on map
2. System retrieves coordinates of all other active permit sites
3. Batch API request to Google Maps Distance Matrix API
4. Cache results for performance optimization
5. Display drive times and distances on map interface

### API Request Optimization
- **Batch Processing**: Send multiple destinations per API call to minimize requests
- **Caching Strategy**: Store frequently requested distance calculations
- **Rate Limiting**: Implement proper throttling to avoid API quotas
- **Error Handling**: Graceful fallback for API failures or network issues

## Integration Flow Summary

```
Municipal Portals í Web Scraping í Address Extraction
        ì
Address Standardization í Geocodio API í Coordinates
        ì
PostGIS Database Storage ê Google Maps Geocoding (fallback)
        ì
Map Interface í User Selection í Google Maps Distance Matrix API
        ì
Drive Time Calculations í Route Planning Interface
```

## Cost Management Guidelines

### Geocodio API
- Use for all initial address geocoding due to lower cost
- Monitor monthly usage and accuracy rates
- Implement batch processing to maximize efficiency

### Google Maps APIs
- Use Distance Matrix API exclusively for drive time calculations
- Use Geocoding API only as fallback to minimize costs
- Implement intelligent caching to reduce repeat requests
- Monitor API usage and set budget alerts

## Performance Requirements

### Geocoding Performance
- Batch process addresses during off-peak hours
- Target 98%+ successful geocoding rate
- Store geocoding confidence scores for quality assurance

### Distance Calculation Performance  
- Sub-2-second response times for distance calculations
- Support calculating distances to 50+ permit sites simultaneously
- Cache results for 24-hour periods to balance accuracy and performance

## Error Handling & Reliability

### Geocoding Errors
- Log failed geocoding attempts with original addresses
- Provide manual address correction interface for admin users
- Maintain audit trail of geocoding accuracy and failures

### Distance Calculation Errors
- Implement graceful degradation when APIs are unavailable
- Show estimated distances using straight-line calculations as fallback
- Retry failed requests with exponential backoff

## Security & API Key Management

### API Key Security
- Store API keys in environment variables
- Use separate keys for development and production environments
- Implement API key rotation procedures
- Monitor API usage for anomalous activity

### Rate Limiting & Quotas
- Implement client-side rate limiting to prevent quota exhaustion
- Set up monitoring alerts for approaching API limits
- Design system to gracefully handle quota exceeded scenarios