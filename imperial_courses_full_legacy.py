# -*- coding: utf-8 -*-
"""
imperial_courses_full_legacy.py
Imperial College course crawler — legacy edition with improved overview & tab text extraction
"""

import re, os, sys, csv, json, time, logging
from urllib.parse import urljoin
from typing import Optional
from bs4 import BeautifulSoup
from bs4.element import Tag

# Selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

try:
    from ftfy import fix_text
except Exception:
    def fix_text(s): return s

# ------------------------------------------------------

def setup_logging(level: str, log_file: Optional[str] = None):
    lvl = getattr(logging, level.upper(), logging.INFO)
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    logging.basicConfig(level=lvl, format="%(asctime)s [%(levelname)s] %(message)s", handlers=handlers)
    return logging.getLogger("imperial")

def ensure_dir(p): os.makedirs(p, exist_ok=True) if p else None

def save_text(d, n, c):
    if not d: return
    ensure_dir(d)
    with open(os.path.join(d, n), "w", encoding="utf-8") as f:
        f.write(c)

def clean_url(u): return u.split("#")[0].rstrip("/")

def expand_pages(spec: str):
    out = []
    for seg in spec.split(","):
        seg = seg.strip()
        if not seg: continue
        if "-" in seg:
            a, b = seg.split("-")
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(seg))
    return sorted(set(out))

# ------------------------------------------------------

def collect_links(log, base_url, pages, debug_dir):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox"); options.add_argument("--disable-gpu"); options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    found = set()
    try:
        for n in pages:
            url = re.sub(r"([?&])page=\d+", rf"\1page={n}", base_url) if "page=" in base_url else (base_url + ("&" if "?" in base_url else "?") + f"page={n}")
            log.info(f"[SEARCH] visiting page {n}: {url}")
            driver.get(url)
            time.sleep(2)
            for _ in range(6):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(0.7)
            html = driver.page_source
            save_text(debug_dir, f"search_page_{n}.html", html)
            soup = BeautifulSoup(html, "lxml")
            for a in soup.select(".course-card__image a, .course-card h3 a, .course-card h4 a"):
                href = a.get("href")
                if not href: continue
                absu = clean_url(urljoin(url, href))
                if re.search(r"/study/courses/(undergraduate|postgraduate-taught)/", absu):
                    found.add(absu)
            log.info(f"[SEARCH] page {n}: total {len(found)} links")
    finally:
        driver.quit()
    links = sorted(found)
    save_text(debug_dir, "links.json", json.dumps(links, indent=2))
    return links

# ------------------------------------------------------

def fetch_html(url, log, debug_dir):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox"); options.add_argument("--disable-gpu"); options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    try:
        log.debug(f"[DETAIL] GET {url}")
        driver.get(url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".course-intro, .lead, .course-content, .tabs-tab-list"))
        )
        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.8)
        html = driver.page_source
        safe_name = re.sub(r"[^a-z0-9]+","_", url.lower())[:80]
        save_text(debug_dir, f"detail_{safe_name}.html", html)
        return html
    finally:
        driver.quit()

# ------------------------------------------------------
# 🆕 改进：把 overview 的所有 <p> 合并抓全（优先 Default 选项）
def parse_overview(soup: BeautifulSoup) -> str:
    """
    精准抓取：Course overview 标题所在的 .course-content 下，
    .course-content__wide > .js-course-selector-content[data-content-value="Default"] 内的所有 <p>。
    失败时再按旧逻辑兜底。
    """
    def join_ps(ps):
        return fix_text(" ".join([p.get_text(" ", strip=True) for p in ps if p.get_text(strip=True)]))

    text = ""

    # 1) 锚定到 h2.s-h4 == "Course overview" 的父级 .course-content
    h2s = soup.select("h2.s-h4")
    target_cc = None
    for h2 in h2s:
        if h2.get_text(strip=True).lower() == "course overview":
            # 寻找最近的 .course-content 容器
            cc = h2.find_parent(class_="course-content")
            if cc:
                target_cc = cc
                break

    if target_cc:
        # 优先：.course-content__wide > .js-course-selector-content[data-content-value="Default"]
        block = target_cc.select_one(".course-content__wide > .js-course-selector-content[data-content-value='Default']")
        if not block:
            # 次选：该 .course-content 内第一个 .js-course-selector-content（有些页面没有 data-content-value）
            block = target_cc.select_one(".course-content__wide > .js-course-selector-content")
        if block:
            ps = block.find_all("p")
            if ps:
                text = join_ps(ps)

    # 2) 如果还没有，兜底为：全页第一个 Default 的 js-course-selector-content
    if not text:
        block = soup.select_one(".js-course-selector-content[data-content-value='Default']")
        if block:
            ps = block.find_all("p")
            if ps:
                text = join_ps(ps)

    # 3) 再兜底：.course-intro / .lead（兼容旧站）
    if not text:
        for sel in [".course-intro", ".lead"]:
            el = soup.select_one(sel)
            if el:
                ps = el.find_all("p")
                if ps:
                    text = join_ps(ps)
                    break
                # 没有 <p> 时取整个块文本
                raw = el.get_text(" ", strip=True)
                if raw:
                    text = fix_text(raw)
                    break

    # 4) 最后兜底：第一个 .course-content 里取前若干段（避免抓到模块说明过多）
    if not text:
        main = soup.select_one(".course-content")
        if main:
            ps = main.find_all("p")
            if ps:
                text = join_ps(ps[:6])

    return text


def parse_keyfacts(soup: BeautifulSoup) -> dict:
    data = {
        "qualification": "",
        "duration": "",
        "start_date": "",
        "ucas_code": "",
        "study_mode": "",
        "delivered_by": "",
        "delivered_by_link": ""
    }
    facts = soup.select_one(".course-key-facts__items")
    if not facts:
        return data

    for li in facts.find_all("li", recursive=False):
        h3 = li.find("h3")
        if not h3:
            continue
        key = h3.get_text(" ", strip=True).lower()

        raw_text = li.get_text(" ", strip=True)
        ktxt = h3.get_text(" ", strip=True)
        val = fix_text(raw_text.replace(ktxt, "", 1).strip())

        if "qualification" in key:
            data["qualification"] = val
        elif "duration" in key:
            data["duration"] = val
        elif "start date" in key or key.startswith("start"):
            data["start_date"] = val
        elif "ucas" in key:
            data["ucas_code"] = val
        elif "study mode" in key:
            data["study_mode"] = val
        elif "delivered by" in key:
            data["delivered_by"] = val
            a = li.find("a")
            if a and a.get("href"):
                data["delivered_by_link"] = a["href"]
    return data

# 🆕 工具：获取元素内所有 <p> 的纯文本（可选过滤掉手风琴面板内的段落）
def collect_paragraphs(root: Tag, exclude_accordion_panels: bool = True) -> list[str]:
    if not root:
        return []
    ps = []
    for p in root.find_all("p"):
        if exclude_accordion_panels:
            panel = p.find_parent(class_="accordion__panel")
            if panel is not None:
                continue
        t = p.get_text(" ", strip=True)
        if t:
            ps.append(fix_text(t))
    return ps

# 🆕 改进：每个 tab 下除了组（h3→accordion），还会抓取 tab 自身的说明文本（overview）
def parse_structure(soup: BeautifulSoup) -> dict:
    out = {}
    # 所有 tab 锚点（a role=tab）
    for a in soup.select(".tabs-tab-list a.tabs-trigger.js-tabs-trigger, a[role='tab'].js-tabs-trigger"):
        tab = fix_text(a.get_text(" ", strip=True))
        href = a.get("href", "")
        if not href.startswith("#"):
            continue
        sec = soup.select_one(href)
        if not sec:
            continue

        # 1) 先抓 tab 自身的说明性段落（不含手风琴面板里的）
        tab_overview_ps = collect_paragraphs(sec, exclude_accordion_panels=True)
        tab_overview = " ".join(tab_overview_ps) if tab_overview_ps else ""

        # 2) 再按 h3 分组抓手风琴模块
        groups = {}
        # 有些页面 h3 在 .course-content__wide 中；统一从当前 tab 的 section 内搜
        for h3 in sec.find_all("h3"):
            group_name = fix_text(h3.get_text(" ", strip=True))
            items = []
            # 绑定到紧随其后的第一个 .accordion
            acc = h3.find_next("div", class_="accordion")
            if acc and acc.find_previous("h3") == h3:
                for h4 in acc.find_all("h4", class_="accordion__selector"):
                    title_node = h4.select_one(".accordion__title span") or h4.select_one(".accordion__title")
                    title = fix_text(title_node.get_text(" ", strip=True)) if title_node else ""
                    desc = ""
                    # 通过 aria-controls 找到面板
                    btn = h4.find("button", {"aria-controls": True})
                    if btn:
                        pid = btn["aria-controls"]
                        panel = sec.find(id=pid)
                        if panel:
                            desc_ps = [p.get_text(" ", strip=True) for p in panel.find_all("p")]
                            desc = " ".join([fix_text(x) for x in desc_ps])
                    items.append({"title": title, "description": fix_text(desc)})
            groups[group_name] = {"items": items}

        # 即使没有 h3/accordion，也至少把 tab 的纯文本塞进去
        out[tab] = {"overview": tab_overview, "groups": groups}

    return out

# ------------------------------------------------------

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--search-url", required=True)
    ap.add_argument("--pages", default="1-20")
    ap.add_argument("--out", default="imperial_courses.csv")
    ap.add_argument("--log-level", default="INFO")
    ap.add_argument("--log-file", default=None)
    ap.add_argument("--debug-dir", default=None)
    args = ap.parse_args()

    log = setup_logging(args.log_level, args.log_file)
    ensure_dir(args.debug_dir)

    pages = expand_pages(args.pages)
    links = collect_links(log, args.search_url, pages, args.debug_dir)
    log.info(f"Found {len(links)} course links.")

    cols = ["url", "title",
            "qualification", "duration", "start_date", "ucas_code", "study_mode",
            "delivered_by", "course_overview", "delivered_by_link",
            "structure_json", "status", "error"]

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for i, url in enumerate(links, 1):
            row = {k: "" for k in cols}
            row["url"] = url
            try:
                html = fetch_html(url, log, args.debug_dir)
                soup = BeautifulSoup(html, "lxml")
                row["title"] = soup.title.get_text(" ", strip=True) if soup.title else ""
                row.update(parse_keyfacts(soup))
                row["course_overview"] = parse_overview(soup)
                structure = parse_structure(soup)
                row["structure_json"] = json.dumps(structure, ensure_ascii=False)
                row["status"] = "ok"
            except Exception as e:
                row["status"] = "error"
                row["error"] = f"{type(e).__name__}: {e}"
                log.exception(e)
            w.writerow(row)
            log.info(f"[DETAIL] ({i}/{len(links)}) done {url}")

    log.info(f"[DONE] saved -> {args.out}")

if __name__ == "__main__":
    main()
