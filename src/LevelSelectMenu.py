import math

import pygame
from Levels import LEVELS
from Button import Button, COLORS
from collections import defaultdict
from save_manager import load_progress, is_level_complete, get_level_solution, delete_progress

class LevelSelectMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font_large = pygame.font.SysFont("futura", 40, bold=True)
        self.font_medium = pygame.font.SysFont("futura", 28)
        self.font_small = pygame.font.SysFont("futura", 20)

        self.level_groups = defaultdict(list)
        for level in LEVELS:
            self.level_groups[level.type].append(level)
        self.selected_type = list(self.level_groups.keys())[0]
        self.selected_level = list(self.level_groups[self.selected_type])[0]
        self.level_buttons = []
        self.type_buttons = []

        self.play_button = Button("Play Level", (0.35, 0.88, 0.57, 0.08), self.font_medium, self._confirm_play)

        self.solution_button = Button(
            "See Solution",
            (0.65, 0.74, 0.25, 0.08),
            self.font_medium,
            self._see_solution
        )
        self.solution_to_start = [False, None]

        self.resetAllProgress_button = Button(
            "Reset All Progress",
            (0.05, 0.04, 0.22, 0.08),
            self.font_medium,
            lambda: (self.progress.clear(), delete_progress(), self._build_type_buttons(), self._build_level_buttons())
        )

        self._build_type_buttons()
        self._build_level_buttons()

        self.level_to_start = None
        self.progress = load_progress()

    def _build_type_buttons(self):
        self.type_buttons.clear()
        y_offset = 0.25
        spacing = 0.1
        for i, t in enumerate(self.level_groups.keys()):
            self.type_buttons.append(
                Button(
                    t,
                    (0.05, y_offset + i * spacing, 0.22, 0.08),
                    self.font_medium,
                    lambda typ=t: self._select_type(typ)
                )
            )

    def _build_level_buttons(self):
        self.level_buttons.clear()
        levels = self.level_groups[self.selected_type]
        base_x, base_y = 0.35, 0.25
        spacing_x = 0.09
        for i, level in enumerate(levels):
            self.level_buttons.append(
                Button(
                    str(i + 1),
                    (base_x + i * spacing_x, base_y, 0.07, 0.1),
                    self.font_medium,
                    lambda l=level: self._select_level(l)
                )
            )

    def _select_type(self, type):
        self.selected_type = type
        self.selected_level = self.level_groups[type][0]
        self._build_level_buttons()

    def _select_level(self, level):
        self.selected_level = level

    def _confirm_play(self):
        if self.selected_level:
            self.level_to_start = self.selected_level

    def handle_event(self, event):
        for button in self.type_buttons:
            button.handle_event(event)
        for button in self.level_buttons:
            button.handle_event(event)
        if self.selected_level and is_level_complete(self.selected_level.name):
            self.solution_button.handle_event(event)
        self.play_button.handle_event(event)
        self.resetAllProgress_button.handle_event(event)

    def update(self):
        w, h = self.screen.get_size()
        for btn in self.type_buttons + self.level_buttons + [self.play_button]:
            btn.update_rect((w, h))

    def draw(self):
        w, h = self.screen.get_size()
        self.screen.fill(COLORS["background"])

        time = pygame.time.get_ticks() / 1000
        glow = (1 + math.sin(time * 2)) / 2
        glow_color = (int(50 + 50 * glow), int(55 + 50 * glow), int(80 + 50 * glow))
        for x in range(0, w, 40):
            pygame.draw.line(self.screen, glow_color, (x, 0), (x, h))
        for y in range(0, h, 40):
            pygame.draw.line(self.screen, glow_color, (0, y), (w, y))


        title = self.font_large.render("Select Level", True, COLORS["accent"])
        self.screen.blit(title, (w * 0.5 - title.get_width() // 2, 40))


        left_rect = pygame.Rect(0, 0, w * 0.3, h)
        pygame.draw.rect(self.screen, (25, 30, 55), left_rect)
        pygame.draw.rect(self.screen, COLORS["accent"], left_rect, 2)
        pygame.draw.line(self.screen, COLORS["background"], (left_rect.right, 0), (left_rect.right, h), 2)

        #spacing = 20
        #for i in range(0, h, spacing):
        #    pygame.draw.line(self.screen, (40, 50, 80), (0, i), (left_rect.right, i), 1)
        #for i in range(0, left_rect.width, spacing):
        #    pygame.draw.line(self.screen, (40, 50, 80), (i, 0), (i, h), 1)

        for btn in self.type_buttons:
            levels = self.level_groups[btn.text]
            completed = all(is_level_complete(lvl.name) for lvl in levels)
            color = (60, 180, 100) if completed else (180, 80, 80)

            pygame.draw.rect(self.screen, color, btn.rect.inflate(10, 10), border_radius=12)
            if btn.text == self.selected_type:
                pygame.draw.rect(self.screen, COLORS["accent"], btn.rect.inflate(14, 14), 2, border_radius=14)

            btn.draw(self.screen)

        for btn in self.level_buttons:
            level = next((lvl for lvl in self.level_groups[self.selected_type]
                          if str(self.level_groups[self.selected_type].index(lvl) + 1) == btn.text), None)
            if level:
                completed = is_level_complete(level.name)
                if completed:
                    pygame.draw.rect(self.screen, (60, 180, 100), btn.rect.inflate(10, 10), border_radius=10)
                else:
                    pygame.draw.rect(self.screen, (180, 80, 80), btn.rect.inflate(10, 10), border_radius=10)

                if self.selected_level == level:
                    pygame.draw.rect(self.screen, COLORS["accent"], btn.rect.inflate(14, 14), 2, border_radius=12)
            btn.draw(self.screen)

        info_rect = pygame.Rect(w * 0.33, h * 0.38, w * 0.62, h * 0.45)
        pygame.draw.rect(self.screen, (25, 30, 55), info_rect, border_radius=16)
        pygame.draw.rect(self.screen, COLORS["accent"], info_rect, 2, border_radius=16)

        base_height = 720
        scale = max(1, min(2.0, h / base_height))
        self.font_large = pygame.font.SysFont("futura", max(30, int(40 * scale)), bold=True)
        self.font_medium = pygame.font.SysFont("futura", max(25, int(28 * scale)))
        self.font_small = pygame.font.SysFont("futura", max(15, int(20 * scale)))

        if self.selected_level:
            name = self.font_medium.render(self.selected_level.name, True, COLORS["accent"])
            desc = self._wrap_text(self.selected_level.description, info_rect.width - 40)
            obj = self._wrap_text("Objective: " + self.selected_level.objective, info_rect.width - 40)
            detailed = self._wrap_text(self.selected_level.detailedDescription, info_rect.width - 40)
            if is_level_complete(self.selected_level.name):
                self.solution_button.update_rect((w, h))
                self.solution_button.draw(self.screen)

            self.screen.blit(name, (info_rect.x + 20, info_rect.y + 20))

            y_offset = info_rect.y + 70
            for line in desc:
                line_surface = self.font_small.render(line, True, COLORS["text"])
                self.screen.blit(line_surface, (info_rect.x + 20, y_offset))
                y_offset += 25

            y_offset += 10
            for line in obj:
                line_surface = self.font_small.render(line, True, COLORS["text"])
                self.screen.blit(line_surface, (info_rect.x + 20, y_offset))
                y_offset += 25

            y_offset += 10
            for line in detailed:
                line_surface = self.font_small.render(line, True, COLORS["text"])
                self.screen.blit(line_surface, (info_rect.x + 20, y_offset))
                y_offset += 25

        self.play_button.draw(self.screen)
        self.resetAllProgress_button.update_rect((w, h))
        self.resetAllProgress_button.draw(self.screen)

    def _wrap_text(self, text, max_width):
        words = text.split()
        lines, line = [], ""
        for word in words:
            test = (line + " " + word).strip()
            if self.font_small.size(test)[0] <= max_width:
                line = test
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
        return lines

    def _see_solution(self):
        if self.selected_level and is_level_complete(self.selected_level.name):
            solution_data = get_level_solution(self.selected_level.name)
            if solution_data:
                self.solution_to_start = [True, solution_data]
            self.level_to_start = self.selected_level
