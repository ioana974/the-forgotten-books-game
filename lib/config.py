import os
import pygame
import sys

from lib.util.save_data import *
from lib.util.edge_detector import *
from lib.util.music_manager import *



def updateExitLoop():
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                save_progress()
                pygame.quit()
                sys.exit()


pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)
pygame.display.set_caption("The Forgotten Books")

info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h

clock = pygame.time.Clock()

BUTTON_COLOR = (60, 40, 20)
BUTTON_HOVER_COLOR = (90, 60, 30)
BUTTON_TEXT_COLOR = (255, 220, 160)
BUTTON_BORDER_COLOR = (255, 228, 181)


FONT_PATH = os.path.join("assets", "font", "MedievalSharp-Book.ttf")
FONT = pygame.font.Font(FONT_PATH, 30)


mouse_click_edge = EdgeDetector()
paper_offsets = [0, -5, 0, 20]

saved_clouds = []
saved_parallax_layers = []


current_screen = 'start'
last_screen = 'start'


music_manager = MusicManager()