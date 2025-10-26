# -*- coding: utf-8 -*-
# viz_structure.py — 可视化 imperial_courses.csv里的 structure_json

import json
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Imperial Courses Structure Viewer", layout="wide")

@st.cache_data
def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8")
    # 兜底：有些字段可能不存在
    for col in ["title","url","qualification","duration","start_date","ucas_code","study_mode","delivered_by","delivered_by_link","course_overview","structure_json"]:
        if col not in df.columns:
            df[col] = ""
    return df

def parse_struct(s: str):
    if not isinstance(s, str) or not s.strip():
        return {}
    try:
        return json.loads(s)
    except Exception:
        return {}

def key_fact(k, v):
    st.metric(k, v if isinstance(v, str) else "")

def render_structure(struct: dict):
    """按层级渲染：tab → h3(组) → items(模块)"""
    if not isinstance(struct, dict) or not struct:
        st.info("此课程没有解析到结构（structure_json 为空）。")
        return
    for tab_name, tab_obj in struct.items():
        with st.expander(f"📑 {tab_name}", expanded=False):
            overview = (tab_obj or {}).get("overview", "")
            if overview:
                st.markdown(f"> {overview}")
            groups = (tab_obj or {}).get("groups", {}) or {}
            if not groups:
                st.write("（该 tab 下无分组）")
            for gname, gobj in groups.items():
                with st.expander(f"🧩 {gname}", expanded=False):
                    items = (gobj or {}).get("items", []) or []
                    if not items:
                        st.write("（该分组下无模块）")
                    for i, it in enumerate(items, 1):
                        title = (it or {}).get("title", "")
                        desc  = (it or {}).get("description", "")
                        with st.expander(f"{i}. {title}" if title else f"{i}. (Untitled)", expanded=False):
                            if desc:
                                st.write(desc)
                            else:
                                st.write("（无描述）")

# --- 侧边栏：加载数据 & 课程选择 ---
st.sidebar.title("设置 / Settings")
csv_path = st.sidebar.text_input("CSV 路径", value="imperial_courses.csv")
df = load_csv(csv_path)

# 去重（按 url 保留第一条）
if "url" in df.columns:
    df = df.sort_values(by=["title"]).drop_duplicates(subset=["url"], keep="first")

titles = df["title"].fillna("").tolist()
urls = df["url"].fillna("").tolist()
options = [f"{t}  —  {u}" if t else u for t, u in zip(titles, urls)]
sel = st.sidebar.selectbox("选择课程", options, index=0 if options else None)

if not options:
    st.warning("没有读取到课程数据。请确认 CSV 路径正确。")
    st.stop()

sel_idx = options.index(sel)
row = df.iloc[sel_idx]

# --- 页面：头部信息 ---
st.title(row.get("title") or "无标题课程")
st.caption(row.get("url") or "")

# 关键信息（四列）
col1, col2, col3, col4 = st.columns(4)
with col1: key_fact("Qualification", row.get("qualification",""))
with col2: key_fact("Duration", row.get("duration",""))
with col3: key_fact("Start date", row.get("start_date",""))
with col4: key_fact("UCAS code", row.get("ucas_code",""))

col5, col6 = st.columns(2)
with col5: key_fact("Study mode", row.get("study_mode",""))
with col6:
    delivered = row.get("delivered_by","")
    link = row.get("delivered_by_link","")
    if link and isinstance(link, str) and link.startswith("http"):
        st.markdown(f"**Delivered by:** [{delivered}]({link})")
    else:
        key_fact("Delivered by", delivered)

# 简介
if row.get("course_overview"):
    st.subheader("Course overview")
    st.write(row["course_overview"])

# 结构
st.subheader("Course structure")
struct = parse_struct(row.get("structure_json",""))
render_structure(struct)

# 可选：下载当前课程的结构为 JSON
st.download_button(
    label="下载当前结构 JSON",
    data=json.dumps(struct, ensure_ascii=False, indent=2),
    file_name="course_structure.json",
    mime="application/json",
)
