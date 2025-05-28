import pygame
import random

from lib.assets import *

class AnimatedPaper(pygame.sprite.Sprite):
    def __init__(self, frame_duration=100, scale=1.0, length=0):
        super().__init__()

        # Load scroll animation frames
        self.frames = [
            pygame.transform.rotozoom(pygame.image.load(path).convert_alpha(), 0, scale)
            for path in paper_frames_path
        ]

        self.sound = None

        # Load matching base paper frames
        self.base_frames = [
            pygame.transform.rotozoom(pygame.image.load(path).convert_alpha(), 0, scale)
            for path in base_paper_path
        ]

        self.offsets = paper_offsets or [0] * len(self.frames)

        self.length = length
        self.frame_duration = frame_duration
        self.scroll_speed = 14 / length 

        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.base_image = self.base_frames[self.current_frame]
        self.last_update = pygame.time.get_ticks()

        self.state = "idle"  # 'idle', 'extending', 'rolling', 'retracting', 'unrolling'
        self.scroll_progress = 0.0

    def update(self):
        now = pygame.time.get_ticks()

        if self.state == "extending":
            self.scroll_progress += self.scroll_speed
            if self.scroll_progress >= 1.0:
                self.scroll_progress = 1.0
                self.state = "rolling"
                self.last_update = now

        elif self.state == "retracting":
            self.scroll_progress -= self.scroll_speed
            if self.scroll_progress <= 0.0:
                self.scroll_progress = 0.0
                self.state = "unrolling"
                self.last_update = now

        elif self.state in ["rolling", "unrolling"]:
            if now - self.last_update >= self.frame_duration:
                self.last_update = now

                direction = 1 if self.state == "rolling" else -1
                self.current_frame += direction
                self.current_frame = max(0, min(self.current_frame, len(self.frames) - 1))

                self.image = self.frames[self.current_frame]
                self.base_image = self.base_frames[self.current_frame]

                if (self.state == "rolling" and self.current_frame == len(self.frames) - 1) or \
                   (self.state == "unrolling" and self.current_frame == 0):
                    self.state = "idle"
        
        elif self.state == "idle" and self.sound:
            self.sound.stop()
            self.sound = None

    def start_roll(self):
        if (self.sound == None):
            self.sound = random.choice(paper_crumble_sounds)
            self.sound.play()

        if self.scroll_progress < 1.0:
            self.state = "extending"
                
        elif self.current_frame < len(self.frames) - 1:
            self.state = "rolling"

    def reverse_roll(self):

        if self.current_frame > 0:
            self.state = "unrolling"

        elif self.scroll_progress > 0.0:
            self.state = "retracting"

            if (self.sound == None):
                self.sound = random.choice(paper_crumble_sounds)
                self.sound.play()

    def draw(self, surface, base_x, base_y):
        overlap = 40
        vertical_shift = 0
        offset_y = self.get_current_offset()

        scroll_width = int(self.scroll_progress * self.length)
        scroll_x = base_x + scroll_width
        scroll_y = base_y + offset_y

        # --- Draw scroll segment FIRST (bottom layer) ---
        surface.blit(self.image, (scroll_x, scroll_y))

        # --- Draw base tiles from LAST to FIRST (top layer last) ---
        if self.base_image:
            base_w = self.base_image.get_width()
            base_h = self.base_image.get_height()
            visible_w = scroll_width + overlap

            tiles_needed = (visible_w // (base_w - overlap)) + 2

            for i in reversed(range(tiles_needed)):
                tile_x = base_x + i * (base_w - overlap)
                tile_y = base_y + offset_y + i * vertical_shift

                # Compute how much of the tile is within visible area
                max_visible = scroll_width + overlap - (tile_x - base_x)
                if max_visible <= 0:
                    continue  # this tile is out of view

                clip_width = min(base_w, max_visible)

                # Create clipped surface
                clipped = pygame.Surface((clip_width, base_h), pygame.SRCALPHA)
                clipped.blit(self.base_image, (0, 0), area=pygame.Rect(0, 0, clip_width, base_h))

                surface.blit(clipped, (tile_x, tile_y))

    def set_length(self, length):
        self.length = length
        self.scroll_speed = 14 / length 

    def get_current_offset(self):
        return self.offsets[self.current_frame]
