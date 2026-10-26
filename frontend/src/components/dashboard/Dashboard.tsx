"use client";

import { useState } from "react";
import { Layers, BarChart2, MessageSquare, Bot, FileText } from "lucide-react";
import { useProject } from "@/lib/hooks";
import { cn } from "@/lib/utils";
import { SourcesTab } from "./SourcesTab";
import { InsightsTab } from "./InsightsTab";
import { ReviewsTab } from "./ReviewsTab";
import { CopilotTab } from "./CopilotTab";
import { ReportsTab } from "./ReportsTab";

type Tab = "sources" | "insights" | "reviews" | "copilot" | "reports";

const TABS: { id: Tab; label: string; icon: React.ReactNode }[] = [
  { id: "sources",  label: "Sources",  icon: <Layers size={13} /> },
  { id: "insights", label: "Insights", icon: <BarChart2 size={13} /> },
  { id: "reviews",  label: "Reviews",  icon: <MessageSquare size={13} /> },
  { id: "copilot",  label: "Copilot",  icon: <Bot size={13} /> },
  { id: "reports",  label: "Reports",  icon: <FileText size={13} /> },
];

interface DashboardProps {
  projectId: string;
}

export function Dashboard({ projectId }: DashboardProps) {
  const [activeTab, setActiveTab] = useState<Tab>("sources");
  const { data: project, isLoading } = useProject(projectId);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full text-[#9aa3b2] text-[13px]">
        Loading project…
      </div>
    );
  }

  if (!project) return null;

  return (
    <div className="flex flex-col h-full fade-in">
      {/* Project header */}
      <div className="mb-4 shrink-0">
        <h1 className="text-lg sm:text-xl font-bold text-[#e7e9ee] truncate">{project.name}</h1>
        <p className="text-[12px] text-[#9aa3b2] mt-0.5 truncate">
          {project.product_name}
          {project.description && ` · ${project.description}`}
          {" · "}
          {project.sources.length} source{project.sources.length !== 1 ? "s" : ""}
        </p>

        {/* Tabs */}
        <div className="flex gap-0.5 mt-3 border-b border-[#2a2f3a] overflow-x-auto no-scrollbar">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                "flex items-center gap-1.5 px-3 py-2 text-[12px] font-semibold border-b-2 transition-all cursor-pointer shrink-0 whitespace-nowrap",
                activeTab === tab.id
                  ? "text-[#e7e9ee] border-[#5b8cff]"
                  : "text-[#9aa3b2] border-transparent hover:text-[#e7e9ee] hover:border-[#2a2f3a]"
              )}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab content */}
      <div className="flex-1 overflow-y-auto overflow-x-hidden">
        {activeTab === "sources"  && <SourcesTab  projectId={project.id} sources={project.sources} />}
        {activeTab === "insights" && <InsightsTab projectId={project.id} />}
        {activeTab === "reviews"  && <ReviewsTab  projectId={project.id} />}
        {activeTab === "copilot"  && <CopilotTab  projectId={project.id} />}
        {activeTab === "reports"  && <ReportsTab  projectId={project.id} />}
      </div>
    </div>
  );
}
