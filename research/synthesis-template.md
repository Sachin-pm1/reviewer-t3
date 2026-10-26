# Synthesis template

> **This has been filled in for real** — see [interview-findings.md](interview-findings.md)
> for the completed synthesis from 6 real interviews, feeding
> [docs/problem-definition.md](../docs/problem-definition.md). Kept below, still
> empty, as a reusable template for future rounds.

Fills two purposes: capture each interview while it's fresh, then roll all 5-6 up into
the inputs Part 3 (problem definition) needs. Copy the per-respondent block below once
per interview; fill the cross-interview grid once all sessions are done.

This is a template, not a finding — leave it empty until real interviews happen. If
you'd like help synthesizing once you have real transcripts or notes, paste them in and
this structure is what to fill in.

---

## Per-respondent notes

Copy for each of the 5-6 respondents.

```
### Respondent [#] — [date]

**Screener profile:** tenure ___ | frequency ___ | self-estimated % familiar ___ |
primary contexts ___

**Self-image vs. behavior gap:** (section 1 self-image) vs. (section 2 actual
last-2-days listening) — did they match or contradict?

**Root cause (their words, section 3):**
- Trigger for the last deliberate discovery attempt: ___
- Named blocker(s): [ ] effort/time  [ ] fear of a bad pick  [ ] decision fatigue
  [ ] doesn't trust recs  [ ] features feel hidden  [ ] social/context pressure
  [ ] other: ___
- Direct quote(s) worth keeping verbatim: ___

**Trust in current recommendations (section 4):**
- Features known/used: ___
- Where the algorithm gets it right / wrong, in their words: ___

**Concept test reaction (section 5):**
- Would they press play on a real pick, and which one: ___
- "Why this fits you" explanations — felt true / generic / off: ___
- Novelty dial — made sense? where would they set it day-to-day: ___
- Comparison to Discover Weekly / Daily Mix, unprompted: ___
- Friction / skepticism moments (exact words): ___
- What would earn enough trust to use weekly: ___

**One thing they'd fix (section 6):** ___

**Interviewer flag:** anything that contradicts the segment hypothesis, or suggests
this respondent doesn't actually belong in it: ___
```

---

## Cross-interview synthesis grid

Fill after all sessions. One row per respondent, so patterns are visible at a glance
rather than buried in six separate documents.

| # | Self-image matched behavior? | Primary named blocker | Trusts recs? | Would play a Companion pick? | Notable quote |
|---|---|---|---|---|---|
| 1 |  |  |  |  |  |
| 2 |  |  |  |  |  |
| 3 |  |  |  |  |  |
| 4 |  |  |  |  |  |
| 5 |  |  |  |  |  |
| 6 |  |  |  |  |  |

**Look for:**
- A blocker named by 4+ of 6 respondents — that's your root cause candidate for Part 3,
  not the first plausible-sounding one from a single interview.
- Whether the segment hypothesis held (most respondents genuinely fit "Comfort-Loop
  Listener") or needs re-cutting (e.g., splits into "too busy to explore" vs. "burned
  by past bad picks" as two different problems needing different fixes).
- Whether the concept test validated the Companion's actual mechanism (deliberate
  novelty + explainability) or revealed the wrong mechanism entirely (e.g., if
  everyone's real blocker is *time*, not *trust*, the MVP may need to change).

---

## Feeding Part 3

Once the grid is filled, Part 3's problem-definition doc needs exactly three things
this grid should now answer directly:

1. **Root cause** — the blocker named by a majority, stated as a mechanism (not a
   symptom). E.g. "users default to familiar tracks under decision fatigue because
   evaluating a new pick costs more attention than they have in-context" is a root
   cause; "users don't discover new music" is a symptom.
2. **Target segment** — confirmed or revised definition of Comfort-Loop Listeners,
   with the screener numbers (tenure/frequency/% familiar) adjusted to match what
   actually qualified real respondents who fit the pattern.
3. **Business case** — which named blockers are addressable by product/AI (trust,
   effort, explainability) versus not (e.g., pure time scarcity is harder to solve
   with a better recommender) — this is what determines whether the opportunity is
   worth prioritizing.
