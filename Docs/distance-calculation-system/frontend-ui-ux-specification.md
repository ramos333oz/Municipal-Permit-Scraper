# Distance Calculation System - Frontend UI/UX Specification

## Overview

This document provides comprehensive UI/UX planning for the Distance Calculation System frontend interface, designed specifically for construction industry workflows and municipal permit tracking. The interface integrates with our completed Phase 1 (Core Infrastructure) and Phase 2 (API Integration) systems.

## System Context

### **Completed Infrastructure Integration**
- **Phase 1**: Core Infrastructure ✅ Complete
- **Phase 2**: API Integration ✅ Complete
  - `/api/distance/calculate` - Single distance calculation
  - `/api/distance/batch` - Batch processing for multiple routes
  - `/api/distance/pricing` - LDP pricing calculations
  - `/api/distance/cache` - Cache management operations
- **Phase 3**: Frontend UI Implementation 🔄 In Progress

### **Technical Foundation**
- **Framework**: Next.js 15 with App Router
- **Styling**: Tailwind CSS with shadcn/ui components
- **State Management**: React hooks with server state management
- **API Integration**: RESTful endpoints with TypeScript interfaces
- **Database**: Supabase PostgreSQL with real-time subscriptions

## User Analysis

### **Primary Users**
1. **Construction Project Managers**
   - Need quick distance calculations for route planning
   - Require LDP pricing for project budgeting
   - Use mobile devices in field operations

2. **Municipal Permit Coordinators**
   - Process multiple permit applications daily
   - Need batch distance calculations for efficiency
   - Require accurate cost estimates for permit fees

3. **Fleet Operations Managers**
   - Optimize truck routes for multiple job sites
   - Monitor fuel costs and time efficiency
   - Need real-time route adjustments

### **User Goals**
- Calculate accurate drive times between permit locations
- Generate LDP pricing using exact formula: (Roundtrip Minutes × 1.83) + Added Minutes
- Process multiple routes efficiently with batch operations
- Monitor system performance and cost optimization
- Access tools on both mobile and desktop devices

## User Flow Analysis

### **Primary User Journeys**

#### **Journey 1: Single Distance Calculation**
```
1. User lands on dashboard
2. Selects "Distance Calculator" from navigation
3. Enters origin coordinates/address
4. Enters destination coordinates/address
5. Clicks "Calculate Distance"
6. Views results: distance, duration, traffic data
7. Optionally calculates LDP pricing
8. Saves or exports results
```

#### **Journey 2: Batch Route Processing**
```
1. User navigates to "Batch Processing"
2. Uploads CSV file or enters multiple routes manually
3. Configures batch processing options
4. Initiates batch calculation
5. Monitors real-time progress
6. Reviews completed results
7. Downloads comprehensive report
```

#### **Journey 3: LDP Pricing Calculation**
```
1. User accesses "LDP Pricing" tool
2. Enters or selects existing distance calculation
3. Inputs additional parameters (dump fee, LDP fee, added minutes)
4. System calculates using formula: (Roundtrip Minutes × 1.83) + Added Minutes
5. Views pricing breakdown
6. Generates quote or invoice
```

#### **Journey 4: Performance Monitoring**
```
1. User checks "Cache Management" dashboard
2. Reviews cache hit rates and performance metrics
3. Monitors API usage and costs
4. Identifies optimization opportunities
5. Manages cache settings
```

## Component Architecture

### **Component Hierarchy**

```
App Layout (layout.tsx)
├── DashboardLayout
│   ├── Sidebar Navigation
│   ├── Top Navigation Bar
│   └── Main Content Area
│       ├── Dashboard Overview (/)
│       │   ├── MetricsCards
│       │   ├── SystemStatus
│       │   └── QuickActions
│       ├── Distance Calculator (/distance)
│       │   ├── SingleCalculationForm
│       │   ├── ResultsDisplay
│       │   └── HistoryPanel
│       ├── LDP Pricing (/pricing)
│       │   ├── PricingCalculatorForm
│       │   ├── FormulaDisplay
│       │   └── PricingBreakdown
│       ├── Batch Processing (/batch)
│       │   ├── BatchUploadForm
│       │   ├── ProgressTracker
│       │   └── ResultsTable
│       ├── Map View (/map)
│       │   ├── InteractiveMap
│       │   ├── RouteOverlay
│       │   └── LocationMarkers
│       └── Cache Management (/cache)
│           ├── CacheStatsPanel
│           ├── PerformanceCharts
│           └── CacheControls
```

### **Core Components**

#### **1. SingleCalculationForm**
```typescript
interface SingleCalculationFormProps {
  onCalculate: (origin: Coordinates, destination: Coordinates) => void
  loading: boolean
  error?: string
}
```

#### **2. BatchProcessingInterface**
```typescript
interface BatchProcessingProps {
  onBatchSubmit: (routes: RouteInput[]) => void
  progress: BatchProgress
  results: BatchResults[]
}
```

#### **3. LDPPricingCalculator**
```typescript
interface LDPPricingProps {
  distanceData?: DistanceResult
  onPricingCalculate: (params: PricingParams) => void
  formula: string // "(Roundtrip Minutes × 1.83) + Added Minutes"
}
```

#### **4. CacheManagementDashboard**
```typescript
interface CacheManagementProps {
  stats: CacheStats
  onCacheAction: (action: CacheAction) => void
  realTimeUpdates: boolean
}
```

## API Integration Strategy

### **Frontend-API Integration Patterns**

#### **1. Single Distance Calculation**
```typescript
// API Endpoint: POST /api/distance/calculate
const calculateDistance = async (origin: Coordinates, destination: Coordinates) => {
  const response = await fetch('/api/distance/calculate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ origin, destination })
  })
  return response.json()
}
```

#### **2. Batch Processing**
```typescript
// API Endpoint: POST /api/distance/batch
const processBatchRoutes = async (routes: RouteInput[]) => {
  const response = await fetch('/api/distance/batch', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ routes, options: { max_concurrent: 5 } })
  })
  return response.json()
}
```

#### **3. LDP Pricing**
```typescript
// API Endpoint: POST /api/distance/pricing
const calculateLDPPricing = async (params: PricingParams) => {
  const response = await fetch('/api/distance/pricing', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params)
  })
  return response.json()
}
```

#### **4. Cache Management**
```typescript
// API Endpoint: GET /api/distance/cache
const getCacheStats = async () => {
  const response = await fetch('/api/distance/cache')
  return response.json()
}
```

### **State Management Strategy**

#### **React Query Integration**
```typescript
// Custom hooks for API integration
export const useDistanceCalculation = () => {
  return useMutation({
    mutationFn: calculateDistance,
    onSuccess: (data) => {
      // Update cache and UI state
    },
    onError: (error) => {
      // Handle error states
    }
  })
}

export const useCacheStats = () => {
  return useQuery({
    queryKey: ['cache-stats'],
    queryFn: getCacheStats,
    refetchInterval: 30000, // Refresh every 30 seconds
  })
}
```

## Responsive Design Plan

### **Mobile-First Design (320px - 768px)**
- **Priority**: Field operations and quick calculations
- **Layout**: Single column, stacked components
- **Navigation**: Collapsible hamburger menu
- **Forms**: Large touch targets, simplified inputs
- **Maps**: Full-screen modal view
- **Key Features**:
  - Quick distance calculation
  - Simple LDP pricing
  - Basic results display

### **Tablet Design (768px - 1024px)**
- **Priority**: Balanced mobile and desktop features
- **Layout**: Two-column grid for forms and results
- **Navigation**: Persistent sidebar with icons
- **Forms**: Enhanced input validation and autocomplete
- **Maps**: Embedded map view with overlay controls

### **Desktop Design (1024px+)**
- **Priority**: Full feature set and productivity
- **Layout**: Multi-column dashboard layout
- **Navigation**: Full sidebar with labels and icons
- **Forms**: Advanced features, bulk operations
- **Maps**: Split-screen with data panels
- **Key Features**:
  - Batch processing interface
  - Advanced cache management
  - Comprehensive reporting

### **Responsive Breakpoints**
```css
/* Mobile First */
.container {
  @apply px-4 mx-auto;
}

/* Tablet */
@media (min-width: 768px) {
  .container {
    @apply px-6 max-w-4xl;
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .container {
    @apply px-8 max-w-7xl;
  }
}
```

## Construction Industry UX Patterns

### **Municipal Permit Workflow Integration**

#### **1. Permit-Centric Navigation**
- Quick access to permit-related calculations
- Integration with existing permit management systems
- Contextual tools based on permit status

#### **2. LDP Pricing Workflow**
```
Permit Application → Distance Calculation → LDP Pricing → Quote Generation
```

#### **3. Field Operations Optimization**
- Offline capability for basic calculations
- GPS integration for current location
- Quick route adjustments
- Emergency contact integration

### **Construction Industry Terminology**
- **LDP**: Load Delivery Point
- **Roundtrip Minutes**: Total travel time including return
- **Added Minutes**: Loading/unloading time (5-30 minutes)
- **Dump Fee**: Site-specific disposal cost
- **Trucking Price**: Calculated transportation cost

### **Industry-Specific Features**
- **Material Type Integration**: Different calculations for different materials
- **Seasonal Adjustments**: Traffic pattern considerations
- **Regulatory Compliance**: Municipal requirement tracking
- **Cost Optimization**: Fuel efficiency and time management

## Performance Considerations

### **Loading States and Progressive Enhancement**

#### **1. Skeleton Loading**
```typescript
const CalculationSkeleton = () => (
  <div className="animate-pulse space-y-4">
    <div className="h-4 bg-gray-200 rounded w-3/4"></div>
    <div className="h-8 bg-gray-200 rounded w-1/2"></div>
  </div>
)
```

#### **2. Progressive Data Loading**
- Initial page load: Basic UI structure
- Secondary load: Cache statistics and recent calculations
- Background load: Historical data and analytics

#### **3. Real-Time Updates**
```typescript
// WebSocket integration for live updates
const useRealTimeUpdates = () => {
  useEffect(() => {
    const ws = new WebSocket('/api/ws/cache-updates')
    ws.onmessage = (event) => {
      const update = JSON.parse(event.data)
      // Update UI state
    }
    return () => ws.close()
  }, [])
}
```

### **Error Handling Patterns**

#### **1. API Error States**
```typescript
interface ErrorState {
  type: 'network' | 'validation' | 'server' | 'rate_limit'
  message: string
  retryable: boolean
  retryAfter?: number
}
```

#### **2. User Feedback Patterns**
- **Success**: Green toast notifications with action buttons
- **Warning**: Yellow alerts with guidance
- **Error**: Red notifications with retry options
- **Info**: Blue messages for system status

#### **3. Graceful Degradation**
- Offline mode for basic calculations
- Cached results when API is unavailable
- Progressive enhancement for advanced features

### **Performance Optimization**

#### **1. Code Splitting**
```typescript
// Lazy load heavy components
const MapView = lazy(() => import('@/components/map/MapView'))
const BatchProcessor = lazy(() => import('@/components/batch/BatchProcessor'))
```

#### **2. Caching Strategy**
- Browser cache for static assets
- Service worker for offline functionality
- React Query for API response caching
- Local storage for user preferences

#### **3. Bundle Optimization**
- Tree shaking for unused code
- Dynamic imports for route-specific code
- Image optimization with Next.js Image component
- CSS purging for production builds

## Next Steps

### **Implementation Priority**
1. **Phase 3.1**: Core dashboard layout and navigation
2. **Phase 3.2**: Single distance calculation interface
3. **Phase 3.3**: LDP pricing calculator
4. **Phase 3.4**: Batch processing interface
5. **Phase 3.5**: Map visualization
6. **Phase 3.6**: Cache management dashboard

### **Success Criteria**
- ✅ Seamless integration with existing API endpoints
- ✅ Mobile-responsive design for field operations
- ✅ Real-time updates and progress tracking
- ✅ Construction industry workflow compliance
- ✅ Performance optimization for large datasets
- ✅ Comprehensive error handling and user feedback

## Wireframe Specifications

### **Dashboard Overview Layout**
```
┌─────────────────────────────────────────────────────────────┐
│ [☰] Municipal Permits Dashboard              [🔔] [👤]     │
├─────────────────────────────────────────────────────────────┤
│ [📊] [🗺️] [💰] [📦] [🗄️]                                    │
│                                                             │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │
│ │Cache Entries│ │Cache Hit    │ │API Calls    │ │Cost     │ │
│ │    1,247    │ │Rate 85.2%   │ │Today 156    │ │Today    │ │
│ │    +12%     │ │    +5.2%    │ │    +8.1%    │ │ $2.34   │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ System Status                              🟢 Online   │ │
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │ │
│ │ │Avg Response │ │Google Maps  │ │Database Connection  │ │ │
│ │ │   150ms     │ │Operational  │ │    Connected        │ │ │
│ │ └─────────────┘ └─────────────┘ └─────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### **Single Distance Calculation Interface**
```
┌─────────────────────────────────────────────────────────────┐
│ Distance Calculator                                         │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Origin Location                                         │ │
│ │ [📍] [Enter address or coordinates...        ] [📍GPS] │ │
│ │                                                         │ │
│ │ Destination Location                                    │ │
│ │ [📍] [Enter address or coordinates...        ] [📍GPS] │ │
│ │                                                         │ │
│ │ Options                                                 │ │
│ │ ☑️ Include traffic data  ☑️ Cache result               │ │
│ │                                                         │ │
│ │                    [Calculate Distance]                 │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Results                                                 │ │
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │ │
│ │ │Distance     │ │Duration     │ │Duration in Traffic  │ │ │
│ │ │21.4 km      │ │24.6 min     │ │25.4 min            │ │ │
│ │ └─────────────┘ └─────────────┘ └─────────────────────┘ │ │
│ │                                                         │ │
│ │ [Calculate LDP Pricing] [Save Result] [Export]          │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### **LDP Pricing Calculator Interface**
```
┌─────────────────────────────────────────────────────────────┐
│ LDP Pricing Calculator                                      │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Formula: (Roundtrip Minutes × 1.83) + Added Minutes    │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Distance Data (from calculation)                        │ │
│ │ Roundtrip Minutes: [50] (calculated: 25.4 min × 2)     │ │
│ │ Added Minutes: [10] (loading/unloading time)            │ │
│ │                                                         │ │
│ │ Additional Costs                                        │ │
│ │ Dump Fee: [$25.00]                                      │ │
│ │ LDP Fee: [$15.00]                                       │ │
│ │                                                         │ │
│ │                    [Calculate Pricing]                  │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Pricing Breakdown                                       │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ Trucking Price: (50 × 1.83) + 10 = $101.50         │ │ │
│ │ │ Dump Fee: $25.00                                    │ │ │
│ │ │ LDP Fee: $15.00                                     │ │ │
│ │ │ ─────────────────────────────────────────────────── │ │ │
│ │ │ Total Price Per Load: $141.50                       │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ │                                                         │ │
│ │ [Generate Quote] [Update Permit] [Export PDF]           │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### **Batch Processing Interface**
```
┌─────────────────────────────────────────────────────────────┐
│ Batch Route Processing                                      │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Upload Routes                                           │ │
│ │ [📁 Choose CSV File] or [➕ Add Routes Manually]        │ │
│ │                                                         │ │
│ │ Processing Options                                      │ │
│ │ Max Concurrent: [5] ☑️ Include Traffic ☑️ Cache Results│ │
│ │                                                         │ │
│ │                    [Start Batch Processing]             │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Progress Tracker                                        │ │
│ │ ████████████████████████████████████████████████ 85%   │ │
│ │ Processing route 17 of 20...                           │ │
│ │                                                         │ │
│ │ ✅ Completed: 15  ⏳ Processing: 2  ❌ Failed: 0       │ │
│ │ Estimated time remaining: 45 seconds                   │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Results Summary                                         │ │
│ │ Total Routes: 20 | Successful: 18 | Failed: 2          │ │
│ │ Total Distance: 456.7 km | Avg Duration: 32.4 min      │ │
│ │ Estimated Cost: $12.50 | Cache Hits: 12 (60%)          │ │
│ │                                                         │ │
│ │ [Download Results] [View Details] [Process Failed]      │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow Architecture

### **Component Data Flow**
```
API Endpoints ←→ React Query ←→ UI Components
     ↓                ↓              ↓
Cache Layer    State Management   User Interface
     ↓                ↓              ↓
Database      Local Storage     User Actions
```

### **State Management Patterns**

#### **1. Server State (React Query)**
```typescript
// Distance calculation state
const distanceQuery = useQuery({
  queryKey: ['distance', origin, destination],
  queryFn: () => calculateDistance(origin, destination),
  staleTime: 5 * 60 * 1000, // 5 minutes
  cacheTime: 30 * 60 * 1000, // 30 minutes
})

// Cache statistics state
const cacheStatsQuery = useQuery({
  queryKey: ['cache-stats'],
  queryFn: getCacheStats,
  refetchInterval: 30000, // Real-time updates
})
```

#### **2. Client State (React Hooks)**
```typescript
// Form state management
const [formData, setFormData] = useState<CalculationForm>({
  origin: { lat: 0, lng: 0 },
  destination: { lat: 0, lng: 0 },
  options: { includeTraffic: true, cacheResult: true }
})

// UI state management
const [isLoading, setIsLoading] = useState(false)
const [error, setError] = useState<string | null>(null)
const [results, setResults] = useState<DistanceResult | null>(null)
```

### **Real-Time Updates Strategy**

#### **1. WebSocket Integration**
```typescript
// Real-time cache updates
const useCacheUpdates = () => {
  const queryClient = useQueryClient()

  useEffect(() => {
    const ws = new WebSocket('/api/ws/cache-updates')

    ws.onmessage = (event) => {
      const update = JSON.parse(event.data)
      queryClient.setQueryData(['cache-stats'], update)
    }

    return () => ws.close()
  }, [queryClient])
}
```

#### **2. Polling Strategy**
```typescript
// Batch processing progress polling
const useBatchProgress = (batchId: string) => {
  return useQuery({
    queryKey: ['batch-progress', batchId],
    queryFn: () => getBatchProgress(batchId),
    refetchInterval: 1000, // Poll every second
    enabled: !!batchId,
  })
}
```

## Accessibility and Usability

### **WCAG 2.1 AA Compliance**

#### **1. Keyboard Navigation**
```typescript
// Keyboard shortcuts for power users
const useKeyboardShortcuts = () => {
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if (event.ctrlKey || event.metaKey) {
        switch (event.key) {
          case 'k': // Ctrl+K for quick calculation
            event.preventDefault()
            openCalculationModal()
            break
          case 'b': // Ctrl+B for batch processing
            event.preventDefault()
            navigateToBatch()
            break
        }
      }
    }

    document.addEventListener('keydown', handleKeyPress)
    return () => document.removeEventListener('keydown', handleKeyPress)
  }, [])
}
```

#### **2. Screen Reader Support**
```typescript
// ARIA labels and descriptions
<button
  aria-label="Calculate distance between origin and destination"
  aria-describedby="calculation-help"
  onClick={handleCalculate}
>
  Calculate Distance
</button>
<div id="calculation-help" className="sr-only">
  This will calculate the driving distance and time between the two locations
</div>
```

#### **3. Color and Contrast**
```css
/* High contrast mode support */
@media (prefers-contrast: high) {
  .btn-primary {
    @apply bg-black text-white border-2 border-white;
  }

  .card {
    @apply border-2 border-gray-900;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .animate-pulse {
    animation: none;
  }

  .transition-all {
    transition: none;
  }
}
```

### **Construction Industry Usability**

#### **1. Field-Optimized Interface**
- Large touch targets (minimum 44px)
- High contrast colors for outdoor visibility
- Simplified navigation for gloved hands
- Offline capability for remote locations

#### **2. Error Prevention**
```typescript
// Input validation for coordinates
const validateCoordinates = (lat: number, lng: number) => {
  const errors: string[] = []

  if (lat < -90 || lat > 90) {
    errors.push('Latitude must be between -90 and 90 degrees')
  }

  if (lng < -180 || lng > 180) {
    errors.push('Longitude must be between -180 and 180 degrees')
  }

  return errors
}
```

#### **3. Progressive Disclosure**
```typescript
// Advanced options hidden by default
const [showAdvancedOptions, setShowAdvancedOptions] = useState(false)

return (
  <div>
    {/* Basic form fields */}
    <button onClick={() => setShowAdvancedOptions(!showAdvancedOptions)}>
      {showAdvancedOptions ? 'Hide' : 'Show'} Advanced Options
    </button>

    {showAdvancedOptions && (
      <div className="mt-4 p-4 border rounded">
        {/* Advanced configuration options */}
      </div>
    )}
  </div>
)
```

## Testing Strategy

### **Component Testing**
```typescript
// Distance calculation form tests
describe('DistanceCalculationForm', () => {
  it('should validate coordinate inputs', () => {
    render(<DistanceCalculationForm />)

    const latInput = screen.getByLabelText('Origin Latitude')
    fireEvent.change(latInput, { target: { value: '91' } })

    expect(screen.getByText('Latitude must be between -90 and 90 degrees'))
      .toBeInTheDocument()
  })

  it('should call API on form submission', async () => {
    const mockCalculate = jest.fn()
    render(<DistanceCalculationForm onCalculate={mockCalculate} />)

    // Fill form and submit
    fireEvent.click(screen.getByText('Calculate Distance'))

    expect(mockCalculate).toHaveBeenCalledWith(
      { lat: 32.7157, lng: -117.1611 },
      { lat: 32.8328, lng: -117.2713 }
    )
  })
})
```

### **Integration Testing**
```typescript
// API integration tests
describe('Distance API Integration', () => {
  it('should handle successful distance calculation', async () => {
    const mockResponse = {
      success: true,
      data: {
        distance_meters: 21376,
        duration_seconds: 1476,
        cached: false
      }
    }

    fetchMock.mockResponseOnce(JSON.stringify(mockResponse))

    const result = await calculateDistance(
      { lat: 32.7157, lng: -117.1611 },
      { lat: 32.8328, lng: -117.2713 }
    )

    expect(result.data.distance_meters).toBe(21376)
  })
})
```

### **E2E Testing**
```typescript
// Playwright end-to-end tests
test('complete distance calculation workflow', async ({ page }) => {
  await page.goto('/dashboard/distance')

  // Fill origin
  await page.fill('[data-testid="origin-lat"]', '32.7157')
  await page.fill('[data-testid="origin-lng"]', '-117.1611')

  // Fill destination
  await page.fill('[data-testid="destination-lat"]', '32.8328')
  await page.fill('[data-testid="destination-lng"]', '-117.2713')

  // Submit calculation
  await page.click('[data-testid="calculate-button"]')

  // Verify results
  await expect(page.locator('[data-testid="distance-result"]'))
    .toContainText('21.4 km')
})
```

## Implementation Guidelines

### **Development Phases**

#### **Phase 3.1: Core Infrastructure (Priority 1)**
- ✅ Create main dashboard layout with responsive navigation
- ✅ Implement basic routing structure with Next.js 15 App Router
- ✅ Set up Tailwind CSS with shadcn/ui component library
- ✅ Configure TypeScript interfaces for API integration
- ✅ Establish error boundary and loading state patterns

#### **Phase 3.2: Distance Calculation UI (Priority 1)**
- ✅ Build single distance calculation form component
- ✅ Integrate with `/api/distance/calculate` endpoint
- ✅ Implement real-time validation and error handling
- ✅ Add GPS location detection for mobile users
- ✅ Create results display with export functionality

#### **Phase 3.3: LDP Pricing Calculator (Priority 1)**
- ✅ Implement LDP pricing form with exact formula display
- ✅ Integrate with `/api/distance/pricing` endpoint
- ✅ Create pricing breakdown visualization
- ✅ Add quote generation and PDF export features
- ✅ Implement permit update functionality

#### **Phase 3.4: Batch Processing Interface (Priority 2)**
- ✅ Build CSV upload and manual entry interface
- ✅ Integrate with `/api/distance/batch` endpoint
- ✅ Implement real-time progress tracking
- ✅ Create comprehensive results table with filtering
- ✅ Add bulk export and reporting features

#### **Phase 3.5: Cache Management Dashboard (Priority 2)**
- ✅ Build cache statistics visualization
- ✅ Integrate with `/api/distance/cache` endpoint
- ✅ Implement real-time performance monitoring
- ✅ Add cache optimization recommendations
- ✅ Create cost analysis and trending charts

#### **Phase 3.6: Map Visualization (Priority 3)**
- ✅ Integrate Google Maps or Leaflet for route visualization
- ✅ Add permit location markers and clustering
- ✅ Implement route overlay and optimization display
- ✅ Create interactive map controls and filters
- ✅ Add mobile-optimized map interface

### **Technical Implementation Standards**

#### **1. Component Structure**
```typescript
// Standard component template
interface ComponentProps {
  // Props interface
}

export default function Component({ ...props }: ComponentProps) {
  // Hooks (React Query, state, effects)
  // Event handlers
  // Render logic with proper error boundaries

  return (
    <div className="component-container">
      {/* JSX with proper accessibility attributes */}
    </div>
  )
}
```

#### **2. API Integration Pattern**
```typescript
// Custom hook for API integration
export const useDistanceCalculation = () => {
  return useMutation({
    mutationFn: async (params: CalculationParams) => {
      const response = await fetch('/api/distance/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
      })

      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`)
      }

      return response.json()
    },
    onSuccess: (data) => {
      // Handle success state
    },
    onError: (error) => {
      // Handle error state
    }
  })
}
```

#### **3. Error Handling Standard**
```typescript
// Error boundary component
export class DistanceCalculationErrorBoundary extends Component {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-fallback">
          <h2>Distance Calculation Error</h2>
          <p>Please try refreshing the page or contact support.</p>
          <button onClick={() => window.location.reload()}>
            Refresh Page
          </button>
        </div>
      )
    }

    return this.props.children
  }
}
```

### **Quality Assurance Checklist**

#### **Functional Requirements**
- [ ] All API endpoints integrate correctly with UI components
- [ ] LDP pricing formula calculates accurately: (Roundtrip Minutes × 1.83) + Added Minutes
- [ ] Batch processing handles large datasets (100+ routes)
- [ ] Real-time updates work for cache statistics
- [ ] Error states provide clear user guidance
- [ ] Loading states prevent user confusion
- [ ] Form validation prevents invalid submissions
- [ ] Export functionality works for all data types

#### **Performance Requirements**
- [ ] Initial page load < 3 seconds on 3G connection
- [ ] API response handling < 500ms for cached results
- [ ] Batch processing progress updates every second
- [ ] Map rendering < 2 seconds for 100+ markers
- [ ] Mobile interface responsive on all screen sizes
- [ ] Desktop interface supports concurrent operations
- [ ] Memory usage optimized for long-running sessions
- [ ] Bundle size optimized with code splitting

#### **Accessibility Requirements**
- [ ] WCAG 2.1 AA compliance verified
- [ ] Keyboard navigation works for all features
- [ ] Screen reader compatibility tested
- [ ] High contrast mode supported
- [ ] Reduced motion preferences respected
- [ ] Focus management implemented correctly
- [ ] ARIA labels and descriptions provided
- [ ] Color-blind friendly design verified

#### **Construction Industry Requirements**
- [ ] Field operations optimized for mobile devices
- [ ] GPS integration works for location detection
- [ ] Offline capability for basic calculations
- [ ] Municipal permit workflow integration
- [ ] Construction terminology used consistently
- [ ] Regulatory compliance features implemented
- [ ] Cost optimization tools functional
- [ ] Industry-standard reporting formats supported

### **Deployment and Monitoring**

#### **Production Deployment Checklist**
- [ ] Environment variables configured correctly
- [ ] API endpoints tested in production environment
- [ ] Database connections verified
- [ ] CDN configuration optimized
- [ ] SSL certificates installed and verified
- [ ] Performance monitoring tools configured
- [ ] Error tracking and logging implemented
- [ ] Backup and recovery procedures tested

#### **Monitoring and Analytics**
```typescript
// Performance monitoring
const usePerformanceMonitoring = () => {
  useEffect(() => {
    // Track Core Web Vitals
    getCLS(console.log)
    getFID(console.log)
    getFCP(console.log)
    getLCP(console.log)
    getTTFB(console.log)
  }, [])
}

// User analytics
const trackUserAction = (action: string, properties?: object) => {
  analytics.track(action, {
    timestamp: new Date().toISOString(),
    page: window.location.pathname,
    ...properties
  })
}
```

### **Documentation and Training**

#### **User Documentation Required**
1. **Quick Start Guide**: Basic distance calculation workflow
2. **LDP Pricing Guide**: Formula explanation and usage examples
3. **Batch Processing Manual**: CSV format and bulk operations
4. **Mobile Field Guide**: GPS usage and offline capabilities
5. **Troubleshooting Guide**: Common issues and solutions

#### **Developer Documentation Required**
1. **API Integration Guide**: Endpoint usage and examples
2. **Component Library**: Reusable component documentation
3. **State Management Guide**: React Query patterns and caching
4. **Testing Guide**: Unit, integration, and E2E test examples
5. **Deployment Guide**: Production setup and configuration

### **Success Metrics and KPIs**

#### **User Experience Metrics**
- **Task Completion Rate**: >95% for single distance calculations
- **User Satisfaction Score**: >4.5/5.0 for construction industry users
- **Mobile Usability Score**: >90% for field operations
- **Error Rate**: <2% for all user interactions
- **Support Ticket Volume**: <5% of total user base per month

#### **Performance Metrics**
- **Page Load Time**: <3 seconds for initial dashboard load
- **API Response Time**: <500ms for cached distance calculations
- **Cache Hit Rate**: >80% for repeated route calculations
- **System Uptime**: >99.9% availability
- **Cost Efficiency**: <$50/month for Google Maps API usage

#### **Business Impact Metrics**
- **Permit Processing Time**: 50% reduction in calculation time
- **Cost Accuracy**: 95% accuracy in LDP pricing estimates
- **User Adoption Rate**: >80% of municipal permit coordinators
- **ROI**: Positive return within 6 months of deployment
- **Scalability**: Support for 35-40 municipal portals

This comprehensive specification serves as the complete blueprint for frontend development, ensuring seamless integration with our completed Phase 1 and Phase 2 infrastructure while meeting all construction industry requirements and technical standards.
