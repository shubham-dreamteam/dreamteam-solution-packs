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
*Not yet written.* Pipeline forecast by category, stage and owner.
File: `forecasting.md`

### churn-analysis
*Not yet written.* At-risk account identification from engagement and activity decay.
File: `churn-analysis.md`

### pipeline-hygiene
*Not yet written.* Stalled deals, missing fields, stage mismatches.
File: `pipeline-hygiene.md`

---

## Always required

### api-truth
Auth, pagination, schema discovery, permissions and the traps. **Load this for every
build, including "something else".** It is not optional and it is not summarised
anywhere else.
File: `api-truth.md`

---

## Something else

If the customer wants a solution not listed here, load `api-truth.md` only, then follow
its rules. Discover the schema before designing anything, and hold to the same
standards: server-side key, verified pagination, no invented numbers.
