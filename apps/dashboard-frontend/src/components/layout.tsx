import { motion } from "framer-motion"
import React from "react"

interface LayoutProps {
  children: React.ReactNode
}

export const DashboardLayout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-background text-foreground relative overflow-hidden flex flex-col font-sans">
      {/* Background Decorative Elements */}
      <div className="absolute top-0 left-0 w-full h-full pointer-events-none overflow-hidden z-0">
        <div className="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] bg-primary/10 rounded-full blur-[120px]" />
        <div className="absolute top-[40%] -right-[10%] w-[30%] h-[50%] bg-emerald-500/5 rounded-full blur-[100px]" />
      </div>

      <header className="sticky top-0 z-50 glass border-b border-white/10 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-primary glow-emerald flex items-center justify-center font-bold text-primary-foreground">
            H
          </div>
          <span className="text-xl font-bold tracking-tight">HimmiRouter</span>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-xs text-muted-foreground uppercase tracking-widest font-semibold">Beta Access</span>
        </div>
      </header>

      <main className="flex-1 relative z-10 p-6 md:p-10 max-w-7xl mx-auto w-full">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: "easeOut" }}
        >
          {children}
        </motion.div>
      </main>

      <footer className="py-6 border-t border-white/5 text-center text-xs text-muted-foreground relative z-10">
        &copy; 2026 HimmiRouter. Enterprise-Grade AI Ingress.
      </footer>
    </div>
  )
}
