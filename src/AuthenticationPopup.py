import pygame
import requests
import json
import os
import time
from Button import Button, COLORS
from FontManager import FontManager
import auth_manager

API_URL = "https://localhost:7054/players"
VERIFY_SSL = False


class AuthenticationPopup:
    def __init__(self, screen, on_authenticated):
        self.screen = screen
        self.on_authenticated = on_authenticated

        self.font_title = FontManager.get(40, bold=True)
        self.font_label = FontManager.get(30)
        self.font_input = FontManager.get(30)
        self.font_button = FontManager.get(30, bold=True)

        self.username = ""
        self.password = ""
        self.active_field = None
        self.error_message = ""
        self.success_message = ""
        self.cursor_visible = True
        self.last_cursor_blink = time.time()

        self.btn_login = Button("Login", (0.28, 0.63, 0.22, 0.07), self.font_button, self._login)
        self.btn_register = Button("Register", (0.52, 0.63, 0.22, 0.07), self.font_button, self._register)
        self.btn_close = Button("X", (0.69, 0.29, 0.05, 0.05), self.font_button, self._close)

        try:
            token, user = auth_manager.load_session()
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
                    self.username += event.unicode
            elif self.active_field == "password":
                if event.key == pygame.K_BACKSPACE:
                    self.password = self.password[:-1]
                elif event.unicode.isprintable():
                    self.password += event.unicode

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self._username_rect().collidepoint(event.pos):
                self.active_field = "username"
            elif self._password_rect().collidepoint(event.pos):
                self.active_field = "password"
            else:
                self.active_field = None

        self.btn_login.handle_event(event)
        self.btn_register.handle_event(event)
        self.btn_close.handle_event(event)

    def draw(self):
        w, h = self.screen.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        box_width, box_height = w * 0.5, h * 0.45
        box_x, box_y = (w - box_width) / 2, (h - box_height) / 2
        box = pygame.Rect(box_x, box_y, box_width, box_height)

        pygame.draw.rect(self.screen, (30, 34, 55), box, border_radius=12)
        pygame.draw.rect(self.screen, COLORS["accent"], box, 2, border_radius=12)

        title = self.font_title.render("Login or Register", True, COLORS["accent"])
        self.screen.blit(title, (box.centerx - title.get_width() // 2, box_y + 20))

        self._draw_label("Username", box_x + 50, box_y + 90)
        self._draw_input(self._username_rect(box), self.username, self.active_field == "username")

        self._draw_label("Password", box_x + 50, box_y + 170)
        self._draw_input(self._password_rect(box), "*" * len(self.password), self.active_field == "password")

        self.btn_login.update_rect((w, h))
        self.btn_register.update_rect((w, h))
        self.btn_close.update_rect((w, h))
        self.btn_login.draw(self.screen)
        self.btn_register.draw(self.screen)
        self.btn_close.draw(self.screen)

        if self.error_message:
            err = self.font_label.render(self.error_message, True, (220, 90, 90))
            self.screen.blit(err, (box.centerx - err.get_width() // 2, box.bottom  - box.top / 2))
        elif self.success_message:
            succ = self.font_label.render(self.success_message, True, (100, 220, 120))
            self.screen.blit(succ, (box.centerx - succ.get_width() // 2, box.bottom - 50))

    def _username_rect(self, box=None):
        if box is None:
            w, h = self.screen.get_size()
            box = pygame.Rect(w * 0.25, h * 0.25, w * 0.50, h * 0.50)
        return pygame.Rect(box.x + 180, box.y + 80, box.width - 230, 40)

    def _password_rect(self, box=None):
        if box is None:
            w, h = self.screen.get_size()
            box = pygame.Rect(w * 0.25, h * 0.25, w * 0.50, h * 0.50)
        return pygame.Rect(box.x + 180, box.y + 160, box.width - 230, 40)

    def _draw_label(self, text, x, y):
        surf = self.font_label.render(text, True, (180, 180, 200))
        self.screen.blit(surf, (x, y))

    def _draw_input(self, rect, text, active):
        now = time.time()
        if now - self.last_cursor_blink > 0.5:
            self.cursor_visible = not self.cursor_visible
            self.last_cursor_blink = now

        color_border = COLORS["accent"] if active else (80, 85, 110)
        pygame.draw.rect(self.screen, (40, 45, 70), rect, border_radius=6)
        pygame.draw.rect(self.screen, color_border, rect, 2, border_radius=6)

        txt = self.font_input.render(text, True, COLORS["text"])
        self.screen.blit(txt, (rect.x + 10, rect.y + (rect.height - txt.get_height()) // 2))

        if active and self.cursor_visible:
            cursor_x = rect.x + 10 + self.font_input.size(text)[0] + 2
            cursor_y = rect.y + 5
            pygame.draw.line(self.screen, COLORS["accent"], (cursor_x, cursor_y), (cursor_x, cursor_y + rect.height - 10), 2)

    def _login(self):
        self._send_request(is_register=False)

    def _register(self):
        self._send_request(is_register=True)

    def _send_request(self, is_register=False):
        self.error_message = ""
        self.success_message = ""

        if not self.username.strip() or not self.password.strip():
            self.error_message = "Please enter both username and password."
            return

        try:
            if is_register:
                r = requests.post(API_URL, json={"username": self.username, "password": self.password},
                                  verify=VERIFY_SSL)
                if r.status_code == 201:
                    self.success_message = "Account created! You can log in now."
                elif r.status_code == 409:
                    self.error_message = "Username already exists."
                else:
                    self.error_message = f"Registration failed ({r.status_code})."
            else:
                login_url = f"{API_URL}/login"
                r = requests.post(login_url, json={"username": self.username, "password": self.password},
                                  verify=VERIFY_SSL)

                if r.status_code == 200:
                    data = r.json()
                    token = data.get("token")
                    user = data.get("user", {})

                    auth_manager.save_session(token, user)

                    self.success_message = f"Welcome back, {user.get('username', self.username)}!"
                    self.on_authenticated(user)
                elif r.status_code == 401:
                    self.error_message = "Invalid username or password."
                else:
                    self.error_message = f"Login failed ({r.status_code})."

        except Exception as e:
            self.error_message = f"Network error: {e}"

    def _close(self):
        self.on_authenticated(None)