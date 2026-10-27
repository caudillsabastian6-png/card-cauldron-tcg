#!/usr/bin/env python3
"""v14 build — Idea Ledger Sweep website batch (all vetted + approved under Nickel's brief, Oct 23).

Base: v13-build/ copied to v14-build/. Changes, and only these:
  1. Nav: 'Browse by Set' link inserted after 'Shop' in .links and .mnav on the 6 nav
     pages (index, shop, bulk, app, about, ask). privacy.html has no shared nav — untouched.
  2. bulk.html: the wave-2 BULK-SCALE slot becomes Potion's 'Bulk Scale' — an interactive
     calculator on the four standing tiers (Unsorted $10 / C-U $15 / Reverse Holos $20 /
     Regular Holos $40 per 1,000; source of truth = the rate cards in #wantboard).
  3. NEW sets.html — Noor's 'Set-Symbol Search' + Index's 'Card Index': every set the shop
     stocks, A-Z, with its set symbol (pokemontcg.io CDN, text label always present, image
     removes itself on error) and the count of singles catalogued in our own tracker,
     counted Oct 23, 2026 (census: ~/workspace/cloudflare-pages/v14-data/).
  4. NEW proof.html — Nickel's 'Proof Page': every claim carries its source link and the
     date it was checked. A claim without a live source does not ship.
  5. NEW is-my-card-fake.html — Noor's answer page 'Is my card fake? Start here.'
     (draft: ~/workspace/social-daily/growth-execution/noor-answer-page/), copy verbatim.
  6. sitemap.xml: the three new pages added.
Every replacement is count-asserted; a mismatch aborts the build.
"""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
DATA = ROOT.parent / "v14-data"

def sub(text, old, new, count, where):
    n = text.count(old)
    assert n == count, f"{where}: expected {count}x {old[:60]!r}, found {n}"
    return text.replace(old, new)

STORE = "https://www.ebay.com/str/cardcauldrontcg"
SETS_LINK = '<a href="/sets.html">Browse by Set</a>'
SETS_LINK_CURRENT = '<a href="/sets.html" aria-current="page">Browse by Set</a>'
SHOP_PLAIN = '<a href="/shop.html">Shop</a>'
SHOP_CURRENT = '<a href="/shop.html" aria-current="page">Shop</a>'
APP_PLAIN = '<a href="/app.html">Real or Replica</a>'
APP_CURRENT = '<a href="/app.html" aria-current="page">Real or Replica</a>'

NAV_PAGES = ["index.html", "shop.html", "bulk.html", "app.html", "about.html", "ask.html"]

# ---------- 1. nav patch on the six nav pages ----------
for name in NAV_PAGES:
    p = ROOT / name
    t = p.read_text(encoding="utf-8")
    if SHOP_CURRENT in t:  # shop.html itself
        t = sub(t, SHOP_CURRENT, SHOP_CURRENT + "\n    " + SETS_LINK, 2, name)
    else:
        t = sub(t, SHOP_PLAIN, SHOP_PLAIN + "\n    " + SETS_LINK, 2, name)
    p.write_text(t, encoding="utf-8")
    print(f"nav patched: {name}")

# ---------- 2. Bulk Scale into bulk.html ----------
bp = ROOT / "bulk.html"
t = bp.read_text(encoding="utf-8")

BULK_CSS = """
  /* ---------- v14 Bulk Scale ---------- */
  .bulk-calc{max-width:46rem; margin-top:1.8rem; background:var(--panel); border:1px solid rgba(255,233,176,.22); border-radius:16px; padding:1.3rem 1.4rem}
  .bulk-calc-label{display:block; font-weight:700; margin-bottom:.55rem}
  .bulk-calc input{width:100%; font:inherit; padding:.8rem 1rem; border-radius:12px; border:1px solid rgba(255,233,176,.35); background:var(--panel); color:var(--ink)}
  .bulk-calc input:focus{outline:2px solid var(--gold); outline-offset:1px}
  .bulk-rows{display:grid; gap:.55rem; margin-top:1.1rem}
  .bulk-row{display:flex; justify-content:space-between; align-items:baseline; gap:1rem; border-top:1px solid rgba(255,233,176,.14); padding-top:.55rem}
  .bulk-tier{font-weight:700}
  .bulk-rate{color:var(--muted); font-size:.92rem}
  .bulk-val{color:var(--gold); font-weight:800; font-size:1.12rem; white-space:nowrap}
  .bulk-note{color:var(--muted); margin-top:1.1rem}
"""
# Inject INSIDE the head <style> block (before its closing </style>): injecting
# before </head> strands CSS as visible text after </style> (v14 leak bug, fixed Oct 23).
t = sub(t, "</style>\n</head>", BULK_CSS + "</style>\n</head>", 1, "bulk css")

t = sub(t,
  "<p>Coming soon to this page: the Bulk Scale — count your cards, pick the tier, and watch the standing rates above do the math before you ever message us.</p>",
  "<p>Count your cards, punch in the number, and watch the standing rates above do the math — before you ever message us. If the rates ever change, the board above changes first, and this scale follows it.</p>",
  1, "bulk intro")

CALC = """<div class="bulk-calc pop">
      <label class="bulk-calc-label" for="bulkCount">How many cards are in your pile?</label>
      <input id="bulkCount" type="number" min="0" step="1" inputmode="numeric" placeholder="e.g. 2500" autocomplete="off" />
      <div class="bulk-rows">
        <div class="bulk-row"><span class="bulk-tier">Unsorted bulk</span><span class="bulk-rate">$10 per 1,000</span><span class="bulk-val" data-rate="10">—</span></div>
        <div class="bulk-row"><span class="bulk-tier">Commons &amp; Uncommons</span><span class="bulk-rate">$15 per 1,000</span><span class="bulk-val" data-rate="15">—</span></div>
        <div class="bulk-row"><span class="bulk-tier">Reverse Holos</span><span class="bulk-rate">$20 per 1,000</span><span class="bulk-val" data-rate="20">—</span></div>
        <div class="bulk-row"><span class="bulk-tier">Regular Holos</span><span class="bulk-rate">$40 per 1,000</span><span class="bulk-val" data-rate="40">—</span></div>
      </div>
      <p class="bulk-note">Each line answers one question: <b>if the whole pile were this tier, we'd pay this.</b> Real piles are mixed — sort yours roughly and add the lines up. Ultras, full arts and secret rares are never bulk: they're priced card by card, by the card (see the board above). Final counts happen in hand, together — the scale is an honest estimate, not a contract.</p>
    </div>"""
t = sub(t,
  "    <!-- BULK-SCALE-CALCULATOR-SLOT (wave 2): the interactive bulk calculator is built into this section. Rates source of truth: the rate cards in #wantboard above. -->",
  "    " + CALC, 1, "bulk slot")

BULK_SCRIPT = """<script>
(function(){
  "use strict";
  var input = document.getElementById("bulkCount");
  if (!input) return;
  var vals = document.querySelectorAll(".bulk-val");
  function fmt(n){ return "$" + n.toFixed(2); }
  function update(){
    var n = parseFloat(input.value);
    var ok = isFinite(n) && n >= 0 && input.value.trim() !== "";
    for (var i = 0; i < vals.length; i++){
      var rate = parseFloat(vals[i].getAttribute("data-rate"));
      vals[i].textContent = ok ? fmt(n / 1000 * rate) : "—";
    }
  }
  input.addEventListener("input", update);
  update();
})();
</script>
"""
t = sub(t, "</main>", BULK_SCRIPT + "</main>", 1, "bulk script")
bp.write_text(t, encoding="utf-8")
print("bulk.html: Bulk Scale built")

# ---------- shared new-page shell (from the nav-patched app.html, v13 pattern) ----------
app = (ROOT / "app.html").read_text(encoding="utf-8")
HEAD0, rest = app.split('<main id="top">', 1)
_, TAIL0 = rest.split('</main>', 1)
OLD_TITLE = "Real or Replica — Pokémon Card Checker | Card Cauldron TCG"
OLD_DESC = ("Real or Replica is Card Cauldron TCG's Pokémon card checker. Study genuine-vs-fake pairs "
            "from our own checking files, learn the tells, and spot a counterfeit before it costs you.")

def make_head(title, desc, slug, css, current=None):
    h = HEAD0
    h = sub(h, OLD_TITLE, title, 3, f"{slug} head title")
    h = sub(h, OLD_DESC, desc, 3, f"{slug} head desc")
    h = sub(h, "https://cardcauldrontcg.com/app.html", f"https://cardcauldrontcg.com/{slug}", 2, f"{slug} head url")
    h = sub(h, APP_CURRENT, APP_PLAIN, 2, f"{slug} nav app")
    if current == "sets":
        h = sub(h, SETS_LINK, SETS_LINK_CURRENT, 2, f"{slug} nav sets")
    # Same fix as bulk above: CSS goes inside the <style> block, before its </style>.
    h = sub(h, "</style>\n</head>", css + "</style>\n</head>", 1, f"{slug} css")
    return h

def make_tail(extra_script=""):
    parts = TAIL0.split("<script>")
    assert len(parts) == 3, f"tail: expected footer + 2 script bundles, got {len(parts)-1} bundles"
    return parts[0] + "<script>" + parts[1] + extra_script + "</body>\n</html>\n"

def more_doors(exclude):
    cards = {
        "sets": ('/sets.html', '📚', 'Browse by Set', 'Every set in the Cauldron, A–Z — with the set symbol and how many singles we\'ve catalogued in it.'),
        "proof": ('/proof.html', '🎯', 'The Proof Page', 'Every claim we make, with its source and the date we checked it. Don\'t take our word for anything.'),
        "fake": ('/is-my-card-fake.html', '🔎', 'Is my card fake? Start here.', 'The office\'s own checks, in the order we run them — back first, then the light test.'),
        "ask": ('/ask.html', '🖋️', 'Ask the Office', 'A card question? The Checking Office answers — signed, or it doesn\'t post.'),
    }
    out = ['  <section id="more">', '    <div class="sec-head pop">',
           '      <div class="num">// MORE DOORS</div>', '      <h2>Keep <em>exploring</em></h2>', '    </div>',
           '    <div class="contact-grid">']
    i = 0
    for key, (href, glyph, h3, p) in cards.items():
        if key == exclude:
            continue
        i += 1
        out.append(f'      <a class="linkcard zoom d{i}" href="{href}">')
        out.append(f'        <div class="glyph">{glyph}</div>')
        out.append(f'        <h3>{h3}</h3>')
        out.append(f'        <p>{p}</p>')
        out.append('      </a>')
    out.append('    </div>')
    out.append('  </section>')
    return "\n".join(out) + "\n"

# ---------- 3. sets.html (Set-Symbol Search + Card Index) ----------
disp = json.loads((DATA / "sets-display.json").read_text(encoding="utf-8"))
symbols = json.loads((DATA / "set-symbols.json").read_text(encoding="utf-8"))
sets = dict(disp["sets"])
# 'Evolutions' and 'XY Evolutions' are the same set (XY Evolutions, /108) under two
# tracker labels — one row, summed count, same treatment as the code/full-name merges.
sets["XY Evolutions"] = sets.get("XY Evolutions", 0) + sets.pop("Evolutions", 0)
symbols["XY Evolutions"] = "xy12"
symbols["Scarlet & Violet 151"] = "sv03.5"  # map keys it as '151'
RENAMES = {
    "m5": "Japanese Mega sets (code m5)",
    "CLB": "CLB (set code)",
    "CSV7C": "Simplified Chinese (code CSV7C)",
    "CSV10C": "Simplified Chinese (code CSV10C)",
    "SV6C": "Simplified Chinese (code SV6C)",
    "SVP Black Star Promos": "Scarlet & Violet Black Star Promos",
}
rows = []
for name in sorted(sets, key=lambda s: s.lower()):
    rows.append({"n": RENAMES.get(name, name), "c": sets[name], "s": symbols.get(name)})
TOTAL = sum(r["c"] for r in rows)
NSETS = len(rows)
assert TOTAL == disp["total"], f"sets total drift: {TOTAL} vs {disp['total']}"
SETS_JSON = json.dumps(rows, ensure_ascii=False)

SETS_CSS = """
  /* ---------- v14 Sets (Card Index + Set-Symbol Search) ---------- */
  .sets-search{max-width:46rem; margin-top:2rem}
  .sets-search-label{display:block; font-weight:700; margin-bottom:.5rem}
  .sets-search input{width:100%; font:inherit; padding:.8rem 1rem; border-radius:12px; border:1px solid rgba(255,233,176,.35); background:var(--panel); color:var(--ink)}
  .sets-search input:focus{outline:2px solid var(--gold); outline-offset:1px}
  .sets-grid{display:grid; grid-template-columns:repeat(auto-fill,minmax(15rem,1fr)); gap:1rem; margin-top:1.6rem}
  .set-card{background:var(--panel); border:1px solid rgba(255,233,176,.22); border-radius:16px; padding:1.1rem 1.2rem}
  .set-card .set-sym{height:2.2rem; display:flex; align-items:center}
  .set-card .set-sym img{max-height:2.2rem; max-width:3.4rem}
  .set-card h3{margin:.5rem 0 .3rem; font-size:1.08rem}
  .set-card p{margin:0; color:var(--muted)}
  .set-card .set-shop{display:inline-block; margin-top:.6rem; font-weight:700}
  .sets-empty{color:var(--muted); margin-top:1.6rem; font-size:1.02rem}
"""

SETS_MAIN = """<main id="top">

  <!-- ============ BROWSE BY SET (Noor's Set-Symbol Search + Index's Card Index, vetted + approved Oct 23) ============ -->
  <section id="sets">
    <div class="sec-head pop">
      <div class="num">// THE CARD INDEX</div>
      <h2>Browse by <em>set</em></h2>
      <p>Every set in the Cauldron, A–Z — the set's own symbol beside its name, and how many singles we've catalogued in it. The counts come from the shop's own card tracker, counted <b>October 23, 2026</b>: __TOTAL__ singles across __NSETS__ sets. Records drift as cards sell and new scans land — the stamp above is the honest one.</p>
    </div>
    <div class="sets-search">
      <label class="sets-search-label" for="setSearch">Find your set</label>
      <input id="setSearch" type="search" placeholder="Try a set name — Destined Rivals, 151, Chilling Reign…" autocomplete="off" />
    </div>
    <div id="setsGrid" class="sets-grid" aria-live="polite"></div>
    <p id="setsEmpty" class="sets-empty" style="display:none">No set by that name in the Cauldron — try a shorter piece of the name. New scans land most weeks, so a set that's missing today may be here soon.</p>
    <noscript><p class="sets-empty">The index needs JavaScript to render — the same sets are all in the eBay store, sorted by listing.</p></noscript>
  </section>

""" + more_doors("sets")

SETS_SCRIPT = """<script>
(function(){
  "use strict";
  var SETS = __SETS_JSON__;
  var STORE = "https://www.ebay.com/str/cardcauldrontcg";
  var grid = document.getElementById("setsGrid");
  var empty = document.getElementById("setsEmpty");
  var search = document.getElementById("setSearch");
  if (!grid) return;
  function render(items){
    grid.innerHTML = "";
    empty.style.display = items.length ? "none" : "";
    items.forEach(function(it){
      var card = document.createElement("article");
      card.className = "set-card";
      if (it.s){
        var sym = document.createElement("div");
        sym.className = "set-sym";
        var img = document.createElement("img");
        img.src = "https://images.pokemontcg.io/" + it.s + "/symbol.png";
        img.alt = "";
        img.loading = "lazy";
        img.onerror = function(){ img.remove(); };
        sym.appendChild(img);
        card.appendChild(sym);
      }
      var h = document.createElement("h3"); h.textContent = it.n;
      var p = document.createElement("p");
      p.textContent = it.c + (it.c === 1 ? " single catalogued" : " singles catalogued");
      var a = document.createElement("a");
      a.className = "set-shop";
      a.href = STORE; a.target = "_blank"; a.rel = "noopener";
      a.textContent = "Shop the store ↗";
      card.appendChild(h); card.appendChild(p); card.appendChild(a);
      grid.appendChild(card);
    });
  }
  render(SETS);
  if (search){
    search.addEventListener("input", function(){
      var q = search.value.trim().toLowerCase();
      if (!q){ render(SETS); return; }
      render(SETS.filter(function(it){ return it.n.toLowerCase().indexOf(q) !== -1; }));
    });
  }
})();
</script>
"""

head = make_head(
    "Browse by Set — The Card Index | Card Cauldron TCG",
    f"Browse Card Cauldron TCG's singles by set: {TOTAL} catalogued singles across {NSETS} sets, counted from the shop's own tracker on October 23, 2026. Set symbols, honest counts, one door to the store.",
    "sets.html", SETS_CSS, current="sets")
main = SETS_MAIN.replace("__TOTAL__", f"{TOTAL:,}").replace("__NSETS__", str(NSETS))
script = SETS_SCRIPT.replace("__SETS_JSON__", SETS_JSON)
(ROOT / "sets.html").write_text(head + main + "</main>" + make_tail(script), encoding="utf-8")
print(f"sets.html written ({NSETS} sets, {TOTAL} singles)")

# ---------- 4. proof.html (Nickel's Proof Page) ----------
PROOF_CSS = """
  /* ---------- v14 Proof Page ---------- */
  .proof-src{margin-top:.8rem; font-size:.92rem}
  .proof-stamp{color:var(--gold); font-weight:700}
"""

def claim(glyph, h3, body, src_label, src_href, delay):
    return f"""      <div class="linkcard zoom d{delay}">
        <div class="glyph">{glyph}</div>
        <h3>{h3}</h3>
        <p>{body}</p>
        <p class="proof-src">Source: <a href="{src_href}" target="_blank" rel="noopener">{src_label}</a> · <span class="proof-stamp">Checked Oct 23, 2026</span></p>
      </div>"""

PROOF_MAIN = """<main id="top">

  <!-- ============ THE PROOF PAGE (Nickel's idea, vetted + approved Oct 23) ============ -->
  <section id="proof">
    <div class="sec-head pop">
      <div class="num">// THE PROOF PAGE</div>
      <h2>Don't take our <em>word</em> for it</h2>
      <p>Every claim on this page carries two things: the <b>source</b> you can check yourself, and the <b>date</b> we checked it. That's the rule this page was built under — a claim without a live source doesn't ship, and if a source ever stops backing a claim, the claim comes down. — Nickel 🪙</p>
    </div>
    <div class="contact-grid">
""" + "\n".join([
    claim("⭐", "Our feedback is public — 98.2% positive",
          "eBay keeps this score, not us. It counts the rated sales we've made as <b>buckeyebinder</b> — the good, the bad, all of it, where anyone can read it.",
          "our eBay seller profile ↗", "https://www.ebay.com/usr/buckeyebinder", 1),
    claim("🤝", "Best Offer is really on",
          "Every single in the store carries Best Offer — open any listing and look under the price. Our Final Examiner opens new listings buyer-side to confirm it renders, because a setting nobody can see isn't a promise kept.",
          "the eBay store ↗", STORE, 2),
    claim("✉️", "Shipping, posted plain",
          "$0.78 by eBay Standard Envelope on singles up to $20; $5.99 Ground Advantage above that. It's printed in every listing's shipping section before you check out — no surprises after.",
          "any listing in the store ↗", STORE, 3),
    claim("⚖️", "Bulk rates, in the open",
          "We buy bulk at $10 / $15 / $20 / $40 per 1,000 cards, posted on a public board with a working scale — the same rates whether you found us yesterday or a year ago.",
          "the bulk board ↗", "/bulk.html#bulkscale", 1),
    claim("📚", "Set counts from our own tracker",
          f"__TOTAL__ singles catalogued across __NSETS__ sets — real records from the shop's own card tracker, counted October 23, 2026. Not a guess, not a rounded-up boast.",
          "the Card Index ↗", "/sets.html", 2),
    claim("🖋️", "No unsigned answers",
          "Card answers post only after our Checking Office signs them. The archive can sit empty — it never sits fake.",
          "Ask the Office ↗", "/ask.html", 3),
    claim("🎯", "No percentages, ever",
          "Our verdicts are Likely Genuine, Likely Counterfeit, or Inconclusive. Anyone who gives you “87% real” from photos is making the number up — we won't.",
          "Is my card fake? Start here ↗", "/is-my-card-fake.html", 1),
]) + """
    </div>
  </section>

""" + more_doors("proof")

head = make_head(
    "The Proof Page — Every Claim, Sourced | Card Cauldron TCG",
    "Every claim Card Cauldron TCG makes, with its source and the date we checked it: eBay feedback, Best Offer, shipping, bulk rates, set counts. Don't take our word for anything.",
    "proof.html", PROOF_CSS)
main = PROOF_MAIN.replace("__TOTAL__", f"{TOTAL:,}").replace("__NSETS__", str(NSETS))
(ROOT / "proof.html").write_text(head + main + "</main>" + make_tail(), encoding="utf-8")
print("proof.html written")

# ---------- 5. is-my-card-fake.html (Noor's answer page, copy verbatim from the approved draft) ----------
FAKE_CSS = """
  /* ---------- v14 Is My Card Fake ---------- */
  .guide{max-width:46rem}
  .guide p{color:var(--muted); font-size:1.03rem; line-height:1.65}
  .guide p b, .guide li b{color:var(--ink)}
  .guide ul{color:var(--muted); font-size:1.03rem; line-height:1.65; padding-left:1.3rem}
  .guide li{margin:.45rem 0}
  .guide .limits{border-left:3px solid var(--gold); padding-left:1rem}
  .guide .signoff{color:var(--ink); font-weight:700}
"""

FAKE_MAIN = """<main id="top">

  <!-- ============ IS MY CARD FAKE? START HERE. (Noor's answer page, approved draft, built Oct 23) ============ -->
  <section id="start">
    <div class="sec-head pop">
      <div class="num">// REAL OR REPLICA — START HERE</div>
      <h2>Is my card fake? <em>Start here.</em></h2>
      <p>Take a breath first. Most cards that <em>feel</em> off are real cards with honest wear, a bad photo, or a weird print run — and even the scary ones can't hurt you if you don't resell them as something they're not. This page walks you through the same checks our shop runs before we sign a verdict, in the order we'd run them. You'll need your card, a bright light (your phone flashlight works), and two minutes.</p>
    </div>
    <div class="guide">
      <h3>First: look at the back. Always the back.</h3>
      <p>Before the front, before the holo, before anything — flip the card over. Counterfeiters spend their effort on the shiny front, and the back is where they get lazy: the blue is often the wrong shade, the Poké Ball swirl sits slightly off, the printing looks flat or fuzzy next to a card you <em>know</em> is real. This is why our checker demands a photo of the back before anyone signs anything. If you only do one check on this page, do this one: hold the back beside a bulk common from the same era that you're sure about, and compare the color and the crispness. Real backs are boringly consistent. Fake backs drift.</p>
    </div>
  </section>

  <section id="check1">
    <div class="sec-head pop">
      <div class="num">// CHECK 1</div>
      <h2>The light test <em>(the strongest test you own)</em></h2>
    </div>
    <div class="guide">
      <p>Hold the card up to a bright light, or put your phone flashlight right behind it. A genuine Pokémon card is built on card stock with a dark core layer, and it <b>blocks the light</b> — you'll see a dull glow at most. Most counterfeits are printed on thin, cheap stock with no core, and they <b>glow translucent</b>, sometimes bright enough to read the front through the back.</p>
      <p>This is the test that settled it for us in our own shop: a Charizard GX that came in through a trade looked wrong, and the light test ended the argument in five seconds. It went out of our inventory that night.</p>
      <p class="limits"><em>Honest limits:</em> the light test tells you about the stock, not the art. A card can fail it (fake stock) or pass it and still be a reprint or a proxy. It's evidence, not a whole verdict.</p>
    </div>
  </section>

  <section id="check2">
    <div class="sec-head pop">
      <div class="num">// CHECK 2</div>
      <h2>The print, under your fingertips <em>and a zoom lens</em></h2>
    </div>
    <div class="guide">
      <p>Real cards are offset-printed, and under a phone camera's zoom you'll see an orderly pattern of tiny dots — a rosette — especially in flat color areas. Counterfeits often show one of three wrong things instead:</p>
      <ul>
        <li><b>Flat, matte smoothness</b> where a real card has that dot pattern.</li>
        <li><b>A uniform sandy grit over everything</b> — including parts of the design that should be perfectly smooth, like the flat silver weakness and retreat bars. Real texture lives in the foil and the art; fake grit doesn't know where to stop.</li>
        <li><b>Mushy small print.</b> Fake printers fail at small sizes first. Look at the tiniest text on the card — the illustrator credit, the set number, the flavor text, the little type icons in the weakness bar. On a real card it's crisp down to the last letter. On a fake, the tiny letters bleed together and small icons (like the droplet in a Water weakness) collapse into a dark blob with the detail missing.</li>
      </ul>
    </div>
  </section>

  <section id="check3">
    <div class="sec-head pop">
      <div class="num">// CHECK 3</div>
      <h2>Color that <em>doesn't sit right</em></h2>
    </div>
    <div class="guide">
      <p>Fakes frequently get the <em>art</em> almost right and the <em>color</em> subtly wrong — a gradient that should glide smoothly from cream to gold prints muddy, gray-green, or speckled; reds go orange; the card looks like a photocopy of a photo of the card. Compare against the official card image for that exact set and number. A warning from our own desk, though: <b>judge color last, not first.</b> Photos, screens, and room lighting all lie about color. Color is a clue that sends you to the stronger tests — it isn't a verdict on its own.</p>
    </div>
  </section>

  <section id="check4">
    <div class="sec-head pop">
      <div class="num">// CHECK 4</div>
      <h2>The holo <em>and the feel</em></h2>
    </div>
    <div class="guide">
      <p>A genuine holo has depth: the pattern sits <em>in</em> the card and shifts as you tilt it. Many fakes have a sticker-like shine that sits <em>on</em> the card, a rainbow that moves all at once, or a texture you can feel as plastic rather than print. Run a fingertip across it. Real full-art cards have a fine, even texture; fakes are often dead smooth, or rough in the wrong, sandy way. (One exception to keep you honest: some genuine older cards and some genuine promos do unusual things with foil. Weird foil alone doesn't convict a card — it's one more piece of evidence.)</p>
    </div>
  </section>

  <section id="check5">
    <div class="sec-head pop">
      <div class="num">// CHECK 5</div>
      <h2>The details that <em>have to match</em></h2>
    </div>
    <div class="guide">
      <p>Line the card up against the official listing for its set and number and compare, one by one: the card number, the set symbol, the HP, the attacks and their energy costs, the weakness/resistance values, the copyright line. Counterfeits do sometimes get all of this right — the best ones are copies, after all — but plenty get lazy somewhere small, and one wrong detail is a real find. What you should <b>never</b> do is convict on a detail you haven't double-checked against the <em>correct</em> printing: many cards have multiple printings, and comparing against the wrong one manufactures a “fake” out of a real card.</p>
    </div>
  </section>

  <section id="verdict">
    <div class="sec-head pop">
      <div class="num">// SO — IS YOURS FAKE?</div>
      <h2>How we <em>honestly</em> land</h2>
    </div>
    <div class="guide">
      <p>Here's how we honestly land, and how our checker is allowed to talk:</p>
      <ul>
        <li><b>Likely genuine</b> — the back matches, it blocks the light, the print is crisp, the details line up. Enjoy your card.</li>
        <li><b>Likely counterfeit</b> — it fails the strong tests (light test, back comparison, mushy fine print) in ways that add up. The card stock doesn't lie.</li>
        <li><b>Inconclusive</b> — the clues point both ways, or the photos aren't good enough to call it. This is a real answer, not a cop-out. An honest “we can't tell from this” protects you from throwing away a real card <em>and</em> from trusting a fake one.</li>
      </ul>
      <p>Notice what's missing: percentages. Nobody honest can look at photos and say “87% real.” We think in bubbles of confidence, not fake-precision numbers, and you should be suspicious of anyone who does it the other way.</p>
    </div>
  </section>

  <section id="iffake">
    <div class="sec-head pop">
      <div class="num">// IF IT IS FAKE</div>
      <h2>Don't panic, and <em>don't pass it on</em></h2>
    </div>
    <div class="guide">
      <p>A counterfeit in your binder isn't a crime scene; it happens to shops, too — it's how this page exists. Just don't sell or trade it as genuine, ever. If you bought it recently as real, go back to the seller with what you found (photos of the light test are very persuasive), and give them the chance to make it right. Most marketplaces have a remedy path for counterfeit goods. And keep the card or clear photos of it until any case is closed — evidence first.</p>
    </div>
  </section>

  <section id="second-eyes">
    <div class="sec-head pop">
      <div class="num">// WANT A SECOND SET OF EYES?</div>
      <h2>Run it through <em>the office</em></h2>
    </div>
    <div class="guide">
      <p>This page is the free version of what we do all day. Our app, <a href="/app.html"><b>Real or Replica</b></a>, runs this exact routine on your photos — front <em>and</em> back, always — and a signed verdict comes back from real checkers, not just an algorithm's shrug.</p>
      <p>And if you'd rather just talk it through with people who've been fooled once and learned from it:</p>
      <p><b>Argue about it with us in the Discord.</b> Bring the card, bring your doubts — the evidence threads go deep, and nobody there will laugh at you for asking. <a href="https://discord.gg/Aj4ahGsSx" target="_blank" rel="noopener"><b>discord.gg/Aj4ahGsSx</b></a></p>
      <p class="signoff">— Noor 🦉 · Card Cauldron TCG · Van Wert, Ohio</p>
    </div>
  </section>

""" + more_doors("fake")

head = make_head(
    "Is My Card Fake? Start Here. | Card Cauldron TCG",
    "The same checks our Checking Office runs, in the order we run them: start with the back, then the light test, the print, the color, the details. Honest verdicts — Likely Genuine, Likely Counterfeit, or Inconclusive. Never percentages.",
    "is-my-card-fake.html", FAKE_CSS)
(ROOT / "is-my-card-fake.html").write_text(head + FAKE_MAIN + "</main>" + make_tail(), encoding="utf-8")
print("is-my-card-fake.html written")

# ---------- 6. sitemap ----------
sm = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
ASK_ENTRY = """  <url>
    <loc>https://cardcauldrontcg.com/ask.html</loc>
    <lastmod>2026-10-23</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>
"""
NEW_ENTRIES = ASK_ENTRY + """  <url>
    <loc>https://cardcauldrontcg.com/sets.html</loc>
    <lastmod>2026-10-23</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://cardcauldrontcg.com/is-my-card-fake.html</loc>
    <lastmod>2026-10-23</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://cardcauldrontcg.com/proof.html</loc>
    <lastmod>2026-10-23</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>
"""
sm = sub(sm, ASK_ENTRY, NEW_ENTRIES, 1, "sitemap new pages")
(ROOT / "sitemap.xml").write_text(sm, encoding="utf-8")
print("sitemap updated")
print("BUILD OK")
