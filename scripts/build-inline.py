#!/usr/bin/env python3
"""
Build self-contained prompts for platforms that cannot fetch a URL.

Some AI-coding platforms (Emergent among them) run in a sandbox with no outbound
web access, so the bootloader's fetch step fails. This concatenates the bootloader,
api-truth.md and one solution pack into a single paste.

One file per solution, because picking the solution on the website removes the need
to ask Q1 and keeps each paste as short as it can be.

Usage:  python3 scripts/build-inline.py
"""

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
REFS = ROOT / "references"
OUT = ROOT / "inline"

HEADER = """You are going to build an application on top of Dreamteam CRM data.

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
"""


def demote(text: str) -> str:
    """Push headings down two levels so the embedded docs sit under their section."""
    return re.sub(r"^(#{1,4}) ", lambda m: "#" * min(len(m.group(1)) + 2, 6) + " ",
                  text, flags=re.M)


def strip_cross_refs(text: str) -> str:
    """Nothing is fetchable here, so pointers to other files would mislead."""
    text = text.replace(
        "**Read `api-truth.md` first.** Everything about auth, pagination and the traps lives\n"
        "there and is not repeated here.",
        "**Read the Dreamteam API reference at the end of this message first.** Auth,\n"
        "pagination and the traps live there and are not repeated here.")
    # "`api-truth.md` section 2" must not become "...this message section 2"
    text = re.sub(r"`api-truth\.md`(,?\s+)(section\b)",
                  r"the API reference at the end of this message,\1\2", text)
    return text.replace("`api-truth.md`", "the API reference at the end of this message")


def main() -> int:
    api_truth = (REFS / "api-truth.md").read_text()
    packs = sorted(p for p in REFS.glob("*.md")
                   if p.name not in {"api-truth.md", "index.md"})

    if not packs:
        print("no solution packs found in references/")
        return 1

    OUT.mkdir(exist_ok=True)
    for pack in packs:
        body = "\n\n".join([
            HEADER.rstrip(),
            "# The solution to build\n",
            demote(strip_cross_refs(pack.read_text())).strip(),
            "\n---\n",
            "# Dreamteam API reference\n",
            demote(api_truth).strip(),
        ])
        dest = OUT / pack.name
        dest.write_text(body + "\n")
        print(f"  {dest.relative_to(ROOT)}  ({len(body.split()):,} words)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
