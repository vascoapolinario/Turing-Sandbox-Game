import json
import math
import os

import pygame
from Levels import LEVELS
from Button import Button, COLORS
from collections import defaultdict
from save_manager import load_progress, is_level_complete, get_level_solution, delete_progress, get_level_stats
from NewLevelPopUp import NewLevelPopup
from Level import Level
from FontManager import FontManager
import save_manager


class LevelSelectMenu:
    def __init__(self, screen, on_close=None):
        self.screen = screen
        self.font_title = FontManager.get(60)
        self.font_large = FontManager.get(40)
        self.font_medium = FontManager.get(28, bold=False)
        self.font_small = FontManager.get(20, bold=False)

        self.level_groups = defaultdict(list)
        for level in LEVELS:
            self.level_groups[level.type].append(level)
        self.selected_type = list(self.level_groups.keys())[0]
        self.selected_level = list(self.level_groups[self.selected_type])[0]
        self.level_buttons = []
        self.type_buttons = []
        self.on_close = on_close

        self.play_button = Button("Play Level", (0.35, 0.88, 0.57, 0.08), self.font_medium, self._confirm_play)
        self.page_index = 0
        self.levels_per_page = 6
        self.delete_level_buttons = {}

        self.solution_button = Button(
            "See Solution",
            (0.69, 0.74, 0.25, 0.08),
            self.font_medium,
            self._see_solution
        )
        self.solution_to_start = [False, None]

        self.resetAllProgress_button = Button(
            "Reset All Progress",
            (0.75, 0.04, 0.22, 0.08),
            self.font_medium,
            lambda: (self.progress.clear(), delete_progress(), self._build_type_buttons(), self._build_level_buttons())
        )

        self.back_button = Button(
            "Back to Main Menu",
            (0.05, 0.04, 0.22, 0.08),
            self.font_medium,
            self.on_close
        )

        self.new_level_button = Button(
            "New Level",
            (0.05, 0.88, 0.22, 0.08),
            self.font_medium,
            self._open_new_level_popup
        )
        self.new_level_popup = None

        custom_levels = self._load_custom_levels()
        if custom_levels:
            for lvl in custom_levels:
                lvl.type = "Custom"
                self.level_groups["Custom"].append(lvl)

        self._build_type_buttons()
        self._build_level_buttons()

        self.level_to_start = None
        self.progress = load_progress()
        self.current_level_stats = None

    def _build_type_buttons(self):
        self.type_buttons.clear()
        y_offset = 0.15
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
        start = self.page_index * self.levels_per_page
        end = start + self.levels_per_page
        visible_levels = levels[start:end]

        base_x, base_y = 0.35, 0.25
        spacing_x = 0.09
        for i, level in enumerate(visible_levels):
            self.level_buttons.append(
                Button(
                    str(start + i + 1),
                    (base_x + i * spacing_x, base_y, 0.07, 0.1),
                    self.font_medium,
                    lambda l=level: self._select_level(l)
                )
            )

        self.prev_page_button = None
        self.next_page_button = None
        total_pages = math.ceil(len(levels) / self.levels_per_page)

        if total_pages > 1:
            if self.page_index > 0:
                self.prev_page_button = Button("<", (0.30, 0.25, 0.04, 0.1), self.font_medium, self._prev_page)
            if self.page_index < total_pages - 1:
                self.next_page_button = Button(">", (0.92, 0.25, 0.04, 0.1), self.font_medium, self._next_page)

    def _select_type(self, type):
        self.selected_type = type
        self.selected_level = self.level_groups[type][0]
        self.current_level_stats = None
        self.page_index = 0
        self._build_level_buttons()

    def _select_level(self, level):
        self.selected_level = level
        self.current_level_stats = None

    def _confirm_play(self):
        if self.selected_level:
            self.level_to_start = self.selected_level

    def handle_event(self, event):
        if self.new_level_popup:
            self.new_level_popup.handle_event(event)
            return

        if self.selected_type == "Custom" and event.type == pygame.MOUSEBUTTONDOWN:
            for level_name, rect in list(self.delete_level_buttons.items()):
                if rect.collidepoint(event.pos):
                    self._delete_custom_level(level_name)
                    return

        self.new_level_button.handle_event(event)
        for button in self.type_buttons:
            button.handle_event(event)
        for button in self.level_buttons:
            button.handle_event(event)
        if hasattr(self, "prev_page_button") and self.prev_page_button:
            self.prev_page_button.handle_event(event)
        if hasattr(self, "next_page_button") and self.next_page_button:
            self.next_page_button.handle_event(event)
        if self.selected_level and is_level_complete(self.selected_level.name):
            self.solution_button.handle_event(event)
        self.play_button.handle_event(event)
        self.resetAllProgress_button.handle_event(event)
        self.back_button.handle_event(event)

    def update(self):
        w, h = self.screen.get_size()
        for btn in self.type_buttons + self.level_buttons + [self.play_button]:
            btn.update_rect((w, h))

    def _draw_title_box(self, text, w, h):
        title_surf = self.font_title.render(text, True, COLORS["text"])
        title_rect = title_surf.get_rect(center=(w / 2, h * 0.05))

        pad_x = 40
        pad_y = 20

        box_rect = pygame.Rect(
            title_rect.x - pad_x // 2,
            title_rect.y - pad_y // 2,
            title_rect.width + pad_x,
            title_rect.height + pad_y
        )

        pygame.draw.rect(self.screen, (50, 70, 110), box_rect, border_radius=15)
        pygame.draw.rect(self.screen, COLORS["accent"], box_rect, 3, border_radius=15)

        self.screen.blit(title_surf, title_rect)

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

        self._draw_title_box("Select Level", w, h)

        left_rect = pygame.Rect(0, 0, w * 0.3, h)
        pygame.draw.rect(self.screen, (25, 30, 55), left_rect)
        pygame.draw.rect(self.screen, COLORS["accent"], left_rect, 2)
        pygame.draw.line(self.screen, COLORS["background"], (left_rect.right, 0), (left_rect.right, h), 2)

        spacing = 20
        for i in range(0, h, spacing):
            pygame.draw.line(self.screen, (40, 50, 80), (0, i), (left_rect.right, i), 1)
        for i in range(0, left_rect.width, spacing):
            pygame.draw.line(self.screen, (40, 50, 80), (i, 0), (i, h), 1)

        for btn in self.type_buttons:
            levels = self.level_groups[btn.text]
            completed = all(is_level_complete(lvl.name) for lvl in levels)
            color = (60, 180, 100) if completed else (180, 80, 80)

            pygame.draw.rect(self.screen, color, btn.rect.inflate(10, 10), border_radius=12)
            if btn.text == self.selected_type:
                pygame.draw.rect(self.screen, COLORS["accent"], btn.rect.inflate(14, 14), 2, border_radius=14)

            btn.draw(self.screen)

        self.delete_level_buttons.clear()
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

            if self.selected_type == "Custom":
                del_rect = pygame.Rect(btn.rect.right + 8, btn.rect.y + 5, 24, 24)
                pygame.draw.rect(self.screen, (120, 40, 40), del_rect, border_radius=4)
                x_text = self.font_small.render("x", True, (255, 255, 255))
                self.screen.blit(x_text, (del_rect.x + 7, del_rect.y - 1))
                self.delete_level_buttons[level.name] = del_rect

        if hasattr(self, "prev_page_button") and self.prev_page_button:
            self.prev_page_button.draw(self.screen)
        if hasattr(self, "next_page_button") and self.next_page_button:
            self.next_page_button.draw(self.screen)

        info_rect = pygame.Rect(w * 0.33, h * 0.38, w * 0.62, h * 0.45)
        pygame.draw.rect(self.screen, (25, 30, 55), info_rect, border_radius=16)
        pygame.draw.rect(self.screen, COLORS["accent"], info_rect, 2, border_radius=16)

        base_height = 720
        scale = max(1, min(2.0, h / base_height))

        self.font_large = FontManager.get(max(40, int(40 * scale)), bold=True)
        self.font_medium = FontManager.get(max(25, int(28 * scale)), bold=False)
        self.font_small = FontManager.get(max(15, int(20 * scale)), bold=False)

        if self.selected_level:
            name = self.font_medium.render(self.selected_level.name, True, COLORS["accent"])
            desc = self._wrap_text(self.selected_level.description, info_rect.width - 40)
            obj = self._wrap_text("Objective: " + self.selected_level.objective, info_rect.width - 40)
            detailed = self._wrap_text(self.selected_level.detailedDescription, info_rect.width - 40)
            if is_level_complete(self.selected_level.name):
                self.solution_button.update_rect((w, h))
                self.solution_button.draw(self.screen)

                if self.current_level_stats is None:
                    self.current_level_stats = get_level_stats(self.selected_level.name)

                stats_text = f"Time: {self.current_level_stats['time']}s, Nodes: {self.current_level_stats['num_nodes']}, Connections: {self.current_level_stats['num_connections']}"
                stats_surf = self.font_small.render(stats_text, True, COLORS["text"])
                self.screen.blit(stats_surf, (info_rect.x + 20, info_rect.bottom - 40))

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
        self.new_level_button.update_rect((w, h))
        self.new_level_button.draw(self.screen)
        self.back_button.update_rect((w, h))
        self.back_button.draw(self.screen)

        if self.new_level_popup:
            self.new_level_popup.draw()

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

    def _open_new_level_popup(self):
        self.new_level_popup = NewLevelPopup(
            self.screen,
            on_save=self._save_new_level,
            on_cancel=self._close_new_level_popup
        )

    def _save_new_level(self, level):
        save_manager.save_custom_level_data(level.name, level.to_dict())

        custom_levels = self._load_custom_levels()
        if custom_levels:
            self.level_groups["Custom"] = custom_levels

        self._build_type_buttons()
        self._build_level_buttons()
        self.new_level_popup = None

    def _load_custom_levels(self):
        custom_levels = []
        for item in save_manager.list_custom_levels():
            try:
                data = item["data"]
                custom_levels.append(Level.from_dict(data))
            except Exception as e:
                print("Error loading custom level:", e)
        return custom_levels

    def _close_new_level_popup(self):
        self.new_level_popup = None

    def _next_page(self):
        self.page_index += 1
        self._build_level_buttons()

    def _prev_page(self):
        self.page_index -= 1
        self._build_level_buttons()

    def _delete_custom_level(self, level_name):
        save_manager.delete_custom_level(level_name)
        print(f"Deleted custom level: {level_name}")

        custom_levels = self._load_custom_levels()

        if custom_levels:
            self.level_groups["Custom"] = custom_levels
        elif "Custom" in self.level_groups:
            del self.level_groups["Custom"]
            if self.selected_type == "Custom":
                self.selected_type = list(self.level_groups.keys())[0]
                self.selected_level = self.level_groups[self.selected_type][0]
                self.current_level_stats = None

        self._build_type_buttons()
        self._build_level_buttons()
