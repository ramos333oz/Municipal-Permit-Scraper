import { Suspense } from 'react'
import { Metadata } from 'next'
import DashboardLayout from '@/components/dashboard/DashboardLayout'
import DashboardOverview from '@/components/dashboard/DashboardOverview'
import DistanceCalculationPanel from '@/components/distance/DistanceCalculationPanel'
import CacheStatsPanel from '@/components/cache/CacheStatsPanel'
import LoadingSpinner from '@/components/ui/LoadingSpinner'

export const metadata: Metadata = {
  title: 'Municipal Permit Distance Calculator - Dashboard',
  description: 'Distance calculation dashboard for municipal permit tracking and LDP pricing calculations',
}

/**
 * Main Dashboard Page - Municipal Permit Distance Calculation System
 * 
 * Features:
 * - Real-time distance calculations with Google Maps API
 * - LDP pricing formula: (Roundtrip Minutes × 1.83) + Added Minutes
 * - Batch processing for multiple routes
 * - Cache management and performance monitoring
 * - Construction industry workflow optimization
 */
export default function DashboardPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Dashboard Overview Section */}
        <section className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                Distance Calculation Dashboard
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-2">
                Municipal permit tracking with drive-time calculations and LDP pricing
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-500 dark:text-gray-400">
                Last updated: {new Date().toLocaleTimeString()}
              </div>
            </div>
          </div>
          
          <Suspense fallback={<LoadingSpinner />}>
            <DashboardOverview />
          </Suspense>
        </section>

        {/* Distance Calculation Tools */}
        <section className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          {/* Distance Calculation Panel */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                Distance Calculation Tools
              </h2>
              <Suspense fallback={<LoadingSpinner />}>
                <DistanceCalculationPanel />
              </Suspense>
            </div>
          </div>

          {/* Cache Management Panel */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                Cache & Performance
              </h2>
              <Suspense fallback={<LoadingSpinner />}>
                <CacheStatsPanel />
              </Suspense>
            </div>
          </div>
        </section>

        {/* Quick Actions */}
        <section className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-700 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Quick Actions
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="flex items-center justify-center p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-600 hover:shadow-md transition-shadow">
              <div className="text-center">
                <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center mx-auto mb-2">
                  <svg className="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                  </svg>
                </div>
                <span className="text-sm font-medium text-gray-900 dark:text-white">Calculate Route</span>
              </div>
            </button>
            
            <button className="flex items-center justify-center p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-600 hover:shadow-md transition-shadow">
              <div className="text-center">
                <div className="w-8 h-8 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mx-auto mb-2">
                  <svg className="w-4 h-4 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                  </svg>
                </div>
                <span className="text-sm font-medium text-gray-900 dark:text-white">LDP Pricing</span>
              </div>
            </button>
            
            <button className="flex items-center justify-center p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-600 hover:shadow-md transition-shadow">
              <div className="text-center">
                <div className="w-8 h-8 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center mx-auto mb-2">
                  <svg className="w-4 h-4 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <span className="text-sm font-medium text-gray-900 dark:text-white">Batch Process</span>
              </div>
            </button>
          </div>
        </section>
      </div>
    </DashboardLayout>
  )
}
