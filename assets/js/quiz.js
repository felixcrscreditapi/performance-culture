/* =================================================================
   PERFORMANCE CULTURE — Apply-it quizzes, gated certificate, confetti
   ----------------------------------------------------------------
   Each distinction gets a situation question. The learner writes how
   they'd apply it; the answer is graded 0–10 by an AI evaluator
   (POST /api/evaluate, served by serve.py with ANTHROPIC_API_KEY).
   When the file is opened without that backend, a local heuristic
   keeps the flow usable (approximate — real grading needs the server).
   Pass 8/10+ on all 13 to unlock a personalised certificate.
   ================================================================= */
(function () {
  "use strict";

  var PASS = 8;
  var TOTAL = 13;
  var STORE = "pc_quiz_v2";

  /* ---------- Situation questions (mirrored in serve.py for grading) ---------- */
  var QUIZ = [
    { id: "d01", n: "01", title: "Complete Work",
      q: "A teammate says the new CSV-export feature is “done” — the code is merged and the tests pass. Applying Complete Work: what is still missing before this is genuinely complete, and what does “done” actually require here?" },
    { id: "d02", n: "02", title: "Ownership",
      q: "You own a data-migration task. In standup, three people give three different answers about its status and nobody can say when it will finish. Applying Ownership: what has gone wrong, and what specifically would you do?" },
    { id: "d03", n: "03", title: "Demonstrated By",
      q: "Your team agrees the goal this quarter is to “make onboarding world-class.” Apply Demonstrated By: write 2–3 concrete things you would observe in reality if this goal were truly met." },
    { id: "d04", n: "04", title: "By When",
      q: "A colleague messages: “I'll get you the pricing analysis as soon as I can.” Using By When: what is the problem with this, and how should the commitment be restated?" },
    { id: "d05", n: "05", title: "The Burndown List",
      q: "You've been handed an ambiguous goal — “reduce customer churn” — and no project tool, just a sheet of paper. Applying The Burndown List: what do you actually put on it, and how does that get you moving?" },
    { id: "d06", n: "06", title: "Qualification is the Enemy of Performance",
      q: "You keep postponing the launch of your proposal because you want to first finish another certification and “be fully ready.” Apply this distinction: what is happening, and what should you do instead?" },
    { id: "d07", n: "07", title: "Communication — Intentional & Effective",
      q: "You sent a detailed Slack message about a pricing change and got two thumbs-up emojis. A week later, Sales acts as if they never heard about it. Apply Intentional & Effective Communication: what went wrong, and what would “effective” have looked like?" },
    { id: "d08", n: "08", title: "Alignment & Enrollment",
      q: "You want to roll out a new code-review process, but two senior engineers think it's a waste of time. Apply Alignment & Enrollment: how do you move forward, and what does “disagree and commit” mean here?" },
    { id: "d09", n: "09", title: "Symptoms vs. Systems",
      q: "Every Monday someone spends two hours manually fixing the same broken report, and it's now “just how we do it.” Apply Symptoms vs. Systems: what is happening, and what is the better move?" },
    { id: "d10", n: "10", title: "Mastering The Tools I Own",
      q: "Your team complains they're slow, and you notice everyone uses your core software at a beginner level with lots of manual workarounds. Apply Mastering The Tools I Own: what would you do, and why?" },
    { id: "d11", n: "11", title: "What I Measure Grows",
      q: "A team insists things are “going well,” but nobody can point to a number — and the one metric they could track looks embarrassing right now. Apply What I Measure Grows: what do you do?" },
    { id: "d12", n: "12", title: "10x Results",
      q: "You spend all your time keeping the existing reporting machine running smoothly and have no time for anything else. Apply 10x Results: what is missing from how you operate, and what would you change?" },
    { id: "d13", n: "13", title: "Dealing with Breakdowns",
      q: "A teammate missed a promised deadline and didn't tell you; your first instinct is that they don't respect your time. Apply Dealing with Breakdowns (and Hanlon's Razor): how do you handle it?" }
  ];

  /* keyword groups for the OFFLINE heuristic fallback only */
  var KEYS = {
    d01: [["customer", "production", "rolled out", "in the hands", "live", "released"], ["document", "marketing", "sales", "train", "monitor"], ["intention", "intended", "complete"]],
    d02: [["own", "ownership", "command", "answer"], ["beginning to end", "ledger", "burn", "single"], ["lead", "resources", "velocity"]],
    d03: [["observe", "see", "measurable", "concrete", "reality"], ["demonstrate", "criteria", "evidence"], ["specific", "number", "unambiguous"]],
    d04: [["by when", "date", "deadline", "time", "5pm", "calendar"], ["commit", "chatter", "vague", "asap"], ["follow up", "reliable", "revise"]],
    d05: [["point a", "point b", "steps", "tasks", "list"], ["paper", "burndown", "plan"], ["intention", "demonstrated", "by when"]],
    d06: [["act", "action", "start", "ship", "ownership"], ["qualified", "certification", "ready", "permission"], ["deliver", "complete work"]],
    d07: [["land", "received", "acknowledge", "recreate", "confirm"], ["intention", "intend", "heard"], ["next step", "owner", "loop", "effective"]],
    d08: [["enroll", "enrollment", "align", "alignment"], ["disagree", "commit", "concern", "consideration"], ["benefit", "their", "next step", "acknowledge"]],
    d09: [["system", "root cause", "underlying"], ["symptom", "patch", "manual", "repeat"], ["step back", "conscious", "redesign", "automate", "fix"]],
    d10: [["master", "learn", "tool", "training"], ["force multiplier", "lever", "leverage"], ["set up", "refine", "own"]],
    d11: [["measure", "metric", "number", "kpi", "okr", "scoreboard"], ["uncomfortable", "embarrassing", "what's so", "honest"], ["track", "progress", "regress"]],
    d12: [["10x", "outsized", "big", "leverage"], ["carve out", "time", "beyond", "machine"], ["project", "growth", "efficiency"]],
    d13: [["un-personal", "not personal", "hanlon", "benefit of the doubt", "mistake"], ["acknowledge", "resolve", "by when", "5 day"], ["walk", "action", "committed"]]
  };

  var root = document.documentElement;
  var hasBackend = null; // unknown until first request

  /* ---------- storage ---------- */
  function load() { try { return JSON.parse(localStorage.getItem(STORE)) || {}; } catch (e) { return {}; } }
  function save(d) { try { localStorage.setItem(STORE, JSON.stringify(d)); } catch (e) {} }
  var state = load();

  function passedCount() {
    var c = 0;
    QUIZ.forEach(function (q) { if (state[q.id] && state[q.id].passed) c++; });
    return c;
  }

  /* ---------- AI grading (with offline fallback) ---------- */
  function gradeOffline(id, answer) {
    var words = answer.trim().split(/\s+/).filter(Boolean).length;
    var groups = KEYS[id] || [];
    var a = answer.toLowerCase();
    var hits = 0;
    groups.forEach(function (g) { if (g.some(function (k) { return a.indexOf(k) !== -1; })) hits++; });
    var score = 3 + 2 * Math.min(hits, 3) + (words >= 30 ? 2 : words >= 15 ? 1 : 0);
    if (words < 6) score = Math.min(score, 3);
    score = Math.max(1, Math.min(10, score));
    var fb = score >= PASS
      ? "Offline check: your answer touches the key ideas of this distinction. (Connect the AI evaluator via serve.py for a real assessment.)"
      : "Offline check: try naming the distinction's core move and a concrete, situation-specific action. (Real grading runs through serve.py.)";
    return Promise.resolve({ score: score, feedback: fb, offline: true });
  }

  function grade(id, answer) {
    // If we already learned the backend is absent, skip the network hop.
    if (hasBackend === false) return gradeOffline(id, answer);
    return fetch("/api/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: id, answer: answer })
    }).then(function (r) {
      if (!r.ok) throw new Error("bad status " + r.status);
      return r.json();
    }).then(function (data) {
      hasBackend = true;
      if (typeof data.score !== "number") throw new Error("bad payload");
      return { score: Math.max(0, Math.min(10, Math.round(data.score))), feedback: data.feedback || "", offline: false };
    }).catch(function () {
      hasBackend = false;
      return gradeOffline(id, answer);
    });
  }

  /* ---------- build a quiz block ---------- */
  function buildQuiz(item) {
    var saved = state[item.id] || {};
    var el = document.createElement("div");
    el.className = "quiz" + (saved.passed ? " is-passed" : "");
    el.id = "quiz-" + item.id;
    el.innerHTML =
      '<div class="quiz__head">' +
        '<span class="quiz__tag mono"><span class="quiz__dot"></span>APPLY IT · ' + item.n + '</span>' +
        '<span class="quiz__state mono" data-state></span>' +
      '</div>' +
      '<p class="quiz__q">' + item.q + '</p>' +
      '<textarea class="quiz__input" rows="3" maxlength="1500" placeholder="Describe how you would apply this distinction to the situation…"></textarea>' +
      '<div class="quiz__actions">' +
        '<button class="quiz__submit" type="button">Submit for evaluation</button>' +
        '<span class="quiz__score mono" data-score></span>' +
      '</div>' +
      '<div class="quiz__feedback" data-feedback></div>';

    var input = el.querySelector(".quiz__input");
    var submit = el.querySelector(".quiz__submit");
    var scoreEl = el.querySelector("[data-score]");
    var stateEl = el.querySelector("[data-state]");
    var fbEl = el.querySelector("[data-feedback]");

    function render(score, feedback, passed, offline) {
      el.classList.toggle("is-passed", !!passed);
      el.classList.toggle("is-failed", score != null && !passed);
      if (score != null) {
        scoreEl.textContent = score + " / 10";
        stateEl.textContent = passed ? "PASSED ✓" : "TRY AGAIN";
        stateEl.className = "quiz__state mono " + (passed ? "is-pass" : "is-fail");
      }
      if (feedback) {
        fbEl.innerHTML = (offline ? '<span class="quiz__offline mono">OFFLINE</span> ' : "") + feedback;
        fbEl.classList.add("is-shown");
      }
    }

    if (saved.answer) input.value = saved.answer;
    if (typeof saved.score === "number") render(saved.score, saved.feedback, saved.passed, saved.offline);

    submit.addEventListener("click", function () {
      var answer = input.value.trim();
      if (answer.length < 3) { input.focus(); return; }
      submit.disabled = true;
      submit.textContent = "Evaluating…";
      el.classList.add("is-loading");
      grade(item.id, answer).then(function (res) {
        var passed = res.score >= PASS;
        state[item.id] = { score: res.score, feedback: res.feedback, passed: passed, answer: answer, offline: res.offline };
        save(state);
        render(res.score, res.feedback, passed, res.offline);
        submit.textContent = passed ? "Re-submit" : "Try again";
        submit.disabled = false;
        el.classList.remove("is-loading");
        updateCert(passed && passedCount() === TOTAL);
      });
    });

    return el;
  }

  /* ---------- inject quizzes after each marker ---------- */
  function injectQuizzes() {
    QUIZ.forEach(function (item) {
      var marker = document.getElementById(item.id);
      if (!marker) return;
      var main = marker.querySelector(".marker__main") || marker;
      main.appendChild(buildQuiz(item));
    });
  }

  /* =================================================================
     CERTIFICATE
     ================================================================= */
  var certEls = {};
  var justUnlocked = false;

  function setupCert() {
    certEls.count = document.querySelector("[data-cert-count]");
    certEls.fill = document.querySelector("[data-cert-fill]");
    certEls.dots = document.querySelector("[data-cert-dots]");
    certEls.bar = document.querySelector(".cert__bar");
    certEls.name = document.getElementById("cert-name");
    certEls.btn = document.querySelector("[data-cert-download]");
    certEls.lock = document.querySelector("[data-cert-lock]");
    certEls.start = document.querySelector("[data-cert-start]");
    certEls.startLabel = document.querySelector("[data-cert-start-label]");
    if (!certEls.dots) return;

    QUIZ.forEach(function (item) {
      var li = document.createElement("li");
      li.className = "cert__dot";
      li.dataset.dot = item.id;
      li.title = item.title;
      li.textContent = item.n;
      certEls.dots.appendChild(li);
    });

    if (certEls.name) {
      try { certEls.name.value = localStorage.getItem("pc_cert_name") || ""; } catch (e) {}
      certEls.name.addEventListener("input", function () {
        try { localStorage.setItem("pc_cert_name", certEls.name.value); } catch (e) {}
        refreshButton();
      });
    }
    if (certEls.btn) certEls.btn.addEventListener("click", onDownload);
    if (certEls.start) certEls.start.addEventListener("click", onStart);
    updateCert(false);
  }

  // jump to the first not-yet-passed "Apply it" question (the quiz that gates the certificate)
  function onStart() {
    var target = null;
    for (var i = 0; i < QUIZ.length; i++) {
      if (!(state[QUIZ[i].id] && state[QUIZ[i].id].passed)) { target = document.getElementById("quiz-" + QUIZ[i].id); break; }
    }
    if (!target) target = document.getElementById("quiz-" + QUIZ[0].id);
    if (!target) return;
    if (window.lenis && window.lenis.scrollTo) window.lenis.scrollTo(target, { offset: -90, duration: 1.2 });
    else target.scrollIntoView({ behavior: "smooth", block: "center" });
    var input = target.querySelector(".quiz__input");
    if (input) setTimeout(function () { try { input.focus({ preventScroll: true }); } catch (e) {} }, 750);
  }

  function refreshButton() {
    if (!certEls.btn) return;
    var unlocked = passedCount() === TOTAL;
    var named = certEls.name && certEls.name.value.trim().length >= 2;
    certEls.btn.disabled = !(unlocked && named);
  }

  function updateCert(fireConfetti) {
    if (!certEls.dots) return;
    var done = passedCount();
    if (certEls.count) certEls.count.textContent = String(done);
    if (certEls.fill) certEls.fill.style.width = (done / TOTAL * 100) + "%";
    if (certEls.bar) certEls.bar.setAttribute("aria-valuenow", String(done));
    QUIZ.forEach(function (item) {
      var dot = certEls.dots.querySelector('[data-dot="' + item.id + '"]');
      if (dot) dot.classList.toggle("is-done", !!(state[item.id] && state[item.id].passed));
    });
    var unlocked = done === TOTAL;
    document.getElementById("cert").classList.toggle("is-unlocked", unlocked);
    if (certEls.lock) {
      certEls.lock.innerHTML = unlocked
        ? "🎉 Unlocked! Enter your name and download your certificate."
        : "🔒 Locked — pass all 13 application checks (8/10+) to unlock your certificate.";
    }
    refreshButton();
    if (certEls.startLabel) {
      certEls.startLabel.textContent = done === 0 ? "Take the challenge"
        : done >= TOTAL ? "Review your answers"
        : "Continue — " + (TOTAL - done) + " to go";
    }

    if (unlocked && fireConfetti && !justUnlocked) {
      justUnlocked = true;
      celebrate(true);
    }
  }

  /* ---------- confetti ---------- */
  function celebrate(big) {
    if (typeof window.confetti !== "function") return;
    var colors = ["#9D6BFF", "#B99BFF", "#7A3FE0", "#F3ECFB", "#ffffff"];
    window.confetti({ particleCount: big ? 160 : 120, spread: 95, startVelocity: 48, origin: { y: 0.62 }, colors: colors, scalar: 1.1 });
    var end = Date.now() + (big ? 1500 : 900);
    (function frame() {
      window.confetti({ particleCount: 5, angle: 60, spread: 62, origin: { x: 0, y: 0.7 }, colors: colors });
      window.confetti({ particleCount: 5, angle: 120, spread: 62, origin: { x: 1, y: 0.7 }, colors: colors });
      if (Date.now() < end) requestAnimationFrame(frame);
    })();
  }

  /* ---------- draw + download the certificate ---------- */
  function onDownload() {
    if (certEls.btn.disabled) return;
    var name = (certEls.name.value || "").trim().slice(0, 42) || "A High Performer";
    celebrate(true);
    drawCertificate(name).then(function (canvas) {
      canvas.toBlob(function (blob) {
        if (!blob) return;
        var url = URL.createObjectURL(blob);
        var a = document.createElement("a");
        a.href = url;
        a.download = "Performance-Culture-Certificate-" + name.replace(/[^a-z0-9]+/gi, "-") + ".png";
        document.body.appendChild(a); a.click(); a.remove();
        setTimeout(function () { URL.revokeObjectURL(url); }, 4000);
      }, "image/png");
    });
  }

  function drawCertificate(name) {
    var W = 1200, H = 850, S = 2; // render at 2x
    var c = document.createElement("canvas");
    c.width = W * S; c.height = H * S;
    var x = c.getContext("2d");
    x.scale(S, S);

    function rgx(c1, c2, vert) {
      var g = x.createLinearGradient(0, 0, vert ? 0 : W, vert ? H : 0);
      g.addColorStop(0, c1); g.addColorStop(1, c2); return g;
    }

    var fonts = document.fonts ? document.fonts.ready : Promise.resolve();
    return fonts.then(function () {
      // background
      x.fillStyle = "#F6F1FC"; x.fillRect(0, 0, W, H);
      x.fillStyle = rgx("#F3ECFB", "#FBF8FF", true); x.fillRect(0, 0, W, H);
      // soft violet glow top
      var rg = x.createRadialGradient(W / 2, 120, 40, W / 2, 120, 520);
      rg.addColorStop(0, "rgba(157,107,255,0.18)"); rg.addColorStop(1, "rgba(157,107,255,0)");
      x.fillStyle = rg; x.fillRect(0, 0, W, H);

      // frames
      x.strokeStyle = "#7A3FE0"; x.lineWidth = 2; x.strokeRect(28, 28, W - 56, H - 56);
      x.strokeStyle = "rgba(122,63,224,0.35)"; x.lineWidth = 1; x.strokeRect(38, 38, W - 76, H - 76);

      var cx = W / 2;
      x.textAlign = "center";

      // diamond mark
      x.save(); x.translate(cx, 96); x.rotate(Math.PI / 4);
      x.fillStyle = "#9D6BFF"; x.fillRect(-11, -11, 22, 22); x.restore();

      // eyebrow
      x.fillStyle = "#7A3FE0";
      x.font = "600 15px 'JetBrains Mono', monospace";
      x.fillText("P E R F O R M A N C E   C U L T U R E", cx, 150);
      x.fillStyle = "#8B83A2";
      x.font = "500 13px 'JetBrains Mono', monospace";
      x.fillText("CERTIFICATE OF MASTERY", cx, 178);

      // name
      x.fillStyle = "#1B1235";
      x.font = "600 66px 'Space Grotesk', sans-serif";
      x.fillText(name, cx, 286);

      // subline
      x.fillStyle = "#4a3d63";
      x.font = "400 19px 'Inter', sans-serif";
      x.fillText("has uncovered all thirteen distinctions and entered", cx, 330);
      x.fillText("the World of Performance.", cx, 358);

      // divider
      x.strokeStyle = "rgba(122,63,224,0.4)"; x.lineWidth = 1;
      x.beginPath(); x.moveTo(cx - 90, 396); x.lineTo(cx + 90, 396); x.stroke();

      // credo quote (wrapped)
      x.fillStyle = "#2c2046";
      x.font = "500 27px 'Space Grotesk', sans-serif";
      var credo = "“I deliver Complete Work, own the outcome, and turn every breakdown into a breakthrough.”";
      wrap(x, credo, cx, 448, 880, 38);

      // attribution with name
      x.fillStyle = "#7A3FE0";
      x.font = "500 20px 'Space Grotesk', sans-serif";
      x.fillText("— " + name, cx, 560);

      // seal
      x.save();
      x.translate(cx, 660);
      x.strokeStyle = "#9D6BFF"; x.lineWidth = 2;
      x.beginPath(); x.arc(0, 0, 50, 0, Math.PI * 2); x.stroke();
      x.strokeStyle = "rgba(157,107,255,0.4)";
      x.beginPath(); x.arc(0, 0, 42, 0, Math.PI * 2); x.stroke();
      x.fillStyle = "#7A3FE0"; x.textAlign = "center";
      x.font = "600 30px 'Space Grotesk', sans-serif"; x.fillText("13", 0, -2);
      x.font = "500 12px 'JetBrains Mono', monospace"; x.fillText("OF 13", 0, 22);
      x.restore();

      // footer row
      var d = new Date();
      var date = d.toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" });
      x.fillStyle = "#8B83A2";
      x.font = "500 13px 'JetBrains Mono', monospace";
      x.textAlign = "left"; x.fillText("ISSUED  " + date.toUpperCase(), 80, H - 70);
      x.textAlign = "right"; x.fillText("PERFORMANCE  CULTURE  ·  FIELD  GUIDE", W - 80, H - 70);

      return c;
    });
  }

  function wrap(x, text, cx, y, maxW, lh) {
    var words = text.split(" "), line = "", lines = [];
    for (var i = 0; i < words.length; i++) {
      var test = line + words[i] + " ";
      if (x.measureText(test).width > maxW && line) { lines.push(line.trim()); line = words[i] + " "; }
      else line = test;
    }
    lines.push(line.trim());
    for (var j = 0; j < lines.length; j++) x.fillText(lines[j], cx, y + j * lh);
  }

  /* ---------- go ---------- */
  window.__pcDrawCertificate = drawCertificate; // debug/QA handle
  function init() {
    injectQuizzes();
    setupCert();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
