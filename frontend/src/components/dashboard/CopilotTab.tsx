"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, BookOpen } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { toast } from "@/components/ui/Toast";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { ChatResponse } from "@/lib/types";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: ChatResponse["sources"];
}

interface CopilotTabProps {
  projectId: string;
}

export function CopilotTab({ projectId }: CopilotTabProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [historyLoaded, setHistoryLoaded] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    let cancelled = false;
    setHistoryLoaded(false);
    api.chat
      .history(projectId)
      .then((items) => {
        if (cancelled) return;
        setMessages(
          items.flatMap((item) => [
            { role: "user" as const, content: item.question },
            { role: "assistant" as const, content: item.answer, sources: item.sources },
          ])
        );
      })
      .catch(() => {
        // No prior history is a normal state (new project) — leave the empty-state UI.
      })
      .finally(() => {
        if (!cancelled) setHistoryLoaded(true);
      });
    return () => {
      cancelled = true;
    };
  }, [projectId]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const question = input.trim();
    if (!question) return;

    setMessages((m) => [...m, { role: "user", content: question }]);
    setInput("");
    setLoading(true);

    try {
      const res = await api.chat.ask(projectId, question);
      setMessages((m) => [
        ...m,
        { role: "assistant", content: res.answer, sources: res.sources },
      ]);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to get response";
      toast(msg, "err");
      setMessages((m) => [
        ...m,
        { role: "assistant", content: `Error: ${msg}` },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card className="flex flex-col" style={{ height: "calc(100vh - 210px)" }}>
      {/* Chat log */}
      <div className="flex-1 overflow-y-auto pr-1 space-y-4 pb-4">
        {!historyLoaded ? null : messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center py-12">
            <Bot size={36} className="text-[#2a2f3a] mb-3" />
            <p className="text-[#9aa3b2] font-medium">Ask the AI copilot</p>
            <p className="text-[12px] text-[#9aa3b2] mt-1 max-w-xs">
              Questions are answered using your project&apos;s ingested feedback as context.
            </p>
            <div className="mt-4 space-y-2 w-full max-w-sm">
              {[
                "Why are users unhappy?",
                "What features do users request most?",
                "What are the biggest pain points?",
              ].map((q) => (
                <button
                  key={q}
                  onClick={() => setInput(q)}
                  className="w-full text-left text-[12px] px-3 py-2 rounded-lg border border-[#2a2f3a] text-[#9aa3b2] hover:border-[#5b8cff] hover:text-[#e7e9ee] transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg, i) => (
            <div
              key={i}
              className={cn("flex gap-2.5", msg.role === "user" ? "justify-end" : "justify-start")}
            >
              {msg.role === "assistant" && (
                <div className="w-7 h-7 rounded-full bg-[#5b8cff]/20 border border-[#5b8cff]/30 flex items-center justify-center shrink-0 mt-0.5">
                  <Bot size={13} className="text-[#5b8cff]" />
                </div>
              )}

              <div
                className={cn(
                  "max-w-[80%] rounded-xl px-3.5 py-2.5 text-[13px] leading-relaxed",
                  msg.role === "user"
                    ? "bg-[#5b8cff] text-[#06122e] font-medium"
                    : "bg-[#1e222b] border border-[#2a2f3a] text-[#e7e9ee]"
                )}
              >
                <p className="whitespace-pre-wrap">{msg.content}</p>

                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-[#2a2f3a]">
                    <div className="flex items-center gap-1 text-[11px] text-[#9aa3b2] mb-1.5">
                      <BookOpen size={10} />
                      <span>Sources ({msg.sources.length})</span>
                    </div>
                    <div className="space-y-1">
                      {msg.sources.slice(0, 3).map((src) => (
                        <div
                          key={src.index}
                          className="text-[11px] text-[#9aa3b2] pl-2 border-l border-[#2a2f3a] line-clamp-2"
                        >
                          [{src.index}] {src.text}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {msg.role === "user" && (
                <div className="w-7 h-7 rounded-full bg-[#1e222b] border border-[#2a2f3a] flex items-center justify-center shrink-0 mt-0.5">
                  <User size={13} className="text-[#9aa3b2]" />
                </div>
              )}
            </div>
          ))
        )}

        {loading && (
          <div className="flex gap-2.5 justify-start">
            <div className="w-7 h-7 rounded-full bg-[#5b8cff]/20 border border-[#5b8cff]/30 flex items-center justify-center shrink-0">
              <Bot size={13} className="text-[#5b8cff]" />
            </div>
            <div className="bg-[#1e222b] border border-[#2a2f3a] rounded-xl px-3.5 py-2.5">
              <div className="flex gap-1 items-center h-5">
                {[0, 150, 300].map((delay) => (
                  <div
                    key={delay}
                    className="w-1.5 h-1.5 rounded-full bg-[#5b8cff]"
                    style={{ animation: `bounce 1s ${delay}ms infinite` }}
                  />
                ))}
              </div>
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="flex gap-2 pt-3 border-t border-[#2a2f3a]">
        <input
          className={cn(
            "flex-1 px-3 py-2 bg-[#1e222b] border border-[#2a2f3a] rounded-lg",
            "text-[#e7e9ee] text-[13px] placeholder:text-[#9aa3b2]",
            "focus:outline-none focus:border-[#5b8cff] transition-colors"
          )}
          placeholder="Why are users unhappy?"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
          autoComplete="off"
        />
        <Button type="submit" variant="primary" loading={loading} disabled={!input.trim()}>
          <Send size={13} />
        </Button>
      </form>

      <style jsx>{`
        @keyframes bounce {
          0%, 60%, 100% { transform: translateY(0); }
          30% { transform: translateY(-4px); }
        }
      `}</style>
    </Card>
  );
}
