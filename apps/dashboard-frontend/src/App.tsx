import { useEffect, useState } from "react"
import { OpenAPI as ControlOpenAPI } from "./client-control"
import { OpenAPI as GatewayOpenAPI } from "./client-gateway"
import { AuthPage } from "./pages/auth"
import { DashboardPage } from "./pages/dashboard"

// Configure API endpoints
ControlOpenAPI.BASE = "http://localhost:8000"
GatewayOpenAPI.BASE = "http://localhost:4000"

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null)

  useEffect(() => {
    const session = localStorage.getItem("himmi_user")
    setIsAuthenticated(!!session)
  }, [])

  if (isAuthenticated === null) return null // Initial check

  return (
    <>
      {isAuthenticated ? (
        <DashboardPage />
      ) : (
        <AuthPage onSuccess={() => setIsAuthenticated(true)} />
      )}
    </>
  )
}

export default App
