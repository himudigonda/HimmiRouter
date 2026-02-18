import { DefaultService as ControlService } from "@/client-control"
import { DashboardLayout } from "@/components/layout"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { AnimatePresence, motion } from "framer-motion"
import { Check, Copy, Key, Wallet } from "lucide-react"
import React, { useEffect, useState } from "react"

export const DashboardPage: React.FC = () => {
  const [user, setUser] = useState<any>(null)
  const [apiKeys, setApiKeys] = useState<any[]>([])
  const [newKeyName, setNewKeyName] = useState("")
  const [isCreating, setIsCreating] = useState(false)
  const [copiedKey, setCopiedKey] = useState<string | null>(null)
  const [lastCreatedKey, setLastCreatedKey] = useState<string | null>(null)

  useEffect(() => {
    const session = localStorage.getItem("himmi_user")
    if (session) {
      const userData = JSON.parse(session)
      fetchData(userData.id)
    }
  }, [])

  const fetchData = async (userId: number) => {
    try {
      const [keys, status] = await Promise.all([
        ControlService.listApiKeysApiKeysGet(userId),
        ControlService.getUserStatusUsersUserIdGet(userId)
      ])
      setApiKeys(keys)
      setUser(status)
    } catch (err) {
      console.error("Failed to fetch data", err)
    }
  }

  const handleCreateKey = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!user) return
    setIsCreating(true)
    try {
      const result = await ControlService.createNewKeyApiKeysCreatePost(
        newKeyName,
        user.id
      )
      setLastCreatedKey(result.api_key)
      setNewKeyName("")
      fetchData(user.id)
    } catch (err) {
      console.error("Failed to create key", err)
    } finally {
      setIsCreating(false)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopiedKey(text)
    setTimeout(() => setCopiedKey(null), 2000)
  }

  if (!user) return null

  return (
    <DashboardLayout>
      <div className="grid gap-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">Service Overview</h1>
          <p className="text-muted-foreground">Manage your infrastructure and monitor credit consumption.</p>
        </div>

        {/* Header Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="glass border-primary/20 relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <Wallet size={48} />
            </div>
            <CardHeader className="pb-2">
              <CardDescription>Available Credits</CardDescription>
              <CardTitle className="text-4xl font-bold flex items-baseline gap-2">
                {user.credits.toLocaleString()}
                <span className="text-sm font-medium text-muted-foreground uppercase tracking-widest">Units</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Badge variant="emerald" className="animate-pulse">Active Balance</Badge>
            </CardContent>
          </Card>

          <Card className="glass border-white/10 opacity-60">
            <CardHeader className="pb-2">
              <CardDescription>Request Count (24h)</CardDescription>
              <CardTitle className="text-4xl font-bold">0</CardTitle>
            </CardHeader>
            <CardContent>
              <Badge variant="secondary">Incoming...</Badge>
            </CardContent>
          </Card>

          <Card className="glass border-white/10 opacity-60">
            <CardHeader className="pb-2">
              <CardDescription>Global Latency</CardDescription>
              <CardTitle className="text-4xl font-bold">-- ms</CardTitle>
            </CardHeader>
            <CardContent>
              <Badge variant="secondary">Offline</Badge>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <div className="grid gap-6">
          <Card className="glass border-white/10">
            <CardHeader>
              <CardTitle>Create Management Key</CardTitle>
              <CardDescription>Keys are used to authenticate your requests against the Inference Gateway.</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreateKey} className="flex gap-4">
                <div className="flex-1 space-y-2">
                  <Input
                    placeholder="Key Name (e.g. Production Client)"
                    value={newKeyName}
                    onChange={(e) => setNewKeyName(e.target.value)}
                    className="bg-white/5"
                    required
                  />
                </div>
                <Button type="submit" disabled={isCreating} className="glow-emerald">
                  {isCreating ? "Creating..." : "Generate Key"}
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Last Created Key Alert */}
          <AnimatePresence>
            {lastCreatedKey && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
              >
                <Card className="bg-primary/10 border-primary/30 text-primary-foreground">
                  <CardHeader className="py-4">
                    <CardTitle className="text-sm">New Key Generated</CardTitle>
                    <CardDescription className="text-primary-foreground/70">
                      Copy this key now. You won't be able to see it again.
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="pb-4">
                    <div className="flex items-center gap-2 p-3 bg-black/40 rounded-lg border border-white/10">
                      <code className="flex-1 font-mono text-xs overflow-x-auto">{lastCreatedKey}</code>
                      <Button 
                        variant="ghost" 
                        size="icon" 
                        className="h-8 w-8"
                        onClick={() => copyToClipboard(lastCreatedKey)}
                      >
                        {copiedKey === lastCreatedKey ? <Check size={14} /> : <Copy size={14} />}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>

          {/* API Keys Table */}
          <Card className="glass border-white/10 overflow-hidden">
            <CardHeader className="bg-white/5 border-b border-white/10">
              <CardTitle className="text-sm font-semibold flex items-center gap-2">
                <Key className="w-4 h-4 text-primary" /> Active API Keys
              </CardTitle>
            </CardHeader>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-white/5 text-muted-foreground uppercase text-[10px] tracking-widest font-bold font-mono">
                  <tr>
                    <th className="px-6 py-4">Name</th>
                    <th className="px-6 py-4">Prefix</th>
                    <th className="px-6 py-4 text-right">Usage</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {apiKeys.length === 0 ? (
                    <tr>
                      <td colSpan={3} className="px-6 py-10 text-center text-muted-foreground italic">
                        No keys found. Generate one to get started.
                      </td>
                    </tr>
                  ) : (
                    apiKeys.map((key) => (
                      <motion.tr 
                        key={key.id}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="hover:bg-white/[0.02] transition-colors"
                      >
                        <td className="px-6 py-4 font-medium">{key.name}</td>
                        <td className="px-6 py-4 font-mono text-xs opacity-60 text-primary">{key.key_prefix}</td>
                        <td className="px-6 py-4 text-right tabular-nums">{key.credits_consumed.toLocaleString()} Units</td>
                      </motion.tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  )
}
