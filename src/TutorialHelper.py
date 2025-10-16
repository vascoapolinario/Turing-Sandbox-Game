import pygame
from MainMenu import COLORS

class TutorialHelper:
    def __init__(self, screen, level_name):
        self.screen = screen
        self.font = pygame.font.SysFont("futura", 20)
        self.title_font = pygame.font.SysFont("futura", 24, bold=True)
        self.level_name = level_name
        self.step = 0
        self.visible = True
        self.messages = self._load_messages(level_name)

    def _load_messages(self, level_name):
        if "How to Play 2: Transformations" in level_name:
            return [
                "Welcome! Let’s build a transformation machine. Add a start node (click 'Node' then click the grid).",
                "Now add an end node (select 'End Node' tool).",
                "Connect start to itself with the 'Connect' tool. and set: Read 0 or 1, write _ and move R.",
                "Now connect the start to the end node, set: Read _, move R.",
                "Press 'Submit' when done — all tests should pass!"
            ]
        else:
            return [
                "Welcome! Let’s learn the basics of building a Turing Machine. Using the toolbox on your top left: Add two nodes node (one of them starts out green, thats the start node).",
                "Now add an end node (the red one).",
                "Connect the start to the blue one node using the 'Connect' tool. Set the connection as if you read a 0 or a 1, move right.",
                "Connect the blue node to itself. Set the connection as if you read a 0 or a 1, move right.",
                "Connect the blue one to the end node. Set the connection as if you read a blank symbol, move right.",
                "Press 'Submit' when done to test your machine!",
                "You may use the button on your right to test other inputs as well and to see the machine in action. Have Fun!",
            ]

    def update(self, nodes, connections, test_complete):
        if not self.visible:
            return
        if self.level_name == "How to Play":
            if self.step == 0 and len(nodes) > 1:
                self.step = 1
            elif self.step == 1 and any(n.is_end for n in nodes):
                self.step = 2
            elif self.step == 2:
                if len(nodes) > 1:
                    start = nodes[0]
                    non_start = next((n for n in nodes if n is not start), None)
                    if non_start and any(
                            c.start == start and c.end == non_start and (
                                    c.read == ["0", "1"] or c.read == ["1", "0"]) and c.move == "R"
                            for c in connections
                    ):
                        self.step = 3
            elif self.step == 3:
                if len(nodes) > 1:
                    non_start = next((n for n in nodes if n is not nodes[0]), None)
                    if non_start and any(
                            c.start == non_start and c.end == non_start and (c.read == ["0", "1"] or c.read == ["1", "0"]) and c.move == "R"
                            for c in connections
                    ):
                        self.step = 4
            elif self.step == 4:
                if len(nodes) > 1:
                    non_start = next((n for n in nodes if n is not nodes[0]), None)
                    if non_start and any(
                            c.start == non_start and getattr(c.end, "is_end", False) and c.read == ["_"] and c.move == "R"
                            for c in connections
                    ):
                        self.step = 5
            elif self.step == 5 and test_complete:
                self.visible = False
        else:
            if self.step == 0 and len(nodes) > 0:
                self.step = 1
            elif self.step == 1 and any(n.is_end for n in nodes):
                self.step = 2
            elif self.step == 2:
                start = next((n for n in nodes if n is nodes[0]), None)
                if start and any(
                        c.start == start and c.end == start and (
                                c.read == ["0", "1"] or c.read == ["1", "0"]) and c.move == "R" and c.write == "_"
                        for c in connections
                ):
                    self.step = 3
            elif self.step == 3:
                if len(nodes) > 1:
                    start = nodes[0]
                    non_start = next((n for n in nodes if n is not nodes[0]), None)
                    if non_start and any(
                            c.start == start and c.end == non_start and (c.read == ["_"] and c.move == "R")
                            for c in connections
                    ):
                        self.step = 4
            elif self.step == 4 and test_complete:
                self.visible = False

    def draw(self):
        if not self.visible or self.step >= len(self.messages):
            return

        w, h = self.screen.get_size()
        msg = self.messages[self.step]

        box = pygame.Rect(40, h - 120, w - 80, 80)
        pygame.draw.rect(self.screen, (20, 25, 45), box, border_radius=12)
        pygame.draw.rect(self.screen, COLORS["accent"], box, 2, border_radius=12)

        title = self.title_font.render("Tutorial", True, COLORS["accent"])
        self.screen.blit(title, (box.x + 15, box.y + 10))

        wrapped = self._wrap_text(msg, self.font, box.width - 30)
        for i, line in enumerate(wrapped):
            text = self.font.render(line, True, COLORS["text"])
            self.screen.blit(text, (box.x + 15, box.y + 40 + i * 24))

    def _wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines, current = [], ""
        for w in words:
            test = current + w + " "
            if font.size(test)[0] < max_width:
                current = test
            else:
                lines.append(current.strip())
                current = w + " "
        if current:
            lines.append(current.strip())
        return lines