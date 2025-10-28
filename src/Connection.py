import pygame
import math
from MainMenu import COLORS
from FontManager import FontManager


class Connection:
    def __init__(self, start_node, end_node, read=None, write=None, move=None, read2=None, write2=None, move2=None):
        self.start = start_node
        self.end = end_node

        self.read = read if read is not None else []
        self.write = write
        self.move = move

        self.read2 = [] if read2 is None else read2
        self.write2 = write2
        self.move2 = move2
        self.label_offset = 0

        self.color = COLORS["text"]
        self.thickness = 3
        self.curvature = 60
        self.arrow_size = 10
        self.font = FontManager.get(18)

    def draw(self, screen, grid):
        start_world = self.start.pos
        end_world = self.end.pos

        if self.start == self.end:
            self._draw_self_loop(screen, grid)
        else:
            self._draw_curve(screen, grid, start_world, end_world)

    def _draw_curve(self, screen, grid, start_world, end_world):
        mid = (start_world + end_world) / 2
        direction = (end_world - start_world)
        if direction.length() == 0:
            return
        normal = pygame.Vector2(-direction.y, direction.x).normalize()
        control_world = mid + normal * self.curvature

        world_points = []
        for t in [i / 30 for i in range(31)]:
            p = (1 - t) ** 2 * start_world + 2 * (1 - t) * t * control_world + t ** 2 * end_world
            world_points.append(p)

        screen_points = [grid.world_to_screen(p) for p in world_points]

        pygame.draw.lines(screen, self.color, False, screen_points, self.thickness)

        mid_index = len(screen_points) // 2
        prev_mid = screen_points[mid_index - 1]
        mid_point = screen_points[mid_index]
        self._draw_arrowhead(screen, mid_point, prev_mid, color=(180, 220, 255))

        label_text = self._make_label_text()
        if label_text:
            label_surface = self.font.render(label_text, True, COLORS["text"])

            offset_dir = (grid.world_to_screen(control_world) - mid_point)
            if offset_dir.length() > 0:
                base_offset = offset_dir.normalize() * 20
            else:
                base_offset = pygame.Vector2(0, -20)

            offset_index = getattr(self, "offset_index", 0)
            total_between = getattr(self, "total_between_same", 1)

            vertical_offset = (offset_index - (total_between - 1) / 2) * 18
            offset = base_offset + pygame.Vector2(0, vertical_offset)

            label_rect = label_surface.get_rect(center=(mid_point + offset))
            label_rect.y += self.label_offset
            screen.blit(label_surface, label_rect)

    def _draw_self_loop(self, screen, grid):
        pos_world = self.start.pos
        r = self.start.radius
        offset = 25
        gap = 10

        start = pygame.Vector2(pos_world.x, pos_world.y - r)
        top = pygame.Vector2(start.x, start.y - offset)
        left = pygame.Vector2(start.x - r - gap, start.y - offset)
        bottom = pygame.Vector2(left.x, pos_world.y - r / 2)
        world_points = [start, top, left, bottom, pos_world]

        screen_points = [grid.world_to_screen(p) for p in world_points]

        pygame.draw.lines(screen, self.color, False, screen_points, self.thickness)

        label_text = self._make_label_text()
        if label_text:
            label_surface = self.font.render(label_text, True, COLORS["text"])
            sx, sy = grid.world_to_screen(pygame.Vector2(left.x + (start.x - left.x) / 2, top.y - 15))
            label_rect = label_surface.get_rect(center=(sx, sy))
            label_rect.y -= self.label_offset
            screen.blit(label_surface, label_rect)

    def _draw_arrowhead(self, screen, prev, end, color=None):
        if color is None:
            color = self.color
        direction = (end - prev)
        if direction.length() == 0:
            return
        direction = direction.normalize()
        scale = 1.6
        left = direction.rotate(150) * (self.arrow_size * scale)
        right = direction.rotate(-150) * (self.arrow_size * scale)
        points = [end, end - left, end - right]
        pygame.draw.polygon(screen, color, points)

    def _make_label_text(self):
        def make_label(read, write, move):
            if not read and not write and not move:
                return ""
            read_part = ",".join(read) if isinstance(read, list) else (str(read) if read is not None else "")
            label = f"{read_part}"
            if write:
                label += f" -> {write}"
            if move:
                label += f", {move}"
            return label

        label1 = make_label(self.read, self.write, self.move)
        label2 = make_label(self.read2, self.write2, self.move2)
        if label1 and label2:
            return f"{label1} || {label2}"
        return label1 or label2 or ""

    def update_logic(self, read=None, write=None, move=None, read2=None, write2=None, move2=None):
        if read is not None:
            self.read = read
        if write is not None:
            self.write = write
        if move is not None:
            self.move = move
        if read2 is not None:
            self.read2 = read2
        if write2 is not None:
            self.write2 = write2
        if move2 is not None:
            self.move2 = move2

    def is_clicked(self, pos, grid, tolerance=8):
        start_world = self.start.pos
        end_world = self.end.pos

        if self.start == self.end:
            r = self.start.radius + 20
            loop_rect = pygame.Rect(
                start_world.x - r, start_world.y - r * 2, r * 2, r * 2
            )
            return loop_rect.collidepoint(grid.screen_to_world(pos))

        mid = (start_world + end_world) / 2
        direction = (end_world - start_world)
        if direction.length() == 0:
            return False
        normal = pygame.Vector2(-direction.y, direction.x).normalize()
        control = mid + normal * self.curvature

        click_world = grid.screen_to_world(pos)
        for t in [i / 30 for i in range(31)]:
            p = (1 - t) ** 2 * start_world + 2 * (1 - t) * t * control + t ** 2 * end_world
            if (p - click_world).length() <= tolerance / grid.zoom:
                return True
        return False

    @classmethod
    def from_dict(cls, conn_data, nodes):
        start_node = next((n for n in nodes if n.id == conn_data["start_id"]), None)
        end_node = next((n for n in nodes if n.id == conn_data["end_id"]), None)
        if not start_node or not end_node:
            return None

        connection = cls(
            start_node=start_node,
            end_node=end_node,
            read=conn_data.get("read", []),
            write=conn_data.get("write"),
            move=conn_data.get("move"),
            read2=conn_data.get("read2", []),
            write2=conn_data.get("write2"),
            move2=conn_data.get("move2")
        )
        return connection

    def to_dict(self):
        return {
            "start_id": self.start.id,
            "end_id": self.end.id,
            "read": self.read,
            "write": self.write,
            "move": self.move,
            "read2": self.read2,
            "write2": self.write2,
            "move2": self.move2
        }
