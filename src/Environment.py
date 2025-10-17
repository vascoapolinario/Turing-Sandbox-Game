import json

import pygame

import save_manager
from Button import Button
from Level import Level
from Node import Node
from SaveMenu import SaveMenu
from Tape import Tape
from MainMenu import COLORS
from Toolbox import Toolbox
from Grid import Grid
from Connection import Connection
from ConnectionWindow import ConnectionWindow
from TuringMachine import TuringMachine
from PauseMenu import PauseMenu
from TutorialHelper import TutorialHelper
from FontManager import FontManager


class Environment:
    def __init__(self, screen, level=None):
        self.level = level or Level(
            name="Sandbox",
            type="sandbox",
            description="Free build mode with no objective.",
            detailedDescription="Have fun!",
            alphabet=['0', '1', '_'],
            objective="Experiment freely.",
            solution={},
            mode="accept",
            double_tape=True

        )
        self.alphabet = self.level.alphabet
        self.screen = screen
        if self.level.double_tape:
            self.tape = Tape(screen, base_y=-210)
            self.tape2 = Tape(screen, base_y=-50)
        else:
            self.tape = Tape(screen)
            self.tape2 = None
        self.running = True
        self.toolbox = Toolbox(screen, self.on_tool_selected)
        self.grid = Grid(screen)
        self.connection_window = None

        self.nodes = []
        Node._id_counter = 0
        self.connections = []
        self.TuringMachine = TuringMachine(screen, self.nodes, self.connections, self.tape, self.tape2, self.level.double_tape)

        self.current_tool = None
        self.connecting_from = None
        self.mouse_pos = pygame.Vector2(0, 0)

        self.test_results = []
        self.test_complete = False
        self.all_passed = False

        self.paused = False
        self.back_to_menu = False
        self.levelselection = False
        self.pause_menu = PauseMenu(
            self.screen,
            on_resume=self._resume,
            on_save_load=self._save_machine,
            on_exit_to_menu=self._return_to_menu,
            on_levels = self._levelmenu,
            on_clear=self._clear_space,
            on_quit=self._quit_game,
            level=self.level
        )

        self.save_menu = SaveMenu(
            self.screen,
            turing_machine=self.TuringMachine,
            on_close=self._resume,
            on_load=self._load_named_machine
        )

        if self.level.type != "sandbox":
            if self.level.mode == "accept":
                self.tape.change_tape(self.level.correct_examples[0] if self.level.correct_examples else "")
            elif self.level.mode == "transform":
                self.tape.change_tape(self.level.transform_tests[0]["input"] if self.level.transform_tests else "")
            self.submit_button = Button(
                "Submit",
                (0.75, 0.10, 0.20, 0.06),
                FontManager.get(22),
                self._run_level_tests
            )

        self.tutorial = None
        if self.level.type == "Tutorial":
            self.tutorial = TutorialHelper(screen, self.level.name)

    def update(self, dt):
        self.TuringMachine.update(dt)
        if self.TuringMachine.alphabet != self.alphabet:
            self.TuringMachine.alphabet = self.alphabet
        self.tape.update(dt)
        if self.level.double_tape:
            self.tape2.update(dt)
        self.toolbox.update(dt)
        if self.tutorial:
            self.tutorial.update(self.nodes, self.connections, self.test_complete)
        keys = pygame.key.get_pressed()
        if not self.paused and not self.pause_menu.visible:
            self.grid.handle_input(dt, keys)
        if self.level.type != "sandbox":
            self.submit_button.update_rect_withscale(self.screen.get_size())
        for node in self.nodes:
            node.update(dt) if hasattr(node, "update") else None

        if self.paused:
            self.pause_menu.update()
            return

    def on_tool_selected(self, tool_name):
        self.current_tool = tool_name
        self.connecting_from = None
        self.toolbox.draw()

    def draw(self):
        self.screen.fill(COLORS["background"])
        self.grid.draw()
        screen_w, _ = self.screen.get_size()
        if self.level.type != "sandbox":
            self.submit_button.rect.topleft = (screen_w - 220, 60)

        for conn in self.connections:
            conn.draw(self.screen, self.grid)
        for node in self.nodes:
            node.draw(self.screen, self.grid)
        if self.current_tool == "connect" and self.connecting_from is not None:
            self._draw_preview_connection()

        self.TuringMachine.draw()

        self._draw_level_info()
        if self.level.type != "sandbox":
            self._draw_level_progress()
            self.submit_button.draw(self.screen)

        if self.connection_window:
            self.connection_window.draw()

        self.tape.draw()
        if self.level.double_tape:
            self.tape2.draw()
        if self.tutorial:
            self.tutorial.draw()
        self.toolbox.draw()

        if self.paused and not self.save_menu.visible:
            self.pause_menu.draw()

        if self.save_menu.visible:
            self.save_menu.draw()
            self.save_menu.update()

    def handle_event(self, event):
        if self.save_menu.visible:
            self.save_menu.handle_event(event)
            return
        elif self.paused and event.type != pygame.KEYDOWN:
            self.pause_menu.handle_event(event)
            return


        toolbox_used = self.toolbox.handle_event(event)
        if toolbox_used:
            return

        if self.connection_window:
            self.connection_window.handle_event(event)
            return

        self.TuringMachine.handle_event(event)
        self.grid.handle_event(event)
        if self.level.type != "sandbox":
            self.submit_button.handle_event(event)

        if event.type == pygame.MOUSEMOTION:
            self.mouse_pos = pygame.Vector2(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.current_tool in ("node", "end_node"):
                if not self.toolbox.toggle_button.collidepoint(event.pos):
                    world_pos = self.grid.screen_to_world(event.pos)
                    pos = self.grid.snap(world_pos)
                    if self._get_node_at(pos, world_space=True):
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

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and not self.save_menu.visible:
            if self.paused:
                self.paused = False
                self.pause_menu.hide()
            else:
                self.paused = True
                self.pause_menu.show()
            return

        for node in self.nodes:
            node.handle_event(event)

    def _get_node_at(self, pos, world_space=False):
        for node in reversed(self.nodes):
            if world_space:
                if node.is_inside(pos):
                    return node
            else:
                if node.is_inside(pos, self.grid):
                    return node
        return None

    def _create_connection(self, start_node, end_node):
        conn = Connection(start_node, end_node)
        for connection in self.connections:
            if connection.start == start_node and connection.end == end_node:
                conn.label_offset += 15
        self.connections.append(conn)
        start_node.add_connection(conn)
        self._sync_machine()

        self.connection_window = ConnectionWindow(
            self.screen,
            conn,
            symbols=self.alphabet,
            on_save=self._save_connection_logic,
            on_cancel=lambda: self._cancel_connection_window(conn),
            double_tape=(self.level.double_tape == True)
        )

    def _save_connection_logic(self, read, write, move, read2=None, write2=None, move2=None):
        if not self.connection_window:
            return

        if not read or not move:
            self._cancel_connection_window(self.connection_window.connection)
            return

        double_mode = self.level.double_tape
        double_provided = (read2 is not None or write2 is not None or move2 is not None)

        if double_provided and (not read2 or not move2):
            self._cancel_connection_window(self.connection_window.connection)
            return

        new_conn = self.connection_window.connection
        start = new_conn.start

        new_read = set(read)
        new_read2 = set(read2 or [])

        for existing in self.connections:
            if existing is new_conn:
                continue
            if existing.start == start:
                existing_read = set(getattr(existing, "read", []))
                existing_read2 = set(getattr(existing, "read2", []))

                if not double_mode:
                    if new_read & existing_read:
                        self._cancel_connection_window(new_conn)
                        return
                else:
                    if new_read & existing_read and new_read2 & existing_read2:
                        self._cancel_connection_window(new_conn)
                        return

        if double_mode and double_provided:
            new_conn.update_logic(read, write, move, read2, write2, move2)
        else:
            new_conn.update_logic(read, write, move)

        self._sync_machine()
        self.connection_window = None

    def _cancel_connection_window(self, conn):
        if conn in self.connections:
            self.connections.remove(conn)
            self._sync_machine()
        self.connection_window = None

    def _draw_preview_connection(self):
        if not self.connecting_from:
            return

        start_screen = self.grid.world_to_screen(self.connecting_from.pos)
        end_screen = pygame.Vector2(self.mouse_pos)

        mid = (start_screen + end_screen) / 2
        direction = (end_screen - start_screen)
        if direction.length() == 0:
            return
        normal = pygame.Vector2(-direction.y, direction.x).normalize()
        control = mid + normal * 60

        points = []
        for t in [i / 20 for i in range(21)]:
            p = (1 - t) ** 2 * start_screen + 2 * (1 - t) * t * control + t ** 2 * end_screen
            points.append(p)

        pygame.draw.lines(self.screen, (180, 180, 180), False, points, 2)
        pygame.draw.circle(self.screen, (230, 230, 230), end_screen, 4)

    def _handle_delete(self, pos):
        node = self._get_node_at(pos)
        if node:
            self._delete_node(node)
            self._sync_machine()
            return

        for conn in self.connections:
            if conn.is_clicked(pos, self.grid):
                self.connections.remove(conn)
                self._sync_machine()
                return

    def _delete_node(self, node):
        self.nodes.remove(node)
        if Node._id_counter > 0:
            Node._id_counter -= 1
            if node.id != 0:
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

    def _draw_level_info(self):
        font = FontManager.get(22)
        desc_font = FontManager.get(18, False)
        name_text = font.render(self.level.name, True, COLORS["accent"])
        desc_text = desc_font.render(self.level.description, True, COLORS["text"])
        name_x = self.screen.get_width() - 20 - name_text.get_width()
        desc_x = self.screen.get_width() - 20 - desc_text.get_width()
        self.screen.blit(name_text, (name_x, 20))
        self.screen.blit(desc_text, (desc_x, 40))

    def _draw_level_progress(self):
        if self.level.mode == "accept" and not (self.level.correct_examples or self.level.wrong_examples):
            return
        if self.level.mode == "transform" and not getattr(self.level, "transform_tests", []):
            return

        bar_x = self.screen.get_width() - 230
        bar_y = 100
        bar_width = 200
        bar_height = 14
        pygame.draw.rect(self.screen, (40, 50, 80), (bar_x, bar_y, bar_width, bar_height), border_radius=6)

        if self.test_results:
            passed = sum(1 for r in self.test_results if r)
            pct = passed / len(self.test_results)
            pygame.draw.rect(self.screen, (90, 200, 90), (bar_x, bar_y, bar_width * pct, bar_height), border_radius=6)

        if self.test_complete:
            font = FontManager.get(22)
            status = "Level Passed" if self.all_passed else "Level Incomplete"
            color = (120, 220, 120) if self.all_passed else (220, 100, 100)
            text = font.render(status, True, color)
            self.screen.blit(text, (bar_x, bar_y + 20))

    def _run_level_tests(self):
        if self.level.mode == "accept" and not (self.level.correct_examples or self.level.wrong_examples):
            return
        if self.level.mode == "transform" and not getattr(self.level, "transform_tests", []):
            return

        self.test_results.clear()
        self.test_complete = False
        self.all_passed = False
        if self.level.mode == "accept":

            for example in self.level.wrong_examples:
                result = self._simulate(example, should_accept=False)
                self.test_results.append(result)

            for example in self.level.correct_examples:
                result = self._simulate(example, should_accept=True)
                self.test_results.append(result)
        else:
            for case in self.level.transform_tests:
                self.test_results.append(self._simulate_transform(case["input"], case["output"]))

        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r)
        self.all_passed = (total > 0 and passed == total)
        if self.all_passed and self.level.type != "sandbox":
            self.level.solution = self.TuringMachine.serialize(self.level.name)
            save_manager.mark_level_complete(self.level.name, self.level.solution)
        self.test_complete = True

        self.TuringMachine.reset()
        if self.level.mode == "accept":
            self.tape.change_tape(self.level.correct_examples[0])
        elif self.level.mode == "transform":
            self.tape.change_tape(self.level.transform_tests[0]["input"] if self.level.transform_tests else "")
        self.TuringMachine.play()
        self.TuringMachine.open = True

    def _simulate(self, input_string, should_accept=True):
        if not self.nodes or not any(n.is_start for n in self.nodes):
            accepted = getattr(self.TuringMachine.current_node, "is_end", False)
            return False

        self.tape.change_tape(input_string)
        self.TuringMachine.reset()
        self.TuringMachine.play()

        for _ in range(200):
            self.TuringMachine.step()
            if self.TuringMachine.finished:
                break
        accepted = getattr(self.TuringMachine.current_node, "is_end", False)
        #print("Input: ", input_string, " Accepted: ", accepted, " Expected: ", should_accept)
        return accepted if should_accept else not accepted

    def _resume(self):
        self.paused = False
        self.pause_menu.hide()

    def _save_machine(self):
        self.pause_menu.hide()
        self.save_menu.show()

    def _load_named_machine(self, name):
        data = save_manager.load_machine(name)
        Node._id_counter = 0
        self.TuringMachine.deserialize(data)

    def _return_to_menu(self):
        self.back_to_menu = True
        self.paused = False
        self.pause_menu.hide()

    def _quit_game(self):
        self.paused = False
        self.pause_menu.hide()
        pygame.event.post(pygame.event.Event(pygame.QUIT))


    def _simulate_transform(self, input_string, expected_output):
        self.tape.change_tape(input_string)
        self.TuringMachine.reset()
        self.TuringMachine.play()

        for _ in range(400):
            self.TuringMachine.step()
            if self.TuringMachine.finished:
                break
        if self.level.double_tape:
            result = self.tape2.get_tape_string().strip("_")
        else:
            result = self.tape.get_tape_string().strip("_")
        #print("Input: ", input_string, " Output: ", result, " Expected: ", expected_output)
        return result == expected_output

    def load_solution(self, solution):
        Node.id_counter = 0
        self.TuringMachine.deserialize(solution)

    def _clear_space(self):
        self.nodes.clear()
        self.connections.clear()
        Node._id_counter = 0
        self.TuringMachine.reset()
        self.TuringMachine.nodes = self.nodes
        self.TuringMachine.connections = self.connections
        self.TuringMachine.current_node = None
        self.TuringMachine.playing = False
        self.TuringMachine.open = False
        self.test_results.clear()
        self.test_complete = False
        self.all_passed = False
        self.paused = False
        self.pause_menu.hide()

    def _levelmenu(self):
        self.back_to_menu = True
        self.levelselection = True
        self.paused = False
        self.pause_menu.hide()
