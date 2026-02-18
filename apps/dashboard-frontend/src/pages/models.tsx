import type { ModelResponse } from "@/client-control"
import { DefaultService as ControlService } from "@/client-control"
import { DashboardLayout } from "@/components/layout"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { AnimatePresence, motion } from "framer-motion"
import { Box, Coins, Search, Zap } from "lucide-react"
import React, { useEffect, useState } from "react"

export const ModelsPage: React.FC = () => {
  const [models, setModels] = useState<ModelResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState("")

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

  // Filter models
  const filteredModels = models.filter(m => 
    m.name.toLowerCase().includes(search.toLowerCase()) || 
    m.slug.toLowerCase().includes(search.toLowerCase()) ||
    m.company?.name.toLowerCase().includes(search.toLowerCase())
  )

  // Group by Company
  const groupedModels = filteredModels.reduce((acc, model) => {
    const companyName = model.company?.name || "Other"
    if (!acc[companyName]) acc[companyName] = []
    acc[companyName].push(model)
    return acc
  }, {} as Record<string, typeof models>)

  return (
    <DashboardLayout>
      <div className="space-y-8 max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight mb-2 flex items-center gap-3">
              <Box className="w-8 h-8 text-primary" />
              Model Marketplace
            </h1>
            <p className="text-muted-foreground">
              Explore and compare {models.length} state-of-the-art models available via HimmiRouter.
            </p>
          </div>
          <div className="relative w-full md:w-96">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search models, providers, or slugs..." 
              className="pl-10 bg-white/5 border-white/10"
            />
          </div>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map(i => (
              <div key={i} className="h-56 rounded-2xl glass animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="space-y-12">
            {Object.keys(groupedModels).length === 0 ? (
               <div className="text-center py-20 opacity-50">
                 <p className="text-xl font-medium">No models found matching "{search}"</p>
               </div>
            ) : (
              Object.entries(groupedModels).sort().map(([company, companyModels]) => (
                <div key={company} className="space-y-6">
                  <div className="flex items-center gap-3 border-b border-white/10 pb-2">
                    <h2 className="text-xl font-bold tracking-tight">{company}</h2>
                    <Badge variant="outline" className="border-white/10 bg-white/5 text-muted-foreground">
                      {companyModels.length} models
                    </Badge>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    <AnimatePresence>
                      {companyModels.map((model) => (
                        <motion.div
                          key={model.id}
                          initial={{ opacity: 0, scale: 0.95 }}
                          animate={{ opacity: 1, scale: 1 }}
                          exit={{ opacity: 0, scale: 0.95 }}
                          layout
                        >
                          <Card className="h-full glass border border-white/10 hover:border-primary/50 transition-all duration-300 flex flex-col group">
                            <CardHeader className="pb-3">
                              <div className="flex justify-between items-start gap-4">
                                <CardTitle className="text-lg font-bold leading-tight">{model.name}</CardTitle>
                                {model.slug.includes("pro") || model.slug.includes("opus") ? (
                                  <Badge className="bg-gradient-to-r from-amber-500 to-orange-500 text-white border-0 text-[10px] px-2 py-0.5">PRO</Badge>
                                ) : (
                                  <Badge variant="secondary" className="bg-white/10 text-muted-foreground text-[10px] px-2 py-0.5">STD</Badge>
                                )}
                              </div>
                              <p className="text-xs font-mono text-muted-foreground break-all opacity-70 group-hover:opacity-100 transition-opacity">
                                {model.slug}
                              </p>
                            </CardHeader>
                            <CardContent className="flex-1 flex flex-col justify-end pt-0">
                              <div className="space-y-3 my-4 p-3 rounded-lg bg-black/20 border border-white/5">
                                <div className="flex items-center justify-between text-xs">
                                  <div className="flex items-center gap-2 text-muted-foreground">
                                    <Zap className="w-3 h-3" />
                                    <span>Input</span>
                                  </div>
                                  <div className="font-mono text-foreground">
                                    ${model.mappings?.[0]?.input_token_cost || 0} <span className="text-muted-foreground">/ 1M</span>
                                  </div>
                                </div>
                                <div className="flex items-center justify-between text-xs">
                                  <div className="flex items-center gap-2 text-muted-foreground">
                                    <Coins className="w-3 h-3" />
                                    <span>Output</span>
                                  </div>
                                  <div className="font-mono text-emerald-400">
                                    ${model.mappings?.[0]?.output_token_cost || 0} <span className="text-muted-foreground">/ 1M</span>
                                  </div>
                                </div>
                              </div>
            
                              <button 
                                onClick={() => {
                                  window.history.pushState({}, "", `/playground?model=${model.slug}`)
                                  window.dispatchEvent(new PopStateEvent("popstate"))
                                }}
                                className="w-full py-2.5 rounded-xl bg-primary/10 text-primary border border-primary/20 text-sm font-semibold hover:bg-primary hover:text-primary-foreground hover:glow-emerald transition-all flex items-center justify-center gap-2 group-hover:translate-y-0 translate-y-2 opacity-0 group-hover:opacity-100 duration-300"
                              >
                                Play in Workbench
                              </button>
                            </CardContent>
                          </Card>
                        </motion.div>
                      ))}
                    </AnimatePresence>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
