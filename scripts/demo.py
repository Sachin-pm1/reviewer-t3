"""End-to-end demo driver for the AI Product Intelligence Platform.

Run the API first (`uvicorn app.main:app --reload`), then in another terminal:

    python scripts/demo.py

It creates a "Spotify" project, adds the sample CSV as a source, runs the analyze
lifecycle, polls the job to completion, prints the insights dashboard, and asks the
copilot a question. The analysis + chat steps require ANTHROPIC_API_KEY; without it the
ingestion + knowledge-base build still run and the analyze job reports a skip note.
"""

from __future__ import annotations

import asyncio
import time
from pathlib import Path

import httpx

BASE_URL = "http://localhost:8000"
SAMPLE_CSV = str((Path(__file__).resolve().parents[1] / "data" / "sample_spotify_reviews.csv"))


async def main() -> None:
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=120) as client:
        health = (await client.get("/health")).json()
        print(f"Health: {health}")

        # 1) Create the project (auto-creates a default product).
        project = (
            await client.post(
                "/projects",
                json={"name": "Spotify", "product_name": "Spotify"},
            )
        ).json()
        project_id = project["id"]
        print(f"Created project {project_id}")

        # 2) Add the CSV source.
        source = (
            await client.post(
                f"/projects/{project_id}/sources",
                json={
                    "source_type": "file_csv",
                    "config": {
                        "path": SAMPLE_CSV,
                        "text_column": "text",
                        "rating_column": "rating",
                        "author_column": "author",
                        "id_column": "id",
                    },
                },
            )
        ).json()
        print(f"Added source {source['id']} ({source['source_type']})")

        # 3) Kick off the analyze lifecycle.
        job = (await client.post(f"/projects/{project_id}/analyze", json={})).json()
        job_id = job["id"]
        print(f"Started analyze job {job_id}")

        # 4) Poll to completion.
        while True:
            job = (await client.get(f"/jobs/{job_id}")).json()
            print(f"  job status={job['status']} stage={job['stage']} progress={job['progress']}")
            if job["status"] in {"completed", "failed"}:
                break
            time.sleep(2)
        print(f"Job result: {job.get('result')}  error={job.get('error')}")

        # 5) Insights dashboard.
        insights = (await client.get(f"/projects/{project_id}/insights")).json()
        print("\n=== INSIGHTS ===")
        print(f"Reviews: {insights['total_reviews']} | Analyzed: {insights['analyzed_reviews']}")
        print(f"Sentiment: {insights['sentiment_distribution']}")
        print("Top pain points:")
        for pp in insights["pain_points"][:5]:
            print(f"  - {pp['label']} (x{pp['count']}) severity={pp['severity_mix']}")
        print("Personas:")
        for p in insights["personas"][:5]:
            print(f"  - {p['label']} (x{p['count']})")
        print("Opportunities:")
        for o in insights["opportunities"][:5]:
            print(f"  - {o['label']} (x{o['count']})")

        # 6) Ask the copilot.
        chat = (
            await client.post(
                f"/projects/{project_id}/chat",
                json={"question": "Why are users unhappy?"},
            )
        ).json()
        print("\n=== COPILOT ===")
        print(chat.get("answer"))
        print(f"({len(chat.get('sources', []))} sources cited)")

        # 7) Generate an executive report (agent-driven, grounded on the insights).
        report_resp = await client.post(
            f"/projects/{project_id}/reports", json={"report_type": "executive"}
        )
        print("\n=== EXECUTIVE REPORT ===")
        if report_resp.status_code == 201:
            report = report_resp.json()
            print(f"{report['title']} (report {report['id']})")
            print("\n".join(report["content_markdown"].splitlines()[:12]))
            print("… (full Markdown + structured JSON returned by the API)")
        else:
            print(f"Report generation returned {report_resp.status_code}: {report_resp.json()}")


if __name__ == "__main__":
    asyncio.run(main())
