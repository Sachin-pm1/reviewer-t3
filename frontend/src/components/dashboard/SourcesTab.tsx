"use client";

import { useState, useEffect } from "react";
import { Plus, Database, CheckCircle2, Clock, AlertCircle, Play, Loader2 } from "lucide-react";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Select, Textarea } from "@/components/ui/Input";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { Badge } from "@/components/ui/Badge";
import { toast } from "@/components/ui/Toast";
import { useSourceTypes, useJob, revalidateProject, revalidateInsights } from "@/lib/hooks";
import { api } from "@/lib/api";
import { SOURCE_TEMPLATES, formatRelative } from "@/lib/utils";
import type { SourceRead, JobRead } from "@/lib/types";

interface SourcesTabProps {
  projectId: string;
  sources: SourceRead[];
}

const STATUS_ICONS: Record<string, React.ReactNode> = {
  active:  <CheckCircle2 size={13} className="text-[#34d399]" />,
  pending: <Clock size={13} className="text-[#fbbf24]" />,
  error:   <AlertCircle size={13} className="text-[#f87171]" />,
};

function JobProgress({ jobId, onDone }: { jobId: string; onDone: () => void }) {
  const { data: job } = useJob(jobId, 1200);

  useEffect(() => {
    if (job?.status === "completed" || job?.status === "failed") {
      onDone();
    }
  }, [job?.status, onDone]);

  if (!job) return null;

  const isRunning = job.status === "pending" || job.status === "running";

  return (
    <div className="mt-3 space-y-1.5">
      <div className="flex justify-between text-[11px] text-[#9aa3b2]">
        <span className="capitalize font-medium">{job.stage}</span>
        {job.total > 0 && (
          <span>{job.processed} / {job.total}</span>
        )}
      </div>
      <ProgressBar value={isRunning ? (job.progress || 0.05) : (job.status === "completed" ? 1 : job.progress)} showLabel />
      {job.status === "failed" && job.error && (
        <p className="text-[11px] text-[#f87171]">{job.error}</p>
      )}
      {job.status === "completed" && (
        <p className="text-[11px] text-[#34d399] font-medium">
          ✓ Analysis complete — switch to Insights tab
        </p>
      )}
    </div>
  );
}

export function SourcesTab({ projectId, sources }: SourcesTabProps) {
  const { data: sourceTypes = [] } = useSourceTypes();
  const [selectedType, setSelectedType] = useState("file_csv");
  const [configJson, setConfigJson] = useState(
    JSON.stringify(SOURCE_TEMPLATES["file_csv"], null, 2)
  );
  const [adding, setAdding] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [activeJobId, setActiveJobId] = useState<string | null>(null);

  useEffect(() => {
    const tpl = SOURCE_TEMPLATES[selectedType] ?? {};
    setConfigJson(JSON.stringify(tpl, null, 2));
  }, [selectedType]);

  async function handleAddSource() {
    let config: Record<string, unknown>;
    try {
      config = JSON.parse(configJson);
    } catch {
      toast("Invalid JSON in config", "err");
      return;
    }
    setAdding(true);
    try {
      await api.sources.add(projectId, { source_type: selectedType, config });
      await revalidateProject(projectId);
      toast("Source added", "ok");
    } catch (err: unknown) {
      toast(err instanceof Error ? err.message : "Failed to add source", "err");
    } finally {
      setAdding(false);
    }
  }

  async function handleAnalyze() {
    setAnalyzing(true);
    try {
      const job = await api.jobs.start(projectId);
      setActiveJobId(job.id);
    } catch (err: unknown) {
      toast(err instanceof Error ? err.message : "Failed to start analyze job", "err");
      setAnalyzing(false);
    }
  }

  function handleJobDone() {
    setAnalyzing(false);
    revalidateProject(projectId);
    revalidateInsights(projectId);
    toast("Analysis finished!", "ok");
  }

  const typeOptions = sourceTypes.map((t) => ({ value: t, label: t }));

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      {/* Add source */}
      <Card>
        <CardHeader>
          <CardTitle>Add a data source</CardTitle>
          <Plus size={14} className="text-[#9aa3b2]" />
        </CardHeader>

        {typeOptions.length > 0 ? (
          <Select
            label="Connector type"
            options={typeOptions}
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
          />
        ) : (
          <p className="text-[12px] text-[#9aa3b2]">Loading connectors…</p>
        )}

        <div className="mt-3">
          <Textarea
            label="Config (JSON)"
            rows={8}
            value={configJson}
            onChange={(e) => setConfigJson(e.target.value)}
            spellCheck={false}
          />
        </div>

        <Button
          variant="default"
          className="mt-3 w-full"
          onClick={handleAddSource}
          loading={adding}
        >
          Add source
        </Button>
      </Card>

      {/* Configured sources + Analyze */}
      <Card>
        <CardHeader>
          <CardTitle>Configured sources</CardTitle>
          <Database size={14} className="text-[#9aa3b2]" />
        </CardHeader>

        {sources.length === 0 ? (
          <p className="text-[12px] text-[#9aa3b2] py-2">No sources yet — add one on the left.</p>
        ) : (
          <ul className="space-y-2 mb-4">
            {sources.map((s) => (
              <li
                key={s.id}
                className="flex justify-between items-start p-2.5 bg-[#1e222b] rounded-lg border border-[#2a2f3a]"
              >
                <div>
                  <div className="flex items-center gap-1.5 text-[12px] font-semibold">
                    {STATUS_ICONS[s.status] ?? STATUS_ICONS.pending}
                    <span>{s.source_type}</span>
                  </div>
                  <div className="text-[11px] text-[#9aa3b2] mt-0.5">
                    {s.review_count > 0 && `${s.review_count} reviews`}
                    {s.last_collected_at && ` · ${formatRelative(s.last_collected_at)}`}
                  </div>
                </div>
                <Badge>{s.status}</Badge>
              </li>
            ))}
          </ul>
        )}

        <div className="border-t border-[#2a2f3a] pt-3">
          <Button
            variant="primary"
            className="w-full"
            onClick={handleAnalyze}
            loading={analyzing && !activeJobId}
            disabled={sources.length === 0 || (analyzing && !!activeJobId)}
          >
            {analyzing && activeJobId ? (
              <><Loader2 size={13} className="spin" /> Running…</>
            ) : (
              <><Play size={13} /> Analyze</>
            )}
          </Button>

          {activeJobId && (
            <JobProgress jobId={activeJobId} onDone={handleJobDone} />
          )}
        </div>
      </Card>
    </div>
  );
}
