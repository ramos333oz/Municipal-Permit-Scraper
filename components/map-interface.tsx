"use client"

import { useState, useMemo } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { PermitCard } from "./permit-card"
import { StatusBadge } from "./ui/status-badge"
import { PermitData } from "@/app/types"
import { PermitStatus } from "@/app/enums"
import { MapPin, Filter, Search, ZoomIn, ZoomOut, Navigation, GitPullRequest } from "lucide-react"

interface MapInterfaceProps {
  permits: PermitData[]
}

export function MapInterface({ permits }: MapInterfaceProps) {
  const [selectedPermit, setSelectedPermit] = useState<PermitData | null>(null)
  const [statusFilter, setStatusFilter] = useState<PermitStatus[]>([])
  const [cityFilter, setCityFilter] = useState<string>("")
  const [searchQuery, setSearchQuery] = useState<string>("")
  const [mapView, setMapView] = useState<"map" | "list">("map")

  // Filter permits based on current filters
  const filteredPermits = useMemo(() => {
    return permits.filter(permit => {
      const matchesStatus = statusFilter.length === 0 || statusFilter.includes(permit.status)
      const matchesCity = !cityFilter || permit.projectCity.toLowerCase().includes(cityFilter.toLowerCase())
      const matchesSearch = !searchQuery || 
        permit.siteNumber.toLowerCase().includes(searchQuery.toLowerCase()) ||
        permit.projectCompany.toLowerCase().includes(searchQuery.toLowerCase()) ||
        permit.projectContact.toLowerCase().includes(searchQuery.toLowerCase())
      
      return matchesStatus && matchesCity && matchesSearch
    })
  }, [permits, statusFilter, cityFilter, searchQuery])

  // Get unique cities for filter dropdown
  const cities = useMemo(() => {
    return Array.from(new Set(permits.map(p => p.projectCity))).sort()
  }, [permits])

  // Status counts for badges
  const statusCounts = useMemo(() => {
    return permits.reduce((acc, permit) => {
      acc[permit.status] = (acc[permit.status] || 0) + 1
      return acc
    }, {} as Record<PermitStatus, number>)
  }, [permits])

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="border-b bg-card p-4">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold">Municipal Permit Tracking</h1>
          <div className="flex gap-2">
            <Button
              variant={mapView === "map" ? "default" : "outline"}
              size="sm"
              onClick={() => setMapView("map")}
              className="touch-target"
            >
              <MapPin className="h-4 w-4 mr-2" />
              Map View
            </Button>
            <Button
              variant={mapView === "list" ? "default" : "outline"}
              size="sm"
              onClick={() => setMapView("list")}
              className="touch-target"
            >
              List View
            </Button>
          </div>
        </div>

        {/* Status Overview */}
        <div className="flex gap-3 mb-4 overflow-x-auto">
          <Badge variant="secondary" className="whitespace-nowrap">
            Total: {permits.length}
          </Badge>
          <Badge className="permit-status-active whitespace-nowrap">
            Active: {statusCounts[PermitStatus.ACTIVE] || 0}
          </Badge>
          <Badge className="permit-status-hot whitespace-nowrap">
            HOT: {statusCounts[PermitStatus.HOT] || 0}
          </Badge>
          <Badge className="permit-status-review whitespace-nowrap">
            Under Review: {statusCounts[PermitStatus.UNDER_REVIEW] || 0}
          </Badge>
          <Badge className="permit-status-completed whitespace-nowrap">
            Completed: {statusCounts[PermitStatus.COMPLETED] || 0}
          </Badge>
        </div>

        {/* Filters */}
        <div className="flex gap-3 flex-wrap">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search permits..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          
          <Select value={cityFilter} onValueChange={setCityFilter}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Filter by city" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Cities</SelectItem>
              {cities.map(city => (
                <SelectItem key={city} value={city}>{city}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Button variant="outline" size="sm" className="touch-target">
            <Filter className="h-4 w-4 mr-2" />
            More Filters
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex">
        {/* Map/List View */}
        <div className="flex-1">
          {mapView === "map" ? (
            <div className="relative h-full bg-muted">
              {/* Map Controls */}
              <div className="absolute top-4 left-4 z-10 space-y-2">
                <Button size="sm" variant="secondary" className="touch-target-large">
                  <ZoomIn className="h-4 w-4" />
                </Button>
                <Button size="sm" variant="secondary" className="touch-target-large">
                  <ZoomOut className="h-4 w-4" />
                </Button>
                <Button size="sm" variant="secondary" className="touch-target-large">
                  <Navigation className="h-4 w-4" />
                </Button>
                <Button size="sm" variant="secondary" className="touch-target-large">
                  <GitPullRequest className="h-4 w-4" />
                </Button>
              </div>

              {/* Map Placeholder */}
              <div className="h-full flex items-center justify-center bg-gradient-to-br from-blue-50 to-green-50">
                <div className="text-center space-y-4">
                  <MapPin className="h-16 w-16 text-primary mx-auto" />
                  <div>
                    <h3 className="text-lg font-semibold">Interactive Map</h3>
                    <p className="text-muted-foreground">
                      Showing {filteredPermits.length} permits across Southern California
                    </p>
                  </div>
                  
                  {/* Mock permit markers */}
                  <div className="flex gap-2 justify-center mt-6">
                    {filteredPermits.slice(0, 5).map(permit => (
                      <Button
                        key={permit.id}
                        size="sm"
                        variant="outline"
                        className="relative"
                        onClick={() => setSelectedPermit(permit)}
                      >
                        <div className={`w-3 h-3 rounded-full mr-2 ${
                          permit.status === PermitStatus.ACTIVE ? 'bg-green-500' :
                          permit.status === PermitStatus.HOT ? 'bg-red-500' :
                          permit.status === PermitStatus.UNDER_REVIEW ? 'bg-orange-500' :
                          permit.status === PermitStatus.COMPLETED ? 'bg-gray-500' :
                          'bg-gray-400'
                        }`} />
                        {permit.siteNumber}
                      </Button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="h-full overflow-auto p-4">
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {filteredPermits.map(permit => (
                  <PermitCard
                    key={permit.id}
                    permit={permit}
                    onSelect={setSelectedPermit}
                    isSelected={selectedPermit?.id === permit.id}
                  />
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        {selectedPermit && (
          <div className="w-96 border-l bg-card overflow-auto">
            <div className="p-4 border-b">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold">Permit Details</h2>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setSelectedPermit(null)}
                  className="touch-target"
                >
                  ×
                </Button>
              </div>
            </div>
            
            <div className="p-4">
              <PermitCard 
                permit={selectedPermit}
                onSelect={() => {}}
                isSelected={true}
              />
              
              <div className="mt-4 space-y-2">
                <Button className="w-full touch-target">
                  Generate LDP Quote
                </Button>
                <Button variant="outline" className="w-full touch-target">
                  Add to Route
                </Button>
                <Button variant="outline" className="w-full touch-target">
                  Mark as HOT
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}