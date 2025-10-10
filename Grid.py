import pygame


class Grid:
    def __init__(self, screen, spacing=130, color=(70, 70, 80)):
        self.screen = screen
        self.spacing = spacing
        self.color = color
        self.enabled = True

    def draw(self):
        if not self.enabled:
            return

        w, h = self.screen.get_size()
        for x in range(0, w, self.spacing):
            pygame.draw.line(self.screen, self.color, (x, 0), (x, h), 1)
        for y in range(0, h, self.spacing):
            pygame.draw.line(self.screen, self.color, (0, y), (w, y), 1)

    def snap(self, pos):
        x, y = pos
        snapped_x = round(x / self.spacing) * self.spacing
        snapped_y = round(y / self.spacing) * self.spacing
        return pygame.Vector2(snapped_x, snapped_y)