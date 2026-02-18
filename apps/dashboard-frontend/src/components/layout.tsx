import { AuthService } from "@/lib/auth"
import { motion } from "framer-motion"
import { LayoutDashboard, Library, LogOut, MessageSquare, Settings } from "lucide-react"
import React from "react"

interface LayoutProps {
  children: React.ReactNode
}

export const DashboardLayout: React.FC<LayoutProps> = ({ children }) => {
  const [activePath, setActivePath] = React.useState(window.location.pathname)

  const navItems = [
    { name: "Dashboard", icon: LayoutDashboard, href: "/dashboard" },
    { name: "Playground", icon: MessageSquare, href: "/playground" },
    { name: "Model Library", icon: Library, href: "/models" },
    { name: "Settings", icon: Settings, href: "/settings" },
  ]

  const handleLogout = () => {
    AuthService.logout()
    window.location.href = "/"
  }

  return (
    <div className="min-h-screen bg-background text-foreground relative overflow-hidden flex font-sans">
      {/* Background Decorative Elements */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
        <div className="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] bg-primary/10 rounded-full blur-[120px]" />
        <div className="absolute top-[40%] -right-[10%] w-[30%] h-[50%] bg-emerald-500/5 rounded-full blur-[100px]" />
      </div>

      {/* Sidebar */}
      <aside className="w-64 border-r border-white/10 glass z-50 flex flex-col hidden md:flex">
        <div className="p-6 border-b border-white/10 flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-primary glow-emerald flex items-center justify-center font-bold text-primary-foreground">
            H
          </div>
          <span className="text-xl font-bold tracking-tight">HimmiRouter</span>
        </div>

        <nav className="flex-1 p-4 flex flex-col gap-2">
          {navItems.map((item) => (
            <button
              key={item.href}
              onClick={() => {
                setActivePath(item.href)
                window.history.pushState({}, "", item.href)
                window.dispatchEvent(new PopStateEvent("popstate"))
              }}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                activePath === item.href
                  ? "bg-primary/20 text-primary border border-primary/20"
                  : "text-muted-foreground hover:bg-white/5 hover:text-foreground"
              }`}
            >
              <item.icon className="w-5 h-5" />
              <span className="font-medium">{item.name}</span>
            </button>
          ))}
        </nav>

        <div className="p-4 border-t border-white/10">
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-muted-foreground hover:bg-red-500/10 hover:text-red-500 transition-all"
          >
            <LogOut className="w-5 h-5" />
            <span className="font-medium">Sign Out</span>
          </button>
        </div>
      </aside>

      <div className="flex-1 flex flex-col relative z-10 w-full overflow-y-auto">
        <header className="sticky top-0 z-40 glass border-b border-white/10 px-6 py-4 flex items-center justify-between md:hidden">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary glow-emerald flex items-center justify-center font-bold text-primary-foreground">
              H
            </div>
          </div>
          <span className="text-xs text-muted-foreground uppercase tracking-widest font-semibold">Beta Access</span>
        </header>

        <main className="flex-1 p-6 md:p-10 max-w-7xl mx-auto w-full">
          <motion.div
            key={activePath}
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, ease: "easeOut" }}
          >
            {children}
          </motion.div>
        </main>

        <footer className="py-6 border-t border-white/5 text-center text-xs text-muted-foreground">
          &copy; 2026 HimmiRouter. Enterprise-Grade AI Ingress.
        </footer>
      </div>
    </div>
  )
}
