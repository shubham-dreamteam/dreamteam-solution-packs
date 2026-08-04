# Churn and account risk

**Access required:** read-only. Objects: `company`, `contact`, `deal`, `pipeline`,
`meeting`, `task`, `user`.
Do not ask the customer about this. It is declared here so they do not have to answer it.

**Read the Dreamteam API reference first.** Auth, pagination and the traps live there and
are not repeated here. Read the design standard too: every number below must drill to the
accounts behind it.

---

## 1. Read this before you build anything

**Dreamteam holds no subscription data.** There is no MRR, no ARR, no renewal date, no
contract term, no billing status, no usage. Verified against the full schema of every
object: `company`, `contact`, `deal`, `product`, `task`, `note` and `meeting`.

That means **you cannot compute churn rate, retention, net revenue retention or
lifetime value.** Any tool that claims to from this data is making it up.

Tell the customer this in one sentence before you build, and offer what is actually
available:

> *"Dreamteam doesn't store subscriptions or renewals, so true churn rate isn't
> computable here. What I can build is account risk: which accounts are going quiet,
> which deals are structurally fragile, and where relationships are thinning. If you
> have billing data elsewhere, that's a separate integration."*

If they want real churn, the honest answer is that it needs their billing system, and
this pack is not it.

**What this pack builds instead:** a leading-indicator view of relationship health.
Every signal here is about attention and engagement, which is what predicts churn before
the invoice does.

---

## 2. Discover first

**`GET /api/v1/objects/company`** gives `name`, `domain`, `industry`, `company_size`,
`icp` (Excellent Fit / Good Fit / Bad Fit / ICP Unknown), `owner_id`, `contact_ids`,
`product_ids`, `last_activity_date`, `next_activity_date`.

**`GET /api/v1/objects/contact`** gives `contact_activity_status`, `engagement`
(High / Medium / Low), `icp_fit`, `buying_role`, `last_activity_date`,
`next_activity_date`, `company_ids`.

**`GET /api/v1/objects/deal`** gives `risk`, `momentum`, `confidence`,
`multi_threading`, `has_gaps?`, `ai_deal_gaps`, `stage_id`, `close_date`,
`last_activity_date`, `won_reason`, `lost_reason`, `company_ids`, `contact_ids`.

**`GET /api/v1/pipelines/{id}`** for `stage_category`, needed to identify won accounts.
The list endpoint omits stages, so fetch each pipeline by id.

**`GET /api/v1/objects/task`** gives `status` (Open / Pending / Done / Recommended),
`due_at`, `completed_at`, `recommendation_status`, `company_ids`, `deal_ids`.

**`GET /api/v1/objects/meeting`** and `/api/v1/meetings` for conversation recency.

Check the populated share of every field before building a view on it. Report anything
under about half as too sparse, rather than charting mostly-null.

---

## 3. Defining an account

Work at **company** level. A contact going quiet is noise; an account going quiet is a
signal.

```
Customer         = company linked to at least one deal whose stage_category
                   is "Closed Won"
Prospect         = company with only open or lost deals
Won date         = max close_date among that company's won deals
Days since won   = today − won date
```

Churn risk applies to **customers**. Prospects going quiet is a pipeline problem, which
is the forecasting pack's job. Keep the two separate and say which population each view
covers, because blending them produces a number that means nothing.

---

## 4. The math

### 4.1 Activity recency, the spine of everything here

```
Days silent = today − company.last_activity_date
```

Bucket, do not average. Averages hide the tail, and the tail is the entire point:

```
0-14 days     healthy
15-30 days    watch
31-60 days    at risk
61-90 days    serious
90+ days      likely gone
never         no activity date recorded at all
```

**Report "never" as its own bucket, never merged into 90+.** A missing date means you do
not know, and the difference between "silent for six months" and "we never recorded
anything" is the difference between a real signal and a data-quality problem.

`last_activity_date` is maintained by Dreamteam from emails, meetings and CRM changes.
Confirm it is actually moving on this tenant before you build on it: if the most recent
value across all companies is months old, the integration is not connected and every
number here is wrong. Check that first and say so.

### 4.2 Coverage gap

```
Uncovered = customer AND next_activity_date is null or in the past
```

Nothing scheduled is the most controllable churn signal on the page. Unlike silence,
which describes the past, this describes a decision nobody has made yet.

Report count, and the share of customers uncovered.

### 4.3 Relationship depth

```
Contacts per account   = count of linked contacts
Engaged contacts       = linked contacts with engagement = High or Medium
Single-threaded        = exactly one linked contact, or one engaged contact
```

Also use `deal.multi_threading` where deals exist: Single-thread, Emerging multi-thread,
Effective multi-thread. It is an ordered scale, so treat it as ordinal, not categorical.

**Single-threading is the strongest structural risk signal available in this data.** One
contact leaving ends the relationship, and unlike silence it is visible before anything
goes wrong.

### 4.4 Engagement decay

Per account, compare a recent window against a prior one of equal length. Default to 90
days each, and let the customer change it.

```
Recent    = meetings whose start_at falls in the last 90 days
Prior     = meetings whose start_at falls in the 90 days before that
Change    = recent − prior
```

Report the change in **absolute counts**, not as a percentage. Percentage change on
small integers is nonsense: going from 1 meeting to 0 is "down 100%" and going from 0 to
1 is undefined. Show "2 → 0", which a human reads correctly at a glance.

Only include accounts with at least one meeting in either window. An account with zero
in both is covered by 4.1 and would otherwise dominate this view with non-events.

### 4.5 A composite risk score, if you build one

Optional, and if you do it, be transparent. A score nobody can decompose gets ignored
the first time it is wrong.

Suggested inputs, each contributing points:

```
Days silent          61-90: +2      90+: +3       never: +2
No next activity     +2
Single-threaded      +2
Deal risk = High     +2             Medium: +1
Momentum Regressing  +2             Stalled: +1
Engagement all Low   +1
```

**Rules if you show a score:**

- Show the components, not just the total. The drill panel lists which rules fired.
- Never present it as a probability. It is not calibrated against actual churn, because
  there is no churn outcome in this data to calibrate against.
- Label it as a heuristic in the interface, in those words.
- Do not weight by revenue. There is no revenue field. Deal `amount` is what was sold
  once, not what they pay now.

If the customer wants a score they can defend, sorting by days silent within
single-threaded accounts gets 80% of the value with none of the false precision. Offer
that first.

### 4.6 Post-sale silence

```
Won accounts with no activity since won date
Days from won to last activity
```

An account that went quiet immediately after signing never onboarded. This is the
highest-value cut in the pack, and it is invisible in every standard CRM view because
the deal is marked Won and stops being looked at.

### 4.7 Why deals are lost

Group closed-lost deals by `lost_reason`. Free text, so show distinct values verbatim
and do not invent buckets. Cross with `icp` where populated: losing consistently outside
ICP is a targeting problem, losing inside it is a product or execution problem, and the
two need different responses.

---

## 5. The views

Follow the design standard. Every number drills to its accounts.

### 5.1 Headline

One sentence, plain language, at headline size. *"11 of 43 customers have had no
activity in over 60 days. 7 of those have a single contact."*

Beneath it, a small KPI row: customers, at risk, uncovered, single-threaded.

State the population in the header, for example "customers only, 43 accounts", so nobody
reads it as the whole database.

### 5.2 Silence distribution

A **column chart** over the buckets in 4.1, with "never" visually separated from the
time buckets by a gap, because it is a different kind of thing.

Sequential ramp darkening with time, not categorical. The buckets are ordered, and a
value-ramp is correct here precisely because the categories have a natural order.

Every column drills to its accounts.

### 5.3 The risk table

The workhorse. One row per customer, default sorted by days silent descending.

Columns: account, owner, days silent, next activity, contacts, engaged contacts,
open deals, deal risk, momentum, days since won.

Sortable on every column, sticky header, click to drill. **Emphasis, not a colour per
row**: accent only the accounts that are both silent and single-threaded, since that
combination is the actionable one. Everything else in neutral ink with a status dot
where a value is genuinely bad.

This table is what the customer will actually use. Give it more care than the charts.

### 5.4 Silence against depth

A **scatter**: days silent on one axis, engaged contacts on the other, one point per
account, radius constant. Do not size by deal amount, which would imply a revenue
weighting the data cannot support.

The bottom-right quadrant, silent and single-threaded, is the working list. Label the
quadrant rather than relying on the reader to find it.

Cap the series at three colours if you split by anything. Scatter is an all-pairs form,
so beyond three the colours stop being separable.

### 5.5 Engagement trend

**Dumbbell chart**: prior window and recent window per account, one line between two
dots, sorted by the size of the decline. One hue, two shades, per the design standard.

Only accounts with a change. A dumbbell of flat lines is noise.

### 5.6 Post-sale drop-off

For won accounts, a **histogram** of days between won date and last activity. A spike
near zero is a handover problem and worth naming in a caption when you see it.

### 5.7 Coverage

A **meter**: share of customers with a future `next_activity_date`. Same-hue track,
which is the right form for one ratio against a limit. Not a two-slice pie.

### 5.8 Loss reasons

**Table with inline bars**, verbatim `lost_reason` values, count and value, with an ICP
split where populated.

---

## 6. Verify

```
customers + prospects            == companies fetched   (mutually exclusive by section 3)
Σ silence buckets                == customers, including the "never" bucket
uncovered                        <= customers
single-threaded                  <= customers
row count                        == metadata.total_elements   for every fetch
```

Show "43 of 43 customers" in the interface. Also show the populated share of
`last_activity_date`, because every view here rests on it and a reader deserves to know
if it is 60% blank.

---

## 7. Traps

**There is no churn data.** Section 1. Never label anything here "churn rate",
"retention" or "NRR". The words imply a measurement that has not been made.

**A missing `last_activity_date` is not old activity.** Its own bucket, always.

**Check the activity feed is live before trusting recency.** If no company anywhere has
activity in the last month, the integration is disconnected and the whole dashboard is
measuring the integration rather than the customers. Check and say so.

**Percentage change on small numbers lies.** Section 4.4. Show counts.

**Deal `amount` is not recurring revenue.** It is one transaction. Do not sum it as
"revenue at risk", do not weight a risk score by it, and do not size marks by it.

**Won does not mean active.** A company with a won deal from two years ago and no
activity since may have already left. This pack surfaces the suspicion. It cannot
confirm it, and should not pretend to.

**Do not blend customers and prospects.** Section 3.

**A composite score is a heuristic, not a probability.** Section 4.5. Show its
components or do not show it.

**Two pagination conventions.** `/objects/*/records` is 1-indexed with `page_size`;
`/meetings` is 0-indexed with `size`. Mixing them truncates one side silently, and an
account looks quiet simply because you did not fetch its meetings.
