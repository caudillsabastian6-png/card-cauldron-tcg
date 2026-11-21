/* Card Cauldron TCG — site pass helpers (Nov 20, 2026).
   1) a slow drifting background (sparkles, runes, soft mist) behind all content
   2) "show the first few" for long grids, with one Show-all button
   3) links to a section inside a closed "More about…" fold open it
   4) the page end always clears the floating dock + sound button
   Remove the <script src="/site-pass.js"> tag to roll all of it back. */
(function () {
  "use strict";
  var doc = document, root = doc.documentElement;
  var reduce = false;
  try { reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches; } catch (e) {}

  /* ---------- 4) bottom band: measure the fixed chrome, pad the page end ---------- */
  function band() {
    var H = window.innerHeight, top = H;
    var els = doc.querySelectorAll(".web-dock, #soundToggle");
    for (var i = 0; i < els.length; i++) {
      var cs = getComputedStyle(els[i]);
      if (cs.position !== "fixed" || cs.display === "none") continue;
      var r = els[i].getBoundingClientRect();
      if (r.height && r.top < top && r.top > H * 0.5) top = r.top;
    }
    root.style.setProperty("--cc-band", Math.max(0, Math.ceil(H - top)) + "px");
  }

  /* ---------- 4b) the dock + sound button stay out of the way: hidden on the first
     screen and while scrolling down to read, back on scroll up and at the page end ---------- */
  function chrome() {
    var lastY = window.scrollY || 0, ticking = false;
    function upd() {
      ticking = false;
      var y = window.scrollY || 0, H = window.innerHeight, end = root.scrollHeight - H - 40;
      var hide;
      if (end <= 80) hide = false;
      else if (y < 60) hide = true;
      else if (y >= end) hide = false;
      else if (Math.abs(y - lastY) < 6) return;
      else hide = y > lastY;
      lastY = y;
      root.classList.toggle("cc-chrome-hide", hide);
    }
    upd();
    window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(upd); } }, { passive: true });
    doc.addEventListener("focusin", function (e) {
      if (e.target.closest && e.target.closest(".web-dock, #soundToggle")) root.classList.remove("cc-chrome-hide");
    });
  }

  /* ---------- 2) long grids: show the first N, then one button ---------- */
  function limit(grid, n, noun) {
    if (!grid || grid.dataset.ccLimit) return;
    grid.dataset.ccLimit = n;
    grid.classList.add("cc-limit");
    var wrap = doc.createElement("div"); wrap.className = "cc-showall";
    var btn = doc.createElement("button"); btn.type = "button";
    wrap.appendChild(btn);
    grid.parentNode.insertBefore(wrap, grid.nextSibling);
    function mark() {
      var kids = grid.children, shown = 0, total = 0;
      for (var i = 0; i < kids.length; i++) {
        var k = kids[i];
        if (k.classList.contains("hide") || k.style.display === "none") { k.classList.remove("cc-over"); continue; }
        total++; shown++;
        k.classList.toggle("cc-over", shown > n);
      }
      wrap.style.display = total > n ? "" : "none";
      btn.textContent = grid.classList.contains("cc-all") ? "Show fewer" : "Show all " + total + " " + noun;
      btn.setAttribute("aria-expanded", grid.classList.contains("cc-all") ? "true" : "false");
    }
    btn.addEventListener("click", function () {
      var open = grid.classList.toggle("cc-all");
      mark();
      if (!open) grid.scrollIntoView({ block: "start" });
    });
    if (window.MutationObserver) new MutationObserver(mark).observe(grid, { childList: true });
    doc.addEventListener("click", function (e) {
      if (e.target.closest && e.target.closest(".chip")) setTimeout(mark, 0);
    });
    grid.ccMark = mark;
    mark();
  }

  /* ---------- 3) open a fold when a link points inside it ---------- */
  function openHash() {
    var id = decodeURIComponent((location.hash || "").slice(1));
    if (!id) return;
    var t = doc.getElementById(id);
    if (!t) return;
    var d = t.closest ? t.closest("details") : null, opened = false;
    while (d) { if (!d.open) { d.open = true; opened = true; } d = d.parentElement && d.parentElement.closest("details"); }
    if (opened) setTimeout(function () { t.scrollIntoView({ block: "start" }); }, 30);
  }

  /* ---------- 1) drifting background ---------- */
  function drift() {
    // retire the older per-page hex layer so only one background animates
    try { if (window.__ccScrollBg && window.__ccScrollBg.destroy) window.__ccScrollBg.destroy(); } catch (e) {}
    var old = doc.getElementById("ccScrollBg"); if (old) old.parentNode.removeChild(old);
    if (reduce || doc.getElementById("ccDrift")) return;

    var cv = doc.createElement("canvas"); cv.id = "ccDrift"; cv.setAttribute("aria-hidden", "true");
    var anchor = doc.getElementById("embers") || doc.body.firstChild;
    doc.body.insertBefore(cv, anchor);
    var ctx = cv.getContext("2d"); if (!ctx) return;
    var COLORS = ["166,120,232", "79,209,197", "226,184,74"]; // plum, teal, gold
    var W = 0, H = 0, dpr = 1, parts = [], mists = [], raf = 0, last = 0, t = 0, running = false;

    function rnd(a, b) { return a + Math.random() * (b - a); }
    function build() {
      var n = Math.round(Math.min(46, Math.max(22, W * H / 26000)));
      parts = [];
      for (var i = 0; i < n; i++) {
        parts.push({ x: Math.random(), y: Math.random(), z: rnd(0.25, 1), s: rnd(1.2, 3.2),
          c: COLORS[i % 3], k: i % 5 === 0 ? "rune" : (i % 3 === 0 ? "star" : "dot"),
          sp: rnd(4, 11), ph: rnd(0, 6.28), rot: rnd(0, 6.28), g: Math.floor(rnd(0, 4)) });
      }
      mists = [];
      for (var j = 0; j < 3; j++) mists.push({ x: rnd(0.1, 0.9), y: rnd(0.1, 0.9), r: rnd(0.35, 0.6), c: COLORS[j], ph: rnd(0, 6.28) });
    }
    function size() {
      dpr = Math.min(window.devicePixelRatio || 1, 1.5);
      W = window.innerWidth; H = window.innerHeight;
      cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      build();
    }
    function rune(g, r) {
      ctx.beginPath();
      if (g === 0) { ctx.moveTo(0, -r); ctx.lineTo(0, r); ctx.moveTo(0, -r * .4); ctx.lineTo(r * .7, -r); }
      else if (g === 1) { ctx.moveTo(-r * .6, r); ctx.lineTo(0, -r); ctx.lineTo(r * .6, r); ctx.moveTo(-r * .35, r * .2); ctx.lineTo(r * .35, r * .2); }
      else if (g === 2) { ctx.moveTo(0, -r); ctx.lineTo(r * .7, 0); ctx.lineTo(0, r); ctx.lineTo(-r * .7, 0); ctx.closePath(); }
      else { ctx.moveTo(-r * .6, -r); ctx.lineTo(r * .6, r); ctx.moveTo(r * .6, -r); ctx.lineTo(-r * .6, r); }
      ctx.stroke();
    }
    function draw() {
      ctx.clearRect(0, 0, W, H);
      var sy = window.scrollY || 0, i, p;
      for (i = 0; i < mists.length; i++) {
        var m = mists[i];
        var mx = (m.x + Math.sin(t * 0.03 + m.ph) * 0.08) * W;
        var my = (m.y + Math.cos(t * 0.025 + m.ph) * 0.06) * H - (sy * 0.04 % H);
        var rr = m.r * Math.max(W, H);
        var gr = ctx.createRadialGradient(mx, my, 0, mx, my, rr);
        gr.addColorStop(0, "rgba(" + m.c + ",0.10)"); gr.addColorStop(1, "rgba(" + m.c + ",0)");
        ctx.fillStyle = gr; ctx.fillRect(0, 0, W, H);
      }
      for (i = 0; i < parts.length; i++) {
        p = parts[i];
        var span = H + 80;
        var y = ((p.y * span - t * p.sp * p.z - sy * 0.18 * p.z) % span + span) % span - 40;
        var x = p.x * W + Math.sin(t * 0.25 + p.ph) * 18 * p.z;
        var a = (0.18 + 0.32 * p.z) * (0.6 + 0.4 * Math.sin(t * 0.8 + p.ph));
        ctx.save(); ctx.translate(x, y);
        ctx.fillStyle = ctx.strokeStyle = "rgba(" + p.c + "," + a.toFixed(3) + ")";
        if (p.k === "dot") { ctx.beginPath(); ctx.arc(0, 0, p.s * p.z, 0, 6.283); ctx.fill(); }
        else if (p.k === "star") {
          var r = p.s * 2.2 * p.z; ctx.rotate(p.rot + t * 0.05);
          ctx.beginPath(); ctx.moveTo(0, -r); ctx.lineTo(r * .22, -r * .22); ctx.lineTo(r, 0); ctx.lineTo(r * .22, r * .22);
          ctx.lineTo(0, r); ctx.lineTo(-r * .22, r * .22); ctx.lineTo(-r, 0); ctx.lineTo(-r * .22, -r * .22); ctx.closePath(); ctx.fill();
        } else { ctx.lineWidth = 1.2; ctx.rotate(Math.sin(t * 0.1 + p.ph) * 0.3); rune(p.g, 5 + 5 * p.z); }
        ctx.restore();
      }
    }
    function frame(now) {
      if (!running) return;
      raf = requestAnimationFrame(frame);
      if (now - last < 33) return;             // ~30 fps is plenty for a slow drift
      var dt = last ? Math.min((now - last) / 1000, 0.1) : 0.033; last = now; t += dt;
      draw();
    }
    function start() { if (running) return; running = true; last = 0; raf = requestAnimationFrame(frame); }
    function stop() { running = false; if (raf) cancelAnimationFrame(raf); raf = 0; }
    size(); draw(); start();
    window.addEventListener("resize", size);
    doc.addEventListener("visibilitychange", function () { if (doc.hidden) stop(); else start(); });
  }

  function init() {
    band();
    chrome();
    window.addEventListener("resize", band);
    setTimeout(band, 600);
    limit(doc.getElementById("catalogGrid"), 6, "cards here");
    limit(doc.getElementById("setsGrid"), 12, "sets");
    var ss = doc.getElementById("setSearch"), sg = doc.getElementById("setsGrid");
    if (ss && sg) ss.addEventListener("input", function () { sg.classList.toggle("cc-all", !!ss.value.trim()); if (sg.ccMark) sg.ccMark(); });
    openHash();
    window.addEventListener("hashchange", openHash);
    drift();
  }
  if (doc.readyState === "loading") doc.addEventListener("DOMContentLoaded", init); else init();
})();

/* =====================================================================
   IDEAS PASS (Nov 20, 2026) — ten small features, all client-side.
   No backend: nothing here collects or sends data. The only storage is
   localStorage on the visitor's own device (streaks, ticks, level).
   Mount points are empty <div data-cc="…"> tags in the HTML.
   ===================================================================== */

/* ---- 1) FAKE OF THE WEEK — swap weekly by editing this one object. ----
   fake/real: image paths already on the site. crop: [left, top, width, height]
   as fractions of the photo, to frame the card inside a shop photo (null = none).
   spots: callout dots on the framed card, x/y in % with the tell they point at. */
window.CC_FOTW = window.CC_FOTW || {
  week: "posted Nov 20, 2026",
  title: "Grit where it should be smooth",
  fake: { src: "assets/fake-charizard-gx.webp", crop: [0.15, 0.16, 0.72, 0.74],
          spots: [{ x: 47, y: 34, n: 1 }, { x: 52, y: 63, n: 2 }, { x: 30, y: 88, n: 3 }] },
  real: { src: "assets/genuine-charizard-gx.webp", crop: null,
          spots: [{ x: 47, y: 34, n: 1 }, { x: 55, y: 60, n: 2 }, { x: 22, y: 92, n: 3 }] },
  tells: [
    "A sandy grit covers the fake's whole face, even flat parts that are smooth on a real card.",
    "Behind the attack text the fake is muddy and speckled; the real card is a smooth gradient.",
    "The tiny bottom print is mush on the fake and crisp on the real card."
  ],
  note: "This fake came out of a trade lot we checked in October 2026. It also failed the light test: it glowed through."
};

/* ---- 7) TODAY'S FEATURED CARD — Potion can pin one card here: set it to the
   eBay item id from the card's shop.html "Buy on eBay" link (e.g. "307278485796").
   Leave null and the page picks one per day (seeded by the date in Eastern time). */
window.CC_FEATURED_PIN = window.CC_FEATURED_PIN || null;

(function () {
  "use strict";
  var doc = document, root = doc.documentElement;
  var reduce = false;
  try { reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches; } catch (e) {}
  var STORE = "https://www.ebay.com/str/cardcauldrontcg";
  var MAIL = "caudillsabastian6@gmail.com";
  var TESTER = "mailto:" + MAIL + "?subject=Real%20or%20Replica%20Android%20tester";

  /* ---------- tiny helpers ---------- */
  function $(sel, ctx) { return (ctx || doc).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || doc).querySelectorAll(sel)); }
  function el(tag, cls, text) { var e = doc.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  function get(k, d) { try { var v = localStorage.getItem("cc_" + k); return v == null ? d : JSON.parse(v); } catch (e) { return d; } }
  function put(k, v) { try { localStorage.setItem("cc_" + k, JSON.stringify(v)); } catch (e) {} }
  function mounts(name) { return $$('[data-cc="' + name + '"]'); }
  function path() { var p = location.pathname.replace(/\.html$/, "").replace(/\/index$/, "/"); return p || "/"; }
  function framed(img, crop) {
    var box = el("div", "cc-frame");
    if (crop) {
      var w = 100 / crop[2];
      img.style.width = w + "%";
      img.style.maxWidth = "none";
      img.style.marginLeft = (-crop[0] * w) + "%";
      img.style.marginTop = (-crop[1] * w * (4 / 3)) + "%"; // shop photos are 3:4
      box.classList.add("cc-cropped");
    }
    box.appendChild(img);
    return box;
  }
  function image(src, alt) { var i = el("img"); i.src = src; i.alt = alt || ""; i.loading = "lazy"; i.decoding = "async"; return i; }

  /* ---------- shop data: the catalog tiles on shop.html (same source as the shop page) ---------- */
  var shopCache = null, shopWait = [];
  function parseTiles(ctx) {
    return $$("#catalogGrid .tile", ctx).map(function (t) {
      var img = $(".ph img", t), buy = $(".buy", t), h = $("h3", t), set = $(".set", t), pr = $(".buy small", t);
      if (!img || !buy || !h) return null;
      return { name: h.textContent.trim(), set: set ? set.textContent.trim() : "", src: img.getAttribute("src"),
        alt: img.getAttribute("alt") || "", href: buy.getAttribute("href"),
        price: pr ? pr.textContent.replace(/[^\d.$]/g, "") : "" };
    }).filter(Boolean);
  }
  function shopData(cb) {
    if (shopCache) return cb(shopCache);
    shopWait.push(cb);
    if (shopWait.length > 1) return;
    function done(list) { shopCache = list; var w = shopWait; shopWait = []; w.forEach(function (f) { f(list); }); }
    if ($("#catalogGrid .tile")) return done(parseTiles(doc));
    if (!window.fetch || !window.DOMParser) return done([]);
    fetch("/shop.html", { credentials: "same-origin" }).then(function (r) { return r.ok ? r.text() : ""; })
      .then(function (html) { done(html ? parseTiles(new DOMParser().parseFromString(html, "text/html")) : []); })
      .catch(function () { done([]); });
  }

  /* ---------- 4) COLLECTOR LEVEL (pages visited + games played, this device only) ---------- */
  var LEVELS = [{ n: "Apprentice", at: 0, ic: "🧪" }, { n: "Alchemist", at: 5, ic: "⚗️" }, { n: "Archmage", at: 15, ic: "🔮" }];
  function points() { return Object.keys(get("pages", {})).length + (get("games", 0) | 0); }
  function levelOf(p) { var l = LEVELS[0]; LEVELS.forEach(function (x) { if (p >= x.at) l = x; }); return l; }
  function chipText() {
    var p = points(), l = levelOf(p), next = LEVELS[LEVELS.indexOf(l) + 1];
    return l.ic + " " + l.n + (next ? " · " + p + "/" + next.at + " to " + next.n : " · top level");
  }
  function toast(msg) {
    var t = el("div", "cc-toast", msg); t.setAttribute("role", "status");
    doc.body.appendChild(t);
    setTimeout(function () { t.classList.add("in"); }, 30);
    setTimeout(function () { t.classList.remove("in"); setTimeout(function () { t.remove(); }, 400); }, 3800);
  }
  function refreshLevel(quiet) {
    var l = levelOf(points()), was = get("level", null);
    $$(".cc-level").forEach(function (c) { c.textContent = chipText(); });
    if (was !== l.n) {
      put("level", l.n);
      if (was && !quiet) toast(l.ic + " Level up: you're now an " + l.n + "!");
    }
  }
  function played() { put("games", (get("games", 0) | 0) + 1); refreshLevel(); }
  function level() {
    var pages = get("pages", {}); pages[path()] = 1; put("pages", pages);
    var panel = $("#webMenuPanel");
    if (panel && !$(".cc-level", panel)) {
      var c = el("span", "cc-level"); c.title = "Collector level: pages explored + games played, saved on this device only";
      panel.insertBefore(c, panel.firstChild);
    }
    refreshLevel(!get("level", null));
    // existing games count too
    $$("#ccTeaser .opts button").forEach(function (b) { b.addEventListener("click", played); });
    var rip = $("#ripBtn"); if (rip) rip.addEventListener("click", played);
  }

  /* ---------- 5) EMBERWYRM TIP — once per page per visitor, inline (never floats over anything) ---------- */
  var TIPS = {
    "/": "Today's featured card changes every day at midnight Eastern.",
    "/shop": "Tap the glowing Mystery Pack for five random live cards.",
    "/sets": "Building a set? Tick what you own and see what's missing.",
    "/is-my-card-fake": "Start with the light test. It's the strongest check you own.",
    "/app": "The fakes on this page are real ones we held. Study the pairs.",
    "/bulk": "Got a box of bulk? Ask before you ship, so nothing's a surprise.",
    "/about": "Questions go to a real person. Ask away."
  };
  function tip() {
    var tipText = TIPS[path()];
    if (reduce || !tipText) return;
    var key = "tip" + path().replace(/\W/g, "_");
    if (get(key, 0)) return;
    var host = $("main section") ; if (!host) return;
    var head = $(".sec-head", host);
    var b = el("div", "cc-tip"); b.setAttribute("role", "note");
    var im = image("assets/emberwyrm.webp", ""); im.width = 40; im.height = 40; im.setAttribute("aria-hidden", "true");
    var p = el("p", null, tipText);
    var x = el("button", "cc-tip-x", "✕"); x.type = "button"; x.setAttribute("aria-label", "Dismiss tip");
    x.addEventListener("click", function () { b.remove(); });
    b.appendChild(im); b.appendChild(p); b.appendChild(x);
    if (head && head.parentNode === host) host.insertBefore(b, head.nextSibling); else host.insertBefore(b, host.firstChild);
    put(key, 1);
  }

  /* ---------- 1) FAKE OF THE WEEK ---------- */
  function fotw(m) {
    var F = window.CC_FOTW; if (!F) return;
    var box = el("div", "cc-fotw cc-teaser");
    box.appendChild(el("p", "cc-kicker", "Fake of the Week · " + F.week));
    box.appendChild(el("h3", null, F.title));
    var pair = el("div", "cc-fotw-pair");
    [["fake", "Known fake", "Known fake, a trade-lot sample photographed by the shop"], ["real", "Genuine", "Genuine, the official reference image"]].forEach(function (s) {
      var side = F[s[0]], fig = el("figure", "cc-fotw-side is-" + s[0]);
      var fr = framed(image(side.src, s[2]), side.crop);
      (side.spots || []).forEach(function (d) {
        var dot = el("span", "cc-dot", String(d.n)); dot.style.left = d.x + "%"; dot.style.top = d.y + "%"; dot.setAttribute("aria-hidden", "true");
        fr.appendChild(dot);
      });
      fig.appendChild(fr);
      fig.appendChild(el("figcaption", "cc-flag cc-flag-" + s[0], (s[0] === "fake" ? "✕ " : "✓ ") + s[1]));
      pair.appendChild(fig);
    });
    box.appendChild(pair);
    var ol = el("ol", "cc-tells"); F.tells.forEach(function (t) { ol.appendChild(el("li", null, t)); });
    box.appendChild(ol);
    box.appendChild(el("p", "small", (F.note ? F.note + " " : "") + "Tells are clues, not proof: a guide, not a guarantee."));
    m.appendChild(box);
  }

  /* ---------- 2) SPOT THE FAKE ---------- */
  var ROUNDS = [
    { fake: { src: "assets/fake-charizard-gx.webp", crop: [0.15, 0.16, 0.72, 0.74] }, real: { src: "assets/genuine-charizard-gx.webp" },
      tell: "The fake has sandy grit across the whole face and muddy print behind the attack text. The real card's print is a smooth gradient." },
    { fake: { src: "assets/fake-salazzle-gx.webp", crop: [0.22, 0.28, 0.58, 0.58] }, real: { src: "assets/genuine-salazzle-gx.webp" },
      tell: "This fake glowed straight through under a lamp. Real card stock blocks the light. A photo can't show that, so do the light test in hand." },
    { fake: { src: "assets/fake-mewtwo-ex.webp", crop: [0.11, 0.11, 0.81, 0.80] }, real: { src: "assets/genuine-mewtwo-ex.webp" },
      tell: "The fake's card number belongs to a different card, and the art is squeezed into a half-art frame. A number that doesn't match is a tell all by itself." },
    { fake: "Glows bright and see-through under a phone flashlight", real: "Blocks the light, with a dull shadow at most",
      tell: "Genuine card stock has an opaque core. A card that glows through isn't real." },
    { fake: "Its card number belongs to a different card", real: "Its card number matches its name and art",
      tell: "Check the number against the set list. A mismatch is a fake on its own." },
    { fake: "Flat silver bars look gritty and sandy", real: "Flat silver bars are smooth metal",
      tell: "Grit on parts that should be smooth foil is a print-quality tell." },
    { fake: "The tiny bottom print is blurry mush", real: "The tiny bottom print is crisp and readable",
      tell: "Real cards keep their small print sharp. Mushy fine print is a common fake tell." },
    { fake: "The font weight looks off: letters too thick or thin", real: "The lettering matches the same card from a pack",
      tell: "Fakes often get the typeface or weight slightly wrong. Compare with a card you know is real." }
  ];
  function spot(m) {
    var box = el("div", "cc-spot cc-teaser");
    box.innerHTML = '<p class="cc-kicker">Spot the Fake</p><h3>Which one is the fake?</h3>' +
      '<p class="cc-streak" aria-live="polite"></p><div class="cc-spot-q"></div><p class="fb" aria-live="polite"></p>' +
      '<div class="cc-ctas"><button type="button" class="btn btn-ghost cc-next" hidden>Next round →</button></div>' +
      '<p class="small">Tells are clues, not proof: a guide, not a guarantee. Photo pairs: our shop photo of a fake vs the official image of the real card.</p>' +
      '<p class="small"><a href="' + TESTER + '">Want the full checker? Be a free Android tester ✉</a></p>';
    m.appendChild(box);
    var q = $(".cc-spot-q", box), fb = $(".fb", box), nx = $(".cc-next", box), st = $(".cc-streak", box);
    var order = [], lastIdx = -1;
    function streak() { st.innerHTML = "Streak <b>" + (get("spot_streak", 0) | 0) + "</b> · Best <b>" + (get("spot_best", 0) | 0) + "</b>"; }
    function deal() {
      if (!order.length) { order = ROUNDS.map(function (_, i) { return i; }).sort(function () { return Math.random() - 0.5; }); if (order[0] === lastIdx) order.push(order.shift()); }
      var idx = order.shift(); lastIdx = idx;
      var R = ROUNDS[idx], fakeFirst = Math.random() < 0.5, photo = typeof R.fake === "object";
      q.innerHTML = ""; fb.textContent = ""; nx.hidden = true;
      q.className = "cc-spot-q " + (photo ? "is-photo" : "is-text");
      [fakeFirst ? "fake" : "real", fakeFirst ? "real" : "fake"].forEach(function (side, i) {
        var b = el("button", "cc-pick"); b.type = "button"; b.dataset.side = side;
        var label = i ? "B" : "A";
        if (photo) {
          var img = image(R[side].src, "Card " + label);
          b.appendChild(framed(img, R[side].crop || null));
          b.appendChild(el("span", "cc-pick-l", "Card " + label));
        } else {
          b.appendChild(el("span", "cc-pick-l", label));
          b.appendChild(el("span", "cc-pick-t", R[side]));
        }
        b.setAttribute("aria-label", "Card " + label + " is the fake" + (photo ? "" : ": " + R[side]));
        b.addEventListener("click", function () { answer(b, R); });
        q.appendChild(b);
      });
    }
    function answer(b, R) {
      if (q.classList.contains("done")) return;
      q.classList.add("done");
      var ok = b.dataset.side === "fake", s = get("spot_streak", 0) | 0;
      s = ok ? s + 1 : 0; put("spot_streak", s); if (s > (get("spot_best", 0) | 0)) put("spot_best", s);
      $$(".cc-pick", q).forEach(function (p) { p.disabled = true; p.classList.add(p.dataset.side === "fake" ? "was-fake" : "was-real"); });
      fb.innerHTML = (ok ? "<b>Got it.</b> " : "<b>Not this time.</b> ") + R.tell.replace(/&/g, "&amp;").replace(/</g, "&lt;");
      nx.hidden = false; streak(); played();
    }
    nx.addEventListener("click", deal);
    streak(); deal();
  }

  /* ---------- 3) MYSTERY PACK (upgrades the shop's existing Sample Pack; dealing stays in shop.html) ---------- */
  function mysteryPack() {
    var rip = $("#ripBtn"), hand = $("#packHand"), top = $("#samplePack .pack-top");
    if (!rip || !hand || !top || $(".cc-mpack", top)) return;
    var pack = el("button", "cc-mpack"); pack.type = "button"; pack.setAttribute("aria-label", "Open the Mystery Pack");
    pack.innerHTML = '<span aria-hidden="true">✦</span><i aria-hidden="true"></i>';
    top.insertBefore(pack, top.firstChild);
    top.classList.add("cc-hasmpack");
    function burst() { pack.classList.remove("burst"); void pack.offsetWidth; pack.classList.add("burst"); hand.classList.add("cc-flip"); }
    rip.addEventListener("click", burst);
    pack.addEventListener("click", function () {
      if (reduce) { rip.click(); return; }
      pack.classList.remove("burst"); void pack.offsetWidth; pack.classList.add("burst");
      setTimeout(function () { rip.click(); }, 420);
    });
  }

  /* ---------- 6) DONATION CAULDRON — empty on purpose until donations start ---------- */
  function donate(m) {
    m.innerHTML = '<div class="cc-donate-in cc-teaser" role="img" aria-label="Donation cauldron, empty: donations coming soon">' +
      '<svg class="cc-cauldron" viewBox="0 0 120 100" aria-hidden="true">' +
      '<g class="cc-steam"><path d="M42 30c-6-8 6-12 0-20"/><path d="M60 28c-6-8 6-12 0-20"/><path d="M78 30c-6-8 6-12 0-20"/></g>' +
      '<ellipse cx="60" cy="40" rx="44" ry="9" fill="#3A2260" stroke="#E2B84A" stroke-width="2.5"/>' +
      '<path d="M18 42c0 30 18 46 42 46s42-16 42-46" fill="#2A1745" stroke="#E2B84A" stroke-width="2.5"/>' +
      '<path d="M34 86l-6 10M86 86l6 10" stroke="#E2B84A" stroke-width="3" stroke-linecap="round"/>' +
      '<ellipse cx="60" cy="40" rx="38" ry="5.5" fill="#4FD1C5" opacity=".18"/></svg>' +
      '<div><p class="cc-kicker">Donation Cauldron</p><div class="cc-meter" aria-hidden="true"><span></span></div>' +
      '<p class="cc-donate-l">Donations coming soon</p></div></div>';
  }

  /* ---------- 7) TODAY'S FEATURED CARD ---------- */
  function etParts(d) {
    var f = new Intl.DateTimeFormat("en-US", { timeZone: "America/New_York", year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", second: "2-digit", hourCycle: "h23" });
    var o = {}; f.formatToParts(d).forEach(function (p) { o[p.type] = p.value; });
    return o;
  }
  function hash(str) { var h = 2166136261; for (var i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; }
  function featured(m) {
    m.innerHTML = '<p class="cc-kicker">Today\'s featured card</p><p class="small">Loading today\'s pick…</p>';
    var start = function () {
      shopData(function (list) {
        if (!list.length) { m.innerHTML = '<p class="cc-kicker">Today\'s featured card</p><p class="small">Today\'s pick couldn\'t load. <a href="/shop.html#catalog">Browse the catalog →</a></p>'; return; }
        var o = etParts(new Date()), day = o.year + "-" + o.month + "-" + o.day, c = null;
        if (window.CC_FEATURED_PIN) list.forEach(function (x) { if (x.href.indexOf(String(window.CC_FEATURED_PIN)) !== -1) c = x; });
        if (!c) c = list[hash("cc-featured-" + day) % list.length];
        m.innerHTML = "";
        var a = el("a", "cc-feat-card"); a.href = c.href; a.target = "_blank"; a.rel = "noopener";
        a.appendChild(image(c.src, c.alt));
        var info = el("div", "cc-feat-info");
        info.appendChild(el("p", "cc-kicker", "Today's featured card"));
        info.appendChild(el("h3", null, c.name));
        if (c.set) info.appendChild(el("p", "cc-feat-set", c.set));
        info.appendChild(el("p", "cc-feat-price", (c.price ? "Listed at " + c.price + " on eBay. " : "") + "The listing price is the final word."));
        var go = el("a", "btn btn-gold", "View it on eBay ↗"); go.href = c.href; go.target = "_blank"; go.rel = "noopener";
        var row = el("div", "cc-ctas"); row.appendChild(go); info.appendChild(row);
        var cd = el("p", "cc-countdown"); info.appendChild(cd);
        m.appendChild(a); m.appendChild(info);
        function tick() {
          var p = etParts(new Date()), left = 86400 - ((+p.hour) * 3600 + (+p.minute) * 60 + (+p.second));
          if (left <= 0 || left > 86400) left = 0;
          var h = Math.floor(left / 3600), mi = Math.floor(left % 3600 / 60), s = left % 60;
          cd.textContent = "New pick in " + h + "h " + (mi < 10 ? "0" : "") + mi + "m " + (s < 10 ? "0" : "") + s + "s (midnight Eastern)";
          if (left <= 1) setTimeout(function () { featured(m); }, 1500);
        }
        tick(); var iv = setInterval(function () { if (!doc.body.contains(cd)) clearInterval(iv); else if (!doc.hidden) tick(); }, 1000);
      });
    };
    if ("IntersectionObserver" in window) {
      var io = new IntersectionObserver(function (es) { if (es.some(function (e) { return e.isIntersecting; })) { io.disconnect(); start(); } }, { rootMargin: "400px" });
      io.observe(m);
    } else start();
  }

  /* ---------- 8) SET COMPLETION HELPER (sets.html) ---------- */
  function setHelper(m) {
    var names = $$("#setsGrid .set-card h3").map(function (h) { return h.textContent.trim(); });
    if (!names.length) return;
    m.innerHTML = '<div class="cc-sethelp cc-teaser"><label class="cc-kicker" for="ccSetPick">Pick a set</label>' +
      '<select id="ccSetPick"><option value="">Choose a set…</option></select>' +
      '<div class="cc-setbody"></div>' +
      '<p class="small">Your ticks are saved on this device only. Nothing is sent anywhere.</p></div>';
    var sel = $("#ccSetPick", m), body = $(".cc-setbody", m);
    names.forEach(function (n) { var o = el("option", null, n); o.value = n; sel.appendChild(o); });
    var last = get("set_last", ""); if (last && names.indexOf(last) !== -1) sel.value = last;
    var info = {};
    function render() {
      var n = sel.value; body.innerHTML = ""; put("set_last", n); if (!n) return;
      var key = n.toLowerCase(), known = info[key] || { total: 0, cards: {} };
      var saved = get("set_" + key, { total: 0, own: [] });
      var total = saved.total || known.total;
      var row = el("div", "cc-setrow");
      var lab = el("label", null, "Cards in the set ");
      var inp = el("input"); inp.type = "number"; inp.min = "1"; inp.max = "400"; inp.inputMode = "numeric"; inp.value = total || "";
      inp.placeholder = "e.g. 182";
      lab.appendChild(inp); row.appendChild(lab); body.appendChild(row);
      if (known.total) body.appendChild(el("p", "small", "Filled in from the number printed on our listings (…/" + known.total + "). Secret rares numbered above it aren't in the grid."));
      else body.appendChild(el("p", "small", "Type the number printed after the slash on your cards to build the checklist."));
      inp.addEventListener("change", function () {
        var v = Math.max(0, Math.min(400, parseInt(inp.value, 10) || 0)); saved.total = v; put("set_" + key, saved); render();
      });
      if (!total) return;
      var own = {}; (saved.own || []).forEach(function (x) { own[x] = 1; });
      var count = el("p", "cc-setcount"); body.appendChild(count);
      var grid = el("div", "cc-checks"); grid.setAttribute("role", "group"); grid.setAttribute("aria-label", "Card numbers you own");
      for (var i = 1; i <= total; i++) {
        var b = el("button", "cc-check", String(i)); b.type = "button"; b.dataset.n = i;
        b.setAttribute("aria-pressed", own[i] ? "true" : "false"); b.setAttribute("aria-label", "Card " + i + (own[i] ? ", owned" : ""));
        grid.appendChild(b);
      }
      body.appendChild(grid);
      var miss = el("div", "cc-missing"); body.appendChild(miss);
      function update() {
        var have = Object.keys(own).filter(function (k) { return +k <= total; }).length;
        count.innerHTML = "<b>" + have + "</b> of " + total + " ticked · " + (total - have) + " missing";
        miss.innerHTML = "";
        var inStock = [];
        for (var j = 1; j <= total; j++) if (!own[j] && known.cards[j]) inStock.push(known.cards[j]);
        if (inStock.length) {
          miss.appendChild(el("p", "cc-kicker", "Missing cards in our catalog"));
          var ul = el("ul", "cc-misslist");
          inStock.slice(0, 12).forEach(function (c) { var li = el("li"); var a = el("a", null, c.name + " ↗"); a.href = c.href; a.target = "_blank"; a.rel = "noopener"; li.appendChild(a); ul.appendChild(li); });
          miss.appendChild(ul);
        }
        var p = el("p", "small"); var a2 = el("a", null, "Look for the rest in our eBay store ↗"); a2.href = STORE; a2.target = "_blank"; a2.rel = "noopener";
        p.appendChild(a2); miss.appendChild(p);
      }
      grid.addEventListener("click", function (e) {
        var b = e.target.closest(".cc-check"); if (!b) return;
        var k = +b.dataset.n; if (own[k]) delete own[k]; else own[k] = 1;
        b.setAttribute("aria-pressed", own[k] ? "true" : "false"); b.setAttribute("aria-label", "Card " + k + (own[k] ? ", owned" : ""));
        saved.own = Object.keys(own).map(Number); put("set_" + key, saved); update();
      });
      update();
    }
    sel.addEventListener("change", render);
    var fold = m.closest("details"), loaded = false;
    function load() {
      if (loaded) return; loaded = true;
      body.innerHTML = '<p class="small">Loading…</p>';
      shopData(function (list) {
        list.forEach(function (c) {
          var mm = c.name.match(/(\d+)\s*\/\s*(\d+)\s*$/); if (!mm || !c.set) return;
          var k = c.set.toLowerCase(), it = info[k] || (info[k] = { total: 0, cards: {} });
          it.total = Math.max(it.total, +mm[2]); it.cards[+mm[1]] = c;
        });
        render();
      });
    }
    if (fold && !fold.open) fold.addEventListener("toggle", function () { if (fold.open) load(); }); else load();
  }

  /* ---------- tabs ---------- */
  function tabs(box) {
    var ts = $$('[role="tab"]', box);
    function show(t, focus) {
      ts.forEach(function (x) {
        var on = x === t; x.setAttribute("aria-selected", on ? "true" : "false"); x.tabIndex = on ? 0 : -1;
        var p = doc.getElementById(x.getAttribute("aria-controls")); if (p) p.hidden = !on;
      });
      if (focus) t.focus();
    }
    ts.forEach(function (t, i) {
      t.addEventListener("click", function () { show(t); });
      t.addEventListener("keydown", function (e) {
        var d = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
        if (d) { e.preventDefault(); show(ts[(i + d + ts.length) % ts.length], true); }
      });
    });
  }

  function init() {
    level();
    $$("[data-cc-tabs]").forEach(tabs);
    mounts("fotw").forEach(fotw);
    mounts("spot").forEach(spot);
    mounts("donate").forEach(donate);
    mounts("featured").forEach(featured);
    mounts("sets").forEach(setHelper);
    mysteryPack();
    tip();
  }
  if (doc.readyState === "loading") doc.addEventListener("DOMContentLoaded", init); else init();
})();
