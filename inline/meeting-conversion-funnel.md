You are going to build an application on top of Dreamteam CRM data.

Everything you need is in this message. Do not try to fetch any URL. If you cannot
reach the internet, that is fine and expected.

## STOP. Do not write any code yet.

Ask me the questions in the next section first. Do not scaffold a project, do not
create files, do not "start with a basic version".

## Ask me these questions

**Q1. Who is allowed to sign in?**
  a) Whatever sign-in my platform already provides, no extra setup. Recommend this
     unless I say otherwise.
  b) Only people who already exist in Dreamteam. On top of (a), the app checks the
     signed-in user's verified email against Dreamteam's user list.
  c) No sign-in at all. Private link only, for a quick internal look.

If I pick (b), tell me plainly what extra setup that needs on my platform before I
commit to it.

**Q2.** (only if I chose 1b) **What should each person see?**
  a) Everyone sees all data.
  b) Admins see everything; everyone else sees only records they own.

Do **not** ask me what objects the app may touch, or whether it should be read-only.
The solution below declares the access it needs. Ask about writing back only if what
I described is genuinely ambiguous about it, and then ask it as one plain question,
once.

Then ask me for two things:
  - **The web address I use for Dreamteam**, for example
    `https://acme.dreamteamcrm.ai`. Extract the workspace name from it yourself and
    confirm it back to me. Do not ask me for a "tenant slug".
  - **My API key.** If I do not have one, tell me to open my Dreamteam profile,
    scroll to API Token, and click Reveal then Copy.

## Non-negotiable build rules

**1. The API key lives on the server.**
The application must have a server-side route that holds the key and calls Dreamteam.
The browser calls only your own routes, never Dreamteam directly.

This is not a preference. Dreamteam's API rejects browser requests from any origin
outside `*.dreamteamcrm.ai` at CORS preflight, before the key is even checked. A
client-side fetch will not work. It would also ship the key to every visitor.

If your platform cannot run server-side code, stop and tell me, because this cannot
be built safely there.

**2. Paginate correctly, and prove it.**
The two Dreamteam list APIs use opposite conventions and neither errors when you get
it wrong. You will silently receive a fraction of the data and everything will look
fine. The API reference at the end of this message has the exact rules. Follow them,
and assert your row count against the reported total before rendering anything.

**3. Discover the schema before assuming it.**
Call the describe endpoint for each object and use the field names that tenant
actually has. Never hardcode a field name or a pipeline stage from an example.

**4. Build what the API can do.**
If Dreamteam's API supports it, the app may do it. Do not restrict the application
beyond what the solution asks for.

**5. Never invent a number.**
If a metric cannot be derived from available fields, show it as unavailable and tell
me why. Do not estimate, interpolate, or fill gaps. A blank cell is fine. A plausible
wrong number is not.

---

# The solution to build


### Meeting Conversion Funnel

**Access required:** read-only. Objects: `contact`, `meeting`, `deal`.
Do not ask the customer about this. It is declared here so they do not have to answer it.

**Read the Dreamteam API reference at the end of this message first.** Auth,
pagination and the traps live there and are not repeated here.

---

#### 1. What this solves

Sales leaders ask two questions that the CRM does not answer directly:

**"Where do contacts die?"** Not the stage they end in, but whether they ever got a
real conversation. A contact marked Unqualified after four meetings is a qualification
outcome. A contact marked Unqualified without a single meeting is a prospecting or
routing failure. The CRM shows both as "Unqualified".

**"Where does the funnel actually leak?"** Booked to completed, completed to qualified,
qualified to deal. Each is a different team's problem, and only one of them is usually
the real one.

You will build two linked views.

##### View A: contact status by meeting outcome

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

##### View B: contact to meeting to deal funnel

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

#### 2. Data you need

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

#### 3. Discover

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

#### 4. Map: deriving meeting outcome

**This is the hard part of this pack and the part most likely to be got wrong.**

Dreamteam does not store a meeting outcome. There is no `status` field on a meeting,
no "completed", no "no-show", no "cancelled". Any tool showing those buckets is
deriving them. You must derive them too, and you must be explicit with the user about
how.

##### The signals available

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

##### The recommended derivation

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

##### No-show and cancelled

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

#### 5. Compute

##### View A, the matrix

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

##### View B, the funnel

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

##### Determining whether a deal is open

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

#### 6. Verify

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

#### 7. Traps

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
