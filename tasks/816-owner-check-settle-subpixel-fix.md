Status: open
Depends on: 307d
Touches: tests/test_owner_check.py, docs/site_flow/307d_*.png (R5: restoring suite re-encodes to
main's bytes before committing - never content changes)

# 816: The 307d owner check - the settle + subpixel probe fix, standalone (the built 814 fix republished so it reaches main without the 814<->230 claim cycle)

(2026-10-15, iteration 195, agent c, filed under the driver's 814 split: agent a had had nothing
to build for 43 minutes, and every waiter - 230, 241, 236c - was held on 814 alone.)

## Why this task exists (read first)

814 built this exact fix and committed it on agent/c (63a4e4e), but its done-claim was
rejected: the driver's mechanical re-check counts the roman test red
(tests/test_src_roman_maclauchlan.py::test_check_staged_joins_and_passes - red on MAIN since
207a/207b's roman staging, cleared by 230's data re-run) as a new red on 814's branch. That red
clears only when 230 merges, and 230's claim was held on 814's old chain (242, 810, 812, 813,
814 on its Depends line): a formal wait cycle the driver's "never both ways" rule forbids.
This task is the fix republished as an independently claimable part: it depends only on done
307d, so it starts immediately. Agent a is the intended claimant: its checkout already carries
230's data, so its suite gate has no roman red. When it merges: the pair is stable on EVERY
branch (230's held claim is released - its Depends now carries this number; 815 unblocks in
parallel); 814 then re-claims against a green main and the 812 -> 813 -> 810 -> 811 -> 242
chain proceeds. The recipe below is the exact committed diff (63a4e4e against the pre-fix file
it came from, 54 added / 0 changed; verified at 195 to apply verbatim to the current main
file, which has no settle/subpixel lines) - apply it as-is, do not redesign.

## The fix (recipe - apply as-is to the embedded PROBE of tests/test_owner_check.py)

````
diff --git a/tests/test_owner_check.py b/tests/test_owner_check.py
@@ -280,6 +280,41 @@ const nextAfter = pending[pending.findIndex(e => e.site === site) + 1];
 const browser = await chromium.launch({ channel: 'chrome', headless: true,
   args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
 const page = await browser.newPage({ viewport: { width: 1280, height: 820 }, colorScheme: 'light' });
+// Settle the map view before every capture and quad read: place chains the 4.5 s site flyTo
+// (index.html select) with a 900 ms fitBounds (fitkit _fkActivate), save runs a 900 ms
+// easeTo, and a deep-link reload re-fires the 4.5 s flyTo - a fixed sleep ends
+// mid-transition, and a mid-transition shot shifts the overlay rectangle against the ground
+// imagery (the 28.6-33.6% run-to-run drift the 242 family measured).
+// isMoving() is true while any camera animation is in flight (MapLibre 5.6.0: _prepareEase
+// sets it, _easeEnd clears it) and false once the view settles; the bounded timeout keeps the
+// probe from hanging - a shot taken after it is mid-transition and the 812 double-shot assert
+// fails loudly on it.
+const settle = async (budgetMs = 20000) => {
+  const t0 = Date.now();
+  while (Date.now() - t0 < budgetMs) {
+    if (await page.evaluate(() => !map.isMoving())) return;
+    await sleep(150);
+  }
+  console.log('[warn] settle: the map view was still moving after ' + budgetMs + ' ms');
+};
+// The quad reads quantise a second way, once the camera is settled: MapLibre 5.6.0's Marker
+// defaults subpixelPositioning to false (ctor: e&&e.subpixelPositioning||!1) and _update rounds
+// _pos to integer pixels on every setLngLat and moveend update, so the page's fit markers
+// (addPairMarker: no subpixel option) sit at whole pixels - a 1-px rounding error exceeds the
+// 1% tolerance on an ~83-px edge (192 measured it: true q1 edge 82.9807 read 82.0, true q2 edge
+// 87.1384 read 87.0057 - exactly the 1.06105 the 230/239/241 flake recorded; the true ratio
+// 1.0501 passes). _fkApply recreates the marker objects with the fresh false default, so this
+// re-enables the vendored public API on the LIVE markers before every read and shot, then forces
+// one re-position (setLngLat of the same point) so an already-rounded marker actually moves.
+// Idempotent with the page-side fix (addPairMarker passing subpixelPositioning: true).
+const subpixel = async () => {
+  await page.evaluate(() => {
+    for (const m of P.marks) {
+      if (!m._subpixelPositioning) m.setSubpixelPositioning(true);
+      if (m._lngLat) m.setLngLat(m.getLngLat());
+    }
+  });
+};
 const lines = [];
 page.on('pageerror', e => lines.push('[pageerror] ' + e.message));
 page.on('requestfailed', r => lines.push('[reqfail] ' + r.url() + ' ' + (r.failure() && r.failure().errorText)));
@@ -296,6 +331,8 @@ const cardText = () => page.evaluate(() => { const c = document.getElementById('
 const card1 = await cardText();
 check('the card names the pick and its best row', !!card1 && card1.name === (pick.name || pick.site) &&
   card1.text.includes(pick.best.row.title || pick.best.row.id), { card1, want: pick.name });
+await settle();
+await subpixel();
 await page.screenshot({ path: outdir + '/1-card.png' });
 
 // ---- place
@@ -311,6 +348,9 @@ await page.click('#fqplace');
 await page.waitForSelector('#fkbar', { timeout: 60000 });
 await page.waitForFunction(() => [...document.querySelectorAll('.gpin.fk-handle')].filter(el => el.style.display !== 'none').length === 4, null, { timeout: 30000 });
 await sleep(2500);
+// the place chain: the 4.5 s site flyTo interrupted by the 900 ms fitBounds
+await settle();
+await subpixel();
 const q0 = await quad(), c0 = await groundOnScreen([propC[2], propC[3]]);
 const sites0 = await served('data/sites.json');
 const entry0 = (sites0.sites || sites0).find(x => x.id === site) || {};
@@ -319,18 +359,26 @@ check('place: the earlier overlay is hidden while placing', !before.vis || (awai
 check('place: the site\'s own ground is pressed (LiDAR relief unless the site has none)',
   await page.evaluate(id => document.getElementById(id) ? document.getElementById(id).getAttribute('aria-pressed') === 'true' : true,
     entry0.lidar === false ? 'g-imagery' : 'g-relief'));
+await settle();
+await subpixel();
 await page.screenshot({ path: outdir + '/2-placed.png' });
 
 // ---- move it the way the owner does: a drag on it, the toolbar's scale and turn
 const mid = [q0.reduce((s, p) => s + p[0], 0) / 4, q0.reduce((s, p) => s + p[1], 0) / 4];
 await page.mouse.move(...mid); await page.mouse.down(); await page.mouse.move(mid[0] + 30, mid[1] + 20, { steps: 6 }); await page.mouse.up();
 await sleep(400);
+await settle();
+await subpixel();
 const q1 = await quad();
 check('drag on the drawing moves it by the pointer', q1.every((p, i) => Math.hypot(p[0] - q0[i][0] - 30, p[1] - q0[i][1] - 20) < 2.5), { q0, q1 });
 await page.click('#fkbar [data-a="s+"]'); await page.click('#fkbar [data-a="r+"]'); await sleep(500);
+await settle();
+await subpixel();
 const q2 = await quad();
 const edge = q => Math.hypot(q[1][0] - q[0][0], q[1][1] - q[0][1]);
 check('toolbar scale and turn change the drawing on screen', Math.abs(edge(q2) / edge(q1) - 1.05) < 0.01, { e1: edge(q1), e2: edge(q2) });
+await settle();
+await subpixel();
 await page.screenshot({ path: outdir + '/3-gestured.png' });
 
 // ---- save from the toolbar: where the corners sit now is what must land
@@ -369,6 +417,9 @@ if (effects.corners) {
 check('line effect (b): the site\'s square takes its new score\'s tier',
   (effects.markerClass || '').split(/\s+/).includes('marker') && (effects.markerClass || '').split(/\s+/).includes(effects.tier), effects);
 check('line effect (c): the site left the open review list', effects.inOpen === false, effects);
+// the save just ran the page's 900 ms easeTo - the shot must not land mid-transition
+await settle();
+await subpixel();
 await page.screenshot({ path: outdir + '/4-saved.png' });
 
 // ---- the card moves on
@@ -402,6 +453,9 @@ check('reload: the site opens with the saved drawing selected and on the map, in
   reload.selectedDep === effects.overlayFile && reload.depVis === 'visible' && reload.depSrc === 'data/sites/' + site + '/' + effects.overlayInk &&
   reload.aerial && reload.ink, reload);
 await sleep(3000);
+// the reload re-fired the 4.5 s site flyTo via the deep link
+await settle();
+await subpixel();
 await page.screenshot({ path: outdir + '/5-reload.png' });
 await page.click('#back', { timeout: 20000 });
 await page.waitForSelector('#fqcard', { timeout: 20000 }).catch(() => {});
````

## Goal

In tests/test_owner_check.py and its embedded PROBE, exactly the recipe above: before every
capture and quad read, wait for the map view to settle (poll `!map.isMoving()` with a bounded
timeout) and re-enable subpixel marker positioning on the live markers. The pick (derived,
never pinned) and every existing check stay exactly as they are; this is a capture-timing
fix, not a flow change. Do not touch tests/test_fit_queue.py (the 307/235 family) or the
page (the page-side counterpart is 815, a separate task on web/index.html). The pair always
runs as one invocation, A then B (PITFALLS: the B test cannot run in isolation).

## Acceptance criteria

- [ ] The fix is applied exactly: the file's diff against the pre-edit file is the 54 lines
      above (0 changed / 0 removed); no TEMP instrumentation residue
      (`grep -cE "TEMP|camlog|__cam|dumpHandles" tests/test_owner_check.py` = 0).
- [ ] Two or three consecutive unflagged pair runs pass end to end (`.venv/bin/python -m pytest
      tests/test_owner_check.py -q -p no:cacheprovider`, one invocation, A then B); every
      run's probe log shows zero `[warn] settle` lines and the ratio check `toolbar scale and
      turn change the drawing on screen` is `[ok]` (pre-fix on this same checkout: red 4/4 at
      the recorded 1.06105, it.214-216).
- [ ] A two-run comparison finds A_4/A_5/B_4/B_5 byte-identical or <0.5% differing pixels at
      threshold 32 (the 28.6-33.6% run-to-run drift is gone) and the other six views at/below
      their historical 0-1.25% band.
- [ ] After ANY owner_check run the ten docs/site_flow/307d_*.png are restored to the committed
      bytes before committing (`git show HEAD:docs/site_flow/<name>.png > docs/site_flow/<name>.png`
      per changed file); the committed tree is clean (R5 - 813's refresh flag retires this once
      it lands).
- [ ] No new red against this branch's suite at claim time (`.venv/bin/python -m pytest tests/ -q
      -p no:cacheprovider`). On this (agent a's) branch the roman red is expected GREEN from
      230's data state (verify with the 2 s isolated run); if it is red, that is a 230-lane
      issue: log it in DECISIONS and stop - do not fix 230's data in passing.

## Notes

- Root cause (814's iterations 192-194, measured - 814's file carries the full record): two
  independent quantisations. (1) Mid-transition captures: the 4.5 s site flyTo (index.html) +
  900 ms fitBounds (fitkit `_fkActivate`) / the 900 ms easeTo on save / the deep-link flyTo on
  reload; `settle()` polls `!map.isMoving()` at 150 ms with a 20 s budget (`Map.isMoving()` is
  true exactly while a camera animation is in flight in MapLibre 5.6.0), called before all
  five shots and the q0/q1/q2 reads, after the existing fixed sleeps. (2) Integer-pixel marker
  rounding (the q1/q2 ratio flake - NOT a moving camera, proven settled to 10-digit zoom with
  zero camera events between reads): `Marker` defaults subpixelPositioning to false and
  `_update` rounds `_pos` on every setLngLat/moveend, so `subpixel()` re-enables the vendored
  public API on the live markers plus one forced re-position, and re-runs after EVERY settle
  site (8 total) because `_fkApply` (web/fitkit.js ~215) recreates the marker objects with the
  fresh false default on each s+/r+ step.
- 194 evidence (the same fix on agent/c, 63a4e4e): two consecutive unflagged pair runs green
  (66.06 s / 66.63 s); run-vs-run A_4/A_5/B_4 byte-identical, B_5-reload 0.0073%, the rest
  at/below 0.0447% (historical band); every probe log all `[ok]`, zero `[warn] settle`, ratio
  check `[ok]` in every captured run (192: red 4/4 without the fix; 193-194: green 6/6); full
  suite no new reds.
- The page-side counterpart (addPairMarker passing subpixelPositioning: true, web/index.html)
  is 815 - it depends on this task and builds in parallel (different file).
- Probe-log capture (the logs die when a green pytest session ends): they live under
  `$TMPDIR/pytest-of-agent/` at any depth (`find <basetemp> -name owner_probe.log`); copy them
  out with a 1 s poll while pytest is still running - the owner dirs nest one level deeper
  than the basetemp root in pytest 9 (814's 194 DECISIONS entry has the full rig and its four
  failed attempts, so the first try is not the one that works).

## Hand-over

(2026-10-15, iteration 195, agent c - created, nothing built yet; the recipe above is complete.)
Claim steps: 1) on this branch verify the roman test is green in isolation (`.venv/bin/python -m
pytest tests/test_src_roman_maclauchlan.py -q -p no:cacheprovider`, 2 s) - if red, log it (230's
lane) and stop; 2) apply the recipe (the context lines match the current main file exactly; if
any hunk fails to apply, main has moved - stop and re-derive the diff against this branch's
file with `git diff main <the 814 fix commit> -- tests/test_owner_check.py` if it is reachable,
otherwise stop and ask); 3) run the pair 2-3 times (one invocation each), capturing the probe
logs; 4) compare the two runs' ten views (20-line PIL compare: count pixels differing by >32 on
any channel, report the fraction per view; A_4/A_5/B_4/B_5 must be byte-identical or <0.5%);
5) restore the re-rendered 307d PNGs (box 4); 6) one full-suite run (box 5); 7) claim done,
recording the run evidence in DECISIONS.

## Proposed changes (2026-10-15, iteration 242, agent a - task 814, which Depends on this)

The fix this task republishes is ALREADY ON MAIN - not via this task, but via the driver's
takeover-carry commit 693b0ea3 ("814 taken over from agent c: its work carried
(c@26853066)"), which landed agent c's 63a4e4e settle+subpixel diff (the recipe above, 54
lines) into main's tests/test_owner_check.py. Verified at it.242: `git diff main --
tests/test_owner_check.py` is 0/0 (main's file carries settle()/subpixel() at all eight
sites), and 814's re-verification on the current tree (= main in code) shows the fix
working: three unflagged pair runs green (70.39/75.11/69.70 s), zero [warn] settle, ratio
check [ok] in every captured probe log, all ten 307d views stable run-vs-run (worst
0.0447%, the card-view jitter band), full suite 194/1/0 all green (the roman red dead via
817/818). So this task's goal ("the pair is stable on every branch") is met, and its it.195
claim steps 2-6 (apply the recipe, pair runs, view compare, PNG restore, full suite) are
satisfied by that evidence - the recipe is now a 0/0 no-op (the it.195 hunk-failure escape
hatch lands in exactly this place: the context lines no longer match because the fix is
already applied).

Recommend: close this task as done via a no-op verification (the claiming agent confirms
the 0/0 diff and that the pair is green on main; no file changes needed). That unblocks
814's done-claim (its remaining dependency: this task). No code change is required anywhere.
