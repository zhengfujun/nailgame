"""
美甲工作室 - Web/Pygbag 入口
"""
import asyncio
import sys
import os
import json
import pygame

print(f"PLATFORM_CHECK: sys.platform={sys.platform!r}")

import nail_pygame as _ng


def _patch_fonts():
    font_path = "font/NotoSansCJK.ttf"
    if not os.path.exists(font_path):
        font_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "font", "NotoSansCJK.ttf"
        )
    if not os.path.exists(font_path):
        print("[font] NotoSansCJK.ttf not found")
        return
    _ng._font_obj_cache.clear()
    for size in (13, 16, 20, 26, 34):
        try:
            _ng._font_obj_cache[size] = pygame.font.Font(font_path, size)
        except Exception as e:
            print(f"[font] size {size} error: {e}")


async def main():
    from nail_pygame import (
        Game, FPS, BG, MenuScene, save_game, load_game,
    )

    pygame.init()
    _patch_fonts()
    load_game()

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
