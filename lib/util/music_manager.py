import pygame

class MusicManager:
    def __init__(self, volume=0.5):
        self.volume = volume
        self.is_playing = False

        self.load(0)

    def toggle(self):
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
        else:
            pygame.mixer.music.unpause()
            self.is_playing = True
    
    def play(self):
        pygame.mixer.music.play(-1)
        self.playing = True

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False

    def pause(self):
        pygame.mixer.music.pause()
        self.is_playing = False

    def resume(self):
        pygame.mixer.music.unpause()
        self.is_playing = True

    def set_volume(self, volume):
        self.volume = volume
        pygame.mixer.music.set_volume(volume)

    def load(self, index):
        if index == 0:
            pygame.mixer.music.load("assets/audio/background/background_music.mp3")
            pygame.mixer.music.set_volume(0.35)
            self.is_playing = False
        elif index == 1:
            pygame.mixer.music.load("assets/audio/background/colorful_flowers.mp3")
            pygame.mixer.music.set_volume(0.06)
            self.is_playing = False


