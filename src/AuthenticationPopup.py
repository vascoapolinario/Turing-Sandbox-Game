import pygame
import time
from Button import Button, COLORS
from FontManager import FontManager
import request_helper


class AuthenticationPopup:
    def __init__(self, screen, on_authenticated):
        self.screen = screen
        self.on_authenticated = on_authenticated
        self.last_box = None

        self.font_title = FontManager.get(40, bold=True)
        self.font_label = FontManager.get(26)
        self.font_input = FontManager.get(28)
        self.font_button = FontManager.get(30, bold=True)
        self.font_small = FontManager.get(20)

        self.username = ""
        self.password = ""
        self.active_field = None
        self.error_message = ""
        self.success_message = ""
        self.cursor_visible = True
        self.last_cursor_blink = time.time()
        self.loading = False
        self.show_password = False

        self.btn_login = Button("Login", (0.28, 0.68, 0.22, 0.07), self.font_button, self._login)
        self.btn_register = Button("Register", (0.52, 0.68, 0.22, 0.07), self.font_button, self._register)
        self.btn_close = Button("X", (0.69, 0.25, 0.05, 0.05), self.font_button, self._close)

        try:
            token, user = request_helper.load_session()
            if token and user:
                print(f"Session verified for {user['username']}")
                self.on_authenticated(user)
        except Exception as e:
            print("Auto-login failed:", e)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                self.active_field = "password" if self.active_field == "username" else "username"
            elif self.active_field == "username":
                if event.key == pygame.K_BACKSPACE:
                    self.username = self.username[:-1]
                elif event.unicode.isprintable():
                    if len(self.username) < 30:
                        self.username += event.unicode
            elif self.active_field == "password":
                if event.key == pygame.K_BACKSPACE:
                    self.password = self.password[:-1]
                elif event.unicode.isprintable():
                    if len(self.password) < 30:
                        self.password += event.unicode

        elif event.type == pygame.MOUSEBUTTONDOWN:
            box = self.last_box or pygame.Rect(0, 0, 0, 0)
            if self._username_rect(box).collidepoint(event.pos):
                self.active_field = "username"
            elif self._password_rect(box).collidepoint(event.pos):
                self.active_field = "password"
            elif self._see_pw_box_rect(box).collidepoint(event.pos):
                self.show_password = not self.show_password
            else:
                self.active_field = None

        for b in [self.btn_login, self.btn_register, self.btn_close]:
            b.handle_event(event)

    def draw(self):
        w, h = self.screen.get_size()

        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        box_width, box_height = w * 0.5, h * 0.52
        box_x, box_y = (w - box_width) / 2, (h - box_height) / 2
        box = pygame.Rect(box_x, box_y, box_width, box_height)
        self.last_box = box


        shadow = pygame.Surface((box.width + 10, box.height + 10), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 120), shadow.get_rect(), border_radius=15)
        self.screen.blit(shadow, (box.x - 5, box.y - 5))

        pygame.draw.rect(self.screen, (30, 34, 55), box, border_radius=15)
        pygame.draw.rect(self.screen, COLORS["accent"], box, 2, border_radius=15)

        title = self.font_title.render("Login or Register", True, COLORS["accent"])
        self.screen.blit(title, (box.centerx - title.get_width() // 2, box_y + 25))

        self._draw_label("Username", box_x + 50, box_y + 95)
        self._draw_input(self._username_rect(box), self.username, self.active_field == "username")

        self._draw_label("Password", box_x + 50, box_y + 180)
        display_pw = self.password if self.show_password else "*" * len(self.password)
        self._draw_input(self._password_rect(box), display_pw, self.active_field == "password")

        check_rect = self._see_pw_box_rect(box)
        label_surf = self.font_small.render("See password", True, (190, 190, 210))
        self.screen.blit(label_surf, (check_rect.right + 10, check_rect.y - 2))

        pygame.draw.rect(self.screen, (90, 95, 120), check_rect, 2, border_radius=4)
        if self.show_password:
            pygame.draw.line(self.screen, COLORS["accent"], (check_rect.x + 5, check_rect.y + 5),
                             (check_rect.right - 5, check_rect.bottom - 5), 3)
            pygame.draw.line(self.screen, COLORS["accent"], (check_rect.right - 5, check_rect.y + 5),
                             (check_rect.x + 5, check_rect.bottom - 5), 3)

        for btn in [self.btn_login, self.btn_register, self.btn_close]:
            btn.update_rect((w, h))
            btn.draw(self.screen)

        msg_y = box.bottom - 45
        if self.loading:
            load_text = self.font_label.render("Loading...", True, (200, 200, 200))
            self.screen.blit(load_text, (box.centerx - load_text.get_width() // 2, msg_y))
        elif self.error_message:
            err = self.font_label.render(self.error_message, True, (220, 90, 90))
            self.screen.blit(err, (box.centerx - err.get_width() // 2, msg_y))
        elif self.success_message:
            succ = self.font_label.render(self.success_message, True, (100, 220, 120))
            self.screen.blit(succ, (box.centerx - succ.get_width() // 2, msg_y))

    def _username_rect(self, box=None):
        if box is None:
            w, h = self.screen.get_size()
            box = pygame.Rect(w * 0.25, h * 0.25, w * 0.50, h * 0.50)
        return pygame.Rect(box.x + 180, box.y + 85, box.width - 260, 45)

    def _password_rect(self, box=None):
        if box is None:
            w, h = self.screen.get_size()
            box = pygame.Rect(w * 0.25, h * 0.25, w * 0.50, h * 0.50)
        return pygame.Rect(box.x + 180, box.y + 170, box.width - 300, 45)

    def _see_pw_box_rect(self, box=None):
        if box is None:
            w, h = self.screen.get_size()
            box = pygame.Rect(w * 0.25, h * 0.25, w * 0.50, h * 0.50)
        return pygame.Rect(box.x + 180, box.y + 230, 24, 24)

    def _draw_label(self, text, x, y):
        surf = self.font_label.render(text, True, (190, 190, 210))
        self.screen.blit(surf, (x, y))

    def _draw_input(self, rect, text, active):
        now = time.time()
        if now - self.last_cursor_blink > 0.5:
            self.cursor_visible = not self.cursor_visible
            self.last_cursor_blink = now

        color_bg = (40, 45, 70)
        border_color = COLORS["accent"] if active else (90, 95, 120)
        glow_rect = pygame.Rect(rect.x - 2, rect.y - 2, rect.width + 4, rect.height + 4)
        if active:
            pygame.draw.rect(self.screen, (80, 90, 130), glow_rect, border_radius=8)
        pygame.draw.rect(self.screen, color_bg, rect, border_radius=6)
        pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=6)

        txt = self.font_input.render(text, True, COLORS["text"])
        self.screen.blit(txt, (rect.x + 12, rect.y + (rect.height - txt.get_height()) // 2))

        if active and self.cursor_visible:
            cursor_x = rect.x + 12 + self.font_input.size(text)[0] + 2
            cursor_y = rect.y + 6
            pygame.draw.line(self.screen, COLORS["accent"], (cursor_x, cursor_y),
                             (cursor_x, cursor_y + rect.height - 12), 2)

    def _login(self):
        self._authenticate(is_register=False)

    def _register(self):
        self._authenticate(is_register=True)

    def _authenticate(self, is_register: bool):
        self.error_message = ""
        self.success_message = ""
        if not self.username.strip() or not self.password.strip():
            self.error_message = "Please enter both username and password."
            return

        self.loading = True
        pygame.display.flip()
        try:
            if is_register:
                data = request_helper.register_user(self.username, self.password)
                if data:
                    self.success_message = f"User '{self.username}' registered successfully!"
                else:
                    self.error_message = "Registration failed."
            else:
                token, user = request_helper.login_user(self.username, self.password)
                if token and user:
                    self.success_message = f"Welcome back, {user.get('username', self.username)}!"
                    self.on_authenticated(user)
                else:
                    self.error_message = "Invalid username or password."
        except Exception as e:
            self.error_message = f"Network error: {e}"
        finally:
            self.loading = False

    def _close(self):
        self.on_authenticated(None)
