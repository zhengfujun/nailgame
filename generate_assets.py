"""
运行一次即可生成所有占位图片到 assets/ 文件夹。
你替换对应文件后，游戏会自动使用你的图片。
运行: python generate_assets.py
"""
import pygame
import os
import math

pygame.init()
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(os.path.join(BASE, "shapes"), exist_ok=True)
os.makedirs(os.path.join(BASE, "decos"),  exist_ok=True)
os.makedirs(os.path.join(BASE, "ui"),     exist_ok=True)

def save(surf, path):
    pygame.image.save(surf, path)
    print(f"  生成: {os.path.relpath(path)}")

# ── 甲型形状  120×180 透明底 ──────────────────────────────────────────
# 每张图只画甲型轮廓（白色填充+深边框），颜色在游戏里动态叠加。
# 替换时：同尺寸 PNG，透明底，白色区域=甲面，边框随意。

SHAPE_W, SHAPE_H = 120, 180

SHAPE_POLYS = {
    "shape_square":      [(-1,-1.4),(1,-1.4),(1,1.4),(-1,1.4)],
    "shape_round":       [(-1,-1),(0,-1.5),(1,-1),(1,1),(0,1.5),(-1,1)],
    "shape_almond":      [(-0.8,-1),(0,-1.7),(0.8,-1),(0.8,1),(0,1.3),(-0.8,1)],
    "shape_stiletto":    [(-0.8,-1),(0,-2),(0.8,-1),(0.8,1),(0,1.3),(-0.8,1)],
    "shape_squoval":     [(-1,-0.9),(-0.7,-1.2),(0.7,-1.2),(1,-0.9),(1,1),(-1,1)],
}
SHAPE_LABELS = {
    "shape_square":   "方形",
    "shape_round":    "圆形",
    "shape_almond":   "杏仁形",
    "shape_stiletto": "尖形",
    "shape_squoval":  "短方圆",
}

def make_shape(name, poly):
    surf = pygame.Surface((SHAPE_W, SHAPE_H), pygame.SRCALPHA)
    cx, cy = SHAPE_W // 2, SHAPE_H // 2
    sw, sh = SHAPE_W / 2.2, SHAPE_H / 3.2
    pts = [(int(cx + x*sw), int(cy + y*sh)) for x, y in poly]
    pygame.draw.polygon(surf, (255, 255, 255, 220), pts)        # 白色甲面
    pygame.draw.polygon(surf, (160, 120, 140, 255), pts, 2)     # 轮廓线
    # 中央写文字说明
    font = pygame.font.SysFont(None, 22)
    lbl  = SHAPE_LABELS[name]
    img  = font.render(lbl, True, (120, 80, 100))
    surf.blit(img, img.get_rect(center=(cx, cy)))
    return surf

for fname, poly in SHAPE_POLYS.items():
    s = make_shape(fname, poly)
    save(s, os.path.join(BASE, "shapes", fname + ".png"))

# ── 装饰贴图  60×60 透明底 ────────────────────────────────────────────
# 替换时：同尺寸 PNG，透明底，图案居中。
# "无" 不需要图片文件。

DECO_W, DECO_H = 60, 60

def make_deco(name):
    surf = pygame.Surface((DECO_W, DECO_H), pygame.SRCALPHA)
    cx, cy, r = DECO_W//2, DECO_H//2, 20
    font = pygame.font.SysFont(None, 18)

    if name == "deco_diamond":
        c = (150, 210, 255)
        pts = [(cx, cy-r),(cx+r,cy),(cx,cy+r),(cx-r,cy)]
        pygame.draw.polygon(surf, c, pts)
        pygame.draw.polygon(surf, (255,255,255), pts, 2)

    elif name == "deco_pearl":
        c = (230, 230, 230)
        pygame.draw.circle(surf, c, (cx, cy), r)
        pygame.draw.circle(surf, (255,255,255), (cx-r//3, cy-r//3), r//3)
        pygame.draw.circle(surf, (200,200,210), (cx, cy), r, 2)

    elif name == "deco_glitter":
        c = (255, 215, 0)
        for i in range(8):
            rad = math.radians(i*45)
            px = cx + int(math.cos(rad)*r)
            py = cy + int(math.sin(rad)*r)
            pygame.draw.circle(surf, c, (px, py), 5)
        pygame.draw.circle(surf, (255,240,150), (cx,cy), 6)

    elif name == "deco_bow":
        c = (255, 105, 180)
        pygame.draw.ellipse(surf, c, (cx-r, cy-r//2, r, r))
        pygame.draw.ellipse(surf, c, (cx,   cy-r//2, r, r))
        pygame.draw.circle(surf, (255,200,220), (cx, cy), r//3)

    elif name == "deco_flower":
        c = (255, 182, 193)
        for i in range(6):
            rad = math.radians(i*60)
            px = cx + int(math.cos(rad)*r*0.7)
            py = cy + int(math.sin(rad)*r*0.7)
            pygame.draw.circle(surf, c, (px, py), r//3)
        pygame.draw.circle(surf, (255, 230, 100), (cx, cy), r//4)

    elif name == "deco_heart":
        c = (255, 80, 80)
        pts = []
        for t_deg in range(0, 361, 5):
            t = math.radians(t_deg)
            x = r * (16*math.sin(t)**3) / 16
            y = -r * (13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t)) / 16
            pts.append((cx+int(x), cy+int(y)))
        if len(pts) > 2:
            pygame.draw.polygon(surf, c, pts)

    elif name == "deco_moon_star":
        c = (180, 180, 255)
        pygame.draw.circle(surf, c, (cx-4, cy), r*2//3)
        pygame.draw.circle(surf, (255,245,250,0), (cx+8, cy-4), r//2)  # 扣月牙
        for i in range(5):
            rad = math.radians(i*72-90)
            sx = cx+r-4 + int(math.cos(rad)*7)
            sy = cy-r+8 + int(math.sin(rad)*7)
            pygame.draw.circle(surf, (255,230,100), (sx,sy), 4)

    elif name == "deco_sticker":
        colors = [(255,200,220),(200,230,255),(200,255,210),(255,240,180)]
        for i, col in enumerate(colors):
            pygame.draw.circle(surf, col, (cx, cy), r-i*4)
        img = font.render("渐变", True, (150,100,130))
        surf.blit(img, img.get_rect(center=(cx,cy)))

    return surf

DECO_NAMES = [
    "deco_diamond", "deco_pearl", "deco_glitter", "deco_bow",
    "deco_flower",  "deco_heart", "deco_moon_star","deco_sticker",
]
for n in DECO_NAMES:
    s = make_deco(n)
    save(s, os.path.join(BASE, "decos", n + ".png"))

# ── UI 图片  ──────────────────────────────────────────────────────────

# 背景图 900×650
bg = pygame.Surface((900, 650))
bg.fill((255, 245, 250))
for i in range(0, 900, 40):
    pygame.draw.line(bg, (255, 230, 240), (i, 0), (i, 650), 1)
for j in range(0, 650, 40):
    pygame.draw.line(bg, (255, 230, 240), (0, j), (900, j), 1)
save(bg, os.path.join(BASE, "ui", "background.png"))

# 金币图标 32×32
coin = pygame.Surface((32, 32), pygame.SRCALPHA)
pygame.draw.circle(coin, (220, 170, 50), (16,16), 14)
pygame.draw.circle(coin, (255, 215, 80), (13,13), 6)
pygame.draw.circle(coin, (220, 170, 50), (16,16), 14, 2)
save(coin, os.path.join(BASE, "ui", "coin_icon.png"))

# 锁图标 32×32
lock = pygame.Surface((32, 32), pygame.SRCALPHA)
pygame.draw.rect(lock, (160,160,160), (7,15,18,14), border_radius=3)
pygame.draw.arc(lock, (160,160,160), (9,5,14,16), math.radians(0), math.radians(180), 3)
save(lock, os.path.join(BASE, "ui", "lock_icon.png"))

# 完美皇冠 48×48
crown = pygame.Surface((48, 48), pygame.SRCALPHA)
pts = [(4,38),(4,24),(14,30),(24,14),(34,30),(44,24),(44,38)]
pygame.draw.polygon(crown, (220,170,50), pts)
for x,y in [(4,24),(14,30),(24,14),(34,30),(44,24)]:
    pygame.draw.circle(crown, (255,230,80), (x,y), 4)
save(crown, os.path.join(BASE, "ui", "crown_icon.png"))

pygame.quit()
print("\n全部生成完毕！")
print("文件结构：")
print("  assets/shapes/  — 5 个甲型 (120×180 PNG)")
print("  assets/decos/   — 8 个装饰 (60×60 PNG)")
print("  assets/ui/      — 背景、金币、锁、皇冠图标")
print("\n替换规则：")
print("  保持文件名不变，尺寸建议不变，透明底 PNG。")
