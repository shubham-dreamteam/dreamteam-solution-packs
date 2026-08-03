You are going to build an application on top of Dreamteam CRM data.

## STOP. Do not write any code yet.

Before writing a single line, you must complete steps 1 and 2 below and get answers
from me. Do not scaffold a project. Do not create files. Do not "start with a basic
version". Ask first.

## Step 1: Load the catalogue

Fetch this URL:

https://raw.githubusercontent.com/shubham-dreamteam/dreamteam-solution-packs/main/references/index.md

Then print the list of available solutions back to me, by name.

If you cannot fetch that URL, say so explicitly and stop. Do not guess what it contains
and do not proceed from memory. I will paste the file in manually instead.

## Step 2: Ask me these three questions

**Q1. Which solution do you want to build?**
List the options from the catalogue you just fetched, plus "something else".
If I pick "something else", you will use `references/api-truth.md` only.

**Q2. Who is allowed to sign in?**
  a) Whatever sign-in my platform already provides, no extra setup. Recommend this
     unless I say otherwise.
  b) Only people who already exist in Dreamteam. On top of (a), the app checks the
     signed-in user's verified email against Dreamteam's user list.
  c) No sign-in at all. Private link only, for a quick internal look.

If I pick (b), tell me plainly what extra setup that needs on my platform before I
commit to it.

**Q3.** (only if I chose 2b) **What should each person see?**
  a) Everyone sees all data.
  b) Admins see everything; everyone else sees only records they own.

Do **not** ask me what objects the app may touch, or whether it should be read-only.
The reference pack declares the access it needs, and most are read-only. Ask about
writing back only if what I described is genuinely ambiguous about it, and then ask it
as one plain question, once.

Then ask me for two things:
  - **The web address I use for Dreamteam**, for example
    `https://acme.dreamteamcrm.ai`. Extract the workspace name from it yourself and
    confirm it back to me. Do not ask me for a "tenant slug".
  - **My API key.** If I do not have one, point me at
    https://github.com/shubham-dreamteam/dreamteam-solution-packs/blob/main/SETUP.md

## Step 3: Load the solution

Fetch `references/api-truth.md` and the reference file for the solution I chose, from
the same repository. Confirm you have both before building. If either fetch fails, stop
and tell me.

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
`api-truth.md` has the exact rules. Follow them, and assert your row count against the
reported total before rendering anything.

**3. Discover the schema before assuming it.**
Call the describe endpoint for each object and use the field names that tenant actually
has. Never hardcode a field name or a pipeline stage from an example.

**4. Build what the API can do.**
If Dreamteam's API supports it, the app may do it. Do not restrict the application
beyond what the reference pack asks for. If the pack says read-only, stay read-only. If
it declares writes, build them properly.

**5. Never invent a number.**
If a metric cannot be derived from available fields, show it as unavailable and tell me
why. Do not estimate, interpolate, or fill gaps. A blank cell is fine. A plausible wrong
number is not.

## If the catalogue fetch failed

These solutions existed as of 2026-08-03. This list may be stale:

- `meeting-conversion-funnel`: contact status by meeting outcome, and the
  contact to meeting to deal funnel
- `forecasting`: pipeline forecast by category, stage and owner
- `churn-analysis`: at-risk account identification
- `pipeline-hygiene`: stalled deals, missing fields, stage mismatches
