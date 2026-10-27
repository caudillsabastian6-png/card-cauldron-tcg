#!/usr/bin/env python3
"""Card Cauldron TCG — v12 multi-page split.

Reads the v11 single-page source (../v11-build/index.html, pristine) and
reassembles it as five pages sharing one head/nav/footer:

  index.html  Home           hero, ticker, watch, categories, reviews, calendar, drops, sounds
  shop.html   Singles&Slabs  catalog, hits, yellow, bundle, configurator, binderlabels, bagodds, wheel
  bulk.html   We Buy Bulk    wantboard (+ owner-approved Unsorted $10 tier, + Bulk Scale wave-2 slot)
  app.html    Real or Replica guidebook, slabs-timeline, fakeweek, holornot
  about.html  About          about, corrections, wickdesk, crewwall, contact
  privacy.html               untouched (copied from v11)

This is a reorganization, not a rewrite: every section's markup, copy, prices
and links carry over unchanged. The only edits beyond the split are:
  * per-page <title>/description/canonical/OG (v11's set stays on Home)
  * the shared nav becomes the 5-page nav (Home/Shop/We Buy Bulk/Real or Replica/About)
  * in-page #anchors that crossed a page boundary become /page.html#anchor
  * 5 null-guards/fallbacks in the shared script so it runs on pages that lack
    the catalog grid / ticker / hero bolts / Cauldron List panel
  * bulk.html gains the owner-approved 4th rate tier (Unsorted $10/1,000)
    and the marked Bulk Scale calculator slot for wave 2
  * two small CSS rules: current-page nav highlight + subpage top spacing
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "v11-build" / "index.html"
OUT = HERE

lines = SRC.read_text(encoding="utf-8").split("\n")


def find(pred, start=0, what="marker"):
    for i in range(start, len(lines)):
        if pred(lines[i]):
            return i
    raise SystemExit(f"build error: {what} not found")


# ---------------------------------------------------------------- segments
i_jsonld = find(lambda l: '<script type="application/ld+json">' in l, what="JSON-LD")
i_jsonld_end = find(lambda l: l.strip() == "</script>", i_jsonld, "JSON-LD end")
i_nav = find(lambda l: l.strip() == "<nav>", i_jsonld_end, "nav start")
i_nav_end = find(lambda l: l.strip() == "</nav>", i_nav, "nav end")
i_main = find(lambda l: '<main id="top">' in l, i_nav_end, "main open")
i_main_end = find(lambda l: l.strip() == "</main>", i_main, "main close")
i_s1 = find(lambda l: l.strip() == "<script>", i_main_end, "script1 start")
i_s1_end = find(lambda l: l.strip() == "</script>", i_s1, "script1 end")
i_s2 = find(lambda l: l.strip() == "<script>", i_s1_end, "script2 start")
i_s2_end = find(lambda l: l.strip() == "</script>", i_s2, "script2 end")

HEAD_A = lines[:i_jsonld]                       # doctype .. </style>
JSONLD = lines[i_jsonld:i_jsonld_end + 1]       # OnlineStore block (home only)
MID = lines[i_jsonld_end + 1:i_nav]             # </head><body> glowfield/embers/flash/ref-banner
MAIN_OPEN = lines[i_main]                       # <main id="top">
MAIN_BODY = lines[i_main + 1:i_main_end]
TAIL = lines[i_main_end:i_s1]                   # </main> footer sound-toggle anthem
SCRIPT1 = lines[i_s1:i_s1_end + 1]
SCRIPT2 = lines[i_s2:i_s2_end + 1]
DOC_END = lines[i_s2_end + 1:]                  # </body></html>

# ---------------------------------------------------------------- blocks
MARKER = re.compile(r"^\s*<!--\s*=+\s*(.*?)\s*=+\s*-->\s*$")
blocks, cur_name, cur = [], None, []
for ln in MAIN_BODY:
    m = MARKER.match(ln)
    if m:
        if cur_name is not None:
            blocks.append((cur_name, cur))
        cur_name, cur = m.group(1), [ln]
    else:
        cur.append(ln)
if cur_name is not None:
    blocks.append((cur_name, cur))

NAME2KEY = {
    "HERO": "hero",
    "TICKER": "ticker",
    "CHARIZARD IN MOTION (v9)": "watch",
    "CATEGORIES": "categories",
    "CATALOG": "catalog",
    "HITS": "hits",
    "WHAT BUYERS SAY": "reviews",
    "YELLOW BORDER": "yellow",
    "BUNDLE + PROMOS": "bundle",
    "MYSTERY BUNDLE CONFIGURATOR": "configurator",
    "ABOUT": "about",
    "CORRECTIONS LOG": "corrections",
    "RELEASE CALENDAR": "calendar",
    "DROP-DAY COUNTDOWN": "drops",
    "GUIDEBOOK": "guidebook",
    "GRADER LABEL TIMELINE": "slabs-timeline",
    "FAKE OF THE WEEK": "fakeweek",
    "PRINTABLE BINDER LABELS": "binderlabels",
    "SOUNDS LIBRARY": "sounds",
    "WANT-LIST BOARD": "wantboard",
    "BAG ODDS — HONEST EDITION": "bagodds",
    "FROM THE DESK OF WICK": "wickdesk",
    "THE CREW WALL": "crewwall",
    "HOLO OR NOT?": "holornot",
    "THE MYSTERY WHEEL": "wheel",
    "CONTACT": "contact",
}
BLOCK = {}
for name, blines in blocks:
    key = NAME2KEY.get(name)
    if key is None:
        raise SystemExit(f"build error: unmapped block {name!r}")
    BLOCK[key] = blines
if len(BLOCK) != 26:
    raise SystemExit(f"build error: expected 26 blocks, got {len(BLOCK)}")

# ---------------------------------------------------------------- page map
SECTION_PAGE = {}
for k in ("hero", "ticker", "watch", "categories", "reviews", "calendar", "drops", "sounds"):
    SECTION_PAGE[k] = "index"
for k in ("catalog", "hits", "yellow", "bundle", "configurator", "binderlabels", "bagodds", "wheel"):
    SECTION_PAGE[k] = "shop"
SECTION_PAGE["wantboard"] = "bulk"
for k in ("guidebook", "slabs-timeline", "fakeweek", "holornot"):
    SECTION_PAGE[k] = "app"
for k in ("about", "corrections", "wickdesk", "crewwall", "contact"):
    SECTION_PAGE[k] = "about"
# anchor id -> section key (ids equal keys except the timeline)
ID2KEY = {k: k for k in SECTION_PAGE}
ID2KEY["slabs-timeline"] = "slabs-timeline"

PAGE_FILE = {"index": "index.html", "shop": "shop.html", "bulk": "bulk.html",
             "app": "app.html", "about": "about.html"}
PAGE_BLOCKS = {
    "index": ["hero", "ticker", "watch", "categories", "reviews", "calendar", "drops", "sounds"],
    "shop": ["catalog", "hits", "yellow", "bundle", "configurator", "binderlabels", "bagodds", "wheel"],
    "bulk": ["wantboard"],
    "app": ["guidebook", "slabs-timeline", "fakeweek", "holornot"],
    "about": ["about", "corrections", "wickdesk", "crewwall", "contact"],
}

META = {
    "index": None,  # v11 values stay verbatim
    "shop": {
        "title": "Pokémon TCG Singles & Graded Slabs for Sale | Card Cauldron TCG",
        "desc": "Shop Pokémon TCG singles and graded slabs at Card Cauldron TCG — near-mint singles, vintage yellow-border cards, PSA &amp; CGC graded slabs and hand-packed mystery bundles. Every photo is the actual card, and every card links to its eBay listing. Ships from Van Wert, Ohio.",
        "url": "https://cardcauldrontcg.com/shop.html",
    },
    "bulk": {
        "title": "We Buy Pokémon Cards in Bulk — Standing Rates | Card Cauldron TCG",
        "desc": "We buy Pokémon cards in bulk at Card Cauldron TCG, every week, at standing rates: $10 per 1,000 unsorted, $15 per 1,000 commons &amp; uncommons, $20 per 1,000 reverse holos and $40 per 1,000 regular holos. Clean bulk from any set. Van Wert, Ohio.",
        "url": "https://cardcauldrontcg.com/bulk.html",
    },
    "app": {
        "title": "Real or Replica — Pokémon Card Checker | Card Cauldron TCG",
        "desc": "Real or Replica is Card Cauldron TCG's Pokémon card checker. Study genuine-vs-fake pairs from our own checking files, learn the tells, and spot a counterfeit before it costs you.",
        "url": "https://cardcauldrontcg.com/app.html",
    },
    "about": {
        "title": "About Card Cauldron TCG — The Brewer &amp; the Crew | Card Cauldron TCG",
        "desc": "Meet Sabastian Caudill, the brewer behind Card Cauldron TCG, and the crew — a Pokémon card shop in Van Wert, Ohio that photographs every card it sells and fixes its mistakes in public.",
        "url": "https://cardcauldrontcg.com/about.html",
    },
}

V11_TITLE = "Pokémon TCG Singles, Graded Slabs & Mystery Bundles | Card Cauldron TCG"
V11_DESC = "Pokémon TCG singles for sale at Card Cauldron TCG — near-mint singles, vintage yellow-border cards, PSA &amp; CGC graded slabs and hand-packed mystery bundles. Every photo is the actual card, and every card links to its eBay listing. Ships from Van Wert, Ohio."
V11_URL = "https://cardcauldrontcg.com/"

V12_CSS = """
  /* ---------- v12 multi-page: current-page nav + subpage top spacing ---------- */
  nav .links a[aria-current="page"], .mnav a[aria-current="page"]{color:var(--gold)}
  body.subpage main > section:first-child{padding-top:clamp(7.5rem,13vw,9rem)}"""


def build_head(page):
    head = list(HEAD_A)
    # v12 CSS goes just before </style> (last line of HEAD_A)
    assert head[-1].strip() == "</style>"
    head = head[:-1] + V12_CSS.split("\n") + [head[-1]]
    text = "\n".join(head)
    meta = META[page]
    if meta is not None:
        pairs = [
            (f"<title>{V11_TITLE}</title>", f"<title>{meta['title']}</title>"),
            (f'<meta name="description" content="{V11_DESC}" />',
             f'<meta name="description" content="{meta["desc"]}" />'),
            (f'<link rel="canonical" href="{V11_URL}" />',
             f'<link rel="canonical" href="{meta["url"]}" />'),
            (f'<meta property="og:url" content="{V11_URL}" />',
             f'<meta property="og:url" content="{meta["url"]}" />'),
            (f'<meta property="og:title" content="{V11_TITLE}" />',
             f'<meta property="og:title" content="{meta["title"]}" />'),
            (f'<meta property="og:description" content="{V11_DESC}" />',
             f'<meta property="og:description" content="{meta["desc"]}" />'),
            (f'<meta name="twitter:title" content="{V11_TITLE}" />',
             f'<meta name="twitter:title" content="{meta["title"]}" />'),
            (f'<meta name="twitter:description" content="{V11_DESC}" />',
             f'<meta name="twitter:description" content="{meta["desc"]}" />'),
        ]
        for old, new in pairs:
            if text.count(old) != 1:
                raise SystemExit(f"build error: head anchor not unique/found: {old[:60]}...")
            text = text.replace(old, new)
    out = text.split("\n")
    if page == "index":
        out += JSONLD
    return out


NAV_LINKS = [("index", "/", "Home"), ("shop", "/shop.html", "Shop"),
             ("bulk", "/bulk.html", "We Buy Bulk"), ("app", "/app.html", "Real or Replica"),
             ("about", "/about.html", "About")]


def build_nav(page):
    brand = "#top" if page == "index" else "/"

    def links(cls):
        parts = [f'  <div class="{cls}">']
        for key, href, label in NAV_LINKS:
            cur = ' aria-current="page"' if key == page else ""
            parts.append(f'    <a href="{href}"{cur}>{label}</a>')
        parts.append("  </div>")
        return parts

    nav = ["<nav>", f'  <a class="brand" href="{brand}">CARD CAULDRON TCG</a>']
    nav += links("links")
    nav.append('  <a class="store-btn" href="https://www.ebay.com/str/cardcauldrontcg" target="_blank" rel="noopener">eBay Store ↗</a>')
    nav += links("mnav")
    nav.append("</nav>")
    return nav


def rewrite_links(text, page):
    def repl(m):
        anchor = m.group(1)
        if anchor == "top":
            return 'href="#top"'
        key = ID2KEY.get(anchor)
        if key is None:
            return m.group(0)
        target = SECTION_PAGE[key]
        if target == page:
            return f'href="#{anchor}"'
        return f'href="/{PAGE_FILE[target]}#{anchor}"'
    return re.sub(r'href="#([a-z0-9-]+)"', repl, text)


def build_script1():
    s = "\n".join(SCRIPT1)
    edits = [
        ('  var track = document.getElementById("tickerTrack");\n  track.innerHTML += track.innerHTML;',
         '  var track = document.getElementById("tickerTrack");\n  if (track){ track.innerHTML += track.innerHTML; }'),
        ('  if (!reduced && window.matchMedia("(pointer: fine)").matches){\n    Array.prototype.forEach.call(grid.children, function(tile){',
         '  if (!reduced && grid && window.matchMedia("(pointer: fine)").matches){\n    Array.prototype.forEach.call(grid.children, function(tile){'),
        ('  var bolts = [document.getElementById("bolt1"), document.getElementById("bolt2")];',
         '  var bolts = [document.getElementById("bolt1"), document.getElementById("bolt2")].filter(function(b){ return !!b; });'),
        ('  function strike(){\n    if (window.scrollY < window.innerHeight * 1.1){',
         '  function strike(){\n    if (!bolts.length) return;\n    if (window.scrollY < window.innerHeight * 1.1){'),
    ]
    for old, new in edits:
        if s.count(old) != 1:
            raise SystemExit(f"build error: script edit anchor failed: {old[:60]}...")
        s = s.replace(old, new)
    fallback = ('  /* ---------- the Cauldron List panel lives on the About page: '
                'pages without it send its buttons there ---------- */\n'
                '  if (!(cBtn && cPanel)){\n'
                '    Array.prototype.forEach.call(document.querySelectorAll("[data-open-cauldron]"), function(btn){\n'
                '      btn.addEventListener("click", function(){ window.location.href = "/about.html#contact"; });\n'
                '    });\n'
                '  }\n\n')
    anchor = '  /* ---------- want-list strip: copy the shop address ---------- */'
    if s.count(anchor) != 1:
        raise SystemExit("build error: want-list anchor not found")
    s = s.replace(anchor, fallback + anchor)
    return s.split("\n")


UNSORTED_CARD = '''      <div class="rate-card pop">
        <span class="hunt-chip">Always hunting</span>
        <h3>Unsorted — Bulk</h3>
        <div class="rate-big">$10 <small>per 1,000 cards</small></div>
        <p style="margin-top:.5rem">Unsorted bulk, just as it comes to you — we do the sorting on our side of the counter.</p>
      </div>
'''

BULKSCALE_SLOT = '''
  <!-- ============ THE BULK SCALE (wave 2) ============ -->
  <section id="bulkscale">
    <div class="sec-head pop">
      <div class="num">// WE BUY BULK — THE BULK SCALE</div>
      <h2>The Bulk <em>Scale</em></h2>
      <p>Coming soon to this page: the Bulk Scale — count your cards, pick the tier, and watch the standing rates above do the math before you ever message us.</p>
    </div>
    <!-- BULK-SCALE-CALCULATOR-SLOT (wave 2): the interactive bulk calculator is built into this section. Rates source of truth: the rate cards in #wantboard above. -->
  </section>
'''


def bulk_block():
    text = "\n".join(BLOCK["wantboard"])
    # owner-approved 4th tier (Oct 22): Unsorted $10/1,000 becomes the first card;
    # the existing cards shift one delay step so the stagger still reads in order.
    shifts = [
        ('      <div class="rate-card pop">\n        <span class="hunt-chip">Always hunting</span>\n        <h3>Commons &amp; Uncommons — Bulk</h3>',
         '      <div class="rate-card pop d1">\n        <span class="hunt-chip">Always hunting</span>\n        <h3>Commons &amp; Uncommons — Bulk</h3>'),
        ('      <div class="rate-card pop d1">\n        <span class="hunt-chip">Always hunting</span>\n        <h3>Reverse Holos — Bulk</h3>',
         '      <div class="rate-card pop d2">\n        <span class="hunt-chip">Always hunting</span>\n        <h3>Reverse Holos — Bulk</h3>'),
        ('      <div class="rate-card pop d2">\n        <span class="hunt-chip">Always hunting</span>\n        <h3>Regular Holos — Bulk</h3>',
         '      <div class="rate-card pop d3">\n        <span class="hunt-chip">Always hunting</span>\n        <h3>Regular Holos — Bulk</h3>'),
        ('      <div class="rate-card pop d3">\n        <span class="hunt-chip">Priced per card</span>',
         '      <div class="rate-card pop d4">\n        <span class="hunt-chip">Priced per card</span>'),
    ]
    for old, new in shifts:
        if text.count(old) != 1:
            raise SystemExit(f"build error: rate-card anchor failed: {old[:70]}...")
        text = text.replace(old, new)
    anchor = '      <div class="rate-card pop d1">\n        <span class="hunt-chip">Always hunting</span>\n        <h3>Commons &amp; Uncommons — Bulk</h3>'
    text = text.replace(anchor, UNSORTED_CARD + anchor)
    return text


def build_page(page):
    out = []
    out += build_head(page)
    mid = list(MID)
    if page != "index":
        mid = ['<body class="subpage">' if l.strip() == "<body>" else l for l in mid]
    out += mid
    out += build_nav(page)
    out += ["", MAIN_OPEN, ""]
    if page == "bulk":
        body = bulk_block() + "\n" + BULKSCALE_SLOT
    else:
        body = "\n".join("\n".join(BLOCK[k]) for k in PAGE_BLOCKS[page])
    out += rewrite_links(body, page).split("\n")
    out += rewrite_links("\n".join(TAIL), page).split("\n")
    out += SCRIPT1_FIXED
    if page in ("shop", "app"):
        out += SCRIPT2
    out += DOC_END
    return "\n".join(out) + "\n"


SCRIPT1_FIXED = build_script1()

SITEMAP = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://cardcauldrontcg.com/</loc>
    <lastmod>2026-10-22</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://cardcauldrontcg.com/shop.html</loc>
    <lastmod>2026-10-22</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://cardcauldrontcg.com/bulk.html</loc>
    <lastmod>2026-10-22</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://cardcauldrontcg.com/app.html</loc>
    <lastmod>2026-10-22</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://cardcauldrontcg.com/about.html</loc>
    <lastmod>2026-10-22</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://cardcauldrontcg.com/privacy.html</loc>
    <lastmod>2026-10-21</lastmod>
    <changefreq>yearly</changefreq>
    <priority>0.3</priority>
  </url>
</urlset>
'''

for page, fname in PAGE_FILE.items():
    (OUT / fname).write_text(build_page(page), encoding="utf-8")
    print(f"wrote {fname}")
(OUT / "sitemap.xml").write_text(SITEMAP, encoding="utf-8")
print("wrote sitemap.xml")
