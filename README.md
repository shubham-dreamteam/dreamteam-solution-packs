# Dreamteam Solution Packs

Build dashboards and internal tools on your Dreamteam CRM data, from any AI-coding
platform, by pasting one prompt.

Like importing a Postman collection, except it carries the thinking as well as the
endpoints.

---

## Copy this prompt

Paste it into Emergent, Lovable, Replit Agent, v0, Claude Code, or any AI-coding tool.
It will ask you a few questions, then build.

<!-- BEGIN PROMPT -->

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

    Then ask me for three things:
      - **The web address I use for Dreamteam**, for example
        `https://acme.dreamteamcrm.ai`. Extract the workspace name from it yourself and
        confirm it back to me. Do not ask me for a "tenant slug".
      - **My API key.** If I do not have one, point me at
        https://github.com/shubham-dreamteam/dreamteam-solution-packs/blob/main/SETUP.md
      - **My company website**, so you can match the app to our brand. See rule 5.

    ## Step 3: Load the solution

    Fetch three files from the same repository and confirm you have all three before
    building: `references/api-truth.md`, `references/design.md`, and the reference file for
    the solution I chose. If any fetch fails, stop and tell me.

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

<!-- END PROMPT -->

The same text lives in [PROMPT.md](PROMPT.md), which is easier to copy cleanly.


---

## What you actually have to do

Three multiple-choice questions, and one page visit to get your key. That is the whole
job. You do not write code, pick a schema, or configure an API.

| | Question | Why it is asked |
|---|---|---|
| Q1 | Which solution | Picks which reference pack gets loaded |
| Q2 | Who can sign in | Default is whatever your platform already provides, no setup |
| Q3 | What each person sees | Keys are shared, so per-user scoping has to be built |

Then two pastes: **your Dreamteam web address** and **your API key**. Both come from the
same page. See **[SETUP.md](SETUP.md)**, which takes about two minutes.

You are not asked what data the app may touch, or whether it should be read-only. Each
pack declares that itself.

### Where it is not fully self-serve

Two places you still have to think:

**Dreamteam-gated sign-in needs an identity provider.** If you pick Q2b, you need real
auth on your platform, which is genuine setup. The default, Q2a, uses whatever sign-in
your platform already gives you and needs nothing.

**Nobody validates the numbers but you.** The packs assert internal consistency and fail
loudly on a mismatch, but they cannot know your business. Check the first output against
a number you already trust.

One thing worth knowing rather than deciding: Dreamteam's API key is not read-only and
cannot be made read-only. The dashboards here only read, and every pack declares its
access up front. [SETUP.md](SETUP.md) covers how the user you create sets the ceiling.

---

## Available solutions

| Pack | What it answers | Status |
|---|---|---|
| [meeting-conversion-funnel](references/meeting-conversion-funnel.md) | Where contacts die, and where the funnel leaks | Ready |
| forecasting | Pipeline forecast by category, stage and owner | Planned |
| churn-analysis | Which accounts are at risk | Planned |
| pipeline-hygiene | Stalled deals, missing fields, stage mismatches | Planned |

Two files load on every build. [api-truth.md](references/api-truth.md) carries the
verified API behaviour, including the pagination traps that silently produce wrong
numbers. [design.md](references/design.md) is the visual standard: calm rather than
loud, charts chosen by the data's job, and the prohibitions that make a dashboard look
generated.

---

## How this works

The prompt is a **bootloader**, not a solution. It carries the universal rules and a
pointer to the catalogue. The reference packs are the swappable payload.

That means the prompt on this page never changes when a solution is added. Copy it once,
and you always get the current catalogue.

Packs are **documents, not code**. There is no app to fork. A working app hardcodes one
tenant's field names and breaks on the next one, so each pack instead carries the
schema-discovery procedure, the metric definitions, and the specific ways that solution
goes wrong. Your platform writes the code.

---

## Platform support

A server-side route is mandatory, because Dreamteam's API cannot be called from a
browser. See [api-truth.md](references/api-truth.md) for why.

| Platform | Works | Note |
|---|---|---|
| Emergent | Yes | full-stack |
| Replit Agent | Yes | full-stack |
| v0 | Yes | via route handlers |
| Lovable | Yes | needs a Supabase edge function |
| Claude Code / Cursor | Yes | packs read as plain markdown |
| Bolt.new | Fragile | WebContainer, no persistent server |

Your platform needs to be able to fetch a URL, since the prompt pulls the catalogue and
the reference files itself.

---

## Adding a solution

Write one markdown file in [references/](references/) and add it to
[references/index.md](references/index.md).

Nothing else changes. Not the prompt, not this README's copy block, not anything a
customer has already pasted.
