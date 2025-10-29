import pygame, random
import request_helper
from Button import Button, COLORS
from FontManager import FontManager
from AuthenticationPopup import AuthenticationPopup


class SettingsMenu:
    def __init__(self, screen, on_close):
        self.screen = screen
        self.on_close = on_close
        self.font_title = FontManager.get(64, bold=True)
        self.font_label = FontManager.get(30, bold=True)
        self.font_small = FontManager.get(22)
        self.font_medium = FontManager.get(26)

        self.symbols_left = [random.choice(['0', '1', '_']) for _ in range(6)]
        self.symbols_right = [random.choice(['0', '1', '_']) for _ in range(6)]
        self.symbol_change_timer = 0

        self.scroll_offset = 0
        self.scroll_speed = 40
        self.auth_popup = None

        token, user = request_helper.load_session()
        self.current_user = user if token else None

        self.btn_back = Button("Back", (0.04, 0.03, 0.12, 0.06), self.font_small, self._close)
        self.btn_login = Button("Login", (0.0, 0.0, 0.2, 0.06), self.font_small, self._open_login)
        self.btn_logout = Button("Logout", (0.0, 0.0, 0.2, 0.06), self.font_small, self._logout)

        self.sandbox_alphabet = ["0", "1", "_"]
        self.input_active = False
        self.input_text = ""

    def update(self, dt):
        self.symbol_change_timer += dt
        if self.symbol_change_timer > 1.5:
            self.symbols_left = [random.choice(['0', '1', '_']) for _ in range(6)]
            self.symbols_right = [random.choice(['0', '1', '_']) for _ in range(6)]
            self.symbol_change_timer = 0

    def handle_event(self, event):
        if self.auth_popup:
            self.auth_popup.handle_event(event)
            return

        self.btn_back.handle_event(event)
        (self.btn_logout if self.current_user else self.btn_login).handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            if hasattr(self, "symbol_rects"):
                for sym, rect in self.symbol_rects:
                    if rect.collidepoint(mouse_pos):
                        if sym in self.sandbox_alphabet and sym != "_":
                            self.sandbox_alphabet.remove(sym)
                            return

            if hasattr(self, "alphabet_input_rect") and self.alphabet_input_rect.collidepoint(mouse_pos):
                self.input_active = True
            else:
                self.input_active = False

        elif self.input_active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                symbol = self.input_text.strip()
                if len(symbol) == 1 and symbol not in self.sandbox_alphabet:
                    self.sandbox_alphabet.insert(len(self.sandbox_alphabet) - 1, symbol)
                self.input_text = ""
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = ""
            elif event.unicode.isprintable() and len(self.input_text) < 1:
                self.input_text = event.unicode
        elif event.type == pygame.KEYDOWN and not self.input_active:
            if event.key == pygame.K_ESCAPE:
                self._close()

    def draw(self):
        self.screen.fill((20, 22, 35))
        w, h = self.screen.get_size()

        for x in range(0, w, 40):
            pygame.draw.line(self.screen, (30, 34, 55), (x, 0), (x, h))
        for y in range(0, h, 40):
            pygame.draw.line(self.screen, (30, 34, 55), (0, y), (w, y))

        title_text = self.font_title.render("Settings", True, COLORS["accent"])
        title_rect = title_text.get_rect(center=(w / 2, h * 0.15))
        self.screen.blit(title_text, title_rect)

        self._draw_tape_effect(title_rect)

        panel_rect = pygame.Rect(int(w * 0.15), int(h * 0.25), int(w * 0.7), int(h * 0.6))
        pygame.draw.rect(self.screen, (35, 38, 60), panel_rect, border_radius=15)
        pygame.draw.rect(self.screen, COLORS["accent"], panel_rect, 2, border_radius=15)

        y_start = panel_rect.y + 30 + self.scroll_offset
        self._draw_profile_section(panel_rect, y_start)
        y_next = y_start + 160
        self._draw_sandbox_alphabet_section(panel_rect, y_next)

        self.btn_back.update_rect((w, h))
        self.btn_back.draw(self.screen)

        if self.auth_popup:
            self.auth_popup.draw()

    def _draw_profile_section(self, panel_rect, y):
        label = self.font_label.render("Profile", True, COLORS["accent"])
        self.screen.blit(label, (panel_rect.x + 30, y))
        pygame.draw.line(self.screen, COLORS["accent"], (panel_rect.x + 20, y + 40),
                         (panel_rect.right - 20, y + 40), 2)

        y_box = y + 60
        box_rect = pygame.Rect(panel_rect.x + 30, y_box, panel_rect.width - 60, 60)
        pygame.draw.rect(self.screen, (45, 48, 75), box_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLORS["accent"], box_rect, 2, border_radius=10)

        if self.current_user:
            username = self.current_user.get("username", "Unknown")
            text = self.font_medium.render(username, True, COLORS["text"])
            self.screen.blit(text, (box_rect.x + 20, box_rect.y + 15))

            btn_w, btn_h = 120, 36
            btn_x = box_rect.right - btn_w - 15
            btn_y = box_rect.y + (box_rect.height - btn_h) / 2
            self.btn_logout.rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
            self.btn_logout.draw(self.screen)
        else:
            text = self.font_medium.render("Not logged in", True, COLORS["text"])
            self.screen.blit(text, (box_rect.x + 20, box_rect.y + 15))
            btn_w, btn_h = 120, 36
            btn_x = box_rect.right - btn_w - 15
            btn_y = box_rect.y + (box_rect.height - btn_h) / 2
            self.btn_login.rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
            self.btn_login.draw(self.screen)

    def _draw_sandbox_alphabet_section(self, panel_rect, y):
        label = self.font_label.render("Sandbox Alphabet", True, COLORS["accent"])
        self.screen.blit(label, (panel_rect.x + 30, y))
        pygame.draw.line(self.screen, COLORS["accent"], (panel_rect.x + 20, y + 40),
                         (panel_rect.right - 20, y + 40), 2)

        y_box = y + 60
        start_x = panel_rect.x + 40
        current_x = start_x
        row_y = y_box
        spacing = 10
        box_h = 45

        self.symbol_rects = []

        for sym in self.sandbox_alphabet:
            box_w = 60
            rect = pygame.Rect(current_x, row_y, box_w, box_h)
            pygame.draw.rect(self.screen, (45, 48, 75), rect, border_radius=10)
            pygame.draw.rect(self.screen, COLORS["accent"], rect, 2, border_radius=10)

            text_surf = self.font_medium.render(sym, True, COLORS["text"])
            self.screen.blit(text_surf, text_surf.get_rect(center=rect.center))

            if sym != "_":
                x_rect = pygame.Rect(rect.right - 18, rect.y + 4, 14, 14)
                pygame.draw.rect(self.screen, (200, 70, 70), x_rect, border_radius=4)
                pygame.draw.line(self.screen, (255, 255, 255), x_rect.topleft, x_rect.bottomright, 2)
                pygame.draw.line(self.screen, (255, 255, 255), x_rect.topright, x_rect.bottomleft, 2)
                self.symbol_rects.append((sym, x_rect))

            current_x += box_w + spacing
            if current_x + box_w > panel_rect.right - 80:
                current_x = start_x
                row_y += box_h + spacing

        input_y = row_y + box_h + 20
        input_rect = pygame.Rect(start_x, input_y, 120, 50)

        bg_color = (65, 68, 95) if not self.input_active else (75, 80, 110)
        border_color = COLORS["accent"] if not self.input_active else (120, 180, 255)

        pygame.draw.rect(self.screen, bg_color, input_rect, border_radius=10)
        pygame.draw.rect(self.screen, border_color, input_rect, 3, border_radius=10)

        placeholder = "Type a symbol"
        text = self.input_text or placeholder
        color = COLORS["text"] if self.input_text else (150, 150, 160)
        text_surf = self.font_small.render(text, True, color)
        self.screen.blit(text_surf, (input_rect.x + 10, input_rect.y + 12))

        self.alphabet_input_rect = input_rect

    def _draw_tape_effect(self, title_rect):
        w = self.screen.get_width()
        tape_font = pygame.font.SysFont("consolas", 26, bold=True)
        cell_w, cell_h, pad = 30, 36, 8
        x_start_left = title_rect.left - (len(self.symbols_left) * (cell_w + pad)) - 40
        y_top = title_rect.centery - cell_h / 2
        for i, sym in enumerate(self.symbols_left):
            rect = pygame.Rect(x_start_left + i * (cell_w + pad), y_top, cell_w, cell_h)
            pygame.draw.rect(self.screen, (50, 70, 110), rect, border_radius=6)
            pygame.draw.rect(self.screen, COLORS["accent"], rect, 2, border_radius=6)
            self.screen.blit(tape_font.render(sym, True, COLORS["text"]),
                             text_rect := tape_font.render(sym, True, COLORS["text"]).get_rect(center=rect.center))

        x_start_right = title_rect.right + 40
        for i, sym in enumerate(self.symbols_right):
            rect = pygame.Rect(x_start_right + i * (cell_w + pad), y_top, cell_w, cell_h)
            pygame.draw.rect(self.screen, (50, 70, 110), rect, border_radius=6)
            pygame.draw.rect(self.screen, COLORS["accent"], rect, 2, border_radius=6)
            self.screen.blit(tape_font.render(sym, True, COLORS["text"]),
                             tape_font.render(sym, True, COLORS["text"]).get_rect(center=rect.center))

    def _open_login(self):
        self.auth_popup = AuthenticationPopup(self.screen, self._on_authenticated)

    def _on_authenticated(self, user):
        if user:
            self.current_user = user
        self.auth_popup = None

    def _logout(self):
        request_helper.clear_session()
        self.current_user = None

    def _close(self):
        self.on_close()