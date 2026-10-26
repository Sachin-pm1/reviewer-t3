# Segment hypothesis + recruitment screener

> **Update: this hypothesis has since been tested against real data and partly
> revised.** See [docs/problem-definition.md](../docs/problem-definition.md)'s
> "Target user segment" section and [interview-findings.md](interview-findings.md) —
> the core pattern held, but real interviews surfaced a second expression of it
> (users who bypass Spotify's discovery entirely via TikTok/Instagram rather than
> narrowing inside it) that this original screener would have excluded. Left
> unedited below as a record of the pre-research hypothesis; don't recruit against
> this screener without reading the update first.

Part 2 exists to pressure-test what the AI review-analysis engine (Part 1) surfaces —
not to rubber-stamp it. This doc has two jobs: state the segment hypothesis this
research is built around, and give you a screener to recruit 5-6 people who actually
belong to it.

## Where this hypothesis comes from

It has **not** yet been confirmed against real review data — [/aura's Insights tab](../app/analysis/schemas.py)
hasn't been run against a live Play Store / App Store / Reddit corpus yet (see the main
project README for the Part 1 connector gaps: Reddit and App Store aren't wired up
yet). Treat everything below as the hypothesis these interviews exist to test, not a
finding. Once Part 1 is run on real data, revisit this segment definition against
whatever personas/topics the Insights tab actually clusters — narrow or re-cut it if
the evidence points elsewhere.

The hypothesis itself comes from the product logic already embedded in the Discovery
Companion MVP (`app/companion/service.py`): it assumes a listener who *has* an
articulable taste profile (seed artists/genres) and wants that profile deliberately
stretched. That only makes sense for a specific kind of user — not everyone who
under-discovers is the same problem.

## Segment hypothesis: "Comfort-Loop Listeners"

**Definition:** Tenured, highly engaged listeners whose recent listening is dominated
by a small, familiar rotation — and who, unprompted or lightly prompted, describe this
as a change from how they used to use the product, not their steady-state preference.

**Explicitly excludes:**
- **New / cold-start users** (< 3 months) — their under-discovery is an onboarding /
  cold-start problem, not a repeat-listening problem. Different root cause, different fix.
- **Content explorers** — users already actively seeking new music through other means
  (blogs, radio, friends) and happy with how they discover. Not underserved; not this
  segment.
- **Churned / about-to-churn users** — a retention research motion, not a discovery one.
  Different interview guide entirely.

**Why this segment matters to the business:** these are the users least likely to
churn (they're still here, still listening daily) and most likely to be invisibly
under-monetized on the discovery dimension — deep catalog plays, new-artist discovery,
and the resulting royalty/label-relationship upside all come disproportionately from
this group if they're unlocked. They're also the hardest segment to see in aggregate
engagement metrics, because total listening time looks healthy even while discovery
specifically has collapsed — which is exactly why review mining (Part 1) and interviews
(Part 2) are needed instead of just reading a dashboard.

## Recruitment screener

Run this as a 5-question intercept survey or a quick pre-call qualifier. Aim for a
mix across Q4 (heavy commute / workout / focus / social listeners) so the discussion
guide's context-mapping section has range to work with.

1. **How long have you used [Spotify]?**
   - < 3 months → **disqualify** (cold-start segment, not this study)
   - 3–12 months → borderline, take if quota needs filling
   - 1+ years → **qualify**

2. **On a typical week, how often do you listen?**
   - A few times a month or less → **disqualify** (not engaged enough to have a
     "loop" to be stuck in)
   - Several times a week / daily → **qualify**

3. **Thinking about the last month: roughly what share of your listening was songs
   or artists you'd already heard many times before, versus something new to you?**
   - Mostly new / actively exploring → **disqualify** (already a content explorer)
   - Mostly familiar / repeat (self-estimate 70%+) → **qualify**
   - Genuinely unsure → keep, this is often the most interesting respondent (repeat
     listening on autopilot, not even tracked consciously)

4. **Which best describes how you feel about that?** *(single select, do not read the
   segment name aloud)*
   - "That's exactly how I like to listen" → **disqualify** (satisfied comfort
     listener — real, but not this segment; they're not underserved, they're served
     correctly)
   - "I used to explore more than I do now" / "I wish I discovered more but don't
     get around to it" / "I don't really think about it, I just end up replaying
     the same stuff" → **qualify** — this is the core signal

5. **Primary listening contexts** *(multi-select — for quota mix, not
   qualification)*: commute, work/study focus, workout, chores/downtime, social
   /parties, sleep/wind-down.

6. **Would you be willing to try a new AI feature live on a 45-minute call and talk
   through your reaction?** *(confirms willingness to do the concept-test portion of
   the discussion guide — decline is a soft disqualifier, not a hard one)*

**Logistics:** 5-6 respondents, 45 min each, remote video call (screen share needed
for the concept-test section), standard incentive for a UX research session. Aim for
at least 2 respondents per primary context if possible (e.g., not all commuters) so
the "when does the loop happen" theme in the discussion guide has contrast to work
with.
