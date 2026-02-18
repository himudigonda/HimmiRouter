import { DashboardLayout } from "@/components/layout"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import { AuthService } from "@/lib/auth"
import { Key, LogOut, Shield, Trash2, User } from "lucide-react"
import React, { useEffect, useState } from "react"

const PROVIDERS = ["OpenAI", "Google", "Anthropic", "Groq", "Perplexity", "Mistral", "xAI"]

export const SettingsPage: React.FC = () => {
  const [user, setUser] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [configuredProviders, setConfiguredProviders] = useState<Set<string>>(new Set())
  const [keyInputs, setKeyInputs] = useState<Record<string, string>>({})
  const [savingState, setSavingState] = useState<Record<string, boolean>>({})

  useEffect(() => {
    const fetchData = async () => {
      const userData = await AuthService.getUserStatus()
      setUser(userData)
      
      if (userData?.id) {
          try {
              const res = await fetch(`http://localhost:4000/users/${userData.id}/provider-keys`)
              if (res.ok) {
                  const keys = await res.json()
                  setConfiguredProviders(new Set(keys.map((k: any) => k.provider)))
              }
          } catch (e) {
              console.error("Failed to fetch provider keys", e)
          }
      }
      
      setLoading(false)
    }
    fetchData()
  }, [])

  const handleSaveKey = async (provider: string) => {
      const key = keyInputs[provider]
      if (!key) return
      
      setSavingState(prev => ({ ...prev, [provider]: true }))
      try {
          const res = await fetch(`http://localhost:4000/users/${user.id}/provider-keys`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                  provider_name: provider, // Use clean name "OpenAI"
                  api_key: key
              })
          })
          
          if (res.ok) {
              setConfiguredProviders(prev => new Set(prev).add(provider))
              setKeyInputs(prev => ({ ...prev, [provider]: "" })) // Clear input
          }
      } catch (e) {
          alert("Failed to save key")
      } finally {
          setSavingState(prev => ({ ...prev, [provider]: false }))
      }
  }

  const handleDeleteKey = async (provider: string) => {
      if (!confirm(`Remove ${provider} key?`)) return
      try {
          // Frontend sends "OpenAI", backend expects what we stored.
          // Note: Backend stores "OpenAI" if we sent "OpenAI".
          const res = await fetch(`http://localhost:4000/users/${user.id}/provider-keys/${provider}`, {
              method: "DELETE"
          })
          if (res.ok) {
              setConfiguredProviders(prev => {
                  const next = new Set(prev)
                  next.delete(provider)
                  return next
              })
          }
      } catch (e) {
         alert("Failed to delete key")
      }
  }

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

          {/* Provider Keys (BYOK) */}
          <Card className="glass border-white/10">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Key className="w-5 h-5 text-emerald-400" />
                <CardTitle>Provider API Keys</CardTitle>
              </div>
              <CardDescription>Bring Your Own Key (BYOK) - Your keys are encrypted at rest.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
               {PROVIDERS.map(provider => {
                   const isConfigured = configuredProviders.has(provider)
                   return (
                   <div key={provider} className={`flex flex-col md:flex-row md:items-center gap-4 p-4 rounded-xl border transition-all ${isConfigured ? 'bg-emerald-500/5 border-emerald-500/20' : 'bg-black/20 border-white/5'}`}>
                      <div className="flex-1 space-y-2">
                        <div className="flex items-center gap-2">
                            <Label className="text-white font-medium">{provider}</Label>
                            {isConfigured && <Badge variant="outline" className="border-emerald-500/50 text-emerald-400 text-[10px] h-5 bg-emerald-500/10">Active</Badge>}
                        </div>
                        <div className="flex gap-2">
                            <Input 
                                type="password" 
                                placeholder={isConfigured ? "••••••••••••••••••••••••" : `sk-...`}
                                className="bg-white/5 border-white/10 text-white placeholder:text-muted-foreground/30 font-mono text-sm"
                                value={keyInputs[provider] || ""}
                                onChange={(e) => setKeyInputs(prev => ({ ...prev, [provider]: e.target.value }))}
                            />
                            <Button 
                                size="sm" 
                                className={isConfigured ? "bg-white/5 hover:bg-white/10 text-white border border-white/10" : "bg-emerald-600 hover:bg-emerald-500 text-white"}
                                onClick={() => handleSaveKey(provider)}
                                disabled={!keyInputs[provider] || savingState[provider]}
                            >
                                {savingState[provider] ? "..." : (isConfigured ? "Update" : "Save")}
                            </Button>
                             {isConfigured && (
                                <Button size="icon" variant="ghost" className="shrink-0 text-red-400 hover:text-red-300 hover:bg-red-500/10" onClick={() => handleDeleteKey(provider)}>
                                    <Trash2 className="w-4 h-4" />
                                </Button>
                             )}
                        </div>
                      </div>
                   </div>
                   )
               })}
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
