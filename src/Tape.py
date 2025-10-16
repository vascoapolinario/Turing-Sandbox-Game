import pygame
from MainMenu import COLORS

class Tape:
    def __init__(self, screen, tape_string=""):
        self.screen = screen
        self.cell_count = len(tape_string) + 10
        self.speed = 400

        self.visible = False
        self.y_offset = 200
        self.target_y_offset = 200
        self.slide_speed = 600

        self.font = pygame.font.SysFont("futura", 48)
        self.cell_color = (50, 70, 110)
        self.border_color = COLORS["accent"]

        self.change_tape(tape_string)

    def show(self):
        self.visible = True
        self.target_y_offset = 0

    def hide(self):
        self.visible = False
        self.target_y_offset = 200

    def change_tape(self, tape_string):
        half = (self.cell_count - len(tape_string)) // 2
        self.symbols = ["_"] * half + list(tape_string) + ["_"] * (self.cell_count - len(tape_string) - half)
        self.cell_index = half

        self.offset = self.cell_index * self.get_cell_width()
        self.target_offset = self.offset

    def move_head(self, direction):
        new_index = self.cell_index + direction

        if new_index < 0:
            self.symbols.insert(0, "_")
            new_index = 0
        elif new_index >= len(self.symbols):
            self.symbols.append("_")

        self.cell_index = max(0, min(new_index, len(self.symbols) - 1))
        self.target_offset = self.cell_index * self.get_cell_width()

    def get_cell_width(self):
        w, _ = self.screen.get_size()
        return w * 0.08

    def update(self, dt):
        if abs(self.target_offset - self.offset) > 1:
            move_dir = (self.target_offset - self.offset) / abs(self.target_offset - self.offset)
            self.offset += move_dir * self.speed * dt
            if (move_dir > 0 and self.offset > self.target_offset) or (move_dir < 0 and self.offset < self.target_offset):
                self.offset = self.target_offset

        if abs(self.target_y_offset - self.y_offset) > 1:
            direction = 1 if self.target_y_offset > self.y_offset else -1
            self.y_offset += direction * self.slide_speed * dt
            if (direction > 0 and self.y_offset > self.target_y_offset) or (direction < 0 and self.y_offset < self.target_y_offset):
                self.y_offset = self.target_y_offset

    def draw(self):
        w, h = self.screen.get_size()
        cell_w = self.get_cell_width()
        cell_h = h * 0.15

        start_x = w / 2 - self.offset
        y = h * 0.9 + self.y_offset

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

    def read_symbol(self):
        return self.symbols[self.cell_index]

    def write_symbol(self, symbol):
        self.symbols[self.cell_index] = symbol

    def move_left(self):
        self.move_head(-1)

    def move_right(self):
        self.move_head(1)

    def reset(self):
        self.cell_index = self.symbols.index(next((s for s in self.symbols if s != "_"), "_"))
        self.offset = self.cell_index * self.get_cell_width()
        self.target_offset = self.offset
        self.hide()

    def get_tape_string(self):
        return "".join(s for s in self.symbols if s != "_")
