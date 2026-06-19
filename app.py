import streamlit as st
from PIL import Image
import base64
import io
import os
import sys
import subprocess

# ── Playwright セットアップ ───────────────────────────────
@st.cache_resource
def install_playwright():
    subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        capture_output=True,
        timeout=180,
    )

install_playwright()


# ── HTML テンプレート ─────────────────────────────────────
def build_html(photo_b64, photo_mime, subtitle, main_title, bg_color, accent_color, sub_size, title_size, width, height):
    pad        = max(40, int(width * 0.04))
    gap        = max(20, int(width * 0.02))
    photo_w    = int(width * 0.47)
    photo_h    = height - pad * 2
    radius     = max(12, int(photo_h * 0.045))
    badge_fs   = max(13, int(height * 0.038))
    badge_py   = int(badge_fs * 0.35)
    badge_px   = int(badge_fs * 0.9)
    deco_fs    = max(36, int(height * 0.13))
    text_gap   = max(10, int(height * 0.035))

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@500;700;900&display=swap" rel="stylesheet">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  width:{width}px; height:{height}px; overflow:hidden;
  background:{bg_color};
  font-family:'Noto Sans JP','Hiragino Sans','Yu Gothic UI',sans-serif;
}}
.wrap {{
  display:flex; align-items:center;
  width:{width}px; height:{height}px;
  padding:{pad}px; gap:{gap}px;
}}
.left {{
  flex:1; min-width:0;
  display:flex; flex-direction:column;
  justify-content:center;
  gap:{text_gap}px;
  padding-bottom:{int(height * 0.06)}px;
}}
.badge {{
  display:inline-flex; align-items:center;
  background:{accent_color}; color:#fff;
  font-size:{badge_fs}px; font-weight:700;
  padding:{badge_py}px {badge_px}px;
  border-radius:999px; letter-spacing:.02em;
  width:max-content;
}}
.sub {{
  font-size:{sub_size}px; font-weight:700;
  color:{accent_color}; line-height:1.5;
}}
.ttl {{
  font-size:{title_size}px; font-weight:900;
  color:#1a1a1a; line-height:1.25;
  word-break: normal;
  overflow-wrap: anywhere;
  line-break: strict;
}}
.right {{
  position:relative;
  width:{photo_w}px; height:{photo_h}px;
  flex-shrink:0;
}}
.leaf {{
  position:absolute;
  top:{-deco_fs // 2}px; right:{-deco_fs // 5}px;
  font-size:{deco_fs}px; z-index:2; line-height:1;
}}
.photo {{
  width:100%; height:100%;
  object-fit:cover; border-radius:{radius}px;
}}
</style>
</head>
<body>
<div class="wrap">
  <div class="left">
    <span class="badge">6ヶ月検証</span>
    <div class="sub">{subtitle}</div>
    <div class="ttl">{main_title}</div>
  </div>
  <div class="right">
    <span class="leaf">🌿</span>
    <img class="photo" src="data:{photo_mime};base64,{photo_b64}">
  </div>
</div>
</body>
</html>"""


def render(html, width, height):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": height})
        page.set_content(html, wait_until="networkidle")
        buf = page.screenshot(
            type="jpeg", quality=95,
            clip={"x": 0, "y": 0, "width": width, "height": height},
        )
        browser.close()
    return buf


def generate(photo_bytes, photo_ext, subtitle, main_title, bg_color, accent_color, sub_size, title_size, width, height):
    # キャンバス高さに比例してフォントをスケール（基準: 450px）
    scale = height / 450
    scaled_sub   = int(sub_size   * scale)
    scaled_title = int(title_size * scale)
    mime = "image/png" if photo_ext.lower() == "png" else "image/jpeg"
    photo_b64 = base64.b64encode(photo_bytes).decode()
    html = build_html(photo_b64, mime, subtitle, main_title, bg_color, accent_color, scaled_sub, scaled_title, width, height)
    return render(html, width, height)


# ── Streamlit UI ──────────────────────────────────────────
st.set_page_config(page_title="UPDATE MV Generator", layout="wide")
st.title("UPDATE MV Generator")
st.divider()

left, right = st.columns([1, 1.2], gap="large")

with left:
    st.subheader("入力")
    uploaded = st.file_uploader("使用画像", type=["jpg", "jpeg", "png"])
    subtitle  = st.text_input("サブタイトル",  placeholder="このスニーカーはなんか違う")
    main_title = st.text_input("メインタイトル", placeholder="今度出る藤原ヒロシコラボ試してみた")

    c1, c2 = st.columns(2)
    with c1:
        bg_color = st.color_picker("背景カラー", "#F0F0F0")
    with c2:
        accent_color = st.color_picker("アクセントカラー", "#2DD4BF")

    st.markdown("**フォントサイズ**")
    cs, ct = st.columns(2)
    with cs:
        sub_size = st.selectbox("サブタイトル", [18, 22, 26, 30, 34], index=1, format_func=lambda x: f"{x}px")
    with ct:
        title_size = st.selectbox("メインタイトル", [32, 38, 44, 50, 58, 66], index=3, format_func=lambda x: f"{x}px")

    ready    = bool(uploaded and subtitle.strip() and main_title.strip())
    generate_btn = st.button("MV を生成", type="primary", disabled=not ready)

    if not ready:
        missing = [label for flag, label in [
            (not uploaded,          "使用画像"),
            (not subtitle.strip(),   "サブタイトル"),
            (not main_title.strip(), "メインタイトル"),
        ] if flag]
        st.caption(f"未入力：{' / '.join(missing)}")

with right:
    st.subheader("プレビュー・ダウンロード")

    if generate_btn and ready:
        photo_bytes = uploaded.read()
        ext = uploaded.name.rsplit(".", 1)[-1]

        with st.spinner("生成中..."):
            jpg_1920 = generate(photo_bytes, ext, subtitle, main_title, bg_color, accent_color, sub_size, title_size, 1920, 550)
            jpg_1200 = generate(photo_bytes, ext, subtitle, main_title, bg_color, accent_color, sub_size, title_size, 1200, 450)

        st.image(jpg_1920, use_container_width=True, caption="1920×550")
        st.image(jpg_1200, use_container_width=True, caption="1200×450")

        c1, c2 = st.columns(2)
        with c1:
            st.download_button("1920×550 ダウンロード", jpg_1920, "mv_1920x550.jpg", "image/jpeg", use_container_width=True)
        with c2:
            st.download_button("1200×450 ダウンロード", jpg_1200, "mv_1200x450.jpg", "image/jpeg", use_container_width=True)
    else:
        st.info("左側の入力を完了して「MV を生成」を押してください")
