# Presentations

Talks and briefings from the AI Institute of South Carolina.

**View them at https://usc-ai-institute.github.io/presentations/**

## Adding a talk

1. Make a folder at the top level, named in lowercase with hyphens, e.g. `rag-for-agencies`. Its name becomes the link: `usc-ai-institute.github.io/presentations/rag-for-agencies/`.
2. Put your talk in it:
   - an HTML deck saved as `index.html` (images, CSS and scripts can sit beside it), **or**
   - a `.pdf`, **or**
   - a `.pptx` (viewers will download it; a PDF export opens in the browser).
3. Optional: add a `talk.json` so the listing shows your details:
   ```json
   {
     "title": "RAG for State Agencies",
     "presenter": "Your Name",
     "date": "2026-11-12",
     "description": "One sentence about the talk."
   }
   ```
   Without it, the title comes from the page `<title>` or the file name, and the date from when the folder was first added.
4. Commit and push to `main` (or open a pull request). The site rebuilds in about a minute and your talk appears on the landing page.

Don't put anything here you wouldn't show publicly: this repo and its site are public. Keep out passwords, API keys, server addresses, and any participant, student or patient data.

## How it works

`.github/workflows/pages.yml` runs `scripts/build_site.py` on every push to `main`. The script copies each talk folder into the site and writes the landing page from what it finds. Folders starting with `.` or `_`, and `scripts/`, are ignored. To preview locally:

```bash
python3 scripts/build_site.py && python3 -m http.server -d _site 8000
```
