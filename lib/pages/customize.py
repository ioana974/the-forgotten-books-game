import pygame
import sys
import random
from lib.config import *
from lib.assets import *
from lib.util.animations.stamp_animation import *

class CustomizeScreen:
    def __init__(self):
        self.paper_y = SCREEN_HEIGHT
        self.paper_target_y = SCREEN_HEIGHT // 2 - customize_book_image.get_height() // 2
        self.font = pygame.font.Font(FONT_PATH, 38)
        self.text_color = (25, 20, 15)
        self.sound = None
        self.background = None
        self.full_text = "\tThis feature will be available in a later release.\n\n\tCheck back in a future update!"
        self.char_index = 0
        self.typing_speed = 0.3
        self.typing_progress = 0.0
        self.writing = False

        self.stamp_animator = None
        self.stamp_placed = False

        self.channel = None

        

    def slide_in(self):
        self.background = screen.copy()

        duration_frames = 45
        start_y = SCREEN_HEIGHT
        end_y = self.paper_target_y

        if not game_data["narrator_oh_you_found_this"] and not self.channel == None:
            self.channel.unpause()
            self.channel.set_volume(0)

        book_shuffle_sound.play()

        for frame in range(duration_frames):
            updateExitLoop()
            t = frame / duration_frames
            eased_t = 1 - (1 - t) ** 3
            self.paper_y = start_y + (end_y - start_y) * eased_t


            # Fade in volume synced with animation
            if not game_data["narrator_oh_you_found_this"] and not self.channel == None:
                self.channel.set_volume(t)  # Use eased volume for smoother ramp-up


            screen.blit(self.background, (0, 0))
            img_rect = customize_book_image.get_rect(center=(SCREEN_WIDTH // 2, self.paper_y + customize_book_image.get_height() // 2))
            screen.blit(customize_book_image, img_rect.topleft)


            self.draw_text(self.char_index)

            if self.stamp_animator:
                self.stamp_animator.update_position(
                    (SCREEN_WIDTH // 2 + 200, self.paper_y + 430)
                )
                self.stamp_animator.update()

            self.draw_text(0)  # show only the title during slide
            pygame.display.update()
            clock.tick(60)

        book_shuffle_sound.fadeout(500)
        self.paper_y = end_y



    def slide_out(self):
        duration_frames = 45
        start_y = self.paper_target_y
        end_y = SCREEN_HEIGHT

        if not game_data["narrator_oh_you_found_this"]: 
            if self.channel.get_busy():
                initial_volume = self.channel.get_volume()
            else:
                initial_volume = 100

        book_shuffle_sound.play()

        for frame in range(duration_frames):
            updateExitLoop()

            t = frame / duration_frames
            eased_t = 1 - (1 - t) ** 3
            self.paper_y = start_y + (end_y - start_y) * eased_t

            # Fade audio
            if not game_data["narrator_oh_you_found_this"]:
                if self.channel.get_busy():
                    new_volume = initial_volume * (1 - t)
                    self.channel.set_volume(new_volume)

            screen.blit(self.background, (0, 0))
            img_rect = customize_book_image.get_rect(center=(SCREEN_WIDTH // 2, self.paper_y + customize_book_image.get_height() // 2))
            screen.blit(customize_book_image, img_rect.topleft)

            self.draw_text(self.char_index)

            if self.stamp_animator:
                self.stamp_animator.update_position(
                    (SCREEN_WIDTH // 2 + 200, self.paper_y + 430)
                )
                self.stamp_animator.update()

            pygame.display.update()
            clock.tick(60)


        if not game_data["narrator_oh_you_found_this"]:
            self.channel.pause()

        book_shuffle_sound.fadeout(500)
        self.paper_y = end_y
       

    def draw_text(self, char_index):
        # === Title ===
        title_font = pygame.font.Font(FONT_PATH, 70)
        title_text = "CUSTOMIZE"
        title_surf = title_font.render(title_text, True, self.text_color)
        title_x = SCREEN_WIDTH // 2 - 380
        title_y = self.paper_y + 190
        screen.blit(title_surf, (title_x, title_y))
        screen.blit(title_surf, (title_x + 1, title_y))

        # === Message ===
        font = pygame.font.Font(FONT_PATH, 38)
        partial_text = self.full_text[:char_index]
        wrap_width = 340
        indent_width = font.size("    ")[0]  # Tab indent space

        lines = []
        for paragraph in partial_text.strip().split("\n\n"):
            words = paragraph.strip().split()
            current_line = ""
            is_first_line = True

            for word in words:
                test_line = current_line + word + " "
                effective_width = wrap_width - (indent_width if is_first_line else 0)
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
        start_y = self.paper_y + 300
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

    def run(self):
        self.slide_in()

        if self.stamp_animator:
            self.stamp_animator.update_position((SCREEN_WIDTH // 2 + 200, self.paper_y + 430))

        running = True
        while running:
            screen.blit(self.background, (0, 0))
            img_rect = customize_book_image.get_rect(center=(SCREEN_WIDTH // 2, self.paper_y + customize_book_image.get_height() // 2))
            screen.blit(customize_book_image, img_rect.topleft)

            if self.char_index < len(self.full_text):
                if not self.writing:
                    self.writing = True
                    writing_sound.play()
                    if self.channel == None and not game_data["narrator_oh_you_found_this"]:
                        self.channel = narrator_oh_you_found_this_sound.play()
                self.typing_progress += self.typing_speed
                while self.typing_progress >= 1:
                    self.char_index += 1
                    self.typing_progress -= 1
            elif self.writing:
                self.writing = False
                game_data["narrator_oh_you_found_this"] = True
                writing_sound.fadeout(300)

                if not self.stamp_placed:
                    stamp_pos = (SCREEN_WIDTH // 2 + 200, self.paper_y + 430)  # adjust as needed
                    self.stamp_animator = StampAnimation(stamp_pos, final_angle=-18, final_scale=1.0)
                    self.stamp_placed = True


            self.draw_text(self.char_index)
            if self.stamp_animator:
                self.stamp_animator.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        if self.writing:
                            self.writing = False
                            writing_sound.fadeout(300)

                        running = False
                    elif event.key == pygame.K_ESCAPE:
                        save_progress()
                        pygame.quit()
                        sys.exit()

            pygame.display.update()
            clock.tick(60)

        self.slide_out()
        return "start"