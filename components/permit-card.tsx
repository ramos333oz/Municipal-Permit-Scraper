"use client"

import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { StatusBadge } from "@/components/ui/status-badge"
import { PermitData } from "@/app/types"
import { MapPin, Phone, Mail, Edit, MoreHorizontal } from "lucide-react"
import { formatCurrency, formatPhoneNumber, formatDate, formatQuantity } from "@/lib/formatters"

interface PermitCardProps {
  permit: PermitData
  onEdit?: (permit: PermitData) => void
  onSelect?: (permit: PermitData) => void
  isSelected?: boolean
}

export function PermitCard({ permit, onEdit, onSelect, isSelected }: PermitCardProps) {
  const truckingPrice = (permit.roundtripMinutes * 1.83) + permit.addedMinutes
  const totalPrice = permit.dumpFee + truckingPrice + permit.ldpFee

  return (
    <Card className={`transition-all duration-200 hover:shadow-md ${isSelected ? 'ring-2 ring-primary' : ''}`}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <h3 className="font-semibold text-lg">{permit.siteNumber}</h3>
            <StatusBadge status={permit.status} />
          </div>
          <div className="flex gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onEdit?.(permit)}
              className="touch-target"
            >
              <Edit className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="touch-target"
            >
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-sm">
            <MapPin className="h-4 w-4 text-muted-foreground" />
            <span className="text-muted-foreground">{permit.projectCity}</span>
          </div>
          <p className="text-sm text-muted-foreground">{permit.address}</p>
        </div>

        <div className="space-y-2">
          <h4 className="font-medium text-sm">Project Details</h4>
          <div className="text-sm space-y-1">
            <p><span className="font-medium">Company:</span> {permit.projectCompany}</p>
            <p><span className="font-medium">Contact:</span> {permit.projectContact}</p>
            <div className="flex items-center gap-2">
              <Phone className="h-3 w-3" />
              <span>{formatPhoneNumber(permit.projectPhone)}</span>
            </div>
            <div className="flex items-center gap-2">
              <Mail className="h-3 w-3" />
              <span>{permit.projectEmail}</span>
            </div>
          </div>
        </div>

        <div className="space-y-2">
          <h4 className="font-medium text-sm">Material & Pricing</h4>
          <div className="text-sm space-y-1">
            <p><span className="font-medium">Material:</span> {permit.materialDescription}</p>
            <p><span className="font-medium">Quantity:</span> {formatQuantity(permit.quantity)}</p>
            <p><span className="font-medium">Total Price/Load:</span> {formatCurrency(totalPrice)}</p>
          </div>
        </div>

        <div className="flex gap-2 pt-2">
          <Button 
            variant="outline" 
            size="sm" 
            className="flex-1 touch-target"
            onClick={() => onSelect?.(permit)}
          >
            View Details
          </Button>
          <Button 
            size="sm" 
            className="flex-1 touch-target"
          >
            Generate Quote
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}