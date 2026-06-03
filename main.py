"""
美甲工作室 - Web/Pygbag 入口
用法: pygbag . 或 pygbag main.py
"""
import asyncio
import sys
import os

# Web 环境下禁用存档文件读写（浏览器无本地文件系统权限）
# 覆盖 nail_pygame 里的存档函数，改为内存存储
import nail_pygame as _ng

_MEMORY_SAVE = {}

def _save_game_web():
    import nail_pygame as m
    _MEMORY_SAVE["coins"]   = m.coins
    _MEMORY_SAVE["unlocks"] = list(m.unlocked_items)

def _load_game_web():
    import nail_pygame as m
    if not _MEMORY_SAVE:
        return
    try:
        m.coins = _MEMORY_SAVE.get("coins", m.coins)
        for item in _MEMORY_SAVE.get("unlocks", []):
            m.unlocked_items.add(item)
    except Exception:
        pass

_ng.save_game = _save_game_web
_ng.load_game = _load_game_web

# 重新执行 load_game 以初始化（此时用 web 版）
_ng.load_game()


async def main():
    import pygame
    from nail_pygame import (
        Game, GW, GH, FPS, BG,
        MenuScene, ShopScene,
        save_game, load_game,
    )

    game = Game()
    # Web 版强制关闭调试面板
    game.debug_on = False
    game._resize()

    while True:
        mouse_abs = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game()
                pygame.quit()
                return

            # 忽略 F1/F2 调试快捷键（Web 版不需要）
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

        await asyncio.sleep(0)  # Pygbag 要求：让出控制权给浏览器


asyncio.run(main())
