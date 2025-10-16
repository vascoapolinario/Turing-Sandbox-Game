import pygame

COLORS = {
        "background": (25, 25, 35),
        "accent": (120, 180, 255),
        "hover": (180, 220, 255),
        "button": (40, 60, 90),
        "text": (255, 255, 255)
    }


class Button:

    def __init__(self, text, rect, font, callback):
        self.text = text
        self.original_rect = rect
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.font = font
        self.callback = callback
        self.hovered = False
        self.update_rect(pygame.display.get_surface().get_size())

    def update_rect(self, screen_size):
        w, h = screen_size
        rx, ry, rw, rh = self.original_rect

        if all(0 < val <= 1 for val in (rx, ry, rw, rh)):
            x = int(rx * w)
            y = int(ry * h)
            width = int(rw * w)
            height = int(rh * h)
        else:
            x, y, width, height = int(rx), int(ry), int(rw), int(rh)

        self.rect = pygame.Rect(x, y, width, height)

    def update_rect_withscale(self, screen_size):
        w, h = screen_size
        rx, ry, rw, rh = self.original_rect

        if all(0 < rx <= 1 for rx in (rx, ry)):
            x = int(rx * w)
            y = int(ry * h)
        else:
            x, y = int(rx), int(ry)

        width = int(rw if rw > 1 else rw * 900)
        height = int(rh if rh > 1 else rh * 600)

        self.rect = pygame.Rect(x, y, width, height)


    def draw(self, screen):
        color = COLORS["hover"] if self.hovered else COLORS["button"]
        pygame.draw.rect(screen, color, self.rect, border_radius=12)
        pygame.draw.rect(screen, (70, 90, 120), self.rect, 2, border_radius=12)

        label = self.font.render(self.text, True, COLORS["text"])
        label_rect = label.get_rect(center=self.rect.center)
        screen.blit(label, label_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hovered:
            self.callback()