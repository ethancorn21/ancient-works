"""Consolidate: the single point where the per-source staging becomes the canonical data (task 211, GOAL.md point 5).

usage: fit/merge.py merge [--root DIR]

The source tasks stage rows next to the canonical files they belong to (data/catalog/extras_<source>*.jsonl,
data/commons/files_<source>*.jsonl, data/commons/classified_<source>*.jsonl). This command is the only writer of
the canonical data/catalog/extras.jsonl, data/commons/files.jsonl and data/commons/classified.jsonl; nothing else
in the project writes them. The staging files are left in place: each source module's own --check still reads
them, and a later source (or a re-stage) that appends new rows is picked up by the next run, which stays a no-op
for everything already merged (idempotent over whatever staging exists).

Rules:
- append-only: a canonical file only grows; every pre-merge line stays byte-identical (the file is rewritten as
  old bytes plus new lines through a temp file, so a crash never truncates the old rows).
- identity: a row is keyed by id (catalog rows) or (site, title) (commons rows); two rows are equal when their
  JSON is equal with keys sorted, so key order in the file is irrelevant.
- first row wins: a key already present (before the merge or in an earlier source file, files read in sorted
  name order) keeps its first row. A conflicting staging row is dropped and recorded in the merge log - never a
  silent rewrite of a row that is not identical.
- evidence gate (files rows only): a picture row (one with a title) must carry the 200 evidence field (rec
  "evidence/1") and must not be kind "none" - a row with no machine-checkable tie is reported and refused, never
  silently kept. Sentinel rows (a site with no old files, no title) are exempt.
- data/merge/log.jsonl: a snapshot of this run's reconciliation, one line per staging row (action merged /
  conflict / rejected), deterministically ordered, no timestamps. A run that changes nothing rewrites it
  byte-identical, so the second run changes nothing.

Exit code 0 when no row was refused; 1 when any row was rejected or the run failed loudly (a malformed row, a
row without a key). A refused row does not stop the merge of the rest.
"""
import glob
import json
import os
import sys

REC = "evidence/1"
LOG = "data/merge/log.jsonl"

# (canonical file, staging prefix, row key) - the three files the page's data is built from
TARGETS = [
    ("data/catalog/extras.jsonl", "data/catalog/extras_", lambda r: (r.get("id"),)),
    ("data/commons/files.jsonl", "data/commons/files_", lambda r: (r.get("site"), r.get("title"))),
    ("data/commons/classified.jsonl", "data/commons/classified_", lambda r: (r.get("site"), r.get("title"))),
]


def norm(line):
    """Row identity that does not depend on key order or ASCII escaping."""
    return json.dumps(json.loads(line), sort_keys=True, ensure_ascii=False)


def source_of(path, prefix):
    """extras_kip.jsonl with prefix extras_ -> kip."""
    base = os.path.basename(path)
    p = os.path.basename(prefix)
    return base[len(p):-len(".jsonl")]


def key_present(key):
    return any(v is None for v in key)


def run_target(root, target, prefix, keyfn, decide):
    """One canonical file: append every staging row that is not there yet. Returns (added, refused).

    decide(target, key, source, action, note) records each staging row's outcome for the merge log."""
    tpath = os.path.join(root, target)
    canon = {}   # key -> raw line (the first row holding the key)
    new_lines = []
    if os.path.exists(tpath):
        for line in open(tpath, encoding="utf-8"):
            if line.strip():
                canon.setdefault(keyfn(json.loads(line)), line)
    added = refused = 0
    for path in sorted(glob.glob(os.path.join(root, prefix + "*.jsonl"))):
        rel = os.path.relpath(path, root)
        src = source_of(path, prefix)
        for lineno, line in enumerate(open(path, encoding="utf-8"), 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
                key = keyfn(row)
            except (ValueError, KeyError, TypeError) as e:
                raise SystemExit(f"merge: {rel}:{lineno}: {e}")
            if key_present(key):
                raise SystemExit(f"merge: {rel}:{lineno}: row has no key field: {line[:120]}")
            if key in canon:
                if norm(canon[key]) == norm(line):
                    decide(target, key, src, "merged", None)
                else:
                    refused += 1
                    decide(target, key, src, "conflict",
                           "the first row holding this key is kept; the staged row differs and was dropped: " + line[:160])
                continue
            if target.endswith("files.jsonl") and row.get("title"):
                ev = row.get("evidence")
                if not isinstance(ev, dict) or ev.get("rec") != REC:
                    refused += 1
                    decide(target, key, src, "rejected", f"no 200 evidence field (rec {REC!r})")
                    continue
                if ev.get("kind") == "none":
                    refused += 1
                    decide(target, key, src, "rejected", "evidence kind 'none' - no machine-checkable tie; refused, never silently kept")
                    continue
            canon[key] = line
            new_lines.append(line if line.endswith("\n") else line + "\n")
            added += 1
            decide(target, key, src, "merged", None)
    if new_lines:
        grow(tpath, new_lines)
    return added, refused


def grow(tpath, new_lines):
    """Append the new lines: old bytes untouched, written back through a temp file (atomic)."""
    data = b"" if not os.path.exists(tpath) else open(tpath, "rb").read()
    if data and not data.endswith(b"\n"):
        data += b"\n"  # make the last stored row line-terminated before the growth; its own bytes are untouched
    tmp = tpath + ".tmp"
    with open(tmp, "wb") as f:
        f.write(data)
        f.writelines(new_lines)
    os.replace(tmp, tpath)


def write_log(root, entries):
    """data/merge/log.jsonl: the snapshot of this run, deterministically ordered. A no-op run rewrites it
    byte-identical, which keeps the second run a no-op."""
    lpath = os.path.join(root, LOG)
    ordered = sorted(entries, key=lambda e: (e["target"], json.dumps(e["key"], sort_keys=True), e["source"], e["action"]))
    text = "".join(json.dumps(e, sort_keys=True, ensure_ascii=False) + "\n" for e in ordered)
    if not text:
        if os.path.exists(lpath):
            os.remove(lpath)  # nothing staged anymore: nothing to log
        return
    old = open(lpath, encoding="utf-8").read() if os.path.exists(lpath) else None
    if old == text:
        return
    os.makedirs(os.path.dirname(lpath), exist_ok=True)
    tmp = lpath + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, lpath)


def main(argv):
    if argv and argv[0] != "merge":
        raise SystemExit(__doc__.strip().splitlines()[1])
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if "--root" in argv:
        root = os.path.abspath(argv[argv.index("--root") + 1])

    entries = []

    def decide(target, key, src, action, note):
        entries.append({"action": action, "key": list(key), "note": note, "source": src, "target": target})

    totals = []
    refused = 0
    for target, prefix, keyfn in TARGETS:
        added, ref = run_target(root, target, prefix, keyfn, decide)
        refused += ref
        totals.append(f"{target}: +{added}")
    write_log(root, entries)
    print("; ".join(totals) + f"; log: {LOG}, refused: {refused}")
    raise SystemExit(1 if refused else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
