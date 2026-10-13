#!/usr/bin/env python3
"""One-off fixture recorder for tests/test_matchfit_station.py (task 302f, working phase).

Records, against the LIVE ELoFTR (127.0.0.1:8091 by default; RoMa stays out: the test pins
ROMA_URL at a dead port), the raw /match responses for every (plan crop, ground window) pair of
badbury-rings-q798831's fit_row - keyed by the sha256 of the exact request body matchfit.match
sends - and then replays them offline through the real tools/site_done.py code on throwaway
copies of the site's files, recording the exact expected output of both branches.

Usage:  .venv/bin/python tests/fixtures/matchfit_station/record.py

Produces (committed, then the test needs no network):
  records.json         confident replay: the live responses + the line's expected stdout,
                       document, depictions entry, spread values and guard verdict
  records_unsure.json  the same with the >=10-inlier responses' ground keypoints permuted, so
                       the judge's 10-inlier bar is missed: expected stdout, review item, counts

The key scheme is the fixture's contract (tests/test_matchfit_station.py serves these records
from an in-process stub keyed the same way): sha256 of the POST body exactly as matchfit.match
builds it, json.dumps({"image0": <b64 PNG of the plan crop>, "image1": <b64 PNG of the ground
window>, "threshold": 0.2, "max_side": 1024}). Same .venv PIL on both sides => same PNG bytes =>
same key; a drifted request 500s and the test's stderr == "" assertion fails loudly.
"""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import shutil
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "fit"))
sys.path.insert(0, str(ROOT / "pipeline"))

import matchfit as mf  # noqa: E402
import matchfit_holdout_dummy  # noqa: F401  (placeholder never used; kept out)
