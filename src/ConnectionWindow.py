import pygame
from MainMenu import COLORS
from FontManager import FontManager


class ConnectionWindow:
    def __init__(self, screen, connection, symbols, on_save, on_cancel, double_tape=False):
        self.screen = screen
        self.connection = connection
        self.symbols = symbols
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.double_tape = double_tape
        self.page_index = 0
        self.symbols_per_page = 4
        self._read_arrows_tape1 = (None, None)
        self._read_arrows_tape2 = (None, None)

        self.font = FontManager.get(24)

        self.selected_read1 = set(connection.read) if connection.read else set()
        self.selected_write1 = connection.write
        self.selected_move1 = connection.move

        self.selected_read2 = {"_"}
        self.selected_write2 = None
        self.selected_move2 = "S"

        self.width = 800 if double_tape else 600
        self.height = 460
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

            for tape in (1, 2 if self.double_tape else 1):
                offset = 0 if tape == 1 else self.width // 2
                for section in ("read", "write"):
                    start = self.page_index * self.symbols_per_page
                    end = start + self.symbols_per_page
                    for i, sym in enumerate(self.symbols[start:end]):
                        rect = self._symbol_rect(i, section, offset)
                        if rect.collidepoint(mx, my):
                            self.hovered_symbol = (tape, section, sym)
                            return
                for move, rect in self._move_buttons(offset).items():
                    if rect.collidepoint(mx, my):
                        self.hovered_move = (tape, move)
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

            for arrows in (self._read_arrows_tape1, self._read_arrows_tape2):
                left_arrow, right_arrow = arrows
                if left_arrow and left_arrow.collidepoint(event.pos) and self.page_index > 0:
                    self.page_index -= 1
                    return True
                if right_arrow and right_arrow.collidepoint(event.pos) and (
                        (self.page_index + 1) * self.symbols_per_page < len(self.symbols)
                ):
                    self.page_index += 1
                    return True

            for tape in (1, 2 if self.double_tape else 1):
                offset = 0 if tape == 1 else self.width // 2
                reads = self.selected_read1 if tape == 1 else self.selected_read2
                write = "selected_write1" if tape == 1 else "selected_write2"
                move = "selected_move1" if tape == 1 else "selected_move2"

                start = self.page_index * self.symbols_per_page
                end = start + self.symbols_per_page
                for i, sym in enumerate(self.symbols[start:end]):
                    rect = self._symbol_rect(i, "read", offset)
                    if rect.collidepoint(event.pos):
                        if sym in reads:
                            reads.remove(sym)
                        else:
                            reads.add(sym)
                        return True

                for i, sym in enumerate(self.symbols[start:end]):
                    rect = self._symbol_rect(i, "write", offset)
                    if rect.collidepoint(event.pos):
                        if getattr(self, write) == sym:
                            setattr(self, write, None)
                        else:
                            setattr(self, write, sym)
                        return True

                for move_key, rect in self._move_buttons(offset).items():
                    if rect.collidepoint(event.pos):
                        if getattr(self, move) == move_key:
                            setattr(self, move, None)
                        else:
                            setattr(self, move, move_key)
                        return True

        return False

    def _commit(self):
        if not self.double_tape:
            self.on_save(list(self.selected_read1), self.selected_write1, self.selected_move1)
        else:
            self.on_save(
                list(self.selected_read1), self.selected_write1, self.selected_move1,
                list(self.selected_read2), self.selected_write2, self.selected_move2
            )

    def draw(self):
        shadow_rect = self.rect.inflate(10, 10)
        pygame.draw.rect(self.screen, (0, 0, 0, 80), shadow_rect, border_radius=14)
        self._draw_gradient_rect(self.rect, (25, 35, 65), (35, 45, 85))
        pygame.draw.rect(self.screen, COLORS["accent"], self.rect, 2, border_radius=12)

        title = self.font.render("Edit Connection Logic", True, COLORS["text"])
        self.screen.blit(title, (self.rect.centerx - title.get_width() // 2, self.rect.y + 15))

        self._draw_tape_section(1, 0)
        if self.double_tape:
            self._draw_tape_section(2, self.width // 2)

        self._draw_button(self.save_button, "Save", (90, 200, 120), hovered=(self.hovered_button == "save"))
        self._draw_button(self.cancel_button, "Cancel", (200, 80, 80), hovered=(self.hovered_button == "cancel"))

    def _draw_tape_section(self, tape_id, offset):
        reads = self.selected_read1 if tape_id == 1 else self.selected_read2
        write = self.selected_write1 if tape_id == 1 else self.selected_write2
        move = self.selected_move1 if tape_id == 1 else self.selected_move2

        label = self.font.render(f"Tape {tape_id}", True, COLORS["text"])
        self.screen.blit(label, (self.rect.x + offset + 20, self.rect.y + 40))

        rlabel = self.font.render("Read Symbols:", True, COLORS["text"])
        self.screen.blit(rlabel, (self.rect.x + offset + 40, self.rect.y + 70))
        start = self.page_index * self.symbols_per_page
        end = start + self.symbols_per_page
        visible_symbols = self.symbols[start:end]

        for i, sym in enumerate(visible_symbols):
            rect = self._symbol_rect(i, "read", offset)
            hovered = self.hovered_symbol == (tape_id, "read", sym)
            self._draw_option(rect, sym, sym in reads, hovered)

        show_arrows = len(self.symbols) > self.symbols_per_page
        left_arrow = right_arrow = None
        if show_arrows:
            left_arrow = pygame.Rect(self.rect.x + offset, self.rect.y + 100, 30, 30)
            right_arrow = pygame.Rect(self.rect.x + offset + 40 + self.symbols_per_page * 70, self.rect.y + 100, 30, 30)
            arrow_font = FontManager.get(20)
            if self.page_index > 0:
                pygame.draw.rect(self.screen, (90, 100, 130), left_arrow, border_radius=6)
                pygame.draw.rect(self.screen, COLORS["text"], left_arrow, 2, border_radius=6)
                la = arrow_font.render("<", True, (255, 255, 255))
                self.screen.blit(la,
                                 (left_arrow.centerx - la.get_width() // 2, left_arrow.centery - la.get_height() // 2))
            if (self.page_index + 1) * self.symbols_per_page < len(self.symbols):
                pygame.draw.rect(self.screen, (90, 100, 130), right_arrow, border_radius=6)
                pygame.draw.rect(self.screen, COLORS["text"], right_arrow, 2, border_radius=6)
                ra = arrow_font.render(">", True, (255, 255, 255))
                self.screen.blit(ra, (
                right_arrow.centerx - ra.get_width() // 2, right_arrow.centery - ra.get_height() // 2))
        if tape_id == 1:
            self._read_arrows_tape1 = (left_arrow, right_arrow)
        else:
            self._read_arrows_tape2 = (left_arrow, right_arrow)

        wlabel = self.font.render("Write Symbol:", True, COLORS["text"])
        self.screen.blit(wlabel, (self.rect.x + offset + 40, self.rect.y + 170))
        for i, sym in enumerate(visible_symbols):
            rect = self._symbol_rect(i, "write", offset)
            hovered = self.hovered_symbol == (tape_id, "write", sym)
            self._draw_option(rect, sym, sym == write, hovered)

        mlabel = self.font.render("Move Direction:", True, COLORS["text"])
        self.screen.blit(mlabel, (self.rect.x + offset + 40, self.rect.y + 270))
        for move_key, rect in self._move_buttons(offset).items():
            hovered = self.hovered_move == (tape_id, move_key)
            self._draw_option(rect, move_key, move_key == move, hovered)

    def _symbol_rect(self, index, section, offset=0):
        base_y = self.rect.y + (100 if section == "read" else 200)
        return pygame.Rect(
            self.rect.x + offset + 40 + index * 70,
            base_y,
            55,
            45,
        )

    def _move_buttons(self, offset=0):
        y = self.rect.y + 300
        x = self.rect.x + offset + 40
        return {
            "L": pygame.Rect(x, y, 80, 45),
            "R": pygame.Rect(x + 110, y, 80, 45),
            "S": pygame.Rect(x + 210, y, 80, 45),
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
        surf = pygame.Surface((rect.width, rect.height))
        for y in range(rect.height):
            ratio = y / rect.height
            r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
            g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
            b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
            pygame.draw.line(surf, (r, g, b), (0, y), (rect.width, y))
        self.screen.blit(surf, rect.topleft)
