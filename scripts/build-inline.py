#!/usr/bin/env python3
"""
Build self-contained prompts for platforms that cannot fetch a URL.

Some AI-coding platforms (Emergent among them) run in a sandbox with no outbound
web access, so the bootloader's fetch step fails. This concatenates the bootloader,
api-truth.md and one solution pack into a single paste.

One file per solution, because picking the solution on the website removes the need
to ask which one, and keeps each paste as short as it can be.

Everything is derived from PROMPT.md and references/. Nothing is duplicated here, so
a rule added to PROMPT.md automatically reaches the inline builds. An earlier version
kept its own copy of the build rules and silently drifted two releases behind.

Usage:  python3 scripts/build-inline.py
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REFS = ROOT / "references"
OUT = ROOT / "inline"

PREAMBLE = """You are going to build an application on top of Dreamteam CRM data.

Everything you need is in this message. Do not try to fetch any URL. If you cannot
reach the internet, that is fine and expected.

## STOP. Do not write any code yet.

Ask me the questions in the next section first. Do not scaffold a project, do not
create files, do not "start with a basic version".

## Ask me these questions
"""

# Rule 5 tells the agent to fetch a website. On a platform that reached for the inline
# build, that will usually fail, so lead with the fallback instead of burying it.
NO_WEB_NOTE = (
    "\n\nYou are probably running somewhere without web access, since that is why you\n"
    "were given this self-contained version. In that case say so plainly, then either\n"
    "ask me to paste our brand colours and logo URL, or use the fallback above.\n"
)


def section(text: str, start: str, end: str | None) -> str:
    """Slice a markdown document between two headings."""
    i = text.index(start)
    j = text.index(end, i) if end else len(text)
    return text[i:j].rstrip()


def build_questions(prompt: str) -> str:
    """Reuse PROMPT.md's questions, minus the one the filename already answers."""
    q = section(prompt, "**Q1. Which solution", "## Step 3")

    # Drop Q1: choosing this file already chose the solution.
    q = q[q.index("**Q2. Who is allowed to sign in?**"):]

    # Renumber, and fix the cross-reference inside Q3.
    q = q.replace("**Q2. Who is allowed to sign in?**", "**Q1. Who is allowed to sign in?**")
    q = q.replace("**Q3.** (only if I chose 2b)", "**Q2.** (only if I chose 1b)")
    q = q.replace("The reference pack declares", "The solution below declares")

    # Nothing is fetchable, so the SETUP.md link cannot be followed.
    q = re.sub(
        r"- \*\*My API key\.\*\*.*?SETUP\.md",
        "- **My API key.** If I do not have one, tell me to open my Dreamteam profile,\n"
        "    scroll to API Token, and click Reveal then Copy.",
        q, flags=re.S)

    return q.rstrip()


def build_rules(prompt: str) -> str:
    rules = section(prompt, "## Non-negotiable build rules", "## If the catalogue fetch failed")

    # Platform hints that assume a fetchable repo, and the pointer to the pack file.
    rules = rules.replace(
        "`api-truth.md` has the exact rules.",
        "The API reference at the end of this message has the exact rules.")
    rules = rules.replace(
        "beyond what the reference pack asks for. If the pack says read-only",
        "beyond what the solution below asks for. If it says read-only")
    rules = rules.replace(
        "**`references/design.md` is binding**",
        "**the Design standard at the end of this message is binding**")

    # Surface the no-web fallback inside the branding rule.
    anchor = "dark variant of it."
    if anchor in rules:
        rules = rules.replace(anchor, anchor + NO_WEB_NOTE, 1)

    return rules.rstrip()


def demote(text: str) -> str:
    """Push headings down two levels so embedded docs sit under their section."""
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
    text = text.replace("`design.md`", "the Design standard at the end of this message")
    return text.replace("`api-truth.md`", "the API reference at the end of this message")


def main() -> int:
    prompt = (ROOT / "PROMPT.md").read_text()
    api_truth = (REFS / "api-truth.md").read_text()
    design = (REFS / "design.md").read_text()
    packs = sorted(p for p in REFS.glob("*.md")
                   if p.name not in {"api-truth.md", "design.md", "index.md"})

    if not packs:
        print("no solution packs found in references/", file=sys.stderr)
        return 1

    head = "\n\n".join([PREAMBLE.rstrip(), build_questions(prompt), build_rules(prompt)])

    OUT.mkdir(exist_ok=True)
    for pack in packs:
        body = "\n\n".join([
            head,
            "\n---\n",
            "# The solution to build\n",
            demote(strip_cross_refs(pack.read_text())).strip(),
            "\n---\n",
            "# Dreamteam API reference\n",
            demote(api_truth).strip(),
            "\n---\n",
            "# Design standard\n",
            demote(design).strip(),
        ])
        for ref in ("api-truth.md", "design.md", "index.md", "SETUP.md",
                    "raw.githubusercontent"):
            if ref in body:
                print(f"  FAIL: {pack.name} still points at {ref}", file=sys.stderr)
                return 1

        dest = OUT / pack.name
        dest.write_text(body + "\n")
        print(f"  {dest.relative_to(ROOT)}  ({len(body.split()):,} words)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
