'use client';

import { useEffect, useState, useRef, useCallback } from 'react';
import { api, type AssistantResponse } from '@/lib/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: string[];
  confidence?: number;
  suggested_actions?: string[];
}

export default function AssistantPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: `Hello! I'm the ClimateTwin AI Climate Assistant. I can answer questions about India's climate, explain AI predictions, analyze regional conditions, and help you interpret climate data.\n\nAsk me about rainfall patterns, heatwave risks, drought conditions, or request an explanation of any AI prediction.`,
      timestamp: new Date(),
      sources: ['ClimateTwin AI'],
      confidence: 1.0,
      suggested_actions: [
        'Which states are at highest flood risk?',
        'Explain the temperature anomaly in Rajasthan',
        'What is the drought status in Tamil Nadu?',
      ],
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>();
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    api.getAssistantSuggestions()
      .then((data) => setSuggestions(data.suggestions || []))
      .catch(() => {});
  }, []);

  const sendMessage = useCallback(async (text?: string) => {
    const msg = text ?? input.trim();
    if (!msg || loading) return;

    setInput('');
    const userMsg: Message = { role: 'user', content: msg, timestamp: new Date() };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await api.chat(msg, sessionId);
      setSessionId(res.session_id);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: res.response,
          timestamp: new Date(),
          sources: res.sources,
          confidence: res.confidence,
          suggested_actions: res.suggested_actions,
        },
      ]);
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error connecting to the ClimateTwin backend. Please ensure the API server is running.',
          timestamp: new Date(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  }, [input, loading, sessionId]);

  return (
    <div className="h-[calc(100vh-56px)] flex flex-col">
      {/* Header */}
      <div className="px-6 py-4 border-b border-white/5 flex items-center justify-between">
        <div>
          <h2 className="text-base font-bold text-display flex items-center gap-2">
            <span className="text-xl">💬</span> AI Climate Assistant
          </h2>
          <p className="text-[10px] text-slate-500">
            Powered by ClimateTwin AI · IMD · INSAT data context
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="status-dot status-live" />
          <span className="text-[10px] text-green-400 font-mono">ONLINE</span>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Chat Area */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex gap-3 animate-fade-up ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-violet-600 flex items-center justify-center text-xs flex-shrink-0 mt-1">
                    🤖
                  </div>
                )}
                <div className={`max-w-[80%] ${msg.role === 'user' ? 'order-first' : ''}`}>
                  <div
                    className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                      msg.role === 'user'
                        ? 'bg-gradient-to-br from-cyan-600 to-violet-700 text-white rounded-br-sm'
                        : 'glass-card border-cyan-500/10 text-slate-200 rounded-bl-sm'
                    }`}
                  >
                    {msg.content}
                  </div>

                  {/* Metadata */}
                  {msg.role === 'assistant' && msg.sources && (
                    <div className="mt-2 flex flex-wrap gap-2">
                      {msg.sources.map((src) => (
                        <span key={src} className="text-[9px] bg-white/5 border border-white/10 px-2 py-0.5 rounded-full text-slate-500">
                          {src}
                        </span>
                      ))}
                      {msg.confidence && (
                        <span className="text-[9px] bg-green-500/10 border border-green-500/20 px-2 py-0.5 rounded-full text-green-400">
                          {(msg.confidence * 100).toFixed(0)}% confidence
                        </span>
                      )}
                    </div>
                  )}

                  {/* Suggested actions */}
                  {msg.role === 'assistant' && msg.suggested_actions && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {msg.suggested_actions.slice(0, 3).map((action) => (
                        <button
                          key={action}
                          onClick={() => sendMessage(action)}
                          className="text-[10px] bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 px-3 py-1 rounded-full hover:bg-cyan-500/20 transition-colors"
                        >
                          {action}
                        </button>
                      ))}
                    </div>
                  )}

                  <p className="text-[9px] text-slate-600 mt-1 px-1">
                    {msg.timestamp.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>

                {msg.role === 'user' && (
                  <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-xs flex-shrink-0 mt-1">
                    👤
                  </div>
                )}
              </div>
            ))}

            {/* Loading indicator */}
            {loading && (
              <div className="flex gap-3 animate-fade-up">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-violet-600 flex items-center justify-center text-xs flex-shrink-0">
                  🤖
                </div>
                <div className="glass-card px-4 py-3 rounded-2xl rounded-bl-sm">
                  <div className="flex gap-1 items-center h-5">
                    {[0, 1, 2].map((i) => (
                      <div
                        key={i}
                        className="w-2 h-2 rounded-full bg-cyan-400 animate-bounce"
                        style={{ animationDelay: `${i * 0.15}s` }}
                      />
                    ))}
                  </div>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input Area */}
          <div className="p-4 border-t border-white/5">
            <div className="flex gap-3">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
                placeholder="Ask about India's climate, predictions, or risk advisories..."
                className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-slate-200 placeholder:text-slate-500 outline-none focus:border-cyan-500/50 transition-colors"
                disabled={loading}
              />
              <button
                onClick={() => sendMessage()}
                disabled={loading || !input.trim()}
                className="btn-primary px-5 py-3 rounded-xl disabled:opacity-40"
              >
                Send
              </button>
            </div>
          </div>
        </div>

        {/* Sidebar — Suggestions */}
        <div className="w-64 border-l border-white/5 p-4 hidden xl:block">
          <h3 className="text-xs font-semibold text-slate-400 mb-3 uppercase tracking-wider">
            Suggested Questions
          </h3>
          <div className="space-y-2">
            {suggestions.map((q, i) => (
              <button
                key={i}
                onClick={() => sendMessage(q)}
                className="w-full text-left text-[11px] text-slate-400 hover:text-slate-200 p-2 rounded-lg hover:bg-white/5 transition-colors leading-relaxed"
              >
                {q}
              </button>
            ))}
          </div>

          <div className="mt-6 p-3 rounded-lg bg-white/[0.02] border border-white/5">
            <p className="text-[10px] text-slate-500 leading-relaxed">
              <strong className="text-slate-400">Note:</strong> Currently using intelligent mock responses. 
              Connect a real LLM (Gemini, GPT-4) via the assistant service plug-in point.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
