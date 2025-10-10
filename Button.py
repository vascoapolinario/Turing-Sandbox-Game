import pygame

COLORS = {
        "background": (25, 25, 35),
        "accent": (120, 180, 255),
        "hover": (180, 220, 255),
        "button": (40, 60, 90),
        "text": (255, 255, 255)
    }


class Button:

    def __init__(self, text, rel_rect, font, callback):
        self.text = text
        self.rel_rect = rel_rect
        self.font = font
        self.callback = callback
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.hovered = False

    def update_rect(self, screen_size):
        sw, sh = screen_size
        rx, ry, rw, rh = self.rel_rect
        self.rect = pygame.Rect(int(rx * sw), int(ry * sh), int(rw * sw), int(rh * sh))

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