import pygame
import random
import copy

from lib.config import *
from lib.assets import *

class CloudTransition:
    def __init__(self, num_cols=5, num_rows=5, spacing_x=300, spacing_y=270):
        self.num_cols = num_cols
        self.num_rows = num_rows
        self.spacing_x = spacing_x
        self.spacing_y = spacing_y

        self.clouds = []
        self.target_positions = []



    def create_clouds(self, speed_multiplier=3.0):
        """Should be called ONCE before enter/exit. Sets layout and start state."""
        self.clouds = []
        self.target_positions = []

        current_y = -250
        for row in range(self.num_rows):
            current_x = -200
            row_spacing_y = random.randint(150, 200)

            for col in range(self.num_cols):
                col_spacing_x = random.randint(350, 400)

                x = current_x
                y = current_y
                self.target_positions.append((x, y))

                # Start from below screen
                start_y = SCREEN_HEIGHT + random.randint(100, 300)

                scale = random.uniform(0.9, 1.2)
                scaled_image = pygame.transform.scale(
                    cloud_image,
                    (
                        int(cloud_image.get_width() * scale),
                        int(cloud_image.get_height() * scale)
                    )
                )

                base_speed = random.uniform(2.5, 4.0) * speed_multiplier

                self.clouds.append({
                    'start_pos': [x, start_y],
                    'pos': [x, start_y],  # start position
                    'target': [x, y],     # where to land
                    'image': scaled_image,
                    'speed': base_speed

                })

                current_x += col_spacing_x
            current_y += row_spacing_y



    def move_clouds(self, direction='up'):
        for cloud in self.clouds:
            if direction == 'up':
                if cloud['pos'][1] > cloud['target'][1]:
                    cloud['pos'][1] -= cloud['speed']
                    if cloud['pos'][1] < cloud['target'][1]:
                        cloud['pos'][1] = cloud['target'][1]
            elif direction == 'down':
                cloud['pos'][1] += cloud['speed']
        
        if direction == "up":
            saved_clouds.clear()
            saved_clouds.append([
                {
                    'start_pos': cloud['start_pos'][:],
                    'pos': cloud['pos'][:],
                    'target': cloud['target'][:],
                    'image': cloud['image'],  # safe to reuse
                    'speed': cloud['speed'],
                }
                for cloud in self.clouds
            ])

    def draw_clouds(self, background=None):
        if background:
            screen.blit(background, (0, 0))
        for cloud in self.clouds:
            screen.blit(cloud['image'], cloud['pos'])

    def enter(self, background=None):
        """Animate from start_pos to target"""
        clock = pygame.time.Clock()

        cursor.hide()
        wind_sound.play()

        while not self._clouds_reached_targets():
            updateExitLoop()

            self.move_clouds('up')
            self.draw_clouds(background)
            pygame.display.update()
            clock.tick(60)
        
        wind_sound.fadeout(500)

    def exit(self, background=None):
        """Animate from target to off-screen"""
        clock = pygame.time.Clock()

        wind_sound.play()

        self.clouds = [
            {
                'start_pos': cloud['start_pos'][:],
                'pos': cloud['pos'][:],
                'target': cloud['target'][:],
                'image': cloud['image'],
                'speed': cloud['speed'],
            }
            for cloud in saved_clouds[0]
        ]

        while not self._clouds_out_of_view():
            updateExitLoop()
            
            self.move_clouds('down')
            self.draw_clouds(background)
            pygame.display.update()
            clock.tick(60)
        
        cursor.show()
        wind_sound.fadeout(500)


    def _clouds_reached_targets(self):
        return all(cloud['pos'][1] <= cloud['target'][1] for cloud in self.clouds)

    def _clouds_out_of_view(self):
        return all(cloud['pos'][1] > screen.get_height() for cloud in self.clouds)

    def reset_to_targets(self):
        for cloud in self.clouds:
            cloud['pos'][1] = cloud['target'][1]
