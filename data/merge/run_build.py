"""Box-3 site runner (task 211): build a list of site ids through the project's own
machinery (pipeline/build_catalog.py per site, then build_site.set_drawings so the
site's entry in web/data/sites.json carries its post-depiction marks), logging every
step to data/merge/build_sites.log (append).

usage: run_build.py <sid> [<sid> ...]     |     run_build.py --marks-only <sid> ...

One process per site: a killed session leaves a clean boundary at the last finished
site (the driver commits the uncommitted work; the next session resumes with the
remaining ids - build_catalog skips already-built sites itself).
"""
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG = os.path.join(ROOT, "data", "merge", "build_sites.log")
VENV = os.path.join(ROOT, ".venv", "bin", "python")


def ts():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def log(line):
    with open(LOG, "a") as f:
        f.write(line + "\n")


def marks_of(sid):
    sys.path.insert(0, os.path.join(ROOT, "pipeline"))
    import build_site
    build_site.set_drawings(sid)
    p = os.path.join(ROOT, "web", "data", "sites", sid, "depictions.json")
    n = len(json.load(open(p))["depictions"]) if os.path.exists(p) else 0
    log(f"marks refreshed: {sid} depictions: {n}")


def run(sid):
    log(f"=== {sid} start {ts()} ===")
    r = subprocess.run([VENV, "pipeline/build_catalog.py", "--ids", sid],
                       cwd=ROOT, capture_output=True, text=True)
    for line in (r.stdout or "").strip().splitlines():
        log(line)
    if r.stderr and r.stderr.strip():
        for line in r.stderr.strip().splitlines()[-12:]:
            log(line)
    log(f"=== {sid} build rc={r.returncode} {ts()} ===")
    if r.returncode != 0:
        return False
    built = [l for l in (r.stdout or "").splitlines() if l.startswith("built ")]
    if built and not built[-1].startswith("built 1"):
        log(f"NOT BUILT: {sid}")
        return False
    marks_of(sid)
    return True


def main():
    args = sys.argv[1:]
    marks_only = []
    if "--marks-only" in args:
        i = args.index("--marks-only")
        marks_only = args[i + 1:]
        args = args[:i]
    for sid in args:
        ok = run(sid)
        log(f"=== {sid} {'ok' if ok else 'FAILED'} ===")
    for sid in marks_only:
        marks_of(sid)


if __name__ == "__main__":
    main()
