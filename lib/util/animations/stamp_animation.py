import pygame
import math
import random

from lib.config import *
from lib.assets import *

class StampAnimation:
    def __init__(self, center_pos, final_angle=0, final_scale=1.0):
        self.center_x, self.center_y = center_pos

        self.final_angle = final_angle
        self.final_scale = final_scale

        # Start with exaggerated offset
        self.start_angle = random.choice([-30, 30])
        self.start_scale = 2.5
        self.duration_frames = 10
        self.impact_frame = 20

        self.frame = 0
        self.sound_played = False
        self.done = False

    def update_position(self, new_center):
        self.center_x, self.center_y = new_center

    def update(self):
        if self.frame >= self.duration_frames:
            self.done = True

        if self.done:
            img = pygame.transform.rotozoom(dwarf_stamp, self.final_angle, self.final_scale)
            rect = img.get_rect(center=(self.center_x, self.center_y))
            screen.blit(img, rect.topleft)
            return

        # Ease out animation
        t = self.frame / self.duration_frames
        eased = 1 - (1 - t) ** 3

        if eased > 0.96 and not self.sound_played:
            stamp_sound.play()
            self.sound_played = True

        angle = self.start_angle + (self.final_angle - self.start_angle) * eased
        scale = self.start_scale + (self.final_scale - self.start_scale) * eased

        # Transform image
        img = pygame.transform.rotozoom(dwarf_stamp, angle, scale)
        rect = img.get_rect(center=(self.center_x, self.center_y))
        screen.blit(img, rect.topleft)

        self.frame += 1
