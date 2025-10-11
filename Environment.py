import pygame

from Node import Node
from Tape import Tape
from MainMenu import COLORS
from Toolbox import Toolbox
from Grid import Grid
from Connection import Connection
from ConnectionWindow import ConnectionWindow
from TuringMachine import TuringMachine

class Environment:
    def __init__(self, screen):
        self.alphabet = ['0', '1', '_']
        self.screen = screen
        self.tape = Tape(screen)
        self.running = True
        self.toolbox = Toolbox(screen, self.on_tool_selected)
        self.grid = Grid(screen)
        self.connection_window = None

        self.nodes = []
        self.connections = []
        self.TuringMachine = TuringMachine(screen, self.nodes, self.connections, self.tape)

        self.current_tool = None
        self.connecting_from = None
        self.mouse_pos = pygame.Vector2(0, 0)

    def update(self, dt):
        self.TuringMachine.update(dt)
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

        self.TuringMachine.draw()

        if self.connection_window:
            self.connection_window.draw()

        self.tape.draw()
        self.toolbox.draw()

    def handle_event(self, event):
        toolbox_used = self.toolbox.handle_event(event)
        if toolbox_used:
            return

        if self.connection_window:
            self.connection_window.handle_event(event)
            return

        self.TuringMachine.handle_event(event)

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
                    if self._get_node_at(pos):
                        return
                    if len(self.nodes) == 0 or (any(n.is_start for n in self.nodes) == False and self.current_tool == "node"):
                        new_node = Node(pos, is_start=True, is_end=False)
                        new_node.id = 0
                        self._sync_machine()
                    else:
                        new_node = Node(pos, is_end=(self.current_tool == "end_node"))
                    self.nodes.append(new_node)
                    self._sync_machine()
                    return

            elif self.current_tool == "connect":
                clicked_node = self._get_node_at(event.pos)
                if clicked_node:
                    if self.connecting_from is None:
                        self.connecting_from = clicked_node
                    else:
                        start_node = self.connecting_from
                        end_node = clicked_node
                        self._create_connection(start_node, end_node)
                        self.connecting_from = None
                    return

            elif self.current_tool == "delete":
                self._handle_delete(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            if self.connecting_from is not None:
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
        if self._connection_exists(start_node, end_node):
            return
        conn = Connection(start_node, end_node)
        self.connections.append(conn)
        start_node.add_connection(conn)
        self._sync_machine()

        self.connection_window = ConnectionWindow(
            self.screen,
            conn,
            symbols=self.alphabet,
            on_save=self._save_connection_logic,
            on_cancel=lambda: self._cancel_connection_window(conn)
        )

    def _connection_exists(self, start_node, end_node):
        for c in self.connections:
            if c.start == start_node and c.end == end_node:
                return True
        return False

    def _save_connection_logic(self, read, write, move):
        if self.connection_window:
            if not read or not move:
                self._cancel_connection_window(self.connection_window.connection)
                return
            for conn in self.connections:
                if (conn.start == self.connection_window.connection.start and
                    conn != self.connection_window.connection and
                    any(sym in conn.read for sym in read)):
                    self._cancel_connection_window(self.connection_window.connection)
                    return
            self.connection_window.connection.update_logic(read, write, move)
            self._sync_machine()
            self.connection_window = None

    def _cancel_connection_window(self, conn):
        if conn in self.connections:
            self.connections.remove(conn)
            self._sync_machine()
        self.connection_window = None


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

    def _handle_delete(self, pos):
        node = self._get_node_at(pos)
        if node:
            print(f"Deleting node {node.id}")
            self._delete_node(node)
            self._sync_machine()
            return

        for conn in self.connections:
            if conn.is_clicked(pos):
                print(f"Deleting connection {conn.start.id} -> {conn.end.id}")
                self.connections.remove(conn)
                self._sync_machine()
                return

    def _delete_node(self, node):
        self.nodes.remove(node)
        if Node._id_counter > 0 and node.id != 0:
            Node._id_counter -= 1
            for n in self.nodes:
                if n.id > node.id:
                    n.id -= 1
        self.connections = [c for c in self.connections if c.start != node and c.end != node]
        self._sync_machine()

    def _sync_machine(self):
        self.TuringMachine.nodes = self.nodes
        self.TuringMachine.connections = self.connections
        if self.TuringMachine.current_node not in self.nodes and len(self.nodes) > 0:
            self.TuringMachine.current_node = next((n for n in self.nodes if getattr(n, "is_start", False)), None)
