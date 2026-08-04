# Forecasting

**Access required:** read-only. Objects: `deal`, `pipeline`, `user`, optionally
`company` and `target`.
Do not ask the customer about this. It is declared here so they do not have to answer it.

**Read the Dreamteam API reference first.** Auth, pagination and the traps live there and
are not repeated here. Read the design standard too: every number below must drill to the
deals behind it.

---

## 1. What this solves

Three questions a sales leader asks every week, which a CRM list view cannot answer:

**"What are we going to close?"** Not the sum of open deals, which is a fantasy. A
weighted number, with the assumptions visible so they can be argued with.

**"Will we make the number?"** Coverage, gap to target, and what would have to happen.

**"Which deals decide it?"** The handful whose slip changes the quarter, separated from
the long tail that does not matter.

Most forecast dashboards fail by presenting one number with no way to see what is inside
it. The number is not the product. **The number plus the ability to interrogate it** is
the product.

---

## 2. Discover first

Never assume. Run these before any logic.

**The pipeline and its stages.** `GET /api/v1/pipelines` lists pipelines, but returns
them **without stages**. You must fetch each one individually:

```
GET /api/v1/pipelines/{id}
  -> stages: [ { id, name, stage_order, stage_category, win_probability, is_closed,
                 entry_criteria, external_id } ]
```

A real default pipeline looks like this:

```
order  name            stage_category     win_probability  is_closed
1      Qualified       Early Stage        10               false
2      Evaluation      Mid-Level Stage    50               false
3      In Pilot Phase  Late Stage         70               false
4      Negotiation     Late Stage         90               false
5      Won             Closed Won         100              true
6      Lost            Closed Lost        0                true
```

Everything in section 4 depends on these four fields. Read them, do not hardcode them.
Stage names, counts, orders and probabilities are all tenant-specific.

**`GET /api/v1/objects/deal`** for the field schema. Note `probability`, `amount`,
`expected_close_date`, `close_date`, `stage_id`, `pipeline_id`, `owner_id`,
`forecast_category`, `momentum`, `risk`, `confidence`, `multi_threading`,
`stage_mismatched?`, `ai_recommended_stage`, `won_reason`, `lost_reason`.

**`GET /api/v1/users`** to turn `owner_id` into names and roles.

**`GET /api/v1/targets`** for quota, if the tenant uses it. **This endpoint is on the
`/meetings` pagination family**, so it is 0-indexed and uses `size`, not `page_size`,
and returns rows under `content`. On a live tenant it returned zero rows, so treat
targets as optional: if empty, drop every coverage and attainment metric rather than
inventing a quota, and say in the interface that no target is set.

---

## 3. Open, won and lost

**`is_closed` does not tell you whether a deal was won.** It is true for both Won and
Lost. Getting this wrong inverts the entire forecast.

```
stage_category = "Closed Won"    -> won
stage_category = "Closed Lost"   -> lost
is_closed = false                -> open, counts toward forecast
```

Match on `stage_category`, not on the stage name. Names are tenant-specific and
translated; "Won" is not a reliable string.

If `stage_category` is missing on a tenant, fall back to `external_id`
(`default_stage_closed_won` / `default_stage_closed_lost`), then to `win_probability`
of 100 versus 0. Say in the interface which rule you used.

**Resolve `stage_id` against the deal's own `pipeline_id`.** Multiple pipelines can
exist and a stage id only means something inside its own. On a live tenant one deal
carried a stage id absent from the default pipeline's stages. Count unresolved deals,
show the count, and exclude them from the forecast rather than guessing.

---

## 4. The math

Precision matters here more than anywhere else in this catalogue. A wrong forecast is
acted on.

### 4.1 Which probability to use

Two exist and they can disagree:

- `stage.win_probability`, from the pipeline definition
- `deal.probability`, an optional per-deal override

**Rule: use `deal.probability` when it is set, otherwise the stage's
`win_probability`.** State which one each deal used in the drill view, and show a count
of overridden deals. A rep who has manually set 90% on a Qualified deal is making a
claim, and the forecast should let a leader see that rather than bury it.

Both are percentages, 0 to 100. Divide by 100 before multiplying.

### 4.2 The core numbers

Compute over **open deals only** unless stated. Open means `is_closed` is false.

```
Open pipeline        = Σ amount                              over open deals
Weighted pipeline    = Σ (amount × probability / 100)        over open deals
Closed won           = Σ amount   where stage_category = "Closed Won"
                                  and close_date falls in the period
Closed lost          = Σ amount   where stage_category = "Closed Lost"
                                  and close_date falls in the period
Forecast             = Closed won (actual) + Weighted pipeline (expected)
```

**Closed won uses `close_date`, not `expected_close_date`.** `close_date` is what
happened; `expected_close_date` is what someone hoped. Mixing them double-counts.

### 4.3 Period filtering, the part most dashboards get wrong

Three different date fields answer three different questions:

| Question | Filter on |
|---|---|
| What closed this quarter? | `close_date` within the period, and closed |
| What is expected to close this quarter? | `expected_close_date` within the period, and open |
| What was created this quarter? | `created_at` within the period |

**Never mix them in one number.** A "Q3 pipeline" built from deals created in Q3 plus
deals closing in Q3 counts some deals twice and is meaningless. Put the date field you
filtered on in the interface, next to the date picker.

Open deals with an `expected_close_date` in the **past** are not in the future forecast
and not in closed. They are slipped, section 4.6. Never silently roll them forward.

### 4.4 Coverage and gap, only if a target exists

```
Remaining target   = target − closed won in period
Coverage ratio     = open pipeline / remaining target
Weighted coverage  = weighted pipeline / remaining target
Gap                = remaining target − weighted pipeline
```

Coverage of 3x is the usual rule of thumb, but it is a rule of thumb and not a fact
about this business. Show the ratio, do not colour it against a threshold you invented.

If `/targets` is empty, omit this whole section. Do not derive a target from history and
present it as a target.

### 4.5 Win rate, by count and by value

These differ, often a lot, and quoting one without the other misleads.

```
Win rate (count) = won deals / (won + lost)          closed deals only
Win rate (value) = won amount / (won + lost amount)  closed deals only
```

**Open deals never appear in a win rate.** Including them drags the rate toward zero
and makes it drift as pipeline grows.

The denominator is closed deals in the period, by `close_date`. Report the denominator
next to the rate. A 67% win rate on three deals is not a fact.

### 4.6 Slippage

```
Slipped = open AND expected_close_date < today
```

Report the count, the value, and the median days overdue. This is usually the most
actionable view on the page: it is pipeline the forecast is quietly still counting that
has already missed its date.

If the tenant populates `expected_close_date` sparsely, say what share is missing. A
slippage view over 20% coverage is not a view.

### 4.7 Sales cycle

```
Cycle days = close_date − created_at, for won deals only
```

Report the **median**, not the mean. Deal cycles are right-skewed and one 400-day
enterprise deal moves a mean and tells you nothing. Show the interquartile range beside
it.

Losses are excluded deliberately: a lost deal's cycle measures how long you took to give
up, which is a different question. Offer it as a separate number if the customer wants
it, labelled as such.

### 4.8 Stage conversion

For each stage in `stage_order`, the share of deals that ever reached the next stage.

**Honest limitation: Dreamteam stores current stage, not stage history.** You cannot
observe a deal's path. What you can compute is a snapshot approximation: of closed
deals, the share that ended at or beyond each stage. Label it exactly that way. Do not
present it as a historical progression, and do not compute "time in stage", because the
data to do so does not exist.

---

## 5. The views

Follow the design standard for form and colour. Every one of these drills.

### 5.1 Lead with the headline

A hero figure: the weighted forecast for the period. Beneath it in one plain sentence,
the composition. *"£412k forecast: £180k already closed, £232k weighted from 34 open
deals."*

If a target exists, a second line: gap and coverage. If not, say no target is set.

**Clicking the hero figure opens every deal in it**, with amount, probability, stage,
owner and expected close date, sorted by weighted value descending.

### 5.2 Forecast composition

A **horizontal stacked bar**: closed won, then weighted contribution by stage category
(Early, Mid-Level, Late). One sequential hue, darkening toward Late, because these are
ordered. 2px surface gap between segments.

This shows at a glance whether the number rests on late-stage deals or on early-stage
optimism. Each segment drills.

Add `deal.forecast_category` (Committed, Best-case, Pipeline) as an **alternative view
behind a toggle, not the default**. On a live tenant this field was null on 51 of 52
deals. Check its populated share first, and if it is under about half, hide the toggle
and say why rather than showing a chart that is 98% "unset".

### 5.3 Pipeline by stage

A **column chart** ordered by `stage_order`, value on the axis, deal count as a label.
Sequential hue.

Two toggles: raw value versus weighted value. The gap between them is the story, and
seeing both is what makes a forecast arguable rather than announced.

### 5.4 Deals that decide the quarter

A **table**, sorted by weighted value descending, top 10 to 20. Columns: deal, account,
owner, amount, probability, weighted, stage, expected close, momentum, risk.

Use **emphasis** rather than categorical colour: accent only the rows that are both
large and at risk. Everything else in neutral ink.

This is usually the most used view on the page. Make it sortable on every column and
make every row drill to the deal.

### 5.5 Slippage

A **column chart** of overdue buckets: 1-7 days, 8-30, 31-90, 90+. Plus a stat tile with
total slipped value.

Use status colour here, not categorical, because this genuinely means "bad". Ships with
a label, never colour alone.

### 5.6 Forecast by owner

A **table**, one row per owner, sorted by weighted value. Columns: open count, open
value, weighted, closed won, win rate by count, win rate by value. Target and attainment
only if targets exist.

Emphasis on the outliers, not a colour per person. Twelve owners is twelve rows, not
twelve hues.

### 5.7 Health signals

Dreamteam populates several judgement fields. Cross-tabulate them against value, as a
small **heatmap** or a set of stat tiles:

- `momentum`: Accelerating, Steady, Stalled, Regressing
- `risk`: High, Medium, Low
- `confidence`: High, Medium, Low
- `multi_threading`: Single-thread, Emerging multi-thread, Effective multi-thread

The single most useful cut: **weighted value sitting in Single-thread deals**. One
contact is one resignation away from a lost deal, and this is the number that makes that
concrete.

`momentum` and `multi_threading` are ordered scales, so use a sequential ramp, not
categorical hues.

### 5.8 Forecast hygiene

Dreamteam computes `ai_recommended_stage` and `stage_mismatched?`. Show:

- Count and value of deals where `stage_mismatched?` is true, with
  `ai_recommended_stage_rationale` visible in the drill.
- Deals missing `amount`, missing `expected_close_date`, or with no `next_activity_date`.
- Deals with no activity in 30 days, from `last_activity_date`.

Present as a checklist of counts, each drilling to the offending deals. This is the view
that gets the underlying data fixed, which improves every other number on the page.

### 5.9 Why we lose

Group closed-lost deals by `lost_reason`. **Table with inline bars**, count and value.
`lost_reason` is free text, so show the distinct values as they are and do not attempt
to bucket them into categories you invented. If it is sparsely populated, say so.

---

## 6. Verify

Assert these before rendering. Any failure means a bug, most likely pagination.

```
open + won + lost                  == total deals fetched
                                      (plus unresolved-stage count, reported separately)
Σ stage values                     == open pipeline
weighted pipeline                  <= open pipeline          always
closed won + closed lost            == closed deals in period
row count                          == metadata.total_elements   for every fetch
```

`weighted <= open` is the cheapest sanity check you have. If weighted exceeds raw, a
probability is being read as a fraction somewhere, or a closed deal has leaked in.

Show "52 of 52 deals" style counts in the interface, plus the count of deals excluded
for a missing `amount`. An excluded deal is invisible otherwise, and a forecast missing
its largest deal is worse than no forecast.

---

## 7. Traps

**`is_closed` is true for Lost as well as Won.** Section 3. This is the one that inverts
the forecast.

**`forecast_category` is largely unpopulated.** 51 of 52 null on a live tenant. Check
before building a view on it.

**`amount` may be null.** Excluding silently understates the forecast. Count and display
the exclusions.

**`probability` may be null**, in which case the stage's `win_probability` applies. Never
default a null probability to zero, and never to 100.

**Do not mix date fields.** Section 4.3.

**Do not roll slipped deals forward.** An open deal with a past expected close is a
problem to surface, not a rounding error to absorb into next month.

**Win rate must exclude open deals.** Section 4.5.

**Do not present stage conversion as history.** No stage history exists. Section 4.8.

**Two pagination conventions.** `/objects/deal/records` is 1-indexed with `page_size`;
`/targets` is 0-indexed with `size`. Mixing them silently truncates one side, and a
forecast built on 20 of 196 deals looks entirely plausible.

**Never present a weighted forecast as a commitment.** Label it, and show the assumption
that produced it. The whole point is that a leader can disagree with the number and see
exactly which deal to argue about.
