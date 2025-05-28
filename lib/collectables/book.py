import pygame

from lib.assets import *

class Book(pygame.sprite.Sprite):
    def __init__(self, frame_duration=200, pos=(0, 0)):
        super().__init__()
        self.frames = self.load_frames((book_collectable_image.get_width(), book_collectable_image.get_height()))
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_duration = frame_duration  # milliseconds per frame
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=pos)

    def load_frames(self, frame_size):
        w, h = frame_size
        sheet_w, sheet_h = book_collectable_image.get_size()

        cols, rows = 2, 2
        frame_w = sheet_w // cols
        frame_h = sheet_h // rows

        frames = []

        for j in range(rows):
            for i in range(cols):
                x, y = i * frame_w, j * frame_h
                frame = book_collectable_image.subsurface(pygame.Rect(x, y, frame_w, frame_h)).copy()
                frames.append(frame)

        return frames[1:]  # Skip top-left


    def update(self, dt):
        self.frame_timer += dt
        if self.frame_timer >= self.frame_duration:
            self.frame_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
