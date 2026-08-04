You are going to build an application on top of Dreamteam CRM data.

Everything you need is in this message. Do not try to fetch any URL. If you have no
web access, that is fine and expected.

## STOP. Do not write any code yet.

Ask me the questions below first, and wait for my answers. Do not scaffold a project,
do not create files, do not "start with a basic version".

## Ask me these questions

**Q1. Which solution do you want to build?**
List the names from the catalogue further down this message, under
"Available solutions", plus "something else".
[If I pick "something else", use only the API reference and design
standard at the end of this message.]

**Q2. Who is allowed to sign in?**
  a) Whatever sign-in my platform already has (recommended)
  b) Only people who exist in Dreamteam
  c) No sign-in, private link only

[Only if I pick (b): in one or two sentences, tell me it needs an auth provider that
returns a verified email claim, such as Google or Microsoft OAuth. Then carry straight
on with (b). Do not say any of this before I have chosen, and do not ask the question
again.]

**Q3.** [only if I chose 2b] **What should each person see?**
  a) Everyone sees all data
  b) Admins see everything, everyone else sees only their own records

Do **not** ask me what objects the app may touch, or whether it should be read-only.
The chosen solution declares the access it needs, and most are read-only. Ask about
writing back only if what I described is genuinely ambiguous about it, and then ask it
as one plain question, once.

Then ask me for three things:
  - **The web address I use for Dreamteam**, for example
    `https://acme.dreamteamcrm.ai`. Extract the workspace name from it yourself and
    confirm it back to me. Do not ask me for a "tenant slug".
  - **My API key.** If I do not have one, tell me exactly this: in Dreamteam, click the
    profile icon in the top right, choose View Profile, scroll to the API Token section
    at the bottom, then click Reveal and Copy. Do not send me to a documentation page,
    the key is not in one.
  - **My company website**, so you can match the app to our brand. See rule 5.

## Non-negotiable build rules

**1. The API key lives on the server.**
The application must have a server-side route that holds the key and calls Dreamteam.
The browser calls only your own routes, never Dreamteam directly.

This is not a preference. Dreamteam's API rejects browser requests from any origin
outside `*.dreamteamcrm.ai` at CORS preflight, before the key is even checked. A
client-side fetch will not work. It would also ship an org-wide key to every visitor.

If you are building in Lovable, put the Dreamteam calls in a Supabase edge function.
If you are building in v0 or Next.js, use route handlers. If your platform cannot run
server-side code, stop and tell me, because this cannot be built safely there.

**2. Paginate correctly, and prove it.**
The two Dreamteam list APIs use opposite conventions and neither errors when you get it
wrong. You will silently receive a fraction of the data and everything will look fine.
The API reference at the end of this message has the exact rules. Follow them, and assert your row count against the
reported total before rendering anything.

**3. Discover the schema before assuming it.**
Call the describe endpoint for each object and use the field names that tenant actually
has. Never hardcode a field name or a pipeline stage from an example.

**4. Build what the API can do.**
If Dreamteam's API supports it, the app may do it. Do not restrict the application
beyond what the chosen solution asks for. If it says read-only, stay read-only. If
it declares writes, build them properly.

**5. Take the branding from my website, and nowhere else.**
Fetch the company website I gave you and pull the design language from it: logo, colour
palette, typography, spacing and general feel. Also read what the company actually does,
what it sells and who it sells to, and use that so the app reads as our internal tool
rather than a generic dashboard.

Only from the site I gave you. Do not search for us, do not use a similarly named
company, and do not invent a brand. If something is not on the site, you do not know it.

**If you cannot pull anything usable from that site**, whether because you have no web
access, the site blocks you, or there is nothing there, say so plainly and then fall
back to: **Inter** as the typeface, a neutral palette, and **both light and dark mode**.
Retry once with a different fetch method before concluding this, same as Step 1.
Do not guess at our colours. When you do have the brand, still produce a light and a
dark variant of it.

You are probably running somewhere without web access, since that is why you
were given this self-contained version. In that case say so plainly, then either
ask me to paste our brand colours and logo URL, or use the fallback above.


Whether or not you get the brand, **the Design standard at the end of this message is binding**. It sets the
visual standard: calm and precise rather than loud, one accent, tabular figures, no
gradients or shadows on data, charts chosen by the data's job. Read it before you lay
out a single screen, and check your output against its final section before you call
anything done.

**Copy: minimal, and never padded.** Where you need words, a landing page or an empty
state, keep them short and plain. If you do not know what should go there, write less.
No marketing language, no invented value propositions, no filler headings, no taglines
you made up. Blank beats fluff.

**6. Prove the connection works before building anything else.**
Your first task after I give you the key is a connection test: call `/api/v1/users` and
show me the result. Use `Authorization: Bearer <key>` plus the `Origin` header. If that
returns 401, retry once with `x-api-key` instead, because older keys use that. Tell me
which one worked.

Do not build a single screen until this passes. Debugging auth through a half-built
dashboard wastes both our time.

**7. Never turn a failed API call into a statement about my business.**
An API call has three outcomes, not two: data, genuinely empty, and failed. Never
collapse "failed" into "empty".

A 401 while checking whether a user exists means the lookup broke. It does not mean the
user is missing. Do not render "not a member of this workspace", "no deals found" or
"zero meetings" unless a request actually succeeded. Show the failing call and its
status code instead, so I can fix it.

This has already gone wrong in a real build, and it sent someone to their admin to solve
a problem that did not exist.

**8. Never invent a number.**
If a metric cannot be derived from available fields, show it as unavailable and tell me
why. Do not estimate, interpolate, or fill gaps. A blank cell is fine. A plausible wrong
number is not.


---


# Available solutions


These are the solutions you can offer me. Read the names out for Q1, then use
the matching section under "The solutions" below.

- **Meeting Conversion Funnel** (`meeting-conversion-funnel`)
  **Access required:** read-only. Objects: `contact`, `meeting`, `deal`.

Plus "something else", which uses only the API reference and design standard.


---


# The solutions


Use only the one I picked in Q1. Ignore the rest.


---


## Meeting Conversion Funnel

**Access required:** read-only. Objects: `contact`, `meeting`, `deal`.
Do not ask the customer about this. It is declared here so they do not have to answer it.

**Read the Dreamteam API reference at the end of this message first.** Auth,
pagination and the traps live there and are not repeated here.

---

### 1. What this solves

Sales leaders ask two questions that the CRM does not answer directly:

**"Where do contacts die?"** Not the stage they end in, but whether they ever got a
real conversation. A contact marked Unqualified after four meetings is a qualification
outcome. A contact marked Unqualified without a single meeting is a prospecting or
routing failure. The CRM shows both as "Unqualified".

**"Where does the funnel actually leak?"** Booked to completed, completed to qualified,
qualified to deal. Each is a different team's problem, and only one of them is usually
the real one.

You will build two linked views.

#### View A: contact status by meeting outcome

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

#### View B: contact to meeting to deal funnel

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

**The two views must reconcile exactly.** Section 6 gives the arithmetic. This is the
single most useful property of this pack: the matrix proves the funnel.

---

### 2. Data you need

| Object | Endpoint | Why |
|---|---|---|
| contacts | `/objects/contact/records` | status, owner |
| meetings | `/meetings` | outcome, contact links |
| deals | `/objects/deal/records` | final funnel stage |

Note the two endpoint families use **different pagination conventions**. See
the API reference at the end of this message, section 2. Getting this wrong here is especially damaging, because your
numerator and denominator would come from different slices of the data and the
percentages would still look plausible.

---

### 3. Discover

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

### 4. Map: deriving meeting outcome

**This is the hard part of this pack and the part most likely to be got wrong.**

Dreamteam does not store a meeting outcome. There is no `status` field on a meeting,
no "completed", no "no-show", no "cancelled". Any tool showing those buckets is
deriving them. You must derive them too, and you must be explicit with the user about
how.

#### The signals available

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

#### The recommended derivation

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

#### No-show and cancelled

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

### 5. Compute

#### View A, the matrix

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

#### View B, the funnel

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

#### Determining whether a deal is open

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

### 5b. Further metrics

Views A and B answer "where do contacts die". These answer *why*, and every one is
derivable from fields already verified on a live tenant. Build the ones the tenant has
data for and say plainly which you skipped.

**Follow the Design standard at the end of this message for every form below.** Each entry names its form because the form
follows the data's job, not preference.

#### Core, build these

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

#### Build if the data supports it

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

#### Not derivable, do not fake

- **No-show and cancelled rates.** No source field. See section 4.
- **Stage or status history.** Records carry current values only, so you cannot show
  how long a contact sat in a status, or reconstruct its path. The cohort heatmap is
  the closest honest substitute.
- **Meeting duration actually used.** `start_at` and `end_at` are the scheduled window,
  not attendance. Do not present scheduled length as time spent.

### 6. Verify

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

Also assert, per the API reference at the end of this message: every fetched collection's row count equals the
reported total. Display "212 of 212 meetings" style counts in the UI so truncation is
visible rather than silent.

---

### 7. Traps

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


---


# Dreamteam API reference


### Dreamteam API: verified behaviour

Every statement here was tested live against real tenants on 2026-08-03. Where this
document disagrees with https://docs.dreamteam.co/api/, trust this document and see
"Known documentation defects" at the bottom.

Use the official docs for the full endpoint list, filter syntax and operators. Use this
file for auth, pagination and the traps.

---

#### 1. Connecting

```
Base URL:  https://api.dreamteamcrm.ai/api/v1
Auth:      Authorization: Bearer <YOUR_KEY>
Tenant:    Origin: https://<tenant-slug>.dreamteamcrm.ai
```

Both headers are required on every request. `https://api.dreamteamcrm.info` is an alias
and behaves identically. Prefer the `.ai` host.

**Use `Bearer`.** It is what the profile page issues today and what the official docs
describe, so it is what customers will have.

##### Fallback: older keys use a different header

Some keys issued before the current profile-token scheme authenticate with
`x-api-key: <key>` instead, and return `401` on `Bearer`. Nothing in the key tells you
which you hold, so run one probe at startup rather than hardcoding:

```
GET /api/v1/users   with  Authorization: Bearer <key>  + Origin
  200  -> use Bearer for everything after this
  401  -> retry once with  x-api-key: <key>
            200  -> use x-api-key instead
            401  -> the key is genuinely invalid. Say so and stop.
```

Once at startup, not per request. Log which scheme won so a later failure is
diagnosable.

*Verified:* four keys across four tenants, including `dreamteam`, all return 200 with
`x-api-key` and 401 with `Bearer`. A profile-page token on that same tenant does the
opposite. Same workspace, opposite result, so this is about the credential, not the
tenant.

##### Other ways the request fails

| Mistake | What you get |
|---|---|
| Wrong header for your credential type | `401 Unauthorized` |
| Genuinely invalid or reset key | `401 Unauthorized` |
| No `Origin` header | `404` |
| Called from a browser | `403 Invalid CORS request` at preflight |

The first two are indistinguishable by status code, which is why the probe tries both
before concluding a key is bad.

##### Why browser calls can never work

The `Origin` header does two jobs at once: it is the CORS allowlist check *and* the
tenant selector. Browsers set `Origin` themselves and forbid JavaScript from changing
it. An app served from `myapp.lovable.app` is therefore rejected by the allowlist, and
even if it were allowed there is no tenant by that name.

Only `*.dreamteamcrm.ai` origins pass preflight. Call from a server.

---

#### 2. Pagination: two APIs, opposite conventions

**This is the most dangerous part of the API. Read it twice.**

Neither endpoint errors when you use the other one's convention. You get a valid-looking
response containing the wrong slice of data.

| | `/objects/{type}/records` | `/meetings`, `/recordings` |
|---|---|---|
| First page index | **1** (`page=0` throws `VALIDATION_FAILED`) | **0** (`page=0` is correct) |
| Page size param | **`page_size`** (max 100) | **`size`** |
| Rows array | `results` | `content` |
| Total count | `metadata.total_elements` | `totalElements` |
| More pages? | `metadata.has_next` | `last` is `false` |
| Page number echo | `metadata.page` | `number` |

##### Verified evidence

```
/objects/deal/records?page=1&size=100        ->  20 rows   WRONG, size is ignored
/objects/deal/records?page=1&page_size=100   -> 100 rows   correct
/objects/deal/records?page=1&page_size=200   -> 100 rows   capped at 100, no error

/meetings?page=1&page_size=100  ->  20 rows  WRONG, page_size ignored AND page 1 is the second page
/meetings?page=1&size=100       ->  85 rows  this is page TWO of 185, you silently skipped 100
/meetings?page=0&size=100       -> 100 rows  correct first page
```

Read that middle line again. On `/meetings`, starting at `page=1` skips the first page
entirely and returns a smaller number that looks like a complete result set.

##### Unknown query parameters are silently ignored

There is no "unknown parameter" error. Passing `size` to an endpoint that wants
`page_size` does not fail. It quietly returns the default 20 rows. This is how a
dashboard ends up built on 20 of 196 deals with no warning anywhere.

##### Required fetch procedure

1. Use the correct first-page index and size parameter for that endpoint family.
2. Loop until `metadata.has_next` is false, or `last` is true.
3. Accumulate rows.
4. **Assert** the accumulated count equals `metadata.total_elements` / `totalElements`.
5. If it does not match, throw. Do not render. Do not fall back to partial data.

Show the record count and the source total somewhere in the UI. If a user can see
"212 of 212 meetings", a truncation bug becomes visible instead of invisible.

##### Never turn an API failure into a business answer

**This has already happened in a real build and it is the worst failure mode in this
system.**

An app checked whether a signed-in person existed in Dreamteam. The lookup returned
`401 Unauthorized` because the auth header was wrong. The code treated "the call did not
succeed" as "the user was not found" and showed:

> *"Not a member of this workspace. shubham@dreamteam.co signed in with Google, but this
> email is not in the Dreamteam workspace user list. Ask an admin to add you."*

Every word of that is false, and it is confidently specific. It sent the user to an
admin to fix a problem that did not exist, while hiding the real one: a broken key.
A blank screen would have been more useful.

The rule: **an API call has three outcomes, not two.**

| Outcome | Meaning | What the user should see |
|---|---|---|
| Success with data | the answer | the answer |
| Success, empty result | genuinely nothing matched | "no results" |
| Failure (any non-2xx, timeout, malformed body) | you do not know anything | an error naming what broke |

Never collapse row three into row two. Concretely:

- Check the HTTP status before touching the body. Non-2xx means throw, not `[]`.
- A `401` from a user-existence check means the lookup failed, never "user not found".
- Error messages must name the failing call and status: *"Could not reach Dreamteam:
  `GET /users` returned 401. Check the API key."* Then the person reading it can act.
- Never phrase an infrastructure failure in business language. "Not a member",
  "no deals in pipeline" and "zero meetings" are claims about the customer's business.
  Only say them when a request actually succeeded.

Apply this everywhere, not just at sign-in. An empty dashboard caused by a bad key looks
exactly like a quiet quarter.

##### Errors do not have a rows key

Error responses are JSON objects with no `results` and no `content`:

```json
{"code":"VALIDATION_FAILED","message":"Page must be at least 1 (pages are 1-based)",
 "path":"/api/v1/objects/deal/records"}
```

Code written as `response.results ?? []` reads an error as "no data" and renders an
empty dashboard. Check for the error shape explicitly before reading rows.

---

#### 3. Record shape

`/objects/{type}/records` returns:

```json
{
  "results": [
    {
      "id": "...",
      "type": "deal",
      "properties": { "name": "...", "amount": 50000, "owner_id": 1000004,
                      "stage_id": "...", "pipeline_id": "...",
                      "expected_close_date": "..." },
      "created_at": "...", "updated_at": "...", "created_by": "..."
    }
  ],
  "metadata": { "page": 1, "page_size": 100, "total_elements": 196,
                "total_pages": 2, "has_next": true, "has_previous": false }
}
```

All business fields live under **`properties`**. Older examples showing a `data` key
are stale.

---

#### 4. Discovering the schema

```
GET /api/v1/objects/{object}
```

where `{object}` is `contact`, `company`, `deal`, `note`, `meeting` or `task`.

Returns `fields[]`, each with `name`, `type`, `label`, `filterable`, `read_only`,
`required`, and `options` for dropdowns.

**Call this before writing any logic.** Tenants can override standard fields and add
their own. A dashboard that hardcodes field names works for the tenant it was built
against and breaks on the next one.

Field types you will meet: `TEXT`, `TEXTAREA`, `EMAIL`, `PHONE`, `URL`, `DATETIME`,
`DECIMAL`, `NUMBER`, `BOOLEAN`, `DROPDOWN`, `LOOKUP`, `FILE`.

`LOOKUP` fields hold references to other records. `owner_id` is a lookup to a user.

---

#### 5. Users, identity and permissions

```
GET /api/v1/users
```

Returns `id`, `primary_email`, `first_name`, `last_name`, `role`, `sales_user`.
Observed roles: `admin`, `sales_member`.

**There is no whoami endpoint.** `/users/me` returns 500.

##### The key model

There is exactly one kind of API key: a **per-user profile token**, generated from that
user's profile page. There is no scoped key, no read-only key, and no expiry. The token
stays valid until someone clicks Reset, which invalidates the previous one immediately.

**The token can write.** The same key that reads also creates, updates and deletes.
There is no way to restrict it at issue time.

That is a fact to know, not a reason to cripple the app. Build whatever the reference
pack declares. If it says read-only, the app reads. If it declares writes, build them
properly. The one thing that does not change is that the token stays on the server.

**A key carries the permissions of the user who generated it.** The API filters to
"records the API caller is permissioned to see". So an admin's token returns everything,
including records owned by other people. *Verified:* a single admin token returned deals
under multiple distinct `owner_id` values.

*Inferred, not verified:* a token from a lower-privilege user, for example a
`sales_member`, should return a correspondingly narrower set. This is worth two minutes
to confirm before relying on it: create a limited user, generate its token, and compare
`total_elements` on the same query against an admin token. If the counts match, there is
no per-user filtering and the note above is wrong.

The practical consequence either way: if your app checks "does this signed-in person
exist in Dreamteam" and then queries with one shared token, every signed-in user sees
whatever *that token's* user can see, not what they themselves can see. Per-user scoping
has to be built.

To scope per user, do it in your server route:

- Look up the signed-in person's verified email in `/api/v1/users`.
- If `role` is `admin`, return everything.
- Otherwise filter to records where `properties.owner_id` equals their `id`.

The email must come from your identity provider's verified claim. Never from a form
field, or anyone can type a colleague's address.

---

#### 6. Known documentation defects

As of 2026-08-03, https://docs.dreamteam.co/api/ is wrong in two ways that will stop
you cold:

1. It documents `Authorization: Bearer <token>` as always required. That returns 401.
   The working header is `x-api-key`.
2. It does not mention the `Origin` tenant header at all, and states the opposite:
   *"The base URL is the same for all customers. Your Bearer token identifies your
   organization."* Omitting `Origin` returns 404.

It is also silent on the `/meetings` pagination convention differing from
`/objects/*/records`.

The docs are correct and useful for the endpoint list, filter syntax, operators and
sorting. Use them for that.


---


# Design standard


### Design standard

Load this on every build, alongside the API reference.

The brief is **calm, not loud**. The apps this produces are looked at every morning by
someone who already knows their business. They should feel like a well-set page, not a
control room. Impact comes from restraint, precision and typography. Never from
saturation, glow, or motion.

If a choice would make the page more exciting but less quiet, it is the wrong choice.

---

#### 1. What "wow" means here

It is not colour. It is these, in order:

1. **The number is the object.** Large, light-weight, tabular figures, generous space
   around it. A well-set 56px figure with one line of context beneath it beats any
   chart treatment.
2. **Alignment you can feel.** One grid, consistent gutters, optical alignment of
   numerals. Most dashboards fail here and it reads as cheapness even when nobody can
   name why.
3. **One accent, used rarely.** A single hue, carrying the one thing that matters on
   the screen. Everything else is ink and surface. An accent used four times is not an
   accent.
4. **Density without crowding.** Show the real numbers, not rounded summaries, but give
   them room. Tables are good. Tables are often better than charts.
5. **Nothing decorative.** No element exists that does not carry data or structure.

#### 2. Hard prohibitions

These read as "poppy" and are not permitted:

- Gradients on data marks. Flat fills only. A gradient on a bar makes its value
  ambiguous.
- Drop shadows on cards or tiles. Separate with a 1px hairline or a surface step.
- Glow, neon, saturated backgrounds, coloured card fills.
- More than one accent hue on a screen.
- Full-width coloured banners or hero blocks.
- Rounded corners above 8px on containers, above 4px on data marks.
- Emoji as iconography.
- Animated counters, ticking numbers, progress animations on load.
- Looping or ambient motion of any kind.
- Confetti, celebration states, gamification.

#### 3. Typography

- **One family.** Inter unless the customer's site gives you a better-justified
  choice. No pairing a display face with a body face.
- **Numerals: tabular, always** (`font-variant-numeric: tabular-nums`). Columns of
  figures that do not align vertically are the single most common tell of a
  generated dashboard.
- **Weight carries hierarchy, size carries scale.** Headline figures go *lighter* as
  they go larger, not bolder. A 56px number at weight 300 reads calm; at 700 it shouts.
- **Labels and axis text**: 11 to 12px, letter-spaced slightly, in muted ink, often
  uppercase. They should recede.
- **Sentence case** for headings. Not Title Case.

#### 4. Colour

Follow this order. Colour is chosen **last**, after the form.

**Assign by the job the colour does:**

| Job | Rule |
|---|---|
| Magnitude (more is more) | **Sequential**: one hue, light to dark. The safe default. |
| Identity (which series is which) | **Categorical**: fixed hue order, never cycled |
| Polarity (above/below, good/bad) | **Diverging**: two opposed hues, neutral grey midpoint |
| State (healthy/at risk/failed) | **Status**: reserved tokens, never reused as a series |

**Non-negotiable:**

- Sequential is the default. Reach for categorical only when the series genuinely
  *are* the subject.
- **Never a rainbow ramp** for magnitude. One hue.
- **Never a hue at a diverging midpoint.** The middle must read as "nothing".
- **Colour follows the entity, never its rank.** Filtering out a series must not
  repaint the survivors. Someone who learned "Outbound is blue" must not be misled.
- **Never generate a 9th categorical hue.** Past eight, fold the tail into "Other" or
  facet into small multiples.
- **Never put a value-ramp on unordered categories.** Colouring each bar
  darker-where-bigger double-encodes the length the chart already shows.
- **Status colours are reserved.** They ship with an icon and a label, never colour
  alone.
- **Text wears text tokens, never the series colour.** A coloured mark next to a
  neutral-ink label carries the identity.

**Contrast and colourblindness:** adjacent categorical hues must remain separable
under deuteranopia and protanopia. If you cannot verify that, reduce to three or fewer
series and add direct labels. Do not eyeball a large palette and assume it is fine.

**Dark mode is designed, not flipped.** Pick its own steps from the same hues against
the dark surface. An inverted light palette produces glowing, oversaturated marks,
which is exactly the failure this document exists to prevent. Both modes ship.

#### 5. Choosing the form

Pick the form from the data's job, before touching colour.

| The data is | Use | Not |
|---|---|---|
| One current value | **Stat tile**: figure, label, optional delta | a one-bar bar chart |
| A few headline numbers | **KPI row** of stat tiles | a grouped bar chart |
| The number the page leads with | **Hero figure**, 48px or larger | anything else |
| One ratio against a limit | **Meter** on a same-hue track | a two-slice pie |
| More than about seven meaningful classes | **A table**, possibly with inline bars | more colours |
| Magnitude across categories | bar or column; **heatmap** for a grid | pie |
| Change over time | line; area for a single series | stacked area for many |
| One series matters, the rest are context | **Emphasis**: one accent, rest in grey | eight categorical hues |
| Above or below a baseline | diverging bar | two-colour arbitrary bars |
| Ordered-scale share, for example sentiment | **diverging stacked bar**, centred on neutral | grouped bars |

**Emphasis is the most underused form and usually the right answer.** If the story is
"this one is the problem", that is one accent series and everything else in
de-emphasis grey. Not a palette.

**A table is a legitimate visualisation.** For seven sources or twelve owners, a table
with a right-aligned numeric column and a thin inline bar is clearer, calmer and more
precise than any chart. Use it without apology.

#### 6. Marks and chrome

- **Thin marks.** Bars slim with space between them, lines 2px, points 8px or more.
- **Rounded data-ends at 4px**, anchored flat to the baseline. Never round both ends
  of a bar.
- **2px surface-coloured gap** between adjacent fills and stacked segments, and a 2px
  surface ring where marks overlap. This one detail separates competent charts from
  amateur ones.
- **Grid and axes recede.** Hairline weight, muted ink, horizontal gridlines only.
  Often no vertical gridlines at all. Never a box frame around the plot.
- **No axis line where the bars already imply one.**
- **Label selectively.** Direct-label the first, last and extreme points. Never a
  number on every point. If every point needs a number, you wanted a table.
- **Legend for two or more series, always.** One series needs no legend, the title
  names it. Four or fewer series get direct labels as well, so identity never depends
  on colour alone.

#### 7. Interaction

- **Hover is expected, not optional.** Crosshair and tooltip on lines and areas,
  per-mark tooltip on bars, cells and points. The only thing that skips it is a bare
  stat tile.
- Hit targets larger than the mark.
- Filters in a single row above the content, never in a sidebar for a single-screen
  dashboard.
- **Transitions: one, short, and only on state change.** 150 to 250ms, ease-out.
  Nothing animates on page load. Nothing loops.
- Honour `prefers-reduced-motion` by removing transitions entirely.

#### 8. Layout

- Establish one column grid and keep every card on it.
- Vertical rhythm from a single spacing scale, for example 4, 8, 12, 16, 24, 32, 48.
- **The lead insight goes above the charts, as a sentence in plain language**, at
  headline size. "899 of 918 unqualified contacts were dropped without a meeting" is
  the product. The table underneath is the evidence.
- Cards separated by hairlines or surface steps, never shadows.
- Empty and error states get the same care as the populated view. An error state names
  the failing call and its status code, never a business explanation.

#### 9. Copy

Minimal and plain. Where you do not know what should go somewhere, write less.

No marketing language, no invented value propositions, no filler headings, no taglines.
Do not explain what a chart obviously shows. Do explain a definition the reader cannot
infer, for example what counts as a completed meeting, and put it below the chart in
muted ink.

**No em dashes**, in the interface or in anything you write to me. Use a comma, a full
stop, or restructure the sentence.

#### 10. Before you call it done

- Open the rendered page and look at it. Check for label collisions, overflow, and
  numbers that do not align.
- Check it against section 2. If any prohibition is present, it is wrong.
- Check both light and dark mode, on the real data, not placeholders.
- Check it at a narrow width. Wide tables scroll inside their own container; the page
  itself never scrolls sideways.
