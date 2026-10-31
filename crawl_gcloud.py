#!/usr/bin/env python3
"""
Crawl https://docs.cloud.google.com/sdk/gcloud/reference and all nested traces,
saving every page as .md in gcloud_cli_data/
"""
import asyncio
import aiohttp
import re
import json
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import html2text

BASE_URL = "https://docs.cloud.google.com/sdk/gcloud/reference"
BASE_PREFIX = "/sdk/gcloud/reference"
DOMAIN = "docs.cloud.google.com"
OUT_DIR = Path("gcloud_cli_data")
OUT_DIR.mkdir(exist_ok=True)

CONCURRENCY = 15
TIMEOUT = 30
RETRIES = 3

h_converter = html2text.HTML2Text()
h_converter.ignore_links = False
h_converter.ignore_images = False
h_converter.body_width = 0
h_converter.ignore_emphasis = False

visited = set()
to_visit = asyncio.Queue()
# for manifest
results = []
failed = []

def url_to_filepath(url: str) -> Path:
    parsed = urlparse(url)
    path = parsed.path  # e.g. /sdk/gcloud/reference/compute/instances/create
    # strip prefix
    if path == "/sdk/gcloud/reference" or path == "/sdk/gcloud/reference/":
        return OUT_DIR / "gcloud.md"
    # remove leading /sdk/gcloud/reference/
    rel = path
    if rel.startswith(BASE_PREFIX):
        rel = rel[len(BASE_PREFIX):].lstrip("/")
    else:
        # fallback sanitize
        rel = rel.lstrip("/").replace("/", "_")
    if not rel:
        return OUT_DIR / "gcloud.md"
    # sanitize each part
    parts = []
    for p in rel.split("/"):
        # windows-safe
        p = re.sub(r'[<>:"/\\|?*]', '_', p).strip()
        if not p:
            continue
        # truncate long names
        if len(p) > 100:
            p = p[:100]
        parts.append(p)
    # hierarchical path + .md
    fp = OUT_DIR.joinpath(*parts).with_suffix(".md")
    return fp

async def fetch(session, url):
    last_err = None
    for attempt in range(RETRIES):
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as resp:
                if resp.status == 429:
                    wait = 2 ** attempt * 2
                    print(f"  429 rate-limit {url}, sleep {wait}s")
                    await asyncio.sleep(wait)
                    continue
                if resp.status != 200:
                    last_err = f"HTTP {resp.status}"
                    await asyncio.sleep(1)
                    continue
                text = await resp.text()
                return text
        except Exception as e:
            last_err = str(e)
            await asyncio.sleep(1 + attempt)
    return None

def extract_links_and_content(html: str, base_url: str):
    soup = BeautifulSoup(html, "html.parser")
    # title
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else base_url
    # main content
    main = soup.find("main") or soup.find("article") or soup.find("div", class_="devsite-article-body")
    if main is None:
        main = soup
    # links
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # skip anchors, mailto, javascript
        if href.startswith("#") or href.startswith("mailto:") or href.startswith("javascript:"):
            continue
        full = urljoin(base_url, href).split("#")[0].split("?")[0].rstrip("/")
        parsed = urlparse(full)
        if parsed.netloc != DOMAIN:
            continue
        # only follow /sdk/gcloud/reference*
        # normalize: remove trailing slash except root
        if parsed.path == BASE_PREFIX or parsed.path.startswith(BASE_PREFIX + "/"):
            # skip language variants? canonical is English; ignore hl params already stripped
            # normalize root trailing slash
            if full == "https://docs.cloud.google.com/sdk/gcloud/reference/":
                full = BASE_URL
            links.add(full)
    return title, main, links

def main_to_markdown(title, main_elem, url):
    # convert main inner HTML to markdown
    try:
        inner_html = str(main_elem)
        md_body = h_converter.handle(inner_html)
    except Exception as e:
        md_body = main_elem.get_text("\n", strip=False) if hasattr(main_elem, "get_text") else str(main_elem)
    # cleanup excessive blank lines
    md_body = re.sub(r"\n{3,}", "\n\n", md_body).strip()
    header = f"# {title}\n\n> Source: {url}\n\n---\n\n"
    return header + md_body + "\n"

async def worker(session, worker_id, progress):
    while True:
        try:
            url = await to_visit.get()
        except asyncio.CancelledError:
            break
        if url in visited:
            to_visit.task_done()
            continue
        visited.add(url)
        fp = url_to_filepath(url)
        # resume: skip if already exists and non-empty
        if fp.exists() and fp.stat().st_size > 500:
            # still need to parse links? If file exists, we still need links to continue crawl.
            # Fetch anyway? To save time, fetch only if we need links. But we can fetch to discover.
            # Optimization: if file exists, still fetch for link discovery but don't rewrite?
            # For speed, if file exists, try to read existing md for links? No, need HTML.
            # So we must fetch anyway for discovery unless we've already visited children.
            # Let's fetch anyway.
            pass

        html = await fetch(session, url)
        if html is None:
            print(f"[w{worker_id}] FAILED {url}")
            failed.append(url)
            to_visit.task_done()
            progress["failed"] += 1
            continue

        title, main_elem, links = extract_links_and_content(html, url)

        # save md
        try:
            fp.parent.mkdir(parents=True, exist_ok=True)
            md = main_to_markdown(title, main_elem, url)
            fp.write_text(md, encoding="utf-8")
            results.append({"url": url, "file": str(fp.as_posix()), "title": title})
            progress["done"] += 1
            if progress["done"] % 100 == 0:
                print(f"  ... progress: {progress['done']} saved, queue={to_visit.qsize()}, visited={len(visited)}, failed={progress['failed']}")
        except Exception as e:
            print(f"[w{worker_id}] WRITE-ERR {url} -> {fp}: {e}")
            failed.append(url)
            progress["failed"] += 1

        # enqueue new links
        new_count = 0
        for link in links:
            if link not in visited:
                # check if already queued? use visited as guard + a queued set
                # simple: if file for link already exists and we have visited? still need to avoid duplicate queue bloat
                # use a global queued set
                if link not in queued:
                    queued.add(link)
                    await to_visit.put(link)
                    new_count += 1

        to_visit.task_done()

async def main():
    global queued
    queued = set()
    await to_visit.put(BASE_URL)
    queued.add(BASE_URL)
    progress = {"done": 0, "failed": 0}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    connector = aiohttp.TCPConnector(limit=CONCURRENCY, ssl=True)
    async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
        workers = [asyncio.create_task(worker(session, i, progress)) for i in range(CONCURRENCY)]
        # wait until queue empty
        await to_visit.join()
        for w in workers:
            w.cancel()
        await asyncio.gather(*workers, return_exceptions=True)
    print(f"DONE. saved={progress['done']} failed={progress['failed']} visited={len(visited)}")
    # write manifest
    (OUT_DIR / "_manifest.json").write_text(json.dumps({"total": len(results), "failed": failed, "pages": results}, indent=2), encoding="utf-8")
    # write index.md
    idx_lines = ["# gcloud CLI Reference Index", "", f"Total pages: {len(results)}", "", f"Source root: {BASE_URL}", "", "## Pages", ""]
    for r in sorted(results, key=lambda x: x["url"]):
        rel = Path(r["file"]).relative_to(OUT_DIR).as_posix()
        idx_lines.append(f"- [{r['title']}]({rel}) — {r['url']}")
    (OUT_DIR / "_index.md").write_text("\n".join(idx_lines), encoding="utf-8")
    print(f"Manifest + index written. Files in {OUT_DIR}: {len(list(OUT_DIR.rglob('*.md')))}")

if __name__ == "__main__":
    asyncio.run(main())
