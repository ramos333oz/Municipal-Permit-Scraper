"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { StatusBadge } from "./ui/status-badge"
import { PermitData } from "@/app/types"
import { MaterialType, ExportFormat } from "@/app/enums"
import { formatCurrency, formatPhoneNumber } from "@/lib/formatters"
import { FileDown, FileUp, Mail, Calculator } from "lucide-react"

interface QuoteSheetProps {
  permit: PermitData
  onExport?: (format: ExportFormat) => void
}

export function QuoteSheet({ permit, onExport }: QuoteSheetProps) {
  const [formData, setFormData] = useState({
    projectCompany: permit.projectCompany,
    projectContact: permit.projectContact,
    projectPhone: permit.projectPhone,
    projectEmail: permit.projectEmail,
    materialDescription: permit.materialDescription,
    quantity: permit.quantity,
    dumpFee: permit.dumpFee,
    ldpFee: permit.ldpFee,
    addedMinutes: permit.addedMinutes,
    notes: permit.notes || ""
  })

  const [errors, setErrors] = useState<Record<string, string>>({})
  const [isCalculating, setIsCalculating] = useState(false)

  // Calculate pricing in real-time
  const truckingPrice = (permit.roundtripMinutes * 1.83) + formData.addedMinutes
  const totalPricePerLoad = formData.dumpFee + truckingPrice + formData.ldpFee
  const estimatedLoads = Math.ceil(formData.quantity / 10) // Assuming 10 CY per load

  // Validation
  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.projectCompany.trim()) {
      newErrors.projectCompany = "Company name is required"
    }
    if (!formData.projectContact.trim()) {
      newErrors.projectContact = "Contact name is required"
    }
    if (!formData.projectEmail.includes("@")) {
      newErrors.projectEmail = "Valid email is required"
    }
    if (formData.quantity <= 0) {
      newErrors.quantity = "Quantity must be greater than 0"
    }
    if (formData.dumpFee < 0) {
      newErrors.dumpFee = "Dump fee cannot be negative"
    }
    if (formData.ldpFee < 0) {
      newErrors.ldpFee = "LDP fee cannot be negative"
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: "" }))
    }
  }

  const handleExport = async (format: ExportFormat) => {
    if (!validateForm()) return

    setIsCalculating(true)
    // Simulate export processing
    setTimeout(() => {
      setIsCalculating(false)
      onExport?.(format)
    }, 1500)
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-2xl">LDP Quote Sheet</CardTitle>
              <p className="text-muted-foreground mt-1">
                Site: {permit.siteNumber} • {permit.projectCity}
              </p>
            </div>
            <StatusBadge status={permit.status} />
          </div>
        </CardHeader>
      </Card>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Main Form */}
        <div className="lg:col-span-2 space-y-6">
          {/* Contact Information */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Contact Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="company">Project Company *</Label>
                  <Input
                    id="company"
                    value={formData.projectCompany}
                    onChange={(e) => handleInputChange("projectCompany", e.target.value)}
                    className={errors.projectCompany ? "border-destructive" : ""}
                  />
                  {errors.projectCompany && (
                    <p className="text-sm text-destructive">{errors.projectCompany}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="contact">Project Contact *</Label>
                  <Input
                    id="contact"
                    value={formData.projectContact}
                    onChange={(e) => handleInputChange("projectContact", e.target.value)}
                    className={errors.projectContact ? "border-destructive" : ""}
                  />
                  {errors.projectContact && (
                    <p className="text-sm text-destructive">{errors.projectContact}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="phone">Project Phone</Label>
                  <Input
                    id="phone"
                    value={formData.projectPhone}
                    onChange={(e) => handleInputChange("projectPhone", e.target.value)}
                    placeholder="(555) 123-4567"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">Project Email *</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.projectEmail}
                    onChange={(e) => handleInputChange("projectEmail", e.target.value)}
                    className={errors.projectEmail ? "border-destructive" : ""}
                  />
                  {errors.projectEmail && (
                    <p className="text-sm text-destructive">{errors.projectEmail}</p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Material Details */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Material & Quantity</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="material">Material Description</Label>
                  <Select
                    value={formData.materialDescription}
                    onValueChange={(value) => handleInputChange("materialDescription", value as MaterialType)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value={MaterialType.DIRT}>Dirt</SelectItem>
                      <SelectItem value={MaterialType.SAND}>Sand</SelectItem>
                      <SelectItem value={MaterialType.GRAVEL}>Gravel</SelectItem>
                      <SelectItem value={MaterialType.CONCRETE}>Concrete</SelectItem>
                      <SelectItem value={MaterialType.ASPHALT}>Asphalt</SelectItem>
                      <SelectItem value={MaterialType.MIXED}>Mixed Materials</SelectItem>
                      <SelectItem value={MaterialType.OTHER}>Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="quantity">Quantity (CY) *</Label>
                  <Input
                    id="quantity"
                    type="number"
                    value={formData.quantity}
                    onChange={(e) => handleInputChange("quantity", parseFloat(e.target.value) || 0)}
                    className={errors.quantity ? "border-destructive" : ""}
                  />
                  {errors.quantity && (
                    <p className="text-sm text-destructive">{errors.quantity}</p>
                  )}
                  <p className="text-sm text-muted-foreground">
                    Estimated loads: {estimatedLoads}
                  </p>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="notes">Additional Notes</Label>
                <Textarea
                  id="notes"
                  value={formData.notes}
                  onChange={(e) => handleInputChange("notes", e.target.value)}
                  placeholder="Any special requirements or notes..."
                  rows={3}
                />
              </div>
            </CardContent>
          </Card>

          {/* Manual Adjustments */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Manual Adjustments</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="addedMinutes">Added Minutes</Label>
                  <Input
                    id="addedMinutes"
                    type="number"
                    value={formData.addedMinutes}
                    onChange={(e) => handleInputChange("addedMinutes", parseFloat(e.target.value) || 0)}
                    min="0"
                    max="60"
                  />
                  <p className="text-sm text-muted-foreground">
                    Typical range: 5-30 minutes
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="dumpFee">Dump Fee ($)</Label>
                  <Input
                    id="dumpFee"
                    type="number"
                    step="0.01"
                    value={formData.dumpFee}
                    onChange={(e) => handleInputChange("dumpFee", parseFloat(e.target.value) || 0)}
                    className={errors.dumpFee ? "border-destructive" : ""}
                  />
                  {errors.dumpFee && (
                    <p className="text-sm text-destructive">{errors.dumpFee}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="ldpFee">LDP Fee ($)</Label>
                  <Input
                    id="ldpFee"
                    type="number"
                    step="0.01"
                    value={formData.ldpFee}
                    onChange={(e) => handleInputChange("ldpFee", parseFloat(e.target.value) || 0)}
                    className={errors.ldpFee ? "border-destructive" : ""}
                  />
                  {errors.ldpFee && (
                    <p className="text-sm text-destructive">{errors.ldpFee}</p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Pricing Calculator */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Calculator className="h-5 w-5" />
                Pricing Calculation
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span>Roundtrip Minutes:</span>
                  <span className="font-mono">{permit.roundtripMinutes}</span>
                </div>
                
                <div className="flex justify-between text-sm">
                  <span>Base Calculation:</span>
                  <span className="font-mono">
                    {permit.roundtripMinutes} × 1.83 = {formatCurrency(permit.roundtripMinutes * 1.83)}
                  </span>
                </div>
                
                <div className="flex justify-between text-sm">
                  <span>Added Minutes:</span>
                  <span className="font-mono">+{formatCurrency(formData.addedMinutes)}</span>
                </div>
                
                <div className="flex justify-between text-sm border-t pt-2">
                  <span className="font-medium">Trucking Price/Load:</span>
                  <span className="font-mono font-medium">{formatCurrency(truckingPrice)}</span>
                </div>
                
                <div className="flex justify-between text-sm">
                  <span>Dump Fee:</span>
                  <span className="font-mono">{formatCurrency(formData.dumpFee)}</span>
                </div>
                
                <div className="flex justify-between text-sm">
                  <span>LDP Fee:</span>
                  <span className="font-mono">{formatCurrency(formData.ldpFee)}</span>
                </div>
                
                <div className="flex justify-between text-lg font-bold border-t pt-2 bg-primary/5 -mx-3 px-3 py-2 rounded">
                  <span>Total Price/Load:</span>
                  <span className="font-mono">{formatCurrency(totalPricePerLoad)}</span>
                </div>
                
                <div className="text-center text-sm text-muted-foreground">
                  Total Project: {formatCurrency(totalPricePerLoad * estimatedLoads)}
                  <br />
                  ({estimatedLoads} loads estimated)
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Export Controls */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Export Quote Sheet</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button
                className="w-full touch-target"
                onClick={() => handleExport(ExportFormat.PDF)}
                disabled={isCalculating}
              >
                <FileDown className="h-4 w-4 mr-2" />
                {isCalculating ? "Generating..." : "Export PDF"}
              </Button>
              
              <Button
                variant="outline"
                className="w-full touch-target"
                onClick={() => handleExport(ExportFormat.EXCEL)}
                disabled={isCalculating}
              >
                <FileUp className="h-4 w-4 mr-2" />
                Export Excel
              </Button>
              
              <Button
                variant="outline"
                className="w-full touch-target"
                onClick={() => handleExport(ExportFormat.CSV)}
                disabled={isCalculating}
              >
                Export CSV
              </Button>
              
              <Button
                variant="outline"
                className="w-full touch-target"
                disabled={isCalculating}
              >
                <Mail className="h-4 w-4 mr-2" />
                Email Quote
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}