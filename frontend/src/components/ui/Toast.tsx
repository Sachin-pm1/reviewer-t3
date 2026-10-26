"use client";

import { useEffect, useState } from "react";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

export type ToastVariant = "ok" | "err" | "info";

interface ToastMessage {
  id: number;
  message: string;
  variant: ToastVariant;
}

let addToastExternal: ((msg: string, variant: ToastVariant) => void) | null = null;

export function toast(msg: string, variant: ToastVariant = "info") {
  addToastExternal?.(msg, variant);
}

export function Toaster() {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  useEffect(() => {
    addToastExternal = (message, variant) => {
      const id = Date.now();
      setToasts((prev) => [...prev, { id, message, variant }]);
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
      }, 4000);
    };
    return () => { addToastExternal = null; };
  }, []);

  return (
    <div className="fixed bottom-5 left-0 right-0 sm:left-1/2 sm:right-auto sm:-translate-x-1/2 z-50 flex flex-col gap-2 items-center px-4">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={cn(
            "flex items-center gap-2 px-4 py-2.5 rounded-lg border shadow-xl text-[13px] font-medium fade-in max-w-full sm:max-w-md",
            "bg-[#1e222b]",
            t.variant === "err"  && "border-[#f87171] text-[#f87171]",
            t.variant === "ok"   && "border-[#34d399] text-[#34d399]",
            t.variant === "info" && "border-[#2a2f3a] text-[#e7e9ee]"
          )}
        >
          <span className="min-w-0">{t.message}</span>
          <button
            onClick={() => setToasts((prev) => prev.filter((x) => x.id !== t.id))}
            className="text-current opacity-60 hover:opacity-100"
          >
            <X size={12} />
          </button>
        </div>
      ))}
    </div>
  );
}
