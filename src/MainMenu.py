import math

import pygame, random
from Button import Button, COLORS
from Grid import Grid
from Node import Node
from FontManager import FontManager
import request_helper
from AuthenticationPopup import AuthenticationPopup


class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.title_font = pygame.font.SysFont("futura", 80, bold=True)
        self.button_font = pygame.font.SysFont("futura", 32)
        self.title_text = self.title_font.render("Turing Machine Sandbox", True, COLORS["accent"])
        self.pressed = ""
        self.current_user = None
        self.AuthenticationPopup = None

        self.buttons = [
            Button("Levels", (0.4, 0.44, 0.2, 0.08), self.button_font, self.open_levels),
            Button("Sandbox", (0.4, 0.54, 0.2, 0.08), self.button_font, self.start_game),
            Button("Multiplayer", (0.4, 0.64, 0.2, 0.08), self.button_font, self.open_multiplayer),
            Button("Settings", (0.4, 0.74, 0.2, 0.08), self.button_font, self.open_settings),
            Button("Quit", (0.4, 0.84, 0.2, 0.08), self.button_font, self.quit_game),
        ]

        self.title_y_offset = 0
        self.direction = 1

        self.grid = Grid(self.screen)
        self.nodes = []
        self.connections = []
        self.scroll_speed = 200

        self.scroll_offset = 0

        self.symbols_left = [random.choice(['0', '1', '_']) for _ in range(6)]
        self.symbols_right = [random.choice(['0', '1', '_']) for _ in range(6)]

    def populate_nodes(self):
        w, h = self.screen.get_size()
        spacing = self.grid.base_spacing
        z = self.grid.zoom
        center = pygame.Vector2(w / 2, h / 2)

        world_left = self.grid.offset.x - center.x / z
        world_right = world_left + w / z
        world_top = self.grid.offset.y - center.y / z

        kx_start = math.floor((world_left - 2 * spacing) / spacing)
        kx_end = math.floor((world_right + 2 * spacing) / spacing)
        ky_start = math.floor((world_top - 6 * spacing) / spacing)
        ky_end = math.floor((world_top - 1 * spacing) / spacing)

        self.nodes.clear()

        for gx in range(kx_start, kx_end + 1):
            for gy in range(ky_start, ky_end + 1):
                if random.random() < 0.08:
                    x = gx * spacing + random.uniform(-spacing * 0.3, spacing * 0.3)
                    y = gy * spacing + random.uniform(-spacing * 0.3, spacing * 0.3)
                    node = Node(self.grid.snap(pygame.Vector2(x, y)),
                                is_start=random.random() < 0.07,
                                is_end=random.random() < 0.09)
                    self.nodes.append(node)

    def update(self, dt=1 / 60):
        self.title_y_offset += 0.3 * self.direction
        if abs(self.title_y_offset) > 10:
            self.direction *= -1
            self.symbols_left = [random.choice(['0', '1', '_']) for _ in range(6)]
            self.symbols_right = [random.choice(['0', '1', '_']) for _ in range(6)]

        screen_size = self.screen.get_size()
        for button in self.buttons:
            button.update_rect(screen_size)

        move = self.scroll_speed * dt
        self.grid.offset.y -= move

        h = self.screen.get_height()
        spacing = self.grid.base_spacing

        if not self.nodes:
            self.populate_nodes()

        for node in self.nodes:
            screen_pos = self.grid.world_to_screen(node.pos)
            if screen_pos.y - node.radius > h:
                new_y = self.grid.screen_to_world((screen_pos.x, -spacing * 1.5)).y
                node.pos.y = round(new_y / spacing) * spacing

    def draw(self):
        self.screen.fill(COLORS["background"])
        self.grid.draw()

        for node in self.nodes:
            node.draw(self.screen, grid=self.grid)

        w, h = self.screen.get_size()

        scale = max(0.5, min(1.5, h / 720))
        title_font = FontManager.get(int(80* scale), bold=True)
        tape_font = pygame.font.SysFont("consolas", int(28 * scale), bold=True)

        cell_w = int(32 * scale)
        cell_h = int(40 * scale)
        padding = int(8 * scale)
        num_cells = 6

        title_text = title_font.render("Turing Machine Sandbox", True, (255, 255, 255))

        title_y = h * 0.25 + self.title_y_offset
        y_center = title_y
        y_top = y_center - cell_h / 2

        x_center = w / 2
        x_start_left = x_center - title_text.get_width() / 2 - (num_cells * (cell_w + padding)) - 20 * scale
        for i, sym in enumerate(self.symbols_left):
            rect = pygame.Rect(x_start_left + i * (cell_w + padding), y_top, cell_w, cell_h)
            pygame.draw.rect(self.screen, (50, 70, 110), rect, border_radius=6)
            pygame.draw.rect(self.screen, COLORS["accent"], rect, 2, border_radius=6)
            text = tape_font.render(sym, True, COLORS["text"])
            self.screen.blit(text, text.get_rect(center=rect.center))

        x_start_right = x_center + title_text.get_width() / 2 + 30 * scale
        for i, sym in enumerate(self.symbols_right):
            rect = pygame.Rect(x_start_right + i * (cell_w + padding), y_top, cell_w, cell_h)
            pygame.draw.rect(self.screen, (50, 70, 110), rect, border_radius=6)
            pygame.draw.rect(self.screen, COLORS["accent"], rect, 2, border_radius=6)
            text = tape_font.render(sym, True, COLORS["text"])
            self.screen.blit(text, text.get_rect(center=rect.center))

        title_rect = title_text.get_rect(center=(x_center, title_y))
        padding_x = int(20 * scale)
        padding_y = int(10 * scale)
        title_box = pygame.Rect(
            title_rect.x - padding_x,
            title_rect.y - padding_y,
            title_rect.width + padding_x * 2,
            title_rect.height + padding_y * 2
        )

        pygame.draw.rect(self.screen, (50, 70, 110), title_box, border_radius=8)
        pygame.draw.rect(self.screen, COLORS["accent"], title_box, 2, border_radius=8)
        self.screen.blit(title_text, title_rect)

        for button in self.buttons:
            button.draw(self.screen)

        if self.AuthenticationPopup:
            self.AuthenticationPopup.draw()

    def handle_event(self, event):
        if self.AuthenticationPopup:
            self.AuthenticationPopup.handle_event(event)
            return
        for button in self.buttons:
            button.handle_event(event)

    def start_game(self):
        self.pressed = "sandbox"

    def open_levels(self):
        self.pressed = "levels"

    def open_settings(self):
        self.pressed = "settings"

    def open_multiplayer(self):
        if self.current_user is None:
            if request_helper.verify_authentication():
                self.current_user = request_helper.get_user()
                self.pressed = "multiplayer"
            else:
                self.AuthenticationPopup = AuthenticationPopup(self.screen, on_authenticated=self._on_auth)
        else:
            self.pressed = "multiplayer"

    def _on_auth(self, user):
        self.current_user = user
        self.AuthenticationPopup = None
        self.pressed = "multiplayer"

    def quit_game(self):
        pygame.quit()
        raise SystemExit
