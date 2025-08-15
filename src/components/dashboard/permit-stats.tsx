'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  FileCheck, 
  Clock, 
  AlertTriangle, 
  DollarSign,
  TrendingUp,
  MapPin
} from 'lucide-react'

// Mock data - replace with real data from Supabase
const stats = [
  {
    title: "Active Permits",
    value: "247",
    change: "+12%",
    changeType: "positive" as const,
    icon: FileCheck,
    description: "Currently active permits"
  },
  {
    title: "Pending Review",
    value: "18",
    change: "-5%",
    changeType: "positive" as const,
    icon: Clock,
    description: "Awaiting approval"
  },
  {
    title: "Expiring Soon",
    value: "8",
    change: "+2",
    changeType: "negative" as const,
    icon: AlertTriangle,
    description: "Within 30 days"
  },
  {
    title: "Total Revenue",
    value: "$124,580",
    change: "+18%",
    changeType: "positive" as const,
    icon: DollarSign,
    description: "This month"
  },
  {
    title: "Avg Processing",
    value: "3.2 days",
    change: "-0.5d",
    changeType: "positive" as const,
    icon: TrendingUp,
    description: "Average approval time"
  },
  {
    title: "Coverage Area",
    value: "35 Cities",
    change: "+2",
    changeType: "positive" as const,
    icon: MapPin,
    description: "Municipal coverage"
  }
]

export function PermitStats() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
      {stats.map((stat) => {
        const Icon = stat.icon
        return (
          <Card key={stat.title} className="hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {stat.title}
              </CardTitle>
              <Icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <div className="flex items-center space-x-2 text-xs">
                <span
                  className={`font-medium ${
                    stat.changeType === 'positive'
                      ? 'text-green-600'
                      : 'text-red-600'
                  }`}
                >
                  {stat.change}
                </span>
                <span className="text-muted-foreground">{stat.description}</span>
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
