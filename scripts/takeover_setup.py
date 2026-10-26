"""Set up (or re-attach on another machine) a takeover engagement; called by scripts/setup.sh.

Usage: takeover_setup.py [--takeover <git-url> [--ref <branch|tag|sha>]]

- First run with --takeover: clones the customer's repository into client/ (ignored by the workspace's git),
  pins the audited baseline (the ref's commit, checked out detached so nothing moves it), and turns
  state/project.json into a takeover project: phase t0-engagement, gates TG0/TG1/G2/G3, `takeover` block.
- Later runs (no arguments, e.g. on the second machine): when the project is a takeover and client/ is
  missing, clone it again and check out the baseline (before TG1) or the ref (after).
Refuses to turn a new-app project that has already started into a takeover.
"""
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECT = ROOT / "state" / "project.json"
CLIENT = ROOT / "client"


def fail(msg):
    sys.stderr.write(f"setup: {msg}\n")
    sys.exit(1)


def git(*args, check=True):
    out = subprocess.run(["git", *args], capture_output=True, text=True)
    if check and out.returncode != 0:
        fail(f"git {' '.join(args)} failed:\n{out.stderr.strip()}")
    return out.stdout.strip()


def parse(argv):
    url = ref = None
    while argv:
        flag = argv.pop(0)
        if flag in ("--takeover", "--ref") and argv:
            value = argv.pop(0)
            url, ref = (value, ref) if flag == "--takeover" else (url, value)
        else:
            fail(f"unknown argument {flag}. Usage: bash scripts/setup.sh [--takeover <git-url> [--ref <branch|tag|sha>]]")
    if ref and not url:
        fail("--ref needs --takeover <git-url>")
    return url, ref


def clone(url):
    if (CLIENT / ".git").exists():
        return False
    if CLIENT.exists() and any(CLIENT.iterdir()):
        fail("client/ exists but is not a git repository; move it away and run setup again.")
    print(f"setup: cloning the customer's repository into client/ ({url})")
    git("clone", url, str(CLIENT))
    return True


def ignore_client():
    gitignore = ROOT / ".gitignore"
    lines = gitignore.read_text(encoding="utf-8").splitlines() if gitignore.exists() else []
    if "client/" not in lines:
        lines += ["", "# Takeover: the customer's repository has its own git history (scripts/setup.sh --takeover)", "client/"]
        gitignore.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("setup: added client/ to .gitignore")


def env_examples():
    files = git("-C", str(CLIENT), "ls-files", "*.env.example", ".env.example", check=False).splitlines()
    return [f for f in files if f]


def main(argv):
    url, ref = parse(argv)
    project = json.loads(PROJECT.read_text(encoding="utf-8"))
    takeover = project.get("takeover") or {}
    is_takeover = project.get("engagement") == "takeover"

    if url and is_takeover and takeover.get("source_repo") not in (None, url):
        fail(f"this workspace already takes over {takeover['source_repo']}; one workspace per engagement.")
    if url and not is_takeover and (project.get("phase") != "0-intake" or project.get("phase_status") != "not-started"):
        fail("this workspace already runs a new-app project. Clone the template into a new folder for the takeover.")
    if not url and not is_takeover:
        return 0

    url = url or takeover.get("source_repo")
    if not url:
        fail("state/project.json says takeover but has no takeover.source_repo.")
    ignore_client()
    cloned = clone(url)
    client = str(CLIENT)

    if not is_takeover:
        if ref:
            git("-C", client, "checkout", "--quiet", ref)
        ref = ref or git("-C", client, "rev-parse", "--abbrev-ref", "HEAD")
        sha = git("-C", client, "rev-parse", "HEAD")
        git("-C", client, "checkout", "--quiet", "--detach", sha)
        project.update({
            "engagement": "takeover",
            "phase": "t0-engagement",
            "phase_status": "not-started",
            "gates": {"TG0_engagement": "pending", "TG1_direction": "pending",
                      "G2_stack": "pending", "G3_release": "pending"},
            "takeover": {"source_repo": url, "ref": ref, "baseline_sha": sha,
                         "baseline_date": date.today().isoformat(), "owners": {}},
        })
        PROJECT.write_text(json.dumps(project, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"setup: takeover project created; audited baseline {sha[:10]} ({ref}). client/ is read-only until gate TG1.")
    elif cloned:
        writable = (project.get("gates") or {}).get("TG1_direction") == "approved"
        target = takeover.get("ref") if writable else takeover.get("baseline_sha")
        args = ["checkout", "--quiet"] + ([] if writable else ["--detach"]) + [target]
        git("-C", client, *args)
        print(f"setup: client/ checked out at {target} ({'TG1 approved' if writable else 'audited baseline'}).")
    else:
        print(f"setup: client/ already present (HEAD {git('-C', client, 'rev-parse', '--short', 'HEAD', check=False)}).")

    envs = env_examples()
    if envs:
        print("setup: the customer's app reads local secrets. PO only: copy your own values next to each of:")
        for f in envs:
            print(f"         client/{f}  ->  client/{f[:-len('.example')]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
