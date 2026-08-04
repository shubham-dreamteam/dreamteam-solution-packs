#!/usr/bin/env python3
"""
Build the self-contained prompt, for platforms that cannot fetch a URL.

Produces ONE file: inline/PROMPT-ALL.md. It contains the bootloader, the catalogue,
every solution pack, the API reference and the design standard, glued together.

It keeps the catalogue mechanic. The agent still asks which solution the customer
wants and still presents the list, it just reads that list from further down the same
message instead of fetching it. An earlier version wrote one file per solution, which
made the customer choose on the website and defeated the point of having a catalogue.

Everything is derived from PROMPT.md and references/. Nothing is duplicated here, so a
rule added to PROMPT.md reaches the inline build automatically. An earlier version kept
its own copy of the build rules and silently drifted two releases behind.

Usage:  python3 scripts/build-inline.py
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REFS = ROOT / "references"
OUT = ROOT / "inline"
DEST = OUT / "PROMPT-ALL.md"

PREAMBLE = """You are going to build an application on top of Dreamteam CRM data.

Everything you need is in this message. Do not try to fetch any URL. If you have no
web access, that is fine and expected.

## STOP. Do not write any code yet.

Ask me the questions below first, and wait for my answers. Do not scaffold a project,
do not create files, do not "start with a basic version".

## Ask me these questions
"""

# The branding rule tells the agent to fetch a website. Anyone using this build probably
# cannot, so surface the fallback rather than leaving it buried.
NO_WEB_NOTE = (
    "\n\nYou are probably running somewhere without web access, since that is why you\n"
    "were given this self-contained version. In that case say so plainly, then either\n"
    "ask me to paste our brand colours and logo URL, or use the fallback above.\n"
)

# Anything naming a file the agent cannot fetch is a bug in the generated prompt.
FORBIDDEN = ("api-truth.md", "design.md", "index.md", "SETUP.md", "raw.githubusercontent")


def section(text: str, start: str, end: str | None) -> str:
    """Slice a markdown document between two markers."""
    i = text.index(start)
    j = text.index(end, i) if end else len(text)
    return text[i:j].rstrip()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    """Substitute, and fail loudly if the anchor has moved.

    A silent no-match here previously shipped a prompt pointing at an unfetchable file.
    """
    if old not in text:
        raise SystemExit(f"build-inline: anchor not found for {label!r}. "
                         f"PROMPT.md wording changed; update this script.")
    return text.replace(old, new, 1)


def build_questions(prompt: str) -> str:
    """Reuse PROMPT.md's questions verbatim, repointing the fetches."""
    q = section(prompt, "**Q1. Which solution", "## Step 3")

    q = replace_once(
        q,
        "List the options from the catalogue you just fetched, plus \"something else\".",
        "List the options from the catalogue further down this message, under\n"
        "\"Available solutions\". Read them out to me by name, and add \"something else\".",
        "Q1 catalogue source")
    q = q.replace("If I pick \"something else\", you will use `references/api-truth.md` only.",
                  "If I pick \"something else\", use only the API reference and design standard\n"
                  "at the end of this message.")
    q = q.replace("The reference pack declares", "The chosen solution declares")

    # SETUP.md cannot be opened from here.
    q = re.sub(
        r"- \*\*My API key\.\*\*.*?SETUP\.md",
        "- **My API key.** If I do not have one, tell me to open my Dreamteam profile,\n"
        "    scroll to API Token, and click Reveal then Copy.",
        q, flags=re.S)

    return q.rstrip()


def build_rules(prompt: str) -> str:
    rules = section(prompt, "## Non-negotiable build rules", "## If the catalogue fetch failed")

    rules = replace_once(
        rules, "`api-truth.md` has the exact rules.",
        "The API reference at the end of this message has the exact rules.",
        "rule 2 api-truth pointer")
    rules = replace_once(
        rules, "beyond what the reference pack asks for. If the pack says read-only",
        "beyond what the chosen solution asks for. If it says read-only",
        "rule 4 pack pointer")
    rules = replace_once(
        rules, "**`references/design.md` is binding**",
        "**the Design standard at the end of this message is binding**",
        "rule 5 design pointer")
    rules = replace_once(
        rules, "dark variant of it.", "dark variant of it." + NO_WEB_NOTE,
        "rule 5 no-web fallback")

    return rules.rstrip()


def demote(text: str, levels: int = 2) -> str:
    """Push headings down so embedded documents nest under their section."""
    return re.sub(r"^(#{1,4}) ",
                  lambda m: "#" * min(len(m.group(1)) + levels, 6) + " ",
                  text, flags=re.M)


def strip_cross_refs(text: str) -> str:
    """Repoint every file reference at a section of this message."""
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


def build_catalogue(index: str, packs: list[pathlib.Path]) -> str:
    """The menu the agent reads out for Q1, with each pack's anchor."""
    lines = [
        "These are the solutions you can offer me. Read the names out for Q1, then use",
        "the matching section under \"The solutions\" below.",
        "",
    ]
    for p in packs:
        body = p.read_text()
        title = next((l[2:].strip() for l in body.splitlines() if l.startswith("# ")), p.stem)
        access = next((l.strip() for l in body.splitlines()
                       if l.startswith("**Access required:**")), "")
        lines.append(f"- **{title}** (`{p.stem}`)")
        if access:
            lines.append(f"  {access}")
    lines += ["", "Plus \"something else\", which uses only the API reference and design standard."]
    return "\n".join(lines)


def main() -> int:
    prompt = (ROOT / "PROMPT.md").read_text()
    packs = sorted(p for p in REFS.glob("*.md")
                   if p.name not in {"api-truth.md", "design.md", "index.md"})
    if not packs:
        print("no solution packs found in references/", file=sys.stderr)
        return 1

    parts = [
        PREAMBLE.rstrip(),
        build_questions(prompt),
        build_rules(prompt),
        "\n---\n",
        "# Available solutions\n",
        build_catalogue((REFS / "index.md").read_text(), packs),
        "\n---\n",
        "# The solutions\n",
        "Use only the one I picked in Q1. Ignore the rest.",
    ]
    for p in packs:
        parts += ["\n---\n", demote(strip_cross_refs(p.read_text()), levels=1).strip()]
    parts += [
        "\n---\n", "# Dreamteam API reference\n",
        demote((REFS / "api-truth.md").read_text()).strip(),
        "\n---\n", "# Design standard\n",
        demote((REFS / "design.md").read_text()).strip(),
    ]

    body = "\n\n".join(parts) + "\n"

    for ref in FORBIDDEN:
        if ref in body:
            print(f"  FAIL: generated prompt still points at {ref}", file=sys.stderr)
            return 1

    OUT.mkdir(exist_ok=True)
    DEST.write_text(body)
    print(f"  {DEST.relative_to(ROOT)}  "
          f"({len(body.split()):,} words, {len(packs)} solution(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
