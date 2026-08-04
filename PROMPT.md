You are going to build an application on top of Dreamteam CRM data.

## STOP. Do not write any code yet.

Before writing a single line, you must complete steps 1 and 2 below and get answers
from me. Do not scaffold a project. Do not create files. Do not "start with a basic
version". Ask first.

## Step 1: Load the catalogue

Fetch this URL:

https://raw.githubusercontent.com/shubham-dreamteam/dreamteam-solution-packs/main/references/index.md

**How to fetch it.** This is a plain text file, not a web page. Use a plain HTTP GET,
`curl` if you have a shell. Do **not** use a browser tool, scraper, crawler or
page-renderer. Those are built for HTML and are known to misreport a raw text URL as
404 when it is actually returning 200.

**Say nothing about this step if it works.** Do not print the status code, do not print
the file, do not list the solutions here. Go straight to Q1, which is where I see the
list. Status codes and fetch chatter are for when something breaks, not for me to read
every time.

**Before you tell me a fetch failed, try the other two.** One tool returning 404 is not
proof of 404. All three of these serve the same file:

```
https://raw.githubusercontent.com/shubham-dreamteam/dreamteam-solution-packs/main/references/index.md
https://github.com/shubham-dreamteam/dreamteam-solution-packs/raw/main/references/index.md
https://api.github.com/repos/shubham-dreamteam/dreamteam-solution-packs/contents/references/index.md
```

Only say you cannot fetch it after a plain GET has genuinely failed against all three,
and then show me the status code or error you actually got. Then stop. Do not guess what
the file contains and do not proceed from memory. I will paste it in manually instead.

The same applies to every fetch in Step 3 and to my company website in rule 5: plain
GET, retry before reporting failure, silent when it works, status codes only when it
does not.

## Step 2: Ask me these three questions

**How to ask.** One question per message. One line for the question, one short line per
option, each option on its own line. No preamble, no explanation of the trade-offs, no
paragraph about what an option implies. I will ask if I want detail. A question longer
than about five lines is too long, so cut it.

**Ask each question exactly once.** Once I have answered, that answer stands. Never
re-ask it, never ask me to confirm it, never restate the options back to me for a second
pick. If you have a caveat about my answer, say it in one or two sentences and keep
going. I will tell you if I want to change something.

**No progress narration.** Do not tell me what you fetched, what you are about to do, or
that a step succeeded. I only want to hear from you when you have a question, a finding,
or something broke. Your first message to me should be Q1 and nothing else.

Anything below written in brackets is a note to you, not text to read out.

**Q1. Which solution do you want to build?**
List the names from the catalogue you just fetched, plus "something else".
[If I pick "something else", use `references/api-truth.md` only.]

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
The reference pack declares the access it needs, and most are read-only. Ask about
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

## Step 3: Load the solution

Fetch three files from the same repository and confirm you have all three before
building: `references/api-truth.md`, `references/design.md`, and the reference file for
the solution I chose.

Same rules as Step 1: plain GET, not a browser or scraper tool, and try the alternate
URL forms before concluding anything failed. Silent when it works. If a fetch genuinely
fails, show the status and stop, rather than building from memory.

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

Whether or not you get the brand, **`references/design.md` is binding**. It sets the
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

## If the catalogue fetch failed

These solutions existed as of 2026-08-03. This list may be stale:

- `meeting-conversion-funnel`: contact status by meeting outcome, and the
  contact to meeting to deal funnel
- `forecasting`: weighted forecast, coverage, slippage, win rates, per-owner
- `churn-analysis`: account risk from activity decay, coverage gaps, single-threading
