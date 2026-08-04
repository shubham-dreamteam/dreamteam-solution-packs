# Dreamteam Solution Pack catalogue

Present these to the customer as the answer to Q1. Read the chosen file, plus
`api-truth.md`, before building anything.

All files live at:
`https://raw.githubusercontent.com/shubham-dreamteam/dreamteam-solution-packs/main/references/<file>`

---

## Available solutions

Every pack declares the access it needs at the top of its file. **Do not ask the
customer about scope, objects, or read versus write.** The pack has already answered it.

### meeting-conversion-funnel
**Where contacts die, and where the funnel leaks.**
Two linked views: a contact-status by meeting-outcome matrix, and a contact to meeting
to deal funnel. Answers whether contacts were disqualified after a real conversation or
without ever having one.
Access: read-only. Objects: contact, meeting, deal.
File: `meeting-conversion-funnel.md`

### forecasting
**What will we close, and will we make the number.**
Weighted forecast against target, composition by stage, the deals that decide the
quarter, slippage, win rates by count and by value, per-owner attainment, and the
health signals behind the number. Every figure drills to its deals.
Access: read-only. Objects: deal, pipeline, user, target.
File: `forecasting.md`

### churn-analysis
**Which accounts are going quiet, and which relationships are fragile.**
Activity-recency decay, coverage gaps, single-threading, engagement trend, post-sale
silence and loss reasons. Note: Dreamteam holds no subscription data, so this is
account risk, not churn rate. The pack says so up front.
Access: read-only. Objects: company, contact, deal, pipeline, meeting, task, user.
File: `churn-analysis.md`

---

## Always required

### api-truth
Auth, pagination, schema discovery, permissions and the traps. **Load this for every
build, including "something else".** It is not optional and it is not summarised
anywhere else.
File: `api-truth.md`

### design
The visual standard every build must meet: calm rather than loud, how to choose a chart
form, colour rules, mark specs, and the prohibitions that make a dashboard look
generated. **Load this for every build too.**
File: `design.md`

---

## Something else

If the customer wants a solution not listed here, load `api-truth.md` and `design.md`,
then follow
its rules. Discover the schema before designing anything, and hold to the same
standards: server-side key, verified pagination, no invented numbers.
