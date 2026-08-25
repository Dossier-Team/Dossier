# Product

<!-- impeccable:product-schema 2 -->

## Platform

web

## Stack

Static HTML/CSS/JS, single self-contained landing page, no framework. Chosen by the user for a one-page marketing surface; trivially deployable to any static host. Deploy target unspecified (portable).

## Users

- **Consumers (supply side):** ordinary people already receiving scam calls that impersonate real brands. Situation: annoyed by spam calls, no current recourse. Job: enroll once (email + phone) so their incoming spam calls feed the capture network. Free to join. They are not paid. The draw is that their phone fights back: the agent wastes the scammer's time, and the user sees where their calls went ("Case #2291: fake Medicare OTC. Your line contributed 3 calls."). Users also get a direct warning when a call impersonated their own bank or provider.
- **Impersonated brands (the customer):** banks, insurers, utilities, retailers, Medicare-style plans. Their name is being used to run scams against their own customers. They buy recurring intelligence and evidence subscriptions. The fraud team is the reader the site's ceiling is built for.
- **Investors:** evaluating a recurring enterprise intelligence business with a consumer-capture moat, not a consumer app play.

## Product Purpose

Dossier answers scam calls with AI agents, maps the impersonation campaigns behind them, and sells the resulting intelligence and evidence to the brands being impersonated. Scam calls only work by naming a brand, so identifying the impersonated brand succeeds on effectively every call. The buyer is solvent by definition.

Revenue is recurring per-brand subscriptions carried by two alert layers, with a third embedded:

1. **Campaign Intel:** maps the operation impersonating the brand (script fingerprints, callback numbers, money routes, wave timing). Fires daily. The substrate and the day-one demo.
2. **Intercepts:** a scammer holding a real customer's credentials attempts OTP or credential extraction on an enrolled phone. Per-account alert the brand can verify against its own auth logs. The primary revenue layer; scales with app density.
3. **Breach Escalation:** a caller recites internal-only data (exact balance, yesterday's transaction), which is deterministic proof the brand's own systems or a vendor leaked. Rare, embedded in the subscription, never priced as a rate.

Success = campaigns captured per vertical, then enterprise subscriptions signed. Enrollment volume matters because the consumer capture channel is the dataset no competitor's honeypot-only approach can produce.

## Positioning

The core thesis: **every scam call names a brand, or the scam doesn't work.** Brands already pay for impersonation defense on domains, social, and deepfakes. Nobody covers the live phone channel. Dossier's agents sit inside the calls themselves, so the brand gets evidence, not screenshots.

The consumer network is the moat: honeypots capture campaigns in the wild, but only real users' phones catch the calls where a scammer holds real customer data. That second category is what a honeypot structurally cannot see.

## Operating Context

How it works, end to end:
1. **Capture:** scam calls arrive on seeded honeypot lines and enrolled users' phones.
2. **Classify:** the agent answers every ambiguous call as a polite receptionist taking a message. Elicitation only begins after high-confidence spam confirmation.
3. **Elicit:** confused-but-cooperative persona keeps the scammer explaining. The agent never asserts a false identity, never expresses purchase interest, never supplies payment info.
4. **Evidence chain:** every call is recorded (disclosed plainly) and locked into a tamper-evident archive (WORM storage, cryptographic hashes, trusted timestamps).
5. **Match:** fragments across calls (scripts, callback numbers, rails) resolve into named campaigns per brand.
6. **Package and sell:** per-brand subscription built on Campaign Intel + Intercepts.
7. **Escalate selectively:** campaigns that clear written pre-committed criteria get deep workup and a law-enforcement referral package the brand can act on. Free to fail; the subscription doesn't depend on it.

## Capabilities and Constraints

- Consumer-facing surface = one marketing landing page with a **single conversion action: consumer signup (email + phone).** No product to log into yet. Signup is the raw material for the capture network, so the signup flow is the page, not a footer form.
- Signup form: fully wired UX (validation, success state) but **stubbed** submit for now (no live backend), placeholder to be connected later.
- Open item: which entity speaks on the consumer-facing site is not yet decided.

### Copy constraints — non-negotiable

- **No payment or income framing anywhere.** Users are not paid and the site must never imply they are. Framing: they're *already* getting these calls; Dossier makes them count for something.
- **No damages figures, loss statistics, or recovery numbers consumer-facing.**
- **Blocking is a stated capability.** Dossier blocks spam calls on enrolled lines — they are intercepted and answered by a Dossier agent rather than ringing through. Copy says so plainly. *(Supersedes the earlier "no protection promises" constraint, changed by the user on 2026-08-24.) Still off-limits: guaranteeing that every call is caught, or implying any wider safety or fraud-loss protection beyond the phone channel.*
- **Recording disclosure must be visible and honest.** The AI agent records every call; the terms say so plainly. The landing page is discoverable evidence and is written accordingly.
- **Any shareable call clips are always scrubbed.** Raw audio can expose a user's own data if a scammer read a real lead list aloud.

## Brand Commitments

- **Name:** Dossier. Lockup: the mark, a 2px black rule, then "Dossier" set in the display face.
- **Logo:** interlocking "DO" monogram. Source asset: `dossier_logoV2.png` (2048×2048, black on white). Derived working assets, trimmed to the mark's true bounding box with transparent counters: `dossier_mark.png` (black ink, for light grounds), `dossier_mark_white.png` (white ink, for black grounds), `dossier_favicon.png` (512×512). Each version must sit on its matching ground — the counters are transparent, so the white mark on a light ground fills in.
- **Brand colors (binding):** white and black, plus **one accent, brand green `#44DD4E`**, user-pinned. Green is an accent, not a field: it is allowed on live/active states, the single conversion plate, chips and small marks, and the focus ring. It never owns a whole section again.
- **Typeface:** Anton for uppercase display, Archivo for body and subheads, JetBrains Mono for labels and data. *(Supersedes the earlier Lexend Deca commitment, which the shipped site never used. The site was refined rather than rebuilt on the user's instruction, so the incumbent type system was preserved — revisit if Lexend Deca is still wanted.)* Anton is condensed: display lines over ~20 characters overflow the hero column, so trim copy rather than resize containers.

## Evidence on Hand

- Logo assets (above). No customers, revenue, testimonials, benchmarks, press, pricing tiers, or case results exist yet; future work must not fabricate any. Public precedents (documented brand-led criminal referrals, documented breaches first recorded on victims' phones) may be cited as precedent, never as Dossier results.

## Product Principles

1. **Capture is the product.** Every design decision serves enrollment, because enrolled phones are the input to the dataset that is the actual company.
2. **The brand pays; the consumer is the sensor network.** Never confuse the two audiences in copy.
3. **The baseline runs without attribution.** Deep attribution is upside, never priced or promised as a rate.
4. **The compliance wall is load-bearing.** The agent's restraint is what keeps the evidence sellable; copy must never celebrate deception.
5. **Honesty is a feature.** Plain recording disclosure, no inflated numbers, no protection theater.
6. **Build the ceiling for the fraud-team reader.** The surface should read as enterprise intelligence infrastructure, not a consumer novelty.

## Accessibility & Inclusion

No product-specific standard established beyond general good practice (WCAG AA color contrast, keyboard-operable signup form, honest/legible disclosures).