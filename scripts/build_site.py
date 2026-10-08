#!/usr/bin/env python3
"""Build the GitHub Pages site: copy every talk folder into _site/ and
generate a landing page that lists them.

A talk is any top-level folder (not starting with "." or "_", and not
"scripts"). Its link is index.html if present, otherwise the first PDF,
then the first PowerPoint file. Details come from an optional talk.json:

    {"title": "...", "presenter": "...", "date": "2026-10-09",
     "description": "..."}

Anything missing falls back to the page <title> or file name, and to the
date the folder was first committed.
"""
import html
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "_site"
SKIP = {"scripts"}


def first_commit_date(folder: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "log", "--diff-filter=A", "--format=%as", "--", folder.name],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.split()
        return out[-1] if out else ""
    except Exception:
        return ""


def pick_entry(folder: Path):
    if (folder / "index.html").exists():
        return "", "Slides"
    for pattern, kind in (("*.pdf", "PDF"), ("*.pptx", "PowerPoint"), ("*.ppt", "PowerPoint")):
        files = sorted(folder.glob(pattern))
        if files:
            return files[0].name, kind
    return None, None


def html_title(folder: Path) -> str:
    page = folder / "index.html"
    if not page.exists():
        return ""
    m = re.search(r"<title>(.*?)</title>", page.read_text(errors="ignore")[:8192], re.S | re.I)
    return m.group(1).strip() if m else ""


def talks():
    for folder in sorted(p for p in ROOT.iterdir() if p.is_dir()):
        if folder.name.startswith((".", "_")) or folder.name in SKIP:
            continue
        entry, kind = pick_entry(folder)
        if kind is None:
            continue
        meta = {}
        if (folder / "talk.json").exists():
            meta = json.loads((folder / "talk.json").read_text())
        title = meta.get("title") or html_title(folder) or (entry and Path(entry).stem) or folder.name
        yield {
            "folder": folder.name,
            "href": f"{folder.name}/{entry}",
            "kind": kind,
            "title": title,
            "presenter": meta.get("presenter", ""),
            "date": meta.get("date") or first_commit_date(folder),
            "description": meta.get("description", ""),
        }


def render(items) -> str:
    items = sorted(items, key=lambda t: t["date"], reverse=True)
    rows = []
    for t in items:
        e = {k: html.escape(v) for k, v in t.items()}
        by = " · ".join(x for x in (e["presenter"], e["date"]) if x)
        desc = f'<p class="desc">{e["description"]}</p>' if e["description"] else ""
        rows.append(
            f'<li><a href="{e["href"]}"><span class="kind">{e["kind"]}</span>'
            f'<span class="title">{e["title"]}</span></a>'
            f'<p class="by">{by}</p>{desc}</li>'
        )
    body = "\n".join(rows) or '<li class="empty">No talks yet.</li>'
    return f"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AIISC Presentations</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;600;700&family=JetBrains+Mono:wght@500;700&display=swap">
<style>
:root{{--bg:#E7EAE6;--fg:#111518;--muted:#525D66;--line:#C3C9C4;--card:#F7F8F5;--accent:#F2B705;--link:#2B59C3}}
@media (prefers-color-scheme:dark){{:root{{--bg:#111518;--fg:#E7EAE6;--muted:#9AA6AF;--line:#2A333B;--card:#1A2128;--link:#86A6F5;color-scheme:dark}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);font-family:'Public Sans',Arial,sans-serif;padding:0 16px}}
.strip{{background:var(--accent);color:#111518;font:700 13px/1 'JetBrains Mono',monospace;letter-spacing:.14em;text-transform:uppercase;padding:12px 16px;margin:0 -16px}}
main{{max-width:880px;margin:0 auto;padding:48px 0 80px}}
h1{{font-size:clamp(32px,6vw,52px);line-height:1.05;margin:0 0 10px}}
.lead{{color:var(--muted);font-size:18px;margin:0 0 36px}}
ul{{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:14px}}
li{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:20px 22px}}
li a{{display:flex;flex-direction:column;gap:6px;color:var(--fg);text-decoration:none}}
li a:hover .title,li a:focus-visible .title{{color:var(--link);text-decoration:underline}}
.kind{{font:700 12px 'JetBrains Mono',monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}}
.title{{font-size:22px;font-weight:700}}
.by{{margin:8px 0 0;color:var(--muted);font:500 14px 'JetBrains Mono',monospace}}
.desc{{margin:8px 0 0;line-height:1.5}}
.empty{{color:var(--muted)}}
footer{{margin-top:40px;color:var(--muted);font-size:14px}}
</style>
<p class="strip">AI Institute of South Carolina</p>
<main>
<h1>Presentations</h1>
<p class="lead">Talks and briefings from the AI Institute of South Carolina.</p>
<ul>
{body}
</ul>
<footer>To add a talk, see the <a href="https://github.com/usc-ai-institute/presentations#adding-a-talk">README</a>.</footer>
</main>
</html>
"""


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    items = list(talks())
    for t in items:
        shutil.copytree(ROOT / t["folder"], OUT / t["folder"])
    (OUT / "index.html").write_text(render(items))
    (OUT / ".nojekyll").write_text("")
    print(f"Built {len(items)} talk(s): " + ", ".join(t["folder"] for t in items))


if __name__ == "__main__":
    main()
