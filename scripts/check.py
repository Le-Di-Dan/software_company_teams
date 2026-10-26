"""Run a build/test/lint command once, keep its full log, print only a short summary (called by check.sh).

Usage: bash scripts/check.sh <name> [-C dir] [--fresh] [--keep <feature-id>] [--timeout sec] -- <command>
       bash scripts/check.sh --clean | --prune

- The whole output (ANSI colors and \\r progress redraws stripped) goes to state/runs/<name>/<stamp>-pass|fail.log.
  Only the summary reaches the agent's context: one line on success; on failure each failing test or error
  with the log line range to Read, plus a command that re-runs only the failures.
- Same command, same code (HEAD + diff + untracked files, state/ and docs/ excluded) as the last run: the
  last result is returned without running again. --fresh forces a run; e2e/integration runs and builds
  (the artifact is the point) never cache.
- Cleanup: a pass keeps only its own log and deletes the check's failed logs and its `<name>~*` re-run
  checks; prune() also caps age, count and total size (state/project.json -> cost_policy: runs_max_mb,
  runs_max_age_days, runs_keep_failed, runs_max_log_mb). state/runs/ is gitignored.
Exit code is the command's (a cached result returns the cached code).
"""
import hashlib
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "state"
RUNS = STATE / "runs"
INDEX = RUNS / "index.jsonl"
DEFAULTS = {"runs_max_mb": 200, "runs_max_age_days": 3, "runs_keep_failed": 3, "runs_max_log_mb": 20}
MAX_DIRS = 30
INDEX_KEEP = 200
SHOWN = 15
# Environment-dependent runs, and builds whose point is the artifact (a cached pass would skip producing it).
NO_CACHE = re.compile(r"maestro|integration|e2e|connectedAndroidTest|emulators:exec|patrol|detox|smoke"
                      r"|\bbuild\b|\bassemble|\bbundle|\barchive|-exportArchive|fastlane", re.I)
ANSI = re.compile(rb"\x1b\[[0-9;?]*[ -/]*[@-~]|\x1b\][^\x07]*\x07|\x1b[()][A-Z0-9]")


def policy():
    try:
        project = json.loads((STATE / "project.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        project = {}
    return {**DEFAULTS, **{k: v for k, v in (project.get("cost_policy") or {}).items() if k in DEFAULTS}}


def rel(path):
    try:
        return Path(path).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return Path(path).as_posix()


def git(*args, repo=ROOT):
    try:
        return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, timeout=60).stdout
    except (OSError, subprocess.SubprocessError):
        return b""


def fingerprint(cwd):
    """Hash of the code as it is now in the git repo the command runs in (the workspace, or the customer's
    client/ clone in a takeover, which the workspace ignores); None outside a git repo."""
    top = git("rev-parse", "--show-toplevel", repo=cwd).decode("utf-8", "replace").strip()
    if not top:
        return None
    repo = Path(top).resolve()
    scope = ["--", "."] + ([":(exclude)state", ":(exclude)docs"] if repo == ROOT else [])
    h = hashlib.sha256(git("rev-parse", "HEAD", repo=repo) + git("diff", "HEAD", "--binary", *scope, repo=repo))
    for name in sorted(git("ls-files", "--others", "--exclude-standard", "-z", *scope, repo=repo).split(b"\0")):
        p = repo / name.decode("utf-8", "replace")
        if not name or not p.is_file():
            continue
        st = p.stat()
        h.update(name + (p.read_bytes() if st.st_size <= 2 << 20 else f"{st.st_size}:{st.st_mtime}".encode()))
    return h.hexdigest()[:16]


# ---------- index ----------

def read_index():
    try:
        lines = INDEX.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    out = []
    for line in lines:
        try:
            out.append(json.loads(line))
        except ValueError:
            pass
    return out


def append_index(entry):
    RUNS.mkdir(parents=True, exist_ok=True)
    with open(INDEX, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def compact_index():
    """Keep the newest entry per (name, cwd, cmd), at most INDEX_KEEP entries."""
    entries = read_index()
    newest = {}
    for e in entries:
        newest[(e.get("name"), e.get("cwd"), e.get("cmd"))] = e
    kept = sorted(newest.values(), key=lambda e: e.get("ts", 0))[-INDEX_KEEP:]
    if len(kept) == len(entries):
        return
    tmp = INDEX.with_suffix(".tmp")
    tmp.write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in kept), encoding="utf-8")
    os.replace(tmp, INDEX)


# ---------- cleanup ----------

def remove(path):
    try:
        shutil.rmtree(path) if path.is_dir() else path.unlink()
    except OSError:
        pass


def logs_of(d):
    return sorted((p for p in d.glob("*.log")), key=lambda p: p.stat().st_mtime, reverse=True)


def after_pass(name, log):
    """A pass resolves the check: drop its older logs and its re-run sub-checks."""
    for p in log.parent.glob("*.log"):
        if p != log:
            remove(p)
    if "~" not in name:
        for d in RUNS.glob(f"{glob_escape(name)}~*"):
            if not busy(d):
                remove(d)


def busy(d):
    """A run is still writing into this check directory."""
    return any(d.glob("*.partial"))


def glob_escape(s):
    return re.sub(r"([*?\[])", r"[\1]", s)


def prune(pol=None):
    """Age, count and size caps for state/runs/ (run on every check and at session start)."""
    if not RUNS.is_dir():
        return
    pol = pol or policy()
    now = time.time()
    max_age = float(pol["runs_max_age_days"]) * 86400
    dirs = [d for d in RUNS.iterdir() if d.is_dir()]
    for d in dirs:
        for p in d.glob("*.partial"):
            if now - p.stat().st_mtime > 7200:  # writer died: a live run touches its log continuously
                remove(p)
        fails = [p for p in logs_of(d) if p.name.endswith("-fail.log")]
        passes = [p for p in logs_of(d) if p.name.endswith("-pass.log")]
        for i, p in enumerate(fails):
            if i >= int(pol["runs_keep_failed"]) or now - p.stat().st_mtime > max_age:
                remove(p)
        for p in passes[1:]:
            remove(p)
    dirs = sorted((d for d in RUNS.iterdir() if d.is_dir()), key=lambda d: d.stat().st_mtime, reverse=True)
    for d in dirs[MAX_DIRS:]:
        if not busy(d):
            remove(d)
    files = sorted((p for p in RUNS.glob("*/*.log") if p.is_file()), key=lambda p: p.stat().st_mtime)
    total, cap = sum(p.stat().st_size for p in files), float(pol["runs_max_mb"]) * (1 << 20)
    for p in files:
        if total <= cap:
            break
        total -= p.stat().st_size
        remove(p)
    for d in RUNS.iterdir():
        if d.is_dir() and not any(d.iterdir()):
            remove(d)
    compact_index()


def clean():
    remove(RUNS)
    print("check: removed state/runs/")


# ---------- running ----------

def clean_line(raw):
    """Strip ANSI and keep only the last redraw of \\r progress lines."""
    raw = ANSI.sub(b"", raw.rstrip(b"\r\n"))
    return raw.rsplit(b"\r", 1)[-1] + b"\n"


def kill_tree(proc):
    if os.name == "nt":
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)], capture_output=True)
    else:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except OSError:
            proc.kill()


def run(cmd, cwd, log, timeout):
    """Stream the command's output into `log`; return (exit code, timed_out)."""
    env = {**os.environ, "NO_COLOR": "1", "FORCE_COLOR": "0", "TERM": "dumb"}
    bash = os.environ.get("CHECK_BASH") or shutil.which("bash") or "bash"
    proc = subprocess.Popen([bash, "-c", cmd], cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, start_new_session=os.name != "nt")
    expired = []
    timer = threading.Timer(timeout, lambda: (expired.append(1), kill_tree(proc))) if timeout else None
    if timer:
        timer.start()

    def pump(fh):
        try:
            for raw in proc.stdout:
                fh.write(clean_line(raw))
        except (OSError, ValueError):
            pass

    with open(log, "wb") as fh:
        reader = threading.Thread(target=pump, args=(fh,), daemon=True)
        reader.start()
        code = proc.wait()
        reader.join(10)  # a daemon the command started (adb, gradle) may keep the pipe open: don't wait for it
        if reader.is_alive():
            proc.stdout.close()
            reader.join(2)
    if timer:
        timer.cancel()
    return (124 if expired else code), bool(expired)


def cap_log(log, max_mb):
    """Very long logs keep their first 1 MB and last part (failures are almost always at the end)."""
    size, cap = log.stat().st_size, int(float(max_mb) * (1 << 20))
    if size <= cap:
        return
    head_n, tail_n = 1 << 20, cap - (1 << 20)
    with open(log, "rb") as fh:
        head = fh.read(head_n)
        fh.seek(size - tail_n)
        tail = fh.read()
    head = head[:head.rfind(b"\n") + 1]
    tail = tail[tail.find(b"\n") + 1:]
    log.write_bytes(head + f"... [check.sh: {(size - len(head) - len(tail)) / (1 << 20):.1f} MB cut from the middle]\n".encode()
                    + tail)


# ---------- reading the log ----------

def block_end(lines, start, stop_re, limit=60):
    """Last line (1-based) of the block that starts at index `start`."""
    for j in range(start + 1, min(len(lines), start + limit)):
        if stop_re.search(lines[j]):
            return j
    return min(len(lines), start + limit)


FLUTTER_PROGRESS = re.compile(r"^\d+:\d+ \+\d+")
FLUTTER_DONE = re.compile(r"^\d+:\d+ \+(\d+)(?: ~(\d+))?(?: -(\d+))?: (?:All tests passed!|Some tests failed\.)")
FLUTTER_FAIL = re.compile(r"^\d+:\d+ \+\d+(?: ~\d+)? -\d+: (?:loading (\S+?\.dart)|(?:(\S+?\.dart): )?(.+?)) \[E\]$")
FLUTTER_LISTED = re.compile(r"^\s+(\S+?\.dart): (.+)$")  # "Failing tests:" section at the end
JEST_FILE = re.compile(r"^\s*FAIL\s+(\S+\.(?:[cm]?[jt]sx?))\s*$")
JEST_CASE = re.compile(r"^\s+● (.+)$")
JEST_STOP = re.compile(r"^\s+● |^Test Suites:|^\s*(?:PASS|FAIL)\s+\S")
VITEST_FAIL = re.compile(r"^\s*FAIL\s+(\S+\.(?:[cm]?[jt]sx?))\s+>\s+(.+?)\s*$")
VITEST_STOP = re.compile(r"^\s*FAIL\s+\S+\s+>|^\s*⎯{3,}|^\s*Test Files\s")
PYTEST_HEAD = re.compile(r"^_{3,} (.+?) _{3,}$")
PYTEST_STOP = re.compile(r"^_{3,} .+ _{3,}$|^={3,} ")
PYTEST_SUMMARY = re.compile(r"^(?:FAILED|ERROR) (\S+::\S+|\S+\.py)")
GO_FAIL = re.compile(r"^\s*--- FAIL: (\S+)")
GO_STOP = re.compile(r"^\s*--- |^=== RUN|^(?:FAIL|ok)\s")
GO_PKG = re.compile(r"^FAIL\s+(\S+)\s+[\d.]+s")
GRADLE_TEST = re.compile(r"^(\S+) > (.+) FAILED$")
GRADLE_TASK = re.compile(r"^> Task (\S+) FAILED$")
GRADLE_WRONG = re.compile(r"^\* What went wrong:")
GRADLE_STOP = re.compile(r"^\* Try:|^\S+ > .+ FAILED$|^BUILD ")
XCTEST_FAIL = re.compile(r"Test Case '-\[(\S+) (\S+)\]' failed")
ANALYZE = re.compile(r"^\s*(error|warning|info) (?:•|-) (?:(.+?) • )?(\S+?):(\d+):(\d+)(?: • | - )(.+)$")
TSC = re.compile(r"^(\S.*?)(?:\((\d+),\d+\):|:(\d+):\d+ -) error (TS\d+): (.*)$")
ESLINT_FILE = re.compile(r"^(?:[A-Za-z]:)?[\\/]?\S+\.(?:[cm]?[jt]sx?|vue)$")
ESLINT_ERR = re.compile(r"^\s+(\d+):\d+\s+error\s+(.*?)(?:\s{2,}(\S+))?$")
KOTLIN_ERR = re.compile(r"^e: (?:file://)?(\S+?\.kts?):(\d+):\d+ (.*)$")
FILE_ERR = re.compile(r"^(?:e: (?:file://)?)?(\S+?\.\w+):(\d+):(?:\d+:?)?\s+(?:(?:fatal )?error:?|Error:|[A-Z]+\d+|undefined:|cannot|expected)\s*(.*)$")
GENERIC = re.compile(r"\b(?:error|fail(?:ed|ure)?|exception|traceback|panic|fatal)\b", re.I)
STATS = [
    re.compile(r"^Tests:\s+(.*total)"),                                     # jest
    re.compile(r"^\s*Tests\s+(.*\(\d+\))"),                                 # vitest
    re.compile(r"^=*\s*(\d+ (?:failed|passed|errors?)\b.*?) in [\d.]+s"),    # pytest
    re.compile(r"(\d+ tests? completed, \d+ failed.*)"),                    # gradle
    re.compile(r"(Executed \d+ tests?, with \d+ failures?)"),               # xcodebuild
    re.compile(r"^(\d+ issues? found)"),                                    # dart / flutter analyze
    re.compile(r"^(Found \d+ errors?.*)"),                                  # tsc
    re.compile(r"(\d+ problems? \(.*\))"),                                  # eslint
]


def analyse(lines, cmd, cwd):
    """Failures [{label, start, end}], re-run hint parts and a stats string, from the cleaned log."""
    fails, flutter, jest, pytest_ids, go_tests, go_pkgs, gradle, xctests = [], [], [], [], [], [], [], []
    seen = set()

    def add(label, start, end):
        if label not in seen:
            seen.add(label)
            fails.append({"label": label, "start": start + 1, "end": max(start + 1, end)})

    jest_file = None
    for i, line in enumerate(lines):
        if m := FLUTTER_FAIL.match(line):
            loading, file, test = m.groups()
            flutter.append([loading or file, test])
            add(f"{file}: {test}" if file else test or f"{loading}: failed to load", i,
                block_end(lines, i, FLUTTER_PROGRESS))
        elif m := VITEST_FAIL.match(line):
            jest.append((m.group(1), m.group(2).split(" > ")[-1]))
            add(f"{m.group(1)} > {m.group(2)}", i, block_end(lines, i, VITEST_STOP))
        elif m := JEST_FILE.match(line):
            jest_file = m.group(1)
        elif (m := JEST_CASE.match(line)) and jest_file:
            jest.append((jest_file, m.group(1).split(" › ")[-1]))
            add(f"{jest_file}: {m.group(1)}", i, block_end(lines, i, JEST_STOP))
        elif m := PYTEST_HEAD.match(line):
            add(m.group(1), i, block_end(lines, i, PYTEST_STOP, 120))
        elif m := PYTEST_SUMMARY.match(line):
            pytest_ids.append(m.group(1))
        elif m := GO_FAIL.match(line):
            go_tests.append(m.group(1).split("/")[0])
            add(f"go {m.group(1)}", i, block_end(lines, i, GO_STOP))
        elif m := GO_PKG.match(line):
            go_pkgs.append(m.group(1))
        elif m := GRADLE_TEST.match(line):
            gradle.append(f"{m.group(1)}.{m.group(2)}")
            add(f"{m.group(1)} > {m.group(2)}", i, block_end(lines, i, GRADLE_STOP))
        elif GRADLE_WRONG.match(line):
            add(f"gradle: {lines[i + 1].strip() if i + 1 < len(lines) else 'build failed'}", i,
                block_end(lines, i, GRADLE_STOP))
        elif m := XCTEST_FAIL.search(line):
            xctests.append(f"{m.group(1).replace('.', '/')}/{m.group(2)}")
            add(f"{m.group(1)} {m.group(2)}", max(0, i - 20), i + 1)
        elif m := TSC.match(line):
            add(f"{m.group(1)}:{m.group(2) or m.group(3)} {m.group(4)} {m.group(5)[:100]}", i, i + 1)
        elif m := ANALYZE.match(line):  # infos count too: `flutter analyze` exits 1 on them by default
            add(f"{m.group(1)} {m.group(3)}:{m.group(4)} {(m.group(2) or m.group(6))[:100]}", i, i + 1)
        elif ESLINT_FILE.match(line):
            j = i + 1
            while j < len(lines) and lines[j].startswith(" "):
                if e := ESLINT_ERR.match(lines[j]):
                    add(f"{line.strip()}:{e.group(1)} {e.group(3) or ''} {e.group(2)[:80]}".strip(), j, j + 1)
                j += 1
        elif m := KOTLIN_ERR.match(line):
            path = m.group(1)[1:] if re.match(r"/[A-Za-z]:/", m.group(1)) else m.group(1)  # file:///C:/...
            add(f"{path}:{m.group(2)} {m.group(3)[:100]}", i, i + 1)
        elif (m := FILE_ERR.match(line)) and not GRADLE_TASK.match(line):
            add(f"{m.group(1)}:{m.group(2)} {m.group(3)[:100]}", i, i + 3)
    if flutter and any(f[0] is None for f in flutter):
        # one test file: flutter prints bare test names, the file only in the closing "Failing tests:" list
        listed = {}
        for line in lines[-200:]:
            if m := FLUTTER_LISTED.match(line):
                listed.setdefault(m.group(2), local_path(m.group(1), cwd))
        for f in flutter:
            f[0] = f[0] or listed.get(f[1])
        flutter = [f for f in flutter if f[0]]
    stats = next((m.group(1) for line in reversed(lines[-400:]) for r in STATS if (m := r.search(line))), "")
    if not stats and (done := next((m for line in reversed(lines[-50:]) if (m := FLUTTER_DONE.match(line))), None)):
        passed, skipped, failed = done.groups()
        stats = ", ".join(x for x in (f"{passed} passed", failed and f"{failed} failed", skipped and f"{skipped} skipped") if x)
    if not stats and go_tests:
        stats = f"{len(go_tests)} failed"
    hint = rerun_hint(cmd, flutter, jest, pytest_ids, go_tests, go_pkgs, gradle, xctests, fails)
    return fails, hint, stats


def local_path(path, cwd):
    """Absolute paths in tool output -> relative to the command's directory, as the re-run expects."""
    try:
        return Path(os.path.relpath(path, cwd)).as_posix() if os.path.isabs(path) else path
    except ValueError:
        return path


def rerun_hint(cmd, flutter, jest, pytest_ids, go_tests, go_pkgs, gradle, xctests, fails):
    """A command that re-runs only what failed, or None when the check is fast enough to repeat as is."""
    q = shlex.quote
    if flutter:
        files = sorted({f for f, _ in flutter})
        if len(flutter) == 1 and flutter[0][1]:
            return f"flutter test {q(files[0])} --plain-name {q(flutter[0][1])}"
        return "flutter test " + " ".join(q(f) for f in files)
    if jest:
        files = sorted({f for f, _ in jest})
        name = f" -t {q(jest[0][1])}" if len(jest) == 1 else ""
        if re.match(r"(?:npm|pnpm|yarn|bun)\s+(?:run\s+)?test\b", cmd):
            return f"{cmd} -- {' '.join(q(f) for f in files)}{name}"
        tool = "npx vitest run" if "vitest" in cmd else "npx jest"
        return f"{tool} {' '.join(q(f) for f in files)}{name}"
    if pytest_ids:
        base = "python -m pytest" if "-m pytest" in cmd else "pytest"
        return f"{base} " + " ".join(q(t) for t in pytest_ids[:10])
    if go_tests:
        pkgs = " ".join(sorted(set(go_pkgs))) or "./..."
        return f"go test -run {q('^(' + '|'.join(sorted(set(go_tests))) + ')$')} {pkgs}"
    if gradle:
        task = m.group(1) if (m := re.search(r"(\S*[tT]est\S*)", cmd.split("gradlew", 1)[-1])) else "test"
        return f"./gradlew {task} " + " ".join(f"--tests {q(t)}" for t in sorted(set(gradle))[:10])
    if xctests and "xcodebuild" in cmd:
        return cmd + "".join(f" -only-testing:<Target>/{t}" for t in xctests[:10])
    if fails and re.search(r"\beslint\b", cmd):
        files = sorted({f["label"].split(":")[0] for f in fails})
        return "npx eslint " + " ".join(q(f) for f in files[:20])
    return None


# ---------- summary ----------

def fmt_dur(sec):
    sec = int(sec)
    return f"{sec // 60}m{sec % 60:02d}s" if sec >= 60 else f"{sec}s"


def quote(cmd):
    """Shell-quote a command readably: double quotes when it only contains single quotes."""
    if "'" in cmd and not re.search(r"[\"`\\]|\$(?!')", cmd):
        return f'"{cmd}"'
    return shlex.quote(cmd)


def check_cmd(name, cwd_rel, cmd):
    c = f" -C {shlex.quote(cwd_rel)}" if cwd_rel not in (".", "") else ""
    return f"bash scripts/check.sh {name}{c} -- {quote(cmd)}"


def summary(e, cached=False):
    stats = f" · {e['stats']}" if e.get("stats") else ""
    when = datetime.fromtimestamp(e["ts"]).strftime("%H:%M")
    if e["exit"] == 0:
        tag = f" (cached: code unchanged since the {when} run; --fresh to force)" if cached else ""
        return f"✔ {e['name']} PASS{tag} · {fmt_dur(e['dur'])}{stats} · log: {e['log']}"
    status = "TIMEOUT (killed)" if e.get("timed_out") else f"FAIL (exit {e['exit']})"
    out = [f"✘ {e['name']} {status} · {fmt_dur(e['dur'])}{stats} · log: {e['log']} ({e['lines']} lines)"]
    if cached:
        out.append(f"  (cached: code unchanged since this run failed at {when}. Read the log instead of re-running; "
                   f"--fresh only if the failure is flaky or environmental.)")
    fails = e.get("failures") or []
    if fails:
        out.append("Failures (Read these line ranges of the log; never re-run just to see output):")
        for i, f in enumerate(fails[:SHOWN], 1):
            rng = f"line {f['start']}" if f["end"] <= f["start"] else f"lines {f['start']}-{f['end']}"
            out.append(f"  {i}. {f['label']} → {rng}")
        if len(fails) > SHOWN:
            out.append(f"  … {len(fails) - SHOWN} more (Grep the log)")
    else:
        out.append("No known failure format; error-like lines (line: text):")
        out += [f"  {n}: {t}" for n, t in e.get("errors") or []] or ["  (none)"]
        out.append("Last lines:")
        out += [f"  {n}: {t}" for n, t in e.get("tail") or []] or ["  (no output)"]
    if e.get("rerun"):
        out.append(f"Fix, then re-run only the failures: {check_cmd(e['name'].split('~')[0] + '~rerun', e['cwd'], e['rerun'])}")
        out.append("Run the full check once more at the end.")
    if e["dur"] > 90:
        out.append(f"Takes {fmt_dur(e['dur'])}: start it with the Bash tool's run_in_background: true next time.")
    return "\n".join(out)


# ---------- main ----------

def auto_name(cmd, cwd_rel):
    words = [w for w in re.split(r"\s+", cmd.strip()) if w and "=" not in w.split("/")[0]]
    words = [w for w in words if w not in ("npx", "bunx", "exec", "-m", "python", "python3", "fvm")]
    core = [re.sub(r"[^A-Za-z0-9]+", "", Path(w).name) for w in words[:3] if not w.startswith("-")][:2]
    digest = hashlib.sha1(f"{cwd_rel}\0{cmd}".encode()).hexdigest()[:4]
    return "-".join([c for c in core if c] + [digest])


def parse_args(argv):
    opts = {"cwd": None, "fresh": False, "keep": None, "timeout": None}
    if "--" not in argv:
        raise SystemExit("usage: bash scripts/check.sh <name> [-C dir] [--fresh] [--keep F-xxx] [--timeout sec] -- <command>")
    i = argv.index("--")
    head, cmd = argv[:i], argv[i + 1:]
    if not head or not cmd:
        raise SystemExit("check: need a check name before -- and a command after it")
    name, rest = head[0], head[1:]
    while rest:
        flag = rest.pop(0)
        if flag == "--fresh":
            opts["fresh"] = True
        elif flag in ("-C", "--keep", "--timeout") and rest:
            opts[{"-C": "cwd", "--keep": "keep", "--timeout": "timeout"}[flag]] = rest.pop(0)
        else:
            raise SystemExit(f"check: unknown option {flag}")
    return name, (cmd[0] if len(cmd) == 1 else shlex.join(cmd)), opts


def keep_evidence(log, feature, name):
    if not log or not (ROOT / log).is_file():
        return
    dest = ROOT / "docs" / "07-qa" / "evidence" / feature
    dest.mkdir(parents=True, exist_ok=True)
    target = dest / f"{name}-{Path(log).name}"
    shutil.copyfile(ROOT / log, target)
    print(f"  evidence: {rel(target)}")


def main(argv):
    if argv[:1] == ["--clean"]:
        return clean() or 0
    if argv[:1] == ["--prune"]:
        return prune() or 0
    name, cmd, opts = parse_args(argv)
    cwd = Path(opts["cwd"]).resolve() if opts["cwd"] else Path.cwd()
    cwd_rel = rel(cwd)
    if name == "auto":
        name = auto_name(cmd, cwd_rel)
    name = re.sub(r"[^\w.~-]+", "-", name)
    pol = policy()
    cacheable = not NO_CACHE.search(f"{name} {cmd}")
    fp = fingerprint(cwd) if cacheable else None

    last = next((e for e in reversed(read_index())
                 if e.get("name") == name and e.get("cmd") == cmd and e.get("cwd") == cwd_rel), None)
    if (fp and not opts["fresh"] and last and last.get("fp") == fp and not last.get("timed_out")
            and (last["exit"] == 0 or (ROOT / last["log"]).is_file())):
        print(summary(last, cached=True))
        if opts["keep"]:
            keep_evidence(last["log"], opts["keep"], name)
        return last["exit"]

    d = RUNS / name
    d.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S") + f"-{os.getpid()}"
    partial = d / f"{stamp}.log.partial"
    print(f"▶ {name}: {cmd}  (log: {rel(partial)})", flush=True)
    start = time.time()
    code, timed_out = run(cmd, cwd, partial, float(opts["timeout"]) if opts["timeout"] else None)
    dur = time.time() - start
    log = d / f"{stamp}-{'pass' if code == 0 else 'fail'}.log"
    os.replace(partial, log)
    cap_log(log, pol["runs_max_log_mb"])

    lines = log.read_text(encoding="utf-8", errors="replace").splitlines()
    entry = {"ts": start, "name": name, "cmd": cmd, "cwd": cwd_rel, "exit": code, "dur": round(dur, 1),
             "log": rel(log), "lines": len(lines), "fp": fp, "timed_out": timed_out}
    failures, hint, stats = analyse(lines, cmd, cwd)
    entry["stats"] = stats
    if code != 0:
        entry.update(failures=failures, rerun=hint)
        if not failures:
            errs = [(n, t.strip()[:160]) for n, t in enumerate(lines, 1) if GENERIC.search(t)]
            entry["errors"] = errs[-15:]
            entry["tail"] = [(n, t[:160]) for n, t in enumerate(lines, 1)][-15:]
    append_index(entry)
    if code == 0:
        after_pass(name, log)
    prune(pol)
    print(summary(entry))
    if opts["keep"]:
        keep_evidence(entry["log"], opts["keep"], name)
    return code


if __name__ == "__main__":
    try:
        code = main(sys.argv[1:])
        sys.stdout.flush()
    except OSError as exc:  # reader closed the pipe (e.g. `| head`): the log is complete anyway
        if not isinstance(exc, BrokenPipeError) and exc.errno != 22:
            raise
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        code = 1
    sys.exit(code)
