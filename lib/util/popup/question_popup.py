import pygame
import random
from lib.config import *
from lib.assets import *
from lib.util.save_data import *

class QuestionPopup:
    used_questions = set()  # Class-level tracking

    def __init__(self):
        self.unused_questions = [i for i in range(len(questions)) if i not in QuestionPopup.used_questions]

        if not self.unused_questions:
            QuestionPopup.used_questions = set()
            self.unused_questions = list(range(len(questions)))

        self.chosen_index = random.choice(self.unused_questions)
        QuestionPopup.used_questions.add(self.chosen_index)

        chosen = questions[self.chosen_index]

        # Save question and answers
        self.question_en = chosen["question_en"]
        self.question_ro = chosen["question_ro"]
        self.original_answers_en = chosen["answers_en"]
        self.original_answers_ro = chosen["answers_ro"]
        self.correct_index = chosen["correct_index"]

        # === Randomize answers and track the new correct index
        indices = list(range(len(self.original_answers_en)))
        random.shuffle(indices)

        self.answer_order = indices
        self.answers_en = [self.original_answers_en[i] for i in indices]
        self.answers_ro = [self.original_answers_ro[i] for i in indices]
        self.shuffled_correct_index = indices.index(self.correct_index)

        # === UI-related setup ===
        self.paper_y = SCREEN_HEIGHT
        self.paper_target_y = SCREEN_HEIGHT // 2 - customize_book_image.get_height() // 2
        self.selected_language = game_data["language"]
        self.selected_index = -1
        self.font = pygame.font.Font(FONT_PATH, 37)
        self.text_color = (20, 15, 10)
        self.background = None
        self.answer_rects = []

        self.char_index = 0
        self.typing_speed = 0.5
        self.typing_progress = 0.0

        self.question_index = self.chosen_index

        self.hint_visible = False
        self.hint_y = -hint_image.get_height()
        self.hint_target_y = -40
        self.hint_slide_speed = 8

        self.hint_anim_progress = 0.0  # 0 to 1
        self.hint_exit = False
        self.hint_anim_frames = 25

        self.hint_char_index = 0
        self.hint_typing_speed = 0.5
        self.hint_typing_progress = 0.0
        
        self.hint_prefix = "Need a hint?" if self.selected_language == "EN" else "Ai nevoie de indiciu?"
        self.hint_text = chosen["hint_en"] if self.selected_language == "EN" else chosen["hint_ro"]
        self.hint_message = self.hint_prefix + "\n\n" + self.hint_text

        self.hint_font = pygame.font.Font(FONT_PATH, 21)
        self.hint_color = self.text_color

        self.hint_entered = False
        self.exiting = False






    def slide_in(self):
        self.background = screen.copy()

        duration_frames = 45
        start_y = SCREEN_HEIGHT
        end_y = self.paper_target_y

        book_shuffle_sound.play()

        for frame in range(duration_frames):
            updateExitLoop()
            t = frame / duration_frames
            eased_t = 1 - (1 - t) ** 3
            self.paper_y = start_y + (end_y - start_y) * eased_t

            screen.blit(self.background, (0, 0))
            img_rect = customize_book_image.get_rect(center=(SCREEN_WIDTH // 2, self.paper_y + customize_book_image.get_height() // 2))
            screen.blit(customize_book_image, img_rect.topleft)


            self.draw_text()
        
            pygame.display.update()
            clock.tick(60)

        book_shuffle_sound.fadeout(500)
        self.paper_y = end_y



    def slide_out(self):
        self.exiting = True

        if self.hint_visible or self.hint_entered:
            self.hint_exit = True
            self.hint_anim_progress = 0

        game_data["language"] = self.selected_language

        duration_frames = 45
        start_y = self.paper_target_y
        end_y = SCREEN_HEIGHT

        book_shuffle_sound.play()

        for frame in range(duration_frames):
            updateExitLoop()

            t = frame / duration_frames
            eased_t = 1 - (1 - t) ** 3
            self.paper_y = start_y + (end_y - start_y) * eased_t

            screen.blit(self.background, (0, 0))
            img_rect = customize_book_image.get_rect(center=(SCREEN_WIDTH // 2, self.paper_y + customize_book_image.get_height() // 2))
            screen.blit(customize_book_image, img_rect.topleft)

            self.draw_text()

            pygame.display.update()
            clock.tick(60)


        book_shuffle_sound.fadeout(500)
        self.paper_y = end_y
       

    def draw_text(self):
        full_text = self.question_en if self.selected_language == "EN" else self.question_ro
        current_text = full_text[:self.char_index]

        # === Message formatting like CustomizeScreen ===
        font = self.font
        wrap_width = 340

        lines = []
        for paragraph in current_text.strip().split("\n\n"):
            words = paragraph.strip().split()
            current_line = ""
            is_first_line = True

            for word in words:
                test_line = current_line + word + " "
                effective_width = wrap_width
                if font.size(test_line)[0] <= effective_width:
                    current_line = test_line
                else:
                    lines.append(("    " + current_line.strip()) if is_first_line else current_line.strip())
                    current_line = word + " "
                    is_first_line = False

            if current_line:
                lines.append(("    " + current_line.strip()) if is_first_line else current_line.strip())
            lines.append("<PARAGRAPH_BREAK>")

        # === Draw the lines ===
        start_x = SCREEN_WIDTH // 2 - 380
        start_y = self.paper_y + 200
        line_spacing = 5
        paragraph_spacing = 25
        y_offset = 0

        for line in lines:
            if line == "<PARAGRAPH_BREAK>":
                y_offset += paragraph_spacing
                continue
            text_surf = font.render(line, True, self.text_color)
            screen.blit(text_surf, (start_x, start_y + y_offset))
            y_offset += font.get_height() + line_spacing

        # === Only show buttons AFTER animation ===
        if self.char_index >= len(full_text):
            self.draw_buttons()

        if not self.exiting and (self.hint_visible and self.char_index >= len(full_text)) or self.hint_entered:
            # Animation logic
            t = self.hint_anim_progress / self.hint_anim_frames
            eased = (t * t * t) if self.hint_exit else (1 - (1 - t) ** 3)
            self.hint_y = (
                self.hint_target_y - eased * (hint_image.get_height() + 20)
                if self.hint_exit else
                -hint_image.get_height() + eased * (self.hint_target_y + hint_image.get_height())
            )

            hint_x = SCREEN_WIDTH - hint_image.get_width()
            screen.blit(hint_image, (hint_x, self.hint_y))

            # === NEW HINT RENDERING LOGIC ===
            hint_lines = []

            # Add the hint prefix as a standalone line
            hint_lines.append(self.hint_prefix)
            hint_lines.append("")  # blank line for spacing

            # Wrap the actual hint text manually
            hint_text_words = self.hint_text.split()
            current_line = ""
            for word in hint_text_words:
                test_line = current_line + word + " "
                if self.hint_font.size(test_line)[0] < hint_image.get_width() - 90:
                    current_line = test_line
                else:
                    hint_lines.append(current_line.strip())
                    current_line = word + " "
            if current_line:
                hint_lines.append(current_line.strip())

            # Clip logic
            text_height = self.hint_font.get_height()
            max_lines = 10
            clip_height = max_lines * text_height + 10 + 5

            clip_rect = pygame.Rect(hint_x + 10, self.hint_y + 10, hint_image.get_width() - 20, clip_height)
            surface = pygame.Surface(clip_rect.size, pygame.SRCALPHA)

            # Draw hint text
            for i, line in enumerate(hint_lines[:max_lines]):
                text_surf = self.hint_font.render(line, True, self.hint_color)
                surface.blit(text_surf, (40, 40 + i * text_height))

            screen.blit(surface, clip_rect.topleft)


            if self.hint_anim_progress < self.hint_anim_frames:
                self.hint_anim_progress += 1
            else:
                self.hint_entered = True




    def draw_buttons(self):
        def wrap_text(text, font, max_width):
            words = text.split()
            lines, line = [], ""
            for word in words:
                test = line + word + " "
                if font.size(test)[0] <= max_width:
                    line = test
                else:
                    lines.append(line.strip())
                    line = word + " "
            if line:
                lines.append(line.strip())
            return lines

        def draw_button_box(rect, bg, border, shadow):
            shadow_rect = rect.copy().move(3, 3)
            pygame.draw.rect(screen, shadow, shadow_rect, border_radius=8)
            pygame.draw.rect(screen, bg, rect, border_radius=8)
            pygame.draw.rect(screen, border, rect, width=2, border_radius=8)

        def render_text(lines, rect, font, color, spacing):
            text_height = font.get_height()
            for j, line in enumerate(lines):
                surf = font.render(line, True, color)
                x = rect.x + (rect.width - surf.get_width()) // 2
                y = rect.y + 10 + j * (text_height + spacing)
                screen.blit(surf, (x, y))

        # === Setup ===
        answers = self.answers_en if self.selected_language == "EN" else self.answers_ro
        self.answer_rects.clear()
        font = pygame.font.Font(FONT_PATH, 32)

        padding_x = 24
        line_spacing = 6
        max_width = 300
        button_spacing = 24
        text_color = (255, 228, 180)
        default_bg = (70, 40, 20)
        border_color = (200, 120, 60)
        shadow_color = (0, 0, 0, 100)
        wrong_bg = (130, 30, 30)

        center_x = SCREEN_WIDTH // 2 + 210
        top_y = self.paper_y + 210

        # Get wrong index if exists
        wrong_indices = set()
        if self.question_index in wrong_answers_memory:
            for original_wrong in wrong_answers_memory[self.question_index]:
                if original_wrong != self.correct_index and original_wrong in self.answer_order:
                    wrong_indices.add(self.answer_order.index(original_wrong))




        for i, ans in enumerate(answers):
            lines = wrap_text(ans, font, max_width)
            text_height = font.get_height()
            button_height = len(lines) * (text_height + line_spacing) - line_spacing + 20
            button_width = min(max_width + padding_x * 2, SCREEN_WIDTH - 100)

            rect = pygame.Rect(center_x - button_width // 2, top_y, button_width, button_height)

            # Apply red if previously wrong
            bg_color = wrong_bg if i in wrong_indices else default_bg

            draw_button_box(rect, bg_color, border_color, shadow_color)
            render_text(lines, rect, font, text_color, line_spacing)

            self.answer_rects.append((rect, i))
            top_y += button_height + button_spacing

        # === Language button ===
        lang_text = "Română" if self.selected_language == "EN" else "English"
        lang_surf = font.render(lang_text, True, text_color)
        lang_width = lang_surf.get_width() + padding_x * 2
        lang_height = 52
        lang_x = SCREEN_WIDTH // 2 + 220
        lang_y = top_y + 10

        lang_rect = pygame.Rect(lang_x, lang_y, lang_width, lang_height)
        draw_button_box(lang_rect, default_bg, border_color, shadow_color)
        screen.blit(lang_surf, (
            lang_rect.x + (lang_width - lang_surf.get_width()) // 2,
            lang_rect.y + (lang_height - lang_surf.get_height()) // 2
        ))

        self.lang_rect = lang_rect
        self.hint_visible = len(wrong_indices) > 0



    def run(self):
        self.slide_in()
        running = True

        while running:
            screen.blit(self.background, (0, 0))
            img_rect = customize_book_image.get_rect(center=(SCREEN_WIDTH // 2, self.paper_y + customize_book_image.get_height() // 2))
            screen.blit(customize_book_image, img_rect.topleft)

            # Typewriter animation for question text
            full_question = self.question_en if self.selected_language == "EN" else self.question_ro
            if self.char_index < len(full_question):
                self.typing_progress += self.typing_speed
                while self.typing_progress >= 1:
                    self.char_index += 1
                    self.typing_progress -= 1

            if self.hint_visible and self.char_index >= len(full_question):
                if self.hint_char_index < len(self.hint_message):
                    self.hint_typing_progress += self.hint_typing_speed
                    while self.hint_typing_progress >= 1:
                        self.hint_char_index += 1
                        self.hint_typing_progress -= 1


            self.draw_text()

            # === Cursor hover handling ===
            hovering = False
            mouse_pos = pygame.mouse.get_pos()

            if self.char_index >= len(self.question_en if self.selected_language == "EN" else self.question_ro):
                for rect, _ in self.answer_rects:
                    if rect.collidepoint(mouse_pos):
                        hovering = True
                        break

                if hasattr(self, "lang_rect") and self.lang_rect.collidepoint(mouse_pos):
                    hovering = True

            if hovering:
                cursor.set_hover()
            else:
                cursor.set_idle()


            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.char_index >= len(self.question_en if self.selected_language == "EN" else self.question_ro):
                        if hasattr(self, "lang_rect") and self.lang_rect.collidepoint(mouse_pos):
                            self.selected_language = "RO" if self.selected_language == "EN" else "EN"

                            # Restart typing animations
                            self.char_index = 0
                            self.typing_progress = 0.0
                            self.hint_char_index = 0
                            self.hint_typing_progress = 0.0

                            # Update hint
                            self.hint_prefix = "Need a hint?" if self.selected_language == "EN" else "Ai nevoie de indiciu?"
                            self.hint_text = questions[self.question_index]["hint_en"] if self.selected_language == "EN" else questions[self.question_index]["hint_ro"]
                            self.hint_message = self.hint_prefix + "\n\n" + self.hint_text

                            pygame.display.update()

                    for rect, i in self.answer_rects:
                        if rect.collidepoint(mouse_pos):
                            self.selected_index = i
                            running = False

                elif event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
                    running = False

            pygame.display.update()
            clock.tick(60)

        was_correct = (self.selected_index == self.shuffled_correct_index)
        
        if not was_correct:
            wrong_answear_sound.set_volume(0.5)
            wrong_answear_sound.play()
            wrongs = wrong_answers_memory.setdefault(self.question_index, set())
            
            original_index = self.answer_order[self.selected_index]
            wrongs.add(original_index)
        
        if was_correct and self.question_index in wrong_answers_memory:
            del wrong_answers_memory[self.question_index]

        if was_correct:
            correct_answear_sound.set_volume(0.5)
            correct_answear_sound.play()

        self.slide_out()
        is_last = len(QuestionPopup.used_questions) == len(questions)

        return was_correct, is_last

