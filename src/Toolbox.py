import pygame
from MainMenu import COLORS
from ToolCell import ToolCell


class Toolbox:
    def __init__(self, screen, on_tool_selected):
        self.screen = screen
        self.on_tool_selected = on_tool_selected
        self.current_tool = None
        self.font = pygame.font.SysFont("futura", 16, bold=True)

        self.is_open = False
        self.animation_progress = 0.0
        self.animation_speed = 6.0
        self.animation_locked = False

        self.toggle_button = pygame.Rect(20, 20, 50, 50)
        self.radius = 25
        self.spacing = 65
        self.tool_radius = 20

        def icon_node(s, x, y):
            pygame.draw.circle(s, COLORS["text"], (x, y), 6)

        def icon_end_node(s, x, y):
            pygame.draw.circle(s, COLORS["text"], (x, y), 8, 2)
            pygame.draw.circle(s, COLORS["text"], (x, y), 3)

        def icon_connect(s, x, y):
            pygame.draw.line(s, COLORS["text"], (x - 10, y), (x + 10, y), 3)
            pygame.draw.polygon(
                s, COLORS["text"], [(x + 10, y), (x + 4, y - 4), (x + 4, y + 4)]
            )

        def icon_delete(s, x, y):
            pygame.draw.line(s, COLORS["text"], (x - 6, y - 6), (x + 6, y + 6), 3)
            pygame.draw.line(s, COLORS["text"], (x + 6, y - 6), (x - 6, y + 6), 3)

        self.tools = [
            ToolCell("node", "Node", icon_node, self.tool_radius, self.font, self.select_tool),
            ToolCell("end_node", "End Node", icon_end_node, self.tool_radius, self.font, self.select_tool),
            ToolCell("connect", "Connect", icon_connect, self.tool_radius, self.font, self.select_tool),
            ToolCell("delete", "Delete", icon_delete, self.tool_radius, self.font, self.select_tool),
        ]

        self.bg_color = (45, 55, 85)
        self.border_color = COLORS["accent"]
        self.hover_label_alpha = 0
        self.hover_label_tool = None

    def update(self, dt):
        target = 1.0 if self.is_open else 0.0
        if abs(self.animation_progress - target) > 0.01:
            self.animation_locked = True
            step = self.animation_speed * dt * (1 if self.is_open else -1)
            self.animation_progress = max(0.0, min(1.0, self.animation_progress + step))
        else:
            self.animation_locked = False

        for tool in self.tools:
            tool.active = (tool.tool_name == self.current_tool)

        if self.hover_label_tool:
            self.hover_label_alpha = min(255, self.hover_label_alpha + 400 * dt)
        else:
            self.hover_label_alpha = max(0, self.hover_label_alpha - 400 * dt)

    def draw(self):
        cx, cy = self.toggle_button.center

        pygame.draw.circle(self.screen, self.bg_color, (cx, cy), self.radius)
        pygame.draw.circle(self.screen, self.border_color, (cx, cy), self.radius, 2)

        if not self.is_open:
            pygame.draw.line(self.screen, COLORS["text"], (cx - 8, cy), (cx + 8, cy), 3)
            pygame.draw.line(self.screen, COLORS["text"], (cx, cy - 8), (cx, cy + 8), 3)
        else:
            pygame.draw.line(self.screen, COLORS["text"], (cx - 8, cy), (cx + 8, cy), 3)

        if self.animation_progress > 0:
            total_height = self.spacing * len(self.tools)
            visible_height = total_height * self.animation_progress
            rect_y = cy + self.radius - (self.radius * (1 - self.animation_progress))
            rect = pygame.Rect(cx - self.radius, rect_y, self.radius * 2, visible_height)

            pygame.draw.rect(self.screen, self.bg_color, rect, border_radius=self.radius)
            pygame.draw.rect(self.screen, self.border_color, rect, 2, border_radius=self.radius)

            for i in range(1, len(self.tools)):
                line_y = rect_y + i * self.spacing * self.animation_progress
                pygame.draw.line(
                    self.screen,
                    (70, 90, 120),
                    (cx - self.radius + 8, line_y),
                    (cx + self.radius - 8, line_y),
                    1,
                )

            for i, tool in enumerate(self.tools):
                offset_y = int((i + 0.5) * self.spacing * self.animation_progress)
                tool.set_position((cx, rect_y + offset_y))
                tool.draw(self.screen)

            if self.hover_label_tool and self.hover_label_alpha > 0:
                label = self.hover_label_tool.label
                surf = self.font.render(label, True, COLORS["text"])
                surf.set_alpha(int(self.hover_label_alpha))
                label_x = cx + self.radius + 15
                label_y = self.hover_label_tool.center[1] - surf.get_height() // 2
                self.screen.blit(surf, (label_x, label_y))

    def handle_event(self, event):
        if self.animation_locked:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.toggle_button.collidepoint(event.pos):
                self.is_open = not self.is_open
                self.hover_label_tool = None
                return True

        hovered_tool = None
        if self.is_open and self.animation_progress > 0.2:
            for tool in self.tools:
                if tool.handle_event(event):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.is_open = False
                        self.hover_label_tool = None
                        return True
                if tool.hovered:
                    hovered_tool = tool

        self.hover_label_tool = hovered_tool
        return False

    def select_tool(self, tool_name):
        self.current_tool = None if self.current_tool == tool_name else tool_name
        self.on_tool_selected(self.current_tool or "select")
        if self.current_tool == "node":
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif self.current_tool == "end_node":
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
        elif self.current_tool == "connect":
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEWE)
        elif self.current_tool == "delete":
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_NO)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
