"""
이틀 (iteul) SNS 이미지 생성 스크립트
아티스트 컨셉: "끝나기 직전의 빛" — 세기가 바뀌기 직전 마지막 새벽의 감성
"""

import math
import os
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ── 경로 설정 ──────────────────────────────────────────────────────────────
OUT_DIR = os.path.join(os.path.dirname(__file__), "iteul-assets")
os.makedirs(OUT_DIR, exist_ok=True)

FONT_KR   = "/tmp/NotoSansCJKkr-Regular.otf"
FONT_SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

# ── 컬러 팔레트 ──────────────────────────────────────────────────────────────
C_NAVY_DEEP  = (13,  27,  42)   # #0d1b2a
C_NAVY       = (27,  42,  74)   # #1b2a4a
C_NAVY_MID   = (20,  35,  60)   # 중간톤
C_ORANGE     = (232, 99,  42)   # #e8632a
C_RED        = (201, 64,  64)   # #c94040
C_WHITE_COOL = (232, 232, 240)  # #e8e8f0
C_GOLD       = (201, 168, 76)   # #c9a84c
C_GOLD_LIGHT = (220, 190, 110)
C_DAWN_GLOW  = (180, 80,  40)   # 새벽빛 중간


# ── 유틸리티 ─────────────────────────────────────────────────────────────────

def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def draw_vertical_gradient(draw, w, h, colors, y_start=0, y_end=None):
    """colors: list of (color, stop_fraction) tuples"""
    if y_end is None:
        y_end = h
    height = y_end - y_start
    stops = sorted(colors, key=lambda x: x[1])
    for y in range(y_start, y_end):
        t_global = (y - y_start) / max(height - 1, 1)
        # find which segment
        color = stops[0][0]
        for i in range(len(stops) - 1):
            t0, t1 = stops[i][1], stops[i + 1][1]
            if t0 <= t_global <= t1:
                seg_t = (t_global - t0) / max(t1 - t0, 1e-9)
                color = lerp_color(stops[i][0], stops[i + 1][0], seg_t)
                break
        else:
            color = stops[-1][0]
        draw.line([(0, y), (w, y)], fill=color)


def draw_radial_glow(img, cx, cy, radius, color, alpha_max=180):
    """부드러운 방사형 글로우 레이어를 합성"""
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    steps = 60
    for i in range(steps, 0, -1):
        r = int(radius * i / steps)
        a = int(alpha_max * (1 - i / steps) ** 1.5)
        gd.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            fill=(*color, a)
        )
    img.alpha_composite(glow)


def draw_shimmer_lines(draw, w, h, color, n=12, alpha=30):
    """빛이 번지는 수평 라인"""
    for _ in range(n):
        y = random.randint(int(h * 0.4), int(h * 0.85))
        thick = random.randint(1, 3)
        x_start = random.randint(0, w // 3)
        x_end   = random.randint(w // 2, w)
        draw.line([(x_start, y), (x_end, y)], fill=(*color, alpha), width=thick)


def draw_star_field(draw, w, h, n=120, region_top=0.0, region_bot=0.5):
    """별 흩뿌리기"""
    for _ in range(n):
        x = random.randint(0, w)
        y = random.randint(int(h * region_top), int(h * region_bot))
        r = random.choice([0, 0, 0, 1, 1, 2])
        brightness = random.randint(140, 240)
        a = random.randint(80, 200)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(brightness, brightness, brightness + 10, a))


def centered_text(draw, text, font, y, w, color, anchor="mm"):
    bbox = font.getbbox(text)
    tw = bbox[2] - bbox[0]
    x = w // 2
    draw.text((x, y), text, font=font, fill=color, anchor=anchor)
    return tw


def add_noise(img, strength=8):
    """미세 노이즈로 필름 질감 추가"""
    import random as rnd
    px = img.load()
    for _ in range(img.width * img.height // 8):
        x = rnd.randint(0, img.width - 1)
        y = rnd.randint(0, img.height - 1)
        p = px[x, y]
        d = rnd.randint(-strength, strength)
        px[x, y] = tuple(max(0, min(255, p[i] + d)) for i in range(3)) + ((p[3],) if len(p) == 4 else ())


# ══════════════════════════════════════════════════════════════════════════════
# 1. 프로필 이미지 (500×500px)  — 2 버전
# ══════════════════════════════════════════════════════════════════════════════

def make_profile_bg(size=500):
    """새벽빛 번지는 프로필 배경 공통 생성"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # 세로 그라디언트: 짙은 네이비 → 번지는 새벽빛
    draw_vertical_gradient(draw, size, size, [
        (C_NAVY_DEEP,  0.00),
        (C_NAVY,       0.40),
        (C_NAVY_MID,   0.60),
        ((50, 30, 25), 0.80),
        (C_NAVY_DEEP,  1.00),
    ])

    # 별
    random.seed(42)
    draw_star_field(draw, size, size, n=80, region_top=0.0, region_bot=0.55)

    # 지평선 글로우 (중앙 하단)
    draw_radial_glow(img, size // 2, int(size * 0.72), int(size * 0.65), C_ORANGE, alpha_max=130)
    draw_radial_glow(img, size // 2, int(size * 0.72), int(size * 0.35), C_RED,    alpha_max=90)

    # 얇은 황금빛 수평선
    glow_y = int(size * 0.70)
    for i, thick in enumerate([6, 3, 1]):
        a = [50, 100, 160][i]
        draw.line([(0, glow_y + i), (size, glow_y + i)], fill=(*C_GOLD, a), width=thick)

    # 빛 번짐 라인
    draw_shimmer_lines(draw, size, size, C_GOLD_LIGHT, n=8, alpha=25)

    return img


def make_profile_text():
    """버전 A — 텍스트 포함"""
    size = 500
    img = make_profile_bg(size)
    draw = ImageDraw.Draw(img)

    # 영문 'iteul' 소문자 (얇게)
    f_en_big  = load_font(FONT_SANS, 58)
    f_en_sub  = load_font(FONT_SANS, 22)
    f_kr      = load_font(FONT_KR,   56)

    # 한글 '이틀' — 중상단
    centered_text(draw, "이틀", f_kr, int(size * 0.42), size, C_WHITE_COOL)

    # 영문 'iteul' — 한글 바로 아래
    centered_text(draw, "iteul", f_en_big, int(size * 0.56), size, (*C_GOLD, 230))

    # 장르 라벨
    centered_text(draw, "R&B  /  Soul", f_en_sub, int(size * 0.68), size, (*C_WHITE_COOL[:3], 140))

    # 골드 장식선 (텍스트 아래)
    lw = 80
    cx = size // 2
    ly = int(size * 0.74)
    draw.line([(cx - lw, ly), (cx + lw, ly)], fill=(*C_GOLD, 120), width=1)

    add_noise(img, strength=6)
    path = os.path.join(OUT_DIR, "profile_text.png")
    img.convert("RGB").save(path)
    print(f"  saved: {path}")


def make_profile_mood():
    """버전 B — 텍스트 없이 무드만"""
    size = 500
    img = make_profile_bg(size)
    draw = ImageDraw.Draw(img)

    # 추상 원형 심볼 — '이틀 전' 태양이 떠오르는 반원
    cx, cy = size // 2, int(size * 0.72)
    # 태양 반원
    sun_r = 48
    for offset, alpha in [(14, 20), (10, 40), (6, 70), (3, 100), (0, 160)]:
        r = sun_r + offset
        draw.arc(
            [cx - r, cy - r, cx + r, cy + r],
            start=190, end=350,
            fill=(*C_GOLD, alpha), width=max(1, offset + 1)
        )

    # 수면 반사 수평 타원
    for i in range(5):
        ellipse_w = int(sun_r * (2.5 - i * 0.3))
        ellipse_h = int(6 - i)
        if ellipse_h < 1:
            break
        offset_y = int(cy + sun_r * 0.3 + i * 9)
        a = max(20, 80 - i * 15)
        draw.ellipse(
            [cx - ellipse_w, offset_y - ellipse_h,
             cx + ellipse_w, offset_y + ellipse_h],
            outline=(*C_GOLD, a), width=1
        )

    add_noise(img, strength=6)
    path = os.path.join(OUT_DIR, "profile_mood.png")
    img.convert("RGB").save(path)
    print(f"  saved: {path}")


# ══════════════════════════════════════════════════════════════════════════════
# 2. 유튜브 헤더 (2560×1440px, 안전영역 1546×423px 중앙)
# ══════════════════════════════════════════════════════════════════════════════

def make_youtube_header():
    W, H = 2560, 1440
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # 배경 그라디언트 — 도시 새벽 하늘
    draw_vertical_gradient(draw, W, H, [
        (C_NAVY_DEEP,          0.00),
        (C_NAVY,               0.30),
        ((30, 40, 65),         0.50),
        ((55, 35, 30),         0.68),
        ((80, 45, 25),         0.78),
        ((40, 25, 20),         0.88),
        (C_NAVY_DEEP,          1.00),
    ])

    random.seed(7)
    # 별 (상단 절반)
    draw_star_field(draw, W, H, n=300, region_top=0.0, region_bot=0.42)

    # 지평선 글로우 — 수평 중심
    horizon_y = int(H * 0.62)
    draw_radial_glow(img, W // 2, horizon_y, int(W * 0.55), C_ORANGE, alpha_max=90)
    draw_radial_glow(img, W // 2, horizon_y, int(W * 0.28), C_RED,    alpha_max=70)
    draw_radial_glow(img, W // 2, horizon_y, int(W * 0.10), C_GOLD,   alpha_max=110)

    # 도시 실루엣 (단순 직사각형 군집)
    random.seed(99)
    building_color = (8, 16, 30)
    window_colors = [(C_GOLD, 0.15), (C_ORANGE, 0.08), (C_WHITE_COOL, 0.06)]
    base_y = int(H * 0.62)
    for i in range(80):
        bw = random.randint(20, 70)
        bh = random.randint(60, 300)
        bx = random.randint(0, W - bw)
        by = base_y - bh
        draw.rectangle([bx, by, bx + bw, base_y], fill=building_color)
        # 창문
        for wy in range(by + 8, base_y - 10, 14):
            for wx in range(bx + 4, bx + bw - 4, 10):
                if random.random() < 0.25:
                    wc, _ = random.choice(window_colors)
                    wa = random.randint(80, 180)
                    draw.rectangle([wx, wy, wx + 5, wy + 7], fill=(*wc, wa))

    # 수면 반사 (도시 아래)
    water_y = base_y
    for i in range(30):
        ry = water_y + i * 14
        alpha = max(0, 110 - i * 4)
        cx_offset = random.randint(-100, 100)
        rw = random.randint(W // 4, W // 2)
        draw.ellipse(
            [W // 2 + cx_offset - rw, ry - 3,
             W // 2 + cx_offset + rw, ry + 3],
            fill=(*lerp_color(C_GOLD, C_ORANGE, i / 30), alpha)
        )

    # 황금 지평선 선
    for offset, a in [(0, 180), (1, 100), (2, 60), (-1, 80)]:
        draw.line([(0, horizon_y + offset), (W, horizon_y + offset)],
                  fill=(*C_GOLD, a), width=max(1, 2 - abs(offset)))

    # ─ 텍스트 — 안전영역 (가로 중앙 1546px, 세로 423px 중앙 기준)
    safe_x  = (W - 1546) // 2        # 507
    safe_y  = (H - 423)  // 2        # 508 (상단)
    safe_cx = W // 2
    safe_cy = H // 2

    # 텍스트 배경 블러 패널 (반투명)
    panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    pd.rectangle(
        [safe_x - 40, safe_y - 20, safe_x + 1546 + 40, safe_y + 423 + 20],
        fill=(C_NAVY_DEEP[0], C_NAVY_DEEP[1], C_NAVY_DEEP[2], 60)
    )
    img.alpha_composite(panel.filter(ImageFilter.GaussianBlur(30)))

    draw = ImageDraw.Draw(img)

    f_kr_xl  = load_font(FONT_KR,   130)
    f_en_xl  = load_font(FONT_BOLD, 110)
    f_en_sub = load_font(FONT_SANS,  42)
    f_label  = load_font(FONT_SANS,  34)

    text_y_kr   = safe_cy - 55
    text_y_en   = safe_cy + 70
    text_y_genre= safe_cy + 150

    # '이틀' 한글
    centered_text(draw, "이틀", f_kr_xl, text_y_kr, W, C_WHITE_COOL)

    # 'iteul' 영문
    centered_text(draw, "iteul", f_en_xl, text_y_en, W, (*C_GOLD, 230))

    # 장르
    centered_text(draw, "R & B  /  S O U L", f_label, text_y_genre, W,
                  (*C_WHITE_COOL[:3], 160))

    # 안전영역 가이드 (주석처리 — 최종 출력엔 표시 안 함)
    # draw.rectangle([safe_x, safe_y, safe_x+1546, safe_y+423], outline=(255,0,0,60), width=2)

    add_noise(img, strength=4)
    path = os.path.join(OUT_DIR, "youtube_header.png")
    img.convert("RGB").save(path)
    print(f"  saved: {path}")


# ══════════════════════════════════════════════════════════════════════════════
# 3. 인스타그램 하이라이트 커버 (원형 1:1, 1000×1000 저장 후 원형 마스크)
# ══════════════════════════════════════════════════════════════════════════════

HIGHLIGHT_THEMES = [
    {
        "name": "새벽",
        "name_en": "dawn",
        "colors": [(C_NAVY_DEEP, 0.0), (C_NAVY, 0.5), ((40, 55, 85), 1.0)],
        "glow": (C_ORANGE, 0.72, 0.55, 120),
        "symbol": "star",
    },
    {
        "name": "불꽃",
        "name_en": "flame",
        "colors": [((20, 8, 5), 0.0), ((80, 20, 5), 0.45), ((160, 50, 10), 0.80), ((30, 10, 5), 1.0)],
        "glow": (C_RED, 0.65, 0.60, 150),
        "symbol": "flame",
    },
    {
        "name": "물",
        "name_en": "water",
        "colors": [((5, 15, 30), 0.0), ((10, 35, 65), 0.50), ((15, 55, 80), 0.80), ((5, 20, 40), 1.0)],
        "glow": ((30, 120, 180), 0.70, 0.55, 130),
        "symbol": "wave",
    },
    {
        "name": "용",
        "name_en": "dragon",
        "colors": [((8, 5, 20), 0.0), ((25, 15, 55), 0.45), ((60, 20, 80), 0.80), ((10, 5, 25), 1.0)],
        "glow": ((120, 50, 200), 0.65, 0.60, 130),
        "symbol": "dragon",
    },
    {
        "name": "음악",
        "name_en": "music",
        "colors": [(C_NAVY_DEEP, 0.0), ((20, 30, 50), 0.45), ((35, 50, 70), 0.80), (C_NAVY_DEEP, 1.0)],
        "glow": (C_GOLD, 0.68, 0.50, 120),
        "symbol": "note",
    },
]


def draw_symbol(draw, cx, cy, size, symbol, color, alpha=200):
    r = size // 2
    c = (*color, alpha)
    c_dim = (*color, alpha // 3)

    if symbol == "star":
        # 별 5각 + 중앙 점
        for angle_deg in range(0, 360, 72):
            angle = math.radians(angle_deg - 90)
            x1 = cx + r * math.cos(angle)
            y1 = cy + r * math.sin(angle)
            x2 = cx + (r * 0.4) * math.cos(angle + math.radians(36))
            y2 = cy + (r * 0.4) * math.sin(angle + math.radians(36))
            draw.line([(x1, y1), (cx, cy)], fill=c, width=3)

    elif symbol == "flame":
        # 불꽃 형태 (베지어 근사)
        pts = []
        for t in range(100):
            a = t / 100 * math.pi * 2
            rx = r * 0.35 * (1 + 0.4 * math.sin(3 * a))
            ry = r * 0.60 * (1 + 0.3 * math.sin(2 * a + 1))
            pts.append((cx + rx * math.cos(a), cy - ry * math.sin(a) * 0.9 + r * 0.15))
        draw.polygon(pts, fill=(*color, alpha // 2), outline=c)

    elif symbol == "wave":
        for i, y_offset in enumerate([-18, 0, 18]):
            pts = []
            for x in range(cx - r, cx + r, 4):
                t = (x - (cx - r)) / (2 * r)
                y = cy + y_offset + int(r * 0.18 * math.sin(t * math.pi * 3 + i))
                pts.append((x, y))
            draw.line(pts, fill=c if i == 1 else c_dim, width=3 if i == 1 else 2)

    elif symbol == "dragon":
        # 용 — 나선형 곡선
        pts = []
        for t in range(200):
            a = t / 200 * math.pi * 4
            rad = r * 0.1 + r * 0.7 * (t / 200)
            pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a) * 0.75))
        draw.line(pts, fill=c, width=4)
        # 뿔
        draw.polygon(
            [(cx - 10, cy - r * 0.3), (cx + 10, cy - r * 0.3), (cx, cy - r * 0.7)],
            outline=c, width=2
        )

    elif symbol == "note":
        # 음표 — 타원 + 세로선 + 꼬리
        ew = int(r * 0.35)
        eh = int(r * 0.25)
        note_cx = cx - int(r * 0.1)
        note_cy = cy + int(r * 0.25)
        draw.ellipse(
            [note_cx - ew, note_cy - eh, note_cx + ew, note_cy + eh],
            fill=c
        )
        # 세로 줄기
        draw.line(
            [(note_cx + ew, note_cy), (note_cx + ew, note_cy - int(r * 0.75))],
            fill=c, width=4
        )
        # 꼬리 (베이어 곡선 근사)
        tail_x = note_cx + ew
        tail_y_top = note_cy - int(r * 0.75)
        for i in range(20):
            t = i / 19
            x = int(tail_x + r * 0.35 * t)
            y = int(tail_y_top + r * 0.30 * t * t)
            draw.ellipse([x - 2, y - 2, x + 2, y + 2], fill=c)


def make_highlight_cover(theme):
    size = 1000
    img = Image.new("RGBA", (size, size), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    draw_vertical_gradient(draw, size, size, theme["colors"])

    glow_color, gy_frac, grad_frac, g_alpha = theme["glow"]
    glow_cy = int(size * gy_frac)
    random.seed(hash(theme["name"]) % 1000)
    draw_star_field(draw, size, size, n=60, region_top=0.0, region_bot=0.55)

    draw_radial_glow(img, size // 2, glow_cy, int(size * grad_frac), glow_color, alpha_max=g_alpha)

    # 심볼 (중앙 상단 영역)
    symbol_y = int(size * 0.38)
    draw = ImageDraw.Draw(img)
    draw_symbol(draw, size // 2, symbol_y, int(size * 0.32), theme["symbol"], glow_color, alpha=210)

    # 키워드 텍스트
    f_kr  = load_font(FONT_KR,   78)
    f_en  = load_font(FONT_SANS, 34)
    centered_text(draw, theme["name"], f_kr, int(size * 0.68), size, C_WHITE_COOL)
    centered_text(draw, theme["name_en"], f_en, int(size * 0.79), size,
                  (*glow_color[:3], 170))

    # 하단 브랜드 라벨
    f_brand = load_font(FONT_SANS, 26)
    centered_text(draw, "iteul", f_brand, int(size * 0.90), size, (*C_GOLD, 140))

    # 원형 마스크 적용
    mask = Image.new("L", (size, size), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([0, 0, size, size], fill=255)
    img.putalpha(mask)

    add_noise(img, strength=5)
    path = os.path.join(OUT_DIR, f"highlight_{theme['name_en']}.png")
    img.save(path)
    print(f"  saved: {path}")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("[ 이틀 (iteul) 이미지 생성 시작 ]")
    print()

    print("▸ 프로필 이미지 생성 중...")
    make_profile_text()
    make_profile_mood()

    print()
    print("▸ 유튜브 헤더 생성 중...")
    make_youtube_header()

    print()
    print("▸ 인스타그램 하이라이트 커버 생성 중...")
    for theme in HIGHLIGHT_THEMES:
        make_highlight_cover(theme)

    print()
    print("✓ 모든 이미지 생성 완료 →", OUT_DIR)
    print()
    for f in sorted(os.listdir(OUT_DIR)):
        full = os.path.join(OUT_DIR, f)
        sz = os.path.getsize(full)
        img = Image.open(full)
        print(f"  {f:40s}  {img.size[0]}x{img.size[1]}  ({sz // 1024} KB)")
