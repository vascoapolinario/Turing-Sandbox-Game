import threading

import pygame
from Button import Button, COLORS
from FontManager import FontManager
import request_helper
from datetime import datetime, timezone
from Environment import Environment


def time_since_utc(utc_str):
    if not utc_str:
        return "?"
    try:
        s = utc_str.strip()

        if "." in s:
            head, tail = s.split(".", 1)
            tail = tail.rstrip("Z")
            tail = tail[:6]
            s = f"{head}.{tail}Z" if utc_str.endswith("Z") else f"{head}.{tail}"

        fmt_variants = [
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%f%z",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
        ]

        dt = None
        for fmt in fmt_variants:
            try:
                dt = datetime.strptime(s, fmt)
                break
            except ValueError:
                continue

        if not dt:
            return "?"

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        diff = now - dt
        seconds = int(diff.total_seconds())

        if seconds < 60:
            return f"{seconds}s ago"
        elif seconds < 3600:
            return f"{seconds // 60}m ago"
        elif seconds < 86400:
            return f"{seconds // 3600}h ago"
        else:
            return f"{seconds // 86400}d ago"

    except Exception:
        return "?"

class LobbyMenu:
    def __init__(self, screen, on_close):
        self.screen = screen
        self.on_close = on_close
        self.font_title = FontManager.get(64, bold=True)
        self.font_small = FontManager.get(24)
        self.font_medium = FontManager.get(28, bold=True)

        self.btn_back = Button("Back", (0.04, 0.03, 0.12, 0.06), self.font_small, self._close)
        self.btn_host = Button("Host Lobby", (0.15, 0.80, 0.25, 0.08), self.font_medium, self._host)

        self.scroll_offset = 0
        self.scroll_speed = 40
        self.lobby_scroll = 0
        self.level_scroll = 0
        self.lobbies = []
        self.kick_buttons = []

        request_helper.connect_signalr(
            on_lobby_created=self._on_lobby_created,
            on_player_joined=self._on_player_joined,
            on_player_left=self._on_player_left,
            on_lobby_deleted=self._on_lobby_deleted,
            on_player_kicked=self._on_player_kicked,
            on_lobby_started=self.on_lobby_started,
            on_environment_synced=self.on_environment_synced,
            on_node_proposed=self.on_node_proposed,
            on_connection_proposed=self.on_connection_proposed,
            on_delete_proposed=self.on_delete_proposed,
            on_chat_message_received=self.on_chat_message_received
        )
        self.join_buttons = []
        self.current_lobby = None
        self.hide_started = False
        self.build_toggle_started_button()
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
        self.btn_level_cancel = Button("Cancel", (0.60, 0.76, 0.15, 0.07),
                                       self.font_small, self._cancel_level_popup)
        self.btn_level_ok = Button("OK", (0.25, 0.76, 0.15, 0.07),
                                   self.font_small, self._confirm_level_popup)
        self.selected_temp_level = None
        self.selected_temp_level_id = None
        self.selected_level_id = None
        self.message_text = ""
        self.message_time = 0
        self.message_duration = 3000

        self.lobby_name = ""
        self.name_focused = False

        self.max_players = 4
        self.slider_dragging = False

        self.code_search = ""
        self.code_search_rect = None
        self.code_search_focused = False
        self.code_search_timer = 0
        self.code_cursor_visible = True

        self.environment = None
        self.in_environment = False

        self.chat_messages = []
        self.chat_input = ""
        self.chat_input_active = False
        self.chat_cursor_visible = True
        self.chat_timer = 0
        self.max_chat_messages = 50

    def refresh_lobbies(self):
        all_lobbies = request_helper.get_lobbies(include_started=True) or []

        if self.hide_started:
            self.lobbies = [l for l in all_lobbies if not l.get("hasStarted", False)]
        else:
            self.lobbies = all_lobbies

        self._build_join_buttons()

    def build_toggle_started_button(self):
        self.btn_toggle_started = Button("Hide Started Lobbies", (0.68, 0.14, 0.1, 0.05),
                                         self.font_small, self._toggle_hide_started)


    def _toggle_hide_started(self):
        self.hide_started = not self.hide_started
        self.btn_toggle_started.text = (
            "Show All Lobbies" if self.hide_started else "Hide Started Lobbies"
        )
        self.refresh_lobbies()

    def _build_join_buttons(self):
        self.join_buttons.clear()
        for i, lobby in enumerate(self.lobbies):
            code = lobby.get("code", "???")
            btn = Button("Join", (0.0, 0.0, 0.2, 0.05),
                         self.font_small, lambda c=code: self._join_lobby(c))
            self.join_buttons.append(btn)

    def _build_kick_buttons(self):
        self.kick_buttons.clear()
        if not self.current_lobby:
            return

        w, h = self.screen.get_size()
        players = self.current_lobby.get("lobbyPlayers", [])
        host_name = self.current_lobby.get("hostPlayer", "Unknown")
        current_user = request_helper.get_username()

        if current_user != host_name:
            return

        players_rect = pygame.Rect(int(w * 0.55), int(h * 0.5),
                                   int(w * 0.38), int(h * 0.4))
        y0 = players_rect.y + 50

        for i, name in enumerate(players):
            if name == host_name:
                continue
            text_y = y0 + i * 40
            btn_rect = pygame.Rect(players_rect.right - int(w * 0.07),
                                   text_y - 5, int(w * 0.05), int(h * 0.04))
            btn = Button("Kick", btn_rect, self.font_small,
                         lambda uname=name: self._kick_player(uname))
            self.kick_buttons.append(btn)

    def update(self, dt):
        if self.in_environment and self.environment:
            self.environment.update(dt)
            return

        now = pygame.time.get_ticks()
        if not hasattr(self, "_last_ui_refresh"):
            self._last_ui_refresh = 0

        if now - self._last_ui_refresh >= 1000:
            self._last_ui_refresh = now
            request_helper.trigger_event()
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"reason": "ui_refresh"}))

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
        if self.in_environment and self.environment:
            self.environment.draw()
            now = pygame.time.get_ticks()
            if self.message_text and now - self.message_time < self.message_duration:
                msg_surf = self.font_small.render(self.message_text, True, COLORS["accent"])
                msg_bg = msg_surf.get_rect(center=(w / 2, h * 0.95))
                bg_rect = pygame.Rect(msg_bg.x - 15, msg_bg.y - 8, msg_bg.width + 30, msg_bg.height + 16)
                pygame.draw.rect(self.screen, (25, 27, 45), bg_rect, border_radius=8)
                pygame.draw.rect(self.screen, COLORS["accent"], bg_rect, 2, border_radius=8)
                self.screen.blit(msg_surf, msg_surf.get_rect(center=bg_rect.center))
            return
        self.screen.fill((20, 22, 35))
        
        for x in range(0, w, 40):
            pygame.draw.line(self.screen, (30, 32, 50), (x, 0), (x, h))
        for y in range(0, h, 40):
            pygame.draw.line(self.screen, (30, 32, 50), (0, y), (w, y))

        self.font_small = FontManager.get(int(24 * (h / 1080)))
        self.font_medium = FontManager.get(int(28 * (h / 1080)), bold=True)

        self._draw_title_box("Multiplayer", w, h)

        if self.current_lobby:
            self._draw_lobby_view(w, h)
            self._draw_chat_box(w, h)
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

        label = self.font_small.render("Code:", True, COLORS["text"])
        label_x = int(w * 0.55)
        label_y = int(h * 0.145)
        self.screen.blit(label, (label_x, label_y))

        input_w = int(w * 0.1)
        input_h = int(h * 0.045)
        input_x = label_x + label.get_width() + 10
        input_y = label_y - 5
        self.code_search_rect = pygame.Rect(input_x, input_y, input_w, input_h)

        pygame.draw.rect(self.screen, (45, 48, 75), self.code_search_rect, border_radius=6)
        pygame.draw.rect(self.screen, COLORS["accent"], self.code_search_rect, 2, border_radius=6)

        now = pygame.time.get_ticks()
        if now - self.code_search_timer > 500:
            self.code_cursor_visible = not self.code_cursor_visible
            self.code_search_timer = now

        display = self.code_search
        if self.code_search_focused and self.code_cursor_visible:
            display += "|"
        elif not display and not self.code_search_focused:
            display = "Search..."

        txt = self.font_small.render(display, True, COLORS["text"])
        self.screen.blit(txt, (self.code_search_rect.x + 8, self.code_search_rect.y + 8))

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

            if i % 2 == 0:
                bg_color = (45, 48, 70)
            else:
                bg_color = (55, 58, 80)

            pygame.draw.rect(self.screen, bg_color, lobby_rect, border_radius=10)
            pygame.draw.rect(self.screen, (25, 27, 45), lobby_rect, 1, border_radius=10)

            code = lobby.get("code", "???")
            host = lobby.get("hostPlayer", "Unknown")
            name = lobby.get("name", f"{host}'s Lobby")
            level = lobby.get("levelName", "Unknown Level")
            created = time_since_utc(lobby.get("createdAt", ""))
            count = len(lobby.get("lobbyPlayers", []))
            max_players = lobby.get("maxPlayers", 4)

            PasswordProtected = lobby.get("passwordProtected", False)
            if PasswordProtected:
                created += " [Requires Password]"


            self.screen.blit(self.font_small.render(f"{name} | Code: {code} | Host: {host} | Created: {created}",
                                                    True, COLORS["text"]),
                             (lobby_rect.x + 15, lobby_rect.y + 5))
            self.screen.blit(self.font_small.render(f"Level: {level} | Players: {count}/{max_players}", True, COLORS["text"]),
                             (lobby_rect.x + 15, lobby_rect.y + 30))

            btn = self.join_buttons[i]
            btn.rect = pygame.Rect(lobby_rect.right - int(w * 0.07),
                                   lobby_rect.y + int(h * 0.015),
                                   int(w * 0.05), int(h * 0.045))
            btn.draw(self.screen)
        self.btn_toggle_started.update_rect(self.screen.get_size())
        self.btn_toggle_started.font = FontManager.get(int(20 * (h / 1080)))
        self.btn_toggle_started.draw(self.screen)
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

        name = lobby.get("name", "Unnamed Lobby")
        code = lobby.get("code", "???")
        level = lobby.get("levelName", "Unknown Level")
        created = time_since_utc(lobby.get("createdAt", ""))

        lines = [f"Name: {name}",f"Code: {code}", f"Level: {level}", f"Created: {created}"]
        for i, line in enumerate(lines):
            surf = self.font_small.render(line, True, COLORS["text"])
            self.screen.blit(surf, (info_rect.x + 20,
                                    info_rect.y + 20 + i * 35))

        players_rect = pygame.Rect(int(w * 0.55), int(h * 0.5),
                                   int(w * 0.38), int(h * 0.4))
        pygame.draw.rect(self.screen, (35, 38, 60), players_rect, border_radius=15)
        pygame.draw.rect(self.screen, COLORS["accent"], players_rect, 2, border_radius=15)

        host_name = lobby.get("hostPlayer", "Unknown")
        players = lobby.get("lobbyPlayers", [])
        y0 = players_rect.y + 50

        self.screen.blit(self.font_medium.render("Players", True, COLORS["accent"]),
                         (players_rect.x + 20, players_rect.y + 10))

        for i, name in enumerate(players):
            tag = "[HOST] " if name == host_name else ""
            text_y = y0 + i * 40
            name_surf = self.font_small.render(f"{tag}{name}", True, COLORS["text"])
            self.screen.blit(name_surf, (players_rect.x + 25, text_y))

        host_name = lobby.get("hostPlayer", "")
        current_user = request_helper.get_username()
        has_started = lobby.get("hasStarted", False)

        if current_user == host_name and not has_started:
            if not hasattr(self, "btn_start"):
                self.btn_start = Button("Start Game", (0.15, 0.75, 0.25, 0.07),
                                        self.font_medium, self._start_lobby)
            self.btn_start.draw(self.screen)
        elif hasattr(self, "btn_start"):
            del self.btn_start

        for btn in self.kick_buttons:
            btn.draw(self.screen)

        if hasattr(self, "btn_leave"):
            self.btn_leave.draw(self.screen)

    def _draw_chat_box(self, w, h):
        box = pygame.Rect(int(w * 0.08), int(h * 0.2), int(w * 0.38), int(h * 0.4))
        pygame.draw.rect(self.screen, (35, 38, 60), box, border_radius=10)
        pygame.draw.rect(self.screen, COLORS["accent"], box, 2, border_radius=10)

        title = self.font_medium.render("Lobby Chat", True, COLORS["accent"])
        self.screen.blit(title, (box.x + 15, box.y + 10))

        y_start = box.y + 50
        line_height = 25
        visible = self.chat_messages[-10:]
        for i, msg in enumerate(visible):
            sender, text = msg
            color = COLORS["text"]
            label = self.font_small.render(f"{sender}: {text}", True, color)
            self.screen.blit(label, (box.x + 15, y_start + i * line_height))

        input_rect = pygame.Rect(box.x + 10, box.bottom - 40, box.width - 20, 30)
        pygame.draw.rect(self.screen, (45, 48, 75), input_rect, border_radius=6)
        pygame.draw.rect(self.screen, COLORS["accent"], input_rect, 2, border_radius=6)

        now = pygame.time.get_ticks()
        if now - self.chat_timer > 500:
            self.chat_cursor_visible = not self.chat_cursor_visible
            self.chat_timer = now

        display = self.chat_input
        if self.chat_input_active and self.chat_cursor_visible:
            display += "|"
        elif not display and not self.chat_input_active:
            display = "Type a message..."

        txt = self.font_small.render(display, True, COLORS["text"])
        self.screen.blit(txt, (input_rect.x + 8, input_rect.y + 5))
        self.chat_input_rect = input_rect

    def _draw_host_form(self, w, h):
        left_rect = pygame.Rect(int(w * 0.08), int(h * 0.2),
                                int(w * 0.38), int(h * 0.7))
        pygame.draw.rect(self.screen, (35, 38, 60), left_rect, border_radius=15)
        pygame.draw.rect(self.screen, COLORS["accent"], left_rect, 2, border_radius=15)
        for y in range(left_rect.y, left_rect.bottom, 40):
            pygame.draw.line(self.screen, (30, 32, 50),
                             (left_rect.x + 10, y),
                             (left_rect.right - 10, y))

        name_label = self.font_small.render("Lobby Name:", True, COLORS["text"])
        self.screen.blit(name_label, (int(w * 0.09), int(h * 0.21)))
        name_rect = pygame.Rect(int(w * 0.09), int(h * 0.25), int(w * 0.25), int(h * 0.05))
        pygame.draw.rect(self.screen, (45, 48, 75), name_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLORS["accent"], name_rect, 2, border_radius=8)

        now = pygame.time.get_ticks()
        if now - getattr(self, "name_timer", 0) > 500:
            self.name_cursor_visible = not getattr(self, "name_cursor_visible", True)
            self.name_timer = now

        if not self.lobby_name:
            if self.name_focused:
                display_name = "|" if self.name_cursor_visible else ""
            else:
                display_name = "Enter lobby name..."
        else:
            display_name = self.lobby_name
            if self.name_focused and self.name_cursor_visible:
                display_name += "|"
        name_surf = self.font_small.render(display_name, True, COLORS["text"])
        self.screen.blit(name_surf, (name_rect.x + 10, name_rect.y + 10))
        self.name_rect = name_rect

        slider_label = self.font_small.render(f"Max Players: {self.max_players}", True, COLORS["text"])
        self.screen.blit(slider_label, (int(w * 0.09), int(h * 0.33)))

        slider_x = int(w * 0.09)
        slider_y = int(h * 0.37)
        slider_w = int(w * 0.25)
        slider_h = 6
        pygame.draw.rect(self.screen, (60, 65, 90), (slider_x, slider_y, slider_w, slider_h), border_radius=3)

        knob_x = slider_x + int(((self.max_players - 2) / 8) * slider_w)
        knob_rect = pygame.Rect(knob_x - 8, slider_y - 8, 16, 20)
        pygame.draw.rect(self.screen, COLORS["accent"], knob_rect, border_radius=4)
        self.slider_rect = pygame.Rect(slider_x, slider_y - 10, slider_w, 25)
        self.knob_rect = knob_rect

        toggle_size = int(h * 0.04)
        toggle_rect = pygame.Rect(int(w * 0.09), int(h * 0.45), toggle_size, toggle_size)
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

        lvl_rect = pygame.Rect(int(w * 0.09), int(h * 0.55), int(w * 0.06), int(h * 0.04))
        pygame.draw.rect(self.screen, (45, 48, 75), lvl_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLORS["accent"], lvl_rect, 2, border_radius=8)
        txt = self.font_small.render("Select Level", True, COLORS["text"])
        self.screen.blit(txt, (lvl_rect.x + 10, lvl_rect.y + 10))

        name = self.selected_level["name"] if self.selected_level else "None"
        label = self.font_small.render(f"Current Level: {name}", True, COLORS["text"])
        self.screen.blit(label, (lvl_rect.right + 20, lvl_rect.y + 15))

        pw_valid = (not self.require_password) or (1 <= len(self.host_password) <= 30)
        name_valid = 1 <= len(self.lobby_name) <= 30
        self.btn_host.disabled = not (self.selected_level and pw_valid and name_valid)

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
        btn_y = box.bottom - int(h * 0.08)

        self.btn_level_cancel.rect = pygame.Rect(int(w * 0.28), btn_y, btn_w, btn_h)
        self.btn_level_ok.rect = pygame.Rect(int(w * 0.57), btn_y, btn_w, btn_h)
        self.btn_level_cancel.draw(self.screen)
        self.btn_level_ok.draw(self.screen)

    def _kick_player(self, player_name):
        if not self.current_lobby or not player_name:
            return

        code = self.current_lobby.get("code")
        success = request_helper.kick_player(code, player_name)

        if success:
            self._show_message(f"{player_name} was kicked.")
            self.refresh_lobbies()
        else:
            self._show_message("Failed to kick player.")


    def handle_event(self, event):
        if self.in_environment and self.environment:
            self.environment.handle_event(event)
            return
        if event.type == pygame.MOUSEWHEEL and not self.show_level_popup:
            if event.y < 0 and self.lobby_scroll < max(0, len(self.lobbies) - 8):
                self.lobby_scroll += 1
            elif event.y > 0 and self.lobby_scroll > 0:
                self.lobby_scroll -= 1
        if self.show_password_popup:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    target_lobby = next((l for l in self.lobbies if l.get("code") == self.password_target_code), None)
                    if target_lobby["hasStarted"]:
                        if request_helper.join_lobby(self.password_target_code, self.password_input):
                            self.current_lobby = target_lobby
                            request_helper.join_signalr_group(self.password_target_code)
                            self.enter_multiplayer_environment()
                    else:
                        if request_helper.join_lobby(self.password_target_code, self.password_input):
                            request_helper.join_signalr_group(self.password_target_code)
                            self.refresh_lobbies()
                            updated = next((l for l in self.lobbies if l.get("code") == self.password_target_code), None)
                            self.current_lobby = updated
                            self.btn_leave = Button("Leave Lobby", (0.15, 0.85, 0.25, 0.07),
                                                    self.font_medium, self._leave_lobby)
                            self._build_kick_buttons()
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
                        self.selected_temp_level_id = lvl["id"]
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
        if self.current_lobby and not self.show_level_popup and not self.show_password_popup:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if hasattr(self, "chat_input_rect") and self.chat_input_rect.collidepoint(event.pos):
                    self.chat_input_active = True
                else:
                    self.chat_input_active = False

            if self.chat_input_active and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and self.chat_input.strip():
                    code = self.current_lobby.get("code")
                    msg = self.chat_input.strip()
                    sender = request_helper.get_username()
                    request_helper.send_chat_message(code, sender, msg)
                    self.chat_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.chat_input = self.chat_input[:-1]
                else:
                    ch = event.unicode
                    if len(ch) == 1 and ch.isprintable() and len(self.chat_input) < 200:
                        self.chat_input += ch

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            toggle_rect = pygame.Rect(int(self.screen.get_width() * 0.09), int(self.screen.get_height() * 0.45),
                                      int(self.screen.get_width() * 0.05), int(self.screen.get_height() * 0.05))

            if self.code_search_rect and self.code_search_rect.collidepoint(mx, my):
                self.code_search_focused = True
            else:
                self.code_search_focused = False

            if self.name_rect and self.name_rect.collidepoint(mx, my):
                self.name_focused = True
            else:
                self.name_focused = False

            if toggle_rect.collidepoint(mx, my):
                self.require_password = not self.require_password
                self.host_password = ""
                self.password_focused = False
            elif self.require_password and self.password_rect and self.password_rect.collidepoint(mx, my):
                self.password_focused = True
            else:
                self.password_focused = False
            lvl_rect = pygame.Rect(int(self.screen.get_width() * 0.09), int(self.screen.get_height() * 0.55),
                                   int(self.screen.get_width() * 0.06), int(self.screen.get_height() * 0.04))
            if lvl_rect.collidepoint(mx, my):
                self.show_level_popup = True
                self._load_levels()

        if event.type == pygame.MOUSEBUTTONDOWN and self.slider_rect.collidepoint(mx, my):
            self.slider_dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.slider_dragging = False

        if event.type == pygame.MOUSEMOTION and self.slider_dragging:
            mx, my = event.pos
            rel_x = max(0, min(mx - self.slider_rect.x, self.slider_rect.width))
            ratio = rel_x / self.slider_rect.width
            new_value = 2 + round(ratio * 8)
            self.max_players = max(2, min(10, new_value))

        if self.code_search_focused and event.type == pygame.KEYDOWN and not self.show_level_popup:
            if event.key == pygame.K_BACKSPACE:
                self.code_search = self.code_search[:-1]
                self._search_lobby_by_code(self.code_search)
            elif event.key == pygame.K_RETURN:
                if len(self.code_search) == 5 and self.code_search.isdigit():
                    self._search_lobby_by_code(self.code_search)
            else:
                ch = event.unicode
                if len(ch) == 1 and ch.isdigit() and len(self.code_search) < 5:
                    self.code_search += ch
                    self._search_lobby_by_code(self.code_search)

        if self.require_password and self.password_focused and event.type == pygame.KEYDOWN and not self.show_password_popup:
            if event.key == pygame.K_BACKSPACE:
                self.host_password = self.host_password[:-1]
            else:
                ch = event.unicode
                if len(ch) == 1 and ch.isprintable() and len(self.host_password) < 30:
                    self.host_password += ch

        if self.name_focused and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.lobby_name = self.lobby_name[:-1]
            else:
                ch = event.unicode
                if len(ch) == 1 and ch.isprintable() and len(self.lobby_name) < 30:
                    self.lobby_name += ch

        self.btn_host.handle_event(event)
        for button in self.join_buttons:
            button.handle_event(event)
        for btn in getattr(self, "kick_buttons", []):
            btn.handle_event(event)
        if event.type == pygame.KEYDOWN and not self.show_level_popup and not self.show_password_popup:
            if event.key == pygame.K_ESCAPE:
                self._close()
        if self.current_lobby and hasattr(self, "btn_leave"):
            self.btn_leave.handle_event(event)
        if hasattr(self, "btn_start"):
            self.btn_start.handle_event(event)
        self.btn_toggle_started.handle_event(event)

    def _on_lobby_created(self, data):
        self.refresh_lobbies()
        request_helper.trigger_event()

    def _on_player_joined(self, data):
        self._show_message("A player has joined the lobby.")
        print("Player joined the lobby")
        if self.in_environment:
            if self.environment and self.environment.is_host:
                threading.Timer(1.0, self.environment._broadcast_state).start()
        else:
            self.refresh_lobbies()

            code = data.get("lobbyCode")
            if self.current_lobby and self.current_lobby.get("code") == code:
                updated = next((l for l in self.lobbies if l.get("code") == code), None)
                if updated:
                    self.current_lobby = updated
                    self._build_kick_buttons()
            request_helper.trigger_event()

    def _on_player_left(self, data):
        self._show_message("A player has left the lobby.")
        print("Player left the lobby")
        self.refresh_lobbies()
        if not any(l.get("code") == self.current_lobby.get("code") for l in self.lobbies):
            if self.in_environment:
                self.environment.multiplayer_left = True
            self.current_lobby = None
            request_helper.leave_signalr_group(data.get("lobbyCode"))
            request_helper.trigger_event()
            return
        request_helper.trigger_event()

        code = data.get("lobbyCode")
        if self.current_lobby and self.current_lobby.get("code") == code:
            updated = next((l for l in self.lobbies if l.get("code") == code), None)
            if updated:
                self.current_lobby = updated
                self._build_kick_buttons()
        request_helper.trigger_event()


    def _on_player_kicked(self, data):
        if not self.current_lobby:
            return

        code = data.get("lobbyCode")
        kicked_name = data.get("kickedPlayerName")

        if request_helper.get_username() == kicked_name:
            if self.current_lobby.get("code") == code:
                if self.in_environment:
                    pass
                else:
                    self._show_message("You were kicked from the lobby.")
                    request_helper.leave_signalr_group(code)
                    self.current_lobby = None
            return

        if self.in_environment:
            self._show_message(f"{kicked_name} was kicked from the lobby.")
        else:
            if self.current_lobby.get("code") == code:
                self.refresh_lobbies()
                updated = next((l for l in self.lobbies if l.get("code") == code), None)
                if updated:
                    self.current_lobby = updated
                    self._build_kick_buttons()
                    if request_helper.get_username() != updated.get("hostPlayer"):
                        self._show_message(f"{kicked_name} was kicked from the lobby.")
            request_helper.trigger_event()

    def _on_lobby_deleted(self, data):
        print("Lobby was closed by host")
        code = data.get("lobbyCode")
        if self.current_lobby and self.current_lobby.get("code") == code:
            self._show_message("Host has closed the lobby.")
            if self.in_environment:
                self.environment.multiplayer_left = True
            self.current_lobby = None
        self.refresh_lobbies()

    def _cancel_level_popup(self):
        self.show_level_popup = False

    def _confirm_level_popup(self):
        if self.selected_temp_level:
            self.selected_level = self.selected_temp_level
            self.selected_level_id = self.selected_temp_level["id"]
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
            return

        if request_helper.join_lobby(code):
            if lobby.get("hasStarted", False):
                self.current_lobby = lobby
                request_helper.join_signalr_group(code)
                self.enter_multiplayer_environment()
                return
            self._show_message("Joined the lobby successfully!")
            self.btn_leave = Button("Leave Lobby", (0.15, 0.85, 0.25, 0.07),
                                    self.font_medium, self._leave_lobby)
            self.refresh_lobbies()
            request_helper.join_signalr_group(code)
            lobby = next((l for l in self.lobbies if l.get("code") == code), None)
            self.current_lobby = lobby
            self._build_kick_buttons()
        request_helper.trigger_event()

    def _leave_lobby(self):
        if not self.current_lobby:
            return
        code = self.current_lobby.get("code")
        if request_helper.leave_lobby(code):
            self._show_message("Left the lobby successfully!")
            self.current_lobby = None
            request_helper.leave_signalr_group(code)
            self.refresh_lobbies()
        request_helper.trigger_event()

    def _host(self):
        if not self.selected_level:
            self._show_message("Please select a level first.")
            return

        password = self.host_password if self.require_password else None

        lobby_data = request_helper.create_lobby(
            self.selected_level["id"],
            self.lobby_name.strip() or "Unnamed Lobby",
            self.max_players,
            password
        )

        if lobby_data:
            self.refresh_lobbies()
            self.current_lobby = lobby_data
            request_helper.join_signalr_group(lobby_data["code"])
            self.btn_leave = Button("Leave Lobby", (0.15, 0.85, 0.25, 0.07),
                                    self.font_medium, self._leave_lobby)
            self._build_kick_buttons()
        else:
            self._show_message("Left the lobby successfully!")
        request_helper.trigger_event()

    def _start_lobby(self):
        if not self.current_lobby:
            return

        if len(self.current_lobby.get("lobbyPlayers", [])) < 2:
            self._show_message("At least 2 players are required to start the lobby.")
            return
        code = self.current_lobby.get("code")
        success = request_helper.start_lobby(code)

        if success:
            self._show_message("Lobby started successfully!")
        else:
            self._show_message("Failed to start lobby.")
        request_helper.trigger_event()

    def on_lobby_started(self, data):
        code = data.get("lobbyCode")

        if self.current_lobby and self.current_lobby.get("code") == code:
            self.current_lobby["hasStarted"] = True
            self._show_message("Lobby has started!")

            self.enter_multiplayer_environment()
        request_helper.trigger_event()

    def enter_multiplayer_environment(self):

        if not self.current_lobby:
            return

        code = self.current_lobby.get("code")
        host_name = self.current_lobby.get("hostPlayer", "")
        current_user = request_helper.get_username()
        is_host = (current_user == host_name)

        if is_host:
            level_id = self.selected_level_id
            level = None
            if level_id:
                level = request_helper.workshopitem_to_object(request_helper.get_workshop_item_by_id(level_id))
        else:
            level_name = self.current_lobby.get("levelName", "")
            level = next((request_helper.workshopitem_to_object(item)
                          for item in request_helper.get_workshop_items().get("LevelItems", [])
                          if item.get("name") == level_name), None)

        self.environment = Environment(
            self.screen,
            level=level,
            sandbox_alphabet=None,
            multiplayer=True,
            is_host=is_host,
            lobby_code=code
        )

        self.in_environment = True
        print(f"[MultiplayerMenu] Environment started for lobby {code}, host={is_host}")


    def _load_levels(self):
        self.results = request_helper.get_workshop_items() or []
        non_filtered_levels = self.results.get("LevelItems", [])
        self.level_results = []
        for level in non_filtered_levels:
            author = level.get("author", "")
            subscribed = level.get("userIsSubscribed", False)
            if author == "TuringSandbox" or subscribed:
                self.level_results.append(level)

    def _show_message(self, text):
        self.message_text = text
        self.message_time = pygame.time.get_ticks()

    def _close(self):
        self.on_close()

    def _search_lobby_by_code(self, code):
        all_lobbies = request_helper.get_lobbies() or []
        filtered = [
            l for l in all_lobbies
            if str(l.get("code", "")).startswith(code)
        ]

        if filtered:
            self.lobbies = filtered
            self._build_join_buttons()
            self._show_message(f"Found {len(filtered)} lobby(ies) matching '{code}'.")
        else:
            self.lobbies = []
            self._build_join_buttons()
            self._show_message("No lobbies found.")
        request_helper.trigger_event()

    def on_environment_synced(self, data):
        print(f"[SignalR] Environment synced: {data.keys() if isinstance(data, dict) else data}")
        code = data.get("lobbyCode")
        state = data.get("state")

        if not state or not self.current_lobby:
            return

        if self.environment and self.current_lobby.get("code") == code:
            print(f"[Multiplayer] Applying remote state for lobby {code} ...")
            self.environment.apply_remote_state(state)
        else:
            print(f"[Multiplayer] Ignored state for lobby {code} (not active).")
        request_helper.trigger_event()

    def on_node_proposed(self, data):
        code = data.get("lobbyCode")
        if not self.environment or self.current_lobby.get("code") != code:
            return

        x = data.get("x")
        y = data.get("y")
        is_end = data.get("isEnd", False)
        proposer = data.get("proposer", "?")
        print(f"[Multiplayer] Node proposed by {proposer} at ({x}, {y}), end={is_end}")

        self.environment.create_node_from_proposal(x, y, is_end)
        request_helper.trigger_event()

    def on_connection_proposed(self, data):
        code = data.get("lobbyCode")
        if not self.environment or self.current_lobby.get("code") != code:
            return

        start_id = data.get("startId")
        end_id = data.get("endId")
        proposer = data.get("proposer")
        print(f"[Multiplayer] Connection proposed by {proposer} ({start_id}->{end_id})")

        self.environment.create_connection_from_proposal(data)
        request_helper.trigger_event()

    def on_delete_proposed(self, data):
        code = data.get("lobbyCode")
        if not self.environment or self.current_lobby.get("code") != code:
            return

        target = data.get("target")
        proposer = data.get("proposer")
        print(f"[Multiplayer] Delete proposed by {proposer}")
        self.environment.apply_delete_proposal(target)
        request_helper.trigger_event()

    def on_chat_message_received(self, data):
        print("received chat message")
        code = data.get("lobbyCode")
        if not self.current_lobby or self.current_lobby.get("code") != code:
            return

        sender = data.get("sender", "Unknown")
        message = data.get("message", "")
        self.chat_messages.append((sender, message))
        request_helper.trigger_event()