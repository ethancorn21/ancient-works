"""Read members of a large remote .zip (Zenodo serves byte ranges) without downloading the whole archive.

usage: remote_zip.py list <url> [pattern]            member names and sizes (reads only the central directory)
       remote_zip.py get <url> <member> <out_path>     one member to a local file

Why: the Amazon LiDAR deposits (EBA transects, SFB forest concessions) are 5-35 GB zips of many files; the Finder
needs a few ground models out of each.
"""
import io
import os
import re
import sys
import time
import urllib.request
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aw  # noqa: E402


class HttpFile(io.RawIOBase):
    """Seekable read-only file over HTTP Range requests, with a small read-ahead block cache."""

    def __init__(self, url, block=1 << 20):
        self.url, self.pos, self.block, self.cache = url, 0, block, {}
        req = urllib.request.Request(url, method="HEAD", headers=aw.UA)
        with urllib.request.urlopen(req, timeout=60) as r:
            self.url = r.geturl()  # follow Zenodo's redirect once
            self.size = int(r.headers["Content-Length"])

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, off, whence=0):
        self.pos = {0: off, 1: self.pos + off, 2: self.size + off}[whence]
        return self.pos

    def _range(self, a, b):
        for k in range(5):
            try:
                req = urllib.request.Request(self.url, headers=dict(aw.UA, Range=f"bytes={a}-{b - 1}"))
                with urllib.request.urlopen(req, timeout=120) as r:
                    return r.read()
            except Exception:
                if k == 4:
                    raise
                time.sleep(3 * (k + 1))

    def read(self, n=-1):
        if n < 0:
            n = self.size - self.pos
        n = max(0, min(n, self.size - self.pos))
        if n > 4 * self.block:  # big reads (member data) go straight through
            data = self._range(self.pos, self.pos + n)
        else:
            out = bytearray()
            p = self.pos
            while len(out) < n:
                i = p // self.block
                if i not in self.cache:
                    if len(self.cache) > 64:
                        self.cache.clear()
                    self.cache[i] = self._range(i * self.block, min(self.size, (i + 1) * self.block))
                blk = self.cache[i]
                take = blk[p - i * self.block: p - i * self.block + n - len(out)]
                out += take
                p += len(take)
            data = bytes(out)
        self.pos += len(data)
        return data

    def readinto(self, b):
        d = self.read(len(b))
        b[:len(d)] = d
        return len(d)


def open_zip(url):
    return zipfile.ZipFile(io.BufferedReader(HttpFile(url), buffer_size=1 << 20))


def get(url, member, out):
    z = open_zip(url)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with z.open(member) as src, open(out + ".part", "wb") as dst:
        while True:
            b = src.read(8 << 20)
            if not b:
                break
            dst.write(b)
    os.replace(out + ".part", out)


if __name__ == "__main__":
    cmd, url = sys.argv[1], sys.argv[2]
    if cmd == "list":
        pat = re.compile(sys.argv[3]) if len(sys.argv) > 3 else None
        for i in open_zip(url).infolist():
            if not pat or pat.search(i.filename):
                print(f"{i.file_size / 1e6:10.1f} MB  {i.compress_size / 1e6:10.1f} MB  {i.filename}")
    elif cmd == "get":
        get(url, sys.argv[3], sys.argv[4])
