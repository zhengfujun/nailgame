"""
美甲工作室 - Web/Pygbag 入口
用法: pygbag . 或 pygbag main.py
"""
import asyncio
import sys
import os
import pygame

# Web 环境下禁用存档文件读写
import nail_pygame as _ng

import json

_LS_KEY = "nailstudio_save"

def _is_web():
    try:
        import platform
        p = platform.system()
        print(f"[save] platform={p}")
        if p == "Emscripten":
            return True
        # 有些 Pygbag 版本用 sys.platform
        import sys
        print(f"[save] sys.platform={sys.platform}")
        return sys.platform in ("emscripten", "wasi")
    except Exception:
        return False

def _save_game_web():
    try:
        data = json.dumps({
            "coins":   _ng.coins,
            "unlocks": list(_ng.unlocked_items),
        })
        print(f"[save] saving coins={_ng.coins} unlocks={len(_ng.unlocked_items)}")
        if _is_web():
            from js import localStorage
            localStorage.setItem(_LS_KEY, data)
            print("[save] saved to localStorage")
        else:
            with open("savegame.json", "w") as f:
                f.write(data)
            print("[save] saved to file")
    except Exception as e:
        print(f"[save] error: {e}")

def _load_game_web():
    try:
        print("[load] attempting load...")
        data = None
        if _is_web():
            from js import localStorage
            data = localStorage.getItem(_LS_KEY)
            print(f"[load] from localStorage: {data}")
        else:
            if os.path.exists("savegame.json"):
                with open("savegame.json") as f:
                    data = f.read()
        if not data:
            print("[load] no save data found")
            return
        d = json.loads(data)
        _ng.coins = d.get("coins", _ng.coins)
        for item in d.get("unlocks", []):
            _ng.unlocked_items.add(item)
        print(f"[load] loaded coins={_ng.coins}")
    except Exception as e:
        print(f"[load] error: {e}")

_ng.save_game = _save_game_web
_ng.load_game = _load_game_web
_ng.load_game()


def _patch_fonts():
    """在 pygame.init() 之后、Game() 之前，用捆绑字体覆盖字体缓存。"""
    import platform
    cwd = os.getcwd()
    print(f"[font] cwd={cwd}")
    print(f"[font] __file__={__file__}")
    print(f"[font] platform={platform.system()}")

    candidates = [
        "font/NotoSansCJK.ttf",
        os.path.join(cwd, "font", "NotoSansCJK.ttf"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "font", "NotoSansCJK.ttf"),
    ]
    font_path = None
    for p in candidates:
        print(f"[font] checking {p} -> exists={os.path.exists(p)}")
        if os.path.exists(p):
            font_path = p
            break

    if not font_path:
        print("[font] WARNING: NotoSansCJK.ttf not found, Chinese will show as squares")
        return

    print(f"[font] loading from {font_path}")
    _ng._font_obj_cache.clear()
    for size in (13, 16, 20, 26, 34):
        try:
            _ng._font_obj_cache[size] = pygame.font.Font(font_path, size)
        except Exception as e:
            print(f"[font] ERROR loading size {size}: {e}")


async def main():
    from nail_pygame import (
        Game, GW, GH, FPS, BG,
        MenuScene, ShopScene,
        save_game,
    )

    pygame.init()
    _patch_fonts()

    game = Game()
    game.debug_on = False
    game._resize()

    while True:
        mouse_abs = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game()
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key in (
                pygame.K_F1, pygame.K_F2
            ):
                continue
            game.scene.handle(event, mouse_abs)

        if isinstance(game.scene, MenuScene):
            game.scene._build()

        game.scene.update()

        game.game_surf.fill(BG)
        game.scene.draw(game.game_surf, mouse_abs)
        game.screen.blit(game.game_surf, (0, 0))

        pygame.display.flip()
        game.clock.tick(FPS)

        await asyncio.sleep(0)


asyncio.run(main())
