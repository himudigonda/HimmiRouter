import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { AuthService } from "@/lib/auth"
import { motion } from "framer-motion"
import { Loader2 } from "lucide-react"
import React, { useState } from "react"

interface AuthPageProps {
  onSuccess: () => void
}

export const AuthPage: React.FC<AuthPageProps> = ({ onSuccess }) => {
  const [mode, setMode] = useState<"login" | "register">("login")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)
    try {
      if (mode === "register") {
        await AuthService.register(email, password)
      } else {
        await AuthService.login(email, password)
      }
      onSuccess()
    } catch (err: any) {
      setError(err.body?.detail || err.message || "Authentication failed")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background relative overflow-hidden">
      {/* Background Glows */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-primary/20 rounded-full blur-[120px] pointer-events-none" />
      
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="w-full max-w-md z-10 px-4"
      >
        <Card className="glass shadow-2xl">
          <CardHeader className="space-y-1">
            <div className="flex justify-center mb-6">
              <div className="w-12 h-12 rounded-xl bg-primary glow-emerald flex items-center justify-center font-bold text-2xl text-primary-foreground">
                H
              </div>
            </div>
            <CardTitle className="text-2xl text-center font-bold tracking-tight">
              {mode === "login" ? "Welcome back" : "Create an account"}
            </CardTitle>
            <CardDescription className="text-center">
              {mode === "login" 
                ? "Enter your credentials to access the workbench." 
                : "Welcome to the future of LLM Routing."
              }
            </CardDescription>
          </CardHeader>
          <form onSubmit={handleAuth}>
            <CardContent className="grid gap-4">
              <div className="grid gap-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="name@example.com"
                  required
                  className="bg-white/5 border-white/10"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  required
                  className="bg-white/5 border-white/10"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
              {error && <p className="text-sm text-destructive font-medium text-center">{error}</p>}
            </CardContent>
            <CardFooter className="flex flex-col gap-4">
              <Button 
                type="submit" 
                className="w-full h-11 glow-emerald" 
                disabled={isLoading}
              >
                {isLoading ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  mode === "login" ? "Login" : "Initialize Gateway"
                )}
              </Button>
              
              <button
                type="button"
                onClick={() => setMode(mode === "login" ? "register" : "login")}
                className="text-sm text-muted-foreground hover:text-primary transition-colors mt-2"
              >
                {mode === "login" 
                  ? "Don't have an account? Sign up" 
                  : "Already have an account? Login"
                }
              </button>
            </CardFooter>
          </form>
        </Card>
      </motion.div>
    </div>
  )
}
