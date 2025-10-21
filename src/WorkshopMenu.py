import os
import json
import pygame
import requests
from Button import Button, COLORS
from FontManager import FontManager
from save_manager import deserialize_level_from_string

API_URL = "https://localhost:7054/levels"
VERIFY_SSL = False
PAGE_SIZE = 6
WORKSHOP_DIR = os.path.expanduser("~/Documents/Turing Sandbox Saves/workshop")

def _sanitize_filename(name: str) -> str:
    bad = '<>:"/\\|?*'
    for c in bad:
        name = name.replace(c, "_")
    return name.strip()

def _workshop_path(level_name: str) -> str:
    os.makedirs(WORKSHOP_DIR, exist_ok=True)
    return os.path.join(WORKSHOP_DIR, f"{_sanitize_filename(level_name)}.json")


class WorkshopMenu:
    def __init__(self, screen, on_close):
        self.screen = screen
        self.on_close = on_close

        self.font_title = FontManager.get(32, bold=True)
        self.font_h3    = FontManager.get(28, bold=True)
        self.font_body  = FontManager.get(24, bold=False)
        self.font_tiny  = FontManager.get(18, bold=False)

        self.search_query = ""
        self.input_active = False
        self.levels = []
        self.page = 0

        self.btn_back   = Button("Back", (0.04, 0.03, 0.12, 0.06), self.font_body, self._close)
        self.btn_search = Button("Search", (0.73, 0.15, 0.15, 0.05), self.font_body, self._do_search)
        self.btn_prev   = Button("Previous", (0.63, 0.87, 0.13, 0.06), self.font_body, self._prev_page)
        self.btn_next   = Button("Next", (0.80, 0.87, 0.13, 0.06), self.font_body, self._next_page)

        self._card_buttons_cache = []
        self._buttons_dirty = True
        self._fetch_levels()

    def _fetch_levels(self, name_filter: str = ""):
        try:
            params = {"nameFilter": name_filter.strip()} if name_filter.strip() else {}
            r = requests.get(API_URL, params=params, verify=VERIFY_SSL, timeout=10)
            r.raise_for_status()
            self.levels = r.json() or []
            self.page = 0
        except Exception as e:
            print("Failed to fetch workshop levels:", e)
            self.levels = []
            self.page = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self._search_rect().collidepoint(event.pos):
                self.input_active = True
            else:
                self.input_active = False

        if event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_RETURN:
                self._do_search()
            elif event.key == pygame.K_BACKSPACE:
                self.search_query = self.search_query[:-1]
            else:
                if event.unicode.isprintable():
                    self.search_query += event.unicode

        for b in [self.btn_back, self.btn_search, self.btn_prev, self.btn_next]:
            b.handle_event(event)

        for (btn, dto, rect) in self._card_buttons_cache:
            btn.handle_event(event)

    def draw(self):
        w, h = self.screen.get_size()
        self.screen.fill((20, 22, 35))

        for x in range(0, w, 40):
            pygame.draw.line(self.screen, (15, 17, 25), (x, 0), (x, h))
        for y in range(0, h, 40):
            pygame.draw.line(self.screen, (15, 17, 25), (0, y), (w, y))

        container = pygame.Rect(int(w * 0.05), int(h * 0.10), int(w * 0.90), int(h * 0.84))
        pygame.draw.rect(self.screen, (32, 36, 56), container, border_radius=18)
        shadow = pygame.Surface((container.width, container.height), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 70))
        self.screen.blit(shadow, (container.x + 4, container.y + 4))

        title = self.font_title.render("Workshop Browser", True, COLORS["text"])
        pad_x, pad_y = 16, 8
        text_w, text_h = title.get_width(), title.get_height()
        bg_w = text_w + pad_x * 2
        bg_h = text_h + pad_y * 2
        bg_x = container.centerx - bg_w // 2
        bg_y = int(h * 0.03)
        title_bg_rect = pygame.Rect(bg_x, bg_y, bg_w, bg_h)

        shadow_surf = pygame.Surface((title_bg_rect.width, title_bg_rect.height), pygame.SRCALPHA)
        shadow_surf.fill((0, 0, 0, 70))
        self.screen.blit(shadow_surf, (title_bg_rect.x + 4, title_bg_rect.y + 4))

        pygame.draw.rect(self.screen, (40, 45, 70), title_bg_rect, border_radius=14)
        pygame.draw.rect(self.screen, COLORS["accent"], title_bg_rect, 2, border_radius=14)

        self.screen.blit(title, (title_bg_rect.x + (bg_w - text_w) // 2, title_bg_rect.y + (bg_h - text_h) // 2))

        self.btn_back.update_rect((w, h))
        self.btn_back.draw(self.screen)

        self._draw_search_bar(container)

        self._draw_level_grid(self._levels_on_current_page(), container)

        self._draw_pagination(container)

    def _do_search(self):
        self._fetch_levels(self.search_query)
        self._card_buttons_cache.clear()
        self._buttons_dirty = True

    def _search_rect(self) -> pygame.Rect:
        w, h = self.screen.get_size()
        return pygame.Rect(int(w * 0.10), int(h * 0.15), int(w * 0.60), int(h * 0.05))

    def _draw_search_bar(self, container):
        w, h = self.screen.get_size()
        rect = self._search_rect()

        pygame.draw.rect(self.screen, (40, 45, 70), rect, border_radius=20)
        pygame.draw.rect(self.screen, COLORS["accent"], rect, 1, border_radius=20)

        pad = 12
        text = self.search_query if self.search_query else "Search levels by name..."
        color = COLORS["text"] if self.search_query else (150, 150, 160)
        surf = self.font_body.render(text, True, color)
        self.screen.blit(surf, (rect.x + pad, rect.y + (rect.height - surf.get_height()) // 2))

        if self.input_active:
            pygame.draw.rect(self.screen, COLORS["accent"], rect, 2, border_radius=20)

        self.btn_search.update_rect((w, h))
        self.btn_search.draw(self.screen)

    def _levels_on_current_page(self):
        start = self.page * PAGE_SIZE
        end = start + PAGE_SIZE
        return self.levels[start:end]

    def _draw_level_grid(self, cards, container):
        w, h = self.screen.get_size()
        margin_y = container.y + int(h * 0.15)
        padding = int(h * 0.015)
        card_h = int(h * 0.12)
        card_w = int(container.width * 0.40)

        if self._buttons_dirty:
            self._card_buttons_cache.clear()
            y = margin_y
            for dto in cards:
                rect = pygame.Rect(container.x + int(container.width * 0.05), y, card_w, card_h)
                name = dto.get("name", "Untitled")
                subscribed = self._is_subscribed(name)

                btn_w = int(rect.width * 0.18)
                btn_h = int(rect.height * 0.40)
                btn_x = rect.right - btn_w - 20
                btn_y = rect.centery - btn_h // 2

                label = "Unsubscribe" if subscribed else "Subscribe"
                btn = Button(label,
                             (btn_x / w, btn_y / h, btn_w / w, btn_h / h),
                             self.font_body,
                             lambda d=dto, s=subscribed: self._toggle_subscription(d, s))
                btn.update_rect((w, h))
                self._card_buttons_cache.append((btn, dto, rect))
                y += card_h + padding
            self._buttons_dirty = False

        for (btn, dto, rect) in self._card_buttons_cache:
            pygame.draw.rect(self.screen, (45, 50, 75), rect, border_radius=12)
            pygame.draw.rect(self.screen, (70, 75, 110), rect, 1, border_radius=12)

            name = dto.get("name", "Untitled")
            desc = dto.get("description", "")
            subscribed = self._is_subscribed(name)

            title = self.font_h3.render(name, True, COLORS["accent"])
            self.screen.blit(title, (rect.x + 14, rect.y + 10))

            desc_lines = self._wrap_text(desc, rect.width - 200)
            y_text = rect.y + 38
            for line in desc_lines[:2]:
                text_surf = self.font_tiny.render(line, True, COLORS["text"])
                self.screen.blit(text_surf, (rect.x + 14, y_text))
                y_text += text_surf.get_height() + 2

            if subscribed:
                badge = self.font_tiny.render("Subscribed", True, (110, 220, 140))
                self.screen.blit(badge, (rect.x + 14, rect.bottom - 20))

            btn.draw(self.screen)

    def _wrap_text(self, text, max_width):
        words = text.split()
        lines, line = [], ""
        for w in words:
            test = (line + " " + w).strip()
            if self.font_body.size(test)[0] <= max_width:
                line = test
            else:
                lines.append(line)
                line = w
        if line:
            lines.append(line)
        return lines

    def _is_subscribed(self, level_name: str) -> bool:
        return os.path.exists(_workshop_path(level_name))

    def _toggle_subscription(self, dto, subscribed):
        self._buttons_dirty = True
        name = dto.get("name", "Untitled")
        try:
            if subscribed:
                path = _workshop_path(name)
                if os.path.exists(path):
                    os.remove(path)
                    print(f"Unsubscribed {name}")
            else:
                lvl = deserialize_level_from_string(dto)
                to_save = getattr(lvl, "to_dict", None)
                data = to_save() if callable(to_save) else lvl.__dict__
                with open(_workshop_path(lvl.name), "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
                print(f"Subscribed {lvl.name}")
        except Exception as e:
            print("Toggle failed:", e)

    def _num_pages(self):
        return max(1, ((len(self.levels) - 1) // PAGE_SIZE) + 1)

    def _prev_page(self):
        if self.page > 0:
            self.page -= 1
            self._buttons_dirty = True

    def _next_page(self):
        if self.page < self._num_pages() - 1:
            self.page += 1
            self._buttons_dirty = True

    def _draw_pagination(self, container):
        w, h = self.screen.get_size()
        page_text = f"Page {self.page + 1} / {self._num_pages()}"
        surf = self.font_body.render(page_text, True, COLORS["text"])
        self.screen.blit(surf, (container.centerx - surf.get_width() // 2, container.bottom - 40))
        self.btn_prev.update_rect((w, h))
        self.btn_next.update_rect((w, h))
        self.btn_prev.draw(self.screen)
        self.btn_next.draw(self.screen)

    def _close(self):
        self.on_close()
