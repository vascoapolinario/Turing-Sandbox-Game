import pygame
from Button import Button, COLORS

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.title_font = pygame.font.SysFont("futura", 80, bold=True)
        self.button_font = pygame.font.SysFont("futura", 32)
        self.title_text = self.title_font.render("Turing Machine Sandbox", True, COLORS["accent"])
        self.pressed = None

        self.buttons = [
            Button("Sandbox", (0.4, 0.5, 0.2, 0.08), self.button_font, self.start_game),
            Button("Levels", (0.4, 0.62, 0.2, 0.08), self.button_font, self.open_levels),
            Button("Settings", (0.4, 0.74, 0.2, 0.08), self.button_font, self.open_settings),
            Button("Quit", (0.4, 0.86, 0.2, 0.08), self.button_font, self.quit_game)
        ]

        self.title_y_offset = 0
        self.direction = 1
        self.pressed = ""

    def update(self):
        self.title_y_offset += 0.3 * self.direction
        if abs(self.title_y_offset) > 10:
            self.direction *= -1

        screen_size = self.screen.get_size()
        for button in self.buttons:
            button.update_rect(screen_size)

    def draw(self):
        self.screen.fill(COLORS["background"])
        w, h = self.screen.get_size()
        title_rect = self.title_text.get_rect(center=(w / 2, h * 0.25 + self.title_y_offset))
        self.screen.blit(self.title_text, title_rect)
        for button in self.buttons:
            button.draw(self.screen)

    def handle_event(self, event):
        for button in self.buttons:
            button.handle_event(event)

    def start_game(self):
        self.pressed = "sandbox"

    def open_levels(self):
        self.pressed = "levels"

    def open_settings(self):
        self.pressed = "settings"

    def quit_game(self):
        pygame.quit()
        raise SystemExit
