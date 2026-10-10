"""Public S3 buckets over plain HTTPS: list, size, whole-object download. No AWS libraries, no credentials.

Every open-data source in docs/sources.md that lives on S3 (USGS prd-tnm and usgs-lidar-public, the National
Library of Scotland tiles, Scotland's LiDAR, the open-lidar-data mirror, state imagery) is read through this.
Requester-pays buckets (NAIP, Landsat) answer 403 and are not usable.
"""
import http.client
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

UA = {"User-Agent": "ancient-works/0.1 (personal research)"}
NS = "{http://s3.amazonaws.com/doc/2006-03-01/}"


def host(bucket, region=None):
    return f"{bucket}.s3.{region + '.' if region else ''}amazonaws.com"


def url(bucket, key, region=None):
    return f"https://{host(bucket, region)}/{urllib.parse.quote(key, safe='/')}"


def ls(bucket, prefix="", delim="/", region=None, limit=10 ** 9):
    """List a prefix. Returns (sub-prefixes, [(key, size, yyyy-mm-dd)]); follows continuation tokens up to `limit` entries."""
    prefixes, keys, token = [], [], None
    while True:
        q = {"list-type": "2", "prefix": prefix, "max-keys": "1000"}
        if delim:
            q["delimiter"] = delim
        if token:
            q["continuation-token"] = token
        req = urllib.request.Request(f"https://{host(bucket, region)}/?" + urllib.parse.urlencode(q), headers=UA)
        root = ET.fromstring(urllib.request.urlopen(req, timeout=90).read())
        prefixes += [e.findtext(NS + "Prefix") for e in root.findall(NS + "CommonPrefixes")]
        keys += [(e.findtext(NS + "Key"), int(e.findtext(NS + "Size")), e.findtext(NS + "LastModified")[:10])
                 for e in root.findall(NS + "Contents")]
        token = root.findtext(NS + "NextContinuationToken")
        if root.findtext(NS + "IsTruncated") != "true" or len(prefixes) + len(keys) >= limit:
            return prefixes, keys


def size(u):
    """Content-Length of an object, or None when it does not exist (404/403)."""
    try:
        with urllib.request.urlopen(urllib.request.Request(u, method="HEAD", headers=UA), timeout=40) as r:
            return int(r.headers.get("Content-Length", 0))
    except urllib.error.HTTPError as e:
        if e.code in (403, 404):
            return None
        raise


def get(u, path=None, tries=5):
    """Whole object as bytes, or saved to `path`. Retries network errors (not 4xx); a file download is streamed to
    <path>.part and resumed with a Range request, so a dropped connection on a 200 MB object costs only the tail."""
    last = None
    have = 0
    chunks = []
    part = (path + ".part") if path else None
    if part:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        open(part, "wb").close()
    for i in range(tries):
        try:
            hdr = dict(UA)
            if have:
                hdr["Range"] = f"bytes={have}-"
            with urllib.request.urlopen(urllib.request.Request(u, headers=hdr), timeout=300) as r:
                if have and r.status != 206:  # server ignored the range: start over
                    have = 0
                    chunks.clear()
                    if part:
                        open(part, "wb").close()
                while True:
                    b = r.read(1 << 20)
                    if not b:
                        break
                    have += len(b)
                    if part:
                        with open(part, "ab") as f:
                            f.write(b)
                    else:
                        chunks.append(b)
            break
        except urllib.error.HTTPError as e:
            if e.code < 500:
                raise
            last = e
        except (urllib.error.URLError, TimeoutError, ConnectionError, http.client.HTTPException) as e:
            last = e
        if i == tries - 1:
            raise last
        time.sleep(2 * (i + 1))
    if part:
        os.replace(part, path)
        return path
    return b"".join(chunks)
