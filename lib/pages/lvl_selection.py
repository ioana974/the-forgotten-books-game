import pygame
import random

from lib.util.animations.tree_transition import *
from lib.util.animations.cloud_transition import *
from lib.levels.lvl1 import *
from lib.assets import *

class LevelSelectionScreen:
    def __init__(self, channel = None):
        self.running = True
        self.channel = channel

        self.level_icons = level_icons_images
        self.level_positions = [
            (140, 180), (500, 280), (400, 650),
            (710, 470), (1080, 430), (1165, 190)
        ]

        self.level_unlocked = game_data["unlocked_levels"]
        self.lock_icon = level_icons_images[-1]

        self.levels = [
            LevelOne()
        ]




    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.running = False
                elif event.key == pygame.K_ESCAPE:
                    save_progress()
                    pygame.quit()
                    sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                for i, pos in enumerate(self.level_positions):
                    if i < len(self.level_unlocked):
                        icon = self.lock_icon
                        icon_center_x = pos[0] + icon.get_width() // 2
                        icon_center_y = pos[1] + icon.get_height() // 2
                        radius = icon.get_width() // 2 - 20

                        dx = mouse_x - icon_center_x
                        dy = mouse_y - icon_center_y

                        if dx * dx + dy * dy <= radius * radius:
                            # Play one of the lock sounds randomly
                            if self.level_unlocked[i]:
                                enter_level.play()
                                
                                if cursor.getState() == 1:
                                    cursor.set_idle()

                                if i == 0:
                                    start_transition = TreeTransition("assets/images/levels/lvl1/tree_tops.png")
                                    start_transition.enter(background=screen.copy())

                                # Run the level and wait for result
                                result = self.levels[i].run()

                                self.update()
                                self.draw()
                                
                                if i == 0:
                                    start_transition = TreeTransition("assets/images/levels/lvl1/tree_tops.png")
                                    start_transition.exit(background=screen.copy())

                                if game_data["music_on"]:
                                    music_manager.load(0)
                                    music_manager.play()
                                    
                                # Optionally check result
                                if result == "level_completed":
                                    print("Level completed!")  # Add logic if needed
                                elif result == "exit":
                                    self.running = False
                            else:
                                random.choice(lock_sounds).play()
                                
                            break




    def update(self):
        hover_detected = False

        if not game_data["narrator_intro_done"]: 
                if not self.channel.get_busy():
                    game_data["narrator_intro_done"] = True
                    game_data["unlocked_levels"][0] = True

        for i, pos in enumerate(self.level_positions):
            icon = self.level_icons[i] if self.level_unlocked[i] else self.lock_icon
            
            mouse_x, mouse_y = pygame.mouse.get_pos()
            icon_center_x = pos[0] + icon.get_width() // 2
            icon_center_y = pos[1] + icon.get_height() // 2
            radius = icon.get_width() // 2 - 20  # or manually define a custom radius

            dx = mouse_x - icon_center_x
            dy = mouse_y - icon_center_y

            if dx * dx + dy * dy <= radius * radius:
                hover_detected = True


        if hover_detected:
            if cursor.getState() == 0:
                cursor.set_hover()
        else:
            if cursor.getState() == 1:
                cursor.set_idle()


    def draw(self):
        screen.blit(map_background_image, (0, 0))

        for i, pos in enumerate(self.level_positions):
            if i < len(self.level_unlocked) and self.level_unlocked[i]:
                icon = self.level_icons[i]  # 0–5 are level numbers
            else:
                icon = self.lock_icon
            screen.blit(icon, pos)


    def run(self):
        clock = pygame.time.Clock()

        self.draw()

        transition = CloudTransition()
        transition.exit(background=screen.copy())

        self.running = True
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.update()
            clock.tick(60)


        transition = CloudTransition()
        transition. create_clouds()
        transition.enter(background=screen.copy())

        return "start"


