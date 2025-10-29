import os
import platform

import pygame
import sys
import pypresence
from MainMenu import MainMenu
from Environment import Environment
from LevelSelectMenu import LevelSelectMenu
from SettingsMenu import SettingsMenu
from LobbyMenu import LobbyMenu
import request_helper

pygame.init()
import ctypes

DISCORD_CLIENT_ID = "1428136659047809034"
rpc = None
try:
    rpc = pypresence.Presence(DISCORD_CLIENT_ID)
    rpc.connect()
except Exception as e:
    print("Could not connect to Discord:", e)

SCREEN_WIDTH, SCREEN_HEIGHT = 900, 600
WINDOW_TITLE = "Turing Machine Sandbox"

if hasattr(sys, "_MEIPASS"):
    icon_path = os.path.join(sys._MEIPASS, "assets", "favicon.ico")
else:
    icon_path = os.path.join("assets", "favicon.ico")

try:
    icon_surface = pygame.image.load(icon_path)
    pygame.display.set_icon(icon_surface)
except Exception as e:
    print("Not able to load icon:", e)
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


def main():
    menu = MainMenu(screen)
    env = None
    level_menu = None
    settings_menu = None
    multiplayer_menu = None
    state = "main_menu"
    previous_state = None
    discord_available = True
    sandbox_alphabet = ['0', '1', '_']

    running = True
    while running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state == "level_select" and level_menu.new_level_popup is None and level_menu.workshop_menu is None and level_menu.auth_popup is None:
                        state = "main_menu"
                        menu = MainMenu(screen)
            if state == "main_menu":
                menu.handle_event(event)
            elif state == "level_select":
                level_menu.handle_event(event)
            elif state == "settings":
                settings_menu.handle_event(event)

            elif state == "multiplayer":
                multiplayer_menu.handle_event(event)
                if menu.pressed == "":
                    state = "main_menu"
                    request_helper.disconnect_signalr()
            else:
                env.handle_event(event)

        if state == "main_menu":
            menu.update()
            menu.draw()

            if menu.pressed == "sandbox":
                env = Environment(screen, sandbox_alphabet=sandbox_alphabet)
                state = "environment"

            elif menu.pressed == "levels":
                level_menu = LevelSelectMenu(
                    screen,
                    on_close=lambda: setattr(menu, "pressed", "")
                )
                state = "level_select"


            elif menu.pressed == "settings":
                settings_menu = SettingsMenu(screen, on_close=lambda: setattr(menu, "pressed", ""))
                state = "settings"

            elif menu.pressed == "multiplayer":
                multiplayer_menu = LobbyMenu(screen, on_close=lambda: setattr(menu, "pressed", ""))
                state = "multiplayer"

        elif state == "level_select":
            level_menu.update()
            level_menu.draw()
            if menu.pressed == "":
                state = "main_menu"

            if level_menu.level_to_start:
                current_level = level_menu.level_to_start
                env = Environment(screen, level=current_level)
                if level_menu.solution_to_start[0]:
                    env.load_solution(level_menu.solution_to_start[1])
                state = "environment"
        elif state == "settings":
            settings_menu.update(dt)
            settings_menu.draw()

            if menu.pressed == "":
                sandbox_alphabet = settings_menu.sandbox_alphabet
                state = "main_menu"

        elif state == "multiplayer":
            if multiplayer_menu.in_environment:
                multiplayer_menu.environment.update(dt)
                if multiplayer_menu.environment.multiplayer_left:
                    multiplayer_menu.in_environment = False
                    multiplayer_menu._leave_lobby()
                    state = "main_menu"
            else:
                multiplayer_menu.update(dt)
            multiplayer_menu.draw()

        elif state == "environment":
            env.update(dt)
            env.draw()

            if env.back_to_menu and not env.levelselection:
                menu = MainMenu(screen)
                env = None
                state = "main_menu"
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            elif env.levelselection:
                level_menu = LevelSelectMenu(screen)
                env = None
                state = "level_select"
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        if discord_available:
            try:
                if state != previous_state and rpc:
                    if state == "main_menu":
                        rpc.update(state="In main menu", details="Choosing GameMode..", large_image="menu")
                    elif state == "level_select":
                        rpc.update(state="Selecting level", details="Browsing levels", large_image="levels")
                    elif state == "environment":
                        rpc.update(state=f"Playing level: {env.level.name}", details="Building a Turing Machine!", large_image="logo")
                    elif state == "settings":
                        rpc.update(state="In settings menu", details="Adjusting settings", large_image="settings")
                    elif state == "multiplayer":
                        rpc.update(state="In multiplayer menu", details="Solving Levels with others!", large_image="multiplayer")
                    previous_state = state
            except Exception as ex:
                print("Discord RPC error:", ex)
                discord_available = False

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
