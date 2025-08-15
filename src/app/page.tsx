import { Suspense } from 'react'
import { DashboardHeader } from '@/components/dashboard/dashboard-header'
import { PermitMap } from '@/components/permit-map/permit-map'
import { PermitStats } from '@/components/dashboard/permit-stats'
import { QuickActions } from '@/components/dashboard/quick-actions'
import { RecentActivity } from '@/components/dashboard/recent-activity'
import { LoadingSpinner } from '@/components/ui/loading-spinner'

export default function HomePage() {
  return (
    <div className="flex flex-col min-h-screen">
      <DashboardHeader />
      
      <main className="flex-1 container mx-auto px-4 py-6 space-y-6">
        {/* Stats Overview */}
        <Suspense fallback={<LoadingSpinner />}>
          <PermitStats />
        </Suspense>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Map Section - Takes up most space */}
          <div className="lg:col-span-3">
            <div className="bg-card rounded-lg border shadow-sm">
              <div className="p-4 border-b">
                <h2 className="text-lg font-semibold">Permit Locations</h2>
                <p className="text-sm text-muted-foreground">
                  Interactive map showing all active permits
                </p>
              </div>
              <div className="h-[600px] relative">
                <Suspense fallback={<LoadingSpinner />}>
                  <PermitMap />
                </Suspense>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <QuickActions />
            
            {/* Recent Activity */}
            <Suspense fallback={<LoadingSpinner />}>
              <RecentActivity />
            </Suspense>
          </div>
        </div>
      </main>
    </div>
  )
}
