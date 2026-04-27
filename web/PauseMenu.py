import pygame
from Button import Button
from MainMenu import COLORS
from FontManager import FontManager

class PauseMenu:
    def __init__(self, screen, on_resume, on_save_load, on_exit_to_menu, on_levels, on_clear, on_quit, level=None, multiplayer=False):
        self.screen = screen
        self.font_title = FontManager.get(46, bold=True)
        self.font_sub = FontManager.get(22, bold=False)
        self.visible = False
        self.level = level
        self.multiplayer = multiplayer

        if multiplayer:
            self.buttons = [
                Button("Resume", (0.4, 0.45, 0.2, 0.07), self.font_sub, on_resume),
                Button("Leave Lobby", (0.4, 0.55, 0.2, 0.07), self.font_sub, on_exit_to_menu),
                Button("Quit", (0.4, 0.65, 0.2, 0.07), self.font_sub, on_quit),
            ]
        else:
            self.buttons = [
                Button("Resume", (0.4, 0.35, 0.2, 0.07), self.font_sub, on_resume),
                Button("Save/Load", (0.4, 0.45, 0.2, 0.07), self.font_sub, on_save_load),
                Button("Return to Menu", (0.4, 0.55, 0.2, 0.07), self.font_sub, on_exit_to_menu),
                Button("Levels", (0.4, 0.65, 0.2, 0.07), self.font_sub, on_levels),
                Button("Clear Space", (0.4, 0.75, 0.2, 0.07), self.font_sub, on_clear),
                Button("Quit", (0.4, 0.85, 0.2, 0.07), self.font_sub, on_quit),
            ]

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def toggle(self):
        self.visible = not self.visible

    def update(self):
        if not self.visible:
            return
        screen_size = self.screen.get_size()
        for button in self.buttons:
            button.update_rect(screen_size)

    def draw(self):
        if not self.visible:
            return

        w, h = self.screen.get_size()

        overlay = pygame.Surface((w, h))
        overlay.set_alpha(150)
        overlay.fill((15, 20, 40))
        self.screen.blit(overlay, (0, 0))

        title = self.font_title.render("Paused", True, COLORS["accent"])
        self.screen.blit(title, (w / 2 - title.get_width() / 2, h * 0.25))

        if self.level:
            sub = self.font_sub.render(f"Level: {self.level.name}", True, COLORS["text"])
            self.screen.blit(sub, (w / 2 - sub.get_width() / 2, h * 0.33))

        for button in self.buttons:
            button.draw(self.screen)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.toggle()
            return
        if not self.visible:
            return
        for button in self.buttons:
            button.handle_event(event)
