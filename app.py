import streamlit as st
import base64
import sys
import subprocess


@st.cache_resource
def install_playwright():
    subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        capture_output=True,
        timeout=180,
    )

install_playwright()


FONT_DEFAULTS = {
    "thumbnail": {"label": 16, "subtitle": 28, "main": 48},
    "sp_mv":     {"label": 18, "subtitle": 31, "main": 55},
    "pc_mv_1":   {"label": 34, "subtitle": 58, "main": 104},
    "pc_mv_2":   {"label": 41, "subtitle": 70,  "main": 125},
}

OUTPUT_CONFIGS = {
    "thumbnail": (672,  672,  "サムネイル",  "square",    "thumbnail_672x672.jpg"),
    "sp_mv":     (752,  752,  "SP版MV",     "square",    "sp_mv_752x752.jpg"),
    "pc_mv_1":   (2400, 900,  "PC版MV①",   "landscape", "pc_mv_1_2400x900.jpg"),
    "pc_mv_2":   (3840, 1100, "PC版MV②",   "landscape", "pc_mv_2_3840x1100.jpg"),
}

OUTPUT_LABELS = {
    "thumbnail": "サムネイル（672×672）",
    "sp_mv":     "SP版MV（752×752）",
    "pc_mv_1":   "PC版MV①（2400×900）",
    "pc_mv_2":   "PC版MV②（3840×1100）",
}


def _blobs_svg(W, H, accent_color, tr_x, tr_y, tr_w, tr_h, bl_x, bl_y, bl_w, bl_h, blur):
    return f"""<svg style="position:absolute;top:0;left:0;width:{W}px;height:{H}px;pointer-events:none;overflow:visible;"
     xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="ftr" x="-80%" y="-80%" width="260%" height="260%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="{blur}"/></filter>
    <filter id="fbl" x="-80%" y="-80%" width="260%" height="260%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="{blur}"/></filter>
  </defs>
  <rect x="{tr_x}" y="{tr_y}" width="{tr_w}" height="{tr_h}"
    rx="{int(tr_w*0.4)}" ry="{int(tr_h*0.4)}"
    fill="{accent_color}" opacity="0.13" filter="url(#ftr)"/>
  <rect x="{bl_x}" y="{bl_y}" width="{bl_w}" height="{bl_h}"
    rx="{int(bl_w*0.4)}" ry="{int(bl_h*0.4)}"
    fill="{accent_color}" opacity="0.11" filter="url(#fbl)"/>
</svg>"""


def _text_block_html(subtitle, main_title, accent_color,
                     lbl_fs, sub_fs, title_fs,
                     lbl_py, lbl_px, line_w, line_h, gap_major, gap_minor, max_w):
    """テキスト一塊（ラベル・サブタイトル+下線・メインタイトル）のインナーHTML"""
    return f"""<div style="
  display:flex;flex-direction:column;align-items:flex-start;
  gap:{gap_major}px;max-width:{max_w}px;">

  <div style="display:inline-flex;align-items:center;background:{accent_color};color:#fff;
    font-size:{lbl_fs}px;font-weight:700;padding:{lbl_py}px {lbl_px}px;
    border-radius:999px;letter-spacing:0.04em;white-space:nowrap;line-height:1;">6ヶ月検証</div>

  <div style="display:flex;flex-direction:column;gap:{gap_minor}px;align-items:flex-start;">
    <div style="color:{accent_color};font-size:{sub_fs}px;font-weight:700;
      line-height:1.2;letter-spacing:-0.01em;
      word-break:normal;overflow-wrap:anywhere;">{subtitle}</div>
    <div style="width:{line_w}px;height:{line_h}px;
      background:{accent_color};border-radius:2px;"></div>
  </div>

  <div style="color:#1c2224;font-size:{title_fs}px;font-weight:900;line-height:1.22;
    letter-spacing:-0.03em;word-break:normal;overflow-wrap:anywhere;
    line-break:strict;">{main_title}</div>
</div>"""


def build_html_square(photo_b64, photo_mime, subtitle, main_title,
                      bg_color, accent_color, lbl_fs, sub_fs, title_fs, W, H):
    img_x = int(0.125 * W)
    img_y = int(0.503 * H)
    img_w = int(0.747 * W)
    img_h = int(0.418 * H)
    img_r = int(0.028 * W)

    # テキストゾーン：上端〜画像上端まで / 上下中央・左揃え
    text_zone_h = img_y
    text_left   = int(0.137 * W)
    text_max_w  = int(0.740 * W)
    gap_major   = max(8,  int(0.035 * H))
    gap_minor   = max(3,  int(0.014 * H))

    lbl_px = max(10, int(lbl_fs * 1.5))
    lbl_py = lbl_px // 2
    line_w = max(8,  int(0.070 * W))
    line_h = max(2,  int(0.004 * H))
    blur   = max(18, int(min(W, H) * 0.038))

    blobs = _blobs_svg(
        W, H, accent_color,
        int(0.75 * W),  int(-0.06 * H), int(0.34 * W), int(0.36 * H),
        int(-0.06 * W), int( 0.76 * H), int(0.34 * W), int(0.30 * H),
        blur,
    )
    inner = _text_block_html(subtitle, main_title, accent_color,
                             lbl_fs, sub_fs, title_fs,
                             lbl_py, lbl_px, line_w, line_h,
                             gap_major, gap_minor, text_max_w)

    return f"""<!DOCTYPE html>
<html lang="ja"><head>
<meta charset="UTF-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@700;900&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{width:{W}px;height:{H}px;overflow:hidden;background:{bg_color};
font-family:'Noto Sans JP','Hiragino Sans','Yu Gothic UI',sans-serif;}}
</style></head>
<body><div style="position:relative;width:{W}px;height:{H}px;overflow:hidden;">

{blobs}

<!-- 画像エリア（下部） -->
<div style="position:absolute;left:{img_x}px;top:{img_y}px;
  width:{img_w}px;height:{img_h}px;border-radius:{img_r}px;overflow:hidden;">
  <img src="data:{photo_mime};base64,{photo_b64}"
    style="display:block;width:100%;height:100%;object-fit:cover;object-position:center;">
</div>

<!-- テキストブロック：画像上エリアで上下中央・左揃え -->
<div style="position:absolute;left:{text_left}px;top:0;
  width:{text_max_w}px;height:{text_zone_h}px;
  display:flex;align-items:center;">
  {inner}
</div>

</div></body></html>"""


def build_html_landscape(photo_b64, photo_mime, subtitle, main_title,
                         bg_color, accent_color, lbl_fs, sub_fs, title_fs,
                         W, H, use_frame=False):
    if use_frame:
        frame_h = H
        frame_w = min(W, int(H * 8 / 3))
        frame_x = (W - frame_w) // 2
    else:
        frame_w, frame_h, frame_x = W, H, 0

    img_x = frame_x + int(0.510 * frame_w)
    img_y = int(0.112 * frame_h)
    img_w = int(0.455 * frame_w)
    img_h = int(0.776 * frame_h)
    img_r = int(0.035 * frame_h)

    # テキストゾーン：frame左端〜画像左端 / 上下左右中央
    text_zone_x = frame_x
    text_zone_w = img_x - frame_x
    text_max_w  = int(0.430 * frame_w)
    gap_major   = max(12, int(0.055 * frame_h))
    gap_minor   = max(4,  int(0.015 * frame_h))

    lbl_px = max(10, int(lbl_fs * 1.4))
    lbl_py = lbl_px // 2
    line_w = max(8,  int(0.060 * frame_w))
    line_h = max(2,  int(0.006 * frame_h))
    blur   = max(30, int(min(W, H) * 0.05))

    blobs = _blobs_svg(
        W, H, accent_color,
        int(W * 0.80),  int(-H * 0.16), int(W * 0.28), int(H * 0.60),
        int(-W * 0.08), int( H * 0.83), int(W * 0.26), int(H * 0.25),
        blur,
    )
    inner = _text_block_html(subtitle, main_title, accent_color,
                             lbl_fs, sub_fs, title_fs,
                             lbl_py, lbl_px, line_w, line_h,
                             gap_major, gap_minor, text_max_w)

    return f"""<!DOCTYPE html>
<html lang="ja"><head>
<meta charset="UTF-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@700;900&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{width:{W}px;height:{H}px;overflow:hidden;background:{bg_color};
font-family:'Noto Sans JP','Hiragino Sans','Yu Gothic UI',sans-serif;}}
</style></head>
<body><div style="position:relative;width:{W}px;height:{H}px;overflow:hidden;">

{blobs}

<!-- 右側：画像エリア -->
<div style="position:absolute;left:{img_x}px;top:{img_y}px;
  width:{img_w}px;height:{img_h}px;border-radius:{img_r}px;overflow:hidden;">
  <img src="data:{photo_mime};base64,{photo_b64}"
    style="display:block;width:100%;height:100%;object-fit:cover;object-position:center;">
</div>

<!-- テキストブロック：左ゾーンで上下左右中央 -->
<div style="position:absolute;left:{text_zone_x}px;top:0;
  width:{text_zone_w}px;height:{H}px;
  display:flex;align-items:center;justify-content:center;">
  {inner}
</div>

</div></body></html>"""


def render(html: str, width: int, height: int) -> bytes:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": height})
        page.set_content(html, wait_until="networkidle")
        buf = page.screenshot(
            type="jpeg", quality=100,
            clip={"x": 0, "y": 0, "width": width, "height": height},
        )
        browser.close()
    return buf


def generate_image(photo_bytes, photo_ext, subtitle, main_title,
                   bg_color, accent_color, lbl_fs, sub_fs, title_fs, key):
    W, H, _, layout, _ = OUTPUT_CONFIGS[key]
    mime = "image/png" if photo_ext.lower() == "png" else "image/jpeg"
    b64  = base64.b64encode(photo_bytes).decode()

    if layout == "square":
        html = build_html_square(b64, mime, subtitle, main_title,
                                 bg_color, accent_color, lbl_fs, sub_fs, title_fs, W, H)
    else:
        html = build_html_landscape(b64, mime, subtitle, main_title,
                                    bg_color, accent_color, lbl_fs, sub_fs, title_fs,
                                    W, H, use_frame=(key == "pc_mv_2"))
    return render(html, W, H)


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
        bg_color     = st.color_picker("背景カラー",      "#FAF9F8")
    with c2:
        accent_color = st.color_picker("アクセントカラー", "#169783")

    st.markdown("---")
    st.markdown("**生成するサイズを選択**")

    selected_keys = []
    for key, label in OUTPUT_LABELS.items():
        if st.checkbox(label, value=True, key=f"chk_{key}"):
            selected_keys.append(key)

    st.markdown("---")

    font_sizes = {}
    for key in selected_keys:
        d = FONT_DEFAULTS[key]
        with st.expander(f"フォントサイズ — {OUTPUT_LABELS[key]}"):
            c1, c2, c3 = st.columns(3)
            with c1:
                lv = st.number_input("ラベル",         min_value=8,  max_value=80,
                                     value=d["label"],    step=1, key=f"lbl_{key}")
            with c2:
                sv = st.number_input("サブタイトル",   min_value=12, max_value=120,
                                     value=d["subtitle"], step=1, key=f"sub_{key}")
            with c3:
                tv = st.number_input("メインタイトル", min_value=24, max_value=200,
                                     value=d["main"],     step=1, key=f"ttl_{key}")
            font_sizes[key] = (int(lv), int(sv), int(tv))

    ready        = bool(uploaded and subtitle.strip() and main_title.strip() and selected_keys)
    generate_btn = st.button("MV を生成", type="primary", disabled=not ready)

    if not ready:
        missing = []
        if not uploaded:           missing.append("使用画像")
        if not subtitle.strip():   missing.append("サブタイトル")
        if not main_title.strip(): missing.append("メインタイトル")
        if not selected_keys:      missing.append("生成サイズ（1つ以上選択）")
        st.caption(f"未入力：{' / '.join(missing)}")


with right:
    st.subheader("プレビュー・ダウンロード")

    if generate_btn and ready:
        photo_bytes = uploaded.read()
        ext = uploaded.name.rsplit(".", 1)[-1]

        results  = {}
        total    = len(selected_keys)
        progress = st.progress(0, text="生成中...")

        for i, key in enumerate(selected_keys):
            progress.progress(i / total, text=f"生成中… {OUTPUT_LABELS[key]}")
            lbl_fs, sub_fs, ttl_fs = font_sizes[key]
            results[key] = generate_image(
                photo_bytes, ext, subtitle, main_title,
                bg_color, accent_color, lbl_fs, sub_fs, ttl_fs, key
            )

        progress.progress(1.0, text="完了！")

        for key, jpg in results.items():
            W, H, _, _, filename = OUTPUT_CONFIGS[key]
            st.image(jpg, use_container_width=True, caption=OUTPUT_LABELS[key])
            st.download_button(
                f"⬇ {OUTPUT_LABELS[key]} ダウンロード",
                jpg, filename, "image/jpeg",
                use_container_width=True,
                key=f"dl_{key}",
            )
    else:
        st.info("左側の入力を完了して「MV を生成」を押してください")
