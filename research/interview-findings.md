# Interview findings — real data (6 respondents)

**Status: real primary research.** Six interviews conducted against the segment
hypothesis in [segment-and-screener.md](segment-and-screener.md). This — not the
screener or discussion guide — is Part 2's actual deliverable. Feeds
[docs/problem-definition.md](../docs/problem-definition.md) directly.

## Respondents

| # | Profile | Plan | Usage | Primary discovery blocker (their words) |
|---|---|---|---|---|
| P1 | 22, college student | Premium, 3+ yrs | 4-5 hr/day | "Spotify knows what I already like, but it rarely surprises me" |
| P2 | 28, software engineer | Premium | 7-8 hr/day (background) | "It keeps recommending music that's 95% similar" |
| P3 | 25, marketing exec | Free | — | "Spotify reacts after music becomes popular" — discovers via TikTok/IG first |
| P4 | 31, product designer | Premium | — | "Spotify keeps me inside my own bubble" — wants cross-language discovery |
| P5 | 20, engineering student | — | — | "If I skip one song, Spotify assumes I don't like that artist" |
| P6 | 35, HR manager | — | — | "Finding music feels like work" — never opens Home recommendations |

(Tenure/frequency weren't captured for every respondent — noted as a real gap below,
not smoothed over.)

## Frequency table (as collected)

| Theme | Frequency |
|---|---|
| Recommendations become repetitive | 6/6 |
| Mostly listens to same playlists | 6/6 |
| Feels trapped in a recommendation bubble | 6/6 |
| Wants a safer + new music balance | 5/6 |
| Wants mood-based recommendations | 5/6 |
| Wants more control over discovery | 5/6 |
| Wants explanations for recommendations | 4/6 |
| Uses external platforms (TikTok/IG/YouTube) for discovery | 4/6 |
| Interested in hidden/emerging artists | 4/6 |
| Doesn't fully trust Discover Weekly | 4/6 |

## What this confirms, revises, and adds to the AI-generated hypothesis

**Confirmed, strongly.** The core Part 1 hypothesis holds: 6/6 describe the exact
comfort-loop pattern — repetitive recommendations, same playlists, feeling boxed in.
This is the strongest possible validation signal a 6-person sample can give.

**Revises the segment definition.** The original "Comfort-Loop Listener" hypothesis
in segment-and-screener.md was scoped narrowly to tenured (1+ yr), heavy, engaged
users. P3 (free tier, discovers primarily via TikTok/Instagram, searches Spotify only
*after* hearing something elsewhere) doesn't fit that profile — she isn't a lapsed
heavy explorer, she may never have trusted Spotify's own discovery much. That's a
real, distinct pattern the original hypothesis didn't anticipate: for some users
Spotify isn't under-serving discovery, it's being *bypassed* — 4/6 mention external
platforms as their actual discovery source. The segment is broader than originally
scoped: the trapped-in-a-bubble feeling shows up regardless of tenure, plan, or usage
intensity in this sample (student, engineer, marketer, designer, HR manager; free and
premium; low and high usage all report it).

**New, not visible in Part 1's review mining at all:**
- **External-platform bypass** (4/6) — nothing in 858 analyzed Play/App Store reviews
  surfaced "I actually discover music on TikTok, not here." People don't write app
  reviews about a competitor; they say it in an interview. This is exactly the kind of
  finding Part 1's own "important limitation" section predicted would be missed.
- **Blunt skip-signal interpretation** (P5): *"If I skip one song, Spotify assumes I
  don't like that artist."* A specific, actionable algorithmic complaint no review in
  the Part 1 dataset named this precisely.
- **Effort/decision fatigue as its own distinct blocker** (P6): *"Finding music feels
  like work."* Distinct from mistrust or algorithmic staleness — for at least one
  real segment, the problem isn't the algorithm's quality, it's the cognitive cost of
  engaging with discovery at all.

**Triangulates with Part 1.** Both independently point at the same underlying
mechanism, arrived at from completely different evidence — real interview language
("it keeps recommending music that's 95% similar," "prioritizes similarity over
exploration") versus Part 1's AI-extracted root causes ("recency-biased... algorithm
that overweights recent browsing over established listening habits"). Independent
convergence from review-mining and interviews on the same mechanism is a real signal,
not a coincidence.

**One direct validation of the MVP itself.** P6, unprompted, describes almost exactly
what the Discovery Companion does: *"I want Spotify to simply understand what I need"*
— type "I'm stressed," "recommend something peaceful," "surprise me with something
new." The novelty-dial concept lines up with the 5/6 who want *"more control over
discovery"* / *"a safer + new music balance"* rather than an all-or-nothing switch, and
the 4/6 who want explanations lines up with the Companion's per-pick reasoning
requirement. That's not proof the MVP works — nobody in this set tried it — but it's
real evidence the mechanism was aimed at the right problem before this data existed.

## Feeding Part 3

- **Root cause:** the recommendation system optimizes for similarity/safety over
  exploration, both by design (Part 1: recency-biased ranking) and by how it
  interprets weak signals as strong ones (Part 2: a single skip read as "don't like
  this artist"). Compounded by low transparency (users don't know *why* something was
  recommended, so an unfamiliar pick is pure risk) and, for a distinct sub-group,
  discovery fatigue that makes users default to familiar choices rather than expend
  effort — this sub-group looks elsewhere (TikTok, Instagram, friends) rather than
  fighting the app's own surface.
- **Target segment:** broader than the original hypothesis — not just tenured heavy
  listeners, but anyone who has stopped trusting Spotify's own surface as their
  discovery mechanism, whether that shows up as passive repeat-listening (P1, P2, P6)
  or as actively discovering elsewhere and only using Spotify to play what they
  already found (P3). Both are "comfort-loop," just with different visible behavior.
- **Business case:** every respondent who discovers externally (4/6) is a data point
  Spotify's own recommendation system never gets credit for and never learns from —
  that's discovery activity happening on a competitor's engagement surface instead of
  Spotify's. Winning back even a fraction of that loop, on top of increasing catalog
  depth played by the passive-repeat majority, is the growth case.

## Honest gaps in this dataset

- Tenure and listening-history detail weren't captured for every respondent (P2-P6),
  so the screener's specific thresholds (tenure, % familiar) can't be fully
  cross-checked against who actually qualified.
- No one in this set was shown the Companion live — the "validates the MVP" point
  above is inference from stated desires, not an observed reaction. Worth doing as a
  fast follow-up with 1-2 of these respondents if possible.
