import pygame
import sys
from MainMenu import MainMenu
from Environment import Environment
from LevelSelectMenu import LevelSelectMenu

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 900, 600
WINDOW_TITLE = "Turing Machine Sandbox"
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption(WINDOW_TITLE)

clock = pygame.time.Clock()


def main():
    menu = MainMenu(screen)
    env = None
    level_menu = None
    current_level = None
    state = "main_menu"

    running = True
    while running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

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
                state = "environment"

        elif state == "environment":
            env.update(dt)
            env.draw()

            if env.back_to_menu:
                menu = MainMenu(screen)
                env = None
                state = "main_menu"

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
