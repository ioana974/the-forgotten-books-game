import pygame
import random
import sys

from lib.config import *
from lib.assets import *
from lib.util.item_drop import *

class RulesScreen:
    def __init__(self):
        self.paper_y = -rule_paper_image.get_height()
        self.paper_target_y = -117
        self.scroll_speed = 30

        self.visible_lines = []

        self.item_images = [ book_item_image, key_item_image, candle_item_image, lock_item_image]
        self.item_drops = []

        self.sound = None
        self.writing = False

        self.scroll_y = 0
        self.font = pygame.font.Font(FONT_PATH, 40)
        self.text_color = (30, 20, 10)
        self.wrap_width = SCREEN_WIDTH - 160
        self.rules_text = (
            "In the beginning, the Forgotten Books were scattered across the realms. "
            "Each book holds ancient power, a piece of the truth long buried in myth.\n\n"
            "Your mission is to retrieve these relics, protect their secrets, and avoid the shadow forces "
            "who seek to corrupt the knowledge within.\n\n"
            "Navigate challenges and solve riddles, but choose wisely: "
            "every decision shapes the fate of the known world.\n\n"
        )
        self.rendered_lines = self.wrap_text(self.rules_text, screen.get_width() * 0.48)
        self.line_surfaces = [self.font.render(line, True, self.text_color) for line in self.rendered_lines]
        self.line_height = self.font.get_height() + 10


    def wrap_text(self, text, max_width):
        paragraphs = text.strip().split("\n\n")
        lines = []
        indent_spacing = 50

        for paragraph in paragraphs:

            words = paragraph.strip().split()
            current_line = ""
            is_first_line = True

            for word in words:

                test_line = current_line + word + " "
                effective_width = max_width - indent_spacing if is_first_line else max_width
                test_surface = self.font.render(test_line, True, self.text_color)

                if test_surface.get_width() <= effective_width:
                    current_line = test_line
                else:
                    if is_first_line:
                        lines.append("[INDENT] " + current_line.strip())
                        is_first_line = False
                    else:
                        lines.append(current_line.strip())
                    current_line = word + " "

            if current_line:
                lines.append(("[INDENT] " if is_first_line else "") + current_line.strip())

            lines.append("<PARAGRAPH_BREAK>")

        return lines
    


    def slide_in(self):
        duration_frames = 60
        start_y = -rule_paper_image.get_height()
        end_y = self.paper_target_y

        if self.sound == None:
            self.sound = random.choice(paper_flutter_sounds)
            self.sound.play()

        for frame in range(duration_frames):
            updateExitLoop()

            t = frame / duration_frames
            eased_t = 1 - (1 - t) ** 3
            self.paper_y = start_y + (end_y - start_y) * eased_t

            scaled_bg = pygame.transform.scale(start_background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(scaled_bg, (0, 0))
            screen.blit(rule_paper_image, (0, self.paper_y))
            pygame.display.update()
            clock.tick(60)

        self.paper_y = end_y

        if self.sound != None:
            self.sound.stop()
            self.sound = None

        # === Setup Drops ===
        item_configs = [
            dict(x=SCREEN_WIDTH * 0.70, y=SCREEN_HEIGHT * 0.69, angle=-35, end_angle=11),
            dict(x=SCREEN_WIDTH * 0.71, y=SCREEN_HEIGHT * 0.20, angle=25, end_angle=-11),
            dict(x=SCREEN_WIDTH * 0.90, y=SCREEN_HEIGHT * 0.01, angle=-20, end_angle=45),
            dict(x=SCREEN_WIDTH * 0.86, y=SCREEN_HEIGHT * 0.35, angle=10, end_angle=-5),
        ]
        drop_delay = 45
        self.item_drops = []
        scheduled_drops = []

        for i, (img, cfg) in enumerate(zip(self.item_images, item_configs)):
            scheduled_drops.append({
                "delay": i * drop_delay,
                "drop": ItemDrop(
                    image=img,
                    x=cfg["x"],
                    start_y=-100,
                    target_y=cfg["y"],
                    duration_frames=60,
                    initial_scale=1.6,
                    final_scale=0.5,
                    start_angle=cfg["angle"],
                    end_angle=cfg["end_angle"],
                    bounce_height=12,
                    bounce_duration=20
                )
            })

        # === Animate everything together ===
        full_text = self.rules_text.upper()
        char_index = 0
        typing_speed = 0.3
        typing_progress = 0.0

        max_frames = drop_delay * len(scheduled_drops) + 120
        for frame in range(max_frames):
            updateExitLoop()

            # Launch new item drops
            for drop in scheduled_drops:
                if drop["delay"] == frame:
                    self.item_drops.append(drop["drop"])

            for d in self.item_drops:
                d.update()

            # Text typing
            if char_index < len(full_text):
                if (self.writing == False):
                    self.writing = True
                    narrator_rules_sound.play()
                    writing_sound.play()

                typing_progress += typing_speed
                while typing_progress >= 1:
                    char_index += 1
                    typing_progress -= 1

            partial_text = full_text[:char_index]
            lines = self.wrap_text(partial_text, screen.get_width() * 0.48)

            y_offset = 0
            paragraph_spacing = 30
            indent_spacing = 40
            max_visible_height = rule_paper_image.get_height() - 250
            text_area_top = self.paper_y + 130
            text_area_left = 125

            # === Draw everything ===
            scaled_bg = pygame.transform.scale(start_background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(scaled_bg, (0, 0))
            screen.blit(rule_paper_image, (0, self.paper_y))

            for d in self.item_drops:
                d.draw(screen)

            for line in lines:
                if line == "<PARAGRAPH_BREAK>":
                    y_offset += paragraph_spacing
                    continue

                is_indented = line.startswith("[INDENT]")
                display_text = line.replace("[INDENT]", "").strip()
                indent = indent_spacing if is_indented else 0

                y = text_area_top + y_offset
                if y > self.paper_y + max_visible_height:
                    break

                x = text_area_left + indent
                if not any(v["text"] == display_text and v["y"] == y for v in self.visible_lines):
                    self.visible_lines.append({
                        "text": display_text,
                        "x": x,
                        "y": y,
                        "alpha": 255,
                        "fade_started": False,
                        "fade_progress": 0
                    })

                surface = self.font.render(display_text, True, self.text_color)
                screen.blit(surface, (x, y))
                screen.blit(surface, (x + 1, y))
                y_offset += self.line_height

            pygame.display.update()
            clock.tick(60)

            if char_index >= len(full_text) and all(d.done for d in self.item_drops):
                break

        return char_index, typing_progress

    def slide_out(self):
        fade_duration = 10
        fade_delay_frames = 5
        scroll_done = False

        if (self.writing == True):
            self.writing = False
            narrator_rules_sound.fadeout(1500)
            writing_sound.stop()

        start_y = self.paper_target_y
        end_y = -rule_paper_image.get_height()
        duration_frames = 60

        # === Fade Text Lines ===
        lines_to_fade = list(reversed(self.visible_lines))
        for i, line in enumerate(lines_to_fade):
            line["fade_started"] = False
            line["fade_progress"] = 0
            line["alpha"] = 255
            line["fade_delay"] = i * fade_delay_frames

        frame = 0
        while self.paper_y > -rule_paper_image.get_height() or not scroll_done:
            updateExitLoop()

            scaled_bg = pygame.transform.scale(start_background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(scaled_bg, (0, 0))
            screen.blit(rule_paper_image, (0, self.paper_y))

            all_faded = True
            for line in lines_to_fade:
                text, x, y = line["text"], line["x"], line["y"]
                screen_y = y - self.paper_target_y + self.paper_y

                if not line["fade_started"] and frame >= line["fade_delay"] and screen_y < SCREEN_HEIGHT - 130:
                    line["fade_started"] = True

                if line["fade_started"] and line["alpha"] > 0:
                    all_faded = False
                    line["fade_progress"] += 1
                    
                    fade_ratio = min(1.0, line["fade_progress"] / fade_duration)
                    eased_ratio = 1 - (1 - fade_ratio) ** 3
                    line["alpha"] = max(0, int(255 * (1 - eased_ratio)))

                elif line["alpha"] > 0:
                    all_faded = False

                surface = self.font.render(text, True, self.text_color).convert_alpha()
                surface.set_alpha(line["alpha"])
                screen.blit(surface, (x, screen_y))
                screen.blit(surface, (x + 1, screen_y))

            if frame < duration_frames:
                if self.sound == None:
                    self.sound = random.choice(paper_flutter_sounds)
                    self.sound.play()

                t = frame / duration_frames
                eased_t = 1 - (1 - t) ** 3
                self.paper_y = start_y + (end_y - start_y) * eased_t
            else:
                if self.sound != None:
                    self.sound.stop()
                    self.sound = None

                self.paper_y = end_y
                scroll_done = True


            for d in self.item_drops:

                d.draw(screen)

            pygame.display.update()
            clock.tick(60)
            frame += 1

            if scroll_done and all_faded:
                break

        # === Animate Items Flying Out ===
        random.shuffle(self.item_drops)
        corners = [
            (SCREEN_WIDTH + 150, SCREEN_HEIGHT + 150),  # bottom-right
            (SCREEN_WIDTH + 150, -150),  # top-right
            (-150, -150), # top-left
            (-150, SCREEN_HEIGHT + 150),  # bottom-left
        ]

        for i, drop in enumerate(self.item_drops):
            drop.exit_delay = i * 16
            drop.exit_target = corners[i % len(corners)]
            drop.exit_triggered = False

        frame = 0
        while True:
            updateExitLoop()

            scaled_bg = pygame.transform.scale(start_background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(scaled_bg, (0, 0))
            screen.blit(rule_paper_image, (0, self.paper_y))

            all_done = True
            for drop in self.item_drops:
                if frame >= drop.exit_delay and not drop.exit_triggered:
                    drop.start_exit(drop.exit_target, duration=40)
                    drop.exit_triggered = True

                drop.update()
                drop.draw(screen)

                if drop.exiting:
                    all_done = False

            pygame.display.update()
            clock.tick(60)
            frame += 1

            if all_done:
                break



    def run(self):
        char_index, typing_progress = self.slide_in()

        full_text = self.rules_text.upper()
        typing_speed = 0.3

        max_visible_height = rule_paper_image.get_height() - 250
        text_area_top = self.paper_y + 130
        text_area_left = 125
        line_spacing = 10
        line_height = self.font.get_height() + line_spacing

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        running = False
                    elif event.key == pygame.K_ESCAPE:
                        save_progress()
                        pygame.quit()
                        sys.exit()

            scaled_bg = pygame.transform.scale(start_background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(scaled_bg, (0, 0))
            screen.blit(rule_paper_image, (0, self.paper_y))
        
            for d in self.item_drops:
                d.draw(screen)

            partial_text = full_text[:char_index]
            lines = self.wrap_text(partial_text, screen.get_width() * 0.48)

            y_offset = 0
            paragraph_spacing = 30
            indent_spacing = 40

            for line in lines:
                if line == "<PARAGRAPH_BREAK>":
                    y_offset += paragraph_spacing
                    continue

                is_indented = line.startswith("[INDENT]")
                display_text = line.replace("[INDENT]", "").strip()
                indent = indent_spacing if is_indented else 0

                y = text_area_top + y_offset
                if y > self.paper_y + max_visible_height:
                    break

                x = text_area_left + indent

                if not any(v["text"] == display_text and v["y"] == y for v in self.visible_lines):
                    self.visible_lines.append({
                        "text": display_text,
                        "x": x,
                        "y": y,
                        "alpha": 255,
                        "fade_started": False,
                        "fade_progress": 0
                    })

                surface = self.font.render(display_text, True, self.text_color)
                screen.blit(surface, (x, y))
                screen.blit(surface, (x + 1, y))  # pseudo-bold
                y_offset += line_height

            if char_index < len(full_text):
                typing_progress += typing_speed
                while typing_progress >= 1:
                    char_index += 1
                    typing_progress -= 1
            elif (self.writing == True):
                self.writing = False
                writing_sound.stop()

            pygame.display.update()
            clock.tick(60)

        self.slide_out()
        return "start"
