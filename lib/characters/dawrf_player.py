import pygame
from lib.assets import *
from lib.collectables.book import *
from lib.util.popup.question_popup import *

class DwarfPlayer(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = dwarf_animations["idle_front"]
        self.rect = self.image.get_rect(center=(x, y))

        self.direction = "down"
        self.last_dir = "down"
        self.anim_index = 0
        self.anim_timer = 0
        self.anim_speed = 120

        self.speed = 4.0
        self.acceleration = 0.2
        self.friction = 0.1
        self.velocity = pygame.Vector2(0, 0)

        self.moving = False
        self.hidden = False

        self.flip = False
        self.flip_data = False

        self.collected_books = 0
        self.text_color = (20, 15, 10)

        self.score = 0
        self.correct_streak = 0
        self.wrong_streak = 0


    def update(self, dt, keys, pos):
        self.last_pos = self.rect.topleft

        move = pygame.Vector2(0, 0)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move.x = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move.x = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            move.y = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            move.y = 1

        if not self.moving and move.length_squared() > 0:
            walking_on_grass_sound.play(-1)
        elif self.moving and not move.length_squared() > 0:
            walking_on_grass_sound.fadeout(500)

        self.moving = move.length_squared() > 0

        if self.hidden and self.moving:
            self.hidden = False

        if self.hidden:
            self.animate(dt, pos)
            return

        if self.moving:
            move = move.normalize()
            if abs(move.x) > abs(move.y):
                self.direction = "right" if move.x > 0 else "left"
            else:
                self.direction = "down" if move.y > 0 else "up"

            if self.direction != self.last_dir:
                self.anim_index = 0
                self.anim_timer = 0
                self.velocity = pygame.Vector2(0, 0)

            self.velocity.x += move.x * self.acceleration
            self.velocity.y += move.y * self.acceleration
        else:
            self.velocity *= (1 - self.friction)
            if self.velocity.length() < 0.1:
                self.velocity = pygame.Vector2(0, 0)

        self.last_dir = self.direction

        if self.velocity.length() > self.speed:
            self.velocity = self.velocity.normalize() * self.speed

        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

        self.animate(dt, pos)


    def animate(self, dt, pos):
        if self.rect.collidepoint(pos) and not self.moving and self.velocity.length_squared() < 0.2 and self.direction != "up":
            cursor.set_hover()
        else:
            cursor.set_idle()

        if self.hidden:
            self.image = dwarf_animations["hide"][0]
            return

        if not self.moving and self.velocity.length_squared() < 0.2:
            self.image = dwarf_animations.get(f"idle_{self.direction}", dwarf_animations["idle_front"])
            return

        frames = dwarf_animations.get(self.direction, [])
        if not frames:
            return

        if self.anim_index >= len(frames):
            self.anim_index = 0

        self.anim_timer += dt
        if self.anim_timer >= self.anim_speed:
            self.anim_index = (self.anim_index + 1) % len(frames)
            self.anim_timer = 0

        self.image = frames[self.anim_index]

    def check_click(self, pos, map_width):
        if self.rect.collidepoint(pos):
            if self.is_idle() and self.direction in ("left", "right", "down") and not self.hidden:
                self.hidden = True

    def is_idle(self):
        return self.velocity.length_squared() < 0.1 and not self.moving

    def draw_hitbox(self, camera_x=0, camera_y=0):
        pygame.draw.rect(
            screen,
            (255, 0, 0),
            pygame.Rect(
                self.rect.x - camera_x,
                self.rect.y - camera_y + self.rect.height * 0.73,
                self.rect.width,
                self.rect.height * 0.27
            ),
            width=2
        )

    def undo_last_movement(self):
        speed = self.velocity.length()

        if speed > 300:
            knockback_dir = -self.velocity.normalize()
            knockback_strength = min(speed * 10, 40)
            self.rect.x += int(knockback_dir.x * knockback_strength)
            self.rect.y += int(knockback_dir.y * knockback_strength)
            self.velocity = knockback_dir * 1.5
        else:
            self.rect.topleft = self.last_pos
            self.velocity = pygame.Vector2(0, 0)

    def get_tree_hitbox(self):
        return pygame.Rect(
            self.rect.x,
            self.rect.y + int(self.rect.height * 0.73),
            self.rect.width,
            int(self.rect.height * 0.27)
        )
    
    def check_book_collision(self, books, tree_spawner, map_width, map_height):
        for book in books:
            if self.get_tree_hitbox().colliderect(book.rect.inflate(-90, -90)):
                self.moving = False
                walking_on_grass_sound.fadeout(300)

                books.remove(book)

                was_correct, is_last = QuestionPopup().run()

                if was_correct:
                    self.collected_books += 1

                    self.wrong_streak = 0
                    self.correct_streak += 1

                    base = 100
                    bonus = self.correct_streak * 10
                    self.score += base + bonus
                else:
                    self.correct_streak = 0
                    self.wrong_streak += 1

                    # Optional penalty: subtract score or trigger a negative effect
                    penalty = self.wrong_streak * 5
                    self.score = max(0, self.score - penalty)
                
                    # Attempt to spawn another book somewhere safe
                    trunks = tree_spawner.get_trunk_hitboxes()
                    tree_tops = tree_spawner.get_tree_top_rects()
                    existing_rects = [b.rect for b in books] + trunks + [self.rect]

                    for _ in range(100):  # Try up to 100 valid positions
                        x = random.randint(200, map_width - 200)
                        y = random.randint(200, map_height - 200)
                        new_book = Book(pos=(x, y))
                        new_rect = new_book.rect.inflate(80, 80)

                        too_close_to_existing = any(new_rect.colliderect(r.inflate(80, 80)) for r in existing_rects)
                        under_tree_top = any(new_rect.colliderect(t) for t in tree_tops)

                        if not too_close_to_existing and not under_tree_top:
                            books.add(new_book)
                            break

    
    def has_books(self):
        return self.collected_books > 0
    
    def draw_score_hud(self):
        font = pygame.font.Font(FONT_PATH, 28)

        # Text color used in QuestionPopup
        color = self.text_color  

        lines = [
            f"SCORE: {self.score}",
            f"BOOKS: {self.collected_books}"
        ]

        if self.correct_streak >= 0 and self.wrong_streak == 0:
            lines.append(f"STREAK: {self.correct_streak}")
        elif self.wrong_streak > 0:
            lines.append(f"MISTAKES: {self.wrong_streak}")

        # === Square tray setup ===
        tray_size = 230  # Square width and height
        tray_x = 20
        tray_y = 8  # Slightly higher

        tray_surface = pygame.transform.smoothscale(score_paper, (tray_size, tray_size))
        screen.blit(tray_surface, (tray_x, tray_y))

        # === Draw centered text inside square tray ===
        padding = 16
        spacing = 10
        total_text_height = sum(font.size(line)[1] for line in lines) + spacing * (len(lines) - 1)
        y = tray_y + (tray_size - total_text_height) // 2

        for line in lines:
            surf = font.render(line, True, color)
            x = tray_x + (tray_size - surf.get_width()) // 2
            screen.blit(surf, (x, y))
            y += surf.get_height() + spacing
