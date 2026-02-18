import { DefaultService as ControlService } from "@/client-control"
import { DashboardLayout } from "@/components/layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Coins, Cpu, Zap } from "lucide-react"
import React, { useEffect, useState } from "react"

export const ModelsPage: React.FC = () => {
  const [models, setModels] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchModels = async () => {
      try {
        const data = await ControlService.listModelsModelsGet()
        setModels(data)
      } catch (err) {
        console.error("Failed to fetch models", err)
      } finally {
        setLoading(false)
      }
    }
    fetchModels()
  }, [])

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">Model Library</h1>
          <p className="text-muted-foreground"> Explore available 2026-era models and their optimized pricing.</p>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-48 rounded-2xl glass animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {models.map((model) => (
              <Card key={model.id} className="group hover:border-primary/50 transition-all duration-300">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-xl font-bold">{model.name}</CardTitle>
                  <div className="p-2 rounded-lg bg-primary/10 text-primary">
                    <Cpu className="w-5 h-5" />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-xs font-mono text-muted-foreground mb-4">
                    {model.slug}
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-2 text-muted-foreground">
                        <Zap className="w-4 h-4" />
                        <span>Input / 1M</span>
                      </div>
                      <div className="font-semibold text-foreground">
                        {model.mappings?.[0]?.input_token_cost || 0}c
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-2 text-muted-foreground">
                        <Coins className="w-4 h-4" />
                        <span>Output / 1M</span>
                      </div>
                      <div className="font-semibold text-emerald-500">
                        {model.mappings?.[0]?.output_token_cost || 0}c
                      </div>
                    </div>
                  </div>

                  <button 
                    onClick={() => {
                      window.history.pushState({}, "", "/playground")
                      window.dispatchEvent(new PopStateEvent("popstate"))
                    }}
                    className="w-full mt-6 py-2 rounded-xl bg-white/5 border border-white/10 text-sm font-medium hover:bg-primary hover:text-primary-foreground hover:border-primary transition-all"
                  >
                    Try in Playground
                  </button>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
