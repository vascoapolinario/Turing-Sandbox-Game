import pygame
from Button import Button, COLORS
from FontManager import FontManager


class HelpPopup:
    def __init__(self, screen, on_close):
        self.screen = screen
        self.on_close = on_close

        self.title_font = FontManager.get(40, bold=True)
        self.header_font = FontManager.get(28, bold=True)
        self.body_font = FontManager.get(22)

        self.scroll_offset = 0
        self.scroll_speed = 30

        self.sections = [
            (
                "Welcome",
                "Turing Machine Sandbox lets you experiment with Turing machines in a visual way. "
                "You can play levels, use the sandbox, or collaborate with friends in Multiplayer."
            ),
            (
                "Turing Machines",
                "A Turing machine consists of states (nodes) and transitions (connections) between them.\n"
                "Each transition specifies what symbols to read from the tape(s), what symbols to write, "
                "and how to move the tape head(s).\n"
                "The machine starts in the initial state with the tape head at the leftmost symbol of the input.\n"
                "It processes the input according to the transitions until it reaches an end state (accept) or gets stuck (reject).\n"
                "Turing machines are defined as a 7-tuple (Q, Σ, Γ, δ, q0, F, b) where:\n"
                "- Q: finite set of states\n"
                "- Σ: input alphabet (symbols that can appear on the input tape)\n"
                "- Γ: tape alphabet (symbols that can appear on the tape, includes blank symbol '_')\n"
                "- δ: transition function (defines state transitions based on current state and tape symbol(s))\n"
                "- q0: initial state (where the machine starts)\n"
                "- F: accept state (machine halts and accepts input)\n"
                "- b: blank symbol (represents empty tape cells)\n"
                "In this sandbox the blank symbol is represented by an underscore (_).\n"
                "For more information on Turing machines, visit https://en.wikipedia.org/wiki/Turing_machine"
            ),
            (
                "Nodes",
                "Nodes represent the states of the Turing machine. There are three types of nodes:\n"
                "- Start Node: The initial state where the machine begins processing. It is marked in green.\n"
                "- Normal Node: An intermediate state where the machine can read/write symbols and move the tape head. Marked in blue\n"
                "- End Node: The accept state where the machine halts and accepts the input. It is marked in red."

            ),
            (
                "Connections",
                "Connections represent the transitions between states. Each connection specifies:\n"
                "- Read: The symbol(s) that must be read from the tape to take this transition.\n"
                "- Write: The symbol to write on the tape when taking this transition.\n"
                "- Move: The direction to move the tape head (L = left, R = right, S = stay).\n"
                "To create a connection, select the 'Connect' tool, click on the start node, then click on the end node.\n"
                "You can connect a node to itself."
            ),
            (
                "Levels",
                "Levels consist of two types of challenges: building machines to pass given test cases and"
                " machines that transform input strings to output strings.\n"
                "In acceptance levels the machine tests various inputs, some of which should be accepted (halted in an end node) "
                "and some rejected (never halting). \n"
                "In transformation levels the machine must convert input strings to target output strings. \n"
                "The level description details what the machine should do to pass the level."
            ),
            (
                "Saving and Sharing",
                "To save and load your Turing Machines, use the 'Save/Load' button in the pause menu.\n"
                "You can share your saved machines with others trough the workshop located in the Level Menu.\n"
                "To create a custom level, go to the Level Menu and click 'New Level'.\n"
                "To subscribe to user-created levels or machines,navigate to the Workshop tab and click 'Subscribe' on any level/machine you like.\n"
                "To play a workshop level in multiplayer, the host must be subscribed to it.\n"
                "Disclaimer: User-created content may vary in quality and accuracy.\n"
                "Saves are stored locally on your device in the documents folder under 'Turing Sandbox Saves'.\n"
                "Workshop levels are stored online and require an internet connection to access.\n"
                "Workshop items are user-generated, to report inappropriate content please contact the developer.\n"
                "Please adhere to the terms of service available on the game's github page."
            ),
            (
                "Sandbox",
                "The Sandbox is a free-build mode. Place nodes, add transitions and test your own ideas "
                "without restrictions. Perfect for experimenting or teaching.\n"
                "To modify the tape alphabet open the settings menu from the main menu."
            ),
            (
                "Two Tape Machines",
                "When building two-tape Turing machines, each transition requires specifying read/move actions for both tapes.\n"
                "By default the second tape already has a read and move set, but you can change it as needed.\n"
                "For Transformation levels, the output should be written on the second tape."
            ),
            (
                "Controls",
                "- Left click:  place elements/delete elements and interact\n"
                "- Right click: cancel connection placement\n"
                "- Mouse wheel: zoom or scroll (depending on view)\n"
                "- WASD: move around the grid\n"
                "- ESC: back or close menus"
            ),
            (
                "Multiplayer",
                "In the Multiplayer mode, you can collaborate with friends to build Turing machines together in real-time.\n"
                "One player hosts a lobby and others can join using the lobby code.\n"
                "All players can add/remove nodes and connections, and changes are synchronized across all clients.\n"
                "Disclaimer: The chat feature is intended for casual communication and may not be moderated.\n"
                "Please adhere to the terms of service available on the game's github page."
            ),
            (
                "Player Accounts",
                "To access multiplayer and workshop features, you need to create an account.\n"
                "To create an account fill out the username and password and click 'Register' in the authentication popup.\n"
                "To log in, enter your credentials and click 'Login'.\n"
                "Although passwords are stored securely and encrypted, avoid using sensitive passwords to guarantee your safety.\n"
                "You can log out from the settings menu in the main menu.\n"
                "To delete your account press the 'Delete Account' button in the settings menu.\n"
            ),
            (
                "Tips",
                "Start simple. Try to solve small versions of the problem first, then extend your machine.\n"
                "Name your levels clearly if you plan to share them.\n"
                "Use the sandbox to test ideas before implementing them in levels.\n"
                "Try to think step-by-step about how the machine should process the input.\n"
                "Have fun and experiment!"
            ),
            (
                "Credits",
                "Turing Machine Sandbox was developed by Vasco Apolinário.\n"
                "Special thanks to all playtesters and contributors who provided valuable feedback and support.\n"
                "For more information, visit the game's github page at https://github.com/vascoapolinario/Turing-Sandbox-Game\n"
                "Although the code is free to view, redistribution or commercial use is prohibited without permission from the author.\n"
                "Thanks for playing!"
            )
        ]
        self.button_font = FontManager.get(24, bold=True)
        self.btn_close = Button("Close", (0.0, 0.0, 0.14, 0.06), self.button_font, self.on_close)

    def _wrap_text(self, text, font, max_width):
        lines = []
        for paragraph in text.split("\n"):
            words = paragraph.split(" ")
            current = ""
            for word in words:
                test = f"{current} {word}".strip()
                if font.size(test)[0] <= max_width:
                    current = test
                else:
                    if current:
                        lines.append(current)
                    current = word
            if current:
                lines.append(current)
        return lines

    def _compute_content_height(self, inner_width):
        y = 0
        header_spacing = 10
        section_spacing = 15

        for header, body in self.sections:
            y += self.header_font.get_height() + header_spacing

            body_lines = self._wrap_text(body, self.body_font, inner_width)
            y += len(body_lines) * (self.body_font.get_height() + 4)

            y += section_spacing

        return y

    def draw(self):
        w, h = self.screen.get_size()

        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        box_w, box_h = int(w * 0.7), int(h * 0.7)
        box_x, box_y = (w - box_w) // 2, (h - box_h) // 2
        box_rect = pygame.Rect(box_x, box_y, box_w, box_h)

        pygame.draw.rect(self.screen, (25, 27, 40), box_rect, border_radius=12)
        pygame.draw.rect(self.screen, COLORS["accent"], box_rect, 3, border_radius=12)

        title_surf = self.title_font.render("Help", True, COLORS["accent"])
        self.screen.blit(title_surf, (box_rect.centerx - title_surf.get_width() // 2, box_rect.y + 20))

        game_version = "v0.6.0"
        version_surf = self.body_font.render(game_version, True, COLORS["text"])
        self.screen.blit(version_surf, (box_rect.right - version_surf.get_width() - 20, box_rect.bottom - version_surf.get_height() - 10))

        self.btn_close.rect = pygame.Rect(
            box_rect.right - int(box_w * 0.2),
            box_rect.y + 20,
            int(box_w * 0.16),
            int(box_h * 0.08),
        )
        self.btn_close.draw(self.screen)

        inner_margin = 30
        text_x = box_rect.x + inner_margin
        text_y_start = box_rect.y + 80
        inner_width = box_rect.width - inner_margin * 2
        inner_height = box_rect.bottom - inner_margin - text_y_start

        content_height = self._compute_content_height(inner_width)
        max_scroll = max(0, content_height - inner_height)
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

        clip_rect = pygame.Rect(text_x, text_y_start, inner_width, inner_height)
        prev_clip = self.screen.get_clip()
        self.screen.set_clip(clip_rect)

        y = text_y_start - self.scroll_offset
        header_spacing = 10
        section_spacing = 15

        for header, body in self.sections:
            header_surf = self.header_font.render(header, True, COLORS["accent"])
            self.screen.blit(header_surf, (text_x, y))
            y += header_surf.get_height() + header_spacing

            body_lines = self._wrap_text(body, self.body_font, inner_width)
            for line in body_lines:
                line_surf = self.body_font.render(line, True, COLORS["text"])
                self.screen.blit(line_surf, (text_x, y))
                y += self.body_font.get_height() + 4

            y += section_spacing

        self.screen.set_clip(prev_clip)

        if content_height > inner_height:
            scrollbar_width = 6
            bar_x = box_rect.right - inner_margin // 2
            bar_y = text_y_start
            bar_h = inner_height

            pygame.draw.rect(self.screen, (40, 44, 70), (bar_x, bar_y, scrollbar_width, bar_h), border_radius=3)

            ratio = inner_height / content_height
            handle_h = max(20, int(bar_h * ratio))
            scroll_ratio = self.scroll_offset / max_scroll if max_scroll > 0 else 0
            handle_y = bar_y + int((bar_h - handle_h) * scroll_ratio)

            pygame.draw.rect(
                self.screen,
                COLORS["accent"],
                (bar_x, handle_y, scrollbar_width, handle_h),
                border_radius=3
            )

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.on_close()
            return

        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset -= event.y * self.scroll_speed
            return

        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            self.btn_close.handle_event(event)

        self.btn_close.handle_event(event)
