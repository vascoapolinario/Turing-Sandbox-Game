import math

import pygame


class Grid:
    def __init__(self, screen, spacing=130, color=(70, 70, 80)):
        self.screen = screen
        self.base_spacing = spacing
        self.color = color
        self.enabled = True

        self.offset = pygame.Vector2(0, 0)
        self.zoom = 1.0
        self.min_zoom = 0.4
        self.max_zoom = 2.0
        self.move_speed = 600
        self.zoom_speed = 0.1

    def handle_input(self, dt, keys):
        move = pygame.Vector2(0, 0)
        speed = self.move_speed * dt / self.zoom

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move.y -= speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move.y += speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move.x -= speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move.x += speed

        self.offset += move

    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            mouse_before = self.screen_to_world(pygame.mouse.get_pos())
            self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom + event.y * self.zoom_speed))
            mouse_after = self.screen_to_world(pygame.mouse.get_pos())
            self.offset += mouse_before - mouse_after

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.reset_view()

    def reset_view(self):
        self.offset = pygame.Vector2(0, 0)
        self.zoom = 1.0

    def draw(self):
        if not self.enabled:
            return

        w, h = self.screen.get_size()
        z = self.zoom
        center = pygame.Vector2(w / 2, h / 2)

        world_left = self.offset.x - center.x / z
        world_right = world_left + w / z
        world_top = self.offset.y - center.y / z
        world_bottom = world_top + h / z

        kx_start = math.floor(world_left / self.base_spacing)
        kx_end = math.floor(world_right / self.base_spacing) + 1
        for k in range(kx_start, kx_end + 1):
            xw = k * self.base_spacing
            xs = (xw - self.offset.x) * z + center.x
            pygame.draw.line(self.screen, self.color, (xs, 0), (xs, h), 1)

        ky_start = math.floor(world_top / self.base_spacing)
        ky_end = math.floor(world_bottom / self.base_spacing) + 1
        for k in range(ky_start, ky_end + 1):
            yw = k * self.base_spacing
            ys = (yw - self.offset.y) * z + center.y
            pygame.draw.line(self.screen, self.color, (0, ys), (w, ys), 1)

    def world_to_screen(self, pos):
        center = pygame.Vector2(self.screen.get_width() / 2, self.screen.get_height() / 2)
        return (pos - self.offset) * self.zoom + center

    def screen_to_world(self, pos):
        center = pygame.Vector2(self.screen.get_width() / 2, self.screen.get_height() / 2)
        return (pygame.Vector2(pos) - center) / self.zoom + self.offset

    def snap(self, world_pos):
        snapped_x = round(world_pos.x / self.base_spacing) * self.base_spacing
        snapped_y = round(world_pos.y / self.base_spacing) * self.base_spacing
        return pygame.Vector2(snapped_x, snapped_y)
