"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"
import { Progress } from "@/components/ui/progress"
import { UserData, DashboardMetrics } from "@/app/types"
import { UserRole, PermitStatus } from "@/app/enums"
import { formatDate, formatUserRole } from "@/lib/formatters"
import { 
  Users, 
  FileText, 
  Settings, 
  BarChart3, 
  Plus, 
  Edit, 
  Trash2, 
  Download,
  Upload,
  CheckSquare,
  AlertTriangle
} from "lucide-react"

interface AdminPanelProps {
  users: UserData[]
  metrics: DashboardMetrics
}

export function AdminPanel({ users, metrics }: AdminPanelProps) {
  const [activeTab, setActiveTab] = useState("dashboard")
  const [selectedUsers, setSelectedUsers] = useState<string[]>([])
  const [newUserForm, setNewUserForm] = useState({
    name: "",
    email: "",
    role: UserRole.VIEWER
  })

  const handleUserSelection = (userId: string, checked: boolean) => {
    if (checked) {
      setSelectedUsers(prev => [...prev, userId])
    } else {
      setSelectedUsers(prev => prev.filter(id => id !== userId))
    }
  }

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedUsers(users.map(user => user.id))
    } else {
      setSelectedUsers([])
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="border-b">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-3xl font-bold">Admin Panel</h1>
          <p className="text-muted-foreground">
            Manage permits, users, and system configuration
          </p>
        </div>
      </div>

      <div className="container mx-auto px-4 py-6">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="dashboard" className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              Dashboard
            </TabsTrigger>
            <TabsTrigger value="permits" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Permits
            </TabsTrigger>
            <TabsTrigger value="users" className="flex items-center gap-2">
              <Users className="h-4 w-4" />
              Users
            </TabsTrigger>
            <TabsTrigger value="settings" className="flex items-center gap-2">
              <Settings className="h-4 w-4" />
              Settings
            </TabsTrigger>
          </TabsList>

          {/* Dashboard Tab */}
          <TabsContent value="dashboard" className="space-y-6">
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Permits</CardTitle>
                  <FileText className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{metrics.totalPermits.toLocaleString()}</div>
                  <p className="text-xs text-muted-foreground">
                    +12% from last month
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Active Permits</CardTitle>
                  <CheckSquare className="h-4 w-4 text-green-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-green-600">{metrics.activePermits}</div>
                  <p className="text-xs text-muted-foreground">
                    Available for construction
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">HOT Permits</CardTitle>
                  <AlertTriangle className="h-4 w-4 text-red-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-red-600">{metrics.hotPermits}</div>
                  <p className="text-xs text-muted-foreground">
                    Require immediate attention
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Data Quality</CardTitle>
                  <BarChart3 className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{metrics.dataQualityScore}%</div>
                  <Progress value={metrics.dataQualityScore} className="mt-2" />
                </CardContent>
              </Card>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Recent Activity</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center gap-3">
                      <div className="w-2 h-2 bg-green-500 rounded-full" />
                      <div className="flex-1">
                        <p className="text-sm font-medium">New permit added</p>
                        <p className="text-xs text-muted-foreground">LA-2025-004 • 2 minutes ago</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="w-2 h-2 bg-blue-500 rounded-full" />
                      <div className="flex-1">
                        <p className="text-sm font-medium">Status updated</p>
                        <p className="text-xs text-muted-foreground">SD-2025-002 marked as HOT • 15 minutes ago</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="w-2 h-2 bg-orange-500 rounded-full" />
                      <div className="flex-1">
                        <p className="text-sm font-medium">Quote sheet exported</p>
                        <p className="text-xs text-muted-foreground">OC-2025-003 • 1 hour ago</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>System Health</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Scraping Services</span>
                      <Badge className="bg-green-100 text-green-800">Healthy</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Database</span>
                      <Badge className="bg-green-100 text-green-800">Healthy</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">API Services</span>
                      <Badge className="bg-green-100 text-green-800">Healthy</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Geocoding</span>
                      <Badge className="bg-yellow-100 text-yellow-800">Warning</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Permits Tab */}
          <TabsContent value="permits" className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Permit Management</h2>
              <div className="flex gap-2">
                <Button variant="outline">
                  <Upload className="h-4 w-4 mr-2" />
                  Import
                </Button>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Permit
                </Button>
              </div>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Bulk Operations</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex gap-4 items-center">
                  <Select>
                    <SelectTrigger className="w-[200px]">
                      <SelectValue placeholder="Select action" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="status">Update Status</SelectItem>
                      <SelectItem value="export">Export Selected</SelectItem>
                      <SelectItem value="archive">Archive</SelectItem>
                      <SelectItem value="delete">Delete</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button variant="outline">Apply to Selected</Button>
                  <div className="text-sm text-muted-foreground">
                    {selectedUsers.length} items selected
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Manual Permit Entry</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-3">
                  <div className="space-y-2">
                    <Label htmlFor="siteNumber">Site Number</Label>
                    <Input id="siteNumber" placeholder="LA-2025-XXX" />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="status">Status</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value={PermitStatus.ACTIVE}>Active</SelectItem>
                        <SelectItem value={PermitStatus.HOT}>HOT</SelectItem>
                        <SelectItem value={PermitStatus.UNDER_REVIEW}>Under Review</SelectItem>
                        <SelectItem value={PermitStatus.COMPLETED}>Completed</SelectItem>
                        <SelectItem value={PermitStatus.INACTIVE}>Inactive</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="city">Project City</Label>
                    <Input id="city" placeholder="Los Angeles" />
                  </div>
                </div>
                <div className="mt-4">
                  <Button>Save Permit</Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Users Tab */}
          <TabsContent value="users" className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">User Management</h2>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Add User
              </Button>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Users</CardTitle>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-12">
                        <Checkbox
                          checked={selectedUsers.length === users.length}
                          onCheckedChange={handleSelectAll}
                        />
                      </TableHead>
                      <TableHead>Name</TableHead>
                      <TableHead>Email</TableHead>
                      <TableHead>Role</TableHead>
                      <TableHead>Last Login</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="w-24">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {users.map((user) => (
                      <TableRow key={user.id}>
                        <TableCell>
                          <Checkbox
                            checked={selectedUsers.includes(user.id)}
                            onCheckedChange={(checked) => handleUserSelection(user.id, checked as boolean)}
                          />
                        </TableCell>
                        <TableCell className="font-medium">{user.name}</TableCell>
                        <TableCell>{user.email}</TableCell>
                        <TableCell>
                          <Badge variant="outline">
                            {formatUserRole(user.role)}
                          </Badge>
                        </TableCell>
                        <TableCell>{formatDate(user.lastLogin)}</TableCell>
                        <TableCell>
                          <Badge className={user.isActive ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"}>
                            {user.isActive ? "Active" : "Inactive"}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-1">
                            <Button variant="ghost" size="sm">
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="sm">
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="settings" className="space-y-6">
            <h2 className="text-2xl font-bold">System Settings</h2>

            <div className="grid gap-6 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Scraping Configuration</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="scrapeInterval">Scrape Interval (hours)</Label>
                    <Input id="scrapeInterval" type="number" defaultValue="6" />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="maxRetries">Max Retries</Label>
                    <Input id="maxRetries" type="number" defaultValue="3" />
                  </div>
                  <Button>Save Settings</Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Notification Settings</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="emailNotifications">Email Notifications</Label>
                    <Select defaultValue="enabled">
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="enabled">Enabled</SelectItem>
                        <SelectItem value="disabled">Disabled</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="alertThreshold">Alert Threshold</Label>
                    <Input id="alertThreshold" type="number" defaultValue="10" />
                  </div>
                  <Button>Save Settings</Button>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}