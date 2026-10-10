"""Index of the EBA strip archives on Zenodo: strip file name -> zip URL (reads only each zip's central directory).

usage: amazon_index.py   -> data/finder/amazon/eba_index.json
"""
import json
import os
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import remote_zip  # noqa: E402

RECORDS = {"7636454": None, "7689693": None, "7689210": None, "7689909": None}  # L1A deposits (all states)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    import urllib.request
    import aw
    out = {}
    for rec in RECORDS:
        with urllib.request.urlopen(urllib.request.Request(f"https://zenodo.org/api/records/{rec}", headers=aw.UA)) as r:
            files = json.load(r)["files"]
        for f in files:
            if not f["key"].endswith(".zip"):
                continue
            url = f"https://zenodo.org/api/records/{rec}/files/{urllib.parse.quote(f['key'])}/content"
            for i in remote_zip.open_zip(url).infolist():
                if i.filename.lower().endswith(".laz"):
                    out[os.path.basename(i.filename)] = {"zip": url, "member": i.filename, "mb": round(i.file_size / 1e6, 1)}
            print(f["key"], len(out), flush=True)
    p = os.path.join(ROOT, "data", "finder", "amazon", "eba_index.json")
    json.dump(out, open(p, "w"), indent=0)
    print(len(out), "strips ->", p)


if __name__ == "__main__":
    main()
