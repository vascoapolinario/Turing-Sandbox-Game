import math

import pygame, random
from Button import Button, COLORS
from Grid import Grid
from Node import Node


class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.title_font = pygame.font.SysFont("futura", 80, bold=True)
        self.button_font = pygame.font.SysFont("futura", 32)
        self.title_text = self.title_font.render("Turing Machine Sandbox", True, COLORS["accent"])
        self.pressed = ""

        self.buttons = [
            Button("Levels", (0.4, 0.5, 0.2, 0.08), self.button_font, self.open_levels),
            Button("Sandbox", (0.4, 0.62, 0.2, 0.08), self.button_font, self.start_game),
            Button("Settings", (0.4, 0.74, 0.2, 0.08), self.button_font, self.open_settings),
            Button("Quit", (0.4, 0.86, 0.2, 0.08), self.button_font, self.quit_game),
        ]

        self.title_y_offset = 0
        self.direction = 1

        self.grid = Grid(self.screen)
        self.nodes = []
        self.connections = []
        self.scroll_speed = 200

        self.scroll_offset = 0

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
