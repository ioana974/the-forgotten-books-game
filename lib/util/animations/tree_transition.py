import pygame
from lib.config import *
from lib.assets import *


class TreeTransition:
    def __init__(self, image_path, scales=[2.5, 3], stop_offsets=[1000, 1000]):
        self.image_path = image_path
        self.base_image = pygame.image.load(image_path).convert_alpha()

        self.layers = []
        self.directions = ['left', 'right', 'top', 'bottom']
        self.center_x = SCREEN_WIDTH // 2
        self.center_y = SCREEN_HEIGHT // 2

        for scale, offset in zip(scales, stop_offsets):
            img = pygame.transform.rotozoom(self.base_image, 0, scale)
            self.layers.append({
                'image': img,
                'w': img.get_width(),
                'h': img.get_height(),
                'stop_offset': offset
            })

    def _get_position(self, direction, offset, eased_progress):
        move = offset * eased_progress
        x, y = self.center_x, self.center_y

        if direction == 'left':
            x -= move
        elif direction == 'right':
            x += move
        elif direction == 'top':
            y -= move
        elif direction == 'bottom':
            y += move

        return x, y

    def draw_images(self, progress, direction='in'):
        eased = (1 - progress) ** 2 if direction == 'out' else progress ** 2

        for layer in self.layers:
            for dir in self.directions:
                cx, cy = self._get_position(dir, layer['stop_offset'], eased)
                rect = layer['image'].get_rect(center=(cx, cy))
                screen.blit(layer['image'], rect.topleft)

    def enter(self, background, duration=2.0, level_completed = False, score = 0):
        music_manager.pause()
        
        cursor.hide()
        leaf_sound.play()
        self._animate(background, 'in', duration, level_completed, score)

    def exit(self, background, duration=1.2):
        leaf_sound.play()
        self._animate(background, 'out', duration)
        cursor.show()

    def _animate(self, background, direction, duration, level_completed = False, score = 0):
        clock = pygame.time.Clock()
        total_frames = int(duration * 60) if direction == 'in' else int(duration * 60 * 0.7)


        for frame in range(total_frames):
            updateExitLoop()
            progress = min(1.0  if direction == 'in' else 0.7, frame / (total_frames - 1) + 0.3 if direction == 'in' else frame / (total_frames - 1))

            if isinstance(background, pygame.Surface):
                screen.blit(background, (0, 0))
            else:
                screen.fill(background)

            self.draw_images(progress, direction)
            pygame.display.update()
            clock.tick(60)


        # Final state
        if isinstance(background, pygame.Surface):
            screen.blit(background, (0, 0))
        else:
            screen.fill(background)
        self.draw_images(1.0, direction)
        pygame.display.update()

        leaf_sound.fadeout(500)

        if direction == "in" and not game_data["lvl1_card_shown"]:
            # === SLIDE CARD IN FROM BOTTOM ===
            card_y_start = SCREEN_HEIGHT + 100
            card_y_end = SCREEN_HEIGHT // 2 - cover_lvl1.get_height() // 2
            card_x = SCREEN_WIDTH // 2 - cover_lvl1.get_width() // 2

            for frame in range(30):
                updateExitLoop()

                t = frame / 30
                eased = 1 - (1 - t) ** 3
                current_y = card_y_start + (card_y_end - card_y_start) * eased

                if isinstance(background, pygame.Surface):
                    screen.blit(background, (0, 0))
                else:
                    screen.fill(background)
                self.draw_images(1.0, direction)

                border_rect = pygame.Rect(card_x - 30, current_y - 30, cover_lvl1.get_width() + 60, cover_lvl1.get_height() + 60)
                pygame.draw.rect(screen, (60, 40, 20), border_rect, width=40)
                screen.blit(cover_lvl1, (card_x, current_y))

                pygame.display.update()
                clock.tick(60)

            # === PAUSE 5 SECONDS ===
            narrator_lvl1_into_sound.play()
            pause_time = pygame.time.get_ticks()
            while pygame.time.get_ticks() - pause_time < 9000:
                updateExitLoop()

                if isinstance(background, pygame.Surface):
                    screen.blit(background, (0, 0))
                else:
                    screen.fill(background)

                self.draw_images(1.0, direction)

                border_rect = pygame.Rect(card_x - 30, current_y - 30, cover_lvl1.get_width() + 60, cover_lvl1.get_height() + 60)
                pygame.draw.rect(screen, (60, 40, 20), border_rect, width=40)
                screen.blit(cover_lvl1, (card_x, card_y_end))

                pygame.display.update()
                clock.tick(60)

            # === SLIDE CARD OUT TO TOP ===
            for frame in range(30):
                updateExitLoop()

                t = frame / 30
                eased = 1 - (1 - t) ** 3
                current_y = card_y_end - (card_y_end + 1000) * eased  # move above screen

                if isinstance(background, pygame.Surface):
                    screen.blit(background, (0, 0))
                else:
                    screen.fill(background)
                self.draw_images(1.0, direction)

                border_rect = pygame.Rect(card_x - 30, current_y - 30, cover_lvl1.get_width() + 60, cover_lvl1.get_height() + 60)
                pygame.draw.rect(screen, (60, 40, 20), border_rect, width=40)
                screen.blit(cover_lvl1, (card_x, current_y))

                pygame.display.update()
                clock.tick(60)
            
            game_data["lvl1_card_shown"] = True



        elif direction == "in" and level_completed:
            # === SET UP SCORE POSITION ===
            card_y_end = 200  # Vertical anchor for score
            font = pygame.font.Font(FONT_PATH, 200)
            text_color = (255, 255, 255)
            best = max(score, game_data.get("lvl1_best_score", 0))

            # Render text to surfaces
            current_text_surface = font.render(f"SCORE: {score}", True, text_color).convert_alpha()
            best_text_surface = font.render(f"BEST: {best}", True, text_color).convert_alpha()

            # Constants
            display_duration = 3000  # Total ms
            fade_duration = 1000     # Fade in/out duration in ms
            start_time = pygame.time.get_ticks()

            while True:
                now = pygame.time.get_ticks()
                elapsed = now - start_time

                if elapsed >= display_duration:
                    break

                updateExitLoop()

                # Compute alpha
                if elapsed < fade_duration:
                    alpha = int((elapsed / fade_duration) * 255)  # Fade in
                elif elapsed > display_duration - fade_duration:
                    alpha = int(((display_duration - elapsed) / fade_duration) * 255)  # Fade out
                else:
                    alpha = 255

                # Clamp alpha
                alpha = max(0, min(255, alpha))

                # Apply alpha
                current_text = current_text_surface.copy()
                best_text = best_text_surface.copy()
                current_text.set_alpha(alpha)
                best_text.set_alpha(alpha)

                # Draw background and layers
                if isinstance(background, pygame.Surface):
                    screen.blit(background, (0, 0))
                else:
                    screen.fill(background)

                self.draw_images(1.0, direction)

                # Draw score text with alpha
                center_x = SCREEN_WIDTH // 2
                screen.blit(current_text, (center_x - current_text.get_width() // 2, card_y_end))
                screen.blit(best_text, (center_x - best_text.get_width() // 2, card_y_end + 220))

                pygame.display.update()
                clock.tick(60)

            # Save best score
            game_data["lvl1_best_score"] = best










            # === SLIDE CARD IN FROM BOTTOM ===
            card_y_start = SCREEN_HEIGHT + 100
            card_y_end = SCREEN_HEIGHT // 2 - cover_lvl1_end.get_height() // 2
            card_x = SCREEN_WIDTH // 2 - cover_lvl1_end.get_width() // 2

            for frame in range(30):
                updateExitLoop()

                t = frame / 30
                eased = 1 - (1 - t) ** 3
                current_y = card_y_start + (card_y_end - card_y_start) * eased

                if isinstance(background, pygame.Surface):
                    screen.blit(background, (0, 0))
                else:
                    screen.fill(background)
                self.draw_images(1.0, direction)

                border_rect = pygame.Rect(card_x - 30, current_y - 30, cover_lvl1_end.get_width() + 60, cover_lvl1_end.get_height() + 60)
                pygame.draw.rect(screen, (60, 40, 20), border_rect, width=40)
                screen.blit(cover_lvl1_end, (card_x, current_y))

                pygame.display.update()
                clock.tick(60)





            # === PAUSE 5 SECONDS ===
            narrator_lvl1_outro_sound.play()
            pause_time = pygame.time.get_ticks()
            while pygame.time.get_ticks() - pause_time < 5000:
                updateExitLoop()

                if isinstance(background, pygame.Surface):
                    screen.blit(background, (0, 0))
                else:
                    screen.fill(background)

                self.draw_images(1.0, direction)

                border_rect = pygame.Rect(card_x - 30, current_y - 30, cover_lvl1_end.get_width() + 60, cover_lvl1_end.get_height() + 60)
                pygame.draw.rect(screen, (60, 40, 20), border_rect, width=40)
                screen.blit(cover_lvl1_end, (card_x, card_y_end))

                pygame.display.update()
                clock.tick(60)

            # === SLIDE CARD OUT TO TOP ===
            for frame in range(30):
                updateExitLoop()

                t = frame / 30
                eased = 1 - (1 - t) ** 3
                current_y = card_y_end - (card_y_end + 1000) * eased  # move above screen

                if isinstance(background, pygame.Surface):
                    screen.blit(background, (0, 0))
                else:
                    screen.fill(background)
                self.draw_images(1.0, direction)

                border_rect = pygame.Rect(card_x - 30, current_y - 30, cover_lvl1_end.get_width() + 60, cover_lvl1_end.get_height() + 60)
                pygame.draw.rect(screen, (60, 40, 20), border_rect, width=40)
                screen.blit(cover_lvl1_end, (card_x, current_y))

                pygame.display.update()
                clock.tick(60)
            
            game_data["lvl1_card_shown"] = True



        pygame.time.wait(100)
