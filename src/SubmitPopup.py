import pygame
from Button import Button
from FontManager import FontManager
from AuthenticationPopup import AuthenticationPopup
import request_helper

class SubmitPopup:
    def __init__(self, screen, level_name, time_seconds, node_count, connection_count, on_submit, on_cancel):
        self.screen = screen
        self.level_name = level_name
        self.time_seconds = time_seconds
        self.node_count = node_count
        self.connection_count = connection_count
        self.on_submit = on_submit
        self.on_cancel = on_cancel

        self.title_font = FontManager.get(26)
        self.text_font = FontManager.get(20)
        self.button_font = FontManager.get(22)

        self.submit_button = Button(
            "Submit",
            (0.5 - 0.11, 0.58, 0.20, 0.06),
            self.button_font,
            self._submit_clicked
        )
        self.cancel_button = Button(
            "No (Saves Locally)",
            (0.5 - 0.11, 0.68, 0.20, 0.06),
            self.button_font,
            self._cancel_clicked
        )
        self.auth_popup = None

    def _submit_clicked(self):
        if self.on_submit:
            if request_helper.verify_authentication():
                self.on_submit()
            else:
                self.auth_popup = AuthenticationPopup(self.screen, on_authenticated=lambda user: self.on_submit())

    def _cancel_clicked(self):
        if self.on_cancel:
            self.on_cancel()

    def draw(self):
        screen = self.screen
        w, h = screen.get_size()

        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        box_w = int(w * 0.4)
        box_h = int(h * 0.28)
        box_x = (w - box_w) // 2
        box_y = (h - box_h) // 2

        pygame.draw.rect(screen, (30, 40, 70), (box_x, box_y, box_w, box_h), border_radius=16)
        pygame.draw.rect(screen, (220, 220, 250), (box_x, box_y, box_w, box_h), 2, border_radius=16)

        title_text = self.title_font.render("Submit to Leaderboard?", True, (240, 240, 255))
        title_x = box_x + (box_w - title_text.get_width()) // 2
        title_y = box_y + 16
        screen.blit(title_text, (title_x, title_y))

        lines = [
            f"Level: {self.level_name}",
            f"Time: {self.time_seconds:.2f} s",
            f"Nodes: {self.node_count}",
            f"Connections: {self.connection_count}",
        ]
        y = title_y + 40
        for line in lines:
            text = self.text_font.render(line, True, (220, 220, 240))
            x = box_x + 24
            screen.blit(text, (x, y))
            y += 24

        btn_width = 140
        btn_height = 40
        gap = 20
        total_btn_width = btn_width * 2 + gap

        buttons_y = box_y + box_h - btn_height - 20
        first_btn_x = box_x + (box_w - total_btn_width) // 2
        second_btn_x = first_btn_x + btn_width + gap

        self.submit_button.rect = pygame.Rect(first_btn_x, buttons_y, btn_width, btn_height)
        self.cancel_button.rect = pygame.Rect(second_btn_x, buttons_y, btn_width, btn_height)

        self.submit_button.draw(screen)
        self.cancel_button.draw(screen)

        if self.auth_popup:
            self.auth_popup.draw()

    def handle_event(self, event):
        if self.auth_popup:
            self.auth_popup.handle_event(event)
            return
        self.submit_button.handle_event(event)
        self.cancel_button.handle_event(event)