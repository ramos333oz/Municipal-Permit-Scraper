'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { 
  Search, 
  Bell, 
  Settings, 
  User, 
  Menu,
  MapPin,
  FileText,
  Calculator
} from 'lucide-react'

export function DashboardHeader() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          {/* Logo and Title */}
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              <Menu className="h-5 w-5" />
            </Button>
            
            <div className="flex items-center space-x-2">
              <div className="h-8 w-8 rounded-lg bg-construction-primary flex items-center justify-center">
                <MapPin className="h-5 w-5 text-white" />
              </div>
              <div className="hidden sm:block">
                <h1 className="text-lg font-semibold">Municipal Permit Tracker</h1>
                <p className="text-xs text-muted-foreground">Construction Management System</p>
              </div>
            </div>
          </div>

          {/* Search Bar */}
          <div className="hidden md:flex flex-1 max-w-md mx-8">
            <div className="relative w-full">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search permits, addresses, or project IDs..."
                className="pl-10 field-input"
              />
            </div>
          </div>

          {/* Navigation and Actions */}
          <div className="flex items-center space-x-2">
            {/* Quick Action Buttons */}
            <div className="hidden lg:flex items-center space-x-2">
              <Button variant="outline" size="sm" className="touch-target">
                <FileText className="h-4 w-4 mr-2" />
                New Permit
              </Button>
              <Button variant="outline" size="sm" className="touch-target">
                <Calculator className="h-4 w-4 mr-2" />
                LDP Quote
              </Button>
            </div>

            {/* Notifications */}
            <Button variant="ghost" size="icon" className="touch-target">
              <Bell className="h-5 w-5" />
              <span className="sr-only">Notifications</span>
            </Button>

            {/* Settings */}
            <Button variant="ghost" size="icon" className="touch-target">
              <Settings className="h-5 w-5" />
              <span className="sr-only">Settings</span>
            </Button>

            {/* User Profile */}
            <Button variant="ghost" size="icon" className="touch-target">
              <User className="h-5 w-5" />
              <span className="sr-only">User menu</span>
            </Button>
          </div>
        </div>

        {/* Mobile Search */}
        <div className="md:hidden pb-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search permits..."
              className="pl-10 field-input"
            />
          </div>
        </div>
      </div>
    </header>
  )
}
