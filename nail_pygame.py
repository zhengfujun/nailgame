"""
美甲工作室 - Pygame 图形版（含实时调试面板）
运行: python nail_pygame.py
调试: 按 F1 切换调试面板  |  F2 导出当前布局到 layout_export.json
依赖: pip install pygame
"""
import pygame
import sys, datetime, random, json, os, math

# ── 路径工具 ─────────────────────────────────────────────────────────

def _exe_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def _assets_dir():
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, "assets")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

SAVE_FILE   = os.path.join(_exe_dir(), "savegame.json")
LAYOUT_FILE = os.path.join(_exe_dir(), "layout_export.json")
ASSETS_DIR  = _assets_dir()

# ══════════════════════════════════════════════════════════════════════
# LAYOUT — 所有可视化调节的数值都在这里，调试面板读写此字典
# 格式: { "场景名": { "元素名": {"x":, "y":, ...} } }
# ══════════════════════════════════════════════════════════════════════
LAYOUT = {
    "hud": {
        "bar_h":        {"v": 44,  "min": 20,  "max": 80,  "label": "HUD高度"},
        "title_x":      {"v": 450, "min": 0,   "max": 900, "label": "标题X"},
        "title_y":      {"v": 22,  "min": 0,   "max": 80,  "label": "标题Y"},
        "title_size":   {"v": 26,  "min": 12,  "max": 48,  "label": "标题字号"},
        "title_color":  {"color": [255,255,255], "label": "标题颜色"},
        "coins_x":      {"v": 16,  "min": 0,   "max": 400, "label": "金币X"},
        "coins_y":      {"v": 14,  "min": 0,   "max": 80,  "label": "金币Y"},
        "coins_color":  {"color": [220,170,50],  "label": "金币颜色"},
        "score_x":      {"v": 130, "min": 0,   "max": 600, "label": "积分X"},
        "score_y":      {"v": 14,  "min": 0,   "max": 80,  "label": "积分Y"},
        "score_color":  {"color": [255,255,255], "label": "积分颜色"},
        "stat_x":       {"v": 890, "min": 400, "max": 900, "label": "统计X"},
        "stat_y":       {"v": 14,  "min": 0,   "max": 80,  "label": "统计Y"},
        "stat_color":   {"color": [255,220,235], "label": "统计颜色"},
    },
    "menu": {
        "welcome_x":    {"v": 450, "min": 0,   "max": 900, "label": "欢迎语X"},
        "welcome_y":    {"v": 90,  "min": 44,  "max": 600, "label": "欢迎语Y"},
        "welcome_size": {"v": 16,  "min": 10,  "max": 40,  "label": "欢迎语字号"},
        "welcome_color":{"color": [120,90,110], "label": "欢迎语颜色"},
        "btn_x":        {"v": 310, "min": 0,   "max": 700, "label": "按钮X"},
        "btn_y0":       {"v": 130, "min": 44,  "max": 500, "label": "按钮起始Y"},
        "btn_gap":      {"v": 70,  "min": 40,  "max": 120, "label": "按钮间距"},
        "btn_w":        {"v": 280, "min": 100, "max": 500, "label": "按钮宽"},
        "btn_h":        {"v": 52,  "min": 24,  "max": 100, "label": "按钮高"},
    },
    "picker": {
        "order_name_x": {"v": 20,  "min": 0,   "max": 400, "label": "顾客名X"},
        "order_name_y": {"v": 54,  "min": 44,  "max": 300, "label": "顾客名Y"},
        "order_name_color":{"color":[60,40,60], "label": "顾客名颜色"},
        "order_req_y":  {"v": 78,  "min": 44,  "max": 300, "label": "要求文字Y"},
        "order_req_color":{"color":[200,120,160],"label":"要求文字颜色"},
        "order_reward_y":{"v":104, "min": 44,  "max": 300, "label": "奖励文字Y"},
        "order_reward_color":{"color":[220,170,50],"label":"奖励颜色"},
        "order_nail_x": {"v": 110, "min": 0,   "max": 400, "label": "目标甲X"},
        "order_nail_y": {"v": 220, "min": 44,  "max": 400, "label": "目标甲Y"},
        "order_nail_w": {"v": 70,  "min": 30,  "max": 150, "label": "目标甲宽"},
        "order_nail_h": {"v": 110, "min": 50,  "max": 200, "label": "目标甲高"},
        "preview_x":    {"v": 310, "min": 100, "max": 600, "label": "预览甲X"},
        "preview_y":    {"v": 195, "min": 44,  "max": 400, "label": "预览甲Y"},
        "preview_w":    {"v": 90,  "min": 30,  "max": 200, "label": "预览甲宽"},
        "preview_h":    {"v": 140, "min": 50,  "max": 300, "label": "预览甲高"},
        "shape_btn_y":  {"v": 340, "min": 200, "max": 580, "label": "甲型按钮Y"},
        "shape_btn_x0": {"v": 30,  "min": 0,   "max": 200, "label": "甲型按钮X起"},
        "shape_btn_gap":{"v": 166, "min": 80,  "max": 250, "label": "甲型按钮间距"},
        "color_x0":     {"v": 30,  "min": 0,   "max": 200, "label": "底色X起"},
        "color_y0":     {"v": 420, "min": 200, "max": 580, "label": "底色Y起"},
        "color_gap":    {"v": 72,  "min": 50,  "max": 120, "label": "底色间距"},
        "color_row_gap":{"v": 86,  "min": 60,  "max": 140, "label": "底色行距"},
        "deco_x0":      {"v": 500, "min": 300, "max": 800, "label": "装饰X起"},
        "deco_y0":      {"v": 420, "min": 200, "max": 580, "label": "装饰Y起"},
        "deco_gap":     {"v": 72,  "min": 50,  "max": 120, "label": "装饰间距"},
        "deco_row_gap": {"v": 86,  "min": 60,  "max": 140, "label": "装饰行距"},
    },
    "result": {
        "title_y":      {"v": 58,  "min": 44,  "max": 200, "label": "标题Y"},
        "mood_y":       {"v": 98,  "min": 44,  "max": 300, "label": "对白Y"},
        "mood_color":   {"color": [120,90,110], "label": "对白颜色"},
        "label_y":      {"v": 135, "min": 44,  "max": 300, "label": "标签Y"},
        "label_color":  {"color": [60,40,60],   "label": "标签颜色"},
        "nail_l_x":     {"v": 225, "min": 0,   "max": 450, "label": "左甲X"},
        "nail_r_x":     {"v": 675, "min": 450, "max": 900, "label": "右甲X"},
        "nail_y":       {"v": 260, "min": 100, "max": 500, "label": "甲Y"},
        "nail_w":       {"v": 90,  "min": 30,  "max": 200, "label": "甲宽"},
        "nail_h":       {"v": 140, "min": 50,  "max": 300, "label": "甲高"},
        "compare_y0":   {"v": 350, "min": 200, "max": 500, "label": "对比文字Y起"},
        "compare_gap":  {"v": 26,  "min": 16,  "max": 50,  "label": "对比行距"},
        "coin_y":       {"v": 440, "min": 300, "max": 600, "label": "金币变化Y"},
    },
    "result_free": {
        "title_y":      {"v": 58,  "min": 44,  "max": 200, "label": "标题Y"},
        "title_color":  {"color": [200,120,160], "label": "标题颜色"},
        "nail_x":       {"v": 450, "min": 100, "max": 800, "label": "甲X"},
        "nail_y":       {"v": 280, "min": 100, "max": 500, "label": "甲Y"},
        "nail_w":       {"v": 110, "min": 40,  "max": 250, "label": "甲宽"},
        "nail_h":       {"v": 170, "min": 60,  "max": 350, "label": "甲高"},
        "info_y":       {"v": 390, "min": 200, "max": 580, "label": "信息Y"},
        "info_color":   {"color": [120,90,110], "label": "信息颜色"},
        "count_y":      {"v": 425, "min": 200, "max": 580, "label": "件数Y"},
        "count_color":  {"color": [200,170,190],"label": "件数颜色"},
    },
    "gallery": {
        "title_y":      {"v": 55,  "min": 44,  "max": 200, "label": "标题Y"},
        "title_color":  {"color": [200,120,160], "label": "标题颜色"},
        "start_y":      {"v": 90,  "min": 44,  "max": 300, "label": "卡片起始Y"},
        "card_x0":      {"v": 30,  "min": 0,   "max": 200, "label": "卡片X起"},
        "thumb_w":      {"v": 100, "min": 50,  "max": 200, "label": "缩略图宽"},
        "thumb_h":      {"v": 140, "min": 60,  "max": 250, "label": "缩略图高"},
        "thumb_pad":    {"v": 18,  "min": 4,   "max": 60,  "label": "卡片间距"},
        "cols":         {"v": 5,   "min": 2,   "max": 8,   "label": "列数"},
    },
    "shop": {
        "title_y":      {"v": 55,  "min": 44,  "max": 200, "label": "标题Y"},
        "title_color":  {"color": [200,120,160], "label": "标题颜色"},
        "item_y0":      {"v": 100, "min": 44,  "max": 300, "label": "商品Y起"},
        "item_gap":     {"v": 50,  "min": 30,  "max": 100, "label": "商品间距"},
        "item_color":   {"color": [60,40,60],   "label": "商品名颜色"},
        "preview_x":    {"v": 20,  "min": 0,   "max": 200, "label": "预览X"},
        "name_x":       {"v": 90,  "min": 40,  "max": 400, "label": "名字X"},
        "btn_x":        {"v": 740, "min": 400, "max": 880, "label": "按钮X"},
        "btn_w":        {"v": 130, "min": 60,  "max": 250, "label": "按钮宽"},
    },
}

def L(scene, key):
    """取数值型参数"""
    return LAYOUT[scene][key]["v"]

def LC(scene, key):
    """取颜色参数，返回 (R,G,B) tuple"""
    return tuple(LAYOUT[scene][key]["color"])

def _is_color(info):
    return "color" in info

# 快照：记录"上次保存"时的值，用于重置
_LAYOUT_SNAPSHOT = {}

def _snapshot_layout():
    """把当前 LAYOUT 所有值复制到快照"""
    for scene, items in LAYOUT.items():
        _LAYOUT_SNAPSHOT[scene] = {}
        for key, info in items.items():
            if _is_color(info):
                _LAYOUT_SNAPSHOT[scene][key] = list(info["color"])
            else:
                _LAYOUT_SNAPSHOT[scene][key] = info["v"]

def reset_item(scene, key):
    """把单个条目恢复到快照值"""
    snap = _LAYOUT_SNAPSHOT.get(scene, {}).get(key)
    if snap is None:
        return
    info = LAYOUT[scene][key]
    if _is_color(info):
        info["color"] = list(snap)
    else:
        info["v"] = snap

def load_layout():
    path = os.path.join(_exe_dir(), "layout_export.json")
    if not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            saved = json.load(f)
        for scene, items in saved.items():
            if scene in LAYOUT:
                for key, val in items.items():
                    if key in LAYOUT[scene]:
                        info = LAYOUT[scene][key]
                        if _is_color(info) and isinstance(val, list):
                            info["color"] = val
                        elif not _is_color(info):
                            info["v"] = val
    except Exception:
        pass
    _snapshot_layout()   # 加载完毕后立即拍快照

def export_layout():
    flat = {}
    for scene, items in LAYOUT.items():
        flat[scene] = {}
        for k, info in items.items():
            flat[scene][k] = info["color"] if _is_color(info) else info["v"]
    with open(LAYOUT_FILE, "w", encoding="utf-8") as f:
        json.dump(flat, f, ensure_ascii=False, indent=2)
    _snapshot_layout()   # 导出后更新快照，下次重置以此为基准
    py_path = os.path.join(_exe_dir(), "layout_export.py")
    with open(py_path, "w", encoding="utf-8") as f:
        f.write("# 复制以下内容替换 LAYOUT 中对应的值\n")
        for scene, items in LAYOUT.items():
            f.write(f"\n# ── {scene} ──\n")
            for key, info in items.items():
                val = info["color"] if _is_color(info) else info["v"]
                f.write(f"# {info['label']}: {val}\n")

# ── 存档 ─────────────────────────────────────────────────────────────

_WEB_SAVE_KEY = "nailstudio_save"

def _is_web_env():
    import sys
    return sys.platform in ("emscripten", "wasi")

def save_game():
    print(f"[save] called, _is_web={_is_web_env()}, coins={state['coins']}")
    data = {
        "coins": state["coins"], "score": state["score"],
        "orders_done": state["orders_done"], "orders_correct": state["orders_correct"],
        "unlocked_colors": list(state["unlocked_colors"]),
        "unlocked_decos":  list(state["unlocked_decos"]),
        "my_works": [{k: (list(v) if isinstance(v, tuple) else v)
                      for k, v in w.items()} for w in state["my_works"]],
    }
    try:
        if _is_web_env():
            from js import localStorage
            localStorage.setItem(_WEB_SAVE_KEY, json.dumps(data, ensure_ascii=True))
        else:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[save] error: {e}")

def load_game():
    try:
        if _is_web_env():
            from js import localStorage
            raw = localStorage.getItem(_WEB_SAVE_KEY)
            if not raw:
                return
            # 检测乱码：正常存档不含 \x83 这样的原始字节转义
            if "\\x83" in raw or "Ã\x83" in raw:
                print("[load] detected corrupted save, clearing")
                localStorage.removeItem(_WEB_SAVE_KEY)
                return
            data = json.loads(raw)
        else:
            if not os.path.exists(SAVE_FILE):
                return
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        state["coins"]           = data.get("coins", 0)
        state["score"]           = data.get("score", 0)
        state["orders_done"]     = data.get("orders_done", 0)
        state["orders_correct"]  = data.get("orders_correct", 0)
        state["unlocked_colors"] = set(data.get("unlocked_colors", []))
        state["unlocked_decos"]  = set(data.get("unlocked_decos", []))
        for w in data.get("my_works", []):
            if "color_rgb" in w and isinstance(w["color_rgb"], list):
                w["color_rgb"] = tuple(w["color_rgb"])
            if "deco_color" in w and isinstance(w["deco_color"], list):
                w["deco_color"] = tuple(w["deco_color"])
            state["my_works"].append(w)
    except Exception as e:
        print(f"[load] error: {e}")
    except Exception:
        pass

# ── 游戏数据 ─────────────────────────────────────────────────────────

NAIL_SHAPES = ["方形", "圆形", "杏仁形", "尖形", "短方圆"]

ALL_COLORS = [
    ("纯黑",  0,  (30,  30,  30)),
    ("纯白",  0,  (245, 245, 245)),
    ("樱花粉", 0,  (255, 182, 193)),
    ("雾霾蓝", 0,  (176, 196, 222)),
    ("酒红",  0,  (139, 0,   0)),
    ("裸色",  0,  (210, 180, 140)),
    ("薄荷绿", 30, (152, 251, 152)),
    ("香芋紫", 30, (180, 130, 210)),
    ("珊瑚橙", 50, (255, 127, 80)),
    ("星空黑", 80, (20,  20,  60)),
    ("玫瑰金", 100,(212, 160, 140)),
]

ALL_DECOS = [
    ("无",    0,  (0,0,0,0),    None),
    ("小钻",   0,  (200,230,255), "diamond"),
    ("珍珠",   0,  (240,240,240), "pearl"),
    ("亮片",   0,  (255,215,0),  "glitter"),
    ("蝴蝶结",  0,  (255,105,180),"bow"),
    ("花朵",   40, (255,182,193),"flower"),
    ("爱心",   40, (255,80,80),  "heart"),
    ("月亮星星", 60, (200,200,255),"moon"),
    ("渐变贴纸", 90, (180,255,200),"sticker"),
]

CUSTOMER_NAMES = ["小美","lily","欣欣","雯雯","Anna","婷婷","可可","Sophie","晓晓","Mia"]
CUSTOMER_MOODS = {"happy":"高兴地说","shy":"害羞地说","bossy":"认真地说","chill":"随意地说"}

state = {
    "coins": 0, "score": 0, "orders_done": 0, "orders_correct": 0,
    "unlocked_colors": set(), "unlocked_decos": set(), "my_works": [],
}

def init_unlocks():
    load_game()
    for name, cost, *_ in ALL_COLORS:
        if cost == 0: state["unlocked_colors"].add(name)
    for name, cost, *_ in ALL_DECOS:
        if cost == 0: state["unlocked_decos"].add(name)

def available_colors():
    return [t for t in ALL_COLORS if t[0] in state["unlocked_colors"]]

def available_decos():
    return [t for t in ALL_DECOS if t[0] in state["unlocked_decos"]]

def generate_order():
    name  = random.choice(CUSTOMER_NAMES)
    mood  = random.choice(list(CUSTOMER_MOODS.keys()))
    shape = random.choice(NAIL_SHAPES)
    color = random.choice(available_colors())[0]
    deco  = random.choice(available_decos())[0]
    tip   = random.randint(1, 3)
    reward = {1:10, 2:18, 3:30}[tip]
    return {"name":name,"mood":mood,"shape":shape,"color":color,
            "deco":deco,"tip":tip,"reward":reward}

# ── 窗口尺寸 ─────────────────────────────────────────────────────────

GW, GH = 900, 650      # 游戏画面尺寸（不变）
DBG_W  = 340           # 调试面板宽
FPS    = 60

# 调色板
BG        = (255, 245, 250)
PANEL     = (255, 255, 255)
ACCENT    = (255, 150, 180)
ACCENT2   = (200, 120, 160)
GOLD      = (220, 170, 50)
TEXT_DARK = (60,  40,  60)
TEXT_MID  = (120, 90, 110)
TEXT_LITE = (200, 170, 190)
BTN_IDLE  = (255, 220, 235)
BTN_HOV   = (255, 190, 215)
BTN_SEL   = (255, 150, 180)
BTN_LOCK  = (210, 210, 210)
GREEN_OK  = (80,  180, 100)
RED_ERR   = (220, 80,  80)
YELLOW_MID= (220, 180, 50)

DBG_BG    = (30,  30,  40)
DBG_PANEL = (45,  45,  58)
DBG_SEL   = (70,  70,  90)
DBG_TEXT  = (220, 220, 230)
DBG_DIM   = (120, 120, 140)
DBG_ACC   = (120, 200, 255)
DBG_GREEN = (80,  200, 120)

# ── 字体 ─────────────────────────────────────────────────────────────

_font_obj_cache = {}

def load_fonts():
    # 候选字体路径：优先捆绑的 ttf，其次系统字体
    candidates = [
        "font/NotoSansCJK.ttf",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "font", "NotoSansCJK.ttf"),
    ]
    found = None
    for p in candidates:
        if os.path.exists(p):
            found = p
            break
    if not found:
        for c in ["microsoftyahei", "simhei", "simsun", "notosanscjk", "wqymicrohei"]:
            f = pygame.font.match_font(c)
            if f:
                found = f
                break
    def mk(size):
        if size not in _font_obj_cache:
            _font_obj_cache[size] = (pygame.font.Font(found, size) if found
                                     else pygame.font.SysFont(None, size))
        return _font_obj_cache[size]
    return mk(13), mk(16), mk(20), mk(26), mk(34)

# ── 资源加载 ─────────────────────────────────────────────────────────

SHAPE_FILE = {"方形":"shape_square","圆形":"shape_round","杏仁形":"shape_almond",
              "尖形":"shape_stiletto","短方圆":"shape_squoval"}
DECO_FILE  = {"小钻":"deco_diamond","珍珠":"deco_pearl","亮片":"deco_glitter",
              "蝴蝶结":"deco_bow","花朵":"deco_flower","爱心":"deco_heart",
              "月亮星星":"deco_moon_star","渐变贴纸":"deco_sticker"}

_img_cache = {}

def load_img(path, size=None):
    key = (path, size)
    if key not in _img_cache:
        _img_cache[key] = (pygame.image.load(path).convert_alpha()
                           if os.path.exists(path) else None)
        if _img_cache[key] and size:
            _img_cache[key] = pygame.transform.smoothscale(_img_cache[key], size)
    return _img_cache[key]

def get_shape_img(name, size):
    fn = SHAPE_FILE.get(name)
    return load_img(os.path.join(ASSETS_DIR,"shapes",fn+".png"), size) if fn else None

def get_deco_img(name, size):
    fn = DECO_FILE.get(name)
    return load_img(os.path.join(ASSETS_DIR,"decos",fn+".png"), size) if fn else None

def get_ui_img(name, size=None):
    return load_img(os.path.join(ASSETS_DIR,"ui",name), size)

# ── 美甲绘制 ─────────────────────────────────────────────────────────

SHAPE_POLYS = {
    "方形":  [(-1,-1.4),(1,-1.4),(1,1.4),(-1,1.4)],
    "圆形":  [(-1,-1),(0,-1.5),(1,-1),(1,1),(0,1.5),(-1,1)],
    "杏仁形":[(-0.8,-1),(0,-1.7),(0.8,-1),(0.8,1),(0,1.3),(-0.8,1)],
    "尖形":  [(-0.8,-1),(0,-2),(0.8,-1),(0.8,1),(0,1.3),(-0.8,1)],
    "短方圆":[(-1,-0.9),(-0.7,-1.2),(0.7,-1.2),(1,-0.9),(1,1),(-1,1)],
}

def scale_poly(poly, cx, cy, w, h):
    sw, sh = w/2.2, h/3.2
    return [(int(cx+x*sw), int(cy+y*sh)) for x,y in poly]

def draw_deco(surf, deco_name, cx, cy, r, color):
    if deco_name == "无" or color is None: return
    c = color[:3]
    if deco_name == "小钻":
        pts = [(cx,cy-r),(cx+r,cy),(cx,cy+r),(cx-r,cy)]
        pygame.draw.polygon(surf,c,pts); pygame.draw.polygon(surf,(255,255,255),pts,1)
    elif deco_name == "珍珠":
        pygame.draw.circle(surf,c,(cx,cy),r)
        pygame.draw.circle(surf,(255,255,255),(cx-r//3,cy-r//3),r//3)
    elif deco_name == "亮片":
        for a,dr in [(0,0),(45,r//2),(90,0),(135,r//2),(180,0),(225,r//2),(270,0),(315,r//2)]:
            rad=math.radians(a)
            pygame.draw.circle(surf,c,(cx+int(math.cos(rad)*(r+dr//2)),cy+int(math.sin(rad)*(r+dr//2))),max(2,r//4))
    elif deco_name == "蝴蝶结":
        pygame.draw.ellipse(surf,c,(cx-r,cy-r//2,r,r))
        pygame.draw.ellipse(surf,c,(cx,cy-r//2,r,r))
        pygame.draw.circle(surf,(255,255,255),(cx,cy),r//3)
    elif deco_name == "花朵":
        for i in range(6):
            rad=math.radians(i*60)
            pygame.draw.circle(surf,c,(cx+int(math.cos(rad)*r*0.7),cy+int(math.sin(rad)*r*0.7)),r//3)
        pygame.draw.circle(surf,(255,230,100),(cx,cy),r//4)
    elif deco_name == "爱心":
        pts=[]
        for t in range(0,361,6):
            t=math.radians(t)
            pts.append((cx+int(r*(16*math.sin(t)**3)/16),cy+int(-r*(13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t))/16)))
        if len(pts)>2: pygame.draw.polygon(surf,c,pts)
    elif deco_name == "月亮星星":
        pygame.draw.circle(surf,c,(cx-r//4,cy),r*2//3)
        pygame.draw.circle(surf,(255,255,255),(cx+r//6,cy-r//4),r//2)
        for i in range(5):
            rad=math.radians(i*72-90)
            pygame.draw.circle(surf,(255,230,100),(cx+r+int(math.cos(rad)*r//3),cy-r//2+int(math.sin(rad)*r//3)),max(2,r//5))
    elif deco_name == "渐变贴纸":
        for i in range(r,0,-2):
            ratio=i/r
            pygame.draw.circle(surf,(int(c[0]*ratio+255*(1-ratio)),int(c[1]*ratio+200*(1-ratio)),int(c[2]*ratio+220*(1-ratio))),(cx,cy),i)

def draw_nail_graphic(surf, shape, color_rgb, deco_name, deco_color, cx, cy, w=80, h=130, border=True):
    img = get_shape_img(shape, (w,h))
    if img:
        tinted = img.copy()
        tint = pygame.Surface((w,h), pygame.SRCALPHA)
        tint.fill((*color_rgb, 180))
        tinted.blit(tint,(0,0),special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(tinted,(cx-w//2,cy-h//2))
    else:
        poly = SHAPE_POLYS.get(shape, SHAPE_POLYS["方形"])
        pts  = scale_poly(poly,cx,cy,w,h)
        pygame.draw.polygon(surf,color_rgb,pts)
        try:
            gl   = tuple(min(255,v+60) for v in color_rgb)
            gloss= pygame.Surface((w,h),pygame.SRCALPHA)
            pygame.draw.polygon(gloss,(*gl,80),scale_poly(poly,w//2-4,h//2-6,w*.4,h*.35))
            surf.blit(gloss,(cx-w//2,cy-h//2))
        except: pass
        if border: pygame.draw.polygon(surf,(180,140,160),pts,2)
    if deco_name and deco_name != "无":
        di = get_deco_img(deco_name,(w//2,w//2))
        if di:  surf.blit(di,(cx-w//4,cy+4))
        elif deco_color: draw_deco(surf,deco_name,cx,cy+10,10,deco_color)

# ── UI 基础 ──────────────────────────────────────────────────────────

def draw_rrect(surf, color, rect, r=10, bw=0, bc=None):
    pygame.draw.rect(surf,color,rect,border_radius=r)
    if bw and bc: pygame.draw.rect(surf,bc,rect,bw,border_radius=r)

def draw_text(surf, text, font, color, x, y, anchor="topleft"):
    img = font.render(text, True, color)
    r   = img.get_rect(**{anchor:(x,y)})
    surf.blit(img,r)
    return r

class Button:
    def __init__(self, rect, label, font, idle=BTN_IDLE, hover=BTN_HOV,
                 sel=BTN_SEL, text_color=TEXT_DARK, selected=False, locked=False, tag=None):
        self.rect=pygame.Rect(rect); self.label=label; self.font=font
        self.idle=idle; self.hover=hover; self.sel_color=sel
        self.text_color=text_color; self.selected=selected; self.locked=locked; self.tag=tag
    def draw(self, surf, mouse):
        hov=self.rect.collidepoint(mouse)
        bg = BTN_LOCK if self.locked else (self.sel_color if self.selected else (self.hover if hov else self.idle))
        draw_rrect(surf,bg,self.rect,r=8,bw=2,bc=ACCENT if self.selected else (200,180,190))
        draw_text(surf,self.label,self.font,TEXT_LITE if self.locked else self.text_color,
                  self.rect.centerx,self.rect.centery,"center")
    def is_clicked(self,event,mouse):
        return (not self.locked and event.type==pygame.MOUSEBUTTONDOWN
                and event.button==1 and self.rect.collidepoint(mouse))

class ColorSwatch:
    def __init__(self,rect,name,rgb,cost,font,unlocked=True,selected=False):
        self.rect=pygame.Rect(rect);self.name=name;self.rgb=rgb;self.cost=cost
        self.font=font;self.unlocked=unlocked;self.selected=selected
    def draw(self,surf,mouse):
        hov=self.rect.collidepoint(mouse)
        c=self.rgb if self.unlocked else (180,180,180)
        draw_rrect(surf,c,self.rect,r=6,bw=3,bc=ACCENT if self.selected else ((255,255,255) if hov else (200,190,200)))
        if not self.unlocked:
            draw_text(surf,f"{self.cost}G",self.font,(100,100,100),self.rect.centerx,self.rect.centery,"center")
    def is_clicked(self,event,mouse):
        return self.unlocked and event.type==pygame.MOUSEBUTTONDOWN and event.button==1 and self.rect.collidepoint(mouse)

class DecoSwatch:
    def __init__(self,rect,name,deco_color,cost,font,unlocked=True,selected=False):
        self.rect=pygame.Rect(rect);self.name=name;self.deco_color=deco_color
        self.cost=cost;self.font=font;self.unlocked=unlocked;self.selected=selected
    def draw(self,surf,mouse):
        hov=self.rect.collidepoint(mouse)
        bg=(250,250,250) if self.unlocked else (200,200,200)
        draw_rrect(surf,bg,self.rect,r=6,bw=3,bc=ACCENT if self.selected else ((255,255,255) if hov else (200,190,200)))
        if self.unlocked and self.name!="无":
            di=get_deco_img(self.name,(44,44))
            if di: surf.blit(di,di.get_rect(center=(self.rect.centerx,self.rect.centery-4)))
            else: draw_deco(surf,self.name,self.rect.centerx,self.rect.centery-6,10,self.deco_color)
        if not self.unlocked:
            li=get_ui_img("lock_icon.png",(24,24))
            if li: surf.blit(li,li.get_rect(center=(self.rect.centerx,self.rect.centery-6)))
            draw_text(surf,f"{self.cost}G",self.font,(100,100,100),self.rect.centerx,self.rect.bottom-14,"center")
    def is_clicked(self,event,mouse):
        return self.unlocked and event.type==pygame.MOUSEBUTTONDOWN and event.button==1 and self.rect.collidepoint(mouse)

# ── HUD ──────────────────────────────────────────────────────────────

def draw_hud(surf, fonts):
    f_s,f_m,_,f_l,_=fonts
    bh = L("hud","bar_h")
    pygame.draw.rect(surf, ACCENT, (0,0,GW,bh))
    fi = _font_obj_cache.get(L("hud","title_size"), fonts[3])
    draw_text(surf,"美甲工作室",fi,      LC("hud","title_color"), L("hud","title_x"),L("hud","title_y"),"center")
    draw_text(surf,f"金币 {state['coins']}",f_m,LC("hud","coins_color"), L("hud","coins_x"),L("hud","coins_y"))
    draw_text(surf,f"积分 {state['score']}",f_m,LC("hud","score_color"),L("hud","score_x"),L("hud","score_y"))
    draw_text(surf,f"接单 {state['orders_done']}  完美 {state['orders_correct']}",
              f_s,LC("hud","stat_color"),L("hud","stat_x"),L("hud","stat_y"),"topright")

# ── 场景基类 ─────────────────────────────────────────────────────────

class Scene:
    scene_key = ""
    def handle(self,event,mouse): pass
    def update(self): pass
    def draw(self,surf,mouse): pass

# ── 主菜单 ───────────────────────────────────────────────────────────

class MenuScene(Scene):
    scene_key = "menu"
    def __init__(self,fonts,switch):
        self.fonts=fonts; self.switch=switch
        self._build()
    def _build(self):
        f=self.fonts[2]
        bx=L("menu","btn_x"); y0=L("menu","btn_y0"); gap=L("menu","btn_gap")
        bw=L("menu","btn_w"); bh=L("menu","btn_h")
        self.btns=[
            Button((bx,y0+gap*0,bw,bh),"接受顾客订单  赚金币",f,tag="order"),
            Button((bx,y0+gap*1,bw,bh),"自由创作",f,tag="free"),
            Button((bx,y0+gap*2,bw,bh),"查看我的作品",f,tag="gallery"),
            Button((bx,y0+gap*3,bw,bh),"解锁商店",f,tag="shop"),
            Button((bx,y0+gap*4,bw,bh),"退出",f,idle=(255,200,200),hover=(255,160,160),tag="quit"),
        ]
    def handle(self,event,mouse):
        for b in self.btns:
            if b.is_clicked(event,mouse):
                if b.tag=="quit": save_game(); pygame.quit(); sys.exit()
                self.switch(b.tag)
    def draw(self,surf,mouse):
        surf.fill(BG); draw_hud(surf,self.fonts)
        fi=_font_obj_cache.get(L("menu","welcome_size"),self.fonts[1])
        draw_text(surf,"欢迎光临！选择你想做的事~",fi,LC("menu","welcome_color"),L("menu","welcome_x"),L("menu","welcome_y"),"center")
        for b in self.btns: b.draw(surf,mouse)

# ── 选择面板 ─────────────────────────────────────────────────────────

class PickerScene(Scene):
    scene_key = "picker"
    def __init__(self,fonts,switch,mode="free"):
        self.fonts=fonts;self.switch=switch;self.mode=mode
        self.order=generate_order() if mode=="order" else None
        self.sel_shape=0;self.sel_color=0;self.sel_deco=0
        self._build_widgets()
    def _build_widgets(self):
        f_s,f_m,_,_,_=self.fonts
        self.shape_btns=[]
        for i,name in enumerate(NAIL_SHAPES):
            bx=L("picker","shape_btn_x0")+i*L("picker","shape_btn_gap")
            self.shape_btns.append(Button((bx,L("picker","shape_btn_y"),150,40),name,f_m,tag=i,selected=(i==0)))
        self.color_swatches=[]
        for i,(name,cost,rgb) in enumerate(ALL_COLORS):
            sx=L("picker","color_x0")+i%6*L("picker","color_gap")
            sy=L("picker","color_y0")+i//6*L("picker","color_row_gap")
            unlocked=name in state["unlocked_colors"]
            self.color_swatches.append(ColorSwatch((sx,sy,60,60),name,rgb,cost,f_s,unlocked=unlocked))
        for i,sw in enumerate(self.color_swatches):
            if sw.unlocked: self.sel_color=i; sw.selected=True; break
        self.deco_swatches=[]
        for i,(name,cost,dc,_) in enumerate(ALL_DECOS):
            sx=L("picker","deco_x0")+i%5*L("picker","deco_gap")
            sy=L("picker","deco_y0")+i//5*L("picker","deco_row_gap")
            unlocked=name in state["unlocked_decos"]
            self.deco_swatches.append(DecoSwatch((sx,sy,60,60),name,dc,cost,f_s,unlocked=unlocked))
        for i,sw in enumerate(self.deco_swatches):
            if sw.unlocked: self.sel_deco=i; sw.selected=True; break
        self.btn_confirm=Button((GW-160,GH-60,140,42),"完成！",self.fonts[2],idle=GREEN_OK,hover=(60,210,80),text_color=(255,255,255))
        self.btn_back=Button((20,GH-60,100,42),"返回",self.fonts[2],idle=(230,210,220),hover=(210,180,200))
    def _cur_color(self): return ALL_COLORS[self.sel_color]
    def _cur_deco(self):  return ALL_DECOS[self.sel_deco]
    def handle(self,event,mouse):
        if self.btn_back.is_clicked(event,mouse): self.switch("menu"); return
        if self.btn_confirm.is_clicked(event,mouse): self._finish(); return
        for i,b in enumerate(self.shape_btns):
            if b.is_clicked(event,mouse):
                self.sel_shape=i
                for bb in self.shape_btns: bb.selected=False
                b.selected=True
        for i,sw in enumerate(self.color_swatches):
            if sw.is_clicked(event,mouse):
                self.sel_color=i
                for s in self.color_swatches: s.selected=False
                sw.selected=True
        for i,sw in enumerate(self.deco_swatches):
            if sw.is_clicked(event,mouse):
                self.sel_deco=i
                for s in self.deco_swatches: s.selected=False
                sw.selected=True
    def _finish(self):
        shape=NAIL_SHAPES[self.sel_shape]
        cname,_,crgb=self._cur_color()
        dname,_,dcolor,_=self._cur_deco()
        ts=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        if self.mode=="order":
            o=self.order
            cs=(shape==o["shape"]); cc=(cname==o["color"]); cd=(dname==o["deco"])
            ac=cs and cc and cd; hits=sum([cs,cc,cd]); state["orders_done"]+=1
            if ac:
                state["orders_correct"]+=1; earned=o["reward"]; state["coins"]+=earned; state["score"]+=10
                result=("perfect",earned)
            elif hits==2:
                earned=o["reward"]//2; state["coins"]+=earned; state["score"]+=3
                wrong=[k for k,v in zip(["甲型","底色","装饰"],[cs,cc,cd]) if not v]
                result=("ok",earned,wrong[0])
            elif hits==1:
                state["score"]=max(0,state["score"]-2); result=("bad",0)
            else:
                state["score"]=max(0,state["score"]-5); result=("fail",0)
            state["my_works"].append({"shape":shape,"color":cname,"color_rgb":crgb,"deco":dname,"deco_color":dcolor,"time":ts,"perfect":ac})
            save_game()
            self.switch("result",{"shape":shape,"color_rgb":crgb,"deco":dname,"deco_color":dcolor,"cname":cname,"order":o,"result":result,"correct_shape":cs,"correct_color":cc,"correct_deco":cd})
        else:
            state["my_works"].append({"shape":shape,"color":cname,"color_rgb":crgb,"deco":dname,"deco_color":dcolor,"time":ts,"perfect":False})
            save_game()
            self.switch("result_free",{"shape":shape,"color_rgb":crgb,"deco":dname,"deco_color":dcolor,"cname":cname})
    def draw(self,surf,mouse):
        surf.fill(BG); draw_hud(surf,self.fonts)
        f_s,f_m,f_n,f_l,_=self.fonts
        if self.mode=="order" and self.order:
            o=self.order; tag=["","普通","加急","豪华"][o["tip"]]; mood=CUSTOMER_MOODS[o["mood"]]
            draw_text(surf,f"顾客 {o['name']} [{tag}] {mood}：",f_m,LC("picker","order_name_color"),L("picker","order_name_x"),L("picker","order_name_y"))
            draw_text(surf,f"「{o['shape']} + {o['color']} + {o['deco']}」",f_n,LC("picker","order_req_color"),L("picker","order_name_x"),L("picker","order_req_y"))
            draw_text(surf,f"完成奖励 {o['reward']} 金币",f_m,LC("picker","order_reward_color"),L("picker","order_name_x"),L("picker","order_reward_y"))
            oc_rgb=next((rgb for n,_,rgb in ALL_COLORS if n==o["color"]),(200,200,200))
            od_col=next((dc for n,_,dc,__ in ALL_DECOS if n==o["deco"]),None)
            draw_nail_graphic(surf,o["shape"],oc_rgb,o["deco"],od_col,L("picker","order_nail_x"),L("picker","order_nail_y"),L("picker","order_nail_w"),L("picker","order_nail_h"))
        else:
            draw_text(surf,"自由创作",f_l,ACCENT2,20,56)
        cname,_,crgb=self._cur_color(); dname,_,dcolor,_=self._cur_deco()
        draw_text(surf,"预览：",f_s,TEXT_MID,L("picker","preview_x")-90,60)
        draw_nail_graphic(surf,NAIL_SHAPES[self.sel_shape],crgb,dname,dcolor,L("picker","preview_x"),L("picker","preview_y"),L("picker","preview_w"),L("picker","preview_h"))
        draw_text(surf,NAIL_SHAPES[self.sel_shape],f_s,TEXT_MID,L("picker","preview_x"),L("picker","preview_y")+L("picker","preview_h")//2+10,"center")
        draw_text(surf,"甲型",f_m,TEXT_DARK,L("picker","shape_btn_x0"),L("picker","shape_btn_y")-22)
        for b in self.shape_btns: b.draw(surf,mouse)
        draw_text(surf,"底色",f_m,TEXT_DARK,L("picker","color_x0"),L("picker","color_y0")-22)
        for sw in self.color_swatches:
            sw.rect.x=L("picker","color_x0")+(list(ALL_COLORS).index((sw.name,sw.cost,sw.rgb))%6)*L("picker","color_gap")
            sw.rect.y=L("picker","color_y0")+(list(ALL_COLORS).index((sw.name,sw.cost,sw.rgb))//6)*L("picker","color_row_gap")
            sw.draw(surf,mouse)
            tc=ACCENT if sw.selected else TEXT_MID
            draw_text(surf,sw.name,f_s,tc,sw.rect.centerx,sw.rect.bottom+2,"midtop")
        draw_text(surf,"装饰",f_m,TEXT_DARK,L("picker","deco_x0"),L("picker","deco_y0")-22)
        for sw in self.deco_swatches:
            idx=next(i for i,(n,*_) in enumerate(ALL_DECOS) if n==sw.name)
            sw.rect.x=L("picker","deco_x0")+idx%5*L("picker","deco_gap")
            sw.rect.y=L("picker","deco_y0")+idx//5*L("picker","deco_row_gap")
            sw.draw(surf,mouse)
            tc=ACCENT if sw.selected else TEXT_MID
            draw_text(surf,sw.name,f_s,tc,sw.rect.centerx,sw.rect.bottom+2,"midtop")
        self.btn_confirm.draw(surf,mouse); self.btn_back.draw(surf,mouse)

# ── 结果（订单） ─────────────────────────────────────────────────────

class ResultScene(Scene):
    scene_key = "result"
    def __init__(self,fonts,switch,data):
        self.fonts=fonts;self.switch=switch;self.data=data
        self.btn=Button((GW//2-80,GH-70,160,44),"返回主菜单",fonts[2],idle=ACCENT,hover=ACCENT2,text_color=(255,255,255))
    def handle(self,event,mouse):
        if self.btn.is_clicked(event,mouse): self.switch("menu")
    def draw(self,surf,mouse):
        surf.fill(BG); draw_hud(surf,self.fonts)
        f_s,f_m,f_n,f_l,_=self.fonts; d=self.data; o=d["order"]; r=d["result"]
        titles={"perfect":("完美！",GREEN_OK),"ok":("还行~",YELLOW_MID),"bad":("较差…",(200,120,50)),"fail":("失败！",RED_ERR)}
        title,tc=titles[r[0]]
        draw_text(surf,title,f_l,tc,GW//2,L("result","title_y"),"center")
        moods={"perfect":f"{o['name']}：「太漂亮了！谢谢你！」","ok":f"{o['name']}：「嗯…将就吧。」",
               "bad":f"{o['name']}：「这…不太对…」","fail":f"{o['name']}：「这根本不是我要的！」"}
        draw_text(surf,moods[r[0]],f_m,LC("result","mood_color"),GW//2,L("result","mood_y"),"center")
        draw_text(surf,"顾客要求",f_m,LC("result","label_color"),L("result","nail_l_x"),L("result","label_y"),"center")
        draw_text(surf,"你做的",f_m,LC("result","label_color"),L("result","nail_r_x"),L("result","label_y"),"center")
        oc_rgb=next((rgb for n,_,rgb in ALL_COLORS if n==o["color"]),(200,200,200))
        od_col=next((dc for n,_,dc,__ in ALL_DECOS if n==o["deco"]),None)
        nw,nh=L("result","nail_w"),L("result","nail_h")
        draw_nail_graphic(surf,o["shape"],oc_rgb,o["deco"],od_col,L("result","nail_l_x"),L("result","nail_y"),nw,nh)
        draw_nail_graphic(surf,d["shape"],d["color_rgb"],d["deco"],d["deco_color"],L("result","nail_r_x"),L("result","nail_y"),nw,nh)
        for i,(lbl,vo,vp,ok) in enumerate(zip(["甲型","底色","装饰"],[o["shape"],o["color"],o["deco"]],[d["shape"],d["cname"],d["deco"]],[d["correct_shape"],d["correct_color"],d["correct_deco"]])):
            draw_text(surf,f"{lbl}：{vo}  /  {vp}",f_m,GREEN_OK if ok else RED_ERR,GW//2,L("result","compare_y0")+i*L("result","compare_gap"),"center")
        if r[0] in ("perfect","ok"):
            draw_text(surf,f"+{r[1]} 金币   现有：{state['coins']}",f_n,GOLD,GW//2,L("result","coin_y"),"center")
        else:
            draw_text(surf,f"扣分   积分：{state['score']}",f_n,RED_ERR,GW//2,L("result","coin_y"),"center")
        self.btn.draw(surf,mouse)

# ── 结果（自由创作） ─────────────────────────────────────────────────

class ResultFreeScene(Scene):
    scene_key = "result_free"
    def __init__(self,fonts,switch,data):
        self.fonts=fonts;self.switch=switch;self.data=data
        self.btn=Button((GW//2-80,GH-70,160,44),"返回主菜单",fonts[2],idle=ACCENT,hover=ACCENT2,text_color=(255,255,255))
    def handle(self,event,mouse):
        if self.btn.is_clicked(event,mouse): self.switch("menu")
    def draw(self,surf,mouse):
        surf.fill(BG); draw_hud(surf,self.fonts); d=self.data
        f_s,f_m,f_n,f_l,_=self.fonts
        draw_text(surf,"美甲完成！已保存到作品集",f_l,LC("result_free","title_color"),GW//2,L("result_free","title_y"),"center")
        draw_nail_graphic(surf,d["shape"],d["color_rgb"],d["deco"],d["deco_color"],L("result_free","nail_x"),L("result_free","nail_y"),L("result_free","nail_w"),L("result_free","nail_h"))
        draw_text(surf,f"{d['shape']}  {d['cname']}  {d['deco']}",f_n,LC("result_free","info_color"),GW//2,L("result_free","info_y"),"center")
        draw_text(surf,f"共 {len(state['my_works'])} 件作品",f_m,LC("result_free","count_color"),GW//2,L("result_free","count_y"),"center")
        self.btn.draw(surf,mouse)

# ── 图片墙 ───────────────────────────────────────────────────────────

class GalleryScene(Scene):
    scene_key = "gallery"
    def __init__(self,fonts,switch):
        self.fonts=fonts;self.switch=switch;self.scroll=0
        self.btn_back=Button((20,GH-58,100,40),"返回",fonts[2],idle=(230,210,220),hover=(210,180,200))
    def handle(self,event,mouse):
        if self.btn_back.is_clicked(event,mouse): self.switch("menu")
        if event.type==pygame.MOUSEWHEEL: self.scroll=max(0,self.scroll-event.y*30)
    def draw(self,surf,mouse):
        surf.fill(BG); draw_hud(surf,self.fonts)
        f_s,f_m,*_=self.fonts; works=state["my_works"]
        draw_text(surf,f"我的作品集  共 {len(works)} 件",self.fonts[2],LC("gallery","title_color"),GW//2,L("gallery","title_y"),"center")
        if not works:
            draw_text(surf,"还没有作品，快去做第一套美甲吧！",f_m,TEXT_MID,GW//2,GH//2,"center")
        else:
            cols=L("gallery","cols"); tw=L("gallery","thumb_w"); th=L("gallery","thumb_h"); pad=L("gallery","thumb_pad")
            start_y=L("gallery","start_y")-self.scroll; x0=L("gallery","card_x0")
            for idx,w in enumerate(works):
                col=idx%cols; row=idx//cols
                tx=x0+col*(tw+pad); ty=start_y+row*(th+pad+30)
                if ty+th<50 or ty>GH: continue
                card=pygame.Rect(tx-6,ty-6,tw+12,th+34)
                draw_rrect(surf,PANEL,card,r=8,bw=2 if w.get("perfect") else 1,bc=GOLD if w.get("perfect") else (210,190,210))
                crgb=w.get("color_rgb",(200,200,200)); dcol=w.get("deco_color")
                draw_nail_graphic(surf,w["shape"],crgb,w["deco"],dcol,tx+tw//2,ty+th//2,tw-10,th-10)
                if w.get("perfect"): draw_text(surf,"完美",f_s,GOLD,tx+tw//2,ty+th+2,"midtop")
                draw_text(surf,w["shape"],f_s,TEXT_MID,tx+tw//2,ty+th+(14 if not w.get("perfect") else 16),"midtop")
        self.btn_back.draw(surf,mouse)

# ── 商店 ─────────────────────────────────────────────────────────────

class ShopScene(Scene):
    scene_key = "shop"
    def __init__(self,fonts,switch):
        self.fonts=fonts;self.switch=switch;self.msg="";self.msg_ok=True;self._build()
    def _build(self):
        f_s,f_m,*_=self.fonts; self.items=[]
        y=L("shop","item_y0"); gap=L("shop","item_gap")
        bx=L("shop","btn_x"); bw=L("shop","btn_w")
        for name,cost,rgb in ALL_COLORS:
            if name not in state["unlocked_colors"]:
                can=state["coins"]>=cost
                btn=Button((bx,y,bw,34),f"解锁 {cost}G",f_m,idle=BTN_IDLE if can else BTN_LOCK,hover=BTN_HOV if can else BTN_LOCK,tag=("color",name,cost))
                self.items.append(("颜色",name,cost,rgb,pygame.Rect(L("shop","preview_x"),y,60,34),btn)); y+=gap
        for name,cost,dc,_ in ALL_DECOS:
            if name not in state["unlocked_decos"]:
                can=state["coins"]>=cost
                btn=Button((bx,y,bw,34),f"解锁 {cost}G",f_m,idle=BTN_IDLE if can else BTN_LOCK,hover=BTN_HOV if can else BTN_LOCK,tag=("deco",name,cost))
                self.items.append(("装饰",name,cost,dc,pygame.Rect(L("shop","preview_x"),y,60,34),btn)); y+=gap
        self.btn_back=Button((20,GH-58,100,40),"返回",self.fonts[2],idle=(230,210,220),hover=(210,180,200))
        self.scroll_max=max(0,y-(GH-100)); self.scroll=0
    def handle(self,event,mouse):
        if self.btn_back.is_clicked(event,mouse): self.switch("menu"); return
        if event.type==pygame.MOUSEWHEEL: self.scroll=max(0,min(self.scroll_max,self.scroll-event.y*30))
        for ks,name,cost,color,srect,btn in self.items:
            adj=btn.rect.move(0,-self.scroll)
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1 and adj.collidepoint(mouse):
                k,n,c=btn.tag
                if state["coins"]<c: self.msg=f"金币不足！还差 {c-state['coins']} 金币"; self.msg_ok=False
                else:
                    state["coins"]-=c
                    if k=="color": state["unlocked_colors"].add(n)
                    else:          state["unlocked_decos"].add(n)
                    save_game()
                    self.msg=f"已解锁 {n}！剩余金币：{state['coins']}"; self.msg_ok=True; self._build()
                return
    def draw(self,surf,mouse):
        surf.fill(BG); draw_hud(surf,self.fonts)
        f_s,f_m,f_n,*_=self.fonts
        draw_text(surf,"解锁商店",self.fonts[3],LC("shop","title_color"),GW//2,L("shop","title_y"),"center")
        if not self.items:
            draw_text(surf,"所有内容已解锁！",f_n,GREEN_OK,GW//2,200,"center")
        else:
            clip=surf.get_clip(); surf.set_clip(pygame.Rect(0,90,GW,GH-140))
            for ks,name,cost,color,srect,btn in self.items:
                sy=srect.y-self.scroll
                if sy+60<90 or sy>GH-90: continue
                pr=pygame.Rect(L("shop","preview_x"),sy,60,36)
                if ks=="颜色": draw_rrect(surf,color,pr,r=6,bw=1,bc=(200,180,200))
                else:
                    draw_rrect(surf,(245,245,245),pr,r=6,bw=1,bc=(200,180,200))
                    if name!="无": draw_deco(surf,name,pr.centerx,pr.centery,10,color)
                draw_text(surf,f"{ks}  {name}",f_m,LC("shop","item_color"),L("shop","name_x"),sy+8)
                can=state["coins"]>=cost; bc=GREEN_OK if can else (180,180,180)
                adj=btn.rect.move(0,-self.scroll)
                draw_rrect(surf,BTN_IDLE if can else BTN_LOCK,adj,r=8,bw=1,bc=bc)
                draw_text(surf,f"解锁 {cost}G",f_m,TEXT_DARK if can else TEXT_LITE,adj.centerx,adj.centery,"center")
            surf.set_clip(clip)
        if self.msg:
            draw_text(surf,self.msg,f_m,GREEN_OK if self.msg_ok else RED_ERR,GW//2,GH-100,"center")
        self.btn_back.draw(surf,mouse)

# ══════════════════════════════════════════════════════════════════════
# 调试面板
# ══════════════════════════════════════════════════════════════════════

class DebugPanel:
    """
    右侧 340px 调试面板。
    - 上方：场景选择 tab
    - 中部：当前场景的参数列表（滑块 + 数字输入框）
    - 下方：导出按钮 + 状态消息
    """
    ITEM_H   = 46    # 数值型参数行高
    COLOR_ITEM_H = 46  # 颜色型参数行高（与数值型一致，色盘浮层覆盖显示）
    TAB_H    = 30
    PAD      = 8

    # 色盘尺寸（内嵌浮层，覆盖在面板上）
    CP_PAD     = 10
    SV_W       = DBG_W - CP_PAD * 2   # SV 矩形占满面板宽
    SV_H       = 160
    HUE_H      = 16
    CP_W       = DBG_W
    # 布局从上到下：标题(18) + SV(160) + 间距(6) + 色相条(16) + 间距(6) + 预览+RGB(36) + 确定按钮(28) + 下边距(8)
    CP_H       = 18 + SV_H + 6 + HUE_H + 6 + 36 + 28 + 8

    def __init__(self, fonts, offset_x):
        self.fonts      = fonts
        self.ox         = offset_x
        self.scene_tabs = list(LAYOUT.keys())
        self.cur_tab    = "hud"
        self.scroll     = 0
        self.drag_key   = None
        self.input_key  = None
        self.input_buf  = ""
        self.msg        = ""
        self.msg_timer  = 0
        self._fsmall    = fonts[0]
        self._fmid      = fonts[1]
        self._fbig      = fonts[2]

        # 色盘状态
        self._cp_open   = False   # 色盘是否打开
        self._cp_info   = None    # 当前编辑的 info dict
        self._cp_key    = None    # 当前编辑的 key（用于标题显示）
        self._cp_h      = 0.0    # 色相 0-1
        self._cp_s      = 1.0    # 饱和度 0-1
        self._cp_v      = 1.0    # 明度 0-1
        self._cp_drag   = None   # "sv" | "hue"
        self._sv_surf   = None   # 缓存 SV 矩形 surface
        self._sv_dirty  = True   # 色相变化时重新生成

    # ── HSV ↔ RGB ──────────────────────────────────────────────────────
    @staticmethod
    def _hsv2rgb(h, s, v):
        if s == 0:
            c = int(v*255)
            return [c, c, c]
        i = int(h*6)
        f = h*6 - i
        p, q, t = v*(1-s), v*(1-f*s), v*(1-(1-f)*s)
        r,g,b = [
            (v,t,p),(q,v,p),(p,v,t),(p,q,v),(t,p,v),(v,p,q)
        ][i%6]
        return [int(r*255), int(g*255), int(b*255)]

    @staticmethod
    def _rgb2hsv(r, g, b):
        r,g,b = r/255, g/255, b/255
        mx,mn = max(r,g,b), min(r,g,b)
        v = mx; s = (mx-mn)/mx if mx else 0
        if s == 0: return 0.0, s, v
        d = mx-mn
        if mx==r:   h = (g-b)/d % 6
        elif mx==g: h = (b-r)/d + 2
        else:       h = (r-g)/d + 4
        return h/6, s, v

    # ── 色盘浮层矩形 ──────────────────────────────────────────────────
    def _cp_rect(self):
        return pygame.Rect(self.ox, self.TAB_H, self.CP_W, self.CP_H)

    def _sv_rect(self):
        r = self._cp_rect()
        return pygame.Rect(r.x + self.CP_PAD, r.y + 22, self.SV_W, self.SV_H)

    def _hue_rect(self):
        sv = self._sv_rect()
        return pygame.Rect(sv.x, sv.bottom + 6, self.SV_W, self.HUE_H)

    def _preview_rect(self):
        hur = self._hue_rect()
        return pygame.Rect(hur.x, hur.bottom + 6, 32, 32)

    def _confirm_rect(self):
        r = self._cp_rect()
        return pygame.Rect(r.x + self.CP_PAD, r.bottom - 32,
                           self.CP_W - self.CP_PAD*2, 24)

    # ── 生成 SV 矩形 surface ──────────────────────────────────────────
    def _build_sv_surf(self):
        w, h = self.SV_W, self.SV_H
        surf = pygame.Surface((w, h))
        for px in range(w):
            s = px / (w-1)
            for py in range(h):
                v = 1 - py / (h-1)
                rgb = self._hsv2rgb(self._cp_h, s, v)
                surf.set_at((px, py), rgb)
        self._sv_surf  = surf
        self._sv_dirty = False

    # ── 生成色相条 surface（静态，只生成一次） ────────────────────────
    @staticmethod
    def _build_hue_surf(w, h):
        surf = pygame.Surface((w, h))
        for px in range(w):
            rgb = DebugPanel._hsv2rgb(px/(w-1), 1.0, 1.0)
            for py in range(h):
                surf.set_at((px, py), rgb)
        return surf

    # ── 打开色盘 ─────────────────────────────────────────────────────
    def _open_cp(self, key, info):
        r, g, b = info["color"]
        self._cp_h, self._cp_s, self._cp_v = self._rgb2hsv(r, g, b)
        self._cp_info  = info
        self._cp_key   = key
        self._cp_open  = True
        self._sv_dirty = True
        if not hasattr(self, "_hue_surf"):
            self._hue_surf = self._build_hue_surf(self.SV_W, self.HUE_H)

    def _close_cp(self):
        self._cp_open = False
        self._cp_info = None
        self._cp_drag = None

    def _cp_apply(self):
        if self._cp_info is None: return
        self._cp_info["color"] = self._hsv2rgb(self._cp_h, self._cp_s, self._cp_v)

    # ── 色盘事件处理 ─────────────────────────────────────────────────
    def _handle_cp(self, event, mx, my):
        sv  = self._sv_rect()
        hur = self._hue_rect()
        cfm = self._confirm_rect()
        cpr = self._cp_rect()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # 确认按钮
            if cfm.collidepoint(mx, my):
                self._close_cp(); return True
            # 点击 SV 区
            if sv.collidepoint(mx, my):
                self._cp_drag = "sv"
                self._cp_s = (mx - sv.x) / sv.width
                self._cp_v = 1 - (my - sv.y) / sv.height
                self._cp_s = max(0, min(1, self._cp_s))
                self._cp_v = max(0, min(1, self._cp_v))
                self._cp_apply(); return True
            # 点击色相条
            if hur.collidepoint(mx, my):
                self._cp_drag = "hue"
                self._cp_h = (mx - hur.x) / hur.width
                self._cp_h = max(0, min(1, self._cp_h))
                self._sv_dirty = True
                self._cp_apply(); return True
            # 点击色盘外部关闭
            if not cpr.collidepoint(mx, my):
                self._close_cp(); return True
            return True

        if event.type == pygame.MOUSEMOTION and self._cp_drag:
            if self._cp_drag == "sv":
                self._cp_s = max(0, min(1, (mx - sv.x) / sv.width))
                self._cp_v = max(0, min(1, 1 - (my - sv.y) / sv.height))
                self._cp_apply()
            elif self._cp_drag == "hue":
                self._cp_h = max(0, min(1, (mx - hur.x) / hur.width))
                self._sv_dirty = True
                self._cp_apply()
            return True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._cp_drag = None
            return True

        return False

    # ── 绘制色盘浮层 ─────────────────────────────────────────────────
    def _draw_cp(self, surf):
        cpr = self._cp_rect()
        sv  = self._sv_rect()
        hur = self._hue_rect()
        pvr = self._preview_rect()
        cfm = self._confirm_rect()

        # 浮层背景
        pygame.draw.rect(surf, (28, 28, 38), cpr)
        pygame.draw.rect(surf, DBG_ACC, cpr, 2)

        # 标题
        draw_text(surf, f"颜色: {self._cp_key}", self._fsmall, DBG_TEXT,
                  cpr.x + self.CP_PAD, cpr.y + 4)

        # SV 矩形
        if self._sv_dirty:
            self._build_sv_surf()
        surf.blit(self._sv_surf, sv.topleft)
        pygame.draw.rect(surf, (160, 160, 160), sv, 1)

        # SV 十字准线
        cx = sv.x + int(self._cp_s * sv.width)
        cy = sv.y + int((1 - self._cp_v) * sv.height)
        pygame.draw.circle(surf, (0, 0, 0),     (cx, cy), 7, 2)
        pygame.draw.circle(surf, (255,255,255),  (cx, cy), 6, 2)

        # 色相条
        surf.blit(self._hue_surf, hur.topleft)
        pygame.draw.rect(surf, (160, 160, 160), hur, 1)
        hx = hur.x + int(self._cp_h * hur.width)
        pygame.draw.rect(surf, (255,255,255), (hx-3, hur.y-3, 6, hur.height+6), 2)

        # 色块预览 + RGB 数值（横排，在色相条下方）
        preview_rgb = self._hsv2rgb(self._cp_h, self._cp_s, self._cp_v)
        pygame.draw.rect(surf, tuple(preview_rgb), pvr, border_radius=4)
        pygame.draw.rect(surf, DBG_DIM, pvr, 1, border_radius=4)
        rx = pvr.right + 10
        ry = pvr.y + 2
        draw_text(surf, f"R  {preview_rgb[0]:3d}", self._fsmall, (220, 80, 80),  rx, ry)
        draw_text(surf, f"G  {preview_rgb[1]:3d}", self._fsmall, (80, 200, 80),  rx + 76, ry)
        draw_text(surf, f"B  {preview_rgb[2]:3d}", self._fsmall, (80,140,255),   rx + 152, ry)
        hex_str = "#{:02X}{:02X}{:02X}".format(*preview_rgb)
        draw_text(surf, hex_str, self._fsmall, DBG_DIM, rx, ry + 16)

        # 确认按钮
        pygame.draw.rect(surf, (50,130,80), cfm, border_radius=5)
        draw_text(surf, "确定  关闭色盘", self._fsmall, (200,255,200),
                  cfm.centerx, cfm.centery, "center")

    # ── 通用辅助 ──────────────────────────────────────────────────────
    def _tab_rect(self, i):
        tw = DBG_W // len(self.scene_tabs)
        return pygame.Rect(self.ox + i*tw, 0, tw, self.TAB_H)

    def _items(self):
        return list(LAYOUT[self.cur_tab].items())

    def _item_h(self, info):
        return self.ITEM_H   # 颜色型和数值型行高相同，色盘用浮层

    def _item_y(self, idx):
        items = self._items()
        y = self.TAB_H + self.PAD - self.scroll
        for i, (_, info) in enumerate(items):
            if i == idx: break
            y += self._item_h(info) + 4
        return y

    def _reset_btn_rect(self, i):
        y = self._item_y(i)
        return pygame.Rect(self.ox + DBG_W - self.PAD - 16, y+2, 16, 16)

    def _slider_rect(self, i, info):
        y = self._item_y(i)
        # 右侧给重置按钮留 20px
        return pygame.Rect(self.ox + self.PAD, y+28, DBG_W-self.PAD*2-74, 10)

    def _input_rect(self, i):
        y = self._item_y(i)
        return pygame.Rect(self.ox + DBG_W-72, y+22, 46, 18)

    def _color_swatch_rect(self, i):
        y = self._item_y(i)
        # 色块在重置按钮左侧
        return pygame.Rect(self.ox + DBG_W - self.PAD - 40, y+12, 20, 20)

    def _export_btn_rect(self):
        return pygame.Rect(self.ox+self.PAD, GH-62, DBG_W-self.PAD*2, 30)

    # ── 主事件处理 ────────────────────────────────────────────────────
    def handle(self, event, abs_mouse):
        mx, my = abs_mouse

        # 色盘打开时优先处理色盘事件
        if self._cp_open:
            consumed = self._handle_cp(event, mx, my)
            if consumed: return True

        # Tab 切换
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, tab in enumerate(self.scene_tabs):
                if self._tab_rect(i).collidepoint(mx, my):
                    self.cur_tab = tab; self.scroll = 0
                    self.drag_key = None; self.input_key = None
                    self._close_cp()
                    return True

        items = self._items()

        # 导出按钮
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._export_btn_rect().collidepoint(mx, my):
                export_layout()
                self._show_msg("已导出 layout_export.json !")
                return True

        # 滚轮
        if event.type == pygame.MOUSEWHEEL and mx >= self.ox:
            total_h = sum(self._item_h(info)+4 for _,info in items)
            max_scroll = max(0, total_h - (GH - self.TAB_H - 75))
            self.scroll = max(0, min(max_scroll, self.scroll - event.y*20))
            return True

        # 点击重置按钮
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, (key, info) in enumerate(items):
                if self._reset_btn_rect(i).collidepoint(mx, my):
                    reset_item(self.cur_tab, key)
                    # 若色盘正在编辑此条目，同步更新色盘状态
                    if self._cp_open and self._cp_key == key and _is_color(info):
                        r, g, b = info["color"]
                        self._cp_h, self._cp_s, self._cp_v = self._rgb2hsv(r, g, b)
                        self._sv_dirty = True
                    self._show_msg(f"已重置: {info['label']}")
                    return True

        # 点击色块 → 打开/关闭色盘
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, (key, info) in enumerate(items):
                if _is_color(info):
                    sr = self._color_swatch_rect(i)
                    if sr.collidepoint(mx, my):
                        if self._cp_open and self._cp_key == key:
                            self._close_cp()
                        else:
                            self._open_cp(key, info)
                        return True

        # 点击输入框（数值型）
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            clicked_input = False
            for i, (key, info) in enumerate(items):
                if not _is_color(info):
                    ir = self._input_rect(i)
                    if ir.collidepoint(mx, my):
                        self.input_key = key; self.input_buf = str(info["v"])
                        clicked_input = True; break
            if not clicked_input and self.input_key:
                self._commit_input(); self.input_key = None

        # 键盘输入
        if event.type == pygame.KEYDOWN and self.input_key:
            if event.key == pygame.K_RETURN:
                self._commit_input(); self.input_key = None
            elif event.key == pygame.K_ESCAPE:
                self.input_key = None
            elif event.key == pygame.K_BACKSPACE:
                self.input_buf = self.input_buf[:-1]
            else:
                if event.unicode in "0123456789.-":
                    self.input_buf += event.unicode
            return True

        # 数值滑块拖拽开始
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, (key, info) in enumerate(items):
                if not _is_color(info):
                    sr = self._slider_rect(i, info)
                    if sr.collidepoint(mx, my):
                        self.drag_key = key; self._drag_slide(mx, sr, info); return True

        # 数值滑块拖拽中
        if event.type == pygame.MOUSEMOTION and self.drag_key:
            for i, (key, info) in enumerate(items):
                if not _is_color(info) and self.drag_key == key:
                    sr = self._slider_rect(i, info)
                    self._drag_slide(mx, sr, info); return True

        # 拖拽结束
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.drag_key = None

        return mx >= self.ox

    def _drag_slide(self, mx, sr, info):
        ratio = max(0.0, min(1.0, (mx - sr.x) / sr.width))
        info["v"] = int(round(info["min"] + ratio * (info["max"] - info["min"])))

    def _commit_input(self):
        try:
            v = float(self.input_buf)
            info = LAYOUT[self.cur_tab][self.input_key]
            info["v"] = int(max(info["min"], min(info["max"], v)))
        except ValueError:
            pass

    def _show_msg(self, text):
        self.msg = text; self.msg_timer = 120

    # ── 绘制 ──────────────────────────────────────────────────────────
    def draw(self, surf, abs_mouse):
        mx, my = abs_mouse

        # 背景
        pygame.draw.rect(surf, DBG_BG, (self.ox, 0, DBG_W, GH))
        pygame.draw.line(surf, DBG_ACC, (self.ox, 0), (self.ox, GH), 2)

        # Tabs
        for i, tab in enumerate(self.scene_tabs):
            tr = self._tab_rect(i)
            sel = (tab == self.cur_tab)
            pygame.draw.rect(surf, DBG_SEL if sel else DBG_PANEL, tr)
            pygame.draw.rect(surf, DBG_ACC if sel else DBG_DIM, tr, 1)
            draw_text(surf, tab[:5], self._fsmall, DBG_ACC if sel else DBG_DIM,
                      tr.centerx, tr.centery, "center")

        # 参数列表
        items    = self._items()
        clip_r   = pygame.Rect(self.ox, self.TAB_H, DBG_W, GH - self.TAB_H - 75)
        old_clip = surf.get_clip()
        surf.set_clip(clip_r)

        for i, (key, info) in enumerate(items):
            y  = self._item_y(i)
            ih = self._item_h(info)
            if y + ih < self.TAB_H or y > GH - 50:
                continue

            row_r = pygame.Rect(self.ox+2, y, DBG_W-4, ih)
            hov   = row_r.collidepoint(mx, my)
            pygame.draw.rect(surf, DBG_SEL if hov else DBG_PANEL, row_r, border_radius=4)

            if _is_color(info):
                # 标签
                draw_text(surf, info["label"], self._fsmall, DBG_TEXT, self.ox+self.PAD, y+2)
                # RGB 数值文字
                rgb = info["color"]
                active = self._cp_open and self._cp_key == key
                draw_text(surf, f"({rgb[0]},{rgb[1]},{rgb[2]})",
                          self._fsmall, DBG_ACC if active else DBG_DIM,
                          self.ox+DBG_W-self.PAD-46, y+16, "midright")
                # 色块（可点击）
                sr = self._color_swatch_rect(i)
                safe = tuple(max(0,min(255,v)) for v in rgb)
                pygame.draw.rect(surf, safe, sr, border_radius=4)
                border_c = DBG_ACC if active else ((255,255,255) if sr.collidepoint(mx,my) else DBG_DIM)
                pygame.draw.rect(surf, border_c, sr, 2, border_radius=4)
            else:
                # 数值型：标签 + 滑块 + 输入框
                draw_text(surf, info["label"], self._fsmall, DBG_TEXT, self.ox+self.PAD, y+2)
                draw_text(surf, str(info["v"]), self._fsmall, DBG_ACC,
                          self.ox+DBG_W-self.PAD-20, y+2, "topright")
                sr = self._slider_rect(i, info)
                pygame.draw.rect(surf, (60,60,80), sr, border_radius=4)
                ratio  = (info["v"]-info["min"]) / max(1, info["max"]-info["min"])
                fill_w = int(sr.width * ratio)
                if fill_w > 0:
                    pygame.draw.rect(surf, DBG_ACC, (sr.x,sr.y,fill_w,sr.height), border_radius=4)
                pygame.draw.circle(surf, (255,255,255), (sr.x+fill_w, sr.centery), 6)
                ir = self._input_rect(i)
                editing = (self.input_key == key)
                pygame.draw.rect(surf, (80,80,100) if editing else (50,50,65), ir, border_radius=3)
                pygame.draw.rect(surf, DBG_ACC if editing else DBG_DIM, ir, 1, border_radius=3)
                draw_text(surf, self.input_buf if editing else str(info["v"]),
                          self._fsmall, DBG_ACC if editing else DBG_TEXT,
                          ir.centerx, ir.centery, "center")

            # 每行右上角重置按钮（↺）
            rb = self._reset_btn_rect(i)
            snap_val = _LAYOUT_SNAPSHOT.get(self.cur_tab, {}).get(key)
            cur_val  = info["color"] if _is_color(info) else info["v"]
            changed  = (snap_val is not None) and (list(cur_val) if isinstance(cur_val, list) else cur_val) != snap_val
            hov_rb   = rb.collidepoint(mx, my)
            rb_bg    = (180, 80, 60) if changed else (55, 55, 70)
            rb_bg    = (220, 100, 80) if (changed and hov_rb) else rb_bg
            pygame.draw.rect(surf, rb_bg, rb, border_radius=3)
            draw_text(surf, "R", self._fsmall, (255,200,180) if changed else DBG_DIM,
                      rb.centerx, rb.centery, "center")

        surf.set_clip(old_clip)

        # 色盘浮层（在参数列表之上）
        if self._cp_open:
            self._draw_cp(surf)

        # 导出按钮
        eb = self._export_btn_rect()
        pygame.draw.rect(surf, (60,120,80) if eb.collidepoint(mx,my) else (40,90,60), eb, border_radius=6)
        draw_text(surf, "F2 导出布局 (layout_export.json)", self._fsmall, (200,255,200),
                  eb.centerx, eb.centery, "center")

        # 消息
        if self.msg_timer > 0:
            self.msg_timer -= 1
            draw_text(surf, self.msg, self._fsmall, DBG_GREEN, self.ox+DBG_W//2, GH-68, "center")

        # 快捷键提示
        draw_text(surf, "F1隐藏  F2导出  |  拖滑块/点数值框输入",
                  self._fsmall, DBG_DIM, self.ox+DBG_W//2, GH-4, "midbottom")

# ══════════════════════════════════════════════════════════════════════
# 主控制器
# ══════════════════════════════════════════════════════════════════════

class Game:
    def __init__(self):
        pygame.init()
        load_layout()          # 先载入上次保存的布局（内部已拍快照）
        if not _LAYOUT_SNAPSHOT:   # 若文件不存在则手动拍初始快照
            _snapshot_layout()
        self.debug_on  = False
        self.total_w   = GW    # 初始不含调试面板
        self.screen    = pygame.display.set_mode((self.total_w, GH))
        pygame.display.set_caption("美甲工作室  [F1=调试面板]")
        self.clock     = pygame.time.Clock()
        self.fonts     = load_fonts()
        init_unlocks()
        self.scene     = MenuScene(self.fonts, self.switch)
        self.game_surf = pygame.Surface((GW, GH))
        self.dbg       = DebugPanel(self.fonts, GW)

    def _resize(self):
        w = GW + (DBG_W if self.debug_on else 0)
        if w != self.total_w:
            self.total_w = w
            self.screen  = pygame.display.set_mode((w, GH))

    def switch(self, name, data=None):
        scenes = {
            "menu":       lambda: MenuScene(self.fonts, self.switch),
            "order":      lambda: PickerScene(self.fonts, self.switch, mode="order"),
            "free":       lambda: PickerScene(self.fonts, self.switch, mode="free"),
            "result":     lambda: ResultScene(self.fonts, self.switch, data),
            "result_free":lambda: ResultFreeScene(self.fonts, self.switch, data),
            "gallery":    lambda: GalleryScene(self.fonts, self.switch),
            "shop":       lambda: ShopScene(self.fonts, self.switch),
        }
        if name in scenes:
            self.scene = scenes[name]()
            # 同步调试面板 tab 到当前场景
            sk = self.scene.scene_key
            if sk in self.dbg.scene_tabs:
                self.dbg.cur_tab = sk

    def run(self):
        while True:
            mouse_abs = pygame.mouse.get_pos()
            # 游戏区鼠标坐标（调试面板展开时右移不影响游戏）
            mouse_game = mouse_abs

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save_game(); pygame.quit(); sys.exit()

                # F1: 切换调试面板
                if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
                    self.debug_on = not self.debug_on
                    self._resize()
                    continue

                # F2: 快捷导出
                if event.type == pygame.KEYDOWN and event.key == pygame.K_F2:
                    export_layout()
                    self.dbg._show_msg("已导出 layout_export.json !")
                    continue

                # 调试面板消费事件（鼠标在面板区域内）
                if self.debug_on:
                    consumed = self.dbg.handle(event, mouse_abs)
                    if consumed:
                        continue

                # 游戏场景事件（菜单里按钮布局用 L() 实时读取，需要先重建）
                self.scene.handle(event, mouse_game)

            # 游戏每帧重建布局敏感组件（菜单按钮随 LAYOUT 移动）
            if isinstance(self.scene, MenuScene):
                self.scene._build()
            if isinstance(self.scene, ShopScene):
                pass  # 商店布局在 draw 里直接读 L()

            self.scene.update()

            # 绘制游戏到 game_surf
            self.game_surf.fill(BG)
            self.scene.draw(self.game_surf, mouse_game)

            # 合并到主屏
            self.screen.blit(self.game_surf, (0, 0))
            if self.debug_on:
                self.dbg.draw(self.screen, mouse_abs)

            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    Game().run()
