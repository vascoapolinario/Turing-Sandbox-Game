import os
import pygame
import json
import request_helper
from Button import Button, COLORS
from FontManager import FontManager
import save_manager
from AddMenu import AddMenu

WORKSHOP_DIR = os.path.expanduser("~/Documents/Turing Sandbox Saves/workshop")
PAGE_SIZE = 6


def _sanitize_filename(name: str) -> str:
    bad = '<>:"/\\|?*'
    for c in bad:
        name = name.replace(c, "_")
    return name.strip()


def _workshop_path(name: str) -> str:
    os.makedirs(WORKSHOP_DIR, exist_ok=True)
    return os.path.join(WORKSHOP_DIR, f"{_sanitize_filename(name)}.json")


class WorkshopMenu:
    def __init__(self, screen, on_close):
        self.screen = screen
        self.on_close = on_close

        self.font_title = FontManager.get(32, bold=True)
        self.font_h3 = FontManager.get(28, bold=True)
        self.font_body = FontManager.get(24)
        self.font_tiny = FontManager.get(18)

        self.items = []
        self.filtered_items = []
        self.search_query = ""
        self.active_tab = "All"
        self.page = 0
        self.input_active = False
        self.user = request_helper.get_user()

        self.btn_back = Button("Back", (0.04, 0.03, 0.12, 0.06), self.font_body, self._close)
        self.btn_search = Button("Search", (0.73, 0.15, 0.15, 0.05), self.font_body, self._do_search)
        self.btn_prev = Button("Prev", (0.63, 0.89, 0.13, 0.06), self.font_body, self._prev_page)
        self.btn_next = Button("Next", (0.80, 0.89, 0.13, 0.06), self.font_body, self._next_page)

        self.btn_tab_all = Button("All", (0.25, 0.03, 0.10, 0.06), self.font_body, lambda: self._switch_tab("All"))
        self.btn_tab_levels = Button("Levels", (0.37, 0.03, 0.15, 0.06), self.font_body, lambda: self._switch_tab("Level"))
        self.btn_tab_machines = Button("Machines", (0.54, 0.03, 0.15, 0.06), self.font_body, lambda: self._switch_tab("Machine"))

        self.btn_add = Button("Add Item", (0.80, 0.03, 0.15, 0.06), self.font_body, self._add_item)

        self._card_buttons_cache = []
        self._buttons_dirty = True

        self.add_menu = None

        self.refresh_items()


    def refresh_items(self, query=""):
        try:
            print("Fetching workshop items...")
            data = request_helper.get_workshop_items(query)
            self.items = data["LevelItems"] + data["MachineItems"]

            self._filter_items()
            self.page = 0
            self._buttons_dirty = True
        except Exception as e:
            print("Failed to load workshop items:", e)
            self.items = []

    def _filter_items(self):
        if self.active_tab == "All":
            self.filtered_items = self.items
        else:
            self.filtered_items = [i for i in self.items if i.get("type", "") == self.active_tab]
        self.filtered_items.sort(key=lambda x: x.get("name", "").lower())


    def _switch_tab(self, tab_name: str):
        self.active_tab = tab_name
        self._filter_items()
        self.page = 0
        self._buttons_dirty = True

    def _do_search(self):
        self.refresh_items(self.search_query)
        self._buttons_dirty = True

    def _prev_page(self):
        if self.page > 0:
            self.page -= 1
            self._buttons_dirty = True

    def _next_page(self):
        if self.page < self._num_pages() - 1:
            self.page += 1
            self._buttons_dirty = True

    def _num_pages(self):
        return max(1, ((len(self.filtered_items) - 1) // PAGE_SIZE) + 1)

    def _toggle_subscription(self, item):
        success = request_helper.toggle_subscription(item["id"])
        if success:
            item["userIsSubscribed"] = not item["userIsSubscribed"]
            self._buttons_dirty = True
            if item["userIsSubscribed"] and item["type"] == "Level":
                save_manager.save_workshop_level(request_helper.workshopitem_to_object(item))
            elif item["userIsSubscribed"] and item["type"] == "Machine":
                save_manager.save_workshop_machine(request_helper.workshopitem_to_object(item))
            elif not item["userIsSubscribed"] and item["type"] == "Level":
                save_manager.delete_workshop_item(item["name"], is_level=True)
            else:
                save_manager.delete_workshop_item(item["name"], is_level=False)
    def _rate_item(self, item, rating: int):
        ok = request_helper.rate_workshop_item(item["id"], rating)
        if ok:
            item["userRating"] = rating
            print(f"Rated item {item['name']} with {rating} stars")
            self._buttons_dirty = True

    def _add_item(self):
        self.add_menu = AddMenu(self.screen, on_close=lambda: setattr(self, "add_menu", None))

    def _close(self):
        self.on_close()


    def handle_event(self, event):
        if self.add_menu:
            self.add_menu.handle_event(event)
            return
        if event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_RETURN:
                self._do_search()
            elif event.key == pygame.K_BACKSPACE:
                self.search_query = self.search_query[:-1]
            else:
                if event.unicode.isprintable():
                    self.search_query += event.unicode
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self._search_rect().collidepoint(event.pos):
                self.input_active = True
            else:
                self.input_active = False

        for b in [self.btn_back, self.btn_search, self.btn_prev, self.btn_next, self.btn_add,
                  self.btn_tab_all, self.btn_tab_levels, self.btn_tab_machines]:
            b.handle_event(event)

        for (card_rect, sub_btn, item, star_rects, delete_btn) in self._card_buttons_cache:
            sub_btn.handle_event(event)
            if delete_btn:
                delete_btn.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(star_rects):
                    if rect.collidepoint(event.pos):
                        self._rate_item(item, i + 1)

    def draw(self):
        w, h = self.screen.get_size()
        self.screen.fill((20, 22, 35))

        for x in range(0, w, 40):
            pygame.draw.line(self.screen, (30, 34, 55), (x, 0), (x, h))
        for y in range(0, h, 40):
            pygame.draw.line(self.screen, (30, 34, 55), (0, y), (w, y))


        container_rect = pygame.Rect(int(w * 0.08), int(h * 0.12), int(w * 0.84), int(h * 0.76))
        pygame.draw.rect(self.screen, (30, 34, 55), container_rect, border_radius=15)
        pygame.draw.rect(self.screen, COLORS["accent"], container_rect, 2, border_radius=15)

        for x in range(container_rect.x, container_rect.right, 40):
            pygame.draw.line(self.screen, (0, 0, 0), (x, container_rect.y), (x, container_rect.bottom))
        for y in range(container_rect.y, container_rect.bottom, 40):
            pygame.draw.line(self.screen, (0, 0, 0), (container_rect.x, y), (container_rect.right, y))

        for b in [self.btn_back, self.btn_add, self.btn_tab_all,
                  self.btn_tab_levels, self.btn_tab_machines]:
            b.update_rect((w, h))
            b.draw(self.screen)

        active_tab_btn = {
            "All": self.btn_tab_all,
            "Level": self.btn_tab_levels,
            "Machine": self.btn_tab_machines
        }[self.active_tab]
        pygame.draw.rect(self.screen, COLORS["accent"], active_tab_btn.rect, 2, border_radius=10)

        self._draw_search_bar()

        self._draw_pagination()

        self._draw_cards()

        if self.add_menu:
            self.add_menu.draw()

    def _search_rect(self):
        w, h = self.screen.get_size()
        return pygame.Rect(int(w * 0.10), int(h * 0.15), int(w * 0.60), int(h * 0.05))

    def _draw_search_bar(self):
        rect = self._search_rect()
        pygame.draw.rect(self.screen, (40, 45, 70), rect, border_radius=20)
        pygame.draw.rect(self.screen, COLORS["accent"], rect, 1, border_radius=20)
        pad = 12
        text = self.search_query or "Search workshop..."
        color = COLORS["text"] if self.search_query else (150, 150, 160)
        surf = self.font_body.render(text, True, color)
        self.screen.blit(surf, (rect.x + pad, rect.y + (rect.height - surf.get_height()) // 2))
        self.btn_search.update_rect(self.screen.get_size())
        self.btn_search.draw(self.screen)
        if self.input_active:
            pygame.draw.rect(self.screen, COLORS["accent"], rect, 2, border_radius=20)

    def _draw_pagination(self):
        w, h = self.screen.get_size()
        text = f"Page {self.page + 1} / {self._num_pages()}"
        surf = self.font_body.render(text, True, COLORS["text"])
        self.screen.blit(surf, (w * 0.45, h * 0.90))
        for b in [self.btn_prev, self.btn_next]:
            b.update_rect((w, h))
            b.draw(self.screen)

    def _draw_cards(self):
        w, h = self.screen.get_size()
        start_y = int(h * 0.24)
        card_w = int(w * 0.36)
        card_h = int(h * 0.14)
        pad_x = int(w * 0.04)
        pad_y = int(h * 0.025)

        visible = self.filtered_items[self.page * PAGE_SIZE:(self.page + 1) * PAGE_SIZE]

        if self._buttons_dirty:
            self._card_buttons_cache.clear()
            for i, item in enumerate(visible):
                col = i % 2
                row = i // 2
                card_x = int(w * 0.10) + col * (card_w + pad_x)
                card_y = start_y + row * (card_h + pad_y)
                card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

                btn_w, btn_h = 120, 34
                btn_x = card_rect.right - btn_w - 15
                btn_y = card_rect.bottom - btn_h - 12

                sub_btn = Button(
                    "Unsubscribe" if item.get("userIsSubscribed", False) else "Subscribe",
                    (
                        btn_x / self.screen.get_width(),
                        btn_y / self.screen.get_height(),
                        btn_w / self.screen.get_width(),
                        btn_h / self.screen.get_height(),
                    ),
                    self.font_tiny,
                    lambda i=item: self._toggle_subscription(i),
                )

                can_delete = (
                        self.user.get("role") == "Admin"
                        or item.get("author") == self.user.get("username")
                )

                delete_btn = None
                if can_delete:
                    del_w, del_h = 100, 34
                    del_x = card_rect.x + 15
                    del_y = card_rect.bottom - del_h - 12
                    delete_btn = Button(
                        "Delete",
                        (
                            del_x / self.screen.get_width(),
                            del_y / self.screen.get_height(),
                            del_w / self.screen.get_width(),
                            del_h / self.screen.get_height(),
                        ),
                        self.font_tiny,
                        lambda i=item: self._delete_workshop_item(i),
                    )

                stars = self._star_rects(5)
                self._card_buttons_cache.append((card_rect, sub_btn, item, stars, delete_btn))
            self._buttons_dirty = False

        for card_rect, sub_btn, item, stars, delete_btn in self._card_buttons_cache:
            self._draw_card(item, card_rect, sub_btn, stars, delete_btn)

    def _draw_card(self, item, card_rect, sub_btn, stars, delete_btn=None):
        pygame.draw.rect(self.screen, (40, 45, 70), card_rect, border_radius=12)
        pygame.draw.rect(self.screen, COLORS["accent"], card_rect, 1, border_radius=12)

        pad_x = 20
        pad_y = 12

        name = self.font_body.render(item.get("type") + ": " +item.get("name", "Unnamed"), True, COLORS["text"])
        self.screen.blit(name, (card_rect.x + pad_x, card_rect.y + pad_y))

        star_start_x = card_rect.right - 140
        for i, srect in enumerate(stars):
            srect.x = star_start_x + i * 22
            srect.y = card_rect.y + pad_y + 2
            color = COLORS["accent"] if i < item.get("userRating", 0) else (100, 100, 100)
            pygame.draw.circle(self.screen, color, srect.center, srect.width // 2)

        pad_y += 26
        author = self.font_tiny.render(f"by {item.get('author', 'Unknown')}", True, (150, 150, 160))
        self.screen.blit(author, (card_rect.x + pad_x, card_rect.y + pad_y))

        desc_text = item.get("description", "")
        if len(desc_text) > 100:
            desc_text = desc_text[:97] + "..."
        pad_y += 20
        desc = self.font_tiny.render(desc_text, True, (180, 180, 180))
        self.screen.blit(desc, (card_rect.x + pad_x, card_rect.y + pad_y))

        pad_y += 20
        rating = item.get("rating", 0.0)
        rating_text = self.font_tiny.render(f"Rating: {rating:.1f}", True, (180, 180, 180))
        self.screen.blit(rating_text, (card_rect.x + pad_x, card_rect.y + pad_y))

        sub_btn.update_rect(self.screen.get_size())
        sub_btn.draw(self.screen)

        if delete_btn:
            delete_btn.update_rect(self.screen.get_size())
            pygame.draw.rect(self.screen, (180, 40, 40), delete_btn.rect, border_radius=10)
            delete_btn.draw(self.screen)


    def _star_rects(self, n):
        size = 18
        return [pygame.Rect(0, 0, size, size) for _ in range(n)]

    def _delete_workshop_item(self, item):
        confirm = True
        if not confirm:
            return

        success = request_helper.delete_workshop_item(item["id"])
        if success:
            print(f"Deleted workshop item {item['name']}")
            self.items = [i for i in self.items if i["id"] != item["id"]]
            self._filter_items()
            self._buttons_dirty = True
