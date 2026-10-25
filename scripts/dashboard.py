#!/usr/bin/env python3
"""HQ dashboard: live local server or static snapshot of the company's state.

  python3 scripts/dashboard.py                 # live map at http://127.0.0.1:8765 (polls every 2 s)
  python3 scripts/dashboard.py --port 9000 --open
  python3 scripts/dashboard.py --snapshot out.html   # self-contained page for the Artifact publish

Reads state/project.json, feature_list.json, security-findings.json, open-questions.md and the agent
activity log state/activity.jsonl (written by .claude/hooks/activity_log.py). Standard library only, so it
runs the same on the Mac and on the Windows PC. Binds to 127.0.0.1 only.
"""
import argparse
import json
import re
import sys
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "state"
TEMPLATE = ROOT / "company" / "templates" / "dashboard.html"
PLACEHOLDER = re.compile(r"/\*STATE\*/.*?/\*END\*/", re.S)
MAX_EVENTS = 300
STATUS_VI = {"not-started": "chưa bắt đầu", "in-progress": "đang làm", "blocked": "đang bị chặn",
             "done": "hoàn tất", "awaiting-po": "chờ PO"}


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def read_events():
    try:
        lines = (STATE / "activity.jsonl").read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    events = []
    for line in lines[-MAX_EVENTS:]:
        try:
            events.append(json.loads(line))
        except ValueError:
            continue
    return events


def collect(live):
    project = read_json(STATE / "project.json") or {}
    phase_match = re.match(r"\d+", str(project.get("phase") or "0"))
    gates = {}
    for key, value in (project.get("gates") or {}).items():
        gates[key.split("_")[0]] = value

    features = read_json(STATE / "feature_list.json") or {}
    items = features.get("features") or []
    findings = (read_json(STATE / "security-findings.json") or {}).get("findings") or []
    blocking = [f for f in findings if str(f.get("severity", "")).lower() in ("critical", "high")
                and f.get("status") not in ("verified", "accepted-risk")]
    try:
        questions = (STATE / "open-questions.md").read_text(encoding="utf-8").splitlines()
    except OSError:
        questions = []

    status = str(project.get("phase_status") or "")
    return {
        "generatedAt": time.time(),
        "live": live,
        "app": project.get("app_name"),
        "phase": min(int(phase_match.group()) if phase_match else 0, 9),
        "phaseStatus": STATUS_VI.get(status, status),
        "gates": gates,
        "squad": project.get("squad") or [],
        "openQuestions": sum(1 for line in questions if line.startswith("- [ ]")),
        "criticalFindings": len(blocking),
        "features": {"done": sum(1 for f in items if f.get("passes")), "total": len(items)} if items else None,
        "events": read_events(),
    }


def render(live):
    html = TEMPLATE.read_text(encoding="utf-8")
    payload = json.dumps(collect(live), ensure_ascii=False).replace("</", "<\\/")
    return PLACEHOLDER.sub(lambda _: payload, html, count=1)


class Handler(BaseHTTPRequestHandler):
    def _send(self, body, ctype):
        data = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):  # noqa: N802 - stdlib naming
        if self.path.startswith("/api/state"):
            self._send(json.dumps(collect(True), ensure_ascii=False), "application/json; charset=utf-8")
        elif self.path in ("/", "/index.html") or self.path.startswith("/?"):
            self._send(render(True), "text/html; charset=utf-8")
        else:
            self.send_error(404)

    def log_message(self, *args):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--open", action="store_true", help="open the map in the default browser")
    parser.add_argument("--snapshot", metavar="FILE", help="write a static snapshot page and exit")
    args = parser.parse_args()

    if args.snapshot:
        out = Path(args.snapshot)
        out.write_text(render(False), encoding="utf-8")
        print(f"Snapshot written: {out}")
        return

    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    url = f"http://127.0.0.1:{args.port}/"
    print(f"Trụ Sở Phần Mềm đang chạy tại {url}  (Ctrl+C để dừng)")
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã dừng.")
        sys.exit(0)


if __name__ == "__main__":
    main()
