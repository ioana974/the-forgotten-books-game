import pygame
from lib.assets import *

class AnimatedTitle(pygame.sprite.Sprite):
    def __init__(self, rows=2, cols=2, frame_duration=400, target_size=(1024, 1024), scale_up=1.45):
        super().__init__()

        # Scale sprite sheet to target size (e.g., 1024x1024 from original)
        self.sprite_sheet = pygame.transform.smoothscale(logo_sprite_sheet_image, target_size)

        self.frame_width = target_size[0] // cols
        self.frame_height = target_size[1] // rows
        self.rows = rows
        self.cols = cols
        self.total_frames = rows * cols
        self.frame_duration = frame_duration  # slower animation

        self.frames = self._extract_frames(scale_up)
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect()

        self.last_update_time = pygame.time.get_ticks()

    def _extract_frames(self, scale_up):
        frames = []
        for row in range(self.rows):
            for col in range(self.cols):
                x = col * self.frame_width
                y = row * self.frame_height
                frame = self.sprite_sheet.subsurface(pygame.Rect(x, y, self.frame_width, self.frame_height))
                # Scale each frame individually if desired
                if scale_up != 1.0:
                    frame = pygame.transform.smoothscale(
                        frame,
                        (int(self.frame_width * scale_up), int(self.frame_height * scale_up))
                    )
                frames.append(frame)
        return frames

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update_time >= self.frame_duration:
            self.current_frame = (self.current_frame + 1) % self.total_frames
            self.image = self.frames[self.current_frame]
            self.last_update_time = now

    def draw(self, surface, pos):
        self.rect.topleft = pos
        surface.blit(self.image, self.rect)
