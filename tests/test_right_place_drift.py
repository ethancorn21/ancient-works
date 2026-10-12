"""Pin tools/right_place.py's verbatim matcher core against pipeline/books_match.py (task 309).

The region between the two "# =====" VERBATIM marker lines in tools/right_place.py is a
copy of the matcher's word-rule core from pipeline/books_match.py. This test extracts
each of that region's top-level blocks (by name) and asserts the exact block text occurs
in pipeline/books_match.py: it fails when the copy drifts from the source, or the source
drifts from the copy. If it fails, the fix belongs in pipeline/books_match.py (the
single source of truth for the matcher's word rules) - or in restoring the copy - never
in editing this list or the other file's rules to make the check pass.

Hermetic: two file reads, stdlib only, no network, no writes.
"""
import re

import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RIGHT_PLACE = ROOT / "tools" / "right_place.py"
BOOKS_MATCH = ROOT / "pipeline" / "books_match.py"

START_MARK = "the following blocks are copied VERBATIM from pipeline/books_match.py"
END_MARK = "end of the verbatim core"

# The top-level names in the verbatim region, in order. (SUFFIX, an 18th block between
# norm and name_keys, is deliberately not pinned here.)
NAMES = (
    "US_STATES", "ABBR", "UK_ABBR", "UK_COUNTIES", "GENERIC",
    "norm", "name_keys", "tokens", "place_of", "site_place", "site_toks",
    "name_lookup_keys", "row_inputs", "score_candidate",
    "BOOK_SCOPE", "PLACE_WORDS", "phrases",
)


def _marker_index(lines, mark):
    hits = [i for i, line in enumerate(lines) if mark in line]
    assert len(hits) == 1, "expected exactly one %r marker line in tools/right_place.py, found %d" % (mark, len(hits))
    return hits[0]


def _block_lines(lines, name, lo, hi):
    """The top-level block for name in lines[lo:hi]: from its def/assignment line until
    the next top-level (non-blank, non-indented) line."""
    pattern = re.compile(r"^(?:def\s+%s\s*\(|%s\s*=)" % (re.escape(name), re.escape(name)))
    starts = [i for i in range(lo, hi) if pattern.match(lines[i])]
    assert len(starts) == 1, "%s: %d top-level statements in the verbatim region, expected exactly 1" % (name, len(starts))
    end = starts[0] + 1
    while end < hi and (not lines[end].strip() or lines[end][:1] in (" ", "\t")):
        end += 1
    return lines[starts[0]:end]


@pytest.mark.parametrize("name", NAMES)
def test_verbatim_block_matches_books_match(name):
    right = RIGHT_PLACE.read_text(encoding="utf-8").splitlines()
    si = _marker_index(right, START_MARK)
    ei = _marker_index(right, END_MARK)
    assert si < ei, "the verbatim region markers are out of order"
    block = "\n".join(_block_lines(right, name, si, ei + 1))
    books = BOOKS_MATCH.read_text(encoding="utf-8")
    assert block in books, (
        "the verbatim core drifted: the %s block of tools/right_place.py no longer "
        "occurs byte-identical in pipeline/books_match.py" % name
    )
