#!/usr/bin/env python3
"""
Performance Culture — static server + AI quiz grader.

Serves the site AND exposes POST /api/evaluate, which grades a learner's
free-text answer (0–10 + short feedback) by calling the Claude Messages API.
Stdlib only — no pip installs required (uses urllib).

Run:   python3 serve.py            ->  http://127.0.0.1:4544
Env:   ANTHROPIC_API_KEY   (required for real AI grading; without it the
                            site falls back to an offline heuristic)
       ANTHROPIC_MODEL     (optional; default "claude-opus-4-8")
       PC_DIR / PC_PORT    (optional overrides)
"""
import json
import os
import re
import urllib.request
import urllib.error
import http.server
import socketserver

DIRECTORY = os.environ.get("PC_DIR", "/Users/felix/Desktop/Performance Culture V1 2.0")
PORT = int(os.environ.get("PC_PORT", "4544"))
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

os.chdir(DIRECTORY)

SYSTEM = (
    "You are an expert evaluator for a 'Performance Culture' learning experience. "
    "A learner is shown a real workplace SITUATION and asked to apply ONE specific "
    "distinction to it. You are given the distinction's definition (the rubric source), "
    "the situation question, and the learner's free-text answer.\n\n"
    "Score the answer 0-10 on how well it APPLIES the distinction to the situation:\n"
    "- 8-10: correctly identifies the distinction's core move AND gives a concrete, "
    "situation-specific way to apply it.\n"
    "- 5-7: partial understanding, vague/generic, or misses part of the idea.\n"
    "- 0-4: misunderstands or misapplies the distinction, or doesn't engage the situation.\n\n"
    "Judge substance and application, not grammar, length, or eloquence. Reward concrete, "
    "specific answers; do not reward buzzwords without application. Be encouraging but honest. "
    "Return an integer 'score' (0-10) and 'feedback' of at most two short, specific, "
    "actionable sentences."
)

SCHEMA = {
    "type": "object",
    "properties": {
        "score": {"type": "integer"},
        "feedback": {"type": "string"},
    },
    "required": ["score", "feedback"],
    "additionalProperties": False,
}

# Canonical distinction text (the grading rubric source) + the situation question.
DISTINCTIONS = {
    "d01": {"title": "Complete Work",
            "q": "A teammate says the new CSV-export feature is done because the code is merged and tests pass. Apply Complete Work: what is still missing, and what does 'done' actually require here?",
            "ctx": "Complete Work means a task finished as it was intended, from beginning to end - not merely built or technically done. For a feature, the real intention is to get it into the hands of a customer working as expected: documentation done, marketing informed, sales trained, rolled out to production with monitoring, and at least one customer successfully using it. 'Merged and tested locally' is a milestone, not Complete Work."},
    "d02": {"title": "Ownership",
            "q": "You own a data-migration task. In standup three people give three different status answers and nobody can say when it will finish. Apply Ownership.",
            "ctx": "Ownership means total command of a task from beginning to end - owning its full Burndown List - so you can give a concrete, concise answer (or get it with velocity) to any question about it. Diverting questions or feeling stuck signals you don't truly own it. Ownership does NOT mean doing everything yourself; it means leading peers and using company resources to drive the owned list to completion."},
    "d03": {"title": "Demonstrated By",
            "q": "The team's goal is to 'make onboarding world-class.' Apply Demonstrated By: name 2-3 concrete things you'd observe in reality if it were truly met.",
            "ctx": "A Demonstrated By tethers an ambiguous intention to the ground of reality by naming what you would concretely, observably see if the goal were truly met. Vague goals live in a 'thought-state' until pinned to specific, measurable, recognizable indicators in reality. The test: what would unambiguously demonstrate the intended outcome was delivered?"},
    "d04": {"title": "By When",
            "q": "A colleague says 'I'll get you the pricing analysis as soon as I can.' Apply By When: what's the problem and how should it be restated?",
            "ctx": "A communication without a By When is just chatter ('asap'). A clear By When ('by 5pm tomorrow') is a reliable commitment others can build on or follow up against. Organizations are held together by a network of reliable By Whens. Missing one is human; failing to communicate an updated, revised or revoked By When reliably reduces performance."},
    "d05": {"title": "The Burndown List",
            "q": "You're handed the ambiguous goal 'reduce customer churn' and only a sheet of paper. Apply The Burndown List: what goes on it and how does it get you moving?",
            "ctx": "The Burndown List is a sheet of paper listing the critical tasks to get from Point A (where we are) to Point B (where we intend to be). It is fundamental to accomplishing anything. Faced with an ambiguous goal you break it into concrete tasks (ideally with Intentions, Demonstrated Bys and By Whens), giving you ownership and a path to move."},
    "d06": {"title": "Qualification is the Enemy of Performance",
            "q": "You keep postponing a launch because you want another certification first and to 'be fully ready.' Apply this distinction.",
            "ctx": "Qualification is the enemy of performance: waiting to feel 'qualified' (another certification, more experience, one more sign-off) before acting is a hidden form of permission-seeking that caps performance. You become qualified by delivering Complete Work and owning outcomes, not by collecting permissions in advance. Choose action and ownership over credentials - without being reckless or skipping genuine skill-building."},
    "d07": {"title": "Communication - Intentional & Effective",
            "q": "You sent a detailed Slack message about a pricing change, got two thumbs-up, and a week later Sales acts as if they never heard. Apply Intentional & Effective Communication.",
            "ctx": "Intentional Communication states your intention and invites input rather than seeking approval ('I intend to..., the reason is..., I'll brief X and report back'). Effective Communication means the message LANDS as intended - sending or saying it is not enough; it must be heard and acknowledged, ideally re-created in the recipient's own words. Complete Communication closes the loop with a clear agreed next step, owner and By When."},
    "d08": {"title": "Alignment & Enrollment",
            "q": "You want to roll out a new code-review process but two senior engineers think it's a waste of time. Apply Alignment & Enrollment, including 'disagree and commit.'",
            "ctx": "Nothing happens without alignment and enrollment. Enrollment means communicating so others discover for themselves how a change benefits them, while acknowledging and dealing with their considerations, concerns and disagreements. Everyone need not reach the same conclusion, but concerns must be acknowledged and a clear commitment / next step made. 'Disagree and commit' promotes action over paralysis; using force often signals underdeveloped leadership."},
    "d09": {"title": "Symptoms vs. Systems",
            "q": "Every Monday someone manually fixes the same broken report for two hours and it's now 'just how we do it.' Apply Symptoms vs. Systems.",
            "ctx": "Symptoms have a gravitational pull - the reflex is to patch them (manual fixes, recurring workarounds) until the patch becomes standard procedure. Performance means recognizing when you're treating symptoms instead of the system causing them, stepping back to find root causes. Sometimes treating the symptom is right - but making that a conscious, communicated choice is the hallmark of good leadership."},
    "d10": {"title": "Mastering The Tools I Own",
            "q": "Your team is slow and everyone uses the core software at a beginner level with manual workarounds. Apply Mastering The Tools I Own.",
            "ctx": "Proper tooling is a force multiplier - like levers. Choosing, setting up and mastering your tools-of-the-craft has an outsized impact on your, your team's and peers' performance. Own your tools, master them, refine them - often you'll know them better than those who built them. The move when a team is slow with beginner-level tool use is to invest in mastery rather than pile on manual workarounds."},
    "d11": {"title": "What I Measure Grows",
            "q": "A team insists things are 'going well' but nobody can point to a number, and the one metric they could track looks embarrassing. Apply What I Measure Grows.",
            "ctx": "Performance only exists in the realm of measurement; there is no performance without measurement, and the scoreboard decides success or failure. Find the right metrics (OKRs/KPIs) that reflect hitting the mark, even when early numbers look terrible or uncomfortable ('telling on ourselves'). The leadership decision: commit to delivering extraordinary performance over 'looking good', and measure what's really so to improve together."},
    "d12": {"title": "10x Results",
            "q": "You spend all your time keeping the existing reporting machine running and have no time for anything else. Apply 10x Results.",
            "ctx": "Beyond running a well-oiled machine of consistent, predictable results, leaders must reliably carve out time for 10x Projects - self-discovered, self-driven efforts whose outcomes are inarguably 10x (10x revenue, 10x efficiency, 10x lower cost). There's no recipe for the projects, but there IS a recipe for creating the structure and time to ask 'What would deliver a 10x move in my area?' Outsized wins come from outsized commitments and efforts."},
    "d13": {"title": "Dealing with Breakdowns",
            "q": "A teammate missed a promised deadline and didn't tell you; your first instinct is that they don't respect your time. Apply Dealing with Breakdowns and Hanlon's Razor.",
            "ctx": "A breakdown is an opportunity for a breakthrough. Treat breakdowns as un-personal - people are not out to get you (Hanlon's Razor: don't attribute to malice what is explained by mistake). Breakdowns are just things in the way of what you want. Deal with them quickly; give peers the benefit of the doubt; focus on what you're both committed to; put a By When on the resolution; and ask: what actions, now, would resolve the breakdown?"},
}


def call_claude(distinction, answer):
    """Grade one answer. Returns dict {score, feedback} or raises."""
    user = (
        "DISTINCTION - " + distinction["title"] + "\n" + distinction["ctx"] +
        "\n\nSITUATION QUESTION:\n" + distinction["q"] +
        "\n\nLEARNER'S ANSWER:\n" + answer.strip()[:4000]
    )
    payload = {
        "model": MODEL,
        "max_tokens": 600,
        "system": SYSTEM,
        "messages": [{"role": "user", "content": user}],
        "output_config": {"format": {"type": "json_schema", "schema": SCHEMA}},
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    text = ""
    for block in data.get("content", []):
        if block.get("type") == "text":
            text = block.get("text", "")
            break
    try:
        parsed = json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}", text, re.S)
        parsed = json.loads(m.group(0)) if m else {}
    score = int(parsed.get("score", 0))
    score = max(0, min(10, score))
    feedback = str(parsed.get("feedback", "")).strip()
    return {"score": score, "feedback": feedback}


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def log_message(self, *args):
        pass

    def _json(self, code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.split("?")[0] == "/api/health":
            return self._json(200, {"ok": True, "model": MODEL, "has_key": bool(API_KEY)})
        return super().do_GET()

    def do_POST(self):
        if self.path.split("?")[0] != "/api/evaluate":
            return self._json(404, {"error": "not found"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            req = json.loads(self.rfile.read(length).decode("utf-8")) if length else {}
        except Exception:
            return self._json(400, {"error": "invalid JSON"})

        did = str(req.get("id", ""))
        answer = str(req.get("answer", "")).strip()
        distinction = DISTINCTIONS.get(did)
        if not distinction:
            return self._json(400, {"error": "unknown distinction id"})
        if len(answer) < 3:
            return self._json(400, {"error": "answer too short"})
        if not API_KEY:
            # No key configured -> tell the client so it can use its offline fallback.
            return self._json(503, {"error": "ANTHROPIC_API_KEY not set", "offline": True})

        try:
            result = call_claude(distinction, answer)
            return self._json(200, result)
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:500]
            return self._json(502, {"error": "claude api error", "status": e.code, "detail": detail})
        except urllib.error.URLError as e:
            return self._json(504, {"error": "network error", "detail": str(e.reason)})
        except Exception as e:
            return self._json(500, {"error": "grading failed", "detail": str(e)})


if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    print("Performance Culture -> http://127.0.0.1:%d  (model=%s, ai_grading=%s)"
          % (PORT, MODEL, "on" if API_KEY else "OFF - offline fallback"))
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        httpd.serve_forever()
