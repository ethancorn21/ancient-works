"""Assemble the publishable page: web/index.html with MapLibre CSS inlined -> dist/index.html, plus dist/data.

Also writes dist/preview.html (same page inside a full HTML skeleton) for local checks.
"""
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
web, dist = os.path.join(ROOT, "web"), os.path.join(ROOT, "dist")
page = open(os.path.join(web, "index.html")).read()
css = open(os.path.join(web, "vendor", "maplibre-gl-5.6.0.css")).read()
title_end = page.index("</title>") + len("</title>")
page = page[:title_end] + "\n<style>/* maplibre-gl 5.6.0 */\n" + css + "\n</style>" + page[title_end:]
if os.path.exists(os.path.join(dist, "data")):
    shutil.rmtree(os.path.join(dist, "data"))
os.makedirs(dist, exist_ok=True)
shutil.copytree(os.path.join(web, "data"), os.path.join(dist, "data"))
open(os.path.join(dist, "index.html"), "w").write(page)
skeleton = ('<!doctype html><html><head><meta charset=utf8><meta name=viewport content="width=device-width,'
            'initial-scale=1,viewport-fit=cover"><style>:root{color-scheme:light;padding:env(safe-area-inset-top,0) 0 '
            'env(safe-area-inset-bottom,0)}body{margin:0;font:14px system-ui}img{max-width:100%}[hidden]{display:none!important}'
            '</style></head><body>')
open(os.path.join(dist, "preview.html"), "w").write(skeleton + page + "</body></html>")
files = []
for d, _, fs in os.walk(os.path.join(dist, "data")):
    files += [os.path.relpath(os.path.join(d, f), dist) for f in fs]
total = sum(os.path.getsize(os.path.join(dist, f)) for f in files) // 1024
print("dist ready:", len(files), "data files,", total, "KB; page", len(page) // 1024, "KB")
