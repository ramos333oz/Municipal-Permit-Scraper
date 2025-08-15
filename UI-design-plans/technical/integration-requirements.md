---
title: Technical Integration Requirements - Municipal Permit Tracking System
description: Comprehensive technical integration documentation covering Supabase real-time features, mapping library integration, geocoding services, and Next.js optimization patterns
feature: technical-integration
last-updated: 2025-01-15
version: 1.0.0
related-files:
  - nextjs-integration.md
  - supabase-integration.md
  - mapping-integration.md
  - performance-optimization.md
dependencies:
  - Next.js framework
  - Supabase backend services
  - Mapping libraries (Leaflet/Google Maps)
  - Geocoding services (Geocodio/Google)
status: draft
---

# Technical Integration Requirements - Municipal Permit Tracking System

## Integration Architecture Overview

The Municipal Permit Tracking System integrates multiple services and technologies to deliver a comprehensive permit tracking and mapping solution. The architecture prioritizes performance, scalability, and real-time data synchronization while maintaining construction industry workflow optimization.

## Next.js Framework Integration

### App Router Architecture
```typescript
// app/layout.tsx - Root layout with providers
import { Providers } from '@/components/providers'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}
```

### Server Components for Permit Data
```typescript
// app/permits/page.tsx - Server component for initial data
import { createServerComponentClient } from '@supabase/auth-helpers-nextjs'
import { cookies } from 'next/headers'
import { PermitMap } from '@/components/permit-map'

export default async function PermitsPage() {
  const supabase = createServerComponentClient({ cookies })
  
  const { data: permits } = await supabase
    .from('permits')
    .select('*')
    .eq('status', 'Active')
    .limit(100)
  
  return (
    <div className="permits-page">
      <PermitMap initialPermits={permits} />
    </div>
  )
}
```

### API Routes for Dynamic Operations
```typescript
// app/api/permits/route.ts - API route for permit operations
import { NextRequest, NextResponse } from 'next/server'
import { createRouteHandlerClient } from '@supabase/auth-helpers-nextjs'
import { cookies } from 'next/headers'

export async function GET(request: NextRequest) {
  const supabase = createRouteHandlerClient({ cookies })
  const { searchParams } = new URL(request.url)
  
  const status = searchParams.get('status')
  const city = searchParams.get('city')
  
  let query = supabase.from('permits').select('*')
  
  if (status) query = query.eq('status', status)
  if (city) query = query.eq('project_city', city)
  
  const { data, error } = await query
  
  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
  
  return NextResponse.json(data)
}

export async function POST(request: NextRequest) {
  const supabase = createRouteHandlerClient({ cookies })
  const permitData = await request.json()
  
  const { data, error } = await supabase
    .from('permits')
    .insert(permitData)
    .select()
  
  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
  
  return NextResponse.json(data[0])
}
```

## Supabase Real-time Integration

### Real-time Subscriptions
```typescript
// hooks/useRealtimePermits.ts - Real-time permit updates
import { useEffect, useState } from 'react'
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'
import type { Database } from '@/types/database'

type Permit = Database['public']['Tables']['permits']['Row']

export function useRealtimePermits(initialPermits: Permit[]) {
  const [permits, setPermits] = useState<Permit[]>(initialPermits)
  const supabase = createClientComponentClient<Database>()
  
  useEffect(() => {
    const channel = supabase
      .channel('permits-changes')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'permits'
        },
        (payload) => {
          if (payload.eventType === 'INSERT') {
            setPermits(prev => [...prev, payload.new as Permit])
          } else if (payload.eventType === 'UPDATE') {
            setPermits(prev => 
              prev.map(permit => 
                permit.id === payload.new.id ? payload.new as Permit : permit
              )
            )
          } else if (payload.eventType === 'DELETE') {
            setPermits(prev => 
              prev.filter(permit => permit.id !== payload.old.id)
            )
          }
        }
      )
      .subscribe()
    
    return () => {
      supabase.removeChannel(channel)
    }
  }, [supabase])
  
  return permits
}
```

### Authentication Integration
```typescript
// components/providers.tsx - Auth and real-time providers
'use client'

import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'
import { SessionContextProvider } from '@supabase/auth-helpers-react'
import { useState } from 'react'

export function Providers({ children }: { children: React.ReactNode }) {
  const [supabase] = useState(() => createClientComponentClient())
  
  return (
    <SessionContextProvider supabaseClient={supabase}>
      {children}
    </SessionContextProvider>
  )
}
```

### Database Queries with PostGIS
```typescript
// services/permitService.ts - Geospatial queries
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'

export class PermitService {
  private supabase = createClientComponentClient()
  
  async getPermitsInBounds(bounds: {
    north: number
    south: number
    east: number
    west: number
  }) {
    const { data, error } = await this.supabase
      .rpc('get_permits_in_bounds', {
        north_lat: bounds.north,
        south_lat: bounds.south,
        east_lng: bounds.east,
        west_lng: bounds.west
      })
    
    if (error) throw error
    return data
  }
  
  async calculateDistance(permitId1: string, permitId2: string) {
    const { data, error } = await this.supabase
      .rpc('calculate_permit_distance', {
        permit_id_1: permitId1,
        permit_id_2: permitId2
      })
    
    if (error) throw error
    return data
  }
}
```

## Mapping Library Integration

### Leaflet Integration (Primary)
```typescript
// components/permit-map.tsx - Leaflet map component
'use client'

import { useEffect, useRef } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { useRealtimePermits } from '@/hooks/useRealtimePermits'

interface PermitMapProps {
  initialPermits: Permit[]
}

export function PermitMap({ initialPermits }: PermitMapProps) {
  const mapRef = useRef<L.Map | null>(null)
  const markersRef = useRef<L.LayerGroup>(new L.LayerGroup())
  const permits = useRealtimePermits(initialPermits)
  
  useEffect(() => {
    if (!mapRef.current) {
      // Initialize map
      mapRef.current = L.map('map').setView([32.7157, -117.1611], 10)
      
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
      }).addTo(mapRef.current)
      
      markersRef.current.addTo(mapRef.current)
    }
    
    // Update markers when permits change
    markersRef.current.clearLayers()
    
    permits.forEach(permit => {
      if (permit.coordinates) {
        const [lng, lat] = permit.coordinates.coordinates
        
        const marker = L.marker([lat, lng], {
          icon: getPermitIcon(permit.status)
        })
        
        marker.bindPopup(`
          <div class="permit-popup">
            <h3>${permit.site_number}</h3>
            <p><strong>Status:</strong> ${permit.status}</p>
            <p><strong>Address:</strong> ${permit.address}</p>
            <button onclick="viewPermitDetails('${permit.id}')">
              View Details
            </button>
          </div>
        `)
        
        markersRef.current.addLayer(marker)
      }
    })
  }, [permits])
  
  return <div id="map" className="w-full h-full" />
}

function getPermitIcon(status: string): L.Icon {
  const iconColors = {
    'Active': '#059669',
    'HOT': '#DC2626',
    'Completed': '#6B7280',
    'Under Review': '#D97706',
    'Inactive': '#9CA3AF'
  }
  
  return L.divIcon({
    className: 'permit-marker',
    html: `<div style="background-color: ${iconColors[status] || '#6B7280'}" class="marker-icon"></div>`,
    iconSize: [32, 32],
    iconAnchor: [16, 32]
  })
}
```

### Google Maps Integration (Secondary)
```typescript
// components/google-map.tsx - Google Maps alternative
'use client'

import { useEffect, useRef } from 'react'
import { Loader } from '@googlemaps/js-api-loader'

export function GooglePermitMap({ permits }: { permits: Permit[] }) {
  const mapRef = useRef<HTMLDivElement>(null)
  const googleMapRef = useRef<google.maps.Map | null>(null)
  const markersRef = useRef<google.maps.Marker[]>([])
  
  useEffect(() => {
    const loader = new Loader({
      apiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY!,
      version: 'weekly',
      libraries: ['places', 'geometry']
    })
    
    loader.load().then(() => {
      if (mapRef.current && !googleMapRef.current) {
        googleMapRef.current = new google.maps.Map(mapRef.current, {
          center: { lat: 32.7157, lng: -117.1611 },
          zoom: 10,
          styles: [
            // Custom map styling for construction industry
            {
              featureType: 'poi.business',
              stylers: [{ visibility: 'off' }]
            }
          ]
        })
      }
    })
  }, [])
  
  useEffect(() => {
    if (googleMapRef.current) {
      // Clear existing markers
      markersRef.current.forEach(marker => marker.setMap(null))
      markersRef.current = []
      
      // Add new markers
      permits.forEach(permit => {
        if (permit.coordinates) {
          const [lng, lat] = permit.coordinates.coordinates
          
          const marker = new google.maps.Marker({
            position: { lat, lng },
            map: googleMapRef.current,
            title: permit.site_number,
            icon: {
              url: getMarkerIcon(permit.status),
              scaledSize: new google.maps.Size(32, 32)
            }
          })
          
          const infoWindow = new google.maps.InfoWindow({
            content: `
              <div class="permit-info-window">
                <h3>${permit.site_number}</h3>
                <p><strong>Status:</strong> ${permit.status}</p>
                <p><strong>Address:</strong> ${permit.address}</p>
              </div>
            `
          })
          
          marker.addListener('click', () => {
            infoWindow.open(googleMapRef.current, marker)
          })
          
          markersRef.current.push(marker)
        }
      })
    }
  }, [permits])
  
  return <div ref={mapRef} className="w-full h-full" />
}
```

## Geocoding Service Integration

### Geocodio Integration (Primary)
```typescript
// services/geocodingService.ts - Multi-provider geocoding
export class GeocodingService {
  private geocodioApiKey = process.env.GEOCODIO_API_KEY!
  private googleApiKey = process.env.GOOGLE_MAPS_API_KEY!
  
  async geocodeAddress(address: string): Promise<GeocodeResult> {
    try {
      // Try Geocodio first (US-focused, cost-effective)
      const geocodioResult = await this.geocodeWithGeocodio(address)
      if (geocodioResult.accuracy >= 0.8) {
        return geocodioResult
      }
    } catch (error) {
      console.warn('Geocodio failed, trying Google:', error)
    }
    
    try {
      // Fallback to Google Geocoding
      return await this.geocodeWithGoogle(address)
    } catch (error) {
      throw new Error(`Geocoding failed for address: ${address}`)
    }
  }
  
  private async geocodeWithGeocodio(address: string): Promise<GeocodeResult> {
    const response = await fetch(
      `https://api.geocod.io/v1.7/geocode?q=${encodeURIComponent(address)}&api_key=${this.geocodioApiKey}`
    )
    
    const data = await response.json()
    
    if (data.results && data.results.length > 0) {
      const result = data.results[0]
      return {
        latitude: result.location.lat,
        longitude: result.location.lng,
        accuracy: result.accuracy,
        formatted_address: result.formatted_address,
        source: 'geocodio'
      }
    }
    
    throw new Error('No results from Geocodio')
  }
  
  private async geocodeWithGoogle(address: string): Promise<GeocodeResult> {
    const response = await fetch(
      `https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(address)}&key=${this.googleApiKey}`
    )
    
    const data = await response.json()
    
    if (data.results && data.results.length > 0) {
      const result = data.results[0]
      return {
        latitude: result.geometry.location.lat,
        longitude: result.geometry.location.lng,
        accuracy: this.getGoogleAccuracy(result.geometry.location_type),
        formatted_address: result.formatted_address,
        source: 'google'
      }
    }
    
    throw new Error('No results from Google')
  }
  
  async batchGeocode(addresses: string[]): Promise<GeocodeResult[]> {
    // Batch processing with rate limiting
    const results: GeocodeResult[] = []
    const batchSize = 10
    
    for (let i = 0; i < addresses.length; i += batchSize) {
      const batch = addresses.slice(i, i + batchSize)
      const batchPromises = batch.map(address => 
        this.geocodeAddress(address).catch(error => ({
          error: error.message,
          address
        }))
      )
      
      const batchResults = await Promise.all(batchPromises)
      results.push(...batchResults.filter(result => !result.error))
      
      // Rate limiting delay
      if (i + batchSize < addresses.length) {
        await new Promise(resolve => setTimeout(resolve, 1000))
      }
    }
    
    return results
  }
}

interface GeocodeResult {
  latitude: number
  longitude: number
  accuracy: number
  formatted_address: string
  source: 'geocodio' | 'google'
}
```

## Performance Optimization

### Code Splitting and Lazy Loading
```typescript
// Dynamic imports for heavy components
import dynamic from 'next/dynamic'

const PermitMap = dynamic(() => import('@/components/permit-map'), {
  loading: () => <div className="map-skeleton">Loading map...</div>,
  ssr: false
})

const LDPQuoteSheet = dynamic(() => import('@/components/ldp-quote-sheet'), {
  loading: () => <div className="quote-skeleton">Loading quote sheet...</div>
})
```

### Image Optimization
```typescript
// next.config.js - Image optimization configuration
/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['tile.openstreetmap.org', 'maps.googleapis.com'],
    formats: ['image/webp', 'image/avif'],
  },
  experimental: {
    optimizeCss: true,
  }
}

module.exports = nextConfig
```

### Caching Strategy
```typescript
// lib/cache.ts - Client-side caching
class PermitCache {
  private cache = new Map<string, { data: any; timestamp: number }>()
  private ttl = 5 * 60 * 1000 // 5 minutes
  
  set(key: string, data: any) {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    })
  }
  
  get(key: string) {
    const cached = this.cache.get(key)
    if (!cached) return null
    
    if (Date.now() - cached.timestamp > this.ttl) {
      this.cache.delete(key)
      return null
    }
    
    return cached.data
  }
  
  clear() {
    this.cache.clear()
  }
}

export const permitCache = new PermitCache()
```

## Error Handling and Monitoring

### Error Boundaries
```typescript
// components/error-boundary.tsx
'use client'

import { Component, ReactNode } from 'react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }
  
  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }
  
  componentDidCatch(error: Error, errorInfo: any) {
    console.error('Error caught by boundary:', error, errorInfo)
    // Send to monitoring service
  }
  
  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="error-fallback">
          <h2>Something went wrong</h2>
          <p>Please refresh the page or contact support</p>
        </div>
      )
    }
    
    return this.props.children
  }
}
```

## Related Documentation

- [Next.js Integration](nextjs-integration.md) - Framework-specific patterns
- [Supabase Integration](supabase-integration.md) - Database and real-time features
- [Mapping Integration](mapping-integration.md) - Map library implementation
- [Performance Optimization](performance-optimization.md) - Performance best practices
- [Frontend Developer Agent](../../../.claude/agents/frontend-developer.md) - Implementation patterns

## Implementation Notes

This integration architecture is optimized for:
- **Real-time Performance**: Sub-2-second data synchronization
- **Scalability**: Handle 35-40 municipal portals efficiently
- **Reliability**: Graceful fallbacks and error handling
- **Construction Industry Workflows**: Professional permit tracking and route planning
- **Maintainability**: Clean separation of concerns and modular architecture

## Last Updated

**Change Log**:
- 2025-01-15: Comprehensive technical integration requirements created
- Next: Implementation and testing phase coordination
