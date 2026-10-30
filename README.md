# Real or Replica — by Card Cauldron TCG

**A card checker that would rather say "I don't know" than guess.**

## The problem, and who this is for

Counterfeit trading cards flood every marketplace, and the people
who get burned are the ones who can least afford it: kids and
parents buying a gift, collectors spending real money on a single
card, and honest small sellers whose genuine stock gets doubted
because fakes are everywhere. Real or Replica is built by a
working card shop — Card Cauldron TCG — for the people on both
sides of that counter. It checks whether a card is genuine and
shows its evidence, so a buyer can decide with their eyes open
and a seller can prove what they're selling.

## The core runs on Meta AI models

The verification core of this project runs on **Meta AI models**.
Its model reads are **Muse Spark** reads of structured card crops
(number strip, set-symbol corner, holo window, full front/back)
and **Muse Wonder** card reads — on Oct 29, 2026, Wonder read 71
held cards and the shop owner checked every read against the
physical cards: **71 of 71 confirmed**. The full pipeline, its
setup instructions, and that read record live in the companion
evidence repo:
**https://github.com/caudillsabastian6-png/Fake-check**
(see "What is simulated, what is real" below for exactly which
parts are labelled samples, and why).

## Deliberately not a simple image analyzer

Real or Replica never judges a card from one photo guess. A check
combines several independent signals: identity lookup against a
33,391-identity reference catalogue, pixel-level tells measured
separately on the front and the back, set-symbol verification,
and the Meta AI model reads above — combined by an agent loop
that is allowed to answer **Inconclusive**.

The three possible outcomes are **Likely Genuine**, **Likely
Counterfeit**, and **Inconclusive**. A Likely verdict is an
estimate, never an official grade and never a guarantee.

Live demo: **https://cardcauldrontcg.com/demo/**
Built for the Meta Global AI Developer Hackathon (Cerebral Valley),
Indie Track. Submission deadline Nov 4, 2026. What predates the
event is called out plainly in "What was pre-existing vs built
during the event" below.

---

## Honest status — read this first

**The checker in this demo runs in SAMPLE mode, on purpose.**

The full verification pipeline is real and documented (see the
evidence repo below), but it has **not passed its calibration gate
yet**. Our calibration run on Oct 28, 2026 failed — safely (zero
confident-wrong answers) but not accurately enough to ship. So:

- Every check result inside this demo is a **sample**: it walks you
  through the real flow and the real questions, with simulated
  results. It is labelled SAMPLE in the app, and it is labelled
  here too.
- **No real verdict has ever shipped.** Verdicts turn real only when
  a calibration re-run on owner-confirmed cards passes the project's
  evidence gate — not before, and not because a deadline is close.
- Where the evidence doesn't settle a card, the honest answer is
  **Inconclusive**, and the design treats that as a real answer,
  not a failure.

**What IS real in this demo:** the complete app itself — the check
flow, the mini-games, the avatar and wardrobe, the shop, the Mallow
helper, live leaderboards, and the card pool, where visitors can
submit front/back photos of their own cards as *pending* entries for
human review and labelling (pending entries are never used as
verdicts or training data). What's simulated is the checker's
verdict, and only that.

**Evidence and work record:** the checker code, calibration reports
(including the failed gate, with numbers), labelling ledgers, and
dated build reports live in the companion repo:
**https://github.com/caudillsabastian6-png/Fake-check**

---

## What is simulated, what is real — and where the real core runs

Hackathon office hours (Oct 30, 2026) put the rule in plain words:
*"A labeled mock or simulated step around a working core is fine, as
long as the core verdict actually runs on Meta models from your
setup instructions."* Here is exactly how this project stands
against that rule:

- **Simulated, and labelled as such:** the check results inside
  this demo app. The demo is a static page; its check flow walks
  the real questions and returns sample results, labelled SAMPLE
  in the app and in this README. This page calls no model, and
  nothing here claims it does.
- **The working core is real, and it runs on Meta models.** The
  verdict pipeline lives in the evidence repo
  ([Fake-check](https://github.com/caudillsabastian6-png/Fake-check)),
  whose README's "Setup & run" section runs the checker end-to-end
  (`checker/app_check_v2.py`). Its signals are: an identity gate
  against a 33,391-identity reference catalogue (printed set +
  number, so a reference for the wrong card can never yield
  "Genuine"); pixel tells measured separately on front and back;
  a set-symbol gate; and **Meta AI model reads** — Muse Spark
  reads of structured card crops (number strip, set-symbol corner,
  holo window, full front/back) via `checker/meta_pipeline.py`,
  returning per-tell observations, and Muse Wonder card reads:
  on Oct 29, 2026, Wonder read 71 held cards and the shop owner
  checked every read against the physical cards — **71 of 71
  confirmed** (record:
  `playground/wonder-holds-2026-10-29/WONDER-RECORD.md` in the
  evidence repo). Those reads ran on the Meta Model API during
  the event; re-running them takes your own Meta Model API key
  (no key is in either repo, and judges may test with their own
  keys).
- **Not a Meta model:** Basil, the small student model being
  trained on the shop's own labelled cards, is part of the wider
  multi-signal design around the checker. Basil is the builder's
  own model — it is never described as a Meta model, and it does
  not run in this demo.
- **Why the demo verdicts are still samples:** the combined
  pipeline has not passed its calibration gate yet (the Oct 28
  run failed safely and is documented in the evidence repo), so
  the front end stays labelled SAMPLE until a re-run passes on
  owner-confirmed cards. The labelled simulation is allowed
  precisely because the core underneath it is real.

---

## Run the demo locally

The demo is a static web page — one HTML file plus its asset
folder. No build step, no account, no API key.

```bash
git clone https://github.com/caudillsabastian6-png/card-cauldron-tcg.git
cd card-cauldron-tcg/demo
python3 -m http.server 8000
# then open http://localhost:8000/ in a browser
```

Serving the `demo/` folder (instead of double-clicking the file)
matters: the page loads its images and a bundled data file by
relative path, and browsers block some of that from `file://`.

Notes:

- `demo/index.html` is the whole app. Everything it needs ships in
  `demo/assets/` and the files beside it in `demo/`.
- A few social features — game leaderboards and card-pool
  submissions — talk to the project's live backend
  (`api.cardcauldrontcg.com`). The card check itself runs in the
  page and returns SAMPLE results by design, as disclosed above.
- No API keys, tokens, or credentials are in this repo or needed
  to run anything in it.

## What's in this repo

| Path | What it is |
|---|---|
| `demo/` | The Real or Replica demo app (the live demo's source). |
| `index.html`, `about.html`, `shop.html`, … | The Card Cauldron TCG shop website, served at cardcauldrontcg.com. |
| `assets/`, `media/` | Site images and media. |
| `build_v*.py` | The site build scripts that assemble the pages. |

## What was pre-existing vs built during the event

Only **Oct 26 – Nov 4, 2026** work is claimed for this hackathon.

- **Pre-existing (not claimed):** the idea; Card Cauldron TCG, the
  builder's real card shop; the website; and the first demo
  (Oct 24–25, 2026).
- **Built during the event:** the multi-signal checker pipeline,
  the calibration and labelling systems, the demo app in its
  current form, and everything documented in the evidence repo.

## Built by

Sabastian Caudill — Card Cauldron TCG. Solo indie builder; a real
card shop whose own confirmed cards and scans are the project's
ground truth.
