"use client";

import { MessageSquare } from "lucide-react";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { useReviews } from "@/lib/hooks";
import { stars, formatDate, cn } from "@/lib/utils";

interface ReviewsTabProps {
  projectId: string;
}

export function ReviewsTab({ projectId }: ReviewsTabProps) {
  const { data: reviews = [], isLoading } = useReviews(projectId, 100);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20 text-[#9aa3b2] text-[13px]">
        Loading reviews…
      </div>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          <div className="flex items-center gap-1.5">
            <MessageSquare size={13} />
            Ingested feedback
          </div>
        </CardTitle>
        <span className="text-[12px] text-[#9aa3b2]">{reviews.length} reviews</span>
      </CardHeader>

      {reviews.length === 0 ? (
        <div className="py-12 text-center">
          <MessageSquare size={28} className="mx-auto mb-3 text-[#2a2f3a]" />
          <p className="text-[#9aa3b2]">No reviews ingested yet.</p>
          <p className="text-[12px] text-[#9aa3b2] mt-1">Run Analyze to ingest your sources.</p>
        </div>
      ) : (
        <div className="divide-y divide-[#2a2f3a]">
          {reviews.map((r) => (
            <div key={r.id} className="py-3 first:pt-0 last:pb-0">
              <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mb-1.5">
                {r.rating != null && (
                  <span className="text-[12px] text-[#fbbf24]">{stars(r.rating)}</span>
                )}
                {r.author && (
                  <span className="text-[12px] font-semibold text-[#e7e9ee]">{r.author}</span>
                )}
                <span className="text-[11px] text-[#9aa3b2]">{formatDate(r.created_at)}</span>
                <Badge variant={r.analyzed ? "positive" : "neutral"}>
                  {r.analyzed ? "analyzed" : "pending"}
                </Badge>
                <Badge>{r.source_type}</Badge>
              </div>
              <p className="text-[13px] text-[#e7e9ee] leading-relaxed line-clamp-3">{r.text}</p>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
