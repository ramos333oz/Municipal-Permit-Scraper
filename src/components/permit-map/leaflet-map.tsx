'use client'

import { useEffect, useRef } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Fix for default markers in Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

interface Permit {
  id: number
  permit_number: string
  project_name: string
  latitude: number
  longitude: number
  status: string
  project_city: string
  issue_date: string
  expiration_date: string
}

interface LeafletMapProps {
  permits: Permit[]
}

const statusColors = {
  active: '#10B981',
  pending: '#F59E0B',
  expired: '#EF4444',
  cancelled: '#6B7280'
}

export function LeafletMap({ permits }: LeafletMapProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<L.Map | null>(null)

  useEffect(() => {
    if (!mapRef.current || mapInstanceRef.current) return

    // Initialize map
    const map = L.map(mapRef.current).setView([34.0522, -118.2437], 10)

    // Add tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(map)

    mapInstanceRef.current = map

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove()
        mapInstanceRef.current = null
      }
    }
  }, [])

  useEffect(() => {
    if (!mapInstanceRef.current || !permits.length) return

    const map = mapInstanceRef.current

    // Clear existing markers
    map.eachLayer((layer) => {
      if (layer instanceof L.Marker) {
        map.removeLayer(layer)
      }
    })

    // Add permit markers
    permits.forEach((permit) => {
      if (permit.latitude && permit.longitude) {
        const color = statusColors[permit.status as keyof typeof statusColors] || '#6B7280'
        
        // Create custom icon
        const customIcon = L.divIcon({
          className: 'custom-marker',
          html: `
            <div style="
              background-color: ${color};
              width: 20px;
              height: 20px;
              border-radius: 50%;
              border: 3px solid white;
              box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            "></div>
          `,
          iconSize: [20, 20],
          iconAnchor: [10, 10]
        })

        const marker = L.marker([permit.latitude, permit.longitude], {
          icon: customIcon
        }).addTo(map)

        // Add popup
        const popupContent = `
          <div class="p-3 min-w-[250px]">
            <h3 class="font-semibold text-lg mb-2">${permit.permit_number}</h3>
            <div class="space-y-1 text-sm">
              <p><strong>Project:</strong> ${permit.project_name}</p>
              <p><strong>City:</strong> ${permit.project_city}</p>
              <p><strong>Status:</strong> 
                <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium" 
                      style="background-color: ${color}20; color: ${color};">
                  ${permit.status.charAt(0).toUpperCase() + permit.status.slice(1)}
                </span>
              </p>
              <p><strong>Issue Date:</strong> ${new Date(permit.issue_date).toLocaleDateString()}</p>
              <p><strong>Expires:</strong> ${new Date(permit.expiration_date).toLocaleDateString()}</p>
            </div>
            <div class="mt-3 pt-2 border-t">
              <button class="text-blue-600 hover:text-blue-800 text-sm font-medium">
                View Details →
              </button>
            </div>
          </div>
        `

        marker.bindPopup(popupContent, {
          maxWidth: 300,
          className: 'custom-popup'
        })
      }
    })

    // Fit map to show all markers
    if (permits.length > 0) {
      const group = new L.FeatureGroup(
        permits
          .filter(p => p.latitude && p.longitude)
          .map(p => L.marker([p.latitude, p.longitude]))
      )
      map.fitBounds(group.getBounds().pad(0.1))
    }
  }, [permits])

  return (
    <div 
      ref={mapRef} 
      className="h-full w-full rounded-lg"
      style={{ minHeight: '400px' }}
    />
  )
}
