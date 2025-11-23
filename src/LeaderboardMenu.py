import pygame
from FontManager import FontManager
from Button import Button, COLORS
import math
import request_helper

class LeaderboardMenu:
    def __init__(self, screen, level_name, on_close):
        self.screen = screen
        self.level_name = level_name
        self.on_close = on_close

        self.title_font = FontManager.get(42)
        self.font_title = self.title_font
        self.entry_font = FontManager.get(24)
        self.header_font = FontManager.get(22)

        self.entries = request_helper.get_leaderboard(level_name) or []

        self.close_button = Button(
            "Close",
            (0.5 - 0.10, 0.88, 0.20, 0.08),
            FontManager.get(26),
            self._close
        )

    def _close(self):
        if self.on_close:
            self.on_close()

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

    def _format_time(self, seconds):
        try:
            s = float(seconds)
        except (TypeError, ValueError):
            return "—"

        if s < 0:
            s = 0.0

        if s < 60:
            value = s
            unit = "second" if abs(value - 1.0) < 1e-6 else "seconds"
        elif s < 3600:
            value = s / 60.0
            unit = "minute" if abs(value - 1.0) < 1e-6 else "minutes"
        else:
            value = s / 3600.0
            unit = "hour" if abs(value - 1.0) < 1e-6 else "hours"

        return f"{value:.2f} {unit}"

    def handle_event(self, event):
        self.close_button.handle_event(event)

    def draw(self):
        screen = self.screen
        w, h = screen.get_size()

        screen.fill(COLORS["background"])
        time = pygame.time.get_ticks() / 1000
        glow = (1 + math.sin(time * 2)) / 2
        glow_color = (int(40 + 40 * glow), int(45 + 40 * glow), int(70 + 40 * glow))
        for x in range(0, w, 40):
            pygame.draw.line(screen, glow_color, (x, 0), (x, h))
        for y in range(0, h, 40):
            pygame.draw.line(screen, glow_color, (0, y), (w, y))

        self._draw_title_box(f"Leaderboard – {self.level_name}", w, h)

        panel_rect = pygame.Rect(w * 0.08, h * 0.14, w * 0.84, h * 0.68)
        pygame.draw.rect(screen, (25, 30, 55), panel_rect, border_radius=18)
        pygame.draw.rect(screen, COLORS["accent"], panel_rect, 2, border_radius=18)

        header_y = panel_rect.y + 20
        row_left = panel_rect.x + 20
        col_rank = row_left
        col_player = row_left + 70
        col_time = panel_rect.x + int(panel_rect.width * 0.55)
        col_nodes = panel_rect.x + int(panel_rect.width * 0.73)
        col_conns = panel_rect.x + int(panel_rect.width * 0.86)

        header_labels = [
            ("#", col_rank),
            ("Player", col_player),
            ("Time", col_time),
            ("Nodes", col_nodes),
            ("Conns", col_conns),
        ]

        for text, x in header_labels:
            surf = self.header_font.render(text, True, COLORS["accent"])
            screen.blit(surf, (x, header_y))

        pygame.draw.line(
            screen,
            (80, 90, 130),
            (panel_rect.x + 10, header_y + 30),
            (panel_rect.right - 10, header_y + 30),
            2,
        )

        row_y = header_y + 40
        row_height = 32
        max_rows = int((panel_rect.height - 70) // row_height)

        if not self.entries:
            empty = self.entry_font.render("No submissions yet for this level.", True, COLORS["text"])
            empty_rect = empty.get_rect(center=panel_rect.center)
            screen.blit(empty, empty_rect)
        else:
            for idx, e in enumerate(self.entries[:max_rows]):
                if idx % 2 == 0:
                    row_bg_color = (30, 36, 70)
                else:
                    row_bg_color = (24, 30, 60)

                if idx == 0:
                    row_bg_color = (80, 70, 30)
                elif idx == 1:
                    row_bg_color = (70, 70, 80)
                elif idx == 2:
                    row_bg_color = (60, 55, 80)

                row_rect = pygame.Rect(panel_rect.x + 10, row_y, panel_rect.width - 20, row_height - 4)
                pygame.draw.rect(screen, row_bg_color, row_rect, border_radius=10)

                rank_text = f"{idx+1}"
                player_name = e.get("playerName", "Unknown")
                time_val = e.get("time", 0.0)
                nodes_val = e.get("nodeCount", 0)
                conns_val = e.get("connectionCount", 0)

                time_text = self._format_time(time_val)

                col_values = [
                    (rank_text, col_rank),
                    (player_name, col_player),
                    (time_text, col_time),
                    (str(nodes_val), col_nodes),
                    (str(conns_val), col_conns),
                ]

                for text, x in col_values:
                    surf = self.entry_font.render(text, True, COLORS["text"])
                    screen.blit(surf, (x, row_y + 4))

                row_y += row_height

        self.close_button.update_rect_withscale(screen.get_size())
        self.close_button.draw(screen)
