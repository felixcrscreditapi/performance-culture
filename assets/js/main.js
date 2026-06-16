/* =================================================================
   PERFORMANCE CULTURE — interaction layer
   Lenis smooth scroll · GSAP ScrollTrigger · text decode · hero net
   ================================================================= */
(function () {
  "use strict";
  const root = document.documentElement;
  // Honour the OS "reduce motion" setting; `?static` forces the same calm,
  // animation-free rendering (used for print, low-power, and visual QA).
  const reduceMotion =
    window.matchMedia("(prefers-reduced-motion: reduce)").matches ||
    new URLSearchParams(location.search).has("static");
  const hasGSAP = !!(window.gsap && window.ScrollTrigger);
  if (hasGSAP) gsap.registerPlugin(ScrollTrigger);
  if (!hasGSAP || reduceMotion) root.classList.add("no-gsap");

  /* ---------- Lenis smooth scroll ---------- */
  let lenis = null;
  if (window.Lenis && !reduceMotion) {
    lenis = new Lenis({ lerp: 0.095, smoothWheel: true, wheelMultiplier: 1 });
    window.lenis = lenis; // expose instance (debug / programmatic scrolling)
    if (hasGSAP) {
      lenis.on("scroll", ScrollTrigger.update);
      gsap.ticker.add((t) => lenis.raf(t * 1000));
      gsap.ticker.lagSmoothing(0);
    } else {
      const raf = (t) => { lenis.raf(t); requestAnimationFrame(raf); };
      requestAnimationFrame(raf);
    }
  }

  /* ---------- Anchor navigation ---------- */
  document.querySelectorAll('a[href^="#"]').forEach((a) => {
    a.addEventListener("click", (e) => {
      const href = a.getAttribute("href");
      if (href.length < 2) return;
      const el = document.querySelector(href);
      if (!el) return;
      e.preventDefault();
      if (lenis) lenis.scrollTo(el, { offset: -70, duration: 1.25 });
      else el.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth" });
    });
  });

  /* ---------- Nav state + scroll progress ---------- */
  const nav = document.getElementById("nav");
  const progress = document.querySelector(".scroll-progress span");
  const closingEl = document.getElementById("closing");
  function onScroll() {
    const y = window.scrollY || window.pageYOffset || 0;
    if (nav) nav.classList.toggle("is-scrolled", y > 40);
    if (nav && closingEl) {
      const r = closingEl.getBoundingClientRect();
      nav.classList.toggle("is-on-light", r.top <= 64 && r.bottom >= 64);
    }
    if (progress) {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      progress.style.width = (max > 0 ? (y / max) * 100 : 0) + "%";
    }
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---------- Custom cursor dot ---------- */
  const dot = document.querySelector(".cursor-dot");
  if (dot && window.matchMedia("(hover:hover) and (pointer:fine)").matches) {
    let x = innerWidth / 2, y = innerHeight / 2, tx = x, ty = y;
    window.addEventListener("mousemove", (e) => { tx = e.clientX; ty = e.clientY; dot.style.opacity = "1"; });
    (function loop() {
      x += (tx - x) * 0.2; y += (ty - y) * 0.2;
      dot.style.transform = `translate(${x}px, ${y}px) translate(-50%, -50%)`;
      requestAnimationFrame(loop);
    })();
    document.querySelectorAll("a, button, .btn, .marker").forEach((el) => {
      el.addEventListener("mouseenter", () => dot.classList.add("is-hover"));
      el.addEventListener("mouseleave", () => dot.classList.remove("is-hover"));
    });
  }

  /* ---------- Text decode (scramble) ---------- */
  const GLYPHS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#%&/()=+*<>";
  function decode(el, delay, duration) {
    const finalHTML = el.innerHTML;
    const finalText = el.textContent;
    const n = finalText.length;
    const start = performance.now() + (delay || 0);
    function frame(now) {
      const t = (now - start) / (duration || 800);
      if (t < 0) { requestAnimationFrame(frame); return; }
      if (t >= 1) { el.innerHTML = finalHTML; return; }
      const revealed = Math.floor(t * t * n);
      let out = "";
      for (let i = 0; i < n; i++) {
        const c = finalText[i];
        if (c === " " || i < revealed) out += c;
        else out += GLYPHS[(Math.random() * GLYPHS.length) | 0];
      }
      el.textContent = out;
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  /* ---------- Hero intro ---------- */
  if (hasGSAP && !reduceMotion) {
    const lines = gsap.utils.toArray(".hero__title .line > *");
    const finals = lines.map((el) => el.innerHTML);
    gsap.set(".hero__title", { opacity: 1 });           // reveal container; lines masked below
    gsap.set(lines, { yPercent: 115 });                 // clean baseline (no CSS transform)
    gsap.set([".hero .eyebrow", ".hero__lede", ".hero__actions"], { opacity: 0, y: 26 });

    const tl = gsap.timeline({ delay: 0.2, defaults: { ease: "power3.out" } });
    tl.to(".hero .eyebrow", { opacity: 1, y: 0, duration: 0.7 })
      .to(lines, { yPercent: 0, duration: 1.05, stagger: 0.08 }, "-=0.25")
      .to(".hero__lede", { opacity: 1, y: 0, duration: 0.8 }, "-=0.5")
      .to(".hero__actions", { opacity: 1, y: 0, duration: 0.7 }, "-=0.55");

    lines.forEach((el, i) => decode(el, 380 + i * 150, 820));

    // Safety net: guarantee the intro reaches its end state even if rAF is
    // throttled (background tab / headless), so content is never left hidden.
    window.setTimeout(() => {
      if (tl.progress() < 1) tl.progress(1);
      lines.forEach((el, i) => { if (el.innerHTML !== finals[i]) el.innerHTML = finals[i]; });
    }, 3200);
  }

  /* ---------- Scroll reveals ---------- */
  if (hasGSAP && !reduceMotion) {
    // generic fade-up (exclude hero, handled above)
    gsap.utils.toArray(".reveal").filter((el) => !el.closest(".hero")).forEach((el) => {
      gsap.from(el, {
        opacity: 0, y: 34, duration: 0.95, ease: "power3.out",
        scrollTrigger: { trigger: el, start: "top 86%" },
      });
    });

    // masked line reveals
    gsap.utils.toArray(".reveal-line").forEach((line) => {
      const inner = line.firstElementChild || line;
      gsap.from(inner, {
        yPercent: 115, duration: 1.05, ease: "power3.out",
        scrollTrigger: { trigger: line, start: "top 90%" },
      });
    });

    // per-marker title + essence
    gsap.utils.toArray(".marker").forEach((m) => {
      gsap.from(m.querySelectorAll(".marker__title, .marker__essence"), {
        opacity: 0, y: 30, duration: 0.85, stagger: 0.12, ease: "power3.out",
        scrollTrigger: { trigger: m, start: "top 80%" },
      });
    });

    // subtle drift on the big marker numbers
    gsap.utils.toArray(".marker__num").forEach((num) => {
      gsap.fromTo(num, { y: -12 }, {
        y: 12, ease: "none",
        scrollTrigger: { trigger: num.closest(".marker"), start: "top bottom", end: "bottom top", scrub: true },
      });
    });

    // hero vista parallax
    gsap.to(".hero__vista", {
      yPercent: 16, ease: "none",
      scrollTrigger: { trigger: ".hero", start: "top top", end: "bottom top", scrub: true },
    });

    // evolving aurora — drifts across the whole journey
    gsap.to(".bg-aurora__blob--1", {
      yPercent: 34, xPercent: 16, ease: "none",
      scrollTrigger: { trigger: document.body, start: "top top", end: "bottom bottom", scrub: 1 },
    });
    gsap.to(".bg-aurora__blob--2", {
      yPercent: -40, xPercent: -12, ease: "none",
      scrollTrigger: { trigger: document.body, start: "top top", end: "bottom bottom", scrub: 1 },
    });

    // interlude background parallax
    gsap.to(".interlude__bg img", {
      yPercent: 14, ease: "none",
      scrollTrigger: { trigger: ".interlude", start: "top bottom", end: "bottom top", scrub: true },
    });

    // movement image bands — parallax + staggered content reveal
    gsap.utils.toArray(".band").forEach((band) => {
      const img = band.querySelector(".band__bg img");
      if (img) {
        gsap.fromTo(img, { yPercent: -9 }, {
          yPercent: 9, ease: "none",
          scrollTrigger: { trigger: band, start: "top bottom", end: "bottom top", scrub: true },
        });
      }
      gsap.from(band.querySelectorAll(".band__n, .band__title, .band__desc, .band__range"), {
        opacity: 0, y: 44, duration: 1, stagger: 0.1, ease: "power3.out",
        scrollTrigger: { trigger: band, start: "top 68%" },
      });
    });
  }

  /* ---------- Active index (rail + marker) ---------- */
  const railLinks = new Map();
  document.querySelectorAll(".rail__list a").forEach((a) => railLinks.set(a.dataset.rail, a));
  const markers = document.querySelectorAll(".marker");
  if (markers.length) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (!en.isIntersecting) return;
        const id = en.target.id;
        markers.forEach((m) => m.classList.toggle("is-active", m === en.target));
        railLinks.forEach((a, k) => a.classList.toggle("is-active", k === id));
      });
    }, { rootMargin: "-45% 0px -50% 0px", threshold: 0 });
    markers.forEach((m) => io.observe(m));
  }

  /* ---------- Fixed rail: visible only during The Field ---------- */
  const railEl = document.querySelector(".rail");
  const fieldSection = document.getElementById("field");
  if (railEl && fieldSection) {
    new IntersectionObserver((entries) => {
      entries.forEach((e) => railEl.classList.toggle("is-visible", e.isIntersecting));
    }, { rootMargin: "-12% 0px -25% 0px" }).observe(fieldSection);
  }

  /* ---------- Active section (nav) ---------- */
  const navLinks = {};
  document.querySelectorAll(".nav__links a").forEach((a) => { navLinks[a.getAttribute("href").slice(1)] = a; });
  const secIO = new IntersectionObserver((entries) => {
    entries.forEach((en) => {
      if (!en.isIntersecting) return;
      Object.values(navLinks).forEach((a) => a.classList.remove("is-active"));
      if (navLinks[en.target.id]) navLinks[en.target.id].classList.add("is-active");
    });
  }, { rootMargin: "-50% 0px -50% 0px", threshold: 0 });
  ["premise", "language", "field", "closing"].forEach((id) => {
    const el = document.getElementById(id);
    if (el) secIO.observe(el);
  });

  /* ---------- Hero network canvas ---------- */
  const canvas = document.getElementById("net");
  if (canvas && !reduceMotion) {
    const ctx = canvas.getContext("2d");
    const host = canvas.parentElement;
    let w = 0, h = 0, dpr = 1, nodes = [], running = false, rafId = 0;
    const LINK = 150;

    function size() {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      const r = host.getBoundingClientRect();
      w = r.width; h = r.height;
      canvas.width = w * dpr; canvas.height = h * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const count = Math.max(26, Math.min(64, Math.floor((w * h) / 17000)));
      nodes = Array.from({ length: count }, () => ({
        x: Math.random() * w, y: Math.random() * h,
        vx: (Math.random() - 0.5) * 0.26, vy: (Math.random() - 0.5) * 0.26,
      }));
    }

    function tick() {
      if (!running) return;
      ctx.clearRect(0, 0, w, h);
      for (const n of nodes) {
        n.x += n.vx; n.y += n.vy;
        if (n.x < 0 || n.x > w) n.vx *= -1;
        if (n.y < 0 || n.y > h) n.vy *= -1;
      }
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const a = nodes[i], b = nodes[j];
          const dx = a.x - b.x, dy = a.y - b.y;
          const d = Math.hypot(dx, dy);
          if (d < LINK) {
            ctx.strokeStyle = "rgba(157,107,255," + ((1 - d / LINK) * 0.2).toFixed(3) + ")";
            ctx.lineWidth = 1;
            ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
          }
        }
      }
      for (const n of nodes) {
        ctx.fillStyle = "rgba(236,237,239,0.45)";
        ctx.beginPath(); ctx.arc(n.x, n.y, 1.3, 0, 6.2832); ctx.fill();
      }
      rafId = requestAnimationFrame(tick);
    }

    function play() { if (!running) { running = true; tick(); } }
    function pause() { running = false; cancelAnimationFrame(rafId); }

    size();
    play();
    let rt;
    window.addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(size, 200); });
    new IntersectionObserver((es) => {
      es.forEach((e) => (e.isIntersecting ? play() : pause()));
    }, { threshold: 0 }).observe(host);
  }

  /* refresh triggers after full load (fonts/images) */
  window.addEventListener("load", () => { if (hasGSAP) ScrollTrigger.refresh(); });
})();
