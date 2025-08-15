'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { 
  Plus, 
  Calculator, 
  FileText, 
  Map, 
  Download,
  Upload
} from 'lucide-react'

const actions = [
  {
    title: "New Permit",
    description: "Add a new permit to track",
    icon: Plus,
    action: () => console.log("New permit"),
    variant: "default" as const
  },
  {
    title: "LDP Quote",
    description: "Generate pricing quote",
    icon: Calculator,
    action: () => console.log("LDP Quote"),
    variant: "outline" as const
  },
  {
    title: "Export Data",
    description: "Download permit data",
    icon: Download,
    action: () => console.log("Export"),
    variant: "outline" as const
  },
  {
    title: "Import Permits",
    description: "Bulk upload permits",
    icon: Upload,
    action: () => console.log("Import"),
    variant: "outline" as const
  },
  {
    title: "View Map",
    description: "Full screen map view",
    icon: Map,
    action: () => console.log("Map view"),
    variant: "outline" as const
  },
  {
    title: "Reports",
    description: "Generate reports",
    icon: FileText,
    action: () => console.log("Reports"),
    variant: "outline" as const
  }
]

export function QuickActions() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Quick Actions</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {actions.map((action) => {
          const Icon = action.icon
          return (
            <Button
              key={action.title}
              variant={action.variant}
              className="w-full justify-start h-auto p-3 touch-target"
              onClick={action.action}
            >
              <div className="flex items-center space-x-3">
                <Icon className="h-5 w-5 flex-shrink-0" />
                <div className="text-left">
                  <div className="font-medium">{action.title}</div>
                  <div className="text-xs text-muted-foreground">
                    {action.description}
                  </div>
                </div>
              </div>
            </Button>
          )
        })}
      </CardContent>
    </Card>
  )
}
