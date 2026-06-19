import streamlit as st
import base64
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


# ── ヘルパー ─────────────────────────────────────────────
def hex_to_rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


# ── HTML テンプレート ─────────────────────────────────────
def build_html(photo_b64, photo_mime, subtitle, main_title, bg_color, accent_color, width, height):
    W, H = width, height

    # ── 右側画像エリア ──────────────────
    img_x = int(0.486 * W)
    img_y = int(0.142 * H)
    img_w = int(0.454 * W)
    img_h = int(0.707 * H)
    img_r = int(min(W, H) * 0.038)

    # ── 固定ラベル ──────────────────────
    lbl_x  = int(0.053 * W)
    lbl_y  = int(0.195 * H)
    lbl_fs = max(10, int(H * 0.033))
    lbl_py = max(4,  int(lbl_fs * 0.35))
    lbl_px = max(10, int(lbl_fs * 0.90))

    # ── サブタイトル ────────────────────
    sub_x  = int(0.053 * W)
    sub_y  = int(0.310 * H)
    sub_mw = int(0.405 * W)
    sub_fs = max(12, int(H * 0.059))

    # ── アクセントライン ────────────────
    line_x = int(0.053 * W)
    line_y = int(0.407 * H)
    line_w = max(8, int(0.054 * W))
    line_h = max(2, int(0.006 * H))

    # ── メインタイトル ──────────────────
    ttl_x  = int(0.052 * W)
    ttl_y  = int(0.455 * H)
    ttl_mw = int(0.430 * W)
    ttl_mh = int(0.360 * H)
    ttl_fs = max(18, int(H * 0.093))

    # ── 背景装飾 ────────────────────────
    deco_tr_x = int(0.72 * W)
    deco_tr_y = int(-0.20 * H)
    deco_tr_w = int(0.42 * W)
    deco_tr_h = int(0.70 * H)

    deco_bl_x = int(-0.06 * W)
    deco_bl_y = int(0.72 * H)
    deco_bl_w = int(0.36 * W)
    deco_bl_h = int(0.55 * H)

    blur_tr = max(20, int(deco_tr_w * 0.15))
    blur_bl = max(20, int(deco_bl_w * 0.15))

    c_tr = hex_to_rgba(accent_color, 0.13)
    c_bl = hex_to_rgba(accent_color, 0.10)

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@700;800;900&display=swap" rel="stylesheet">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  width:{W}px; height:{H}px; overflow:hidden;
  background:{bg_color};
  font-family:'Noto Sans JP','Hiragino Sans','Yu Gothic UI',sans-serif;
}}
</style>
</head>
<body>
<div style="position:relative;width:{W}px;height:{H}px;overflow:hidden;">

  <!-- 背景装飾：右上 -->
  <div style="
    position:absolute;
    left:{deco_tr_x}px; top:{deco_tr_y}px;
    width:{deco_tr_w}px; height:{deco_tr_h}px;
    background:{c_tr};
    border-radius:50%;
    filter:blur({blur_tr}px);
    pointer-events:none;
  "></div>

  <!-- 背景装飾：左下 -->
  <div style="
    position:absolute;
    left:{deco_bl_x}px; top:{deco_bl_y}px;
    width:{deco_bl_w}px; height:{deco_bl_h}px;
    background:{c_bl};
    border-radius:50%;
    filter:blur({blur_bl}px);
    pointer-events:none;
  "></div>

  <!-- 右側：画像エリア -->
  <div style="
    position:absolute;
    left:{img_x}px; top:{img_y}px;
    width:{img_w}px; height:{img_h}px;
    border-radius:{img_r}px;
    overflow:hidden;
  ">
    <img src="data:{photo_mime};base64,{photo_b64}" style="
      display:block;
      width:100%; height:100%;
      object-fit:cover;
      object-position:center;
    ">
  </div>

  <!-- 固定ラベル：6ヶ月検証 -->
  <div style="
    position:absolute;
    left:{lbl_x}px; top:{lbl_y}px;
    display:inline-flex; align-items:center;
    background:{accent_color};
    color:#fff;
    font-size:{lbl_fs}px; font-weight:700;
    padding:{lbl_py}px {lbl_px}px;
    border-radius:999px;
    letter-spacing:0.04em;
    white-space:nowrap; line-height:1;
  ">6ヶ月検証</div>

  <!-- サブタイトル -->
  <div style="
    position:absolute;
    left:{sub_x}px; top:{sub_y}px;
    max-width:{sub_mw}px;
    color:{accent_color};
    font-size:{sub_fs}px; font-weight:800;
    line-height:1.12;
    letter-spacing:-0.02em;
    word-break:normal;
    overflow-wrap:anywhere;
  ">{subtitle}</div>

  <!-- アクセントライン -->
  <div style="
    position:absolute;
    left:{line_x}px; top:{line_y}px;
    width:{line_w}px; height:{line_h}px;
    background:{accent_color};
    border-radius:1px;
  "></div>

  <!-- メインタイトル -->
  <div style="
    position:absolute;
    left:{ttl_x}px; top:{ttl_y}px;
    max-width:{ttl_mw}px;
    max-height:{ttl_mh}px;
    color:#151b1b;
    font-size:{ttl_fs}px; font-weight:900;
    line-height:1.22;
    letter-spacing:-0.03em;
    word-break:normal;
    overflow-wrap:anywhere;
    line-break:strict;
    overflow:hidden;
  ">{main_title}</div>

</div>
</body>
</html>"""


def render(html: str, width: int, height: int) -> bytes:
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


def generate(photo_bytes: bytes, photo_ext: str, subtitle: str, main_title: str,
             bg_color: str, accent_color: str, width: int, height: int) -> bytes:
    mime = "image/png" if photo_ext.lower() == "png" else "image/jpeg"
    photo_b64 = base64.b64encode(photo_bytes).decode()
    html = build_html(photo_b64, mime, subtitle, main_title, bg_color, accent_color, width, height)
    return render(html, width, height)


# ── Streamlit UI ──────────────────────────────────────────
st.set_page_config(page_title="UPDATE MV Generator", layout="wide")
st.title("UPDATE MV Generator")
st.divider()

left, right = st.columns([1, 1.2], gap="large")

with left:
    st.subheader("入力")
    uploaded   = st.file_uploader("使用画像", type=["jpg", "jpeg", "png"])
    subtitle   = st.text_input("サブタイトル",   placeholder="このスニーカーはなんか違う")
    main_title = st.text_input("メインタイトル", placeholder="今度出る藤原ヒロシコラボ試してみた")

    c1, c2 = st.columns(2)
    with c1:
        bg_color     = st.color_picker("背景カラー",     "#FBFAF9")
    with c2:
        accent_color = st.color_picker("アクセントカラー", "#15977F")

    ready        = bool(uploaded and subtitle.strip() and main_title.strip())
    generate_btn = st.button("MV を生成", type="primary", disabled=not ready)

    if not ready:
        missing = [label for flag, label in [
            (not uploaded,           "使用画像"),
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
            jpg_1920 = generate(photo_bytes, ext, subtitle, main_title, bg_color, accent_color, 1920, 550)
            jpg_1200 = generate(photo_bytes, ext, subtitle, main_title, bg_color, accent_color, 1200, 450)

        st.image(jpg_1920, use_container_width=True, caption="1920×550")
        st.image(jpg_1200, use_container_width=True, caption="1200×450")

        col1, col2 = st.columns(2)
        with col1:
            st.download_button("⬇ 1920×550 ダウンロード", jpg_1920, "mv_1920x550.jpg", "image/jpeg", use_container_width=True)
        with col2:
            st.download_button("⬇ 1200×450 ダウンロード", jpg_1200, "mv_1200x450.jpg", "image/jpeg", use_container_width=True)
    else:
        st.info("左側の入力を完了して「MV を生成」を押してください")
