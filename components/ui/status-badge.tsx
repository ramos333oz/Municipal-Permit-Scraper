"use client"

import { Badge } from "@/components/ui/badge"
import { PermitStatus } from "@/app/enums"
import { cn } from "@/lib/utils"

interface StatusBadgeProps {
  status: PermitStatus
  className?: string
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const getStatusConfig = (status: PermitStatus) => {
    switch (status) {
      case PermitStatus.ACTIVE:
        return {
          label: "Active",
          className: "permit-status-active"
        }
      case PermitStatus.HOT:
        return {
          label: "HOT",
          className: "permit-status-hot"
        }
      case PermitStatus.UNDER_REVIEW:
        return {
          label: "Under Review",
          className: "permit-status-review"
        }
      case PermitStatus.COMPLETED:
        return {
          label: "Completed",
          className: "permit-status-completed"
        }
      case PermitStatus.INACTIVE:
        return {
          label: "Inactive",
          className: "permit-status-inactive"
        }
      default:
        return {
          label: "Unknown",
          className: "bg-gray-500 text-white"
        }
    }
  }

  const config = getStatusConfig(status)

  return (
    <Badge 
      className={cn(
        "text-xs font-medium uppercase tracking-wide",
        config.className,
        className
      )}
    >
      {config.label}
    </Badge>
  )
}