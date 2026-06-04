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

_MEMORY_SAVE = {}

def _save_game_web():
    _MEMORY_SAVE["coins"]   = _ng.coins
    _MEMORY_SAVE["unlocks"] = list(_ng.unlocked_items)

def _load_game_web():
    if not _MEMORY_SAVE:
        return
    try:
        _ng.coins = _MEMORY_SAVE.get("coins", _ng.coins)
        for item in _MEMORY_SAVE.get("unlocks", []):
            _ng.unlocked_items.add(item)
    except Exception:
        pass

_ng.save_game = _save_game_web
_ng.load_game = _load_game_web
_ng.load_game()


def _patch_fonts():
    """在 pygame.init() 之后、Game() 之前，用捆绑字体覆盖字体缓存。"""
    font_path = "font/NotoSansCJK.ttf"
    if not os.path.exists(font_path):
        return
    _ng._font_obj_cache.clear()
    for size in (13, 16, 20, 26, 34):
        try:
            _ng._font_obj_cache[size] = pygame.font.Font(font_path, size)
        except Exception:
            pass


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
