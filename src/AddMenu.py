import os
import pygame
import json
import request_helper
import save_manager
from Button import Button, COLORS
from FontManager import FontManager


class AddMenu:
    def __init__(self, screen, on_close, on_uploaded=None):
        self.screen = screen
        self.on_close = on_close
        self.on_uploaded = on_uploaded

        self.font_title = FontManager.get(36, bold=True)
        self.font_body = FontManager.get(22)
        self.font_small = FontManager.get(18)

        self.active_tab = "Level"
        self.selected_item = None
        self.message = ""
        self.description_input = ""
        self.input_active = False
        self.scroll_offset = 0

        self.btn_tab_level = Button("Levels", (0.27, 0.20, 0.18, 0.07), self.font_body, lambda: self._switch_tab("Level"))
        self.btn_tab_machine = Button("Machines", (0.55, 0.20, 0.18, 0.07), self.font_body, lambda: self._switch_tab("Machine"))

        self.btn_upload = Button("Upload", (0.33, 0.79, 0.11, 0.08), self.font_body, self._upload_selected)
        self.btn_cancel = Button("Cancel", (0.53, 0.79, 0.11, 0.08), self.font_body, self._close)

        self._refresh_local_items()

    def _refresh_local_items(self):
        if self.active_tab == "Level":
            self.local_items = save_manager.list_custom_levels()
        else:
            self.local_items = []
            path = save_manager.get_save_dir()
            for f in os.listdir(path):
                if f.endswith(".json"):
                    self.local_items.append({
                        "name": f[:-5],
                        "description": "Machine save file",
                        "path": os.path.join(path, f)
                    })
        self.selected_item = None
        self.message = ""
        self.scroll_offset = 0
        self.description_input = ""

    def _switch_tab(self, tab):
        self.active_tab = tab
        self._refresh_local_items()

    def _close(self):
        self.on_close()

    def _upload_selected(self):
        if not self.selected_item:
            self.message = "Select an item first."
            return

        if not self.description_input.strip():
            self.message = "Please enter a description before uploading."
            return
        try:
            with open(self.selected_item["path"], "r", encoding="utf-8") as f:
                data = json.load(f)

            if self.active_tab == "Level":
                level = save_manager.Level.from_dict(data)
                level.detailed_description = self.description_input.strip()
                result = request_helper.upload_level(level)
            else:
                data["description"] = self.description_input.strip()
                result = request_helper.upload_machine(data)

            if result:
                self.message = f"{self.active_tab} uploaded successfully!"
                if self.on_uploaded:
                    self.on_uploaded(result)
            else:
                self.message = "Upload failed."
        except Exception as e:
            self.message = f"Error: {e}"

    def handle_event(self, event):
        for b in [self.btn_tab_level, self.btn_tab_machine, self.btn_upload, self.btn_cancel]:
            b.handle_event(event)


        if event.type == pygame.MOUSEBUTTONDOWN:
            w, h, start_y, list_height, pitch, item_h = self._list_metrics()

            for i, item in enumerate(self.local_items):
                item_rect = pygame.Rect(int(w * 0.20), start_y + i * pitch - self.scroll_offset, int(w * 0.60), item_h)
                if item_rect.collidepoint(event.pos):
                    self.selected_item = item
                    self.message = f"Selected: {item['name']}"
                    break

            input_rect = self._get_input_rect()
            self.input_active = input_rect.collidepoint(event.pos)

            if event.button == 4:
                self.scroll_offset -= pitch
                self._clamp_scroll()
            elif event.button == 5:
                self.scroll_offset += pitch
                self._clamp_scroll()

        elif event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                self.input_active = False
            elif event.key == pygame.K_BACKSPACE:
                self.description_input = self.description_input[:-1]
            else:
                if event.unicode.isprintable() and len(self.description_input) < 120:
                    self.description_input += event.unicode
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.on_close()

    def draw(self):
        w, h = self.screen.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        popup_rect = pygame.Rect(int(w * 0.15), int(h * 0.12), int(w * 0.70), int(h * 0.76))
        pygame.draw.rect(self.screen, (25, 28, 48), popup_rect, border_radius=16)
        pygame.draw.rect(self.screen, COLORS["accent"], popup_rect, 2, border_radius=16)

        title = self.font_title.render("Upload to Workshop", True, COLORS["text"])
        self.screen.blit(title, (popup_rect.centerx - title.get_width() // 2, popup_rect.y + 25))

        for b in [self.btn_tab_level, self.btn_tab_machine]:
            b.update_rect((w, h))
            b.draw(self.screen)
        active_btn = self.btn_tab_level if self.active_tab == "Level" else self.btn_tab_machine
        pygame.draw.rect(self.screen, COLORS["accent"], active_btn.rect, 3, border_radius=10)

        self._draw_list_area()

        self._draw_input_box()

        for b in [self.btn_upload, self.btn_cancel]:
            b.update_rect((w, h))
            b.draw(self.screen)

        if self.message:
            msg = self.font_body.render(self.message, True, COLORS["text"])
            self.screen.blit(msg, (popup_rect.centerx - msg.get_width() // 2, h * 0.36 - 40))

    def _draw_list_area(self):
        w, h = self.screen.get_size()
        start_y = int(h * 0.36)
        list_height = int(h * 0.36)

        list_rect = pygame.Rect(int(w * 0.18), start_y - 10, int(w * 0.64), list_height + 20)
        pygame.draw.rect(self.screen, (35, 40, 70), list_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLORS["accent"], list_rect, 1, border_radius=10)

        for i, item in enumerate(self.local_items):
            y = start_y + i * 42 - self.scroll_offset
            if y < start_y - 40 or y > start_y + list_height:
                continue

            item_rect = pygame.Rect(int(w * 0.20), y, int(w * 0.60), 36)
            base_color = (45, 50, 80) if i % 2 == 0 else (55, 60, 90)
            color = COLORS["accent"] if self.selected_item == item else base_color
            pygame.draw.rect(self.screen, color, item_rect, border_radius=6)

            text = self.font_small.render(item["name"], True, COLORS["text"])
            self.screen.blit(text, (item_rect.x + 12, item_rect.y + 8))

    def _get_input_rect(self):
        w, h = self.screen.get_size()
        return pygame.Rect(int(w * 0.22), int(h * 0.74), int(w * 0.56), 36)

    def _draw_input_box(self):
        rect = self._get_input_rect()
        pygame.draw.rect(self.screen, (40, 45, 70), rect, border_radius=8)
        border_color = COLORS["accent"] if self.input_active else (80, 80, 110)
        pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=8)

        placeholder = "Enter description..." if not self.description_input else self.description_input
        color = COLORS["text"] if self.description_input else (150, 150, 160)
        surf = self.font_small.render(placeholder, True, color)
        self.screen.blit(surf, (rect.x + 10, rect.y + 8))

    def _list_metrics(self):
        w, h = self.screen.get_size()
        start_y = int(h * 0.36)
        list_height = int(h * 0.36)
        item_pitch = 42
        item_h = 36
        return w, h, start_y, list_height, item_pitch, item_h

    def _clamp_scroll(self):
        _, _, start_y, list_h, pitch, item_h = self._list_metrics()
        n = len(self.local_items)

        if n <= 0:
            self.scroll_offset = 0
            return

        max_scroll = (n - 1) * pitch + item_h - list_h
        if max_scroll < 0:
            max_scroll = 0

        if self.scroll_offset < 0:
            self.scroll_offset = 0
        elif self.scroll_offset > max_scroll:
            self.scroll_offset = max_scroll
