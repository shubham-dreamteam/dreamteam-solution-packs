# Design standard

Load this on every build, alongside the API reference.

The brief is **calm, not loud**. The apps this produces are looked at every morning by
someone who already knows their business. They should feel like a well-set page, not a
control room. Impact comes from restraint, precision and typography. Never from
saturation, glow, or motion.

If a choice would make the page more exciting but less quiet, it is the wrong choice.

---

## 1. What "wow" means here

It is not colour. It is these, in order:

1. **The number is the object.** Large, light-weight, tabular figures, generous space
   around it. A well-set 56px figure with one line of context beneath it beats any
   chart treatment.
2. **Alignment you can feel.** One grid, consistent gutters, optical alignment of
   numerals. Most dashboards fail here and it reads as cheapness even when nobody can
   name why.
3. **One accent, used rarely.** A single hue, carrying the one thing that matters on
   the screen. Everything else is ink and surface. An accent used four times is not an
   accent.
4. **Density without crowding.** Show the real numbers, not rounded summaries, but give
   them room. Tables are good. Tables are often better than charts.
5. **Nothing decorative.** No element exists that does not carry data or structure.

## 2. Hard prohibitions

These read as "poppy" and are not permitted:

- Gradients on data marks. Flat fills only. A gradient on a bar makes its value
  ambiguous.
- Drop shadows on cards or tiles. Separate with a 1px hairline or a surface step.
- Glow, neon, saturated backgrounds, coloured card fills.
- More than one accent hue on a screen.
- Full-width coloured banners or hero blocks.
- Rounded corners above 8px on containers, above 4px on data marks.
- Emoji as iconography.
- Animated counters, ticking numbers, progress animations on load.
- Looping or ambient motion of any kind.
- Confetti, celebration states, gamification.

## 3. Typography

- **One family.** Inter unless the customer's site gives you a better-justified
  choice. No pairing a display face with a body face.
- **Numerals: tabular, always** (`font-variant-numeric: tabular-nums`). Columns of
  figures that do not align vertically are the single most common tell of a
  generated dashboard.
- **Weight carries hierarchy, size carries scale.** Headline figures go *lighter* as
  they go larger, not bolder. A 56px number at weight 300 reads calm; at 700 it shouts.
- **Labels and axis text**: 11 to 12px, letter-spaced slightly, in muted ink, often
  uppercase. They should recede.
- **Sentence case** for headings. Not Title Case.

## 4. Colour

Follow this order. Colour is chosen **last**, after the form.

**Assign by the job the colour does:**

| Job | Rule |
|---|---|
| Magnitude (more is more) | **Sequential**: one hue, light to dark. The safe default. |
| Identity (which series is which) | **Categorical**: fixed hue order, never cycled |
| Polarity (above/below, good/bad) | **Diverging**: two opposed hues, neutral grey midpoint |
| State (healthy/at risk/failed) | **Status**: reserved tokens, never reused as a series |

**Non-negotiable:**

- Sequential is the default. Reach for categorical only when the series genuinely
  *are* the subject.
- **Never a rainbow ramp** for magnitude. One hue.
- **Never a hue at a diverging midpoint.** The middle must read as "nothing".
- **Colour follows the entity, never its rank.** Filtering out a series must not
  repaint the survivors. Someone who learned "Outbound is blue" must not be misled.
- **Never generate a 9th categorical hue.** Past eight, fold the tail into "Other" or
  facet into small multiples.
- **Never put a value-ramp on unordered categories.** Colouring each bar
  darker-where-bigger double-encodes the length the chart already shows.
- **Status colours are reserved.** They ship with an icon and a label, never colour
  alone.
- **Text wears text tokens, never the series colour.** A coloured mark next to a
  neutral-ink label carries the identity.

**Contrast and colourblindness:** adjacent categorical hues must remain separable
under deuteranopia and protanopia. If you cannot verify that, reduce to three or fewer
series and add direct labels. Do not eyeball a large palette and assume it is fine.

**Dark mode is designed, not flipped.** Pick its own steps from the same hues against
the dark surface. An inverted light palette produces glowing, oversaturated marks,
which is exactly the failure this document exists to prevent. Both modes ship.

## 5. Choosing the form

Pick the form from the data's job, before touching colour.

| The data is | Use | Not |
|---|---|---|
| One current value | **Stat tile**: figure, label, optional delta | a one-bar bar chart |
| A few headline numbers | **KPI row** of stat tiles | a grouped bar chart |
| The number the page leads with | **Hero figure**, 48px or larger | anything else |
| One ratio against a limit | **Meter** on a same-hue track | a two-slice pie |
| More than about seven meaningful classes | **A table**, possibly with inline bars | more colours |
| Magnitude across categories | bar or column; **heatmap** for a grid | pie |
| Change over time | line; area for a single series | stacked area for many |
| One series matters, the rest are context | **Emphasis**: one accent, rest in grey | eight categorical hues |
| Above or below a baseline | diverging bar | two-colour arbitrary bars |
| Ordered-scale share, for example sentiment | **diverging stacked bar**, centred on neutral | grouped bars |

**Emphasis is the most underused form and usually the right answer.** If the story is
"this one is the problem", that is one accent series and everything else in
de-emphasis grey. Not a palette.

**A table is a legitimate visualisation.** For seven sources or twelve owners, a table
with a right-aligned numeric column and a thin inline bar is clearer, calmer and more
precise than any chart. Use it without apology.

## 6. Marks and chrome

- **Thin marks.** Bars slim with space between them, lines 2px, points 8px or more.
- **Rounded data-ends at 4px**, anchored flat to the baseline. Never round both ends
  of a bar.
- **2px surface-coloured gap** between adjacent fills and stacked segments, and a 2px
  surface ring where marks overlap. This one detail separates competent charts from
  amateur ones.
- **Grid and axes recede.** Hairline weight, muted ink, horizontal gridlines only.
  Often no vertical gridlines at all. Never a box frame around the plot.
- **No axis line where the bars already imply one.**
- **Label selectively.** Direct-label the first, last and extreme points. Never a
  number on every point. If every point needs a number, you wanted a table.
- **Legend for two or more series, always.** One series needs no legend, the title
  names it. Four or fewer series get direct labels as well, so identity never depends
  on colour alone.

## 7. Interaction

- **Hover is expected, not optional.** Crosshair and tooltip on lines and areas,
  per-mark tooltip on bars, cells and points. The only thing that skips it is a bare
  stat tile.
- Hit targets larger than the mark.
- Filters in a single row above the content, never in a sidebar for a single-screen
  dashboard.
- **Transitions: one, short, and only on state change.** 150 to 250ms, ease-out.
  Nothing animates on page load. Nothing loops.
- Honour `prefers-reduced-motion` by removing transitions entirely.

## 8. Layout

- Establish one column grid and keep every card on it.
- Vertical rhythm from a single spacing scale, for example 4, 8, 12, 16, 24, 32, 48.
- **The lead insight goes above the charts, as a sentence in plain language**, at
  headline size. "899 of 918 unqualified contacts were dropped without a meeting" is
  the product. The table underneath is the evidence.
- Cards separated by hairlines or surface steps, never shadows.
- Empty and error states get the same care as the populated view. An error state names
  the failing call and its status code, never a business explanation.

## 9. Copy

Minimal and plain. Where you do not know what should go somewhere, write less.

No marketing language, no invented value propositions, no filler headings, no taglines.
Do not explain what a chart obviously shows. Do explain a definition the reader cannot
infer, for example what counts as a completed meeting, and put it below the chart in
muted ink.

## 10. Before you call it done

- Open the rendered page and look at it. Check for label collisions, overflow, and
  numbers that do not align.
- Check it against section 2. If any prohibition is present, it is wrong.
- Check both light and dark mode, on the real data, not placeholders.
- Check it at a narrow width. Wide tables scroll inside their own container; the page
  itself never scrolls sideways.
