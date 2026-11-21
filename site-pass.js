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
