import type { ModelResponse } from "@/client-control"
import { DefaultService as ControlService } from "@/client-control"
import { DashboardLayout } from "@/components/layout"
import { AnimatePresence, motion } from "framer-motion"
import "highlight.js/styles/atom-one-dark.css"
import { Activity, AlertCircle, Bot, Cpu, Key, Send, Sparkles, Trash2, User } from "lucide-react"
import React, { useEffect, useRef, useState } from "react"
import ReactMarkdown from "react-markdown"
import rehypeHighlight from "rehype-highlight"

// Helper to clean up markdown (e.g. sometimes spacing is off)
const preprocessMarkdown = (markdown: string) => {
  // Ensure code blocks have newlines before/after
  return markdown
}

export const PlaygroundPage: React.FC = () => {
  const [models, setModels] = useState<ModelResponse[]>([])
  const [filteredModels, setFilteredModels] = useState<ModelResponse[]>([])
  const [selectedProvider, setSelectedProvider] = useState("All")
  const [selectedModel, setSelectedModel] = useState("")
  const [selectedKey, setSelectedKey] = useState("")
  const [messages, setMessages] = useState<any[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [credits, setCredits] = useState<number | null>(null)
  
  // Stats
  const [sessionUsage, setSessionUsage] = useState({ requests: 0, tokens: 0, cost: 0 })
  
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const fetchData = async () => {
      const user = JSON.parse(localStorage.getItem("himmi_user") || "{}")
      if (!user.id) return
      
      try {
        const [modelsData, userData] = await Promise.all([
          ControlService.listModelsModelsGet(),
          ControlService.getUserStatusUsersUserIdGet(user.id)
        ])
        setModels(modelsData)
        setFilteredModels(modelsData)
        setCredits(userData.credits)
        
        // Check for model in URL query params
        const params = new URLSearchParams(window.location.search)
        const modelParam = params.get("model")

        if (modelParam && modelsData.some((m: any) => m.slug === modelParam)) {
          setSelectedModel(modelParam)
          // Auto-select provider if possible
          const m = modelsData.find((m: any) => m.slug === modelParam)
          if (m?.company?.name) setSelectedProvider(m.company.name)
        } else if (modelsData.length > 0) {
          setSelectedModel(modelsData[0].slug)
        }
      } catch (err) {
        console.error("Failed to fetch playground data", err)
      }
    }
    fetchData()
  }, [])

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  // Filter models when provider changes
  useEffect(() => {
    if (selectedProvider === "All") {
      setFilteredModels(models)
    } else {
      setFilteredModels(models.filter(m => m.company?.name === selectedProvider))
    }
    // Reset selected model if it's no longer in the list
    /* if (!filteredModels.find(m => m.slug === selectedModel) && filteredModels.length > 0) {
       setSelectedModel(filteredModels[0].slug)
    } */
  }, [selectedProvider, models])
  
  // Extract unique providers
  const providers = ["All", ...Array.from(new Set(models.map(m => m.company?.name).filter(Boolean)))].sort()

  const handleSend = async () => {
    if (!input.trim() || !selectedModel || isLoading) return
    if (!selectedKey) {
      alert("Please enter a valid API Key. You can generate one in the Dashboard.")
      return
    }

    if (!selectedKey.trim().startsWith("sk-or-v1-")) {
        alert("Invalid API Key Format.\n\nYou entered a Provider Key (e.g. Google/OpenAI) or a malformed key.\n\nPlease use a HimmiRouter API Key generated in the Dashboard. It must start with 'sk-or-v1-'.")
        return
    }

    const userMessage = { role: "user", content: input }
    const completedMessages = messages.filter(m => m.content !== "")
    const apiMessages = [...completedMessages, userMessage]
    
    setMessages(prev => [...prev.filter(m => m.content !== ""), userMessage, { role: "assistant", content: "" }])
    setInput("")
    setIsLoading(true)

    // Calculate estimated cost for this request (approximate)
    const currentModel = models.find(m => m.slug === selectedModel)
    const inputCostPer1M = currentModel?.mappings?.[0]?.input_token_cost || 0
    const outputCostPer1M = currentModel?.mappings?.[0]?.output_token_cost || 0
    
    let currentResponseTokens = 0

    try {
      const response = await fetch("http://localhost:4000/v1/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${selectedKey.trim()}`,
        },
        body: JSON.stringify({
          model: selectedModel,
          messages: apiMessages,
          stream: true
        })
      })

      if (!response.ok) {
        const errText = await response.text()
        let errMsg = errText
        try {
            const jsonErr = JSON.parse(errText)
            errMsg = jsonErr.detail || jsonErr.error || errText
        } catch {}
        
        throw new Error(`HTTP ${response.status}: ${errMsg} ${response.status === 401 ? "(Check your API Key)" : ""}`)
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      let assistantContent = ""
      
      while (true) {
        const { done, value } = await reader!.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split("\n")
        
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const dataStr = line.slice(6).trim()
            if (dataStr === "[DONE]") break
            try {
              const data = JSON.parse(dataStr)
              const delta = data.choices?.[0]?.delta?.content || ""
              assistantContent += delta
              
              if (delta) currentResponseTokens += 1 // Crude approximation
              
              setMessages(prev => {
                const updated = [...prev]
                updated[updated.length - 1] = { role: "assistant", content: assistantContent }
                return updated
              })
              
              // If usage is returned in the stream (LiteLLM feature)
              if (data.usage) {
                  const u = data.usage
                  const cost = ((u.prompt_tokens * inputCostPer1M) + (u.completion_tokens * outputCostPer1M)) / 1_000_000
                  setSessionUsage(prev => ({
                      requests: prev.requests, 
                      tokens: prev.tokens + u.completion_tokens, // simplistic add
                      cost: prev.cost + cost
                  }))
              }
              
            } catch (e) {
              // Ignore
            }
          }
        }
      }
      
      // Update session stats manually if usage wasn't streamed
      setSessionUsage(prev => ({ 
          requests: prev.requests + 1,
          tokens: prev.tokens + (currentResponseTokens), // rough est
          cost: prev.cost // only update accurate cost if backend sends it
      }))
      
      // Refresh credits
      const user = JSON.parse(localStorage.getItem("himmi_user") || "{}")
      if (user.id) {
        const updatedUser = await ControlService.getUserStatusUsersUserIdGet(user.id)
        setCredits(updatedUser.credits)
      }

    } catch (err: any) {
      console.error("Stream error", err)
      setMessages(prev => {
        const updated = [...prev]
        updated[updated.length - 1] = { role: "assistant", content: `Error: ${err.message || "Failed to get response."}` }
        return updated
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <DashboardLayout>
      <div className="flex flex-col h-[calc(100vh-140px)] gap-6">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight mb-2 flex items-center gap-3">
              <Sparkles className="text-primary w-8 h-8" />
              AI Playground
            </h1>
            <p className="text-muted-foreground text-sm">Experience ultra-low latency routing to 2026-era models.</p>
          </div>
          <div className="flex items-center gap-3">
             <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-white/10 text-xs text-muted-foreground mr-4">
               <Activity className="w-3 h-3 text-emerald-500" />
               <span>Session: {sessionUsage.requests} reqs</span>
               <span className="w-px h-3 bg-white/10 mx-1" />
               <span>≈ ${sessionUsage.cost.toFixed(4)}</span>
             </div>
             
             <div className="flex items-center gap-3 glass border border-white/10 px-4 py-2 rounded-2xl">
              <span className="text-xs text-muted-foreground uppercase font-semibold">Balance</span>
              <span className="text-lg font-bold text-primary">${credits?.toFixed(4) ?? "---"}</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-1 overflow-hidden">
          {/* Settings Sidebar */}
          <div className="space-y-6 lg:border-r lg:border-white/10 lg:pr-6 overflow-y-auto">
            
            <div className="space-y-4">
               <label className="text-sm font-semibold flex items-center gap-2">
                <Bot className="w-4 h-4 text-muted-foreground" /> Provider
              </label>
              <select 
                value={selectedProvider}
                onChange={(e) => setSelectedProvider(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2 focus:ring-2 focus:ring-primary outline-none transition-all text-sm"
              >
                {providers.map(p => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>

            <div className="space-y-4">
              <label className="text-sm font-semibold flex items-center gap-2">
                <Cpu className="w-4 h-4 text-primary" /> Model
              </label>
              <select 
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2 focus:ring-2 focus:ring-primary outline-none transition-all text-sm"
              >
                {filteredModels.map(m => (
                    <option key={m.id} value={m.slug}>
                        {m.name} (${m.mappings?.[0]?.input_token_cost}/1M)
                    </option>
                ))}
              </select>
              <p className="text-[10px] text-muted-foreground">
                Pricing is per 1M input tokens.
              </p>
            </div>

            <div className="space-y-4">
              <label className="text-sm font-semibold flex items-center gap-2">
                <Key className="w-4 h-4 text-emerald-500" /> API Key
              </label>
              <input 
                type="password"
                placeholder="sk-or-v1-..."
                value={selectedKey}
                onChange={(e) => setSelectedKey(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2 focus:ring-2 focus:ring-emerald-500 outline-none transition-all text-sm font-mono"
              />
              <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-[11px] text-red-200 leading-relaxed flex gap-2">
                <AlertCircle className="w-4 h-4 shrink-0 translate-y-0.5 text-red-400" />
                <p>
                  <span className="font-bold text-red-400">DO NOT</span> use Google/OpenAI keys here. You must generate a <span className="font-bold text-emerald-400">HimmiRouter Key</span> in the Dashboard.
                </p>
              </div>
            </div>

            <button 
              onClick={() => setMessages([])}
              className="w-full flex items-center justify-center gap-2 py-2 rounded-xl text-muted-foreground hover:bg-white/5 transition-all text-sm"
            >
              <Trash2 className="w-4 h-4" /> Clear Chat
            </button>
            
            <div className="mt-8 pt-6 border-t border-white/10">
                <h4 className="text-xs font-bold uppercase tracking-widest text-muted-foreground mb-3">SDK Usage</h4>
                <div className="bg-black/40 rounded-lg p-3 border border-white/5 font-mono text-[10px] text-muted-foreground overflow-x-auto">
                    <span className="text-purple-400">import</span> openai<br/>
                    <br/>
                    client = openai.OpenAI(<br/>
                    &nbsp;&nbsp;base_url=<span className="text-green-400">"http://localhost:4000/v1"</span>,<br/>
                    &nbsp;&nbsp;api_key=<span className="text-green-400">"{selectedKey || 'YOUR_KEY'}"</span><br/>
                    )<br/>
                    <br/>
                    check = client.models.list()
                </div>
            </div>
          </div>

          {/* Chat Interface */}
          <div className="lg:col-span-3 flex flex-col glass rounded-2xl border border-white/10 overflow-hidden relative">
            <div 
              ref={scrollRef}
              className="flex-1 overflow-y-auto p-6 space-y-6"
            >
              {messages.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-center space-y-4 opacity-40">
                  <div className="p-4 rounded-full bg-primary/10">
                    <Bot className="w-12 h-12" />
                  </div>
                  <div>
                    <p className="text-xl font-bold">Welcome to the Workbench</p>
                    <p className="text-sm">Select a model and start a conversation.</p>
                  </div>
                </div>
              ) : (
                <AnimatePresence>
                  {messages.map((msg, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={`flex gap-4 ${msg.role === "user" ? "flex-row-reverse" : ""}`}
                    >
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                        msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-white/10 text-primary"
                      }`}>
                        {msg.role === "user" ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
                      </div>
                      <div className={`px-4 py-2 rounded-2xl max-w-[85%] overflow-hidden ${
                        msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-white/5 border border-white/10"
                      }`}>
                        {msg.role === "user" ? (
                           <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                        ) : (
                           <div className="text-sm prose prose-invert prose-p:leading-relaxed prose-pre:bg-black/50 prose-pre:border prose-pre:border-white/10 max-w-none break-words dark:prose-invert">
                               <ReactMarkdown rehypePlugins={[rehypeHighlight]}>
                                   {preprocessMarkdown(msg.content || (isLoading && i === messages.length - 1 ? "..." : ""))}
                               </ReactMarkdown>
                           </div>
                        )}
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
              )}
            </div>

            <div className="p-6 border-t border-white/10 bg-black/20 backdrop-blur-xl">
              <div className="relative">
                <textarea 
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && (e.preventDefault(), handleSend())}
                  placeholder="Type your message..."
                  className="w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-4 pr-16 focus:ring-2 focus:ring-primary outline-none transition-all resize-none h-20"
                />
                <button 
                  onClick={handleSend}
                  disabled={isLoading || !input.trim()}
                  className="absolute right-4 top-1/2 -translate-y-1/2 p-2 rounded-xl bg-primary text-primary-foreground hover:glow-emerald transition-all disabled:opacity-50 disabled:hover:glow-none"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
              <p className="text-[10px] text-center mt-3 text-muted-foreground uppercase tracking-widest">
                Real-time usage tracking enabled • Each request consumes credits
              </p>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
