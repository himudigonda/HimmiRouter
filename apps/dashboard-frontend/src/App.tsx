import { useEffect, useState } from "react"
import { OpenAPI as ControlOpenAPI } from "./client-control"
import { OpenAPI as GatewayOpenAPI } from "./client-gateway"
import { AuthPage } from "./pages/auth"
import { DashboardPage } from "./pages/dashboard"

// Configure API endpoints
ControlOpenAPI.BASE = "http://localhost:8000"
GatewayOpenAPI.BASE = "http://localhost:4000"

import { ModelsPage } from "./pages/models"
import { PlaygroundPage } from "./pages/playground"

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null)
  const [currentPath, setCurrentPath] = useState(window.location.pathname)

  useEffect(() => {
    const session = localStorage.getItem("himmi_user")
    setIsAuthenticated(!!session)

    const handleLocationChange = () => {
      setCurrentPath(window.location.pathname)
    }

    window.addEventListener("popstate", handleLocationChange)
    return () => window.removeEventListener("popstate", handleLocationChange)
  }, [])

  if (isAuthenticated === null) return null

  if (!isAuthenticated) {
    return <AuthPage onSuccess={() => setIsAuthenticated(true)} />
  }

  // Simple Router
  const renderPage = () => {
    switch (currentPath) {
      case "/playground":
        return <PlaygroundPage />
      case "/models":
        return <ModelsPage />
      default:
        return <DashboardPage />
    }
  }

  return renderPage()
}

export default App
