import pygame

from lib.config import *
from lib.assets import *

class GoblinPopup:
    def __init__(self):
        self.image = pygame.transform.smoothscale_by(load_image("characters\\enemies\\goblin\\goblin_grab_background.png"), 1)
        self.visible = False
        self.display_duration = 1500  # Show for 2 seconds

    def show(self):
        self.visible = True
        self.timer = pygame.time.get_ticks()
        book_catch_sound.set_volume(0.5)
        book_catch_sound.play()

    def update(self):
         if self.visible:
            now = pygame.time.get_ticks()
            if now - self.timer > self.display_duration:
                self.visible = False

    def draw(self, surface):
        if self.visible:
            surface.blit(self.image, (0, -50))
