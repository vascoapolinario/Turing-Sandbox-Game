import pygame
from MainMenu import COLORS
from FontManager import FontManager


class TuringMachine:
    def __init__(self, screen, nodes, connections, tape, tape2=None, double_tape=False):
        self.screen = screen
        self.nodes = nodes
        self.connections = connections
        self.tape = tape
        self.double_tape = double_tape
        self.tape2 = tape2 if (double_tape and tape2) else None

        self.input_active = False
        self.input_text = ""
        self.alphabet = ['0', '1', '_']

        self.current_node = next((n for n in nodes if getattr(n, "is_start", False)), None)
        if self.current_node:
            self.current_node.is_active = True

        self.running = False
        self.paused = True
        self.finished = False
        self.timer = 0
        self.step_delay = 0.8

        self.target_width = 260
        self.current_width = 0
        self.height = 300
        self.animation_speed = 480
        self.open = False

        self.font = FontManager.get(24)
        self.small_font = FontManager.get(18, bold=False)

        self.buttons = {}
        self.hovered_button = None
        self.toggle_rect = None
        self.toggle_hovered = False


    def update(self, dt):
        target = self.target_width if self.open else 0
        if abs(self.current_width - target) > 1:
            direction = 1 if self.open else -1
            self.current_width = max(0, min(self.target_width, self.current_width + direction * self.animation_speed * dt))
        else:
            self.current_width = target

        if self.running and not self.paused and not self.finished:
            self.timer += dt
            if self.timer >= self.step_delay:
                self.step()
                self.timer = 0
    def step(self):
        if not self.current_node:
            self.finished = True
            return

        if getattr(self.current_node, "is_end", False):
            self.finished = True
            self.running = False
            return

        s1 = self.tape.read_symbol()
        s2 = self.tape2.read_symbol() if self.double_tape and self.tape2 else None

        valid_conn = None
        for conn in self.connections:
            if conn.start is not self.current_node:
                continue

            if self.double_tape and self.tape2:
                if s1 in conn.read and (not conn.read2 or s2 in conn.read2):
                    valid_conn = conn
                    break
            else:
                if s1 in conn.read:
                    valid_conn = conn
                    break

        if not valid_conn:
            self.finished = True
            self.running = False
            return

        if valid_conn.write:
            self.tape.write_symbol(valid_conn.write)
        if self.double_tape and valid_conn.write2 and self.tape2:
            self.tape2.write_symbol(valid_conn.write2)

        if valid_conn.move == "L":
            self.tape.move_left()
        elif valid_conn.move == "R":
            self.tape.move_right()
        if self.double_tape and self.tape2:
            if valid_conn.move2 == "L":
                self.tape2.move_left()
            elif valid_conn.move2 == "R":
                self.tape2.move_right()

        self.current_node.is_active = False
        self.current_node = valid_conn.end
        self.current_node.is_active = True

        self.tape.show()
        if self.double_tape and self.tape2:
            self.tape2.show()

        if getattr(self.current_node, "is_end", False):
            self.finished = True
            self.running = False

    def play(self):
        if not self.current_node:
            return
        if self.finished:
            self.reset()
        self.running = True
        self.paused = False
        self.current_node.is_active = True
        self.tape.show()
        if self.double_tape and self.tape2:
            self.tape2.show()

    def pause(self):
        if self.running:
            self.paused = not self.paused

    def reset(self):
        self.current_node = next((n for n in self.nodes if getattr(n, "is_start", False)), None)
        for n in self.nodes:
            n.is_active = False
        if self.current_node:
            self.current_node.is_active = False
        self.tape.reset()
        if self.double_tape and self.tape2:
            self.tape2.reset()
            self.tape2.change_tape("")
        self.finished = False
        self.running = False
        self.paused = True

    def draw(self):
        sw, sh = self.screen.get_size()

        pill_w, pill_h = 26, 70
        pill_x = sw - 10 - pill_w
        pill_y = sh // 2 - pill_h // 2
        self.toggle_rect = pygame.Rect(pill_x, pill_y, pill_w, pill_h)

        shadow = self.toggle_rect.move(-2, 2)
        pygame.draw.rect(self.screen, (0,0,0,90), shadow, border_radius=12)
        pygame.draw.rect(self.screen, (45, 55, 85), self.toggle_rect, border_radius=12)
        pygame.draw.rect(self.screen, COLORS["accent"], self.toggle_rect, 2, border_radius=12)

        cx = self.toggle_rect.centerx
        cy = self.toggle_rect.centery
        if self.open:
            pygame.draw.polygon(self.screen, COLORS["text"], [(cx+4,cy), (cx-4,cy-8), (cx-4,cy+8)])
        else:
            pygame.draw.polygon(self.screen, COLORS["text"], [(cx-4,cy), (cx+4,cy-8), (cx+4,cy+8)])

        if self.current_width <= 4:
            return

        panel_y = sh / 2 - self.height / 2
        target_x = sw - self.target_width - self.toggle_rect.width - 8
        start_x = sw
        open_ratio = self.current_width / self.target_width if self.target_width > 0 else 0
        panel_x = start_x - (start_x - target_x) * open_ratio

        rect = pygame.Rect(panel_x, panel_y, self.target_width, self.height)
        shadow = rect.move(-5, 5)
        pygame.draw.rect(self.screen, (0, 0, 0, 100), shadow, border_radius=16)
        pygame.draw.rect(self.screen, (30, 35, 60), rect, border_radius=16)
        pygame.draw.rect(self.screen, COLORS["accent"], rect, 2, border_radius=16)

        title = self.font.render("Turing Machine", True, COLORS["text"])
        self.screen.blit(title, (rect.centerx - title.get_width() // 2, rect.y + 15))

        status = "Stopped" if not self.running else ("Paused" if self.paused else "Running")
        status_color = (220,120,80) if status=="Paused" else (120,220,120) if status=="Running" else (200,200,200)
        state_label = self.small_font.render(f"State: {status}", True, status_color)
        node_text = f"Current: q{self.current_node.id}" if self.current_node else "Current: —"
        node_label = self.small_font.render(node_text, True, COLORS["text"])
        self.screen.blit(state_label, (rect.x + 22, rect.y + 68))
        self.screen.blit(node_label, (rect.x + 22, rect.y + 96))

        bx = rect.x + 22
        by = rect.y + 145
        spacing = 90
        self.buttons = {
            "play_pause": pygame.Rect(bx, by, 88, 40),
            "step": pygame.Rect(bx + spacing, by, 88, 40),
            "reset": pygame.Rect(bx, by + 58, 88, 40),
            "Show/Hide Tape": pygame.Rect(bx + spacing, by + 58, 120, 40),
            "Test Word": pygame.Rect(bx, by + 100, 188, 40),
        }
        for name, r in self.buttons.items():
            hovered = (self.hovered_button == name)
            self._draw_button(r, name, hovered)

        if self.input_active:
            self._draw_input_box()

    def handle_event(self, event):
        if self.input_active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.tape.change_tape(self.input_text)
                    self.input_active = False
                elif event.key == pygame.K_ESCAPE:
                    self.input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                elif (event.unicode.upper() in self.alphabet) and len(self.input_text) < 30:
                    self.input_text += event.unicode.upper()
                else:
                    return

        if event.type == pygame.MOUSEMOTION:
            self.hovered_button = None
            self.toggle_hovered = self.toggle_rect and self.toggle_rect.collidepoint(event.pos)
            for name, rect in self.buttons.items():
                if rect.collidepoint(event.pos):
                    self.hovered_button = name
                    break

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.toggle_rect and self.toggle_rect.collidepoint(event.pos):
                self.open = not self.open
                return

            if self.open and self.current_width > 10:
                for name, rect in self.buttons.items():
                    if rect.collidepoint(event.pos):
                        if name == "play_pause":
                            if not self.running:
                                self.play()
                            else:
                                self.pause()
                        elif name == "step":
                            self.step()
                        elif name == "reset":
                            self.reset()
                        elif name == "Show/Hide Tape":
                            if self.tape.visible:
                                self.tape.hide()
                                if self.double_tape and self.tape2:
                                    self.tape2.hide()
                            else:
                                self.tape.show()
                                if self.double_tape and self.tape2:
                                    self.tape2.show()
                        elif name == "Test Word":
                            self.input_active = True
                            self.input_text = ""
                            return
                        return

    def _draw_button(self, rect, name, hovered):
        if name == "play_pause":
            label = "Play" if (not self.running or self.paused) else "Pause"
            base = (90, 200, 110)
        elif name == "step":
            label = "Step"
            base = (100, 130, 220)
        elif name == "Show/Hide Tape":
            label = "Hide Tapes" if self.tape.visible else "Show Tapes"
            base = (120, 100, 200)
        elif name == "Test Word":
            label = "Set Tape Word"
            base = (90, 160, 220)
        else:
            label = "Reset"
            base = (200, 90, 90)

        color = tuple(min(255, c + 40) for c in base) if hovered else base
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        pygame.draw.rect(self.screen, (25, 25, 25), rect, 2, border_radius=10)

        text = self.small_font.render(label, True, (255, 255, 255))
        self.screen.blit(text, (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2))

    def _draw_input_box(self):
        sw, sh = self.screen.get_size()
        box_w, box_h = 400, 150
        box_x = sw / 2 - box_w / 2
        box_y = sh / 2 - box_h / 2
        rect = pygame.Rect(box_x, box_y, box_w, box_h)

        shadow = rect.move(-4, 4)
        pygame.draw.rect(self.screen, (0, 0, 0, 120), shadow, border_radius=12)
        pygame.draw.rect(self.screen, (40, 45, 70), rect, border_radius=12)
        pygame.draw.rect(self.screen, COLORS["accent"], rect, 2, border_radius=12)

        prompt = self.small_font.render("Enter input word (use symbols: " + ", ".join(self.alphabet) + "):", True, COLORS["text"])
        self.screen.blit(prompt, (rect.x + 20, rect.y + 20))

        input_rect = pygame.Rect(rect.x + 20, rect.y + 60, box_w - 40, 40)
        pygame.draw.rect(self.screen, (60, 70, 100), input_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLORS["accent"], input_rect, 2, border_radius=8)

        input_text_surface = self.small_font.render(self.input_text, True, COLORS["text"])
        self.screen.blit(input_text_surface, (input_rect.x + 10, input_rect.y + 8))

    def serialize(self, name):
        return {
            "name": name,
            "nodes": [
                {
                    "id": n.id,
                    "x": n.pos.x,
                    "y": n.pos.y,
                    "is_start": getattr(n, "is_start", False),
                    "is_end": getattr(n, "is_end", False)
                }
                for n in self.nodes
            ],
            "connections": [
                {
                    "start": c.start.id,
                    "end": c.end.id,
                    "read": c.read,
                    "write": c.write,
                    "move": c.move,
                    "read2": c.read2,
                    "write2": c.write2,
                    "move2": c.move2
                }
                for c in self.connections
            ],
            "alphabet": self.alphabet,
        }

    def deserialize(self, data):
        from Node import Node
        from Connection import Connection

        self.nodes.clear()
        self.connections.clear()

        id_to_node = {}
        for ndata in data.get("nodes", []):
            node = Node(
                pos=pygame.Vector2(ndata["x"], ndata["y"]),
                is_start=ndata["is_start"],
                is_end=ndata["is_end"]
            )
            node.id = ndata["id"]
            self.nodes.append(node)
            id_to_node[node.id] = node

        for cdata in data.get("connections", []):
            start = id_to_node.get(cdata["start"])
            end = id_to_node.get(cdata["end"])
            if not start or not end:
                continue
            conn = Connection(start, end)
            conn.update_logic(cdata["read"], cdata["write"], cdata["move"], cdata.get("read2"), cdata.get("write2"), cdata.get("move2"))
            self.connections.append(conn)
            for connection in self.connections:
                if connection.start == start and connection.end == end:
                    conn.label_offset += 15

        self.current_node = next((n for n in self.nodes if getattr(n, "is_start", False)), None)
        self.finished = False
        self.running = False

    @classmethod
    def from_dict(cls, machine_data):
        from Node import Node
        from Connection import Connection
        nodes = []
        connections = []
        id_to_node = {}
        alphabet = ['_']

        for ndata in machine_data.get("nodes", []):
            node = Node(
                pos=pygame.Vector2(ndata["x"], ndata["y"]),
                is_start=ndata["is_start"],
                is_end=ndata["is_end"]
            )
            node.id = ndata["id"]
            nodes.append(node)
            id_to_node[node.id] = node

        for cdata in machine_data.get("connections", []):
            start = id_to_node.get(cdata["start"])
            end = id_to_node.get(cdata["end"])
            if not start or not end:
                continue
            conn = Connection(start, end)
            conn.update_logic(cdata["read"], cdata["write"], cdata["move"], cdata.get("read2"), cdata.get("write2"), cdata.get("move2"))
            connections.append(conn)
            for connection in connections:
                if connection.start == start and connection.end == end:
                    conn.label_offset += 15
        for sym in machine_data.get("alphabet", []):
            if sym not in alphabet:
                alphabet.append(sym)

        tm = cls(screen=None, nodes=nodes, connections=connections, tape=None, double_tape=False)
        tm.name = machine_data.get("name", "Unnamed Machine")
        tm.description = machine_data.get("description", "")
        tm.alphabet = machine_data.get("alphabet", ["_"])
        return tm

    def to_dict(self):
        return {
            "name": getattr(self, "name", "Unnamed Machine"),
            "description": getattr(self, "description", ""),
            "alphabet": getattr(self, "alphabet", ["_"]),
            "nodes": getattr(self, "nodes", []),
            "connections": getattr(self, "connections", [])
        }