import pygame
from Button import COLORS
from FontManager import FontManager


class Node:
    _id_counter = 0

    def __init__(self, pos, is_end=False, is_start=False):
        self.id = Node._id_counter
        Node._id_counter += 1

        self.pos = pygame.Vector2(pos)
        self.radius = 35
        self.is_end = is_end
        self.is_start = is_start
        self.is_active = False

        self.connections = []
        self.selected = False
        self.hovered = False
        self.dragging = False
        self.drag_offset = pygame.Vector2(0, 0)

        self.base_color = COLORS["accent"]
        self.start_color = (80, 200, 120)
        self.end_color = (200, 80, 80)
        self.hover_color = COLORS["hover"]
        self.text_color = COLORS["text"]
        self.font_size = 35

    def draw(self, screen, grid=None):
        draw_pos = self.pos
        radius = self.radius * grid.zoom
        size = int(self.font_size * grid.zoom) if grid else self.font_size
        font = FontManager.get(size)
        if grid:
            draw_pos = grid.world_to_screen(self.pos)

        if self.is_start and not self.is_active:
            color = self.start_color
        elif self.is_end and not self.is_active:
            color = self.end_color
        elif self.is_active:
            color = (255, 220, 70)
        else:
            color = self.base_color

        if self.selected:
            pygame.draw.circle(screen, self.hover_color, draw_pos, radius + 4)
        elif self.hovered:
            pygame.draw.circle(screen, self.hover_color, draw_pos, radius + 2)

        pygame.draw.circle(screen, color, draw_pos, radius)
        pygame.draw.circle(screen, self.text_color, draw_pos, radius, 2)

        text = font.render(f"q{self.id}", True, self.text_color)
        text_rect = text.get_rect(center=draw_pos)
        screen.blit(text, text_rect)

        if self.is_end:
            pygame.draw.circle(screen, self.text_color, draw_pos, radius - 5, 2)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.is_inside(event.pos)
            if self.dragging:
                mouse_pos = pygame.Vector2(event.pos)
                self.pos = mouse_pos - self.drag_offset

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_inside(event.pos):
                self.selected = True
                self.dragging = True
                self.drag_offset = pygame.Vector2(event.pos) - self.pos
                return True
            else:
                self.selected = False

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False

        return False

    def add_connection(self, connection):
        self.connections.append(connection)

    def remove_connection(self, connection):
        if connection in self.connections:
            self.connections.remove(connection)

    def is_inside(self, pos, grid=None):
        if grid:
            pos = grid.screen_to_world(pos)
        dx = pos[0] - self.pos.x
        dy = pos[1] - self.pos.y
        return (dx * dx + dy * dy) <= (self.radius ** 2)
