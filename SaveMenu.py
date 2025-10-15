import pygame
from MainMenu import COLORS
from Button import Button
import save_manager

class SaveMenu:
    def __init__(self, screen, turing_machine, on_close, on_load):
        self.screen = screen
        self.visible = False
        self.font = pygame.font.SysFont("futura", 26, bold=True)
        self.small = pygame.font.SysFont("futura", 18)
        self.turing_machine = turing_machine
        self.on_close = on_close
        self.on_load = on_load

        self.page = 0
        self.per_page = 6
        self.saves = []
        self.input_active = False
        self.input_text = ""

        self.close_button = Button("Back", (0.05, 0.1, 0.1, 0.07), self.small, self.close)
        self.new_button = Button("+ New Save", (0.80, 0.1, 0.15, 0.07), self.small, self.new_save_prompt)
        self.prev_button = Button("< Prev", (0.30, 0.88, 0.15, 0.07), self.small, self.prev_page)
        self.next_button = Button("Next >", (0.55, 0.88, 0.15, 0.07), self.small, self.next_page)

        self.refresh()

    def refresh(self):
        self.saves = save_manager.list_saves()
        total_pages = max(1, (len(self.saves) - 1) // self.per_page + 1)
        self.page = min(self.page, total_pages - 1)

    def show(self):
        self.visible = True
        self.refresh()

    def close(self):
        self.visible = False
        self.input_active = False
        self.input_text = ""
        self.on_close()

    def new_save_prompt(self):
        self.input_active = True
        self.input_text = ""

    def prev_page(self):
        if self.page > 0:
            self.page -= 1

    def next_page(self):
        total_pages = max(1, (len(self.saves) - 1) // self.per_page + 1)
        if self.page < total_pages - 1:
            self.page += 1

    def update(self):
        if not self.visible:
            return
        screen_size = self.screen.get_size()
        self.close_button.update_rect(screen_size)
        self.new_button.update_rect(screen_size)
        self.prev_button.update_rect(screen_size)
        self.next_button.update_rect(screen_size)

    def handle_event(self, event):
        if not self.visible:
            return

        if self.input_active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and self.input_text.strip():
                    data = self.turing_machine.serialize(self.input_text)
                    save_manager.save_machine(self.input_text, data)
                    self.input_active = False
                    self.refresh()
                elif event.key == pygame.K_ESCAPE:
                    self.input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                elif len(self.input_text) < 20 and event.unicode.isprintable():
                    self.input_text += event.unicode
            return

        self.close_button.handle_event(event)
        self.new_button.handle_event(event)
        self.prev_button.handle_event(event)
        self.next_button.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            grid_rect = self._grid_rect()

            if grid_rect.collidepoint(x, y):
                for i, save in enumerate(
                        self.saves[self.page * self.per_page: (self.page + 1) * self.per_page]
                ):
                    slot_rect = self._slot_rect(i)
                    delete_rect = self._delete_rect(slot_rect)

                    if delete_rect.collidepoint(x, y):
                        save_manager.delete_machine(save["name"])
                        self.refresh()
                        return

                    if slot_rect.collidepoint(x, y):
                        self.on_load(save["name"])
                        self.close()
                        return

    def draw(self):
        if not self.visible:
            return

        w, h = self.screen.get_size()
        overlay = pygame.Surface((w, h))
        overlay.set_alpha(160)
        overlay.fill((10, 15, 30))
        self.screen.blit(overlay, (0, 0))

        title = self.font.render("Saved Turing Machines", True, COLORS["accent"])
        self.screen.blit(title, (w/2 - title.get_width()/2, 40))

        grid_rect = self._grid_rect()
        pygame.draw.rect(self.screen, (35, 45, 70), grid_rect, border_radius=18)
        pygame.draw.rect(self.screen, COLORS["accent"], grid_rect, 2, border_radius=18)

        self.close_button.draw(self.screen)
        self.new_button.draw(self.screen)
        self.prev_button.draw(self.screen)
        self.next_button.draw(self.screen)

        total_pages = max(1, (len(self.saves) - 1) // self.per_page + 1)
        page_label = self.small.render(f"Page {self.page + 1}/{total_pages}", True, COLORS["accent"])
        self.screen.blit(page_label,
                         (self.screen.get_width() / 2 - page_label.get_width() / 2, self.screen.get_height() * 0.89))

        start_idx = self.page * self.per_page
        for i, save in enumerate(self.saves[start_idx : start_idx + self.per_page]):
            rect = self._slot_rect(i)
            pygame.draw.rect(self.screen, COLORS["button"], rect, border_radius=12)
            pygame.draw.rect(self.screen, COLORS["accent"], rect, 2, border_radius=12)
            name_label = self.small.render(save["name"], True, COLORS["text"])
            self.screen.blit(name_label, (rect.x + 10, rect.y + 8))
            try:
                data = save_manager.load_machine(save["name"])
                self._draw_preview(data, rect)
            except Exception as e:
                print("Error drawing preview:", e)
            delete_rect = self._delete_rect(rect)
            hover = delete_rect.collidepoint(pygame.mouse.get_pos())
            color = (200, 80, 80) if hover else (150, 50, 50)
            pygame.draw.rect(self.screen, color, delete_rect, border_radius=6)
            pygame.draw.line(self.screen, (255, 255, 255),
                             (delete_rect.x + 5, delete_rect.y + 5),
                             (delete_rect.right - 5, delete_rect.bottom - 5), 2)
            pygame.draw.line(self.screen, (255, 255, 255),
                             (delete_rect.x + 5, delete_rect.bottom - 5),
                             (delete_rect.right - 5, delete_rect.y + 5), 2)

        if self.input_active:
            self._draw_input_box()

    def _grid_rect(self):
        w, h = self.screen.get_size()
        grid_width, grid_height = min(800, w * 0.9), min(400, h * 0.7)
        x = w/2 - grid_width/2
        y = h/2 - grid_height/2 + 30
        return pygame.Rect(x, y, grid_width, grid_height)

    def _slot_rect(self, i):
        grid = self._grid_rect()
        cols = 3
        padding = 20
        slot_w = (grid.width - padding * (cols + 1)) / cols
        slot_h = 150
        col = i % cols
        row = i // cols
        x = grid.x + padding + col * (slot_w + padding)
        y = grid.y + padding + row * (slot_h + padding)
        return pygame.Rect(x, y, slot_w, slot_h)

    def _draw_preview(self, data, rect):
        nodes = data.get("nodes", [])
        conns = data.get("connections", [])
        if not nodes:
            return
        xs = [n["x"] for n in nodes]
        ys = [n["y"] for n in nodes]
        minx, maxx = min(xs), max(xs)
        miny, maxy = min(ys), max(ys)
        w, h = (maxx - minx or 1), (maxy - miny or 1)
        scale = min((rect.width-40) / w, (rect.height-40) / h)
        cx, cy = rect.centerx, rect.centery + 15

        for c in conns:
            try:
                s = next(n for n in nodes if n["id"] == c["start"])
                e = next(n for n in nodes if n["id"] == c["end"])
            except StopIteration:
                continue
            sx = cx + (s["x"] - minx - w/2) * scale
            sy = cy + (s["y"] - miny - h/2) * scale
            ex = cx + (e["x"] - minx - w/2) * scale
            ey = cy + (e["y"] - miny - h/2) * scale
            pygame.draw.line(self.screen, (100, 150, 200), (sx, sy), (ex, ey), 2)

        for n in nodes:
            nx = cx + (n["x"] - minx - w/2) * scale
            ny = cy + (n["y"] - miny - h/2) * scale
            color = (90, 220, 120) if n["is_start"] else (220, 100, 100) if n["is_end"] else (200, 200, 200)
            pygame.draw.circle(self.screen, color, (int(nx), int(ny)), 5)

    def _draw_input_box(self):
        w, h = self.screen.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))

        box = pygame.Rect(w/2 - 180, h/2 - 30, 360, 60)
        pygame.draw.rect(self.screen, (40, 60, 100), box, border_radius=12)
        pygame.draw.rect(self.screen, COLORS["accent"], box, 2, border_radius=12)

        label = self.small.render("Enter save name:", True, COLORS["accent"])
        self.screen.blit(label, (box.x, box.y - 30))

        txt = self.small.render(self.input_text + "|", True, COLORS["text"])
        self.screen.blit(txt, (box.x + 10, box.y + 18))

    def _delete_rect(self, slot_rect):
        size = 22
        padding = 6
        return pygame.Rect(slot_rect.right - size - padding, slot_rect.y + padding, size, size)
