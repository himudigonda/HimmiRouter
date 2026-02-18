import { AuthService } from "@/lib/auth"
import { motion } from "framer-motion"
import { ChevronLeft, ChevronRight, LayoutDashboard, Library, LogOut, MessageSquare, Settings } from "lucide-react"
import React from "react"

interface LayoutProps {
  children: React.ReactNode
}

export const DashboardLayout: React.FC<LayoutProps> = ({ children }) => {
  const [activePath, setActivePath] = React.useState(
    window.location.pathname === "/" ? "/dashboard" : window.location.pathname
  )
  const [isCollapsed, setIsCollapsed] = React.useState(false)

  const navItems = [
    { name: "Dashboard", icon: LayoutDashboard, href: "/dashboard" },
    { name: "Playground", icon: MessageSquare, href: "/playground" },
    { name: "Model Library", icon: Library, href: "/models" },
    { name: "Settings", icon: Settings, href: "/settings" },
  ]

  React.useEffect(() => {
    const handleLocationChange = () => {
      const path = window.location.pathname === "/" ? "/dashboard" : window.location.pathname
      setActivePath(path)
    }
    window.addEventListener("popstate", handleLocationChange)
    return () => window.removeEventListener("popstate", handleLocationChange)
  }, [])

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
      <motion.aside 
        initial={false}
        animate={{ width: isCollapsed ? 80 : 256 }}
        className="border-r border-white/10 glass z-50 flex flex-col hidden md:flex sticky top-0 h-screen transition-all duration-300 ease-in-out"
      >
        <div className={`p-6 border-b border-white/10 flex items-center ${isCollapsed ? 'justify-center' : 'justify-between'}`}>
          <div className="flex items-center gap-3 overflow-hidden">
             <div className="w-8 h-8 rounded-lg bg-primary glow-emerald flex items-center justify-center font-bold text-primary-foreground shrink-0">
               H
             </div>
             {!isCollapsed && (
                <motion.span 
                  initial={{ opacity: 0 }} 
                  animate={{ opacity: 1 }} 
                  className="text-xl font-bold tracking-tight whitespace-nowrap"
                >
                  HimmiRouter
                </motion.span>
             )}
          </div>
          {!isCollapsed && (
             <button onClick={() => setIsCollapsed(true)} className="text-muted-foreground hover:text-foreground">
                <ChevronLeft className="w-4 h-4" />
             </button>
          )}
        </div>

        <nav className="flex-1 p-4 flex flex-col gap-2 overflow-y-auto overflow-x-hidden">
          {navItems.map((item) => (
            <button
              key={item.href}
              onClick={() => {
                setActivePath(item.href)
                window.history.pushState({}, "", item.href)
                window.dispatchEvent(new PopStateEvent("popstate"))
              }}
              title={isCollapsed ? item.name : undefined}
              className={`flex items-center gap-3 px-3 py-3 rounded-xl transition-all ${
                activePath === item.href
                  ? "bg-primary/20 text-primary border border-primary/20"
                  : "text-muted-foreground hover:bg-white/5 hover:text-foreground"
              } ${isCollapsed ? 'justify-center' : ''}`}
            >
              <item.icon className="w-5 h-5 shrink-0" />
              {!isCollapsed && (
                <motion.span 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="font-medium whitespace-nowrap"
                >
                  {item.name}
                </motion.span>
              )}
            </button>
          ))}
        </nav>

        <div className="p-4 border-t border-white/10 flex flex-col items-center">
            {isCollapsed ? (
                <button 
                  onClick={() => setIsCollapsed(false)} 
                  className="p-2 rounded-lg hover:bg-white/5 text-muted-foreground mb-4"
                  title="Expand Sidebar"
                >
                    <ChevronRight className="w-5 h-5" />
                </button>
            ) : null}
            
          <button
            onClick={handleLogout}
            title={isCollapsed ? "Sign Out" : undefined}
            className={`w-full flex items-center gap-3 px-3 py-3 rounded-xl text-muted-foreground hover:bg-red-500/10 hover:text-red-500 transition-all ${isCollapsed ? 'justify-center' : ''}`}
          >
            <LogOut className="w-5 h-5 shrink-0" />
            {!isCollapsed && <span className="font-medium whitespace-nowrap">Sign Out</span>}
          </button>
        </div>
      </motion.aside>

      <div className="flex-1 flex flex-col relative z-10 w-full overflow-hidden h-screen">
        <header className="sticky top-0 z-40 glass border-b border-white/10 px-6 py-4 flex items-center justify-between md:hidden">
            {/* Mobile Header */}
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary glow-emerald flex items-center justify-center font-bold text-primary-foreground">
              H
            </div>
            <span className="font-bold">HimmiRouter</span>
          </div>
          <span className="text-xs text-muted-foreground uppercase tracking-widest font-semibold">Beta Access</span>
        </header>

        <main className="flex-1 overflow-y-auto p-6 md:p-10 w-full scrollbar-thin scrollbar-thumb-white/10 hover:scrollbar-thumb-white/20">
          <motion.div
            key={activePath}
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, ease: "easeOut" }}
            className="max-w-7xl mx-auto w-full pb-20"
          >
            {children}
          </motion.div>
        </main>
      </div>
    </div>
  )
}
