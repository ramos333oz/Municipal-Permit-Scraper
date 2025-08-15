'use client'

import { useEffect, useState } from 'react'
import dynamic from 'next/dynamic'
import { LoadingSpinner } from '@/components/ui/loading-spinner'

// Dynamically import the map component to avoid SSR issues
const DynamicMap = dynamic(
  () => import('./leaflet-map').then((mod) => mod.LeafletMap),
  {
    ssr: false,
    loading: () => (
      <div className="h-full flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    ),
  }
)

interface PermitMapProps {
  initialPermits?: any[]
  className?: string
}

export function PermitMap({ initialPermits = [], className }: PermitMapProps) {
  const [permits, setPermits] = useState(initialPermits)
  const [isLoading, setIsLoading] = useState(false)

  // Mock data for demonstration
  useEffect(() => {
    if (permits.length === 0) {
      setIsLoading(true)
      // Simulate API call
      setTimeout(() => {
        setPermits([
          {
            id: 1,
            permit_number: "GR-2024-0156",
            project_name: "Sunset Boulevard Grading",
            latitude: 34.0522,
            longitude: -118.2437,
            status: "active",
            project_city: "Los Angeles",
            issue_date: "2024-01-15",
            expiration_date: "2024-12-15"
          },
          {
            id: 2,
            permit_number: "GR-2024-0157",
            project_name: "Hollywood Hills Development",
            latitude: 34.1184,
            longitude: -118.3004,
            status: "pending",
            project_city: "Los Angeles",
            issue_date: "2024-01-20",
            expiration_date: "2024-12-20"
          },
          {
            id: 3,
            permit_number: "GR-2024-0158",
            project_name: "Santa Monica Residential",
            latitude: 34.0195,
            longitude: -118.4912,
            status: "expired",
            project_city: "Santa Monica",
            issue_date: "2023-06-10",
            expiration_date: "2024-01-10"
          }
        ])
        setIsLoading(false)
      }, 1000)
    }
  }, [permits.length])

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className={`h-full w-full ${className}`}>
      <DynamicMap permits={permits} />
    </div>
  )
}
