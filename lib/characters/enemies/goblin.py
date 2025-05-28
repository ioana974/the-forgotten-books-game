import pygame
import random
import math
from lib.assets import *

class Goblin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = goblin_animations["idle_right"]
        self.rect = self.image.get_rect(center=(x, y))

        self.anim_index = 0
        self.anim_timer = 0
        self.anim_speed = 400

        self.speed = random.uniform(3.0, 3.3)
        self.direction = pygame.Vector2(0, 0)
        self.velocity = pygame.Vector2(0, 0)
        self.last_pos = self.rect.topleft

        self.state = "idle"
        self.chase_range = 350
        self.reach_radius = 70
        self.aggroed = False
        self.facing_left = False

        self.player_hitbox = None
        self.debug_player_pos = None
        self.debug_los_point = None

        self.grab_release_timer = 0  # milliseconds
        self.grab_hold_time = 500

        self.fleeing = False
        self.flee_time = 3000  # milliseconds to flee
        self.flee_timer = 0

        self.flee_target = None
        self.has_stolen_book = False



    def update(self, dt, player_hitbox, tree_hitboxes, player_has_books):
        self.last_pos = self.rect.topleft
        goblin_center = pygame.Vector2(self.get_hitbox().center)
        player_center = pygame.Vector2(player_hitbox.center)
        distance = player_center.distance_to(goblin_center)

        self.debug_player_pos = player_center
        self.debug_los_point = None

        self.player_hitbox = player_hitbox
        self.tree_hitboxes = tree_hitboxes

        if not self.fleeing:
            self.update_aggro(distance, player_has_books)
            self.update_state_and_movement(distance, player_hitbox)

        self.update_facing()
        self.animate(dt)

    def update_aggro(self, distance, player_has_books):
        if not self.aggroed and distance < self.chase_range and self.has_any_los() and player_has_books:
            if not self.aggroed:
                self.play_random_snippet()
            self.aggroed = True
        elif self.aggroed and distance > self.chase_range * 1.5:
            self.aggroed = False

    def update_state_and_movement(self, distance, player_hitbox):
        goblin_center = pygame.Vector2(self.get_hitbox().center)

        if self.fleeing:
            self.state = "walking"
            return
        
        if self.aggroed:
            # Still in grab range
            if self.state == "grab":

                if self.circle_intersects_rect(self.get_hitbox().center, self.reach_radius, self.player_hitbox):
                    self.grab_release_timer = self.grab_hold_time 
                    self.velocity = pygame.Vector2(0, 0)
                    self.fleeing = True
                    return
                else:
                    self.grab_release_timer -= 16  # Approx ~60fps frame time
                    if self.grab_release_timer > 0:
                        self.velocity = pygame.Vector2(0, 0)
                        return
                    else:
                        self.state = "walking"  # Timer expired, switch to walking

            # Enter grab if close
            if self.circle_intersects_rect(self.get_hitbox().center, self.reach_radius, self.player_hitbox):
                self.state = "grab"
                self.grab_release_timer = self.grab_hold_time
                self.velocity = pygame.Vector2(0, 0)
                return

            # Movement logic
            target = None
            if self.has_any_los():
                target = pygame.Vector2(player_hitbox.center)
            else:
                target = self.find_closest_visible_point(player_hitbox.center, self.tree_hitboxes)
                self.debug_los_point = target

            if target:
                to_target = pygame.Vector2(target) - goblin_center
                pursuit = to_target.normalize()
                circular = self.get_tree_circular_avoidance(goblin_center, to_target, self.tree_hitboxes)

                combined = (pursuit + circular * 3).normalize()

                self.direction = combined
                self.velocity = combined * self.speed
                self.rect.x += int(self.velocity.x)
                self.rect.y += int(self.velocity.y)
                self.state = "walking" if self.velocity.length_squared() > 0.5 else "idle"
            else:
                self.state = "idle"
                self.velocity = pygame.Vector2(0, 0)

        else:
            self.state = "idle"
            self.velocity = pygame.Vector2(0, 0)


    def update_facing(self):
        if self.direction.x < 0:
            self.facing_left = True
        elif self.direction.x > 0:
            self.facing_left = False

    def animate(self, dt):
        if self.state == "idle":
            self.image = goblin_animations["idle_left" if self.facing_left else "idle_right"]
            return

        if self.state == "walking":
            frames = goblin_animations["move_left"] if self.facing_left else goblin_animations["move_right"]
        elif self.state == "grab":
            frames = goblin_animations["grab"]
        else:
            return

        if not frames:
            return

        if self.anim_index >= len(frames):
            self.anim_index = 0

        self.anim_timer += dt
        if self.anim_timer >= self.anim_speed:
            self.anim_index = (self.anim_index + 1) % len(frames)
            self.anim_timer = 0

        frame = frames[self.anim_index]
        if self.state == "grab" and self.facing_left:
            frame = pygame.transform.flip(frame, True, False)

        self.image = frame

    def undo_last_movement(self):
        self.rect.topleft = self.last_pos
        self.velocity = pygame.Vector2(0, 0)

    def get_hitbox(self):
        return pygame.Rect(
            self.rect.x,
            self.rect.y + int(self.rect.height * 0.6),
            self.rect.width,
            int(self.rect.height * 0.4)
        )

    def get_tree_hitbox(self):
        return self.get_hitbox()

    def draw_hitbox(self, camera_x=0, camera_y=0, show_aggro=True):
        hitbox = self.get_hitbox()
        center = hitbox.center

        pygame.draw.rect(screen, (0, 255, 0), hitbox.move(-camera_x, -camera_y), width=2)

        if show_aggro:
            pygame.draw.circle(screen, (0, 100, 255),
                               (int(center[0] - camera_x), int(center[1] - camera_y)),
                               self.chase_range, width=1)
            pygame.draw.circle(screen, (255, 0, 0),
                               (center[0] - camera_x, center[1] - camera_y),
                               self.reach_radius, width=1)

        if self.debug_player_pos:
            if self.player_hitbox:
                goblin_center = self.get_hitbox().center
                for corner in [
                    self.player_hitbox.topleft,
                    self.player_hitbox.topright,
                    self.player_hitbox.bottomleft,
                    self.player_hitbox.bottomright
                ]:
                    pygame.draw.line(
                        screen, (255, 255, 0),  # yellow
                        (goblin_center[0] - camera_x, goblin_center[1] - camera_y),
                        (corner[0] - camera_x, corner[1] - camera_y),
                        width=1
                    )

        if self.debug_los_point:
            pygame.draw.circle(screen, (0, 255, 255),
                               (self.debug_los_point[0] - camera_x, self.debug_los_point[1] - camera_y),
                               5, width=1)

    @staticmethod
    def circle_intersects_rect(circle_center, radius, rect):
        closest_x = max(rect.left, min(circle_center[0], rect.right))
        closest_y = max(rect.top, min(circle_center[1], rect.bottom))
        dx = circle_center[0] - closest_x
        dy = circle_center[1] - closest_y
        return dx * dx + dy * dy <= radius * radius

    def has_any_los(self):
        corners = [
            self.player_hitbox.topleft,
            self.player_hitbox.topright,
            self.player_hitbox.bottomleft,
            self.player_hitbox.bottomright
        ]
        for corner in corners:
            if self.has_line_of_sight(corner, self.tree_hitboxes):
                return True
        return False

    def has_line_of_sight(self, target_pos, obstacles):
        for obs in obstacles:
            if obs.clipline(self.get_hitbox().center, target_pos):
                return False
        return True

    def find_closest_visible_point(self, player_pos, obstacles, radius=100, resolution=24):
        closest_point = None
        min_distance = float('inf')
        goblin_center = pygame.Vector2(self.get_hitbox().center)

        for i in range(resolution):
            angle = (2 * math.pi / resolution) * i
            px = int(player_pos[0] + math.cos(angle) * radius)
            py = int(player_pos[1] + math.sin(angle) * radius)
            point = (px, py)

            if self.has_line_of_sight(point, obstacles):
                dist = goblin_center.distance_to(point)
                if dist < min_distance:
                    closest_point = point
                    min_distance = dist

        return closest_point

    def get_tree_circular_avoidance(self, center, velocity, trees, avoid_radius=150, strength=2.5):
        adjustment = pygame.Vector2(0, 0)

        for tree in trees:
            tree_center = pygame.Vector2(tree.center)
            to_tree = center - tree_center
            distance = to_tree.length()

            if 0 < distance < avoid_radius:
                # Radial repulsion away from the tree
                repulse = to_tree.normalize()

                # Tangent force for circling around
                tangent = pygame.Vector2(-to_tree.y, to_tree.x).normalize()

                # Weigh both forces
                weight = (avoid_radius - distance) / avoid_radius

                adjustment += (repulse + tangent * 0.8) * weight * strength

        return adjustment
    
    def play_random_snippet(self):
        random.choice(goblin_sounds).play()



