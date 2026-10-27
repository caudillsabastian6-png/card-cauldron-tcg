#!/usr/bin/env python3
"""v13 build — adds Noor's 'Ask the Office' page (round-2 on-the-house idea, vetted + approved Oct 23).

Base: v12-build/ copied to v13-build/. Changes, and only these:
  1. NEW ask.html — generated from app.html's shell (head/CSS/nav/footer/script bundle 1)
     with Ask-the-Office head metadata, its own main content, and a small FAQ script.
     The signed-answers archive launches EMPTY by design (guardrail: only office-signed
     answers ever post; none exist yet, so none are shown — never invent one).
  2. Nav: 'Ask the Office' link inserted after 'Real or Replica' in .links and .mnav
     on the 5 nav pages (privacy.html carries no shared nav — untouched, byte-identical).
  3. sitemap.xml: ask.html added; lastmod bumped to 2026-10-23 on the nav-changed pages.
Every replacement is count-asserted; a mismatch aborts the build.
"""
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent

def sub(text, old, new, count, where):
    n = text.count(old)
    assert n == count, f"{where}: expected {count}x {old[:60]!r}, found {n}"
    return text.replace(old, new)

ASK_LINK = '<a href="/ask.html">Ask the Office</a>'
ASK_LINK_CURRENT = '<a href="/ask.html" aria-current="page">Ask the Office</a>'
APP_PLAIN = '<a href="/app.html">Real or Replica</a>'
APP_CURRENT = '<a href="/app.html" aria-current="page">Real or Replica</a>'

# ---------- 1. nav patch on the five existing nav pages ----------
for name in ["index.html", "shop.html", "bulk.html", "app.html", "about.html"]:
    p = ROOT / name
    t = p.read_text(encoding="utf-8")
    if APP_CURRENT in t:  # this page is app.html itself: keep its own current marker
        t = sub(t, APP_CURRENT, APP_CURRENT + "\n    " + ASK_LINK, 2, name)
    else:
        t = sub(t, APP_PLAIN, APP_PLAIN + "\n    " + ASK_LINK, 2, name)
    p.write_text(t, encoding="utf-8")
    print(f"nav patched: {name}")

# ---------- 2. ask.html from app.html shell ----------
app = (ROOT / "app.html").read_text(encoding="utf-8")
head, rest = app.split('<main id="top">', 1)
_, tail = rest.split('</main>', 1)

# head metadata
OLD_TITLE = "Real or Replica — Pokémon Card Checker | Card Cauldron TCG"
NEW_TITLE = "Ask the Office — Signed Card Answers | Card Cauldron TCG"
OLD_DESC = ("Real or Replica is Card Cauldron TCG's Pokémon card checker. Study genuine-vs-fake pairs "
            "from our own checking files, learn the tells, and spot a counterfeit before it costs you.")
NEW_DESC = ("Ask the Office is where Card Cauldron TCG's Checking Office answers your Pokémon card questions. "
            "Answers are posted only after the office signs them — no unsigned answers, ever.")
head = sub(head, OLD_TITLE, NEW_TITLE, 3, "ask head title")          # <title>, og:title, twitter:title
head = sub(head, OLD_DESC, NEW_DESC, 3, "ask head desc")             # description, og:, twitter:
head = sub(head, "https://cardcauldrontcg.com/app.html", "https://cardcauldrontcg.com/ask.html", 2, "ask head url")
# nav in head part: app.html was built above from the already-nav-patched app.html,
# so it currently has app=aria-current + plain ask links. Fix: app loses current, ask gains it.
head = sub(head, APP_CURRENT, APP_PLAIN, 2, "ask nav app")
head = sub(head, ASK_LINK, ASK_LINK_CURRENT, 2, "ask nav ask")

# page-specific CSS, injected INSIDE the head <style> block (just before its closing
# </style>, which directly precedes </head>). Injecting before </head> instead would
# strand the CSS as raw text after </style> — browsers render it as visible page text
# and the rules never apply. (That was the v13/v14 CSS-leak bug, fixed Oct 23.)
ASK_CSS = """
  /* ---------- v13 Ask the Office ---------- */
  .ask-search{max-width:46rem; margin-top:2rem}
  .ask-search-label{display:block; font-weight:700; margin-bottom:.5rem}
  .ask-search input{width:100%; font:inherit; padding:.8rem 1rem; border-radius:12px; border:1px solid rgba(255,233,176,.35); background:var(--panel); color:var(--ink)}
  .ask-search input:focus{outline:2px solid var(--gold); outline-offset:1px}
  .ask-answers{display:grid; gap:1rem; margin-top:1.6rem; max-width:46rem}
  .ask-answer{background:var(--panel); border:1px solid rgba(255,233,176,.22); border-radius:16px; padding:1.2rem 1.3rem}
  .ask-answer h3{margin:0 0 .45rem; font-size:1.15rem}
  .ask-answer p{margin:0; color:var(--muted)}
  .ask-answer .ask-sig{margin-top:.8rem; color:var(--gold); font-weight:700; font-size:.9rem}
  .ask-empty{color:var(--muted); max-width:46rem; margin-top:1.6rem; font-size:1.02rem}
"""
head = sub(head, "</style>\n</head>", ASK_CSS + "</style>\n</head>", 1, "ask css")

MAIN = """<main id="top">

  <!-- ============ ASK THE OFFICE (Noor's idea, round-2 on-the-house, vetted + approved Oct 23) ============ -->
  <section id="ask">
    <div class="sec-head pop">
      <div class="num">// NEW — ASK THE OFFICE</div>
      <h2>Ask the <em>Office</em></h2>
      <p>Got a Pokémon card you're not sure about — a holo that looks off, a texture that feels wrong, a deal that smells too good? Ask the shop's <b>Checking Office</b>. Every answer posted here was earned the slow way: the office ran a real check on the card first, and <b>signed</b> the answer before it went up. If it isn't signed, it isn't posted. No exceptions, no auto-replies.</p>
    </div>
    <div class="contact-grid">
      <a class="linkcard zoom d1" href="mailto:caudillsabastian6@gmail.com?subject=Ask%20the%20Office">
        <div class="glyph">✉️</div>
        <h3>Ask by email</h3>
        <p>Tell us the card's name, its set, and what looks off. Clear photos of the front <b>and</b> the back help the office most — a check is only as good as what it can see.</p>
      </a>
      <a class="linkcard zoom d2" href="https://discord.gg/Aj4ahGsSx" target="_blank" rel="noopener">
        <div class="glyph">💬</div>
        <h3>Ask in the Discord</h3>
        <p>Drop your question in our Discord and point the office at it. Same rule applies: answers post here once they're signed, and your name never goes up with them.</p>
      </a>
    </div>
  </section>

  <!-- ============ THE SIGNED RULE ============ -->
  <section id="how">
    <div class="sec-head pop">
      <div class="num">// THE SIGNED RULE</div>
      <h2>How an answer earns its <em>signature</em></h2>
      <p>An answer on this page is a claim the shop stands behind, so it has to survive the same gauntlet as every card in <a href="/app.html">Real or Replica</a>.</p>
    </div>
    <div class="contact-grid">
      <div class="linkcard zoom d1">
        <div class="glyph">🃏</div>
        <h3>1 — You ask</h3>
        <p>Email or Discord: the card's name, its set, and what looks off. Front and back photos help the office most.</p>
      </div>
      <div class="linkcard zoom d2">
        <div class="glyph">🔎</div>
        <h3>2 — The office looks</h3>
        <p>Lens takes the first round, Gauge takes the second, and the call is made at the boss's desk — the same three-step signing as every check the office runs.</p>
      </div>
      <div class="linkcard zoom d3">
        <div class="glyph">🖋️</div>
        <h3>3 — It posts, signed</h3>
        <p>Only then does the answer land here, carrying its signature and the date it was signed. Still being looked at? It isn't here yet — we'd rather post late than post wrong.</p>
      </div>
    </div>
  </section>

  <!-- ============ SIGNED ANSWERS ARCHIVE ============ -->
  <section id="answers">
    <div class="sec-head pop">
      <div class="num">// THE ARCHIVE</div>
      <h2>Signed <em>answers</em></h2>
      <p>Every answer below carries the Checking Office's signature. Search the archive — and if your question isn't here yet, <a href="#ask">ask it</a>.</p>
    </div>
    <div class="ask-search">
      <label class="ask-search-label" for="askSearch">Search signed answers</label>
      <input id="askSearch" type="search" placeholder="Try a card name, a set, or a tell — texture, holo bleed, yellow border…" autocomplete="off" />
    </div>
    <div id="askAnswers" class="ask-answers" aria-live="polite"></div>
    <p id="askEmpty" class="ask-empty"></p>
  </section>

"""

FAQ_SCRIPT = """<script>
(function(){
  "use strict";
  /* ================================================================
     SIGNED ANSWERS — CREW ONLY.
     Add an entry ONLY when the Checking Office has signed the answer
     (a real check: Lens round + Gauge round + boss decision, with the
     office-issued check number). Never invent an entry, a signature,
     or a check number. Format:
       { q: "The question, names removed",
         a: "The signed answer, in plain words.",
         check: "FC-0000",
         signed: "YYYY-MM-DD" }
     ================================================================ */
  var SIGNED_ANSWERS = [
    /* No signed answers yet — the archive launches empty on purpose. */
  ];
  var EMPTY_COPY = "No signed answers yet. The archive opens empty on purpose — answers appear here once the Checking Office has signed them, and not a moment before. Yours could be the first: ask the office above.";
  var NOMATCH_COPY = "No signed answers match that search yet. Try a card name or a shorter word — or ask the office above and start a new one.";
  var list = document.getElementById("askAnswers");
  var empty = document.getElementById("askEmpty");
  var search = document.getElementById("askSearch");
  if (!list || !empty) return;
  function render(items, query){
    list.innerHTML = "";
    if (!items.length){
      empty.textContent = query ? NOMATCH_COPY : EMPTY_COPY;
      empty.style.display = "";
      return;
    }
    empty.style.display = "none";
    items.forEach(function(it){
      var card = document.createElement("article");
      card.className = "ask-answer";
      var q = document.createElement("h3"); q.textContent = it.q;
      var a = document.createElement("p"); a.textContent = it.a;
      var sig = document.createElement("p"); sig.className = "ask-sig";
      sig.textContent = "✔ Signed by the Checking Office · Check " + it.check + " · " + it.signed;
      card.appendChild(q); card.appendChild(a); card.appendChild(sig);
      list.appendChild(card);
    });
  }
  render(SIGNED_ANSWERS, "");
  if (search){
    search.addEventListener("input", function(){
      var query = search.value.trim().toLowerCase();
      if (!query){ render(SIGNED_ANSWERS, ""); return; }
      render(SIGNED_ANSWERS.filter(function(it){
        return (it.q + " " + it.a).toLowerCase().indexOf(query) !== -1;
      }), query);
    });
  }
})();
</script>
"""

# tail: footer + sound button + script bundle 1 only (drop app.html's quiz/wheel bundle 2)
parts = tail.split("<script>")
assert len(parts) == 3, f"ask tail: expected footer + 2 script bundles, got {len(parts)-1} bundles"
tail = parts[0] + "<script>" + parts[1] + FAQ_SCRIPT + "</body>\n</html>\n"

(ROOT / "ask.html").write_text(head + MAIN + "</main>" + tail, encoding="utf-8")
print("ask.html written")

# ---------- 3. sitemap ----------
sm = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
for page in ["", "shop.html", "bulk.html", "app.html", "about.html"]:
    sm = sub(sm, f"<loc>https://cardcauldrontcg.com/{page}</loc>\n    <lastmod>2026-10-22</lastmod>",
             f"<loc>https://cardcauldrontcg.com/{page}</loc>\n    <lastmod>2026-10-23</lastmod>", 1, f"sitemap {page or 'home'}")
APP_ENTRY = """  <url>
    <loc>https://cardcauldrontcg.com/app.html</loc>
    <lastmod>2026-10-23</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
"""
ASK_ENTRY = APP_ENTRY + """  <url>
    <loc>https://cardcauldrontcg.com/ask.html</loc>
    <lastmod>2026-10-23</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>
"""
sm = sub(sm, APP_ENTRY, ASK_ENTRY, 1, "sitemap ask")
(ROOT / "sitemap.xml").write_text(sm, encoding="utf-8")
print("sitemap updated")
print("BUILD OK")
