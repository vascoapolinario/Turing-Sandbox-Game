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
        if isinstance(self.original_rect, tuple) and all(0 < v <= 1 for v in self.original_rect):
            w, h = screen_size
            rel_x, rel_y, rel_w, rel_h = self.original_rect
            self.rect = pygame.Rect(int(w * rel_x), int(h * rel_y), int(w * rel_w), int(h * rel_h))

    def draw(self, screen):
        color = COLORS["hover"] if self.hovered else COLORS["button"]
        pygame.draw.rect(screen, color, self.rect, border_radius=12)

        label = self.font.render(self.text, True, COLORS["text"])
        label_rect = label.get_rect(center=self.rect.center)
        screen.blit(label, label_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hovered:
            self.callback()