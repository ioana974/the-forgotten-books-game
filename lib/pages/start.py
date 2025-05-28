import pygame
import sys
import math

import lib.config as cfg
from lib.ui import *
from lib.assets import *
from lib.util.animations.cloud_transition import *
from lib.util.animations.animated_logo import *
from lib.util.animations.animated_paper import *
from lib.util.music_manager import *
from lib.util.save_data import *


class StartScreen:
    def __init__(self):
        self.animated_logo = AnimatedTitle(
            rows=2,
            cols=2,
            frame_duration=300
        )

        self.buttons = [
            {
                "label": "START",
                "icon": "sword_icon_image",
                "action": "level_selection",
                "animated_paper": AnimatedPaper(scale=0.4, length=200),
                "hovered": False
            },
            {
                "label": "CUSTOMIZE",
                "icon": "gear_icon_image",
                "action": "customize",
                "animated_paper": AnimatedPaper(scale=0.4, length=200),
                "hovered": False
            },
            {
                "label": "RULES",
                "icon": "book_icon_image",
                "action": "rules",
                "animated_paper": AnimatedPaper(scale=0.4, length=200),
                "hovered": False
            },
            {
                "label": "MUSIC: ON",
                "icon": "music_icon_image",
                "action": "toggle_music",
                "animated_paper": AnimatedPaper(scale=0.4, length=200),
                "hovered": False
            }
        ]

        music_manager.play()
        music_manager.is_playing = True

        if not game_data["music_on"]:
            music_manager.pause()
            self.buttons[3]["label"] = "MUSIC: OFF"

        if not game_data["narrator_intro_done"]:
            game_data["unlocked_levels"][0] = False
            self.channel = narrator_intro_sound.play()
        else:
            self.channel = None



    def open_page(self, page_number):
        running = True
        while running:
            updateExitLoop()

            scaled_bg = pygame.transform.scale(start_background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(scaled_bg, (0, 0))

            draw_button(f"Page {page_number}", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50, 300, 100)
            draw_button('Back', 10, 10, 150, 50)

            mouse_x, mouse_y = pygame.mouse.get_pos()
            if pygame.mouse.get_pressed()[0]:
                if 10 <= mouse_x <= 160 and 10 <= mouse_y <= 60:
                    return

            pygame.display.update()
            clock.tick(60)

    def run(self):
        target_action = None
        if cfg.last_screen == "customize" and not game_data["narrator_intro_done"]:
            self.channel.unpause()

        if cfg.last_screen == 'level_selection':
            screen.fill((0, 0, 0))
            scaled_bg = pygame.transform.scale(start_background_image, (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
            screen.blit(scaled_bg, (0, 0))

            # Create temp surface for all UI
            content_surface = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA)
            
            # Draw logo
            self.animated_logo.update()
            logo_x = 40
            logo_y = SCREEN_HEIGHT // 2 - self.animated_logo.rect.height // 2
            self.animated_logo.draw(content_surface, (logo_x, logo_y))

            left_pressed = pygame.mouse.get_pressed()[0]
            just_clicked = mouse_click_edge.update(left_pressed)

            # Buttons
            num_buttons = len(self.buttons)
            spacing = 20
            top_bottom_margin = 80
            available_height = cfg.SCREEN_HEIGHT - 2 * top_bottom_margin
            button_height = (available_height - (spacing * (num_buttons - 1))) // num_buttons
            start_x = cfg.SCREEN_WIDTH // 2 + 50
            total_height = num_buttons * button_height + (num_buttons - 1) * spacing
            start_y = cfg.SCREEN_HEIGHT // 2 - total_height // 2

            for i, btn in enumerate(self.buttons):
                updateExitLoop()

                x = start_x
                y = start_y + i * (button_height + spacing)

                hovered = draw_button(
                    text=btn["label"],
                    x=x,
                    y=y,
                    height=button_height,
                    icon=getattr(sys.modules['lib.assets'], btn["icon"]),
                    animated_paper=btn["animated_paper"],
                    button_state=btn,
                    surface=content_surface
                )

            # Blit all contents
            screen.blit(content_surface, (0, 0))

            transition = CloudTransition()
            transition.exit(background=screen.copy())

        while True:
            updateExitLoop()

            screen.fill((0, 0, 0))
            scaled_bg = pygame.transform.scale(start_background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(scaled_bg, (0, 0))

            # Create temp surface for all UI
            content_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            
            # Draw logo
            self.animated_logo.update()
            logo_x = 40
            logo_y = SCREEN_HEIGHT // 2 - self.animated_logo.rect.height // 2
            self.animated_logo.draw(content_surface, (logo_x, logo_y))

            left_pressed = pygame.mouse.get_pressed()[0]
            just_clicked = mouse_click_edge.update(left_pressed)

            # Buttons
            num_buttons = len(self.buttons)
            spacing = 20
            top_bottom_margin = 80
            available_height = SCREEN_HEIGHT - 2 * top_bottom_margin
            button_height = (available_height - (spacing * (num_buttons - 1))) // num_buttons
            start_x = SCREEN_WIDTH // 2 + 50
            total_height = num_buttons * button_height + (num_buttons - 1) * spacing
            start_y = SCREEN_HEIGHT // 2 - total_height // 2

            general_hover = False

            for i, btn in enumerate(self.buttons):
                x = start_x
                y = start_y + i * (button_height + spacing)

                hovered = draw_button(
                    text=btn["label"],
                    x=x,
                    y=y,
                    height=button_height,
                    icon=getattr(sys.modules['lib.assets'], btn["icon"]),
                    animated_paper=btn["animated_paper"],
                    button_state=btn,
                    surface=content_surface
                )

                if hovered:
                    general_hover = True

                if hovered and just_clicked:
                    action = btn["action"]
                    if action == "toggle_music":
                        music_manager.toggle()
                        
                        game_data["music_on"] = music_manager.is_playing
                        btn["label"] = "MUSIC: ON" if music_manager.is_playing else "MUSIC: OFF"
                    else:
                        target_action = action

            if just_clicked:
                cursor.set_idle()
            elif general_hover:
                if cursor.getState() == 0:
                    cursor.set_hover()
            else:
                if cursor.getState() == 1:
                    cursor.set_idle()

            if not game_data["narrator_intro_done"]: 
                if not self.channel.get_busy():
                    game_data["narrator_intro_done"] = True
                    game_data["unlocked_levels"][0] = True

            # Blit all contents
            screen.blit(content_surface, (0, 0))
            pygame.display.update()
            clock.tick(60)

            # --- Trigger transition ---
            if target_action:
                # Stop scroll sounds from all papers before transitioning
                for button in self.buttons:  # assuming self.buttons holds all button data
                    paper = button.get("animated_paper")
                    if paper.sound != None:
                        paper.sound.fadeout(700)

                if target_action == "level_selection":
                    transition = CloudTransition()

                    transition. create_clouds()
                    transition.enter(background=screen.copy())
                elif target_action != "customize":
                    self.slide_out(content_surface)
                elif not self.channel == None:
                    self.channel.pause()

                return target_action



    def slide_out(self, surface):
        steps = 60  # total animation frames

        if not game_data["narrator_intro_done"]: 
            if self.channel.get_busy():
                initial_volume = self.channel.get_volume()
            else:
                initial_volume = 100

        wind_sound.play()

        for i in range(steps + 1):
            updateExitLoop()

            t = i / steps  # normalized 0 to 1
            eased = -0.5 * (math.cos(math.pi * t) - 1)  # easeInOutQuad
            shift = int(eased * (SCREEN_WIDTH + 200))  # 200 adds a bit of overshoot

            # Fade audio
            if not game_data["narrator_intro_done"]:
                if self.channel.get_busy():
                    new_volume = initial_volume * (1 - t)
                    self.channel.set_volume(new_volume)

            # Draw background
            scaled_bg = pygame.transform.scale(start_background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(scaled_bg, (0, 0))

            # Move content left with easing
            screen.blit(surface, (-shift, 0))

            pygame.display.update()
            clock.tick(60)


        if not game_data["narrator_intro_done"]:
            self.channel.pause()
        wind_sound.fadeout(1500)

    def slide_in(self):
        wind_sound.play()

        if not game_data["narrator_intro_done"]:
            self.channel.unpause()
            self.channel.set_volume(0)

        # Prepare the full content surface to slide in
        content_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        # Draw logo
        self.animated_logo.update()
        logo_x = 40
        logo_y = SCREEN_HEIGHT // 2 - self.animated_logo.rect.height // 2
        self.animated_logo.draw(content_surface, (logo_x, logo_y))

        # Draw buttons
        num_buttons = len(self.buttons)
        spacing = 20
        top_bottom_margin = 80
        available_height = SCREEN_HEIGHT - 2 * top_bottom_margin
        button_height = (available_height - (spacing * (num_buttons - 1))) // num_buttons
        start_x = SCREEN_WIDTH // 2 + 50
        total_height = num_buttons * button_height + (num_buttons - 1) * spacing
        start_y = SCREEN_HEIGHT // 2 - total_height // 2

        for i, btn in enumerate(self.buttons):
            updateExitLoop()
            x = start_x
            y = start_y + i * (button_height + spacing)
            draw_button(
                text=btn["label"],
                x=x,
                y=y,
                height=button_height,
                icon=getattr(sys.modules['lib.assets'], btn["icon"]),
                animated_paper=btn["animated_paper"],
                button_state=btn,
                surface=content_surface
            )

        # Slide in from the left with audio fade-in
        steps = 60
        for i in range(steps + 1):
            updateExitLoop()

            t = i / steps
            eased = -0.5 * (math.cos(math.pi * t) - 1)  # easeInOut
            shift = int((1 - eased) * (SCREEN_WIDTH + 200))

            # Fade in volume synced with animation
            if not game_data["narrator_intro_done"]:
                self.channel.set_volume(eased)  # Use eased volume for smoother ramp-up

            scaled_bg = pygame.transform.scale(start_background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(scaled_bg, (0, 0))
            screen.blit(content_surface, (-shift, 0))
            pygame.display.update()
            clock.tick(60)

        wind_sound.stop()

