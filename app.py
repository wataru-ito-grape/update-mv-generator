import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import os

# ── フォント ─────────────────────────────────────────────
FONT_BOLD_CANDIDATES = [
    "fonts/NotoSansJP-Bold.otf",
    "fonts/NotoSansJP-Bold.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
]
FONT_MEDIUM_CANDIDATES = [
    "fonts/NotoSansJP-Medium.otf",
    "fonts/NotoSansJP-Regular.otf",
    "fonts/NotoSansJP-Regular.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
]
FONT_LABEL_CANDIDATES = [
    "fonts/NotoSansJP-Black.otf",
    "fonts/NotoSansJP-ExtraBold.otf",
    "fonts/NotoSansJP-Bold.otf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
]


def load_font(candidates, size):
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def hex_to_rgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def text_color_for_bg(rgb):
    r, g, b = rgb
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return (20, 20, 20) if brightness > 140 else (245, 245, 245)


def wrap_text(draw, text, font, max_width):
    lines = []
    current = ""
    for char in text:
        test = current + char
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_width and current:
            lines.append(current)
            current = char
        else:
            current = test
    if current:
        lines.append(current)
    return lines


def draw_pill(draw, x, y, text, font, fill=(255, 255, 255), text_fill=(20, 20, 20), border=None):
    pad_h = 18
    pad_v = 10
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    w = tw + pad_h * 2
    h = th + pad_v * 2
    r = h // 2
    draw.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=fill, outline=border, width=3 if border else 0)
    tx = x + pad_h - bbox[0]
    ty = y + pad_v - bbox[1]
    draw.text((tx, ty), text, font=font, fill=text_fill)
    return w, h


def draw_accent_dots(draw, width, height, color, count=6, radius=6):
    import random
    random.seed(42)
    safe_x = int(width * 0.56)
    for _ in range(count):
        cx = random.randint(safe_x, width - 30)
        cy = random.randint(20, height - 20)
        r = random.randint(radius - 2, radius + 4)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)


# ── メイン生成関数 ─────────────────────────────────────────
def generate_mv(photo_bytes, subtitle, main_title, bg_hex, sub_size, title_size, width, height):
    bg_rgb = hex_to_rgb(bg_hex)
    img = Image.new("RGB", (width, height), bg_rgb)
    draw = ImageDraw.Draw(img)

    text_color = text_color_for_bg(bg_rgb)
    pad = max(56, int(width * 0.042))

    # ── 写真 ───────────────────────────────────────────────
    photo_w = int(width * 0.44)
    photo_h = height - pad * 2
    photo_x = width - photo_w - pad
    photo_y = pad

    photo_src = Image.open(io.BytesIO(photo_bytes)).convert("RGB")
    src_aspect = photo_src.width / photo_src.height
    tgt_aspect = photo_w / photo_h
    if src_aspect > tgt_aspect:
        rh = photo_h
        rw = int(rh * src_aspect)
    else:
        rw = photo_w
        rh = int(rw / src_aspect)
    photo_src = photo_src.resize((rw, rh), Image.LANCZOS)
    left = (rw - photo_w) // 2
    top = (rh - photo_h) // 2
    photo_crop = photo_src.crop((left, top, left + photo_w, top + photo_h))
    img.paste(photo_crop, (photo_x, photo_y))

    # ── アクセントドット ────────────────────────────────────
    r, g, b = bg_rgb
    dot_color = (min(255, r + 35), min(255, g + 35), min(255, b + 35))
    draw_accent_dots(draw, width, height, dot_color)

    # ── テキストエリア幅 ───────────────────────────────────
    text_area_w = photo_x - pad * 2
    tx = pad

    # ── 6ヶ月検証 ラベル ──────────────────────────────────
    label_font_size = max(16, int(height * 0.05))
    label_font = load_font(FONT_LABEL_CANDIDATES, label_font_size)
    pill_w, pill_h = draw_pill(
        draw, tx, pad, "6ヶ月検証", label_font,
        fill=(255, 255, 255), text_fill=(20, 20, 20), border=(20, 20, 20)
    )

    # ── サブタイトル ───────────────────────────────────────
    sub_font = load_font(FONT_MEDIUM_CANDIDATES, sub_size)
    sub_y = pad + pill_h + int(height * 0.04)
    sub_lines = wrap_text(draw, subtitle, sub_font, text_area_w)
    for line in sub_lines:
        draw.text((tx, sub_y), line, font=sub_font, fill=text_color)
        sub_y += sub_size + int(sub_size * 0.2)

    # ── メインタイトル ─────────────────────────────────────
    title_font = load_font(FONT_BOLD_CANDIDATES, title_size)
    title_y = sub_y + int(height * 0.022)
    title_lines = wrap_text(draw, main_title, title_font, text_area_w)
    for line in title_lines:
        draw.text((tx, title_y), line, font=title_font, fill=text_color)
        title_y += title_size + int(title_size * 0.18)

    return img


# ── Streamlit UI ──────────────────────────────────────────
st.set_page_config(page_title="UPDATE MV Generator", layout="wide")

st.title("UPDATE MV Generator")
st.caption("メインビジュアル（MV）を2サイズで生成します")
st.divider()

left, right = st.columns([1, 1.2], gap="large")

with left:
    st.subheader("入力")
    uploaded = st.file_uploader("使用画像", type=["jpg", "jpeg", "png"])
    subtitle = st.text_input("サブタイトル", placeholder="このスニーカーはちょっと違う！")
    main_title = st.text_input("メインタイトル", placeholder="On『Cloudmonster 1』を履いてみた")
    bg_color = st.color_picker("背景カラー", "#F0E040")

    st.markdown("**フォントサイズ**")
    col_s, col_t = st.columns(2)
    with col_s:
        sub_size = st.selectbox(
            "サブタイトル",
            [18, 22, 26, 30, 34],
            index=1,
            format_func=lambda x: f"{x}px",
        )
    with col_t:
        title_size = st.selectbox(
            "メインタイトル",
            [32, 38, 44, 50, 58, 66],
            index=2,
            format_func=lambda x: f"{x}px",
        )

    ready = uploaded and subtitle.strip() and main_title.strip()
    generate = st.button("MV を生成", type="primary", disabled=not ready)

    if not ready:
        missing = []
        if not uploaded:
            missing.append("使用画像")
        if not subtitle.strip():
            missing.append("サブタイトル")
        if not main_title.strip():
            missing.append("メインタイトル")
        st.caption(f"未入力：{' / '.join(missing)}")

with right:
    st.subheader("プレビュー・ダウンロード")

    if generate and ready:
        photo_bytes = uploaded.read()
        with st.spinner("生成中..."):
            img_1920 = generate_mv(photo_bytes, subtitle, main_title, bg_color, sub_size, title_size, 1920, 550)
            img_1200 = generate_mv(photo_bytes, subtitle, main_title, bg_color, sub_size, title_size, 1200, 450)

        # プレビュー（縮小表示）
        preview = img_1920.copy()
        preview.thumbnail((800, 250), Image.LANCZOS)
        st.image(preview, use_container_width=True, caption="1920×550 プレビュー")

        preview2 = img_1200.copy()
        preview2.thumbnail((800, 300), Image.LANCZOS)
        st.image(preview2, use_container_width=True, caption="1200×450 プレビュー")

        # ダウンロード
        buf1 = io.BytesIO()
        img_1920.save(buf1, format="JPEG", quality=95)
        buf1.seek(0)

        buf2 = io.BytesIO()
        img_1200.save(buf2, format="JPEG", quality=95)
        buf2.seek(0)

        dl1, dl2 = st.columns(2)
        with dl1:
            st.download_button("1920×550 ダウンロード", buf1, "mv_1920x550.jpg", "image/jpeg", use_container_width=True)
        with dl2:
            st.download_button("1200×450 ダウンロード", buf2, "mv_1200x450.jpg", "image/jpeg", use_container_width=True)

    else:
        st.info("左側の入力を完了して「MV を生成」を押してください")
