"use client";

import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
} from "recharts";
import { AlertTriangle, Users, Lightbulb, Tag } from "lucide-react";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { useInsights } from "@/lib/hooks";
import { sentimentColor, capitalize, cn } from "@/lib/utils";
import type { Sentiment } from "@/lib/types";

const SENTIMENT_ORDER: Sentiment[] = ["positive", "negative", "neutral", "mixed"];

interface InsightsTabProps {
  projectId: string;
}

function EmptyInsights() {
  return (
    <div className="sm:col-span-2 flex flex-col items-center justify-center py-16 text-center">
      <AlertTriangle size={32} className="text-[#2a2f3a] mb-3" />
      <p className="text-[#9aa3b2] font-medium">No insights yet</p>
      <p className="text-[12px] text-[#9aa3b2] mt-1">
        Add a data source and click <strong className="text-[#e7e9ee]">Analyze</strong> on the Sources tab.
      </p>
    </div>
  );
}

export function InsightsTab({ projectId }: InsightsTabProps) {
  const { data: overview, isLoading } = useInsights(projectId);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20 text-[#9aa3b2] text-[13px]">
        Loading insights…
      </div>
    );
  }

  if (!overview || overview.analyzed_reviews === 0) {
    return <div className="grid grid-cols-1 sm:grid-cols-2 gap-4"><EmptyInsights /></div>;
  }

  const sentimentData = SENTIMENT_ORDER
    .filter((k) => (overview.sentiment_distribution[k] ?? 0) > 0)
    .map((k) => ({
      name: capitalize(k),
      value: overview.sentiment_distribution[k] ?? 0,
      color: sentimentColor(k),
    }));

  const topicData = overview.top_topics
    .slice(0, 8)
    .map((t) => ({ name: t.label.length > 22 ? t.label.slice(0, 22) + "…" : t.label, count: t.count }));

  return (
    <div className="space-y-4 fade-in">
      {/* KPI row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: "Total reviews", value: overview.total_reviews, color: "text-[#5b8cff]" },
          { label: "Analyzed",      value: overview.analyzed_reviews, color: "text-[#34d399]" },
          { label: "Pain points",   value: overview.pain_points.length, color: "text-[#f87171]" },
          { label: "Opportunities", value: overview.opportunities.length, color: "text-[#fbbf24]" },
        ].map((k) => (
          <Card key={k.label} className="text-center">
            <div className={cn("text-3xl font-bold", k.color)}>{k.value}</div>
            <div className="text-[11px] text-[#9aa3b2] mt-1">{k.label}</div>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Sentiment Pie */}
        <Card>
          <CardHeader>
            <CardTitle>Sentiment distribution</CardTitle>
          </CardHeader>
          {sentimentData.length > 0 ? (
            <div className="flex items-center gap-4">
              <ResponsiveContainer width={140} height={140}>
                <PieChart>
                  <Pie
                    data={sentimentData}
                    cx="50%"
                    cy="50%"
                    innerRadius={42}
                    outerRadius={65}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {sentimentData.map((entry, i) => (
                      <Cell key={i} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ background: "#1e222b", border: "1px solid #2a2f3a", borderRadius: 8, fontSize: 12 }}
                    itemStyle={{ color: "#e7e9ee" }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-1.5 flex-1">
                {sentimentData.map((s) => (
                  <div key={s.name} className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5">
                      <div className="w-2 h-2 rounded-full" style={{ background: s.color }} />
                      <span className="text-[12px] text-[#9aa3b2]">{s.name}</span>
                    </div>
                    <span className="text-[12px] font-semibold" style={{ color: s.color }}>{s.value}</span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p className="text-[12px] text-[#9aa3b2]">No data yet.</p>
          )}
        </Card>

        {/* Top topics Bar */}
        <Card>
          <CardHeader>
            <CardTitle>
              <div className="flex items-center gap-1.5"><Tag size={13} />Top topics</div>
            </CardTitle>
          </CardHeader>
          {topicData.length > 0 ? (
            <ResponsiveContainer width="100%" height={160}>
              <BarChart data={topicData} layout="vertical" margin={{ left: 0, right: 16, top: 0, bottom: 0 }}>
                <CartesianGrid horizontal={false} stroke="#2a2f3a" strokeDasharray="3 3" />
                <XAxis type="number" tick={{ fill: "#9aa3b2", fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis type="category" dataKey="name" width={110} tick={{ fill: "#9aa3b2", fontSize: 10 }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ background: "#1e222b", border: "1px solid #2a2f3a", borderRadius: 8, fontSize: 12 }}
                  itemStyle={{ color: "#34d399" }}
                  cursor={{ fill: "#2a2f3a" }}
                />
                <Bar dataKey="count" fill="#5b8cff" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-[12px] text-[#9aa3b2]">No topics yet.</p>
          )}
        </Card>

        {/* Pain points */}
        <Card>
          <CardHeader>
            <CardTitle>
              <div className="flex items-center gap-1.5"><AlertTriangle size={13} className="text-[#f87171]" />Pain points</div>
            </CardTitle>
          </CardHeader>
          <ul className="divide-y divide-[#2a2f3a]">
            {overview.pain_points.slice(0, 6).map((pp) => (
              <li key={pp.label} className="py-2 first:pt-0 last:pb-0">
                <div className="flex justify-between items-start gap-2">
                  <span className="text-[13px] font-semibold text-[#e7e9ee]">{pp.label}</span>
                  <span className="text-[11px] text-[#9aa3b2] shrink-0">{pp.count}×</span>
                </div>
                {pp.examples[0] && (
                  <p className="text-[11px] text-[#9aa3b2] mt-0.5 line-clamp-1">{pp.examples[0]}</p>
                )}
                {Object.keys(pp.severity_mix).length > 0 && (
                  <div className="flex gap-1 mt-1 flex-wrap">
                    {Object.entries(pp.severity_mix).map(([sev, cnt]) => (
                      <Badge key={sev} variant={sev === "critical" || sev === "high" ? "negative" : "neutral"}>
                        {sev} {cnt}
                      </Badge>
                    ))}
                  </div>
                )}
              </li>
            ))}
          </ul>
          {overview.pain_points.length === 0 && (
            <p className="text-[12px] text-[#9aa3b2]">No pain points identified.</p>
          )}
        </Card>

        {/* Personas */}
        <Card>
          <CardHeader>
            <CardTitle>
              <div className="flex items-center gap-1.5"><Users size={13} className="text-[#5b8cff]" />Personas</div>
            </CardTitle>
          </CardHeader>
          <ul className="divide-y divide-[#2a2f3a]">
            {overview.personas.slice(0, 5).map((p) => (
              <li key={p.label} className="py-2 first:pt-0 last:pb-0">
                <div className="flex justify-between items-center gap-2">
                  <span className="text-[13px] font-semibold text-[#e7e9ee]">{p.label}</span>
                  <span className="text-[11px] text-[#9aa3b2]">{p.count}×</span>
                </div>
                {p.top_pain_points.length > 0 && (
                  <div className="flex gap-1 mt-1 flex-wrap">
                    {p.top_pain_points.slice(0, 3).map((pp) => (
                      <Badge key={pp}>{pp}</Badge>
                    ))}
                  </div>
                )}
              </li>
            ))}
          </ul>
          {overview.personas.length === 0 && (
            <p className="text-[12px] text-[#9aa3b2]">No personas identified.</p>
          )}
        </Card>

        {/* Opportunities */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>
              <div className="flex items-center gap-1.5"><Lightbulb size={13} className="text-[#fbbf24]" />Product opportunities</div>
            </CardTitle>
          </CardHeader>
          {overview.opportunities.length === 0 ? (
            <p className="text-[12px] text-[#9aa3b2]">No opportunities identified yet.</p>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">
              {overview.opportunities.slice(0, 6).map((op) => (
                <div
                  key={op.label}
                  className="p-3 bg-[#1e222b] rounded-lg border border-[#2a2f3a] hover:border-[#fbbf24] transition-colors"
                >
                  <div className="text-[13px] font-semibold text-[#e7e9ee] mb-1">{op.label}</div>
                  <div className="text-[11px] text-[#9aa3b2]">Mentioned {op.count}×</div>
                  {Object.entries(op.impact_mix).map(([impact, cnt]) => (
                    <Badge key={impact} variant={impact === "high" ? "warn" : "neutral"} className="mt-1.5">
                      {impact} impact ({cnt})
                    </Badge>
                  ))}
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
