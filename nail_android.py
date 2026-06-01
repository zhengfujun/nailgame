"""
美甲工作室 - Android 平板版
分辨率: 1280x800 横屏（主流 10 寸平板）
触控: 单指点击等同鼠标左键，无需额外处理
字体: 内置 font/NotoSansCJK.ttf，不依赖系统字体
"""
import pygame
import sys, datetime, random, json, os, math

# ── Android / 桌面双模式路径 ─────────────────────────────────────────

def _base_dir():
    """资源和存档的根目录"""
    # Android (python-for-android) 环境
    if "ANDROID_ARGUMENT" in os.environ or "ANDROID_PRIVATE" in os.environ:
        try:
            from android.storage import app_storage_path
            return app_storage_path()
        except Exception:
            return "/sdcard/NailStudio"
    # 桌面
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR   = _base_dir()
SAVE_FILE  = os.path.join(BASE_DIR, "savegame.json")
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
FONT_PATH  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "font", "NotoSansCJK.ttf")

# ── 屏幕尺寸（1280×800 横屏，常见平板分辨率） ────────────────────────
W, H = 1280, 800
FPS  = 60

# ── 调色板 ───────────────────────────────────────────────────────────
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

# ── 字体缓存 ─────────────────────────────────────────────────────────
_font_cache = {}

def get_font(size):
    if size not in _font_cache:
        if os.path.exists(FONT_PATH):
            _font_cache[size] = pygame.font.Font(FONT_PATH, size)
        else:
            # 回退：尝试系统字体
            for name in ["microsoftyahei", "simhei", "simsun"]:
                path = pygame.font.match_font(name)
                if path:
                    _font_cache[size] = pygame.font.Font(path, size)
                    break
            else:
                _font_cache[size] = pygame.font.SysFont(None, size)
    return _font_cache[size]

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

def save_game():
    os.makedirs(os.path.dirname(SAVE_FILE), exist_ok=True)
    data = {
        "coins": state["coins"], "score": state["score"],
        "orders_done": state["orders_done"], "orders_correct": state["orders_correct"],
        "unlocked_colors": list(state["unlocked_colors"]),
        "unlocked_decos":  list(state["unlocked_decos"]),
        "my_works": [{k: (list(v) if isinstance(v, tuple) else v)
                      for k, v in w.items()} for w in state["my_works"]],
    }
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_game():
    if not os.path.exists(SAVE_FILE): return
    try:
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
    except Exception:
        pass

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
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            if size: img = pygame.transform.smoothscale(img, size)
            _img_cache[key] = img
        else:
            _img_cache[key] = None
    return _img_cache[key]

def get_shape_img(name, size):
    fn = SHAPE_FILE.get(name)
    return load_img(os.path.join(ASSETS_DIR,"shapes",fn+".png"), size) if fn else None

def get_deco_img(name, size):
    fn = DECO_FILE.get(name)
    return load_img(os.path.join(ASSETS_DIR,"decos",fn+".png"), size) if fn else None

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

def draw_deco(surf, name, cx, cy, r, color):
    if name == "无" or color is None: return
    c = color[:3]
    if name == "小钻":
        pts=[(cx,cy-r),(cx+r,cy),(cx,cy+r),(cx-r,cy)]
        pygame.draw.polygon(surf,c,pts); pygame.draw.polygon(surf,(255,255,255),pts,1)
    elif name == "珍珠":
        pygame.draw.circle(surf,c,(cx,cy),r)
        pygame.draw.circle(surf,(255,255,255),(cx-r//3,cy-r//3),r//3)
    elif name == "亮片":
        for a in range(0,360,45):
            rad=math.radians(a)
            pygame.draw.circle(surf,c,(cx+int(math.cos(rad)*r),cy+int(math.sin(rad)*r)),max(2,r//4))
    elif name == "蝴蝶结":
        pygame.draw.ellipse(surf,c,(cx-r,cy-r//2,r,r))
        pygame.draw.ellipse(surf,c,(cx,cy-r//2,r,r))
        pygame.draw.circle(surf,(255,255,255),(cx,cy),r//3)
    elif name == "花朵":
        for i in range(6):
            rad=math.radians(i*60)
            pygame.draw.circle(surf,c,(cx+int(math.cos(rad)*r*0.7),cy+int(math.sin(rad)*r*0.7)),r//3)
        pygame.draw.circle(surf,(255,230,100),(cx,cy),r//4)
    elif name == "爱心":
        pts=[]
        for t_deg in range(0,361,6):
            t=math.radians(t_deg)
            pts.append((cx+int(r*(16*math.sin(t)**3)/16),cy+int(-r*(13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t))/16)))
        if len(pts)>2: pygame.draw.polygon(surf,c,pts)
    elif name == "月亮星星":
        pygame.draw.circle(surf,c,(cx-r//4,cy),r*2//3)
        pygame.draw.circle(surf,(255,255,255),(cx+r//6,cy-r//4),r//2)
        for i in range(5):
            rad=math.radians(i*72-90)
            pygame.draw.circle(surf,(255,230,100),(cx+r+int(math.cos(rad)*r//3),cy-r//2+int(math.sin(rad)*r//3)),max(2,r//5))
    elif name == "渐变贴纸":
        for i in range(r,0,-2):
            ratio=i/r
            pygame.draw.circle(surf,(int(c[0]*ratio+255*(1-ratio)),int(c[1]*ratio+200*(1-ratio)),int(c[2]*ratio+220*(1-ratio))),(cx,cy),i)

def draw_nail(surf, shape, color_rgb, deco_name, deco_color, cx, cy, w=100, h=160):
    img = get_shape_img(shape, (w, h))
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
            gl=tuple(min(255,v+60) for v in color_rgb)
            gloss=pygame.Surface((w,h),pygame.SRCALPHA)
            pygame.draw.polygon(gloss,(*gl,80),scale_poly(poly,w//2-4,h//2-6,w*.4,h*.35))
            surf.blit(gloss,(cx-w//2,cy-h//2))
        except: pass
        pygame.draw.polygon(surf,(180,140,160),pts,2)
    if deco_name and deco_name != "无":
        di = get_deco_img(deco_name,(w//2,w//2))
        if di: surf.blit(di,(cx-w//4,cy+4))
        elif deco_color: draw_deco(surf,deco_name,cx,cy+10,max(8,w//8),deco_color)

# ── UI 基础 ──────────────────────────────────────────────────────────

def draw_rrect(surf, color, rect, r=12, bw=0, bc=None):
    pygame.draw.rect(surf, color, rect, border_radius=r)
    if bw and bc: pygame.draw.rect(surf, bc, rect, bw, border_radius=r)

def draw_text(surf, text, size, color, x, y, anchor="topleft"):
    img = get_font(size).render(text, True, color)
    r   = img.get_rect(**{anchor:(x,y)})
    surf.blit(img, r)
    return r

# ── 触摸友好按钮（更大的点击区域） ──────────────────────────────────

class Button:
    def __init__(self, rect, label, size=22,
                 idle=BTN_IDLE, hover=BTN_HOV, sel=BTN_SEL,
                 text_color=TEXT_DARK, selected=False, locked=False, tag=None):
        self.rect=pygame.Rect(rect); self.label=label; self.size=size
        self.idle=idle; self.hover=hover; self.sel_color=sel
        self.text_color=text_color; self.selected=selected
        self.locked=locked; self.tag=tag

    def draw(self, surf, mouse):
        hov = self.rect.collidepoint(mouse)
        if self.locked: bg=BTN_LOCK
        elif self.selected: bg=self.sel_color
        elif hov: bg=self.hover
        else: bg=self.idle
        draw_rrect(surf,bg,self.rect,r=14,bw=3,
                   bc=ACCENT if self.selected else (200,180,190))
        tc = TEXT_LITE if self.locked else self.text_color
        draw_text(surf,self.label,self.size,tc,self.rect.centerx,self.rect.centery,"center")

    def is_clicked(self, event, mouse):
        return (not self.locked and event.type==pygame.MOUSEBUTTONDOWN
                and event.button==1 and self.rect.collidepoint(mouse))

class ColorSwatch:
    def __init__(self, rect, name, rgb, cost, unlocked=True, selected=False):
        self.rect=pygame.Rect(rect); self.name=name; self.rgb=rgb
        self.cost=cost; self.unlocked=unlocked; self.selected=selected
    def draw(self, surf, mouse):
        hov=self.rect.collidepoint(mouse)
        c=self.rgb if self.unlocked else (180,180,180)
        draw_rrect(surf,c,self.rect,r=10,bw=4,
                   bc=ACCENT if self.selected else ((255,255,255) if hov else (200,190,200)))
        if not self.unlocked:
            draw_text(surf,f"{self.cost}G",18,(100,100,100),self.rect.centerx,self.rect.centery,"center")
    def is_clicked(self,event,mouse):
        return self.unlocked and event.type==pygame.MOUSEBUTTONDOWN and event.button==1 and self.rect.collidepoint(mouse)

class DecoSwatch:
    def __init__(self, rect, name, deco_color, cost, unlocked=True, selected=False):
        self.rect=pygame.Rect(rect); self.name=name; self.deco_color=deco_color
        self.cost=cost; self.unlocked=unlocked; self.selected=selected
    def draw(self, surf, mouse):
        hov=self.rect.collidepoint(mouse)
        bg=(250,250,250) if self.unlocked else (200,200,200)
        draw_rrect(surf,bg,self.rect,r=10,bw=4,
                   bc=ACCENT if self.selected else ((255,255,255) if hov else (200,190,200)))
        if self.unlocked and self.name!="无":
            di=get_deco_img(self.name,(52,52))
            if di: surf.blit(di,di.get_rect(center=(self.rect.centerx,self.rect.centery-4)))
            else: draw_deco(surf,self.name,self.rect.centerx,self.rect.centery-6,12,self.deco_color)
        if not self.unlocked:
            draw_text(surf,f"{self.cost}G",18,(100,100,100),self.rect.centerx,self.rect.centery,"center")
    def is_clicked(self,event,mouse):
        return self.unlocked and event.type==pygame.MOUSEBUTTONDOWN and event.button==1 and self.rect.collidepoint(mouse)

# ── HUD ──────────────────────────────────────────────────────────────

def draw_hud(surf):
    pygame.draw.rect(surf, ACCENT, (0,0,W,56))
    draw_text(surf,"美甲工作室",30,(255,255,255),W//2,28,"center")
    draw_text(surf,f"金币 {state['coins']}",22,GOLD,20,17)
    draw_text(surf,f"积分 {state['score']}",22,(255,255,255),180,17)
    draw_text(surf,f"接单 {state['orders_done']}  完美 {state['orders_correct']}",
              18,(255,220,235),W-16,17,"topright")

# ── 场景基类 ─────────────────────────────────────────────────────────

class Scene:
    def handle(self,event,mouse): pass
    def draw(self,surf,mouse): pass

# ── 主菜单 ───────────────────────────────────────────────────────────

class MenuScene(Scene):
    def __init__(self, switch):
        self.switch = switch
        cx = W//2
        self.btns = [
            Button((cx-200,130,400,72),"接受顾客订单  赚金币",26,tag="order"),
            Button((cx-200,218,400,72),"自由创作",26,tag="free"),
            Button((cx-200,306,400,72),"查看我的作品",26,tag="gallery"),
            Button((cx-200,394,400,72),"解锁商店",26,tag="shop"),
            Button((cx-200,500,400,66),"退出",24,idle=(255,200,200),hover=(255,160,160),tag="quit"),
        ]

    def handle(self,event,mouse):
        for b in self.btns:
            if b.is_clicked(event,mouse):
                if b.tag=="quit": save_game(); pygame.quit(); sys.exit()
                self.switch(b.tag)

    def draw(self,surf,mouse):
        surf.fill(BG); draw_hud(surf)
        draw_text(surf,"欢迎光临！选择你想做的事~",22,TEXT_MID,W//2,90,"center")
        for b in self.btns: b.draw(surf,mouse)

# ── 选择面板（甲型 + 底色 + 装饰） ───────────────────────────────────

class PickerScene(Scene):
    # 平板横屏布局：左侧顾客信息+预览，右侧选择区
    SWATCH_SIZE = 72   # 色块/装饰图标尺寸（手指友好）

    def __init__(self, switch, mode="free"):
        self.switch=switch; self.mode=mode
        self.order=generate_order() if mode=="order" else None
        self.sel_shape=0; self.sel_color=0; self.sel_deco=0
        self._build()

    def _build(self):
        ss = self.SWATCH_SIZE
        gap = 10

        # 甲型按钮：横排，右侧区域顶部
        self.shape_btns=[]
        for i,name in enumerate(NAIL_SHAPES):
            bx = 420 + i*(148+8)
            self.shape_btns.append(Button((bx,68,148,54),name,20,tag=i,selected=(i==0)))

        # 底色色块：2行×6列
        self.color_swatches=[]
        for i,(name,cost,rgb) in enumerate(ALL_COLORS):
            col=i%6; row=i//6
            sx=420+col*(ss+gap); sy=140+row*(ss+gap+20)
            unlocked=name in state["unlocked_colors"]
            self.color_swatches.append(ColorSwatch((sx,sy,ss,ss),name,rgb,cost,unlocked=unlocked))
        for i,sw in enumerate(self.color_swatches):
            if sw.unlocked: self.sel_color=i; sw.selected=True; break

        # 装饰图标：2行×5列（"无"也占一格）
        self.deco_swatches=[]
        for i,(name,cost,dc,_) in enumerate(ALL_DECOS):
            col=i%5; row=i//5
            sx=420+col*(ss+gap); sy=430+row*(ss+gap+20)
            unlocked=name in state["unlocked_decos"]
            self.deco_swatches.append(DecoSwatch((sx,sy,ss,ss),name,dc,cost,unlocked=unlocked))
        for i,sw in enumerate(self.deco_swatches):
            if sw.unlocked: self.sel_deco=i; sw.selected=True; break

        self.btn_ok   = Button((W-220,H-80,200,60),"完成！",26,idle=GREEN_OK,hover=(60,210,80),text_color=(255,255,255))
        self.btn_back = Button((20,H-80,140,60),"返回",24,idle=(230,210,220),hover=(210,180,200))

    def _cur_color(self): return ALL_COLORS[self.sel_color]
    def _cur_deco(self):  return ALL_DECOS[self.sel_deco]

    def handle(self,event,mouse):
        if self.btn_back.is_clicked(event,mouse): self.switch("menu"); return
        if self.btn_ok.is_clicked(event,mouse):   self._finish(); return
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
                state["orders_correct"]+=1; earned=o["reward"]
                state["coins"]+=earned; state["score"]+=10; result=("perfect",earned)
            elif hits==2:
                earned=o["reward"]//2; state["coins"]+=earned; state["score"]+=3
                wrong=[k for k,v in zip(["甲型","底色","装饰"],[cs,cc,cd]) if not v]
                result=("ok",earned,wrong[0])
            elif hits==1:
                state["score"]=max(0,state["score"]-2); result=("bad",0)
            else:
                state["score"]=max(0,state["score"]-5); result=("fail",0)
            state["my_works"].append({"shape":shape,"color":cname,"color_rgb":crgb,"deco":dname,"deco_color":dcolor,"time":ts,"perfect":ac})
            self.switch("result",{"shape":shape,"color_rgb":crgb,"deco":dname,"deco_color":dcolor,"cname":cname,"order":o,"result":result,"correct_shape":cs,"correct_color":cc,"correct_deco":cd})
        else:
            state["my_works"].append({"shape":shape,"color":cname,"color_rgb":crgb,"deco":dname,"deco_color":dcolor,"time":ts,"perfect":False})
            self.switch("result_free",{"shape":shape,"color_rgb":crgb,"deco":dname,"deco_color":dcolor,"cname":cname})

    def draw(self,surf,mouse):
        surf.fill(BG); draw_hud(surf)
        ss=self.SWATCH_SIZE

        # 左侧：顾客信息 + 预览
        if self.mode=="order" and self.order:
            o=self.order; tag=["","普通","加急","豪华"][o["tip"]]
            draw_text(surf,f"顾客 {o['name']} [{tag}] {CUSTOMER_MOODS[o['mood']]}：",20,TEXT_DARK,20,65)
            draw_text(surf,f"「{o['shape']} + {o['color']} + {o['deco']}」",24,ACCENT2,20,92)
            draw_text(surf,f"奖励 {o['reward']} 金币",20,GOLD,20,122)
            draw_text(surf,"目标",18,TEXT_MID,20,155)
            oc_rgb=next((rgb for n,_,rgb in ALL_COLORS if n==o["color"]),(200,200,200))
            od_col=next((dc for n,_,dc,__ in ALL_DECOS if n==o["deco"]),None)
            draw_nail(surf,o["shape"],oc_rgb,o["deco"],od_col,110,310,w=120,h=190)
        else:
            draw_text(surf,"自由创作",32,ACCENT2,20,65)

        # 预览
        cname,_,crgb=self._cur_color(); dname,_,dcolor,_=self._cur_deco()
        draw_text(surf,"预览",18,TEXT_MID,260,155)
        draw_nail(surf,NAIL_SHAPES[self.sel_shape],crgb,dname,dcolor,310,310,w=130,h=200)
        draw_text(surf,NAIL_SHAPES[self.sel_shape],16,TEXT_MID,310,418,"center")
        draw_text(surf,cname,16,TEXT_MID,310,436,"center")
        draw_text(surf,dname,16,TEXT_MID,310,454,"center")

        # 右侧：甲型
        draw_text(surf,"甲型",20,TEXT_DARK,420,65,"topleft")
        for b in self.shape_btns: b.draw(surf,mouse)

        # 底色
        draw_text(surf,"底色",20,TEXT_DARK,420,132,"topleft")
        for sw in self.color_swatches:
            sw.draw(surf,mouse)
            tc=ACCENT if sw.selected else TEXT_MID
            draw_text(surf,sw.name,14,tc,sw.rect.centerx,sw.rect.bottom+2,"midtop")

        # 装饰
        draw_text(surf,"装饰",20,TEXT_DARK,420,422,"topleft")
        for sw in self.deco_swatches:
            sw.draw(surf,mouse)
            tc=ACCENT if sw.selected else TEXT_MID
            draw_text(surf,sw.name,14,tc,sw.rect.centerx,sw.rect.bottom+2,"midtop")

        self.btn_ok.draw(surf,mouse); self.btn_back.draw(surf,mouse)

# ── 结果页（订单） ───────────────────────────────────────────────────

class ResultScene(Scene):
    def __init__(self,switch,data):
        self.switch=switch; self.data=data
        self.btn=Button((W//2-160,H-90,320,68),"返回主菜单",26,idle=ACCENT,hover=ACCENT2,text_color=(255,255,255))

    def handle(self,event,mouse):
        if self.btn.is_clicked(event,mouse): self.switch("menu")

    def draw(self,surf,mouse):
        surf.fill(BG); draw_hud(surf)
        d=self.data; o=d["order"]; r=d["result"]
        titles={"perfect":("完美！",GREEN_OK),"ok":("还行~",YELLOW_MID),"bad":("较差…",(200,120,50)),"fail":("失败！",RED_ERR)}
        title,tc=titles[r[0]]
        draw_text(surf,title,46,tc,W//2,65,"center")
        moods={"perfect":f"{o['name']}：太漂亮了！","ok":f"{o['name']}：嗯，将就吧。",
               "bad":f"{o['name']}：不太对…","fail":f"{o['name']}：这不是我要的！"}
        draw_text(surf,moods[r[0]],22,TEXT_MID,W//2,118,"center")

        # 两侧对比甲
        draw_text(surf,"顾客要求",22,TEXT_DARK,W//4,148,"center")
        draw_text(surf,"你做的",22,TEXT_DARK,3*W//4,148,"center")
        oc_rgb=next((rgb for n,_,rgb in ALL_COLORS if n==o["color"]),(200,200,200))
        od_col=next((dc for n,_,dc,__ in ALL_DECOS if n==o["deco"]),None)
        draw_nail(surf,o["shape"],oc_rgb,o["deco"],od_col,W//4,330,w=120,h=190)
        draw_nail(surf,d["shape"],d["color_rgb"],d["deco"],d["deco_color"],3*W//4,330,w=120,h=190)

        for i,(lbl,vo,vp,ok) in enumerate(zip(
                ["甲型","底色","装饰"],[o["shape"],o["color"],o["deco"]],
                [d["shape"],d["cname"],d["deco"]],
                [d["correct_shape"],d["correct_color"],d["correct_deco"]])):
            draw_text(surf,f"{lbl}：{vo}  /  {vp}",20,GREEN_OK if ok else RED_ERR,W//2,460+i*30,"center")

        if r[0] in ("perfect","ok"):
            draw_text(surf,f"+{r[1]} 金币   现有：{state['coins']}",24,GOLD,W//2,560,"center")
        else:
            draw_text(surf,f"扣分   积分：{state['score']}",24,RED_ERR,W//2,560,"center")
        self.btn.draw(surf,mouse)

# ── 结果页（自由创作） ───────────────────────────────────────────────

class ResultFreeScene(Scene):
    def __init__(self,switch,data):
        self.switch=switch; self.data=data
        self.btn=Button((W//2-160,H-90,320,68),"返回主菜单",26,idle=ACCENT,hover=ACCENT2,text_color=(255,255,255))

    def handle(self,event,mouse):
        if self.btn.is_clicked(event,mouse): self.switch("menu")

    def draw(self,surf,mouse):
        surf.fill(BG); draw_hud(surf); d=self.data
        draw_text(surf,"美甲完成！已保存到作品集",36,ACCENT2,W//2,70,"center")
        draw_nail(surf,d["shape"],d["color_rgb"],d["deco"],d["deco_color"],W//2,340,w=150,h=230)
        draw_text(surf,f"{d['shape']}  {d['cname']}  {d['deco']}",24,TEXT_MID,W//2,470,"center")
        draw_text(surf,f"共 {len(state['my_works'])} 件作品",20,TEXT_LITE,W//2,510,"center")
        self.btn.draw(surf,mouse)

# ── 图片墙 ───────────────────────────────────────────────────────────

class GalleryScene(Scene):
    COLS=6; TW=140; TH=190; PAD=16

    def __init__(self,switch):
        self.switch=switch; self.scroll=0
        self.btn_back=Button((20,H-80,140,60),"返回",24,idle=(230,210,220),hover=(210,180,200))

    def handle(self,event,mouse):
        if self.btn_back.is_clicked(event,mouse): self.switch("menu")
        if event.type==pygame.MOUSEWHEEL: self.scroll=max(0,self.scroll-event.y*40)
        # 触摸滑动（FINGERMOTION）
        if event.type==pygame.FINGERMOTION:
            self.scroll=max(0,self.scroll-int(event.dy*H*0.5))

    def draw(self,surf,mouse):
        surf.fill(BG); draw_hud(surf)
        works=state["my_works"]
        draw_text(surf,f"我的作品集  共 {len(works)} 件",28,ACCENT2,W//2,65,"center")
        if not works:
            draw_text(surf,"还没有作品，快去做第一套美甲吧！",24,TEXT_MID,W//2,H//2,"center")
        else:
            start_y=95-self.scroll; x0=20
            for idx,w in enumerate(works):
                col=idx%self.COLS; row=idx//self.COLS
                tx=x0+col*(self.TW+self.PAD); ty=start_y+row*(self.TH+self.PAD+28)
                if ty+self.TH<56 or ty>H: continue
                card=pygame.Rect(tx-8,ty-8,self.TW+16,self.TH+36)
                draw_rrect(surf,PANEL,card,r=12,bw=3 if w.get("perfect") else 1,bc=GOLD if w.get("perfect") else (210,190,210))
                crgb=w.get("color_rgb",(200,200,200)); dcol=w.get("deco_color")
                draw_nail(surf,w["shape"],crgb,w["deco"],dcol,tx+self.TW//2,ty+self.TH//2,self.TW-12,self.TH-12)
                if w.get("perfect"): draw_text(surf,"完美",16,GOLD,tx+self.TW//2,ty+self.TH+2,"midtop")
                draw_text(surf,w["shape"],15,TEXT_MID,tx+self.TW//2,ty+self.TH+18 if not w.get("perfect") else ty+self.TH+18,"midtop")
        self.btn_back.draw(surf,mouse)

# ── 商店 ─────────────────────────────────────────────────────────────

class ShopScene(Scene):
    def __init__(self,switch):
        self.switch=switch; self.msg=""; self.msg_ok=True; self.scroll=0; self._build()

    def _build(self):
        self.items=[]; y=95
        for name,cost,rgb in ALL_COLORS:
            if name not in state["unlocked_colors"]:
                can=state["coins"]>=cost
                btn=Button((W-240,y,210,52),f"解锁 {cost}G",22,idle=BTN_IDLE if can else BTN_LOCK,hover=BTN_HOV if can else BTN_LOCK,tag=("color",name,cost))
                self.items.append(("颜色",name,cost,rgb,pygame.Rect(20,y,68,52),btn)); y+=68
        for name,cost,dc,_ in ALL_DECOS:
            if name not in state["unlocked_decos"]:
                can=state["coins"]>=cost
                btn=Button((W-240,y,210,52),f"解锁 {cost}G",22,idle=BTN_IDLE if can else BTN_LOCK,hover=BTN_HOV if can else BTN_LOCK,tag=("deco",name,cost))
                self.items.append(("装饰",name,cost,dc,pygame.Rect(20,y,68,52),btn)); y+=68
        self.btn_back=Button((20,H-80,140,60),"返回",24,idle=(230,210,220),hover=(210,180,200))
        self.scroll_max=max(0,y-(H-140))

    def handle(self,event,mouse):
        if self.btn_back.is_clicked(event,mouse): self.switch("menu"); return
        if event.type==pygame.MOUSEWHEEL: self.scroll=max(0,min(self.scroll_max,self.scroll-event.y*40))
        if event.type==pygame.FINGERMOTION: self.scroll=max(0,min(self.scroll_max,self.scroll-int(event.dy*H*0.5)))
        for ks,name,cost,color,srect,btn in self.items:
            adj=btn.rect.move(0,-self.scroll)
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1 and adj.collidepoint(mouse):
                k,n,c=btn.tag
                if state["coins"]<c: self.msg=f"金币不足！还差 {c-state['coins']}"; self.msg_ok=False
                else:
                    state["coins"]-=c
                    if k=="color": state["unlocked_colors"].add(n)
                    else:          state["unlocked_decos"].add(n)
                    self.msg=f"已解锁 {n}！"; self.msg_ok=True; self._build()
                return

    def draw(self,surf,mouse):
        surf.fill(BG); draw_hud(surf)
        draw_text(surf,"解锁商店",32,ACCENT2,W//2,65,"center")
        if not self.items:
            draw_text(surf,"所有内容已解锁！",26,GREEN_OK,W//2,200,"center")
        else:
            clip=surf.get_clip(); surf.set_clip(pygame.Rect(0,90,W,H-150))
            for ks,name,cost,color,srect,btn in self.items:
                sy=srect.y-self.scroll
                if sy+68<90 or sy>H-90: continue
                pr=pygame.Rect(20,sy,68,52)
                if ks=="颜色": draw_rrect(surf,color,pr,r=10,bw=2,bc=(200,180,200))
                else:
                    draw_rrect(surf,(245,245,245),pr,r=10,bw=2,bc=(200,180,200))
                    if name!="无": draw_deco(surf,name,pr.centerx,pr.centery,14,color)
                draw_text(surf,f"{ks}  {name}",22,TEXT_DARK,100,sy+14)
                can=state["coins"]>=cost; bc=GREEN_OK if can else (180,180,180)
                adj=btn.rect.move(0,-self.scroll)
                draw_rrect(surf,BTN_IDLE if can else BTN_LOCK,adj,r=10,bw=2,bc=bc)
                draw_text(surf,f"解锁 {cost}G",22,TEXT_DARK if can else TEXT_LITE,adj.centerx,adj.centery,"center")
            surf.set_clip(clip)
        if self.msg:
            draw_text(surf,self.msg,22,GREEN_OK if self.msg_ok else RED_ERR,W//2,H-100,"center")
        self.btn_back.draw(surf,mouse)

# ── 主游戏控制器 ─────────────────────────────────────────────────────

class Game:
    def __init__(self):
        pygame.init()
        # 设置横屏
        if "ANDROID_ARGUMENT" in os.environ or "ANDROID_PRIVATE" in os.environ:
            self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
            global W, H
            W, H = self.screen.get_size()
            # 如果拿到的是竖屏尺寸则交换
            if H > W: W, H = H, W
        else:
            self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("美甲工作室")
        self.clock = pygame.time.Clock()
        init_unlocks()
        self.scene = MenuScene(self.switch)

    def switch(self, name, data=None):
        scenes = {
            "menu":       lambda: MenuScene(self.switch),
            "order":      lambda: PickerScene(self.switch, mode="order"),
            "free":       lambda: PickerScene(self.switch, mode="free"),
            "result":     lambda: ResultScene(self.switch, data),
            "result_free":lambda: ResultFreeScene(self.switch, data),
            "gallery":    lambda: GalleryScene(self.switch),
            "shop":       lambda: ShopScene(self.switch),
        }
        if name in scenes:
            self.scene = scenes[name]()

    def run(self):
        while True:
            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save_game(); pygame.quit(); sys.exit()
                # Android 返回键
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    save_game(); pygame.quit(); sys.exit()
                self.scene.handle(event, mouse)
            self.screen.fill(BG)
            self.scene.draw(self.screen, mouse)
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    Game().run()
