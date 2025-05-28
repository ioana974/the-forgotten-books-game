import pygame
from lib.assets import *

class Sadogandul(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.position = pygame.Vector2(pos)

        # Animation frames
        self.frames = self._split_sprite_sheet(forrest_spirit_image)
        self.frame_index = 0
        self.anim_timer = 0
        self.anim_speed = 400  # Slower animation (ms per frame)

        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos)

        # Cloud
        self.cloud_image = forrest_spirit_cloud_image
        self.cloud_offset = pygame.Vector2(0, self.rect.height // 2 - 5)

    def _split_sprite_sheet(self, sheet):
        frames = []
        sheet_width, sheet_height = sheet.get_size()
        frame_width = sheet_width // 2
        frame_height = sheet_height // 2

        for row in range(2):
            for col in range(2):
                # Get base frame
                rect = pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height)
                frame = sheet.subsurface(rect).copy()

                # Trim 3 pixels from all sides
                trimmed = frame.subsurface(pygame.Rect(3, 3, frame_width - 6, frame_height - 6)).copy()
                frames.append(trimmed)

        return frames

    def update(self, dt):
        self.anim_timer += dt
        if self.anim_timer >= self.anim_speed:
            self.anim_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]

    def draw(self, surface, camera_x=0, camera_y=0):
        screen_x = self.position.x - camera_x
        screen_y = self.position.y - camera_y

        # Draw spirit
        frame_pos = (screen_x - self.image.get_width() // 2,
                     screen_y - self.image.get_height() // 2)
        surface.blit(self.image, frame_pos)

        # Draw cloud on top
        cloud_pos = (screen_x - self.cloud_image.get_width() // 2,
                     screen_y - self.cloud_image.get_height() // 2 + self.cloud_offset.y)
        surface.blit(self.cloud_image, cloud_pos)

    def get_sprite(self):
        return {
        "custom_draw": True,  # tells the main loop not to draw this directly
        "sort_y": self.position.y + 100,
        "type": "sadogandul"
    }
