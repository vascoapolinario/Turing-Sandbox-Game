import pygame
from Button import Button, COLORS
from FontManager import FontManager
import request_helper
from datetime import datetime, timezone


def time_since_utc(utc_str):
    try:
        utc_time = datetime.fromisoformat(utc_str.replace("Z", "+00:00")).astimezone(timezone.utc)
        local_time = utc_time.astimezone()
        now = datetime.now().astimezone()

        diff = now - local_time
        seconds = int(diff.total_seconds())

        if seconds < 60:
            return f"{seconds}s ago"
        elif seconds < 3600:
            mins = seconds // 60
            return f"{mins}m ago"
        elif seconds < 86400:
            hours = seconds // 3600
            return f"{hours}h ago"
        else:
            days = seconds // 86400
            return f"{days}d ago"
    except Exception:
        return "?"

class MultiplayerMenu:
    def __init__(self, screen, on_close):
        self.screen = screen
        self.on_close = on_close
        self.font_title = FontManager.get(64, bold=True)
        self.font_small = FontManager.get(24)
        self.font_medium = FontManager.get(28, bold=True)

        self.btn_back = Button("Back", (0.04, 0.03, 0.12, 0.06), self.font_small, self._close)
        self.btn_host = Button("Host Lobby", (0.15, 0.55, 0.25, 0.08), self.font_medium, self._host)

        self.scroll_offset = 0
        self.scroll_speed = 40
        self.lobby_scroll = 0
        self.level_scroll = 0
        self.lobbies = []

        request_helper.connect_signalr(
            on_lobby_created=self._on_lobby_created,
            on_player_joined=self._on_player_joined,
            on_player_left=self._on_player_left,
            on_lobby_deleted=self._on_lobby_deleted
        )
        self.join_buttons = []
        self.current_lobby = None
        self.refresh_lobbies()

        self.show_password_popup = False
        self.password_input = ""
        self.password_cursor_visible = True
        self.password_timer = 0
        self.password_target_code = None

        self.require_password = False
        self.host_password = ""
        self.password_focused = False
        self.show_level_popup = False
        self.selected_level = None
        self.level_search = ""
        self.level_results = []
        self.level_cursor_visible = True
        self.level_timer = 0
        self.btn_level_cancel = Button("Cancel", (0.25, 0.73, 0.15, 0.07),
                                       self.font_small, self._cancel_level_popup)
        self.btn_level_ok = Button("OK", (0.60, 0.73, 0.15, 0.07),
                                   self.font_small, self._confirm_level_popup)
        self.selected_temp_level = None
        self.message_text = ""
        self.message_time = 0
        self.message_duration = 3000

    def refresh_lobbies(self):
        self.lobbies = request_helper.get_lobbies() or []
        self._build_join_buttons()

    def _build_join_buttons(self):
        self.join_buttons.clear()
        for i, lobby in enumerate(self.lobbies):
            code = lobby.get("code", "???")
            btn = Button("Join", (0.0, 0.0, 0.2, 0.05),
                         self.font_small, lambda c=code: self._join_lobby(c))
            self.join_buttons.append(btn)

    def update(self, dt):
        pass

    def draw(self):
        self.screen.fill((20, 22, 35))
        w, h = self.screen.get_size()

        self.font_title = FontManager.get(int(64 * (h / 1080)), bold=True)
        self.font_small = FontManager.get(int(24 * (h / 1080)))
        self.font_medium = FontManager.get(int(28 * (h / 1080)), bold=True)

        title = self.font_title.render("Multiplayer", True, COLORS["accent"])
        self.screen.blit(title, title.get_rect(center=(w / 2, h * 0.1)))

        if self.current_lobby:
            self._draw_lobby_view(w, h)
        else:
            self._draw_host_form(w, h)
            self.btn_host.draw(self.screen)
            self._draw_lobby_list(w, h)

        self.btn_back.draw(self.screen)
        if self.show_password_popup:
            self._draw_password_popup(w, h)
        if self.show_level_popup:
            self._draw_level_popup(w, h)

        now = pygame.time.get_ticks()
        if self.message_text and now - self.message_time < self.message_duration:
            msg_surf = self.font_small.render(self.message_text, True, COLORS["accent"])
            msg_bg = msg_surf.get_rect(center=(w / 2, h * 0.95))
            bg_rect = pygame.Rect(msg_bg.x - 15, msg_bg.y - 8, msg_bg.width + 30, msg_bg.height + 16)
            pygame.draw.rect(self.screen, (25, 27, 45), bg_rect, border_radius=8)
            pygame.draw.rect(self.screen, COLORS["accent"], bg_rect, 2, border_radius=8)
            self.screen.blit(msg_surf, msg_surf.get_rect(center=bg_rect.center))

    def _draw_lobby_list(self, w, h):
        panel_rect = pygame.Rect(int(w * 0.55), int(h * 0.2),
                                 int(w * 0.38), int(h * 0.7))
        pygame.draw.rect(self.screen, (35, 38, 60), panel_rect, border_radius=15)
        pygame.draw.rect(self.screen, COLORS["accent"], panel_rect, 2, border_radius=15)

        y_start = panel_rect.y + int(h * 0.02)
        item_h = int(h * 0.065)

        max_visible = 8
        start = self.lobby_scroll
        end = min(start + max_visible, len(self.lobbies))

        for i, lobby in enumerate(self.lobbies[start:end], start=start):
            idx = i - start
            lobby_rect = pygame.Rect(
                panel_rect.x + int(w * 0.005),
                y_start + idx * (item_h + int(h * 0.01)),
                panel_rect.width - int(w * 0.01),
                item_h
            )

            code = lobby.get("code", "???")
            host = lobby.get("hostPlayer", "Unknown")
            level = lobby.get("levelName", "Unknown Level")
            created = time_since_utc(lobby.get("createdAt", ""))
            count = len(lobby.get("lobbyPlayers", []))

            PasswordProtected = lobby.get("passwordProtected", False)
            if PasswordProtected:
                created += " [Requires Password]"



            self.screen.blit(self.font_small.render(f"Code: {code} | Host: {host}",
                                                    True, COLORS["text"]),
                             (lobby_rect.x + 15, lobby_rect.y + 5))
            self.screen.blit(self.font_small.render(f"Level: {level}", True, COLORS["text"]),
                             (lobby_rect.x + 15, lobby_rect.y + 30))
            self.screen.blit(self.font_small.render(f"Created: {created}", True, COLORS["text"]),
                             (lobby_rect.x + w * 0.15, lobby_rect.y + 5))
            self.screen.blit(self.font_small.render(f"Players: {count}/4", True, COLORS["text"]),
                             (lobby_rect.x + w * 0.15, lobby_rect.y + 30))

            btn = self.join_buttons[i]
            btn.rect = pygame.Rect(lobby_rect.right - int(w * 0.07),
                                   lobby_rect.y + int(h * 0.015),
                                   int(w * 0.05), int(h * 0.045))
            btn.draw(self.screen)
        if len(self.lobbies) == 0:
            no_lobbies_text = self.font_medium.render("No lobbies available.", True, COLORS["text"])
            self.screen.blit(no_lobbies_text, no_lobbies_text.get_rect(center=panel_rect.center))

    def _draw_lobby_view(self, w, h):
        lobby = self.current_lobby
        if not lobby:
            return

        info_rect = pygame.Rect(int(w * 0.55), int(h * 0.2),
                                int(w * 0.38), int(h * 0.25))
        pygame.draw.rect(self.screen, (35, 38, 60), info_rect, border_radius=15)
        pygame.draw.rect(self.screen, COLORS["accent"], info_rect, 2, border_radius=15)

        code = lobby.get("code", "???")
        level = lobby.get("levelName", "Unknown Level")
        created = time_since_utc(lobby.get("createdAt", ""))

        lines = [f"Code: {code}", f"Level: {level}", f"Created: {created}"]
        for i, line in enumerate(lines):
            surf = self.font_small.render(line, True, COLORS["text"])
            self.screen.blit(surf, (info_rect.x + 20,
                                    info_rect.y + 20 + i * 35))

        players_rect = pygame.Rect(int(w * 0.55), int(h * 0.5),
                                   int(w * 0.38), int(h * 0.4))
        pygame.draw.rect(self.screen, (35, 38, 60), players_rect, border_radius=15)
        pygame.draw.rect(self.screen, COLORS["accent"], players_rect, 2, border_radius=15)

        host = lobby.get("hostPlayer", "Unknown")
        players = lobby.get("lobbyPlayers", [])
        y0 = players_rect.y + 40
        self.screen.blit(self.font_medium.render("Players", True, COLORS["accent"]),
                         (players_rect.x + 20, players_rect.y + 10))
        for i, p in enumerate(players):
            if isinstance(p, dict):
                name = p.get("username", str(p))
            else:
                name = str(p)
            tag = "[HOST] " if name == host else ""
            self.screen.blit(self.font_small.render(f"{tag}{name}", True, COLORS["text"]),
                             (players_rect.x + 25, y0 + i * 30))

        if hasattr(self, "btn_leave"):
            self.btn_leave.draw(self.screen)

    def _draw_host_form(self, w, h):
        toggle_size = int(h * 0.04)
        toggle_rect = pygame.Rect(int(w * 0.15), int(h * 0.25), toggle_size, toggle_size)

        pygame.draw.rect(self.screen, (80, 80, 110), toggle_rect, border_radius=4)
        pygame.draw.rect(self.screen, COLORS["accent"], toggle_rect, 2, border_radius=4)

        label_surface = self.font_small.render("Password Protection", True, COLORS["text"])
        self.screen.blit(label_surface, (toggle_rect.right + 12, toggle_rect.y + 5))

        if self.require_password:
            pad = int(toggle_size * 0.2)
            pygame.draw.line(self.screen, COLORS["accent"],
                             (toggle_rect.x + pad, toggle_rect.y + pad),
                             (toggle_rect.right - pad, toggle_rect.bottom - pad), 3)
            pygame.draw.line(self.screen, COLORS["accent"],
                             (toggle_rect.right - pad, toggle_rect.y + pad),
                             (toggle_rect.x + pad, toggle_rect.bottom - pad), 3)
            pw_rect = pygame.Rect(toggle_rect.right + int(w * 0.1),
                                  toggle_rect.y - 2,
                                  int(w * 0.18), int(h * 0.05))
            pygame.draw.rect(self.screen, (45, 48, 75), pw_rect, border_radius=8)
            pygame.draw.rect(self.screen, COLORS["accent"], pw_rect, 2, border_radius=8)

            now = pygame.time.get_ticks()
            if now - self.password_timer > 500:
                self.password_cursor_visible = not self.password_cursor_visible
                self.password_timer = now

            masked = "*" * len(self.host_password)
            if self.password_focused and self.password_cursor_visible:
                masked += "|"
            elif not self.host_password and not self.password_focused:
                masked = "Click to type..."

            txt = self.font_small.render(masked, True, COLORS["text"])
            self.screen.blit(txt, (pw_rect.x + 10, pw_rect.y + 10))

            self.password_rect = pw_rect
        else:
            self.password_rect = None

        lvl_rect = pygame.Rect(int(w * 0.15), int(h * 0.35), int(w * 0.06), int(h * 0.04))
        pygame.draw.rect(self.screen, (45, 48, 75), lvl_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLORS["accent"], lvl_rect, 2, border_radius=8)
        txt = self.font_small.render("Select Level", True, COLORS["text"])
        self.screen.blit(txt, (lvl_rect.x + 10, lvl_rect.y + 10))

        name = self.selected_level["name"] if self.selected_level else "None"
        label = self.font_small.render(f"Current Level: {name}", True, COLORS["text"])
        self.screen.blit(label, (lvl_rect.right + 20, lvl_rect.y + 15))

        pw_valid = (not self.require_password) or (1 <= len(self.host_password) <= 30)
        self.btn_host.disabled = not (self.selected_level and pw_valid)

    def _draw_password_popup(self, w, h):
        box_w, box_h = int(w * 0.4), int(h * 0.25)
        box_x, box_y = (w - box_w) // 2, (h - box_h) // 2
        rect = pygame.Rect(box_x, box_y, box_w, box_h)

        pygame.draw.rect(self.screen, (30, 32, 50), rect, border_radius=12)
        pygame.draw.rect(self.screen, COLORS["accent"], rect, 3, border_radius=12)

        title = self.font_medium.render("Enter Password", True, COLORS["accent"])
        self.screen.blit(title, (rect.centerx - title.get_width() // 2, rect.y + 25))

        input_rect = pygame.Rect(rect.x + 40, rect.y + 90, rect.width - 80, 50)
        pygame.draw.rect(self.screen, (45, 48, 75), input_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLORS["accent"], input_rect, 2, border_radius=8)

        now = pygame.time.get_ticks()
        if now - self.password_timer > 500:
            self.password_cursor_visible = not self.password_cursor_visible
            self.password_timer = now

        display_text = "*" * len(self.password_input)
        if self.password_cursor_visible:
            display_text += "|"

        text_surf = self.font_small.render(display_text, True, COLORS["text"])
        self.screen.blit(text_surf, (input_rect.x + 10, input_rect.y + 10))

        hint = self.font_small.render("Press Enter to confirm, Esc to cancel", True, COLORS["text"])
        self.screen.blit(hint, (rect.centerx - hint.get_width() // 2, rect.bottom - 35))

    def _draw_level_popup(self, w, h):
        box = pygame.Rect(int(w * 0.2), int(h * 0.15), int(w * 0.6), int(h * 0.7))
        pygame.draw.rect(self.screen, (25, 27, 40), box, border_radius=12)
        pygame.draw.rect(self.screen, COLORS["accent"], box, 3, border_radius=12)

        title = self.font_medium.render("Select a Level", True, COLORS["accent"])
        self.screen.blit(title, (box.centerx - title.get_width() // 2, box.y + 20))

        y_start = box.y + 80
        item_height = 45
        max_visible = 10
        start = self.level_scroll
        end = min(start + max_visible, len(self.level_results))

        for i, lvl in enumerate(self.level_results[start:end], start=start):
            rect = pygame.Rect(box.x + 20, y_start + (i - start) * (item_height + 10),
                               box.width - 40, item_height)

            color = (60, 65, 100)
            if self.selected_temp_level == lvl:
                base = COLORS["accent"]
                color = tuple(min(int(c * 1.2), 255) for c in base)
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            pygame.draw.rect(self.screen, COLORS["accent"], rect, 2, border_radius=8)

            name = lvl.get("name", "Unnamed")
            author = lvl.get("author", "?")
            txt = self.font_small.render(f"{name}  ({author})", True, COLORS["text"])
            self.screen.blit(txt, (rect.x + 10, rect.y + 10))

        btn_w, btn_h = int(w * 0.15), int(h * 0.07)
        btn_y = box.bottom - int(h * 0.12)

        self.btn_level_cancel.rect = pygame.Rect(int(w * 0.28), btn_y, btn_w, btn_h)
        self.btn_level_ok.rect = pygame.Rect(int(w * 0.57), btn_y, btn_w, btn_h)
        self.btn_level_cancel.draw(self.screen)
        self.btn_level_ok.draw(self.screen)


    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL and not self.show_level_popup:
            if event.y < 0 and self.lobby_scroll < max(0, len(self.lobbies) - 8):
                self.lobby_scroll += 1
            elif event.y > 0 and self.lobby_scroll > 0:
                self.lobby_scroll -= 1
        if self.show_password_popup:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if request_helper.join_lobby(self.password_target_code, self.password_input):
                        self.current_lobby = next(
                            (l for l in self.lobbies if l.get("code") == self.password_target_code), None)
                        self.btn_leave = Button("Leave Lobby", (0.15, 0.85, 0.25, 0.07),
                                                self.font_medium, self._leave_lobby)
                    else:
                        self._show_message("Incorrect password or failed join.")
                    self.show_password_popup = False
                elif event.key == pygame.K_ESCAPE:
                    self.show_password_popup = False
                elif event.key == pygame.K_BACKSPACE:
                    self.password_input = self.password_input[:-1]
                else:
                    ch = event.unicode
                    if len(ch) == 1 and ch.isprintable():
                        self.password_input += ch
        if self.show_level_popup:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._cancel_level_popup()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                w, h = self.screen.get_size()
                box = pygame.Rect(int(w * 0.2), int(h * 0.15), int(w * 0.6), int(h * 0.7))
                y_start = box.y + 80
                item_height = 45
                max_visible = 10
                start = self.level_scroll
                end = min(start + max_visible, len(self.level_results))

                for i, lvl in enumerate(self.level_results[start:end], start=start):
                    rect = pygame.Rect(box.x + 20, y_start + (i - start) * (item_height + 10),
                                       box.width - 40, item_height)
                    if rect.collidepoint(mx, my):
                        self.selected_temp_level = lvl
                        break

                self.btn_level_cancel.handle_event(event)
                self.btn_level_ok.handle_event(event)

            elif event.type == pygame.MOUSEWHEEL:
                if event.y < 0 and self.level_scroll < max(0, len(self.level_results) - 10):
                    self.level_scroll += 1
                elif event.y > 0 and self.level_scroll > 0:
                    self.level_scroll -= 1
            self.btn_level_cancel.handle_event(event)
            self.btn_level_ok.handle_event(event)
        self.btn_back.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            toggle_rect = pygame.Rect(int(self.screen.get_width() * 0.15), int(self.screen.get_height() * 0.25),
                                      int(self.screen.get_width() * 0.05), int(self.screen.get_height() * 0.05))
            if toggle_rect.collidepoint(mx, my):
                self.require_password = not self.require_password
                self.host_password = ""
                self.password_focused = False
            elif self.require_password and self.password_rect and self.password_rect.collidepoint(mx, my):
                self.password_focused = True
            else:
                self.password_focused = False
            lvl_rect = pygame.Rect(int(self.screen.get_width() * 0.15), int(self.screen.get_height() * 0.35),
                                   int(self.screen.get_width() * 0.25), int(self.screen.get_height() * 0.06))
            if lvl_rect.collidepoint(mx, my):
                self.show_level_popup = True
                self._load_levels()
        if self.require_password and self.password_focused and event.type == pygame.KEYDOWN and not self.show_password_popup:
            if event.key == pygame.K_BACKSPACE:
                self.host_password = self.host_password[:-1]
            else:
                ch = event.unicode
                if len(ch) == 1 and ch.isprintable() and len(self.host_password) < 30:
                    self.host_password += ch
        self.btn_host.handle_event(event)
        for button in self.join_buttons:
            button.handle_event(event)
        if event.type == pygame.KEYDOWN and not self.show_level_popup and not self.show_password_popup:
            if event.key == pygame.K_ESCAPE:
                self._close()
        if self.current_lobby and hasattr(self, "btn_leave"):
            self.btn_leave.handle_event(event)

    def _on_lobby_created(self, data):
        print(f"[SignalR] Lobby created: {data}")
        self.refresh_lobbies()

    def _on_player_joined(self, data):
        print(f"[SignalR] Player joined: {data}")
        self.refresh_lobbies()

    def _on_player_left(self, data):
        print(f"[SignalR] Player left: {data}")
        self.refresh_lobbies()

    def _on_lobby_deleted(self, data):
        print(f"[SignalR] Lobby deleted: {data}")
        self.refresh_lobbies()

    def _cancel_level_popup(self):
        self.show_level_popup = False

    def _confirm_level_popup(self):
        if self.selected_temp_level:
            self.selected_level = self.selected_temp_level
        self.show_level_popup = False

    def _join_lobby(self, code):
        lobby = next((l for l in self.lobbies if l.get("code") == code), None)
        if not lobby:
            return

        if lobby.get("passwordProtected", False):
            self.show_password_popup = True
            self.password_input = ""
            self.password_target_code = code
            self.password_timer = pygame.time.get_ticks()
            print("Lobby requires password, showing popup.")
            return

        print(f"Attempting to join lobby {code}")
        if request_helper.join_lobby(code):
            self._show_message("Joined the lobby successfully!")
            self.current_lobby = lobby

    def _leave_lobby(self):
        if not self.current_lobby:
            return
        code = self.current_lobby.get("code")
        if request_helper.leave_lobby(code):
            self._show_message("Left the lobby successfully!")
            self.current_lobby = None
            self.refresh_lobbies()

    def _host(self):
        if not self.selected_level:
            self._show_message("Please select a level first.")
            return

        password = self.host_password if self.require_password else None

        lobby_data = request_helper.create_lobby(self.selected_level["id"], password)
        if lobby_data:
            self.current_lobby = lobby_data
            self.refresh_lobbies()
            self.btn_leave = Button("Leave Lobby", (0.15, 0.85, 0.25, 0.07),
                                    self.font_medium, self._leave_lobby)
        else:
            self._show_message("Left the lobby successfully!")

    def _load_levels(self):
        self.results = request_helper.get_workshop_items() or []
        non_filtered_levels = self.results.get("LevelItems", [])
        self.level_results = []
        for level in non_filtered_levels:
            author = level.get("author", "")
            subscribed = level.get("userIsSubscribed", False)
            if author == "TuringSandbox" or subscribed:
                self.level_results.append(level)
        print(f"Loaded {len(self.level_results)} levels from Workshop.")

    def _show_message(self, text):
        self.message_text = text
        self.message_time = pygame.time.get_ticks()

    def _close(self):
        self.on_close()
