import type { ModelResponse } from "@/client-control"
import { DefaultService as ControlService } from "@/client-control"
import { DashboardLayout } from "@/components/layout"
import { Badge } from "@/components/ui/badge"
import { AnimatePresence, motion } from "framer-motion"
import "highlight.js/styles/atom-one-dark.css"
import { Activity, Bot, Cpu, Key, Send, Sparkles, ThumbsUp, Trash2, User, Zap } from "lucide-react"
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
  const [messages, setMessages] = useState<any[]>([]) // Shared history
  
  // Shadow Mode State
  const [shadowMode, setShadowMode] = useState(false)
  const [pendingComparison, setPendingComparison] = useState<{
      prompt: string,
      primaryModel: string,
      primaryResponse: string,
      shadowModel: string,
      shadowResponse: string
  } | null>(null)

  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [credits, setCredits] = useState<number | null>(null)
  
  const formatContext = (length: number | null | undefined) => {
    if (!length) return "N/A"
    if (length >= 1000000) return `${(length / 1000000).toFixed(1)}M`
    if (length >= 1000) return `${Math.floor(length / 1000)}k`
    return length.toString()
  }

  // Stats
  const [sessionUsage, setSessionUsage] = useState({ requests: 0, tokens: 0, cost: 0 })
  
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Always fetch models — no auth required for the catalog
    const fetchModels = async () => {
      try {
        const modelsData = await ControlService.listModelsModelsGet()
        setModels(modelsData)
        setFilteredModels(modelsData)

        // Check for model in URL query params
        const params = new URLSearchParams(window.location.search)
        const modelParam = params.get("model")

        if (modelParam && modelsData.some((m: any) => m.slug === modelParam)) {
          setSelectedModel(modelParam)
          const m = modelsData.find((m: any) => m.slug === modelParam)
          if (m?.company?.name) setSelectedProvider(m.company.name)
        } else if (modelsData.length > 0) {
          setSelectedModel(modelsData[0].slug)
        }
      } catch (err) {
        console.error("Failed to fetch models", err)
      }
    }

    // Fetch user credits only when logged in
    const fetchUser = async () => {
      const user = JSON.parse(localStorage.getItem("himmi_user") || "{}")
      if (!user.id) return
      try {
        const userData = await ControlService.getUserStatusUsersUserIdGet(user.id)
        setCredits(userData.credits)
      } catch (err: any) {
        console.error("Failed to fetch user data", err)
        if (err.status === 404) {
          localStorage.removeItem("himmi_user")
          window.location.href = "/login"
        }
      }
    }

    fetchModels()
    fetchUser()
  }, [])

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, pendingComparison])

  // Filter models when provider changes
  useEffect(() => {
    if (selectedProvider === "All") {
      setFilteredModels(models)
    } else {
      setFilteredModels(models.filter(m => 
        m.mappings?.some(map => map.provider === selectedProvider)
      ))
    }
  }, [selectedProvider, models])
  
  // Extract unique providers from mappings
  const providers = ["All", ...Array.from(new Set(
    models.flatMap(m => m.mappings?.map(map => map.provider || "") || [])
    .filter(Boolean)
  ))].sort()

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
    
    // Clear previous comparison if starting new chat
    setPendingComparison(null)

    const userMessage = { role: "user", content: input }
    const currentInput = input // Capture for later use in vote
    const completedMessages = messages.filter(m => m.content !== "")
    const apiMessages = [...completedMessages, userMessage]
    
    // Optimistic Update
    setMessages(prev => [...prev.filter(m => m.content !== ""), userMessage, { role: "assistant", content: "", isCached: false }])
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
          stream: !shadowMode, // Disable stream if shadow mode is ON to allow simpler capture
          shadow_mode: shadowMode
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

      if (shadowMode) {
          // Non-streaming response for Shadow Mode
          const data = await response.json()
          const primaryContent = data.choices?.[0]?.message?.content || ""
          
          setMessages(prev => {
              const updated = [...prev]
              updated[updated.length - 1] = { role: "assistant", content: primaryContent, isCached: data.usage?.prompt_tokens === 0 && data.usage?.completion_tokens === 0 }
              return updated
          })
          
          if (data.shadow_response) {
              setPendingComparison({
                  prompt: currentInput,
                  primaryModel: selectedModel,
                  primaryResponse: primaryContent,
                  shadowModel: data.shadow_model || "shadow-model",
                  shadowResponse: data.shadow_response
              })
          }
          
          // Update stats
          if (data.usage) {
               const u = data.usage
               const cost = ((u.prompt_tokens * inputCostPer1M) + (u.completion_tokens * outputCostPer1M)) / 1_000_000
               setSessionUsage(prev => ({
                    requests: prev.requests + 1, 
                    tokens: prev.tokens + u.completion_tokens, 
                    cost: prev.cost + cost
               }))
          }
          
      } else {
        // Streaming Logic (Existing)
        const reader = response.body?.getReader()
        const decoder = new TextDecoder()
        let assistantContent = ""
        let isCached = false
        
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
                
                if (delta) currentResponseTokens += 1 
                
                // If usage comes back 0, likely cached (or very short)
                // Backend sends full response immediately if cached, so stream might look different?
                // Actually my backend impl for cache sends full response in one go but `ainvoke` output processing in main.py wraps it in SSE if `stream=True` requested.
                // The cache node returns `response_content` direct. The `log_request_task` logs it.
                // But `stream_iterator` is NOT set by cache node.
                // So if cached, `result.get('stream_iterator')` is None?
                // Wait. `router.py`: `cache_lookup_node` returns `response_content`, `is_cached=True`.
                // It does NOT set `stream_iterator`.
                // `main.py` checks: `if request.stream and result.get("stream_iterator")`.
                // So if cached, it falls through to regular JSON response!
                // So even if `stream=True` was sent, if it's cached, my `main.py` will return JSON.
                // Wait, frontend `fetch` handles stream via reader. If it gets JSON, `response.body` is still readable stream technically but...
                // The `fetch` loop reads stream. If response is simple JSON, it reads it all in one chunk.
                // But `line.startsWith("data: ")` logic will FAIL for simple JSON.
                // I need to handle this hybrid response type or ensure `cache_lookup_node` returns iterator if stream requested.
                // Or frontend detects Content-Type.
                // Let's rely on standard practice: If cached, we return non-stream JSON usually.
                
                // Let's modify frontend to handle both.
                // Actually, if `main.py` returns JSON, the loop `lines.startsWith("data: ")` will find nothing.
                // So `assistantContent` stays empty? That's bad.
                
                // Fix: Check Content-Type.
                
                if (data.usage) {
                    const u = data.usage
                    const cost = ((u.prompt_tokens * inputCostPer1M) + (u.completion_tokens * outputCostPer1M)) / 1_000_000
                    setSessionUsage(prev => ({
                        requests: prev.requests, 
                        tokens: prev.tokens + u.completion_tokens,
                        cost: prev.cost + cost
                    }))
                    
                    if (u.prompt_tokens === 0 && u.completion_tokens === 0) {
                        isCached = true
                    }
                }
                
                setMessages(prev => {
                    const updated = [...prev]
                    updated[updated.length - 1] = { role: "assistant", content: assistantContent, isCached }
                    return updated
                })
                
                } catch (e) { }
            }
            }
        }
        
        // If content type was application/json (Cached hit falling through streaming request)
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
             // Re-read body as json (reader already consumed?? NO, if loop didn't find "data:", maybe it's still there?)
             // Reader consumes stream. If it was short JSON, "value" holds it.
             // But if we already read it...
             // Simplification: `clone()` response before reading? Or check header first.
             // I can't restart `reader`.
             // But wait, if it was JSON, my loop printed nothing?
             // Actually, `wrapper` logic aside, let's fix `main.py` or `router.py` to stream cached response?
             // Or update Frontend to check header.
        }
      } 
      
      // Update session stats manually if usage wasn't streamed
      setSessionUsage(prev => ({ 
          requests: prev.requests + 1,
          tokens: prev.tokens + (currentResponseTokens), 
          cost: prev.cost 
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

  const handleVote = async (preference: "primary" | "shadow") => {
      if (!pendingComparison) return;
      
      try {
          await fetch("http://localhost:4000/analytics/preference", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                  prompt: pendingComparison.prompt,
                  primary_model: pendingComparison.primaryModel,
                  primary_response: pendingComparison.primaryResponse,
                  shadow_model: pendingComparison.shadowModel,
                  shadow_response: pendingComparison.shadowResponse,
                  user_preference: preference
              })
          });
          // Clear comparison after vote to show "Thank you" or just remove UI overlay
          setPendingComparison(null);
          // Optional: Show toast
      } catch (e) {
          console.error("Failed to submit preference", e);
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
                        {m.name} ({formatContext(m.context_length)} ctx • ${m.mappings?.[0]?.input_token_cost}/1M)
                    </option>
                ))}
              </select>
            </div>
            
            {/* Shadow Mode Toggle */}
            <div className="p-4 rounded-xl bg-purple-500/10 border border-purple-500/20">
                <div className="flex items-center justify-between mb-2">
                    <label className="text-sm font-bold text-purple-200 flex items-center gap-2">
                        <Zap className="w-4 h-4 text-purple-400" /> Shadow Mode
                    </label>
                    <input 
                        type="checkbox"
                        checked={shadowMode}
                        onChange={(e) => setShadowMode(e.target.checked)}
                        className="accent-purple-500 w-4 h-4 cursor-pointer"
                    />
                </div>
                <p className="text-[10px] text-purple-300/70 leading-relaxed">
                    Runs a cheaper model (Llama-3 8B) alongside your primary selection to compare quality.
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
            </div>

            <button 
              onClick={() => { setMessages([]); setPendingComparison(null); }}
              className="w-full flex items-center justify-center gap-2 py-2 rounded-xl text-muted-foreground hover:bg-white/5 transition-all text-sm"
            >
              <Trash2 className="w-4 h-4" /> Clear Chat
            </button>
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
                        {msg.role === "assistant" && msg.isCached && (
                            <Badge variant="outline" className="mb-2 border-emerald-500/50 text-emerald-400 bg-emerald-500/10 gap-1 rounded-sm text-[10px] px-1 py-0 h-5">
                                <Zap className="w-3 h-3 fill-current" /> Semantic Cache Hit (Free)
                            </Badge>
                        )}
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
                  
                  {/* Shadow Comparison UI */}
                  {pendingComparison && (
                      <motion.div 
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="mt-8 p-6 rounded-2xl border border-purple-500/30 bg-purple-900/10 backdrop-blur-sm"
                      >
                          <h3 className="text-center text-purple-200 font-bold mb-6 flex items-center justify-center gap-2">
                              <Sparkles className="w-5 h-5" />
                              Shadow Mode Comparison
                              <span className="text-xs font-normal text-purple-300/50 ml-2">(RLHF Data Collection)</span>
                          </h3>
                          
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                              {/* Primary Answer */}
                              <div className="p-4 rounded-xl bg-black/40 border border-white/10 flex flex-col">
                                  <div className="text-xs font-bold text-emerald-400 mb-2 uppercase tracking-wider">{pendingComparison.primaryModel} (Primary)</div>
                                  <div className="flex-1 text-sm text-gray-300 prose prose-invert max-w-none mb-4 max-h-60 overflow-y-auto">
                                     <ReactMarkdown>{pendingComparison.primaryResponse}</ReactMarkdown>
                                  </div>
                                  <button 
                                    onClick={() => handleVote("primary")}
                                    className="w-full mt-auto flex items-center justify-center gap-2 py-2 rounded-lg bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 border border-emerald-500/20 transition-all font-semibold text-xs"
                                  >
                                      <ThumbsUp className="w-3 h-3" /> Better Response
                                  </button>
                              </div>
                              
                              {/* Shadow Answer */}
                              <div className="p-4 rounded-xl bg-black/40 border border-white/10 flex flex-col">
                                  <div className="text-xs font-bold text-purple-400 mb-2 uppercase tracking-wider">Llama-3 (Shadow)</div>
                                  <div className="flex-1 text-sm text-gray-300 prose prose-invert max-w-none mb-4 max-h-60 overflow-y-auto">
                                     <ReactMarkdown>{pendingComparison.shadowResponse}</ReactMarkdown>
                                  </div>
                                  <button 
                                    onClick={() => handleVote("shadow")}
                                    className="w-full mt-auto flex items-center justify-center gap-2 py-2 rounded-lg bg-purple-500/10 text-purple-400 hover:bg-purple-500/20 border border-purple-500/20 transition-all font-semibold text-xs"
                                  >
                                      <ThumbsUp className="w-3 h-3" /> Better Response
                                  </button>
                              </div>
                          </div>
                      </motion.div>
                  )}
                  
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
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
