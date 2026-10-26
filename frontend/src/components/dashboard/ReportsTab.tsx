"use client";

import { useState } from "react";
import { FileText, Download, Clock } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { toast } from "@/components/ui/Toast";
import { useReports, useReportTypes, revalidateReports } from "@/lib/hooks";
import { api } from "@/lib/api";
import { formatRelative, capitalize } from "@/lib/utils";
import type { ReportRead, ReportSummary } from "@/lib/types";

interface ReportsTabProps {
  projectId: string;
}

const REPORT_COLORS: Record<string, string> = {
  executive: "text-[#5b8cff]",
  prd:       "text-[#34d399]",
  roadmap:   "text-[#fbbf24]",
};

export function ReportsTab({ projectId }: ReportsTabProps) {
  const { data: reports = [], isLoading } = useReports(projectId);
  const { data: reportTypes = [] } = useReportTypes();
  const [generating, setGenerating] = useState<string | null>(null);
  const [preview, setPreview] = useState<ReportRead | null>(null);
  const [loadingPreview, setLoadingPreview] = useState(false);

  async function handleGenerate(type: string) {
    setGenerating(type);
    try {
      const report = await api.reports.generate(projectId, type);
      await revalidateReports(projectId);
      setPreview(report);
      toast(`${capitalize(type)} report generated`, "ok");
    } catch (err: unknown) {
      toast(err instanceof Error ? err.message : "Failed to generate report", "err");
    } finally {
      setGenerating(null);
    }
  }

  async function handleSelectReport(summary: ReportSummary) {
    if (preview?.id === summary.id) return;
    setLoadingPreview(true);
    try {
      const full = await api.reports.get(summary.id);
      setPreview(full);
    } catch {
      toast("Failed to load report", "err");
    } finally {
      setLoadingPreview(false);
    }
  }

  function handleDownload() {
    if (!preview) return;
    const blob = new Blob([preview.content_markdown], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${preview.report_type}-report.md`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:h-full">
      {/* Left: generate + history */}
      <div className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Generate a report</CardTitle>
            <FileText size={14} className="text-[#9aa3b2]" />
          </CardHeader>
          {reportTypes.length === 0 ? (
            <p className="text-[12px] text-[#9aa3b2]">Loading report types…</p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {reportTypes.map((type) => (
                <Button
                  key={type}
                  variant="default"
                  size="sm"
                  loading={generating === type}
                  onClick={() => handleGenerate(type)}
                  disabled={generating !== null}
                  className={REPORT_COLORS[type]}
                >
                  {capitalize(type)}
                </Button>
              ))}
            </div>
          )}
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>History</CardTitle>
            <Clock size={14} className="text-[#9aa3b2]" />
          </CardHeader>
          {isLoading ? (
            <p className="text-[12px] text-[#9aa3b2]">Loading…</p>
          ) : reports.length === 0 ? (
            <p className="text-[12px] text-[#9aa3b2]">No reports yet — generate one above.</p>
          ) : (
            <ul className="space-y-2">
              {reports.map((r) => (
                <li
                  key={r.id}
                  onClick={() => handleSelectReport(r)}
                  className="flex justify-between items-center p-2.5 bg-[#1e222b] rounded-lg border border-[#2a2f3a] cursor-pointer hover:border-[#5b8cff] transition-colors"
                >
                  <div>
                    <div className={`text-[12px] font-semibold ${REPORT_COLORS[r.report_type] ?? ""}`}>
                      {capitalize(r.report_type)}
                    </div>
                    <div className="text-[11px] text-[#9aa3b2] mt-0.5 line-clamp-1">{r.title}</div>
                  </div>
                  <div className="text-right shrink-0">
                    <Badge>{r.report_type}</Badge>
                    <div className="text-[10px] text-[#9aa3b2] mt-0.5">{formatRelative(r.created_at)}</div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>

      {/* Right: preview */}
      <Card className="flex flex-col overflow-hidden">
        <CardHeader>
          <CardTitle>Preview</CardTitle>
          {preview && (
            <Button size="sm" variant="ghost" onClick={handleDownload}>
              <Download size={12} />
              Download .md
            </Button>
          )}
        </CardHeader>

        <div className="flex-1 overflow-y-auto">
          {loadingPreview ? (
            <div className="flex items-center justify-center h-32 text-[#9aa3b2] text-[12px]">
              Loading…
            </div>
          ) : preview ? (
            <div className="prose-report">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {preview.content_markdown}
              </ReactMarkdown>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-full py-16 text-center">
              <FileText size={28} className="text-[#2a2f3a] mb-3" />
              <p className="text-[12px] text-[#9aa3b2]">Select or generate a report to preview it here.</p>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}
