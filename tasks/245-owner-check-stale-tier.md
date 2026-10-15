Status: done
Depends on: 815
Touches: web/index.html

# 245: The 307d owner check - the marker keeps the pre-rescore tier: saveFit's one-shot sites.json fetch

Filed 2026-10-15 (iteration 236, agent a, on the 230/242/810-814 cycle branch): the owner_check
pair, with the 814/816 settle + subpixel fix in, passed A end to end and red'd B for the first
time at a NEW step - "line effect (b): the site's square takes its new score's tier" - so this
is not the mid-transition flake (that one is fixed) and not a test defect: it is a product
race the test caught, and the cycle's green-suite gate (230's claim, 810's box 3, 242's box 2)
cannot be reliable while it stands. Built on agent/a's branch this iteration (the driver
carried the whole cycle to one agent so the tests pass with all of it in place); the 815 lane
(the page-side subpixel, same file) is what this task waits on for the claim.

## Why this task exists (the measured race, do not re-derive)

The save path (the test's hermetic server is the real one: `server/serve.py` runs
`tools/site_done.py`'s one-site line in a worker thread, which builds the overlay first and
re-scores the site second - the score is computed FROM the built overlays, so the order is
mandatory, `pipeline/build_site.py::marks`):

1. page PUTs the platefit doc; the worker syncs it: the site's `depictions.json` gains the new
   depiction entry (B's run: 01:57:23.310);
2. the worker then runs `build_site.set_drawings`, rewriting `web/data/sites.json` with the
   re-scored entry (01:57:23.429) - **119 ms later** (the ink build itself takes ~6.5 s, but the
   gap the page can land in is the depiction->re-score beat).

`saveFit()` (web/index.html) polls `depictions.json` every 1.5 s for the saved depiction and,
the moment it appears, fetches `data/sites.json` ONCE, adopts `drawings/score/oldest/overlays`
into the in-memory entry and sets the marker class from that fetch, then stops. A poll landing
in the 119 ms gap adopts the PRE-rescore score and the marker keeps its old tier until a
reload. Measured on 2026-10-15 (devil-s-dyke-q3307343, the pair's derived B pick): pre-save
score 1.1 (tier t1), post-save 1.45 (tier t2); the page's fetch landed in the gap, the live
marker read "marker t1" for the probe's full 120 s poll, and only the reloaded page showed the
correct "marker t2". The same run's A pick (richard-s-castle) won the race: its fetch landed
after the re-score and the class came out t2. The window is small (P per save ~10%) but it is
on the owner's own save path: the owner would see the wrong square tier until a manual reload.
The one-site line's own print ("plan_fit.py has re-scored the site in sites.json: take its new
tier") states the page's intent - taking the stale score is not a design, it is a race.

The pipeline order cannot be changed (the re-score reads the built depictions), the server
cannot push (the page polls files over HTTP; sockets are dead in the hermetic run by design),
so the fix is the page's adoption: re-fetch until the re-score has landed, bounded, before
setting the marker class.

## Goal

In `saveFit()` in web/index.html only. When the saved depiction appears in `depictions.json`,
replace the one-shot `sites.json` fetch with a bounded re-fetch loop: adopt
`drawings/score/oldest/overlays` from each fetch, and stop as soon as the fetched entry's
`overlays` count exceeds the in-memory pre-save value (the re-score ran for this save: the new
depiction is counted by `overlays()`); a missing `overlays` on either side keeps today's
single-fetch behaviour (no wait). Budget: 8 fetches at 250 ms (the re-score finishes within a
second of the depiction; the page must never hang on it - after the budget the existing
proceeds with what it has, exactly as today when the entry was missing). No other change: the
marker-class line, `endFit()`, `applyDep(s)` and the timeout fallback keep their behaviour; no
other function touched; the 815 page-side subpixel (same file, different function) is a
separate task this one depends on.

## Acceptance criteria

- [x] The fix is applied in `saveFit()` as designed (the one-shot fetch becomes the bounded
      re-fetch loop; everything else in the function and the file unchanged - diff review:
      no other line moved); the page still passes its own syntax check (extract the script
      block, `node --check`).
- [x] The owner_check pair passes with the fix: in two or three consecutive unflagged runs
      (one invocation each, A then B) the check "line effect (b): the site's square takes its
      new score's tier" is `[ok]` in EVERY run (pre-fix it red's when the 1.5 s poll lands in
      the depiction->re-score gap - measured 119 ms on 2026-10-15; the page's own adoption
      then takes the stale score no matter how long the probe polls, so no test-side wait can
      clear it - this check is the pair's regression gate for the race).
- [x] No new red against the branch's suite at claim time
      (`.venv/bin/python -m pytest tests/ -q -p no:cacheprovider`).
- [x] After ANY owner_check run the ten docs/site_flow/307d_*.png are restored to the
      committed bytes before committing (R5; 813's refresh flag retires this once it lands).

## Notes

- The reload-side check already asserts the same tier after a full page load (it fetches
  fresh), so a race that survives this fix would show as effects-red/reload-green - that
  split is the diagnostic signature if the loop's signal ever misfires.
- The signal choice: `overlays` (the built-overlay count, always incremented by the saved
  depiction) rather than `score` (which can stay value-equal across a rescore) or `drawings`
  (which only moves for drawing-kind fits). `marks()` sets all three from `overlays()`/
  `drawings()`; the page already copies all four fields.
- B's run artifacts that prove the timeline (retained 2026-10-15, /tmp/loop-ancient-works.a,
  pytest-of-agent/pytest-0/awowner0): doc write 01:57:15.802, base overlay 01:57:16.816, ink
  overlay 01:57:23.309, depictions.json 01:57:23.310, sites.json 01:57:23.429, review.json
  01:57:23.846.

## Hand-over

(2026-10-15, iteration 215, agent c - **task complete**: boxes 3 and 4 verified and
ticked this session; all four boxes ticked; `Status: done`).

**State:** branch agent/c = main (747ca6fb, 815's PITFALLS commit) + driver
bookkeeping only (no code delta; the 245 fix ab57da1b and 815's page hunk are both
on main). Regime = old R5 (813 not on main yet; agent a runs 810/812 in its own
checkout - no new commits on main since it.214). If this task is ever re-opened
BEFORE 813 lands: the worktree is clean, all ten 307d PNGs are at main's bytes, and
the box 4 restore discipline still applies (see the box). If re-opened AFTER 813
lands: box 4's discipline retires per the box's own note - an unflagged run must
leave the PNGs byte-identical (write-surface proof), no restore needed.

**Box 1 (ticked it.213):** the saveFit bounded re-fetch loop is on main exactly as
designed (fix commit ab57da1b, one hunk; no other line moved since; six script
blocks node --check clean).

**Box 2 (ticked it.214):** three consecutive unflagged pair runs (65.0/66.7/66.1
s), "line effect (b): the site's square takes its new score's tier" [ok] on A and
B in EVERY run, zero [warn] settle in all six probes.

**Box 3 (ticked this session):** the driver's exact full-suite command
`TMPDIR=/tmp/loop-ancient-works.c .venv/bin/python -m pytest tests/ -q -p
no:cacheprovider` -> **195 passed, 1 skipped, 0 failed** (593.45 s / 9:53; the
f160ae5a baseline was 195P/1S/0F in 631 s - same counts, faster). Identical counts
to main's last baseline -> no new red against the branch, no red to attribute (the
driver's 2026-10-13 loop-start red, test_fit_queue placement, does not reproduce on
current main). The suite's own owner_check run (one A-then-B invocation) passed ->
"line effect (b)" was [ok] in the claim run too. Pre-run checks: no live
pytest/serve in any checkout, no orphans of my lane, 24G free.

**Box 4 (ticked this session):** after EVERY owner_check run so far (the it.214
pair runs and this suite run) exactly the three known dirty PNGs (307d_A_1-card.png,
307d_B_1-card.png, 307d_B_5-reload.png) diverged - the same set as it.213/it.214;
all ten restored to main's bytes after each; `git diff main --stat --
docs/site_flow/` empty before this commit; worktree clean.

**Claim commit:** task file + DECISIONS.md only (no web/, no PNGs - the PNG
restorations were no-ops against HEAD, since the branch's PNGs already matched
main's).
