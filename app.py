import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import os
import math

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
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def brightness(rgb):
    r, g, b = rgb
    return (r * 299 + g * 587 + b * 114) / 1000


def text_color_for_bg(rgb):
    return (20, 20, 20) if brightness(rgb) > 140 else (240, 240, 240)


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


def paste_rounded(canvas, photo, x, y, w, h, radius=20):
    src = photo.convert("RGBA")
    src_aspect = src.width / src.height
    tgt_aspect = w / h
    if src_aspect > tgt_aspect:
        rh = h
        rw = int(rh * src_aspect)
    else:
        rw = w
        rh = int(rw / src_aspect)
    src = src.resize((rw, rh), Image.LANCZOS)
    left = (rw - w) // 2
    top = (rh - h) // 2
    src = src.crop((left, top, left + w, top + h))

    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=255)
    canvas.paste(src.convert("RGB"), (x, y), mask)


def draw_leaf(draw, cx, cy, size, color):
    # 楕円を重ねてシンプルな葉を描く
    for angle, scale in [(0, 1.0), (40, 0.7), (-30, 0.6)]:
        rad = math.radians(angle)
        ox = int(math.cos(rad) * size * 0.3)
        oy = int(math.sin(rad) * size * 0.3)
        w = int(size * scale)
        h = int(size * scale * 0.55)
        draw.ellipse(
            [cx + ox - w // 2, cy + oy - h // 2, cx + ox + w // 2, cy + oy + h // 2],
            fill=color,
        )


def generate_mv(photo_bytes, subtitle, main_title, bg_hex, accent_hex, sub_size, title_size, width, height):
    bg_rgb = hex_to_rgb(bg_hex)
    accent_rgb = hex_to_rgb(accent_hex)
    dark_text = (20, 20, 20)

    img = Image.new("RGB", (width, height), bg_rgb)
    draw = ImageDraw.Draw(img)

    pad = max(48, int(width * 0.04))

    # ── 写真（右側・角丸） ──────────────────────────────
    photo_w = int(width * 0.43)
    photo_h = int(height - pad * 2)
    photo_x = width - photo_w - pad
    photo_y = pad

    photo_src = Image.open(io.BytesIO(photo_bytes))
    paste_rounded(img, photo_src, photo_x, photo_y, photo_w, photo_h, radius=max(12, int(height * 0.04)))

    # ── 葉デコレーション（右上） ───────────────────────
    leaf_color_bright = brightness(accent_rgb)
    leaf_lightness = 40
    leaf_rgb = (
        min(255, accent_rgb[0] + leaf_lightness),
        min(255, accent_rgb[1] + leaf_lightness),
        min(255, accent_rgb[2] + leaf_lightness),
    )
    leaf_size = int(height * 0.12)
    draw_leaf(draw, photo_x + photo_w - leaf_size // 2, photo_y - leaf_size // 4, leaf_size, leaf_rgb)

    # ── テキストエリア ──────────────────────────────────
    text_max_w = photo_x - pad * 2
    tx = pad

    # ── 6ヶ月検証 バッジ ──────────────────────────────
    badge_font_size = max(14, int(height * 0.042))
    badge_font = load_font(FONT_BOLD_CANDIDATES, badge_font_size)

    badge_text = "6ヶ月検証"
    badge_pad_h = int(badge_font_size * 0.9)
    badge_pad_v = int(badge_font_size * 0.35)
    bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
    bw = bbox[2] - bbox[0] + badge_pad_h * 2
    bh = bbox[3] - bbox[1] + badge_pad_v * 2
    by = pad

    # アクセントカラー背景のピル
    draw.rounded_rectangle([tx, by, tx + bw, by + bh], radius=bh // 2, fill=accent_rgb)
    badge_text_color = (255, 255, 255) if brightness(accent_rgb) < 160 else (20, 20, 20)
    draw.text((tx + badge_pad_h - bbox[0], by + badge_pad_v - bbox[1]), badge_text, font=badge_font, fill=badge_text_color)

    # ── サブタイトル ───────────────────────────────────
    sub_font = load_font(FONT_BOLD_CANDIDATES, sub_size)
    sub_y = by + bh + int(height * 0.045)
    sub_lines = wrap_text(draw, subtitle, sub_font, text_max_w)
    for line in sub_lines:
        draw.text((tx, sub_y), line, font=sub_font, fill=accent_rgb)
        sub_y += sub_size + int(sub_size * 0.15)

    # ── メインタイトル ─────────────────────────────────
    title_font = load_font(FONT_BOLD_CANDIDATES, title_size)
    title_y = sub_y + int(height * 0.02)
    title_lines = wrap_text(draw, main_title, title_font, text_max_w)
    for line in title_lines:
        draw.text((tx, title_y), line, font=title_font, fill=dark_text)
        title_y += title_size + int(title_size * 0.12)

    return img.convert("RGB")


# ── Streamlit UI ──────────────────────────────────────────
st.set_page_config(page_title="UPDATE MV Generator", layout="wide")
st.title("UPDATE MV Generator")
st.divider()

left, right = st.columns([1, 1.2], gap="large")

with left:
    st.subheader("入力")
    uploaded = st.file_uploader("使用画像", type=["jpg", "jpeg", "png"])
    subtitle = st.text_input("サブタイトル", placeholder="このスニーカーはなんか違う")
    main_title = st.text_input("メインタイトル", placeholder="今度出る藤原ヒロシコラボ試してみた")

    col_bg, col_ac = st.columns(2)
    with col_bg:
        bg_color = st.color_picker("背景カラー", "#F0F0F0")
    with col_ac:
        accent_color = st.color_picker("アクセントカラー", "#2DD4BF")

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
            img_1920 = generate_mv(photo_bytes, subtitle, main_title, bg_color, accent_color, sub_size, title_size, 1920, 550)
            img_1200 = generate_mv(photo_bytes, subtitle, main_title, bg_color, accent_color, sub_size, title_size, 1200, 450)

        preview = img_1920.copy()
        preview.thumbnail((800, 250), Image.LANCZOS)
        st.image(preview, use_container_width=True, caption="1920×550 プレビュー")

        preview2 = img_1200.copy()
        preview2.thumbnail((800, 300), Image.LANCZOS)
        st.image(preview2, use_container_width=True, caption="1200×450 プレビュー")

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
