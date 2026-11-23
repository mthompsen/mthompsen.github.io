#!/usr/bin/env python3
"""Pre-render the portfolio so it works with JavaScript turned off.

app.html is the source page (it renders itself from data/portfolio.json with
JavaScript). This script loads it in headless Chrome, saves the finished HTML as
index.html, and writes one static page per project under projects/. The small
assets/site.js only adds extras: the theme toggle, the copy-email button, and a
redirect for old #project-<id> links.

Usage, from the repo root, after `bundle exec jekyll build`:
    python3 tools/prerender.py [--site _site] [--chrome google-chrome]
Then run `bundle exec jekyll build` again and commit index.html and projects/.
"""
import argparse, html, json, os, re, subprocess, sys, threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def serve(directory):
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=directory))
    SimpleHTTPRequestHandler.log_message = lambda *a: None
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd

def dump(chrome, url):
    out = subprocess.run([chrome, "--headless=new", "--no-sandbox", "--disable-gpu",
                          "--virtual-time-budget=10000", "--dump-dom", url],
                         capture_output=True, text=True, timeout=120)
    if "Featured projects" not in out.stdout:
        sys.exit(f"render failed for {url}")
    return out.stdout

def clean(doc, source_head_icon):
    doc = re.sub(r"<script\b[^>]*>.*?</script>", "", doc, flags=re.S)          # every script
    doc = re.sub(r'<html[^>]*>', '<html lang="en">', doc, count=1)               # drop the theme vars set at render time
    doc = re.sub(r'\s(?:data-dc-tpl|data-sc-name)="[^"]*"', "", doc)             # editor bookkeeping
    doc = re.sub(r'<link rel="icon"[^>]*>', source_head_icon, doc, count=1)      # the runtime rewrote the SVG favicon
    # theme toggle: the snapshot may be in light mode; ship the dark default
    doc = doc.replace('aria-label="Switch to dark mode" title="Switch to dark mode"',
                      'aria-label="Switch to light mode" title="Switch to light mode" data-theme-toggle=""')
    doc = doc.replace('aria-label="Switch to light mode" title="Switch to light mode" style',
                      'aria-label="Switch to light mode" title="Switch to light mode" data-theme-toggle="" style', 1)
    doc = re.sub(r'(data-theme-toggle=""[^>]*>\s*<i[^>]*class="ph )ph-(?:moon|sun)', r"\1ph-sun", doc, count=1)
    # buttons that need JavaScript are hidden until site.js runs
    doc = re.sub(r'<button([^>]*)>(\s*<i[^>]*ph-copy)', r'<button\1 data-copy-email="" data-js-only="">\2', doc, count=1)
    doc = doc.replace("data-theme-toggle=\"\"", "data-theme-toggle=\"\" data-js-only=\"\"", 1)
    # make sure every video can be played without JavaScript
    doc = re.sub(r"<video\b(?![^>]*\bcontrols\b)", "<video controls", doc)
    head_extra = ('<style>html:not(.js) [data-js-only]{display:none !important}</style>\n'
                  '<script src="assets/site.js"></script>\n</head>')
    return doc.replace("</head>", head_extra, 1)

def inner_of(doc, opening):
    """Inner HTML of the first element starting with `opening`, matching nested divs."""
    i = doc.find(opening)
    if i < 0:
        return None
    start = doc.index(">", i) + 1
    depth, pos = 1, start
    for m in re.finditer(r"<(/?)div\b[^>]*>", doc[start:]):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return doc[start:start + m.start()]
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default=os.path.join(ROOT, "_site"))
    ap.add_argument("--chrome", default="google-chrome")
    a = ap.parse_args()
    data = json.load(open(os.path.join(ROOT, "data", "portfolio.json")))
    src = open(os.path.join(ROOT, "app.html")).read()
    icon = re.search(r'<link rel="icon"[^>]*>', src).group(0)
    httpd = serve(a.site)
    base = f"http://127.0.0.1:{httpd.server_address[1]}/app.html"

    # home page
    home = clean(dump(a.chrome, base), icon)
    ids = [p["id"] for p in data["featured"]]
    btns = list(re.finditer(r'<button([^>]*)aria-haspopup="dialog"([^>]*)>(.*?)</button>', home, flags=re.S))
    assert len(btns) == len(ids), (len(btns), ids)
    for m, pid in reversed(list(zip(btns, ids))):
        attrs = (m.group(1) + m.group(2)).replace('type="button"', "").strip()
        home = home[:m.start()] + f'<a {attrs} href="projects/{pid}.html">{m.group(3)}</a>' + home[m.end():]
    open(os.path.join(ROOT, "index.html"), "w").write(home)

    # one page per project, built from that project's panel
    os.makedirs(os.path.join(ROOT, "projects"), exist_ok=True)
    for p in data["featured"]:
        page = clean(dump(a.chrome, f"{base}#project-{p['id']}"), icon)
        inner = inner_of(page, '<div role="dialog"')
        if inner is None:
            sys.exit(f"panel not found for {p['id']}")
        inner = re.sub(r'<button[^>]*aria-label="Close project details"[^>]*>.*?</button>',
                       f'<a class="btn btn-secondary" href="index.html#card-{p["id"]}"><i class="ph ph-arrow-left" aria-hidden="true"></i>All projects</a>',
                       inner, count=1, flags=re.S)
        head = page[:page.index("<body")]
        title = f"{html.escape(p['name'])} · Mason Thompsen"
        head = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", head, count=1, flags=re.S)
        head = head.replace("<head>", '<head>\n<base href="../">', 1)
        body = ('<body><main style="min-height: 100vh; background: var(--color-bg); color: var(--color-text); font-family: var(--font-body);">'
                '<div style="max-width: 760px; margin: 0 auto; padding: clamp(24px, 5vw, 56px) clamp(20px, 5vw, 40px) 64px; display: grid; gap: 20px;">'
                f'{inner}</div></main></body></html>\n')
        open(os.path.join(ROOT, "projects", f"{p['id']}.html"), "w").write(head + body)
    httpd.shutdown()
    print("wrote index.html and", len(ids), "project pages")

if __name__ == "__main__":
    main()
