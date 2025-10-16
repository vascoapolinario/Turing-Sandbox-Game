import pygame
from MainMenu import COLORS


class ToolCell:
    def __init__(self, tool_name, label, icon_func, radius, font, on_select):
        self.tool_name = tool_name
        self.label = label
        self.icon_func = icon_func
        self.radius = radius
        self.font = font
        self.on_select = on_select
        self.center = (0, 0)
        self.active = False
        self.hovered = False

    def set_position(self, pos):
        self.center = pos

    def draw(self, screen):
        cx, cy = self.center
        color = COLORS["accent"] if self.active else (70, 80, 110)
        outline_color = COLORS["hover"] if self.hovered or self.active else COLORS["text"]

        pygame.draw.circle(screen, color, (cx, cy), self.radius)
        pygame.draw.circle(screen, outline_color, (cx, cy), self.radius, 2)

        self.icon_func(screen, cx, cy)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            dist = ((event.pos[0] - self.center[0]) ** 2 + (event.pos[1] - self.center[1]) ** 2) ** 0.5
            self.hovered = dist <= self.radius
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            dist = ((event.pos[0] - self.center[0]) ** 2 + (event.pos[1] - self.center[1]) ** 2) ** 0.5
            if dist <= self.radius:
                self.on_select(self.tool_name)
                return True
        return False
