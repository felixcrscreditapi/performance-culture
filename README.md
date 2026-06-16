# Performance Culture — Field Guide

An interactive, single-page (One-Pager) story-website on *Performance Culture*, built from the
document `CRS's Performance Culture`. Premium dark design in the spirit of
[terminal-industries.com](https://terminal-industries.com), coloured after
[crscreditapi.com](https://crscreditapi.com): deep violet-black canvas, a CRS **electric-violet**
signal colour (`#9D6BFF`), grotesk-display + monospace type.

## The story (roter Faden)

> **Welcome to the World of Performance.**

1. **Premise** — hero with a violet vista and a text-decode effect.
2. **The Language** — jargon & distinctions as a “treasure map”.
3. **Interlude** — a cinematic image band as a breather.
4. **The Field** — all 13 distinctions in 4 “movements”, each opened by a full-bleed image band.
   **Under every distinction is an interactive “Apply it” box.**
5. **Closing** — light lavender panel with the gated **certificate** + a link to the source PDF.

## Interactive certification

- **Apply-it quizzes** — one **situation question** per distinction (apply it to a real scenario, not
  trivia). The learner answers in free text.
- **AI grading** — the answer is scored **0–10 with short feedback** by Claude
  (`POST /api/evaluate`, served by `serve.py`), graded against the distinction's text on the page.
- **Gated certificate** — score **8/10 or higher on all 13** to unlock a **personalised certificate**
  (name + a credo quote ending with the recipient's name), rendered to a downloadable PNG.
- **Confetti** — a celebratory burst (canvas-confetti) on unlock and on download.
- Progress is saved in `localStorage`, so it persists across visits.

### Enabling real AI grading

The grader calls the Claude Messages API. Set your key and run the server:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."      # required for real grading
# optional: faster / cheaper grading model
export ANTHROPIC_MODEL="claude-haiku-4-5"  # default: claude-opus-4-8
python3 serve.py                            # → http://127.0.0.1:4544
```

> **Without a key** (or when `index.html` is opened directly via `file://`), the quizzes still work
> using a local **offline heuristic** — clearly badged `OFFLINE` — so the flow never breaks. Real,
> nuanced grading needs the server + key. Structured-output grading requires Opus 4.8, Sonnet 4.6 or
> Haiku 4.5. The key is read from the environment and never leaves your machine.

## Start

```bash
python3 serve.py        # static site + AI grader → http://127.0.0.1:4544
# or, static only (no AI grading):
python3 -m http.server 8080
# or just open index.html (offline grading fallback)
```

## Files

```
index.html                     Structure + the full document content
assets/css/styles.css          Design system (tokens, components, responsive)
assets/js/main.js              Lenis smooth-scroll, GSAP parallax/reveals, hero canvas
assets/js/quiz.js              Apply-it quizzes, progress, gated certificate, confetti
assets/img/*.svg               Cinematic “Bildwelten” (hero, m1–m4, interlude)
scripts/generate-imagery.py    Generator for the SVG imagery (stdlib only)
serve.py                       Static server + /api/evaluate AI grader (stdlib urllib)
CRS's Performance Culture …pdf Source document (linked from “Complete version”)
```

## Scroll & motion

Evolving aurora background, parallax on hero/interlude/movement images, full-bleed image chapters,
a marquee ticker, a mitlaufende fixed index rail, masked line reveals, text-decode hero, custom cursor.
Respects `prefers-reduced-motion`; append `?static=1` to the URL for a calm, animation-free render.

Responsive for desktop, tablet and mobile. The complete original document text is included.
