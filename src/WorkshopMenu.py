import json
import os
import pygame
import requests

import auth_manager
from Button import Button, COLORS
from FontManager import FontManager
from save_manager import list_custom_levels, deserialize_level_from_string, list_saves, load_machine
from SaveMenu import SaveMenu

API_URL = "https://turingmachinesapi.onrender.com/workshop"
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
        self.font_h3 = FontManager.get(28, bold=True)
        self.font_body = FontManager.get(24, bold=False)
        self.font_tiny = FontManager.get(18, bold=False)

        self.adding_mode = False
        self.custom_levels = []
        self.add_scroll = 0
        self.add_card_height = 100

        self.search_query = ""
        self.input_active = False
        self.levels = []
        self.page = 0

        self.active_tab = "Level"
        self.btn_tab_level = Button("Levels", (0.25, 0.03, 0.15, 0.06), self.font_body, self._switch_to_levels)
        self.btn_tab_machine = Button("Machines", (0.43, 0.03, 0.15, 0.06), self.font_body, self._switch_to_machines)

        self.btn_back = Button("Back", (0.04, 0.03, 0.12, 0.06), self.font_body, self._close)
        self.btn_search = Button("Search", (0.73, 0.15, 0.15, 0.05), self.font_body, self._do_search)
        self.btn_prev = Button("Previous", (0.63, 0.87, 0.13, 0.06), self.font_body, self._prev_page)
        self.btn_next = Button("Next", (0.80, 0.87, 0.13, 0.06), self.font_body, self._next_page)
        self.btn_add = Button("Add Level", (0.80, 0.03, 0.15, 0.06), self.font_body, self._add_level)

        self._card_buttons_cache = []
        self._buttons_dirty = True
        self._fetch_levels()

    def _fetch_levels(self, name_filter: str = ""):
        try:
            headers = auth_manager.get_auth_headers()
            params = {"NameFilter": name_filter.strip()} if name_filter.strip() else {}

            r = requests.get(API_URL, params=params, headers=headers, verify=VERIFY_SSL, timeout=10)
            r.raise_for_status()
            self.levels = r.json() or []
            self.levels.sort(key=lambda x: x.get("name", "").lower())

            for item in self.levels:
                try:
                    resp = requests.get(
                        f"{API_URL}/{item['id']}/subscribed",
                        headers=headers,
                        verify=VERIFY_SSL,
                        timeout=5
                    )
                    if resp.status_code == 200:
                        item["subscribed"] = resp.json()
                    else:
                        item["subscribed"] = False

                    r2 = requests.get(
                        f"{API_URL}/{item['id']}/rating",
                        headers=headers,
                        verify=VERIFY_SSL,
                        timeout=5
                    )
                    if r2.status_code == 200:
                        item["user_rating"] = r2.json()
                    else:
                        item["user_rating"] = 0
                except Exception as e:
                    print(f"Failed to check subscription for {item.get('id')}: {e}")
                    item["subscribed"] = False

            self.page = 0
            self._buttons_dirty = True

        except Exception as e:
            print("Failed to fetch workshop items:", e)
            self.levels = []
            self.page = 0

    def _toggle_subscription(self, dto):
        self._buttons_dirty = True
        try:
            headers = auth_manager.get_auth_headers()
            r = requests.post(f"{API_URL}/{dto['id']}/subscribe", headers=headers, verify=VERIFY_SSL)
            if r.status_code == 200:
                print(f"Toggled subscription for {dto['id']}")

                path = _workshop_path(dto["name"])
                if dto.get("subscribed"):
                    if os.path.exists(path):
                        os.remove(path)
                else:
                    r2 = requests.get(f"{API_URL}/{dto['id']}", headers=headers, verify=VERIFY_SSL)
                    if r2.status_code == 200:
                        item_data = r2.json()
                        level_obj = deserialize_level_from_string(item_data)

                        with open(path, "w", encoding="utf-8") as f:
                            json.dump(level_obj.to_dict(), f, indent=4, ensure_ascii=False)
                        print(f"Saved subscribed level: {path}")
                    else:
                        print("Failed to download full level:", r2.status_code, r2.text)

                self._fetch_levels()
            else:
                print("Subscribe failed:", r.text)
        except Exception as e:
            print("Toggle failed:", e)

    def _rate_item(self, dto, stars):
        try:
            headers = auth_manager.get_auth_headers()
            r = requests.post(f"{API_URL}/{dto['id']}/rate/{stars}",headers=headers, verify=VERIFY_SSL)
            if r.status_code == 200:
                print(f"Rated {dto['id']} with {stars} stars")
                self._fetch_levels()
            else:
                print("Rating failed:%d\n %s",r.status_code, r.text)
                print(dto['id'])
        except Exception as e:
            print("Rating failed:", e)

    def _add_level(self):
        try:
            self.custom_levels = list_custom_levels()
            if not self.custom_levels:
                print("No custom levels found.")
                return
            self.adding_mode = True
            self.add_scroll = 0
            self._setup_upload_buttons()
        except Exception as e:
            print("Failed to load custom levels:", e)

    def handle_event(self, event):
        if hasattr(self, "save_menu") and self.save_menu.visible:
            self.save_menu.handle_event(event)
            return

        if event.type == pygame.KEYDOWN and not self.input_active:
            if event.key == pygame.K_ESCAPE and self.adding_mode:
                self._close_upload_popup()
                return
            else:
                self._close()
        if self.adding_mode:
            self._handle_add_menu_event(event)
            return
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

        for b in [self.btn_back, self.btn_search, self.btn_prev, self.btn_next, self.btn_add]:
            b.handle_event(event)

        for btn in [self.btn_tab_level, self.btn_tab_machine]:
            btn.handle_event(event)

        for (btn, dto, rect, stars_rects) in self._card_buttons_cache:
            btn.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, star_rect in enumerate(stars_rects):
                    if star_rect.collidepoint(event.pos):
                        self._rate_item(dto, i + 1)

    def draw(self):
        w, h = self.screen.get_size()
        base_h = 1080
        scale = h / base_h

        self.font_title = FontManager.get(int(32 * scale), bold=True)
        self.font_h3 = FontManager.get(int(28 * scale), bold=True)
        self.font_body = FontManager.get(int(24 * scale))
        self.font_tiny = FontManager.get(int(18 * scale))
        self.screen.fill((20, 22, 35))
        for x in range(0, w, 40):
            pygame.draw.line(self.screen, (15, 17, 25), (x, 0), (x, h))
        for y in range(0, h, 40):
            pygame.draw.line(self.screen, (15, 17, 25), (0, y), (w, y))

        container_outline = pygame.Rect(int(w * 0.05) - 3, int(h * 0.10) - 3, int(w * 0.90) + 6, int(h * 0.84) + 6)
        pygame.draw.rect(self.screen, COLORS["accent"], container_outline, 2, border_radius=20)
        container = pygame.Rect(int(w * 0.05), int(h * 0.10), int(w * 0.90), int(h * 0.84))
        pygame.draw.rect(self.screen, (32, 36, 56), container, border_radius=18)

        for x in range(container.x, container.right, 40):
            pygame.draw.line(self.screen, (25, 27, 40), (x, container.y), (x, container.bottom))
        for y in range(container.y, container.bottom, 40):
            pygame.draw.line(self.screen, (25, 27, 40), (container.x, y), (container.right, y))

        title = self.font_title.render("Workshop Browser", True, COLORS["text"])
        self.screen.blit(title, (container.centerx - title.get_width() // 2, int(h * 0.03)))

        for btn in [self.btn_tab_level, self.btn_tab_machine]:
            btn.update_rect((w, h))
            btn.draw(self.screen)

        active_color = COLORS["accent"]
        if self.active_tab == "Level":
            pygame.draw.rect(self.screen, active_color, self.btn_tab_level.rect, 2, border_radius=10)
        else:
            pygame.draw.rect(self.screen, active_color, self.btn_tab_machine.rect, 2, border_radius=10)

        for b in [self.btn_back, self.btn_add]:
            b.update_rect((w, h))
            b.draw(self.screen)

        self._draw_search_bar(container)
        self._draw_level_grid(self._levels_on_current_page(), container)
        self._draw_pagination(container)

        if hasattr(self, "save_menu") and self.save_menu.visible:
            self.save_menu.draw()
            return

        if self.adding_mode:
            self._draw_add_menu()
            return

    def _draw_level_grid(self, cards, container):
        w, h = self.screen.get_size()
        if not hasattr(self, "_last_size"):
            self._last_size = (w, h)
        elif self._last_size != (w, h):
            self._last_size = (w, h)
            self._buttons_dirty = True
        margin_y = container.y + int(h * 0.15)
        padding = int(h * 0.015)
        card_h = int(h * 0.12)
        card_w = int(container.width * 0.40)

        if self._buttons_dirty:
            self._card_buttons_cache.clear()
            y = margin_y
            for dto in cards:
                rect = pygame.Rect(
                    container.x + int(container.width * 0.05),
                    y,
                    card_w,
                    card_h
                )

                subscribed = dto.get("subscribed", False)
                label = "Unsubscribe" if subscribed else "Subscribe"

                btn_w = int(rect.width * 0.18)
                btn_h = int(rect.height * 0.40)
                btn_x = rect.right - btn_w - int(w * 0.01)
                btn_y = rect.centery - btn_h // 2

                btn = Button(
                    label,
                    (btn_x / w, btn_y / h, btn_w / w, btn_h / h),
                    self.font_body,
                    lambda d=dto, s=subscribed: self._toggle_subscription(d)
                )
                btn.update_rect((w, h))

                star_size = int(rect.height * 0.25)
                star_spacing = int(star_size * 1.4)
                stars_rects = []
                for i in range(5):
                    sx = rect.x + int(rect.width * 0.35) + i * star_spacing
                    sy = rect.bottom - int(rect.height * 0.35)
                    stars_rects.append(pygame.Rect(sx, sy, star_size, star_size))

                self._card_buttons_cache.append((btn, dto, rect, stars_rects))
                y += card_h + padding
            self._buttons_dirty = False

        for (btn, dto, rect, stars_rects) in self._card_buttons_cache:
            pygame.draw.rect(self.screen, (45, 50, 75), rect, border_radius=12)
            pygame.draw.rect(self.screen, (70, 75, 110), rect, 1, border_radius=12)

            name = dto.get("name", "Unnamed")
            author = dto.get("author", "Unknown")
            description = dto.get("description", "")
            subscribers = dto.get("subscribers", 0)

            title_y = rect.y + int(rect.height * 0.10)
            desc_y = rect.y + int(rect.height * 0.45)
            author_y = rect.bottom - int(rect.height * 0.30)

            avg_rating = dto.get("rating", 0)
            title_text = f"{name} ({avg_rating:.1f}/5)"
            title = self.font_h3.render(title_text, True, COLORS["accent"])
            subscribers_text = self.font_tiny.render(f"Subscribers: {subscribers}", True, COLORS["text"])
            self.screen.blit(title, (rect.x + int(rect.width * 0.03), title_y))
            self.screen.blit(subscribers_text, (rect.right - subscribers_text.get_width() - int(rect.width * 0.03), title_y))

            desc = self.font_body.render(description[:50] + ("..." if len(description) > 50 else ""), True,
                                         COLORS["text"])
            self.screen.blit(desc, (rect.x + int(rect.width * 0.03), desc_y))

            author_text = self.font_tiny.render(f"By: {author}", True, COLORS["accent"])
            self.screen.blit(author_text, (rect.x + int(rect.width * 0.03), author_y))

            user_rating = dto.get("user_rating", 0)
            for i, star_rect in enumerate(stars_rects):
                if i < int(user_rating):
                    color = (255, 215, 0)
                else:
                    color = (100, 100, 100)
                star_size = int(rect.height * 0.25)
                pygame.draw.polygon(
                    self.screen,
                    color,
                    [
                        (star_rect.centerx, star_rect.y),
                        (star_rect.right, star_rect.centery - star_size // 4),
                        (star_rect.centerx + star_size // 4, star_rect.bottom),
                        (star_rect.centerx - star_size // 4, star_rect.bottom),
                        (star_rect.left, star_rect.centery - star_size // 4),
                    ],
                )

            btn.draw(self.screen)


    def _do_search(self):
        self._fetch_levels(self.search_query)
        self._card_buttons_cache.clear()
        self._buttons_dirty = True

    def _levels_on_current_page(self):
        filtered = [x for x in self.levels if x.get("type", "").lower() == self.active_tab.lower()]
        start = self.page * PAGE_SIZE
        end = start + PAGE_SIZE
        return filtered[start:end]

    def _prev_page(self):
        if self.page > 0:
            self.page -= 1
            self._buttons_dirty = True

    def _next_page(self):
        if self.page < self._num_pages() - 1:
            self.page += 1
            self._buttons_dirty = True

    def _num_pages(self):
        return max(1, ((len(self.levels) - 1) // PAGE_SIZE) + 1)

    def _draw_search_bar(self, container):
        w, h = self.screen.get_size()
        rect = self._search_rect()
        pygame.draw.rect(self.screen, (40, 45, 70), rect, border_radius=20)
        pygame.draw.rect(self.screen, COLORS["accent"], rect, 1, border_radius=20)

        pad = 12
        text = self.search_query if self.search_query else "Search levels by name..."
        if text == "Search levels by name..." and self.active_tab == "Machine":
            text = "Search machines by name..."
        color = COLORS["text"] if self.search_query else (150, 150, 160)
        surf = self.font_body.render(text, True, color)
        self.screen.blit(surf, (rect.x + pad, rect.y + (rect.height - surf.get_height()) // 2))
        if self.input_active:
            pygame.draw.rect(self.screen, COLORS["accent"], rect, 2, border_radius=20)
        self.btn_search.update_rect((w, h))
        self.btn_search.draw(self.screen)

    def _search_rect(self) -> pygame.Rect:
        w, h = self.screen.get_size()
        return pygame.Rect(int(w * 0.10), int(h * 0.15), int(w * 0.60), int(h * 0.05))

    def _draw_pagination(self, container):
        w, h = self.screen.get_size()
        page_text = f"Page {self.page + 1} / {self._num_pages()}"
        surf = self.font_body.render(page_text, True, COLORS["text"])
        self.screen.blit(surf, (container.centerx - surf.get_width() // 2, container.bottom - 40))
        self.btn_prev.update_rect((w, h))
        self.btn_next.update_rect((w, h))
        self.btn_prev.draw(self.screen)
        self.btn_next.draw(self.screen)

    def _draw_add_menu(self):
        w, h = self.screen.get_size()

        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        modal_w, modal_h = int(w * 0.5), int(h * 0.5)
        modal_x, modal_y = (w - modal_w) // 2, (h - modal_h) // 2
        rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)
        pygame.draw.rect(self.screen, (30, 33, 52), rect, border_radius=14)
        pygame.draw.rect(self.screen, COLORS["accent"], rect, 2, border_radius=14)

        title = self.font_h3.render("Upload Custom Level", True, COLORS["accent"])
        if self.active_tab == "Machine":
            title = self.font_h3.render("Upload Custom Machine", True, COLORS["accent"])
        self.screen.blit(title, (rect.centerx - title.get_width() // 2, rect.y + 20))

        card_h = 50
        padding = 10
        start_y = rect.y + 80
        visible_levels = self.custom_levels[self.add_scroll:self.add_scroll + 6]

        for i, lvl in enumerate(visible_levels):
            y = start_y + i * (card_h + padding)
            card = pygame.Rect(rect.x + 20, y, modal_w - 40, card_h)
            pygame.draw.rect(self.screen, (45, 50, 75), card, border_radius=8)
            pygame.draw.rect(self.screen, (70, 75, 110), card, 1, border_radius=8)

            name = self.font_body.render(lvl["name"], True, COLORS["text"])
            self.screen.blit(name, (card.x + 12, card.y + 10))

        for btn in self._upload_buttons:
            btn.update_rect((w, h))
            btn.draw(self.screen)

    def _handle_add_menu_event(self, event):
        for btn in self._upload_buttons:
            btn.handle_event(event)

        if event.type == pygame.MOUSEWHEEL:
            self.add_scroll = max(0, min(self.add_scroll - event.y, len(self.custom_levels) - 6))
            self._setup_upload_buttons()

    def _add_machine(self):
        def on_upload(save):
            try:
                data = load_machine(save["name"])
                headers = auth_manager.get_auth_headers()
                payload = {
                    "name": save["name"],
                    "description": "",
                    "authorName": auth_manager.get_username(),
                    "type": "Machine",
                    "machineData": json.dumps(data, ensure_ascii=False)
                }
                r = requests.post(API_URL, json=payload, headers=headers, verify=VERIFY_SSL)
                if r.status_code in (200, 201):
                    print(f"Uploaded machine {save['name']} successfully!")
                    self._fetch_levels()
                else:
                    print("Upload failed:", r.status_code, r.text)
            except Exception as e:
                print("Upload error:", e)

        self.save_menu = SaveMenu(
            self.screen,
            turing_machine=None,
            on_close=self._close_save_menu,
            on_load=None,
            upload_mode=True,
            on_upload=on_upload
        )
        self.save_menu.show()

    def _close_save_menu(self):
        if hasattr(self, "save_menu"):
            self.save_menu.visible = False
            del self.save_menu

    def _setup_upload_buttons_machine(self):
        self._upload_buttons = []
        w, h = self.screen.get_size()
        modal_w, modal_h = int(w * 0.5), int(h * 0.5)
        modal_x, modal_y = (w - modal_w) // 2, (h - modal_h) // 2
        card_h = 50
        padding = 10
        start_y = modal_y + 80
        visible = self.custom_machines[self.add_scroll:self.add_scroll + 6]

        for i, m in enumerate(visible):
            y = start_y + i * (card_h + padding)
            btn_x = modal_x + modal_w - 130
            btn_y = y + (card_h - 36) // 2
            btn = Button(
                "Upload",
                (btn_x / w, btn_y / h, 100 / w, 36 / h),
                self.font_tiny,
                lambda machine=m: self._upload_machine(m)
            )
            self._upload_buttons.append(btn)

        close_btn = Button(
            "Close",
            ((modal_x + modal_w - 120) / w, (modal_y + 20) / h, 90 / w, 36 / h),
            self.font_tiny,
            self._close_upload_popup
        )
        self._upload_buttons.append(close_btn)

    def _upload_machine(self, machine):
        try:
            headers = auth_manager.get_auth_headers()
            payload = {
                "name": machine["name"],
                "description": machine.get("description", ""),
                "authorName": auth_manager.get_username(),
                "type": "Machine",
                "machineData": json.dumps(machine["data"], ensure_ascii=False)
            }

            r = requests.post(API_URL, json=payload, headers=headers, verify=VERIFY_SSL)
            if r.status_code in (200, 201):
                print(f"Uploaded machine {machine['name']} successfully!")
                self._close_upload_popup()
                self._fetch_levels()
                self._buttons_dirty = True
            else:
                print("Upload failed:", r.status_code, r.text)
        except Exception as e:
            print("Upload error:", e)

    def _upload_level(self, lvl):
        try:
            headers = auth_manager.get_auth_headers()
            payload = {
                "name": lvl["name"],
                "description": lvl.get("description", ""),
                "authorName": auth_manager.get_username(),
                "type": "Level",
                "levelData": json.dumps(lvl["data"], ensure_ascii=False)
            }

            r = requests.post(API_URL, json=payload, headers=headers, verify=VERIFY_SSL)
            if r.status_code in (200, 201):
                print(f"Uploaded {lvl['name']} successfully!")
                self._close_upload_popup()
                self._fetch_levels()
                self._buttons_dirty = True
            else:
                print("Upload failed:", r.status_code, r.text)
        except Exception as e:
            print("Upload error:", e)

    def _setup_upload_buttons(self):
        self._upload_buttons = []
        w, h = self.screen.get_size()

        modal_w, modal_h = int(w * 0.5), int(h * 0.5)
        modal_x, modal_y = (w - modal_w) // 2, (h - modal_h) // 2

        card_h = 50
        padding = 10
        start_y = modal_y + 80

        visible_levels = self.custom_levels[self.add_scroll:self.add_scroll + 6]

        for i, lvl in enumerate(visible_levels):
            y = start_y + i * (card_h + padding)
            btn_x = modal_x + modal_w - 130
            btn_y = y + (card_h - 36) // 2
            btn = Button(
                "Upload",
                (btn_x / w, btn_y / h, 100 / w, 36 / h),
                self.font_tiny,
                lambda l=lvl: self._upload_level(l)
            )
            self._upload_buttons.append(btn)

        close_btn = Button(
            "Close",
            ((modal_x + modal_w - 120) / w, (modal_y + 20) / h, 90 / w, 36 / h),
            self.font_tiny,
            self._close_upload_popup
        )
        self._upload_buttons.append(close_btn)

    def _switch_to_levels(self):
        self.active_tab = "Level"
        self.btn_add.text = "Add Level"
        self.btn_add.callback = self._add_level
        self._buttons_dirty = True

    def _switch_to_machines(self):
        self.active_tab = "Machine"
        self.btn_add.text = "Add Machine"
        self.btn_add.callback = self._add_machine
        self._buttons_dirty = True

    def _close_upload_popup(self):
        self.adding_mode = False
        self._upload_buttons = []

    def _close(self):
        self.on_close()
