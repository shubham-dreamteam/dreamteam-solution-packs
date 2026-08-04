# Meeting Conversion Funnel

**Access required:** read-only. Objects: `contact`, `meeting`, `deal`.
Do not ask the customer about this. It is declared here so they do not have to answer it.

**Read `api-truth.md` first.** Everything about auth, pagination and the traps lives
there and is not repeated here.

---

## 1. What this solves

Sales leaders ask two questions that the CRM does not answer directly:

**"Where do contacts die?"** Not the stage they end in, but whether they ever got a
real conversation. A contact marked Unqualified after four meetings is a qualification
outcome. A contact marked Unqualified without a single meeting is a prospecting or
routing failure. The CRM shows both as "Unqualified".

**"Where does the funnel actually leak?"** Booked to completed, completed to qualified,
qualified to deal. Each is a different team's problem, and only one of them is usually
the real one.

You will build two linked views.

### View A: contact status by meeting outcome

A matrix. Rows are contact status, columns are meeting outcome, plus a "no meeting"
column. It answers "which of these contacts ever had a conversation".

```
STATUS                TOTAL   MTG DONE   SCHEDULED/PENDING   NO-SHOW   CANCELLED   NO MEETING
New                      12          2                   -         -           -           10
Contacted                41          2                   1         -           -           38
Meeting Booked          114         63                  16        17           1           17
Qualified                 8          7                   -         1           -            -
Opportunity Created      17         17                   -         -           -            -
Unqualified             317        121                   8        34          13          141
```

The headline sits above the table and names the single worst number, for example:
*"141 of 317 Unqualified contacts (44%) were disqualified without ever booking a
meeting."*

### View B: contact to meeting to deal funnel

**Render this as an actual funnel, not a bar chart.** Five stages, each bar
**centre-aligned** and narrowing as counts fall, so the taper is visible at a glance.
Conversion rate sits between consecutive bars, in the gap, because it describes the
transition rather than either stage. Percentage of total goes on the right.

```
        Total contacts   ████████████████████████████████████████   509   100%
                                    60% converted
       Meetings booked        ███████████████████████████           303    60%
                                    70% converted
    Meetings completed           ███████████████████                212    42%
                                    11% converted   <- worst, highlight
             Qualified                  ██                           24     5%
                                    50% converted
     Open deal created                  █                            12     2%
```

Rules that make it read as a funnel:

- **Bar width is proportional to count**, scaled so stage 1 fills the width. A stage
  with 24 of 509 must actually look like a sliver. Do not use a minimum bar width that
  flattens the taper, and do not give every stage its own scale.
- **Centre each bar.** Left-aligned bars read as a progress list, not a funnel.
- **Conversion sits between bars**, not inside or beside them.
- **Highlight the single worst conversion** in a warning colour, and label it. That one
  number is the reason the chart exists.
- A stage of 0 still gets a visible marker, otherwise a total collapse looks like a
  rendering bug.

**Both views must drill.** Clicking any matrix cell, funnel stage or conversion gap
opens the contacts behind that number, with status, owner, meeting count, last meeting
date and a link back to the record in Dreamteam. Clicking a status row cross-filters
the funnel to that status, and vice versa. The design standard has the full
requirements; none of it is optional here, because "141 contacts were dropped without a
meeting" is useless until you can see which 141.

**The two views must reconcile exactly.** Section 6 gives the arithmetic. This is the
single most useful property of this pack: the matrix proves the funnel.

---

## 2. Data you need

| Object | Endpoint | Why |
|---|---|---|
| contacts | `/objects/contact/records` | status, owner |
| meetings | `/meetings` | outcome, contact links |
| deals | `/objects/deal/records` | final funnel stage |

Note the two endpoint families use **different pagination conventions**. See
`api-truth.md` section 2. Getting this wrong here is especially damaging, because your
numerator and denominator would come from different slices of the data and the
percentages would still look plausible.

---

## 3. Discover

Run these before writing any logic.

**Contact status field.** `GET /api/v1/objects/contact`

Look for `contact_activity_status`, type `DROPDOWN`. On a default tenant its options
are exactly:

```
New, Contacted, Meeting Booked, Qualified, Opportunity Created, Unqualified
```

Use the options this tenant returns, in the order returned. Do not hardcode the list
above. Tenants can override standard fields.

If `contact_activity_status` does not exist, look for another `DROPDOWN` field whose
options describe a lifecycle. If there is none, stop and tell the user this solution
needs a contact status field.

**Meeting fields.** `GET /api/v1/objects/meeting`

You will find: `title`, `start_at`, `end_at`, `meeting_url`, `recording_url`,
`contact_ids`, `transcript`, `ai_meeting_summary`, `ai_sentiment`, `external`,
`user_id`, `bot_id`.

**You will not find a meeting outcome field. There isn't one.** Read section 4.

**Deal fields.** `GET /api/v1/objects/deal`

You need `contact_ids`, `status`, `amount`, `stage_id`, `pipeline_id`.

---

## 4. Map: deriving meeting outcome

**This is the hard part of this pack and the part most likely to be got wrong.**

Dreamteam does not store a meeting outcome. There is no `status` field on a meeting,
no "completed", no "no-show", no "cancelled". Any tool showing those buckets is
deriving them. You must derive them too, and you must be explicit with the user about
how.

### The signals available

**Completion evidence.** A meeting genuinely happened if it produced an artefact:

```
transcript is non-empty  OR  recording_url is present  OR  ai_meeting_summary is non-empty
```

**Time.** `start_at` relative to now.

**Bot telemetry.** The `/meetings` endpoint returns a `recording_bot` object that
`/objects/meeting/records` does not:

```json
{"state":"ATTACHED","status":"DONE","scheduled_join_at":"2026-07-18T05:30:00Z",
 "reason":"bot_kicked_from_waiting_room","can_attach":false,"can_detach":false}
```

Observed values, from a live tenant's 185 meetings:

| state / status / reason | Count | What it means |
|---|---|---|
| `NOT_APPLICABLE` / `PAST_START` | 89 | meeting imported after it happened, backfill. **No outcome signal.** |
| `NOT_APPLICABLE` / `INTERNAL_MEETING` | 40 | all attendees internal, bot skipped by design |
| `ATTACHED` / `DONE` / `timeout_exceeded_waiting_room` | 28 | bot joined, host never admitted it. Meeting likely happened, not captured. |
| `NOT_APPLICABLE` / `NO_MEETING_URL` | 13 | no conferencing link, in person or personal event |
| `ATTACHED` / `TRANSCRIPT_DONE` / `timeout_exceeded_everyone_left` | 5 | captured successfully, meeting definitely happened |
| `ATTACHED` / `DONE` / `bot_kicked_from_waiting_room` | 5 | bot actively removed. Meeting happened. |
| `ATTACHED` / `PENDING` | 2 | scheduled, bot will join |

**Critical: `recording_bot` describes the bot, not the meeting.** A missing recording
does not mean a missing meeting. In the tenant above, 89 of 185 meetings carry
`PAST_START`, meaning they were imported after the fact and the bot never had a chance
to join. Treating those as "no-show" would be wrong for roughly half the dataset.

### The recommended derivation

```
COMPLETED         start_at < now AND completion evidence present
SCHEDULED/PENDING start_at >= now
                  OR (start_at < now AND no completion evidence)   <- label "Pending Review"
NO-SHOW           not derivable from standard fields
CANCELLED         not derivable from standard fields
NO MEETING        contact appears in no meeting's contact_ids
```

Note what "Scheduled/Pending" really contains: genuinely upcoming meetings **and**
meetings whose date has passed with no outcome logged. Those are different things and
users will misread the column unless you say so. Put a line under the table:

> *"Scheduled/Pending includes meetings whose date has already passed with no outcome
> logged yet (Pending Review), not only genuinely upcoming ones."*

### No-show and cancelled

These cannot be derived from standard fields. Before building, ask the user:

> *"Dreamteam doesn't store no-show or cancelled as a meeting outcome. Do you track
> those somewhere, for example a custom field on the meeting, a note convention, or
> your calendar provider? If not, I'll leave those columns out rather than guess."*

**Leaving the columns out is the correct behaviour if there is no source.** Do not
infer no-show from a missing recording. As the table above shows, that would
misclassify backfilled meetings, internal meetings, and every meeting where the host
simply did not admit the bot.

If the tenant does have a custom field, discover its options and map them.

---

## 5. Compute

### View A, the matrix

For each contact, resolve exactly one outcome bucket using this precedence, so every
contact is counted once and the row sums to TOTAL:

1. No meetings linked at all → **NO MEETING**
2. Any meeting classified COMPLETED → **MTG DONE**
3. Otherwise, any meeting classified CANCELLED → **CANCELLED**
4. Otherwise, any meeting classified NO-SHOW → **NO-SHOW**
5. Otherwise → **SCHEDULED/PENDING**

A contact with three meetings where one completed counts as MTG DONE, once. The columns
are mutually exclusive by construction. Verify: every row must satisfy
`TOTAL = MTG DONE + SCHEDULED/PENDING + NO-SHOW + CANCELLED + NO MEETING`.

Linking contacts to meetings uses `meeting.contact_ids`, a LOOKUP array. One meeting can
reference several contacts, and each of them counts.

### View B, the funnel

Each stage counts only contacts that passed the previous stage. This is a strict funnel,
not five independent counts.

| Stage | Definition |
|---|---|
| Total contacts | all contacts |
| Meetings booked | contacts with at least one linked meeting, any outcome |
| Meetings completed | contacts with at least one COMPLETED meeting |
| Qualified | contacts with a completed meeting **and** status in {Qualified, Opportunity Created} |
| Open deal created | those contacts linked to at least one deal in a stage where `is_closed` is false |

**The Qualified stage is conditional and this matters.** It is not "all contacts whose
status is Qualified". It is "contacts who got a real conversation and then qualified".
The difference is the point of the whole chart: it isolates conversion *given* a
meeting, rather than blending in contacts that qualified without one.

Conversion rate on each row is `stage / previous stage`, not stage over total. Show
percentage of total separately on the right.

### Determining whether a deal is open

**Do not use `deal.status`. It is not a lifecycle field.**

This was got wrong in a real build. `status` is free text and on a live tenant every one
of 52 deals held the value `"Red Flag"`, an AI risk annotation. The app read the distinct
values, found one, treated it as "open", and reported a meaningless zero.

Open and closed live on the **stage**, not the deal:

```
GET /api/v1/pipelines/{pipeline_id}
  -> { "id": ..., "name": ..., "stages": [
         {"name": "Qualified",      "is_closed": false},
         {"name": "Evaluation",     "is_closed": false},
         {"name": "In Pilot Phase", "is_closed": false},
         {"name": "Negotiation",    "is_closed": false},
         {"name": "Won",            "is_closed": true},
         {"name": "Lost",           "is_closed": true} ] }
```

A deal is open when the stage matching its `stage_id` has `is_closed: false`.

The stage also carries `stage_category` (`Early Stage`, `Mid-Level Stage`, `Late Stage`,
`Closed Won`, `Closed Lost`), `stage_order` and `win_probability`. If you need to tell a
won deal from a lost one, use `stage_category`. **`is_closed` is true for both**, so it
cannot distinguish them, and matching on the stage name is unreliable because names are
tenant-specific.

**Trap: the list endpoint omits stages.** `GET /pipelines` returns pipelines with no
`stages` key at all. You must fetch each pipeline individually by id to get them.
`GET /pipelines/{id}/stages` and `GET /stages?pipeline_id=` both 404, so the single
pipeline fetch is the only route.

**Trap: resolve against the deal's own pipeline.** Tenants can have several pipelines
and a deal's `stage_id` only means something within its own `pipeline_id`. On the tenant
above, one deal carried a `stage_id` absent from the default pipeline's six stages.
If a `stage_id` does not resolve, count it as unknown and surface the count. Do not
silently treat it as open or closed.

Stage names are tenant-specific. Never match on the string "Won" or "Closed". Use the
`is_closed` boolean.

---

## 5b. Further metrics

Views A and B answer "where do contacts die". These answer *why*, and every one is
derivable from fields already verified on a live tenant. Build the ones the tenant has
data for and say plainly which you skipped.

**Follow `design.md` for every form below.** Each entry names its form because the form
follows the data's job, not preference.

### Core, build these

**1. Time to first meeting.**
`contact.created_at` to the earliest `start_at` among its linked meetings. Report the
median as a stat tile, and the spread as a column chart bucketed by days: same day,
1-3, 4-7, 8-14, 15-30, 30+.
*Why it matters:* the funnel says how many convert. This says how long they wait, and
speed to first conversation is usually the most actionable lever a team has.

**2. Cohort funnel.**
Group contacts by `created_at` month, run the whole of View B within each cohort, and
render as a **heatmap**: rows are cohorts, columns are funnel stages, cell is the
conversion into that stage. One sequential hue, light to dark.
*Why it matters:* this is the fix for View A being a snapshot. A blended funnel mixes
contacts from different eras and hides whether things are improving. If the most recent
cohorts are lighter, the problem is getting worse right now.

**3. Funnel by source.**
`contact.source` is a standard dropdown: Email, Meeting, CRM Form, Front Office
Assistant, Website Form, Outbound, Others. Seven values sits at the ceiling for
categorical colour, so render this as a **table** with a thin inline bar per row, not a
seven-colour chart. Columns: contacts, booked, completed, qualified, and the
completed-to-qualified rate.
*Why it matters:* it separates volume from quality. A channel producing many contacts
and no qualified meetings is costing money twice.

**4. Funnel by owner.**
Same shape as source, joining `owner_id` to `/api/v1/users`. Table, sorted by the
completed-to-qualified rate. Use **emphasis**, not categorical colour: highlight rows
materially below the team median in the accent, leave the rest in neutral ink.
*Why it matters:* it distinguishes a pipeline problem from a person problem.

**5. Status against reality.**
Count contacts whose `contact_activity_status` implies a meeting happened but which
have no linked meeting at all. Stat tile with the count and share.
*Why it matters:* on a live tenant, 262 of 274 contacts marked "Meeting Booked" had no
meeting attached. Either the CRM is being updated by hand and drifting, or the calendar
integration is not attached. Both are worth knowing before anyone trusts the funnel.
Check your `contact_ids` join first, because a broken join looks identical.

### Build if the data supports it

**6. Meetings before qualifying.**
For contacts that reached Qualified or Opportunity Created, count completed meetings
before they got there. Median as a stat tile, distribution as a small column chart.
*Why it matters:* it sizes the real cost of a win and exposes teams stuck in
never-ending discovery. Needs a reasonable number of qualified contacts to mean
anything; below about 20, show the raw numbers instead of a median.

**7. Sentiment against outcome.**
`meeting.ai_sentiment` holds Good, Neutral or Bad. Cross it with whether the contact
later qualified. Render as a **diverging stacked bar centred on Neutral**, since this
is an ordered scale, not three unrelated categories.
*Why it matters:* it tests whether the AI read of the room predicts anything. If Good
meetings do not convert better than Bad ones, either the signal is noise or something
downstream is losing deals that went well. Both are findings.
Only build this if `ai_sentiment` is populated on a decent share of meetings. Check
first and say so if it is sparse.

**8. Meeting capture rate.**
From the `/meetings` endpoint, `recording_bot` carries `state`, `status` and `reason`.
Group into: captured, bot joined but never admitted, not applicable by design, and
pending. Render as a single horizontal **stacked bar** with a 2px surface gap between
segments.
*Why it matters:* on one tenant, 33 meetings had the bot attached and sitting in a
waiting room it was never admitted to. That is an enablement gap, not a product fault,
and it is invisible in every other view. Read the `recording_bot` table in section 4
before assigning buckets, and never treat a missing recording as a missing meeting.

**9. Pipeline value per completed meeting.**
Sum `deal.amount` for deals linked to contacts with a completed meeting, divided by the
number of completed meetings. Hero figure.
*Why it matters:* it is the one number that connects meeting activity to money, which
is the language the person reading this dashboard actually thinks in. Say plainly that
it is an average over a period and not a forecast. If `amount` is sparsely populated,
show the populated share next to it or omit the metric.

### Not derivable, do not fake

- **No-show and cancelled rates.** No source field. See section 4.
- **Stage or status history.** Records carry current values only, so you cannot show
  how long a contact sat in a status, or reconstruct its path. The cohort heatmap is
  the closest honest substitute.
- **Meeting duration actually used.** `start_at` and `end_at` are the scheduled window,
  not attendance. Do not present scheduled length as time spent.

## 6. Verify

**The two views cross-check each other exactly. Assert all four of these before
rendering. If any fails, you have a bug, most likely pagination.**

```
Funnel "Total contacts"      == sum of the matrix TOTAL column
Funnel "Meetings booked"     == total contacts - sum of the NO MEETING column
Funnel "Meetings completed"  == sum of the MTG DONE column
Funnel "Qualified"           == MTG DONE for the Qualified row + MTG DONE for the
                                Opportunity Created row
```

Worked example from a real tenant, showing all four holding:

```
TOTAL column:        12 + 41 + 114 + 8 + 17 + 317  = 509   -> Total contacts 509
NO MEETING column:   10 + 38 +  17 + 0 +  0 + 141  = 206   -> 509 - 206 = 303 booked
MTG DONE column:      2 +  2 +  63 + 7 + 17 + 121  = 212   -> Meetings completed 212
Qualified rows:                        7 + 17      =  24   -> Qualified 24
```

Also assert, per `api-truth.md`: every fetched collection's row count equals the
reported total. Display "212 of 212 meetings" style counts in the UI so truncation is
visible rather than silent.

---

## 7. Traps

**Pagination convention differs between the two endpoints you need here.** `/meetings`
is 0-indexed and uses `size`. `/objects/*/records` is 1-indexed and uses `page_size`.
Use the wrong one and you get a clean-looking response with a fraction of the rows, and
your funnel percentages will be confidently wrong. This is the single most likely cause
of a mismatch in section 6.

**`recording_bot` is about the bot, not the meeting.** Never treat a missing recording
as a missing meeting. In the sample tenant, 48% of meetings had no bot signal at all
because they were imported after the fact.

**Do not invent no-show or cancelled.** If there is no source field, omit the columns
and say why in the UI. A missing column is honest. A guessed column becomes a metric
someone manages their team against.

**The "Scheduled/Pending" column is two different things.** Genuinely upcoming, and
past-dated with no outcome. Label it, or users will read a stale-data problem as a
healthy pipeline.

**Status is a point-in-time value, not history.** `contact_activity_status` tells you
where a contact is now, not the path it took. A contact currently Unqualified that had
a completed meeting was not necessarily Unqualified when the meeting happened. Do not
describe this chart as showing progression over time. It is a snapshot.

**A contact can link to several meetings.** Count contacts once using the precedence
in section 5, or your columns will sum to more than the row total.

**Empty is not zero.** If a fetch fails, an error object has no `results` key and naive
code renders 0. Show an error state instead. A funnel of zeros looks like a business
problem and will be reported as one.

**A status of "Meeting Booked" does not mean a meeting exists.** On a live tenant, 262
of 274 contacts in that status had no linked meeting at all. That is a real finding
about their process, not a bug in your join, so surface it rather than hiding it. But
check your `contact_ids` matching first, because a broken join looks identical.

**`deal.status` is not open or closed.** See section 5. Every deal on the tenant tested
carried `"Red Flag"`. Use the stage's `is_closed` flag.
