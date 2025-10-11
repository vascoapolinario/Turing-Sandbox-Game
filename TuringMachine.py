import pygame
from MainMenu import COLORS

class TuringMachine:
    def __init__(self, screen, nodes, connections, tape):
        self.screen = screen
        self.nodes = nodes
        self.connections = connections
        self.tape = tape

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

        self.font = pygame.font.SysFont("futura", 24, bold=True)
        self.small_font = pygame.font.SysFont("futura", 18)


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
            print("❌ No current node — invalid machine.")
            self.finished = True
            return

        current_symbol = self.tape.read_symbol()

        valid_conn = None
        for conn in self.connections:
            print(f"  Checking transition from q{conn.start.id} to q{conn.end.id} for symbols {conn.read}")
            if conn.start == self.current_node and current_symbol in conn.read:
                valid_conn = conn
                break

        if self.current_node:
            self.current_node.is_active = False

        if not valid_conn:
            print("❌ No valid transition found. Halting.")
            self.finished = True
            self.running = False
            return

        if valid_conn.write:
            self.tape.write_symbol(valid_conn.write)

        if valid_conn.move == "L":
            self.tape.move_left()
        elif valid_conn.move == "R":
            self.tape.move_right()

        self.current_node = valid_conn.end

        self.current_node.is_active = True
        self.tape.show()

        if getattr(self.current_node, "is_end", False):
            print("✅ Reached end state.")
            self.finished = True
            self.running = False

    def play(self):
        if not self.current_node:
            print("❌ No start node defined.")
            return
        if self.finished:
            print("⚠️ Machine finished. Reset first.")
            return
        self.running = True
        self.paused = False
        self.current_node.is_active = True
        self.tape.show()

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
        self.finished = False
        self.running = False
        self.paused = True
        self.tape.hide()

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

        panel_x = sw - self.current_width - self.toggle_rect.width - 8
        panel_y = sh / 2 - self.height / 2
        rect = pygame.Rect(panel_x, panel_y, self.current_width, self.height)

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
        }
        for name, r in self.buttons.items():
            hovered = (self.hovered_button == name)
            self._draw_button(r, name, hovered)

    def handle_event(self, event):
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
                            else:
                                self.tape.show()
                        return

    def _draw_button(self, rect, name, hovered):
        if name == "play_pause":
            label = "Play" if (not self.running or self.paused) else "Pause"
            base = (90, 200, 110)
        elif name == "step":
            label = "Step"
            base = (100, 130, 220)
        elif name == "Show/Hide Tape":
            label = "Hide Tape" if self.tape.visible else "Show Tape"
            base = (120, 100, 200)
        else:
            label = "Reset"
            base = (200, 90, 90)

        color = tuple(min(255, c + 40) for c in base) if hovered else base
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        pygame.draw.rect(self.screen, (25, 25, 25), rect, 2, border_radius=10)

        text = self.small_font.render(label, True, (255, 255, 255))
        self.screen.blit(text, (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2))
