#!/usr/bin/env python3
"""Retry failed URLs + discover their children"""
import asyncio, aiohttp, re, json
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import html2text

BASE_PREFIX="/sdk/gcloud/reference"
DOMAIN="docs.cloud.google.com"
OUT_DIR=Path("gcloud_cli_data")
BASE_URL="https://docs.cloud.google.com/sdk/gcloud/reference"
CONCURRENCY=10
TIMEOUT=45
RETRIES=5

h=html2text.HTML2Text()
h.ignore_links=False
h.ignore_images=False
h.body_width=0

def url_to_fp(url):
    p=urlparse(url).path
    if p=="/sdk/gcloud/reference" or p=="/sdk/gcloud/reference/":
        return OUT_DIR/"gcloud.md"
    rel=p[len(BASE_PREFIX):].lstrip("/") if p.startswith(BASE_PREFIX) else p.lstrip("/").replace("/","_")
    parts=[re.sub(r'[<>:"/\\|?*]','_',x).strip()[:100] for x in rel.split("/") if x]
    return OUT_DIR.joinpath(*parts).with_suffix(".md")

def fp_to_url(fp):
    if fp.name in ("_index.md",): return None
    if fp.name=="gcloud.md" and len(fp.relative_to(OUT_DIR).parts)==1:
        return BASE_URL
    try:
        rel=fp.relative_to(OUT_DIR).with_suffix("").as_posix()
    except: return None
    if fp.suffix!=".md": return None
    return f"https://docs.cloud.google.com{BASE_PREFIX}/{rel}"

async def fetch(sess,url):
    for att in range(RETRIES):
        try:
            async with sess.get(url, timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as r:
                if r.status==429:
                    await asyncio.sleep(3**att+2)
                    continue
                if r.status!=200:
                    await asyncio.sleep(2)
                    continue
                return await r.text()
        except Exception:
            await asyncio.sleep(2+att*2)
    return None

def extract(html,base):
    soup=BeautifulSoup(html,"html.parser")
    t=soup.find("title")
    title=t.get_text(strip=True) if t else base
    main=soup.find("main") or soup.find("article") or soup
    links=set()
    for a in soup.find_all("a",href=True):
        href=a["href"]
        if href.startswith("#") or href.startswith("mailto:") or href.startswith("javascript:"): continue
        full=urljoin(base,href).split("#")[0].split("?")[0].rstrip("/")
        pr=urlparse(full)
        if pr.netloc!=DOMAIN: continue
        if pr.path==BASE_PREFIX or pr.path.startswith(BASE_PREFIX+"/"):
            if full.endswith("/sdk/gcloud/reference/"): full=BASE_URL
            links.add(full)
    return title,main,links

def wrap(title,main_elem,url):
    try: body=h.handle(str(main_elem))
    except: body=main_elem.get_text("\n") if hasattr(main_elem,"get_text") else str(main_elem)
    body=re.sub(r"\n{3,}","\n\n",body).strip()
    return f"# {title}\n\n> Source: {url}\n\n---\n\n{body}\n"

async def main():
    mf=json.loads((OUT_DIR/"_manifest.json").read_text(encoding="utf-8"))
    failed=mf.get("failed",[])
    print(f"Retrying {len(failed)} failed",flush=True)
    # saved urls
    saved=set()
    for f in OUT_DIR.rglob("*.md"):
        u=fp_to_url(f)
        if u: saved.add(u)
    print(f"saved {len(saved)}",flush=True)
    q=asyncio.Queue()
    queued=set()
    visited=set(saved)  # don't refetch successes; only failed + new
    # remove failed from visited so they get fetched
    for u in failed:
        if u in visited: visited.remove(u)
        if u not in queued:
            queued.add(u)
            await q.put(u)
    prog={"done":0,"new":0,"fail":0}
    new_failed=[]
    headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    conn=aiohttp.TCPConnector(limit=CONCURRENCY,ssl=True)
    async with aiohttp.ClientSession(headers=headers,connector=conn) as sess:
        async def worker(wid):
            while True:
                try: url=await q.get()
                except asyncio.CancelledError: break
                if url in visited:
                    q.task_done(); continue
                visited.add(url)
                html=await fetch(sess,url)
                if html is None:
                    print(f"FAIL {url}",flush=True)
                    new_failed.append(url); prog["fail"]+=1
                    q.task_done(); continue
                title,main_elem,links=extract(html,url)
                fp=url_to_fp(url)
                try:
                    fp.parent.mkdir(parents=True,exist_ok=True)
                    is_new=not (fp.exists() and fp.stat().st_size>500)
                    fp.write_text(wrap(title,main_elem,url),encoding="utf-8")
                    prog["done"]+=1
                    if is_new: prog["new"]+=1
                    if prog["done"]%100==0:
                        print(f"  retry progress done={prog['done']} new={prog['new']} fail={prog['fail']} q={q.qsize()} visited={len(visited)}",flush=True)
                except Exception as e:
                    print(f"write err {url}: {e}",flush=True)
                    new_failed.append(url); prog["fail"]+=1
                for l in links:
                    if l not in visited and l not in queued:
                        queued.add(l); await q.put(l)
                q.task_done()
        workers=[asyncio.create_task(worker(i)) for i in range(CONCURRENCY)]
        await q.join()
        for w in workers: w.cancel()
        await asyncio.gather(*workers,return_exceptions=True)
    print(f"RETRY DONE {prog} new_failed={len(new_failed)} visited={len(visited)}",flush=True)
    # rebuild manifest
    allf=list(OUT_DIR.rglob("*.md"))
    pages=[]
    for f in allf:
        if f.name=="_index.md": continue
        u=fp_to_url(f)
        if not u or f.suffix!=".md": continue
        try:
            txt=f.read_text(encoding="utf-8",errors="ignore")
            mm=re.search(r"^# (.+)$",txt,re.M)
            title=mm.group(1).strip() if mm else u
        except: title=u
        pages.append({"url":u,"file":f.as_posix(),"title":title})
    (OUT_DIR/"_manifest.json").write_text(json.dumps({"total":len(pages),"failed":new_failed,"pages":pages},indent=2),encoding="utf-8")
    idx=["# gcloud CLI Reference Index","","Total pages: "+str(len(pages)),"",f"Source root: {BASE_URL}","","## Pages",""]
    for r in sorted(pages,key=lambda x:x["url"]):
        rel=Path(r["file"]).relative_to(OUT_DIR).as_posix()
        idx.append(f"- [{r['title']}]({rel}) — {r['url']}")
    (OUT_DIR/"_index.md").write_text("\n".join(idx),encoding="utf-8")
    print(f"manifest rebuilt md={len(allf)} pages={len(pages)}",flush=True)

if __name__=="__main__":
    import asyncio; asyncio.run(main())
