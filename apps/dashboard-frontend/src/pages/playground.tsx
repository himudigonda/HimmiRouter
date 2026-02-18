import { DefaultService as ControlService } from "@/client-control"
import { DashboardLayout } from "@/components/layout"
import { AnimatePresence, motion } from "framer-motion"
import { Bot, Cpu, Key, Send, Sparkles, Trash2, User } from "lucide-react"
import React, { useEffect, useRef, useState } from "react"

export const PlaygroundPage: React.FC = () => {
  const [models, setModels] = useState<any[]>([])
  const [selectedModel, setSelectedModel] = useState("")
  const [selectedKey, setSelectedKey] = useState("")
  const [messages, setMessages] = useState<any[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [credits, setCredits] = useState<number | null>(null)
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
        setCredits(userData.credits)
        
        // Check for model in URL query params
        const params = new URLSearchParams(window.location.search)
        const modelParam = params.get("model")

        if (modelParam && modelsData.some((m: any) => m.slug === modelParam)) {
          setSelectedModel(modelParam)
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

  const handleSend = async () => {
    if (!input.trim() || !selectedModel || isLoading) return

    const userMessage = { role: "user", content: input }
    // Only include completed messages (filter out empty assistant placeholders)
    const completedMessages = messages.filter(m => m.content !== "")
    const apiMessages = [...completedMessages, userMessage]
    
    // Update display state: add user message + empty placeholder for streaming
    setMessages(prev => [...prev.filter(m => m.content !== ""), userMessage, { role: "assistant", content: "" }])
    setInput("")
    setIsLoading(true)

    try {
      const response = await fetch("http://localhost:4000/v1/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${selectedKey}`,
        },
        body: JSON.stringify({
          model: selectedModel,
          messages: apiMessages,
          stream: true
        })
      })

      if (!response.ok) {
        const errText = await response.text()
        throw new Error(`HTTP ${response.status}: ${errText}`)
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
              
              setMessages(prev => {
                const updated = [...prev]
                updated[updated.length - 1] = { role: "assistant", content: assistantContent }
                return updated
              })
            } catch (e) {
              // Ignore parse errors for empty/non-JSON chunks
            }
          }
        }
      }
      
      // Refresh credits after stream ends
      const user = JSON.parse(localStorage.getItem("himmi_user") || "{}")
      if (user.id) {
        const updatedUser = await ControlService.getUserStatusUsersUserIdGet(user.id)
        setCredits(updatedUser.credits)
      }

    } catch (err) {
      console.error("Stream error", err)
      setMessages(prev => {
        const updated = [...prev]
        updated[updated.length - 1] = { role: "assistant", content: `Error: ${(err as Error).message || "Failed to get response. Please check your API Key and Gateway connectivity."}` }
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
          <div className="flex items-center gap-3 glass border border-white/10 px-4 py-2 rounded-2xl">
            <span className="text-xs text-muted-foreground uppercase font-semibold">Credits</span>
            <span className="text-lg font-bold text-primary">{credits?.toLocaleString() ?? "---"}</span>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-1 overflow-hidden">
          {/* Settings Sidebar */}
          <div className="space-y-6 lg:border-r lg:border-white/10 lg:pr-6">
            <div className="space-y-4">
              <label className="text-sm font-semibold flex items-center gap-2">
                <Cpu className="w-4 h-4 text-primary" /> Model Selection
              </label>
              <select 
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2 focus:ring-2 focus:ring-primary outline-none transition-all"
              >
                {models.map(m => <option key={m.id} value={m.slug}>{m.name}</option>)}
              </select>
            </div>

            <div className="space-y-4">
              <label className="text-sm font-semibold flex items-center gap-2">
                <Key className="w-4 h-4 text-emerald-500" /> API Key
              </label>
              <input 
                type="password"
                placeholder="Enter raw sk-or-v1-..."
                value={selectedKey}
                onChange={(e) => setSelectedKey(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2 focus:ring-2 focus:ring-emerald-500 outline-none transition-all"
              />
              <p className="text-[10px] text-muted-foreground italic">Paste your generated key here for current session.</p>
            </div>

            <button 
              onClick={() => setMessages([])}
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
                      <div className={`px-4 py-2 rounded-2xl max-w-[80%] ${
                        msg.role === "user" ? "bg-primary/20 text-foreground" : "bg-white/5 border border-white/10"
                      }`}>
                        <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.content || (isLoading && i === messages.length - 1 ? "..." : "")}</p>
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
