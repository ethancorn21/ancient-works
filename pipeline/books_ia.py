"""Internet Archive helpers for the book index: metadata, BookReader page list, OCR text, page images.

Polite by design: one User-Agent, retries with backoff, everything cached on disk under data/raw/books/,
so every step can be re-run and resumes where it stopped.

Leaf convention (same as the fitted plates, e.g. Squier & Davis Plate XXV = leaf n161):
    n        0-based index into the BookReader page list = the `page/n{N}.jpg` endpoint
    leafNum  number of the jp2 file inside <id>_jp2.zip (differs from n when pages are skipped)
    pageNum  printed page number, when IA's scandata has one
"""
import json
import os
import time
import urllib.parse
import urllib.request

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
RAW = os.path.join(ROOT, "data", "raw", "books")
UA = {"User-Agent": "ancient-works/0.2 (personal research)"}


def get(url, tries=5, timeout=60):
    """GET with backoff on errors and 429/5xx. Returns bytes."""
    last = None
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (400, 401, 403, 404):
                raise
        except Exception as e:  # timeouts, resets
            last = e
        print(f"  retry {i + 1}/{tries} after {last!r:.120} for {url[:100]}", flush=True)
        time.sleep(min(60, 4 * 2 ** i))
    raise last


def cached(path, url, binary=True):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        body = get(url)
        tmp = path + ".part"
        with open(tmp, "wb") as f:
            f.write(body)
        os.replace(tmp, path)
    with open(path, "rb") as f:
        b = f.read()
    return b if binary else b.decode("utf-8", "replace")


def metadata(ia_id):
    return json.loads(cached(os.path.join(RAW, ia_id, "metadata.json"), f"https://archive.org/metadata/{ia_id}"))


def pages(ia_id):
    """Flat BookReader page list; list index == n of page/n{N}.jpg."""
    path = os.path.join(RAW, ia_id, "bookreader.json")
    if not os.path.exists(path):
        md = metadata(ia_id)
        q = urllib.parse.urlencode({"id": ia_id, "itemPath": md["dir"], "server": md["d1"], "format": "json",
                                    "subPrefix": ia_id})
        cached(path, f"https://{md['d1']}/BookReader/BookReaderJSIA.php?{q}")
    d = json.load(open(path))
    opts = d["data"]["brOptions"]
    flat = [p for spread in opts["data"] for p in spread]
    for n, p in enumerate(flat):
        p["n"] = n
    return flat


def djvu_txt(ia_id):
    """IA's full OCR text (pages separated by form feeds in most items)."""
    md = metadata(ia_id)
    names = [f["name"] for f in md["files"]]
    name = ia_id + "_djvu.txt" if ia_id + "_djvu.txt" in names else next(n for n in names if n.endswith("_djvu.txt"))
    return cached(os.path.join(RAW, ia_id, name), f"https://archive.org/download/{ia_id}/{urllib.parse.quote(name)}",
                  binary=False)


def page_image_url(page, scale=1):
    """BookReaderImages.php URL for one page; scale k returns about 1/k of full size (k=1: full)."""
    u = page["uri"]
    return u + ("&scale=%d&rotate=0" % scale if scale > 1 else "")


def full_url(ia_id, n):
    """Stable public URL of the full-resolution page image."""
    return f"https://archive.org/download/{ia_id}/page/n{n}.jpg"


def triage_scale(page, long_side=1400):
    """Smallest integer reduction that keeps the long side at or above ~long_side*0.85."""
    L = max(page["width"], page["height"])
    k = max(1, int(L / long_side + 0.15))
    return k


def page_texts(ia_id):
    """IA OCR text per page, keyed by leafNum (hOCR page i == jp2 leaf i; verified per book in books.py check)."""
    import gzip
    d = os.path.join(RAW, ia_id)
    pi = json.loads(gzip.decompress(cached(os.path.join(d, "hocr_pageindex.json.gz"),
                                           f"https://archive.org/download/{ia_id}/{ia_id}_hocr_pageindex.json.gz")))
    txt = gzip.decompress(cached(os.path.join(d, "hocr_searchtext.txt.gz"),
                                 f"https://archive.org/download/{ia_id}/{ia_id}_hocr_searchtext.txt.gz")).decode("utf-8", "replace")
    return {i: txt[a:b] for i, (a, b, *_rest) in enumerate(pi)}
