---
name: Dossier
description: Brand impersonation intelligence for the phone channel — a white-ground neubrutalist system where black is a full surface and green is a rationed accent.
colors:
  green: "#44DD4E"
  green-deep: "#23A631"
  green-text: "#157A24"
  paper: "#FFFFFF"
  paper-tint: "#F1F1F1"
  ink: "#0B0B0B"
  black: "#000000"
  ink-panel: "#141414"
  ink-line: "#2A2A2A"
  grey-1: "#232323"
  grey-2: "#4A4A4A"
  grey-3: "#9B9B9B"
  grey-4: "#CFCFCF"
typography:
  display:
    fontFamily: "Anton, Arial Narrow, sans-serif"
    fontSize: "clamp(2.7rem, 6.4vw, 5.1rem)"
    fontWeight: 400
    lineHeight: 0.92
    letterSpacing: "-0.01em"
  headline:
    fontFamily: "Anton, Arial Narrow, sans-serif"
    fontSize: "clamp(2.2rem, 5.5vw, 4rem)"
    fontWeight: 400
    lineHeight: 0.92
    letterSpacing: "-0.01em"
  title:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "1.15rem"
    fontWeight: 800
    lineHeight: 1.05
    letterSpacing: "-0.02em"
  lede:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "clamp(1.1rem, 1rem + 0.7vw, 1.4rem)"
    fontWeight: 500
    lineHeight: 1.4
  body:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "JetBrains Mono, ui-monospace, monospace"
    fontSize: "0.72rem"
    fontWeight: 700
    letterSpacing: "0.08em"
  data:
    fontFamily: "JetBrains Mono, ui-monospace, monospace"
    fontSize: "0.74rem"
    fontWeight: 400
    letterSpacing: "0.02em"
    fontFeature: "tnum 1"
rounded:
  none: "0"
  beat: "50%"
spacing:
  hair: "2px"
  border: "3px"
  border-heavy: "4px"
  xs: "0.3rem"
  sm: "0.6rem"
  md: "1rem"
  card: "1.3rem"
  gap: "clamp(1rem, 2.5vw, 2rem)"
  section: "clamp(3.5rem, 8vw, 6.5rem)"
  maxw: "1240px"
components:
  button-primary:
    backgroundColor: "{colors.green}"
    textColor: "{colors.black}"
    rounded: "{rounded.none}"
    padding: "0.85rem 1.4rem"
    typography: "{typography.title}"
  button-primary-hover:
    backgroundColor: "{colors.green}"
    textColor: "{colors.black}"
  button-ghost:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "0.85rem 1.4rem"
  button-ink:
    backgroundColor: "{colors.black}"
    textColor: "{colors.paper}"
    rounded: "{rounded.none}"
    padding: "0.85rem 1.4rem"
  button-lg:
    backgroundColor: "{colors.green}"
    textColor: "{colors.black}"
    padding: "1.05rem 1.8rem"
  input:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "0.85rem 1rem"
  chip:
    backgroundColor: "{colors.green}"
    textColor: "{colors.black}"
    rounded: "{rounded.none}"
    padding: "0.28rem 0.55rem"
    typography: "{typography.label}"
  chip-ink:
    backgroundColor: "{colors.black}"
    textColor: "{colors.paper}"
  chip-open:
    backgroundColor: "transparent"
    textColor: "{colors.grey-2}"
  card:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "{spacing.card}"
  card-ink:
    backgroundColor: "{colors.ink-panel}"
    textColor: "{colors.grey-4}"
    rounded: "{rounded.none}"
    padding: "{spacing.card}"
  enroll-plate:
    backgroundColor: "{colors.green}"
    textColor: "{colors.black}"
    rounded: "{rounded.none}"
    padding: "clamp(1.1rem, 2.2vw, 1.6rem)"
  nav-link:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "0.5rem 0.7rem"
---

# Design System: Dossier

## Overview

**Creative North Star: "The Evidence Desk"**

Dossier is a neubrutalist evidence desk: white paper on the table, black ink pressed hard into it, and one live green light that only turns on when something has actually resolved. Every surface is a physical card with a 3px black edge and a zero-blur offset shadow, as if each block had been laid on top of the page rather than rendered into it. Nothing glows, nothing blurs, nothing floats on a soft gradient — depth is carried entirely by hard edges and displaced shadow.

The system runs on three grounds and no more: pure white (`#FFFFFF`) as the default page, one neutral band (`#F1F1F1`) for zebra rows and a single section, and true black (`#000000`) as a full inverted surface that owns whole regions of the page — the thesis strip, the campaign index, the closing CTA, the footer, one step card, one note card. Black is not a text colour that occasionally becomes a background; it is a co-equal ground, and any surface sitting on it uses its own darker card fill (`#141414`) and hairline (`#2A2A2A`) rather than white.

Green is the smallest part of the system and the loudest. It is rationed to a fixed list — the single conversion plate, chips and small marks, the focus ring, the headline's third line, and the footer's top rule — and appears nowhere else. Density is high in data regions (mono, 0.7–0.76rem, tight cells) and deliberately loose in narrative regions (68ch paragraphs, poster headlines at up to 5.1rem). The world refuses the near-black neon SOC dashboard and its opposite, the friendly pastel consumer-app palette.

**Key Characteristics:**
- Hard 3px/4px black borders on every container and control; zero radius everywhere except one 10px status dot.
- Zero-blur offset shadows (`6px 6px 0`, `4px 4px 0`, `10px 10px 0`) instead of ambient depth.
- Black as a full ground, not just a text colour, across six named regions.
- Green as a rationed accent on a closed list, never as a field.
- Anton poster display, Archivo heavy sans, JetBrains Mono for anything that is data.
- Press physics: every control moves into its own shadow on hover and lands flush on active.

## Colors

A three-value world — white ground, black ink and surface, one green accent — extended only by the greys that black surfaces force into existence.

### Primary
- **Signal Green** (`#44DD4E`): The single accent. Fills the one conversion plate, the chip default, the hover/tick marks, the FAQ plus, the checkbox check, the focus halo, the footer's top rule, and every the ledger's live beat, and the thesis highlight. It is never a section ground.
- **Deep Green** (`#23A631`): Large display type on white only — the headline's third line. Chosen because Signal Green fails legibility at text weight on white.
- **Text Green** (`#157A24`): Small green text on light grounds (inline emphasis in mono notes, assembled counts in the ledger, the caret). Never used as a fill.

### Neutral
- **Paper** (`#FFFFFF`): The page ground and every light card fill.
- **Band Grey** (`#F1F1F1`): The one neutral shade — zebra rows in the ledger, the ledger foot, and the single grey band section.
- **Ink** (`#0B0B0B`): Body text on light grounds.
- **True Black** (`#000000`): All borders, all hard shadows, and the full inverted surface.
- **Panel Ink** (`#141414`): Card fill for anything sitting on a black surface.
- **Panel Line** (`#2A2A2A`): Hairline, divider and offset shadow on a black surface, where black-on-black would disappear.
- **Grey 1** (`#232323`) / **Grey 2** (`#4A4A4A`): Body copy inside light cards; mono meta on light.
- **Grey 3** (`#9B9B9B`) / **Grey 4** (`#CFCFCF`): Mono meta and body copy on black.

### Named Rules
**The Rationed Green Rule.** Green appears only on this closed list: the single conversion plate, chips and small marks, the focus ring, the headline's third line, and the footer's top rule. A new surface does not get to add a sixth use. If something needs emphasis and is not on the list, it gets black.

**The Two Greens Rule.** `#44DD4E` is a fill colour, not a text colour. On white, display type uses Deep Green and small text uses Text Green; on black, `#44DD4E` is the text colour and needs no substitute.

**The Black-Surface Rule.** On a black ground, cards fill with Panel Ink, edges and offset shadows use Panel Line, and body copy uses Grey 4 — never white borders, never black-on-black shadows.

## Typography

**Display Font:** Anton (with Arial Narrow, sans-serif)
**Body Font:** Archivo (with system-ui, sans-serif)
**Label/Mono Font:** JetBrains Mono (with ui-monospace, monospace)

**Character:** Anton is a condensed poster face used only in uppercase and only at scale — it shouts the argument. Archivo carries the reasoning at weight 800 for headings and 400–600 for prose; JetBrains Mono handles everything that is evidence: labels, counts, fragments, spec rows, footnotes.

### Hierarchy
- **Display** (400, `clamp(2.7rem, 6.4vw, 5.1rem)`, 0.92 line-height, uppercase): Page headline only. Hand-broken across three lines.
- **Headline** (400, `clamp(2.2rem, 5.5vw, 4rem)`, 0.92, uppercase): Section openers, in Anton, on both white and black grounds. A third Anton step (`clamp(1.6rem, 3.2vw, 2.4rem)`) exists for panel-scale display.
- **Title** (Archivo 800, 1.02–1.25rem, 1.05, uppercase, `-0.02em`): Card and step headings, FAQ questions, ledger heads.
- **Lede** (500, `clamp(1.1rem, 1rem + 0.7vw, 1.4rem)`, 1.4, max 34ch in hero / 60ch in section heads): The one-sentence framing under a headline.
- **Body** (400–500, 0.9–1rem, 1.55, max 68ch): Card and section prose.
- **Label** (JetBrains Mono 700, 0.72rem, `0.08em`, uppercase): Field labels, panel titles, footer column heads, chips (at `0.06em`).
- **Data** (JetBrains Mono 400–700, 0.70–0.78rem, tabular numerals): Cell fragments, counts, spec definitions, ledger meta, disclosure notes.

### Named Rules
**The Evidence-Is-Mono Rule.** If a value could be cited — a count, a callback number, a fragment, a timestamp, a spec — it is JetBrains Mono with tabular numerals. If it is an argument, it is Archivo. Never mix the two inside one sentence except as deliberate inline emphasis.

**The Anton-Uppercase Rule.** Anton appears only uppercase, only at display sizes, and never below `1.6rem`. It is never used for body, labels, or buttons.

## Layout

A single centred column, `min(100% - 2.5rem, 1240px)`, with section rhythm at `clamp(3.5rem, 8vw, 6.5rem)` of vertical padding and a shared inter-card gap of `clamp(1rem, 2.5vw, 2rem)`. Full-bleed grounds (black sections, the grey band) run edge to edge and re-enter the container inside; they are bordered top and bottom with the 4px heavy rule.

Asymmetric two-column grids are the default composition: hero at `1.05fr 0.95fr` (copy left, the monogram owning the right half), thesis at `1.3fr 1fr`, the brand-value block at `1.1fr 0.9fr`, the closing CTA at `1.1fr 0.9fr`, the footer at `1.4fr 1fr 1fr`. Symmetric grids appear only for peer content: the six-up step grid (`repeat(3, 1fr)`), the FAQ and brand-card pairs.

Breakpoints are content-driven rather than device-driven: 1120px (nav links collapse to the CTA alone), 900px (hero stacks), 820px (thesis, steps to 2-up, brand block, closing CTA stack), 720px (FAQ, brand cards, footer), 680px (ledger rows stack to one column, right-aligned figures go left), 560px (panel cells to 2-up, hero compresses so the enroll plate stays inside a 390×844 viewport), 540px (steps to 1-up), 460px (nav and mark shrink; the enroll row goes single-column).

**The Fold Rule.** The conversion plate sits in the headline column, directly under the headline, and its submit stays inside the first viewport on both phone and desktop. Hero spacing compresses at 560px specifically to hold this — no surface may push it below the fold.

## Elevation & Depth

No blur exists anywhere in the system. Depth is entirely displacement: a solid, zero-blur offset shadow in the same colour as the border, so every block reads as a physical card resting a few millimetres above the page with a hard cast edge. There is no ambient shadow, no elevation ramp, no translucency, no backdrop filter.

### Shadow Vocabulary
- **Standard** (`box-shadow: 6px 6px 0 #000000`): Cards, steps, note cards, brand cards, the core block.
- **Small** (`box-shadow: 4px 4px 0 #000000`): Buttons at rest, chips-in-nav hover, the FAQ card, the step numeral tile.
- **Large** (`box-shadow: 10px 10px 0 #000000`): The two page-level objects — the conversion plate and the ledger.
- **On-black** (`box-shadow: 6px 6px 0 #2A2A2A` / `10px 10px 0 #2A2A2A`): The same three weights, cast in Panel Line, for any card sitting on a black surface.

### Named Rules
**The Press Rule.** Controls move into their own shadow. Hover translates `2px, 2px` and halves the shadow; active translates the full `6px, 6px` and drops the shadow to zero, so the control lands flush on the page. Transition is `90ms cubic-bezier(.2,.9,.3,1)` and nothing else moves.

**The Matched-Shadow Rule.** A shadow is always the same colour as its element's border. Never cast a black shadow on a black ground, and never blur one.

## Shapes

Zero radius, universally. Every container, control, chip, input, checkbox, cell and tile is a hard rectangle; the only curve in the system is the 10px live beat dot, which is round because it is a light, not a box. Borders are the primary form language and come in exactly two weights: 3px for standard containers and controls, 4px for page-level objects and section rules (the conversion plate, the ledger, the sticky nav's bottom edge, the top/bottom rules on full-bleed sections, the footer's green top rule). Thin 2px rules do the internal work — ledger row separators, spec-row dividers, chip edges, legend keys, small dividers on black.

Two textures exist as meaning, not decoration: a `-45deg` repeating stripe (7px/7px, white to `#F0F0F0`) marks a ledger row that has not resolved, and a dashed 2px grey edge marks an unresolved fragment chip. Both encode absence; neither is available as ornament.

## Components

### Buttons
- **Shape:** Hard rectangle (0 radius), 3px black border.
- **Primary:** Signal Green fill, black label, Archivo 800 uppercase 1rem, padding `0.85rem 1.4rem`, small offset shadow. Optional inline arrow SVG that nudges 3px right on hover.
- **Hover / Focus:** Press physics (see The Press Rule). Focus uses the global dual ring.
- **Ghost:** White fill, ink label, same border and shadow. **Ink:** black fill, white label. **Large:** `1.15rem` type, `1.05rem 1.8rem` padding, standard shadow. **Block:** full width, centred.
- **Disabled:** 50% opacity, shadow frozen at rest, no press.

### Chips
- **Style:** Mono 700, 0.72rem, uppercase, `0.06em`, 2px black border, padding `0.28rem 0.55rem`, zero radius.
- **Variants:** Green fill (default), ink fill on light grounds, white fill on dark. **Open** (`chip--open`) is transparent with a dashed grey edge and grey text — an unresolved fragment, where the absence of fill is the information.

### Cards / Containers
- **Corner Style:** 0 radius.
- **Background:** White on light grounds; Panel Ink on black grounds.
- **Shadow Strategy:** Standard offset (see Elevation).
- **Border:** 3px black on light; 3px Panel Line on black.
- **Internal Padding:** `1.2–1.3rem` for note and step cards; `clamp(1.4rem, 3vw, 2.2rem)` for the large content card.

### Inputs / Fields
- **Style:** White fill, 3px black border, 0 radius, `0.85rem 1rem` padding, Archivo 600 at `1.05rem`, mono label above. Green caret.
- **Focus:** The border does not move; a 4px green inset ring animates in over 120ms, so the field fills inward.
- **Error:** A 4px black inset ring plus a faint warm tint, with a mono error line beneath in black.
- **Checkbox:** 24×24 white square with a 3px black edge; checked fills black with a green tick drawn from borders.
- **Focus (global):** Dual ring — 3px solid black outline at 2px offset, plus a 6px green halo — so the ring survives on white, black, and green grounds alike.

### Navigation
- Sticky, white ground, 4px black bottom rule. Brand lockup is the DO monogram (26px) + a 2px black vertical rule + "DOSSIER" in Anton at `1.7rem`. Links are Archivo 700 uppercase `0.88rem` with a transparent 3px border that becomes black with a white fill and a small offset shadow on hover — the link becomes a card. One alternate link (`nav__link--alt`) is sentence-case, underlined 2px, and drops the underline on hover. Below 1120px the link row is hidden and only the CTA remains.

### Hero Monogram (signature)
The DO mark at page scale, and the only place in the system where an asset is used as composition rather than as identity. `dossier_mark.png` is absolutely positioned inside the hero at `left: 52%`, `width: 88vw`, `opacity: 0.5`, `max-width: none`, `z-index: 0` — so it owns the hero's right half, runs off the right edge of the page (clipped by the body's `overflow-x: hidden`), and is deliberately never seen whole. `pointer-events: none`, `user-select: none`, `alt=""`, `aria-hidden`: it carries no meaning a screen reader needs.

`.hero__grid` and `#enroll` are raised to `z-index: 1` above it, so the conversion plate crosses over the monogram's lower left and takes a bite out of it. That overlap is the point — the plate reads as sitting *on* the page rather than beside the mark.

**Named rule — The Half-Mark Rule.** When the monogram is used as composition it is always cropped by the viewport and always crossed by a foreground object. A version that fits entirely on screen, or floats clear of everything, is decoration and is off-system. At 50% black on white it lands on `#808080`, so nothing but a foreground surface may sit on top of it: no body copy, no green display type, no small marks.

Below 900px the copy goes full width and the plate is nearly page-wide, so there is no right half to bleed into. The monogram drops to `bottom: 0.75rem; left: 22%; width: 135vw`, its top hidden by the plate and one band of its lower edge running off the right, and the hero's bottom padding opens to `clamp(5.5rem, 24vw, 9rem)` to hold it.

### Ledger
A white table on a black section: 4px black edge, Panel Line offset shadow, black head bar with a green live beat, rows on a `1.4fr 1fr 0.8fr` grid with 2px black separators and Band Grey zebra striping. A row that has not resolved (`ledger__row--open`) is diagonally hatched and carries dashed open chips; its figures drop to grey. Below 680px rows stack and the right-aligned figures go left.

### Conversion Plate
The single green field on the page, because it is the single action: Signal Green fill, 4px black edge, large offset shadow, mono labels, a two-up field row collapsing to one at 460px, an inline consent line, and a block submit. The same plate reappears once at the close of the page on a black surface (`enroll--close`) where its shadow is cast in Panel Line. On success it swaps the form for a confirmation panel and moves focus to its heading.

### Spec List
A chain-of-custody definition list: 6rem mono uppercase terms against mono grey definitions, separated by 2px black rules, no bullets, no card of its own beyond the note card holding it.

## Do's and Don'ts

### Do:
- **Do** keep green on its closed list — the conversion plate, chips and small marks, the focus ring, the headline's third line, the footer top rule.
- **Do** cast every shadow zero-blur, offset, and in the same colour as the element's border (`#000` on light, `#2A2A2A` on black).
- **Do** use black as a whole ground when a section is a change of register, and switch its cards to Panel Ink / Panel Line / Grey 4 when you do.
- **Do** give every control the press physics: `2px` in on hover with a halved shadow, full `6px` in on active with no shadow.
- **Do** set anything citable — counts, fragments, callback numbers, spec rows — in JetBrains Mono with tabular numerals.
- **Do** hold body measure at 68ch and hero ledes at 34ch.
- **Do** provide a static, causally consistent resolved state for `prefers-reduced-motion` and for no-JS, not a frozen mid-animation frame.

### Don't:
- **Don't** let green become a section ground or a large field; the plate is the only green surface at scale.
- **Don't** set `#44DD4E` as text on white — use Deep Green for display, Text Green for small text.
- **Don't** introduce a corner radius; the only round thing in the system is the live beat dot.
- **Don't** blur a shadow, add a gradient, or use translucency to imply depth.
- **Don't** use Anton below `1.6rem`, in sentence case, or for buttons and labels.
- **Don't** use the hatch texture or the dashed open chip decoratively; both mean "unresolved."
- **Don't** carry the retired warm-paper grounds, per-claim fee treatments, or thesis sequence numerals back in — the ground is white, the band is `#F1F1F1`, and nothing else.

### Headroom (unspent, deliberately)
Three devices this world owns but has not yet used, recorded so they are not lost: the DO monogram appears only at ~26–30px and has never been used at poster scale or as a knockout on a black ground; rotation is spent exactly once, on the MATCHED stamp (`-3deg` → `-7deg`), and is available nowhere else; and every black section is currently a padded band with a left-aligned heading and an empty right half. Any of the three is legitimate to spend on a future surface.
