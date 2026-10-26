# Problem Definition (Part 3)

Grounded in [docs/part1-findings.md](part1-findings.md) (858 real Play Store + App
Store reviews, AI-analyzed) and [research/interview-findings.md](../research/interview-findings.md)
(6 real interviews). Where the two sources agree, that's called out explicitly — it's
the strongest evidence in this doc. Where they add different things, both are kept
rather than smoothed into one tidy story.

## Root cause

**Spotify's recommendation system optimizes for similarity and safety over
exploration — both by design and by how it reads weak behavioral signals as strong
ones — and gives users no visibility into or control over that trade-off.**

Three concrete mechanisms, not just a restated symptom:

1. **Recency- and familiarity-biased ranking.** A Premium power listener in the Part 1
   data: *"[Spotify] buries the user's true long-term favorites after short browsing
   sessions"* (root cause extracted: recency-biased ranking overweighting recent
   browsing). Independently, interview respondents describe the identical mechanism in
   plain language: *"it keeps recommending music that's 95% similar"* (P2), *"the
   system prioritizes similarity over exploration"* (synthesized across 6/6). Two
   independent methods, same conclusion — that convergence is the strongest single
   piece of evidence in this document.
2. **Weak signals treated as strong ones.** P5, unprompted: *"If I skip one song,
   Spotify assumes I don't like that artist."* A single skip (which could mean
   anything — wrong mood, wrong moment, already heard it today) gets treated as a
   durable negative preference, quietly narrowing future recommendations. Nothing in
   the Part 1 review data named this mechanism this precisely — it took an interview
   to surface it.
3. **No transparency, so no trust, so no risk-taking.** 4/6 interview respondents
   don't fully trust Discover Weekly; 4/6 want explanations for *why* something was
   recommended. Part 1 corroborates from the other side: *"Incredibly bad Algorithm"*
   / recommendations described as forcibly injected into curated playlists with no
   opt-out. An unfamiliar track with zero stated reasoning is pure downside risk to a
   listener — there's nothing to evaluate before spending the time.

A fourth factor showed up only in interviews, not reviews: for a subset of users the
blocker isn't algorithm quality at all, it's **effort** — "finding music feels like
work" (P6) — who default to familiar choices not because the algorithm failed them
but because engaging with discovery costs more attention than they have in the
moment. That's a different mechanism requiring a different fix (frictionless,
conversational input) than the trust/similarity mechanism above (explainability,
control) — both are real, and conflating them would understate the problem's shape.

## Target user segment

**Broader than the original "Comfort-Loop Listener" hypothesis.** That hypothesis
(tenured 1+ year, heavily engaged, self-aware of a decline from past exploration) is
*confirmed as one real expression* of this problem — P1, P2, and P6 all fit it
directly. But the interviews revealed a second, distinct expression the original
screener would have excluded: **users who bypass Spotify's discovery entirely**,
finding new music on TikTok, Instagram, or through friends, and only opening Spotify
to search for what they already heard elsewhere (P3, and referenced by 4/6 overall).
This isn't a lapsed explorer — it may be someone who never trusted Spotify's own
surface for discovery to begin with.

Both are the same underlying problem wearing different behavior: passive repeat
listening (visible in engagement data as "healthy," per the original segment
rationale) versus active discovery that's simply happening on a competitor's surface
(invisible to Spotify's metrics entirely — arguably worse). The revised segment is:
**engaged listeners — regardless of tenure or plan — who do not currently treat
Spotify as their primary discovery surface**, whether that shows up as staying inside
a narrowing loop or as routing discovery elsewhere and using Spotify only for
playback.

Confirmed cross-cutting, not niche: this pattern appeared in 6/6 interviews across a
deliberately varied set (student, engineer, marketer, designer, student, HR manager;
free and premium; 4-5 hrs/day to background-all-day usage) and independently in Part
1's persona clustering, where the reviews naming this problem skew toward "Longtime
music explorer" / "Premium power listener" / "Music discovery enthusiast" rather than
the casual majority.

**Confidence caveat, stated plainly:** 6 interviews is the minimum the brief asks for,
and tenure/frequency detail wasn't captured for every respondent, so the segment's
exact boundaries (how broad is "broader"?) aren't fully pinned down — this is a
directional revision backed by real evidence, not a precisely re-measured segment.

## Why solving this makes business sense

This problem is real and sizeable but **structurally invisible in the metrics
Spotify already watches** — that invisibility is itself the business case:

- **It hides in engagement data.** A user replaying the same 150 songs for months
  looks identical, in raw listening-time and session-count metrics, to a healthy,
  satisfied user. Nothing in aggregate engagement dashboards would flag this segment
  as at-risk or underserved, which is exactly why it took targeted review analysis
  *and* primary interviews to surface — and why it likely stays unaddressed by default
  without a deliberate initiative like this one.
- **It hides in review data too, mostly.** Only ~11.5% of 858 real analyzed reviews
  (99 reviews) touch discovery/repetition themes at all — people write app-store
  reviews when something breaks or annoys them acutely (ads, crashes), not to report a
  slow behavioral drift they may not have consciously noticed. Interviews closed this
  gap directly: 6/6 respondents articulated the exact pattern once asked, even though
  it's nearly invisible in unprompted review text.
- **It's actively leaking to competitors' engagement surfaces.** 4 of 6 respondents
  described discovering new music primarily through TikTok, Instagram, or friends —
  meaning that discovery activity, and the attention/engagement that comes with it, is
  happening somewhere Spotify gets no credit and learns nothing from. Every one of
  those moments is a chance for a competing platform (or a competing music app) to
  become the actual discovery destination, with Spotify reduced to "the app I search
  once I already know the name."
- **The blockers are addressable without new licensing, new catalog, or new
  infrastructure** — trust/explainability, blunt-signal interpretation, and decision
  effort are all things a conversational, reasoning-capable interface can address
  directly (see [docs/why-ai-mvp.md](why-ai-mvp.md)); this is a product and AI
  investment, not a content-acquisition one, which makes the cost side of this
  business case comparatively small.

## What would change this assessment

- A larger interview sample confirming (or contradicting) how common the
  "bypasses Spotify entirely" sub-pattern is relative to the "narrowing loop"
  sub-pattern — that ratio matters for prioritizing which behavior the MVP should
  target first.
- Real usage data (not self-report) on how often "skip" is actually treated as a
  durable negative signal by the production recommender — P5's claim is a perception,
  worth validating against how the algorithm actually behaves before treating it as
  confirmed fact.
- Reddit/community-forum data, once accessible (see README), to see whether the
  external-platform-bypass finding (TikTok/Instagram as primary discovery) shows up
  independently in more reflective discussion venues, not just these 6 interviews.
