#!/usr/bin/env python3
"""Resume crawl: efficiently continue from existing files in gcloud_cli_data/"""
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

CONCURRENCY = 30
TIMEOUT = 30
RETRIES = 3

h_converter = html2text.HTML2Text()
h_converter.ignore_links = False
h_converter.ignore_images = False
h_converter.body_width = 0

def url_to_filepath(url: str) -> Path:
    parsed = urlparse(url)
    path = parsed.path
    if path == "/sdk/gcloud/reference" or path == "/sdk/gcloud/reference/":
        return OUT_DIR / "gcloud.md"
    rel = path
    if rel.startswith(BASE_PREFIX):
        rel = rel[len(BASE_PREFIX):].lstrip("/")
    else:
        rel = rel.lstrip("/").replace("/", "_")
    if not rel:
        return OUT_DIR / "gcloud.md"
    parts = []
    for p in rel.split("/"):
        p = re.sub(r'[<>:"/\\|?*]', '_', p).strip()
        if not p:
            continue
        if len(p) > 100:
            p = p[:100]
        parts.append(p)
    return OUT_DIR.joinpath(*parts).with_suffix(".md")

def filepath_to_url(fp: Path):
    if fp.name in ("_index.md", "_manifest.json"):
        return None
    if fp.name == "gcloud.md" and len(fp.relative_to(OUT_DIR).parts) == 1:
        return BASE_URL
    rel = fp.relative_to(OUT_DIR).with_suffix("").as_posix()
    return f"https://docs.cloud.google.com{BASE_PREFIX}/{rel}"

def is_group_url(url: str, fp: Path) -> bool:
    # directory sibling exists => known group
    sibling_dir = fp.with_suffix("")
    if sibling_dir.is_dir():
        return True
    # depth heuristic: depth 1-2 always refetch (they are groups or may have missing children)
    parsed = urlparse(url)
    rel = parsed.path[len(BASE_PREFIX):].lstrip("/") if parsed.path.startswith(BASE_PREFIX) else ""
    if not rel:
        return True
    depth = len([p for p in rel.split("/") if p])
    if depth <= 2:
        return True
    return False

async def fetch(session, url):
    for attempt in range(RETRIES):
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as resp:
                if resp.status == 429:
                    await asyncio.sleep(2 ** attempt * 2)
                    continue
                if resp.status != 200:
                    await asyncio.sleep(1)
                    continue
                return await resp.text()
        except Exception:
            await asyncio.sleep(1 + attempt)
    return None

def extract(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else base_url
    main = soup.find("main") or soup.find("article") or soup
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("#") or href.startswith("mailto:") or href.startswith("javascript:"):
            continue
        full = urljoin(base_url, href).split("#")[0].split("?")[0].rstrip("/")
        parsed = urlparse(full)
        if parsed.netloc != DOMAIN:
            continue
        if parsed.path == BASE_PREFIX or parsed.path.startswith(BASE_PREFIX + "/"):
            if full.endswith("/sdk/gcloud/reference/"):
                full = BASE_URL
            links.add(full)
    return title, main, links

def md_wrap(title, main_elem, url):
    try:
        body = h_converter.handle(str(main_elem))
    except Exception:
        body = main_elem.get_text("\n") if hasattr(main_elem, "get_text") else str(main_elem)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    return f"# {title}\n\n> Source: {url}\n\n---\n\n{body}\n"

async def main():
    # scan existing
    existing_files = list(OUT_DIR.rglob("*.md"))
    saved_urls = set()
    for f in existing_files:
        u = filepath_to_url(f)
        if u:
            saved_urls.add(u)
    print(f"Existing files: {len(existing_files)}, saved_urls: {len(saved_urls)}", flush=True)

    visited = set()
    queued = set()
    to_visit = asyncio.Queue()
    results = []  # will reload at end from disk
    failed = []
    progress = {"done": 0, "skipped": 0, "failed": 0, "new": 0}

    # Decide what to queue for refetch (groups) vs mark done (leaves)
    refetch = set()
    for u in saved_urls:
        fp = url_to_filepath(u)
        if is_group_url(u, fp):
            refetch.add(u)
        else:
            visited.add(u)  # leaf, don't refetch
    # always include root
    refetch.add(BASE_URL)
    print(f"Refetch groups: {len(refetch)}, skip leaves: {len(visited)}", flush=True)
    for u in refetch:
        if u not in queued:
            queued.add(u)
            await to_visit.put(u)

    async def worker(wid):
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
            # if leaf already saved, skip fetch (should already be in visited, but double-check)
            if fp.exists() and fp.stat().st_size > 500 and url not in refetch:
                progress["skipped"] += 1
                to_visit.task_done()
                continue
            html = await fetch(session, url)
            if html is None:
                failed.append(url)
                progress["failed"] += 1
                to_visit.task_done()
                continue
            title, main_elem, links = extract(html, url)
            try:
                fp.parent.mkdir(parents=True, exist_ok=True)
                is_new = not (fp.exists() and fp.stat().st_size > 500)
                fp.write_text(md_wrap(title, main_elem, url), encoding="utf-8")
                progress["done"] += 1
                if is_new:
                    progress["new"] += 1
                if progress["done"] % 100 == 0:
                    print(f"  progress saved={progress['done']} new={progress['new']} failed={progress['failed']} queue={to_visit.qsize()} visited={len(visited)}", flush=True)
            except Exception as e:
                print(f"[w{wid}] write err {url}: {e}", flush=True)
                failed.append(url)
                progress["failed"] += 1
            for link in links:
                if link not in visited and link not in queued:
                    queued.add(link)
                    await to_visit.put(link)
            to_visit.task_done()

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    connector = aiohttp.TCPConnector(limit=CONCURRENCY, ssl=True)
    async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
        nonlocal_vars = {"session": session}
        # bind session for worker closure
        globals()["session"] = session
        workers = [asyncio.create_task(worker(i)) for i in range(CONCURRENCY)]
        await to_visit.join()
        for w in workers:
            w.cancel()
        await asyncio.gather(*workers, return_exceptions=True)

    print(f"DONE saved_ops={progress} visited={len(visited)} failed={len(failed)}", flush=True)
    # rebuild manifest from disk
    all_files = list(OUT_DIR.rglob("*.md"))
    pages = []
    for f in all_files:
        if f.name in ("_index.md",):
            continue
        u = filepath_to_url(f)
        if not u:
            continue
        # title = first line
        try:
            txt = f.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r"^# (.+)$", txt, re.M)
            title = m.group(1).strip() if m else u
        except Exception:
            title = u
        pages.append({"url": u, "file": f.as_posix(), "title": title})
    (OUT_DIR / "_manifest.json").write_text(json.dumps({"total": len(pages), "failed": failed}, indent=2), encoding="utf-8")
    idx = ["# gcloud CLI Reference Index", "", f"Total pages: {len(pages)}", "", f"Source root: {BASE_URL}", "", "## Pages", ""]
    for r in sorted(pages, key=lambda x: x["url"]):
        rel = Path(r["file"]).relative_to(OUT_DIR).as_posix()
        idx.append(f"- [{r['title']}]({rel}) — {r['url']}")
    (OUT_DIR / "_index.md").write_text("\n".join(idx), encoding="utf-8")
    (OUT_DIR / "_manifest.json").write_text(json.dumps({"total": len(pages), "failed": failed, "pages": pages}, indent=2), encoding="utf-8")
    print(f"Manifest+index written. md count={len(all_files)}", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
