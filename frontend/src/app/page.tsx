"use client";

import { useState } from "react";
import { Compass } from "lucide-react";
import { Topbar } from "@/components/layout/Topbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { Dashboard } from "@/components/dashboard/Dashboard";
import { Toaster } from "@/components/ui/Toast";

export default function Home() {
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-[#0f1115]">
      <Topbar onMenuClick={() => setSidebarOpen((v) => !v)} />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          selectedId={selectedProjectId}
          onSelect={setSelectedProjectId}
          open={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
        />

        <main className="flex-1 overflow-y-auto min-w-0 p-3 sm:p-5">
          {selectedProjectId ? (
            <Dashboard projectId={selectedProjectId} />
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-center fade-in px-4">
              <div className="w-16 h-16 rounded-2xl bg-[#5b8cff]/10 border border-[#5b8cff]/20 flex items-center justify-center mb-4">
                <Compass size={28} className="text-[#5b8cff]" />
              </div>
              <h1 className="text-xl sm:text-2xl font-bold text-[#e7e9ee] mb-2">
                AI Product Intelligence
              </h1>
              <p className="text-[#9aa3b2] max-w-sm leading-relaxed">
                Create a project, add a data source, and click{" "}
                <strong className="text-[#e7e9ee]">Analyze</strong>. The platform
                ingests your feedback, builds a knowledge base, and extracts structured
                insights with Claude.
              </p>
              <p className="text-[12px] text-[#9aa3b2] mt-3">
                <span className="hidden lg:inline">← Select or create a project to get started.</span>
                <span className="lg:hidden">Tap ☰ to select or create a project.</span>
              </p>
            </div>
          )}
        </main>
      </div>

      <Toaster />
    </div>
  );
}
