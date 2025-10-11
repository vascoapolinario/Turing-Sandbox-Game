import pygame
import sys
from MainMenu import MainMenu
from Environment import Environment

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 900, 600
WINDOW_TITLE = "Turing Machine Sandbox"
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption(WINDOW_TITLE)

clock = pygame.time.Clock()


def main():
    menu = MainMenu(screen)
    env = None
    in_menu = True

    running = True
    while running:
        dt = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if in_menu:
                menu.handle_event(event)
            else:
                env.handle_event(event)

        if in_menu:
            menu.update()
            menu.draw()

            if menu.start_pressed:
                env = Environment(screen)
                in_menu = False

        else:
            env.update(dt)
            env.draw()

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
