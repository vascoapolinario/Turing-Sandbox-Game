import pygame
from MainMenu import COLORS


class Tape:
    def __init__(self, screen, tape_string="10101", cell_count=15):
        self.screen = screen
        self.symbols = ["_"] * ((cell_count - len(tape_string)) // 2) + list(tape_string) + ["_"] * ((cell_count - len(tape_string)) // 2)
        self.cell_count = len(self.symbols)
        self.cell_index_middle = self.cell_count // 2
        for i, s in enumerate(self.symbols):
            if s != "_":
                self.cell_index = i
                break
        else:
            self.cell_index = len(self.symbols) // 2
        self.offset = 0
        self.target_offset = 0
        self.speed = 400

        self.font = pygame.font.SysFont("futura", 48)
        self.cell_color = (50, 70, 110)
        self.border_color = COLORS["accent"]

    def move_head(self, direction):
        new_index = self.cell_index + direction
        if 0 <= new_index < self.cell_count:
            self.cell_index = new_index
            self.target_offset += direction * self.get_cell_width()

    def get_cell_width(self):
        w, _ = self.screen.get_size()
        return w * 0.08

    def update(self, dt):
        if abs(self.target_offset - self.offset) > 1:
            move_dir = (self.target_offset - self.offset) / abs(self.target_offset - self.offset)
            self.offset += move_dir * self.speed * dt
            if (move_dir > 0 and self.offset > self.target_offset) or (move_dir < 0 and self.offset < self.target_offset):
                self.offset = self.target_offset

    def draw(self):
        w, h = self.screen.get_size()
        cell_w = self.get_cell_width()
        cell_h = h * 0.15
        start_x = w / 2 - self.cell_index_middle * cell_w - self.offset
        y = h * 0.9

        tape_y = y + cell_h / 2
        pygame.draw.rect(self.screen, (20, 30, 50), (0, tape_y - 5, w, 10))

        for i, symbol in enumerate(self.symbols):
            x = start_x + i * cell_w
            rect = pygame.Rect(x, y - cell_h / 2, cell_w - 4, cell_h)
            pygame.draw.rect(self.screen, self.cell_color, rect, border_radius=8)
            pygame.draw.rect(self.screen, self.border_color, rect, 2, border_radius=8)

            label = self.font.render(symbol, True, COLORS["text"])
            label_rect = label.get_rect(center=rect.center)
            self.screen.blit(label, label_rect)

        tri_y = y - cell_h / 1.5
        center_x = start_x + self.cell_index * cell_w - 2
        pygame.draw.polygon(self.screen, COLORS["accent"], [
            (center_x - 10, tri_y),
            (center_x + 10, tri_y),
            (center_x, tri_y + 20)
        ])
