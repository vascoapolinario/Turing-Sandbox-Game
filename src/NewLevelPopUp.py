import pygame
from Button import Button, COLORS
from FontManager import FontManager
from Level import Level

class NewLevelPopup:
    def __init__(self, screen, on_save, on_cancel):
        self.screen = screen
        self.font = FontManager.get(22)
        self.small_font = FontManager.get(18, False)
        self.inputs = {
            "Name": "",
            "Description": "",
            "Objective": "",
        }
        self.alphabet_input = ""
        self.alphabet_list = ["_"]

        self.mode = "accept"
        self.double_tape = False
        self.examples = {
            "correct_examples": ["" for _ in range(2)],
            "wrong_examples": ["" for _ in range(2)],
            "transform_tests": [("", "") for _ in range(2)],
        }
        self.examples_per_page = 2
        self.pages = {k: 0 for k in self.examples.keys()}

        self.add_buttons = {
            "correct_examples": Button("+", (0, 0, 0, 0), self.small_font,
                                       lambda: self._add_example("correct_examples")),
            "wrong_examples": Button("+", (0, 0, 0, 0), self.small_font,
                                      lambda: self._add_example("wrong_examples")),
            "transform_tests": Button("+", (0, 0, 0, 0), self.small_font,
                                      lambda: self._add_example("transform_tests")),
        }

        self.nav_buttons = {
            "correct_examples": {
                "prev": Button("<", (0, 0, 0, 0), self.small_font,
                               lambda: self._prev_page("correct_examples")),
                "next": Button(">", (0, 0, 0, 0), self.small_font,
                               lambda: self._next_page("correct_examples")),
            },
            "wrong_examples": {
                "prev": Button("<", (0, 0, 0, 0), self.small_font,
                               lambda: self._prev_page("wrong_examples")),
                "next": Button(">", (0, 0, 0, 0), self.small_font,
                               lambda: self._next_page("wrong_examples")),
            },
            "transform_tests": {
                "prev": Button("<", (0, 0, 0, 0), self.small_font,
                               lambda: self._prev_page("transform_tests")),
                "next": Button(">", (0, 0, 0, 0), self.small_font,
                               lambda: self._next_page("transform_tests")),
            },
        }

        self.delete_buttons = {}

        self.active_field = None
        self.on_save = on_save
        self.on_cancel = on_cancel

        self.save_button = Button("Save", (0, 0, 0, 0), self.font, self._save)
        self.cancel_button = Button("Cancel", (0, 0, 0, 0), self.font, self._cancel)
        self.warning_text = ""

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._check_clicks(event.pos)

        elif event.type == pygame.KEYDOWN and self.active_field:
            key = self.active_field

            if key == "Alphabet":
                if event.key == pygame.K_RETURN:
                    if self.alphabet_input.strip() and self.alphabet_input.strip() not in self.alphabet_list:
                        if len(self.alphabet_input.strip()) == 1:
                            self.alphabet_list.insert(0, self.alphabet_input.strip())
                    self.alphabet_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.alphabet_input = self.alphabet_input[:-1]
                else:
                    self.alphabet_input += event.unicode
                return

            if isinstance(key, tuple):
                grp, idx, which = key
                page_offset = self.pages[grp] * self.examples_per_page
                real_idx = page_offset + idx

                if self.mode == "accept":
                    if event.key == pygame.K_RETURN:
                        self.active_field = None
                    elif event.key == pygame.K_BACKSPACE:
                        self.examples[grp][real_idx] = self.examples[grp][real_idx][:-1]
                    else:
                        self.examples[grp][real_idx] += event.unicode
                else:
                    current = list(self.examples["transform_tests"][real_idx])
                    if event.key == pygame.K_RETURN:
                        self.active_field = None
                    elif event.key == pygame.K_BACKSPACE:
                        current[0 if which == "input" else 1] = current[0 if which == "input" else 1][:-1]
                    else:
                        current[0 if which == "input" else 1] += event.unicode
                    self.examples["transform_tests"][real_idx] = tuple(current)
            else:
                if event.key == pygame.K_RETURN:
                    self.active_field = None
                elif event.key == pygame.K_BACKSPACE:
                    self.inputs[key] = self.inputs[key][:-1]
                else:
                    self.inputs[key] += event.unicode

        for b in getattr(self, "all_buttons", []):
            b.handle_event(event)

    def _check_clicks(self, pos):
        if self.mode_rect.collidepoint(pos):
            self.mode = "transform" if self.mode == "accept" else "accept"
            return

        if self.checkbox_rect.collidepoint(pos):
            self.double_tape = not self.double_tape
            return

        for key, rect in self._get_field_rects().items():
            if rect.collidepoint(pos):
                self.active_field = key
                return

        if self.alphabet_rect.collidepoint(pos):
            self.active_field = "Alphabet"
            return

        for (grp, idx), rect in self.delete_buttons.items():
            if rect.collidepoint(pos):
                self._delete_example(grp, idx)
                return

        example_rects = self._get_example_rects()
        for grp, rects in example_rects.items():
            for i, rect_pair in enumerate(rects):
                for which, rect in rect_pair:
                    if rect and rect.collidepoint(pos):
                        self.active_field = (grp, i, which)
                        return

    def _get_field_rects(self):
        sw, sh = self.screen.get_size()
        box_w, box_h = 520, 620
        box_x, box_y = sw / 2 - box_w / 2, sh / 2 - box_h / 2 - 20
        rects = {}
        for i, key in enumerate(self.inputs.keys()):
            rects[key] = pygame.Rect(box_x + 30, box_y + 60 + i * 40, box_w - 60, 35)
        self.mode_rect = pygame.Rect(box_x + 30, box_y + 70 + len(self.inputs) * 55, 120, 30)
        self.checkbox_rect = pygame.Rect(self.mode_rect.right + 40, self.mode_rect.y + 8, 18, 18)
        self.alphabet_rect = pygame.Rect(box_x + 30, box_y + 60 + (40 * 3), box_w - 60, 35)
        return rects

    def _get_example_rects(self):
        sw, sh = self.screen.get_size()
        box_w, box_h = 520, 620
        box_x, box_y = sw / 2 - box_w / 2, sh / 2 - box_h / 2
        rects = {}

        if self.mode == "accept":
            for grp_idx, grp in enumerate(["correct_examples", "wrong_examples"]):
                y_start = box_y + 300 + grp_idx * 130
                rects[grp] = []

                start = self.pages[grp] * self.examples_per_page
                end = start + self.examples_per_page
                visible = self.examples[grp][start:end]

                for i, val in enumerate(visible):
                    rect = pygame.Rect(box_x + 40, y_start + i * 40, box_w - 100, 30)
                    rects[grp].append((("input", rect),))
        else:
            y_start = box_y + 300
            rects["transform_tests"] = []

            start = self.pages["transform_tests"] * self.examples_per_page
            end = start + self.examples_per_page
            visible = self.examples["transform_tests"][start:end]

            for i, (inp, out) in enumerate(visible):
                rin = pygame.Rect(box_x + 40, y_start + i * 40, 180, 30)
                rout = pygame.Rect(rin.right + 30, y_start + i * 40, 180, 30)
                rects["transform_tests"].append((("input", rin), ("output", rout)))
        return rects

    def draw(self):
        sw, sh = self.screen.get_size()
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        box_w, box_h = 520, 620
        box_x, box_y = sw / 2 - box_w / 2, sh / 2 - box_h / 2
        pygame.draw.rect(self.screen, (30, 40, 70), (box_x, box_y, box_w, box_h), border_radius=16)
        pygame.draw.rect(self.screen, COLORS["accent"], (box_x, box_y, box_w, box_h), 2, border_radius=16)
        self.all_buttons = [self.save_button, self.cancel_button]


        for key, rect in self._get_field_rects().items():
            is_active = (self.active_field == key)
            pygame.draw.rect(self.screen, (60, 70, 100), rect, border_radius=8)
            pygame.draw.rect(self.screen, COLORS["accent"] if is_active else (80, 80, 110), rect, 2, border_radius=8)
            txt = self.small_font.render(f"{key}: {self.inputs[key]}", True, COLORS["text"])
            self.screen.blit(txt, (rect.x + 8, rect.y + 6))

        pygame.draw.rect(self.screen, (60, 70, 100), self.mode_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLORS["accent"], self.mode_rect, 2, border_radius=8)
        label = self.small_font.render(f"Mode: {self.mode}", True, COLORS["text"])
        self.screen.blit(label, (self.mode_rect.x + 8, self.mode_rect.y + 6))

        pygame.draw.rect(self.screen, COLORS["accent"], self.checkbox_rect, 2)
        if self.double_tape:
            pygame.draw.line(self.screen, COLORS["accent"], self.checkbox_rect.topleft, self.checkbox_rect.bottomright, 1)
            pygame.draw.line(self.screen, COLORS["accent"], self.checkbox_rect.topright, self.checkbox_rect.bottomleft, 1)
        lbl = self.small_font.render("Double Tape", True, COLORS["text"])
        self.screen.blit(lbl, (self.checkbox_rect.right + 10, self.checkbox_rect.y - 3))

        pygame.draw.rect(self.screen, (60, 70, 100), self.alphabet_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLORS["accent"] if self.active_field == "Alphabet" else (80, 80, 110),
                         self.alphabet_rect, 2, border_radius=8)
        text = self.small_font.render(f"Alphabet Input: {self.alphabet_input}", True, COLORS["text"])
        self.screen.blit(text, (self.alphabet_rect.x + 8, self.alphabet_rect.y + 6))
        alpha_list = " ".join([f"[{a}]" for a in self.alphabet_list])
        list_text = self.small_font.render(alpha_list, True, COLORS["accent"])
        self.screen.blit(list_text, (self.alphabet_rect.x + 8, self.alphabet_rect.bottom + 5))

        self._draw_examples(box_x, box_y)

        self.save_button.rect = pygame.Rect(box_x + 90, box_y + box_h - 60, 140, 40)
        self.cancel_button.rect = pygame.Rect(box_x + 290, box_y + box_h - 60, 140, 40)

        for b in self.all_buttons:
            b.draw(self.screen)

        if self.warning_text:
            warn = self.small_font.render(self.warning_text, True, (255, 80, 80))
            self.screen.blit(warn, (box_x + 30, box_y + box_h - 90))

    def _draw_examples(self, box_x, box_y):
        example_rects = self._get_example_rects()
        self.delete_buttons.clear()
        title_y = box_y + 270

        if self.mode == "accept":
            y_positions = {
                "correct_examples": box_y + 260,
                "wrong_examples": box_y + 405
            }

            for grp in ["correct_examples", "wrong_examples"]:
                y_start = y_positions[grp]
                self.screen.blit(self.small_font.render(grp.replace("_", " ").title(), True, COLORS["accent"]),
                                 (box_x + 30, y_start))

                for i, rect_pair in enumerate(example_rects[grp]):
                    _, rect = rect_pair[0]
                    rect = rect.move(0, 5)
                    is_active = (self.active_field == (grp, i, "input"))
                    border = COLORS["accent"] if is_active else (70, 80, 110)
                    pygame.draw.rect(self.screen, (60, 70, 100), rect, border_radius=6)
                    pygame.draw.rect(self.screen, border, rect, 2, border_radius=6)
                    page_start = self.pages[grp] * self.examples_per_page
                    val = self.examples[grp][page_start + i]
                    t = self.small_font.render(f"{val}", True, COLORS["text"])
                    self.screen.blit(t, (rect.x + 5, rect.y + 4))

                    del_rect = pygame.Rect(rect.right + 5, rect.y + 4, 20, 20)
                    pygame.draw.rect(self.screen, (100, 50, 50), del_rect)
                    d = self.small_font.render("x", True, (255, 255, 255))
                    self.screen.blit(d, (del_rect.x + 5, del_rect.y - 2))
                    self.delete_buttons[(grp, page_start + i)] = del_rect

                self._draw_section_controls(grp, box_x + 30, y_start + 120)

        else:
            self.screen.blit(self.small_font.render("Transform Tests", True, COLORS["accent"]),
                             (box_x + 30, title_y))
            in_label = self.small_font.render("In", True, COLORS["accent"])
            out_label = self.small_font.render("Out", True, COLORS["accent"])
            self.screen.blit(in_label, (box_x + 50, title_y + 18))
            self.screen.blit(out_label, (box_x + 250, title_y + 18))

            for i, rect_pair in enumerate(example_rects["transform_tests"]):
                for which, rect in rect_pair:
                    is_active = (self.active_field == ("transform_tests", i, which))
                    pygame.draw.rect(self.screen, (60, 70, 100), rect, border_radius=6)
                    pygame.draw.rect(self.screen, COLORS["accent"] if is_active else (70, 80, 110),
                                     rect, 2, border_radius=6)
                    page_start = self.pages["transform_tests"] * self.examples_per_page
                    val = self.examples["transform_tests"][page_start + i][0 if which == "input" else 1]
                    t = self.small_font.render(val, True, COLORS["text"])
                    self.screen.blit(t, (rect.x + 5, rect.y + 4))
                del_rect = pygame.Rect(rect.right + 10, rect.y + 4, 20, 20)
                pygame.draw.rect(self.screen, (100, 50, 50), del_rect)
                d = self.small_font.render("x", True, (255, 255, 255))
                self.screen.blit(d, (del_rect.x + 5, del_rect.y - 2))
                self.delete_buttons[("transform_tests", page_start + i)] = del_rect

            self._draw_section_controls("transform_tests", box_x + 30, title_y + 180)

    def _draw_section_controls(self, group, x, y):
        add_btn = self.add_buttons[group]
        add_btn.rect = pygame.Rect(x + 270, y, 30, 25)
        add_btn.draw(self.screen)

        prev_btn = self.nav_buttons[group]["prev"]
        next_btn = self.nav_buttons[group]["next"]
        prev_btn.rect = pygame.Rect(x + 320, y, 30, 25)
        next_btn.rect = pygame.Rect(x + 360, y, 30, 25)
        prev_btn.draw(self.screen)
        next_btn.draw(self.screen)

        self.all_buttons.extend([add_btn, prev_btn, next_btn])

    def _save(self):
        if not self.inputs["Name"].strip() or not self.inputs["Objective"].strip():
            self.warning_text = "Please fill in all required fields!"
            return

        if self.mode == "accept":
            if not any(x.strip() for x in self.examples["correct_examples"]):
                self.warning_text = "Add at least one correct example!"
                return
        else:
            if not any(i.strip() or o.strip() for i, o in self.examples["transform_tests"]):
                self.warning_text = "Add at least one transform test!"
                return

        self.warning_text = ""

        if self.mode == "accept":
            new_level = Level(
                name=self.inputs["Name"],
                type="Custom",
                description=self.inputs["Description"],
                detailedDescription="",
                alphabet=self.alphabet_list or ["0", "1", "_"],
                objective=self.inputs["Objective"],
                mode="accept",
                correct_examples=[x for x in self.examples["correct_examples"] if x.strip()],
                wrong_examples=[x for x in self.examples["wrong_examples"] if x.strip()],
                double_tape=self.double_tape
            )
        else:
            new_level = Level(
                name=self.inputs["Name"],
                type="Custom",
                description=self.inputs["Description"],
                detailedDescription="",
                alphabet=self.alphabet_list or ["0", "1", "_"],
                objective=self.inputs["Objective"],
                mode="transform",
                transform_tests=[{"input": i, "output": o} for i, o in self.examples["transform_tests"] if i or o],
                double_tape=self.double_tape
            )
        self.on_save(new_level)

    def _cancel(self):
        self.on_cancel()

    def _add_example(self, group):
        if group == "transform_tests":
            self.examples[group].append(("", ""))
        else:
            self.examples[group].append("")

    def _delete_example(self, group, index):
        if 0 <= index < len(self.examples[group]):
            del self.examples[group][index]

    def _next_page(self, group):
        max_page = max(0, (len(self.examples[group]) - 1) // self.examples_per_page)
        if self.pages[group] < max_page:
            self.pages[group] += 1

    def _prev_page(self, group):
        if self.pages[group] > 0:
            self.pages[group] -= 1
