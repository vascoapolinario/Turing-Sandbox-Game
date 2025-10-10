import pygame

from Node import Node
from Tape import Tape
from MainMenu import COLORS
from Toolbox import Toolbox
from Grid import Grid
from Connection import Connection

class Environment:
    def __init__(self, screen):
        self.screen = screen
        self.tape = Tape(screen)
        self.running = True
        self.toolbox = Toolbox(screen, self.on_tool_selected)
        self.grid = Grid(screen)

        self.nodes = []
        self.connections = []

        self.current_tool = None
        self.connecting_from = None
        self.mouse_pos = pygame.Vector2(0, 0)

    def update(self, dt):
        self.tape.update(dt)
        self.toolbox.update(dt)
        for node in self.nodes:
            node.update(dt) if hasattr(node, "update") else None

    def on_tool_selected(self, tool_name):
        print(f"Tool selected: {tool_name}")
        self.current_tool = tool_name
        self.connecting_from = None
        self.toolbox.draw()

    def draw(self):
        self.screen.fill(COLORS["background"])
        self.grid.draw()

        for conn in self.connections:
            conn.draw(self.screen)
        for node in self.nodes:
            node.draw(self.screen)
        if self.current_tool == "connect" and self.connecting_from is not None:
            self._draw_preview_connection()

        self.tape.draw()
        self.toolbox.draw()

    def handle_event(self, event):
        toolbox_used = self.toolbox.handle_event(event)
        if toolbox_used:
            return

        if event.type == pygame.MOUSEMOTION:
            self.mouse_pos = pygame.Vector2(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.current_tool in ("node", "end_node"):
                if not self.toolbox.toggle_button.collidepoint(event.pos):
                    snapped_pos = getattr(self, "grid", None)
                    if snapped_pos:
                        pos = self.grid.snap(event.pos)
                    else:
                        pos = event.pos
                    if len(self.nodes) == 0:
                        new_node = Node(pos, is_start=True, is_end=False)
                        print("Created start node (q0).")
                    else:
                        new_node = Node(pos, is_end=(self.current_tool == "end_node"))
                    self.nodes.append(new_node)
                    return

            elif self.current_tool == "connect":
                clicked_node = self._get_node_at(event.pos)
                if clicked_node:
                    if self.connecting_from is None:
                        self.connecting_from = clicked_node
                        print(f"Starting connection from {clicked_node.id}")
                    else:
                        start_node = self.connecting_from
                        end_node = clicked_node
                        self._create_connection(start_node, end_node)
                        print(f"Created connection: {start_node.id} -> {end_node.id}")
                        self.connecting_from = None
                    return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            if self.connecting_from is not None:
                print("Connection cancelled with right click.")
                self.connecting_from = None
                return

        for node in self.nodes:
            node.handle_event(event)

    def _get_node_at(self, pos):
        for node in reversed(self.nodes):
            if node.is_inside(pos):
                return node
        return None

    def _create_connection(self, start_node, end_node):
        conn = Connection(start_node, end_node)
        self.connections.append(conn)
        start_node.add_connection(conn)

    def _connection_exists(self, start_node, end_node):
        for c in self.connections:
            if c.start == start_node and c.end == end_node:
                return True
        return False

    def _draw_preview_connection(self):
        start = self.connecting_from.pos
        end = self.mouse_pos

        mid = (start + end) / 2
        direction = (end - start)
        if direction.length() == 0:
            return
        normal = pygame.Vector2(-direction.y, direction.x).normalize()
        control = mid + normal * 60

        points = []
        for t in [i / 20 for i in range(21)]:
            p = (1 - t) ** 2 * start + 2 * (1 - t) * t * control + t ** 2 * end
            points.append(p)

        pygame.draw.lines(self.screen, (180, 180, 180), False, points, 2)
        pygame.draw.circle(self.screen, (230, 230, 230), end, 4)