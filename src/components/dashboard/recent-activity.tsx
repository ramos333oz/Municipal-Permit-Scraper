'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  FileCheck, 
  Clock, 
  AlertTriangle, 
  CheckCircle,
  XCircle
} from 'lucide-react'

// Mock data - replace with real data from Supabase
const activities = [
  {
    id: 1,
    type: "approved",
    title: "Permit #GR-2024-0156",
    description: "Grading permit approved for Sunset Blvd project",
    time: "2 hours ago",
    status: "approved",
    icon: CheckCircle
  },
  {
    id: 2,
    type: "pending",
    title: "Permit #GR-2024-0157",
    description: "New grading permit submitted for review",
    time: "4 hours ago",
    status: "pending",
    icon: Clock
  },
  {
    id: 3,
    type: "expiring",
    title: "Permit #GR-2024-0145",
    description: "Permit expires in 5 days - renewal required",
    time: "1 day ago",
    status: "warning",
    icon: AlertTriangle
  },
  {
    id: 4,
    type: "rejected",
    title: "Permit #GR-2024-0158",
    description: "Application rejected - missing documentation",
    time: "2 days ago",
    status: "rejected",
    icon: XCircle
  },
  {
    id: 5,
    type: "updated",
    title: "Permit #GR-2024-0140",
    description: "Permit details updated with new contractor info",
    time: "3 days ago",
    status: "updated",
    icon: FileCheck
  }
]

const statusConfig = {
  approved: { color: "bg-green-100 text-green-800", label: "Approved" },
  pending: { color: "bg-yellow-100 text-yellow-800", label: "Pending" },
  warning: { color: "bg-orange-100 text-orange-800", label: "Expiring" },
  rejected: { color: "bg-red-100 text-red-800", label: "Rejected" },
  updated: { color: "bg-blue-100 text-blue-800", label: "Updated" }
}

export function RecentActivity() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Recent Activity</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-3 max-h-96 overflow-y-auto custom-scrollbar">
          {activities.map((activity) => {
            const Icon = activity.icon
            const config = statusConfig[activity.status as keyof typeof statusConfig]
            
            return (
              <div key={activity.id} className="flex items-start space-x-3 p-3 rounded-lg hover:bg-muted/50 transition-colors">
                <div className={`p-2 rounded-full ${config.color}`}>
                  <Icon className="h-4 w-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium truncate">
                      {activity.title}
                    </p>
                    <Badge variant="secondary" className="text-xs">
                      {config.label}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {activity.description}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {activity.time}
                  </p>
                </div>
              </div>
            )
          })}
        </div>
        
        <div className="pt-3 border-t">
          <button className="text-sm text-primary hover:underline w-full text-center">
            View all activity
          </button>
        </div>
      </CardContent>
    </Card>
  )
}
