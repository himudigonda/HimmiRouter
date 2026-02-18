import { DashboardLayout } from "@/components/layout"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import { AuthService } from "@/lib/auth"
import { LogOut, Shield, User } from "lucide-react"
import React, { useEffect, useState } from "react"

export const SettingsPage: React.FC = () => {
  const [user, setUser] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchUser = async () => {
      const userData = await AuthService.getUserStatus()
      setUser(userData)
      setLoading(false)
    }
    fetchUser()
  }, [])

  const handleLogout = () => {
    AuthService.logout()
    window.location.reload()
  }

  if (loading) return null

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in duration-500">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">Account Settings</h1>
          <p className="text-muted-foreground">Manage your profile and security preferences.</p>
        </div>

        <div className="grid gap-6">
          {/* Profile Section */}
          <Card className="glass border-white/10">
            <CardHeader>
              <div className="flex items-center gap-2">
                <User className="w-5 h-5 text-primary" />
                <CardTitle>Profile Information</CardTitle>
              </div>
              <CardDescription>Your personal account details</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-2">
                <Label>Email Address</Label>
                <Input value={user?.email || ""} disabled className="bg-white/5 border-white/10" />
                <p className="text-xs text-muted-foreground">Managed by system administrator</p>
              </div>
              <div className="grid gap-2">
                <Label>Account ID</Label>
                <div className="font-mono text-sm bg-black/20 p-2 rounded border border-white/5 w-fit">
                  {user?.id}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Billing / Credits Section */}
          <Card className="glass border-white/10">
             <CardHeader>
              <div className="flex items-center gap-2">
                <Shield className="w-5 h-5 text-emerald-400" />
                <CardTitle>Plans & Billing</CardTitle>
              </div>
              <CardDescription>View your current plan and credit usage</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                <div>
                  <p className="font-semibold text-emerald-400">Trial Plan</p>
                  <p className="text-xs text-emerald-400/80">Active since registration</p>
                </div>
                <Badge className="bg-emerald-500 text-white hover:bg-emerald-600">Active</Badge>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Current Balance</span>
                  <span className="font-mono">${(user?.credits || 0).toFixed(2)}</span>
                </div>
                 <div className="h-2 rounded-full bg-white/10 overflow-hidden">
                    <div className="h-full bg-emerald-500 w-full animate-pulse" style={{ width: `${Math.min(100, (user?.credits || 0) * 10)}%` }} />
                 </div>
                 <p className="text-xs text-muted-foreground text-right">Top-up is currently disabled in simulator mode.</p>
              </div>
            </CardContent>
          </Card>

          <Separator className="bg-white/10" />

          {/* Danger Zone */}
          <div className="pt-4">
            <h3 className="text-red-400 font-semibold mb-4 text-sm uppercase tracking-wider">Danger Zone</h3>
            <div className="p-4 rounded-lg border border-red-500/20 bg-red-500/5 flex items-center justify-between">
              <div>
                <p className="font-medium text-red-200">Sign Out</p>
                <p className="text-xs text-red-200/60">End your current session</p>
              </div>
              <Button variant="destructive" size="sm" onClick={handleLogout} className="bg-red-500/80 hover:bg-red-500 text-white">
                <LogOut className="w-4 h-4 mr-2" /> 
                Sign Out
              </Button>
            </div>
          </div>

        </div>
      </div>
    </DashboardLayout>
  )
}
