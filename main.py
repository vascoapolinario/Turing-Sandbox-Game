import os
import platform
import sys

import pygame
from MainMenu import MainMenu
from Environment import Environment
from LevelSelectMenu import LevelSelectMenu
import asyncio

pygame.init()
import ctypes

SCREEN_WIDTH, SCREEN_HEIGHT = 1600, 1000
WINDOW_TITLE = "Turing Machine Sandbox"
if os.path.exists("Logo2.png"):
    pygame.display.set_icon(pygame.image.load("Logo2.png"))
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)

if platform.system() == "Windows":
    try:
        hwnd = pygame.display.get_wm_info().get("window")
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 3)
    except Exception as e:
        print("Could not maximize window:", e)

pygame.display.set_caption(WINDOW_TITLE)

clock = pygame.time.Clock()


async def main():
    menu = MainMenu(screen)
    env = None
    level_menu = None
    state = "main_menu"

    running = True
    while running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state == "level_select":
                        state = "main_menu"
                        menu = MainMenu(screen)
            if state == "main_menu":
                menu.handle_event(event)
            elif state == "level_select":
                level_menu.handle_event(event)
            else:
                env.handle_event(event)

        if state == "main_menu":
            menu.update()
            menu.draw()

            if menu.pressed == "sandbox":
                env = Environment(screen)
                state = "environment"

            elif menu.pressed == "levels":
                level_menu = LevelSelectMenu(screen)
                state = "level_select"

        elif state == "level_select":
            level_menu.update()
            level_menu.draw()
            if level_menu.level_to_start:
                current_level = level_menu.level_to_start
                env = Environment(screen, level=current_level)
                if level_menu.solution_to_start[0]:
                    env.load_solution(level_menu.solution_to_start[1])
                state = "environment"

        elif state == "environment":
            env.update(dt)
            env.draw()

            if env.back_to_menu:
                menu = MainMenu(screen)
                env = None
                state = "main_menu"

        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()
    sys.exit()



asyncio.run(main())
