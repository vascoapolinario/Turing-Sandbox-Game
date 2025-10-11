import pygame
from MainMenu import COLORS


class ConnectionWindow:
    def __init__(self, screen, connection, symbols, on_save, on_cancel):
        """
        symbols: list[str] — allowed tape symbols for read/write (e.g. ['0', '1', '_'])
        """
        self.screen = screen
        self.connection = connection
        self.symbols = symbols
        self.on_save = on_save
        self.on_cancel = on_cancel

        self.font = pygame.font.SysFont("futura", 24, bold=True)
        self.selected_read = set(connection.read) if connection.read else set()
        self.selected_write = connection.write
        self.selected_move = connection.move


        self.width = 600
        self.height = 420
        self.rect = pygame.Rect(
            screen.get_width() // 2 - self.width // 2,
            screen.get_height() // 2 - self.height // 2,
            self.width,
            self.height,
        )


        self.save_button = pygame.Rect(self.rect.x + 120, self.rect.bottom - 60, 150, 45)
        self.cancel_button = pygame.Rect(self.rect.x + 330, self.rect.bottom - 60, 150, 45)


        self.hovered_symbol = None
        self.hovered_move = None
        self.hovered_button = None

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered_symbol = None
            self.hovered_move = None
            self.hovered_button = None
            mx, my = event.pos


            for section in ("read", "write"):
                for i, sym in enumerate(self.symbols):
                    rect = self._symbol_rect(i, section)
                    if rect.collidepoint(mx, my):
                        self.hovered_symbol = (section, sym)
                        return

            for move, rect in self._move_buttons().items():
                if rect.collidepoint(mx, my):
                    self.hovered_move = move
                    return


            if self.save_button.collidepoint(mx, my):
                self.hovered_button = "save"
            elif self.cancel_button.collidepoint(mx, my):
                self.hovered_button = "cancel"

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.save_button.collidepoint(event.pos):
                self._commit()
                return True
            elif self.cancel_button.collidepoint(event.pos):
                self.on_cancel()
                return True

            for i, sym in enumerate(self.symbols):
                rect = self._symbol_rect(i, "read")
                if rect.collidepoint(event.pos):
                    if sym in self.selected_read:
                        self.selected_read.remove(sym)
                    else:
                        self.selected_read.add(sym)
                    return True

            for i, sym in enumerate(self.symbols):
                rect = self._symbol_rect(i, "write")
                if rect.collidepoint(event.pos):
                    self.selected_write = sym
                    return True

            for move, rect in self._move_buttons().items():
                if rect.collidepoint(event.pos):
                    self.selected_move = move
                    return True
        return False

    def _commit(self):
        read = list(self.selected_read)
        write = self.selected_write
        move = self.selected_move
        self.on_save(read, write, move)

    def draw(self):
        shadow_rect = self.rect.inflate(10, 10)
        pygame.draw.rect(self.screen, (0, 0, 0, 80), shadow_rect, border_radius=14)
        self._draw_gradient_rect(self.rect, (25, 35, 65), (35, 45, 85))
        pygame.draw.rect(self.screen, COLORS["accent"], self.rect, 2, border_radius=12)

        title = self.font.render("Edit Connection Logic", True, COLORS["text"])
        self.screen.blit(title, (self.rect.centerx - title.get_width() // 2, self.rect.y + 15))

        read_label = self.font.render("Read Symbols (Mandatory):", True, COLORS["text"])
        self.screen.blit(read_label, (self.rect.x + 40, self.rect.y + 70))
        for i, sym in enumerate(self.symbols):
            rect = self._symbol_rect(i, "read")
            hovered = self.hovered_symbol == ("read", sym)
            self._draw_option(rect, sym, sym in self.selected_read, hovered)

        write_label = self.font.render("Write Symbol:", True, COLORS["text"])
        self.screen.blit(write_label, (self.rect.x + 40, self.rect.y + 170))
        for i, sym in enumerate(self.symbols):
            rect = self._symbol_rect(i, "write")
            hovered = self.hovered_symbol == ("write", sym)
            self._draw_option(rect, sym, sym == self.selected_write, hovered)

        move_label = self.font.render("Move Direction (Mandatory):", True, COLORS["text"])
        self.screen.blit(move_label, (self.rect.x + 40, self.rect.y + 270))
        for move, rect in self._move_buttons().items():
            hovered = self.hovered_move == move
            self._draw_option(rect, move, move == self.selected_move, hovered)

        self._draw_button(
            self.save_button,
            "Save",
            (90, 200, 120),
            hovered=(self.hovered_button == "save"),
        )
        self._draw_button(
            self.cancel_button,
            "Cancel",
            (200, 80, 80),
            hovered=(self.hovered_button == "cancel"),
        )

    def _symbol_rect(self, index, section):
        base_y = self.rect.y + (100 if section == "read" else 200)
        return pygame.Rect(
            self.rect.x + 40 + index * 70,
            base_y,
            55,
            45,
        )

    def _move_buttons(self):
        y = self.rect.y + 300
        x = self.rect.x + 40
        return {
            "L": pygame.Rect(x, y, 80, 45),
            "R": pygame.Rect(x + 120, y, 80, 45)
        }

    def _draw_option(self, rect, text, selected, hovered):
        base_color = (70, 90, 120)
        if selected:
            base_color = (110, 200, 110)
        elif hovered:
            base_color = (100, 120, 160)
        pygame.draw.rect(self.screen, base_color, rect, border_radius=6)
        pygame.draw.rect(self.screen, COLORS["text"], rect, 2, border_radius=6)
        label = self.font.render(str(text), True, (255, 255, 255))
        self.screen.blit(label, (rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2))

    def _draw_button(self, rect, text, color, hovered=False):
        c = tuple(min(255, x + 40) for x in color) if hovered else color
        pygame.draw.rect(self.screen, c, rect, border_radius=10)
        pygame.draw.rect(self.screen, (30, 30, 30), rect, 2, border_radius=10)
        label = self.font.render(text, True, (255, 255, 255))
        self.screen.blit(label, (rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2))

    def _draw_gradient_rect(self, rect, top_color, bottom_color):
        """Draws a vertical gradient inside a rect."""
        gradient_surface = pygame.Surface((rect.width, rect.height))
        for y in range(rect.height):
            ratio = y / rect.height
            r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
            g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
            b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
            pygame.draw.line(gradient_surface, (r, g, b), (0, y), (rect.width, y))
        self.screen.blit(gradient_surface, rect.topleft)
