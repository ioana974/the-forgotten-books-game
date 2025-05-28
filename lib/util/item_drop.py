import pygame
import random
import math

from lib.assets import *

class ItemDrop:
    def __init__(self, image, x, start_y, target_y, duration_frames,
                 initial_scale=2.0, final_scale=1.0,
                 start_angle=0, end_angle=0, bounce_height=15, bounce_duration=12):
        self.original_image = image.convert_alpha()
        self.x = x
        self.start_y = start_y
        self.target_y = target_y
        self.duration = duration_frames
        self.frame = 0

        self.initial_scale = initial_scale
        self.final_scale = final_scale
        self.current_scale = initial_scale

        self.start_angle = start_angle
        self.end_angle = end_angle
        self.current_angle = start_angle

        self.bounce_height = bounce_height
        self.bounce_duration = bounce_duration
        self.bounce_frame = 0
        self.bouncing = False

        self.y = start_y
        self.done = False
        self.landed = False

        # Exit params
        self.exiting = False
        self.exit_frame = 0
        self.exit_duration = 40
        self.exit_start = None
        self.exit_target = None

        self.particles = []
        self.spawned_particles = False

        self.sliding_channel = None



    def update(self):
        if self.done and not self.exiting and not self.particles:
            return

        if not self.landed:
            # Natural falling - ease-in
            self.frame += 1
            t = min(self.frame / self.duration, 1.0)
            ease_t = t ** 2.8
            self.y = self.start_y + (self.target_y - self.start_y) * ease_t
            self.current_scale = self.initial_scale + (self.final_scale - self.initial_scale) * ease_t
            self.current_angle = self.start_angle + (self.end_angle - self.start_angle) * ease_t

            if self.frame >= self.duration:
                self.landed = True
                self.bouncing = True
                self.bounce_frame = 0

                if not self.spawned_particles:
                    self.spawn_particles()
                    self.spawned_particles = True
                    random.choice(impact_sounds).play()


        elif self.bouncing:
            # Bounce animation
            self.bounce_frame += 1
            t = self.bounce_frame / self.bounce_duration
            if t >= 1.0:
                self.y = self.target_y
                self.current_angle = self.end_angle
                self.bouncing = False
                self.done = True
            else:
                bounce_offset = math.sin(t * math.pi) * self.bounce_height * (1 - t)
                self.y = self.target_y - bounce_offset

        elif self.exiting:
            self.exit_frame += 1
            t = min(self.exit_frame / self.exit_duration, 1.0)
            eased = t ** 2  # ease-in
            pos = self.exit_start.lerp(self.exit_target, eased)
            self.x, self.y = pos
            if t >= 1.0:
                if self.sliding_channel:
                    self.sliding_channel.stop()
                    self.sliding_channel = None

                self.exiting = False
                

        # Update particles
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.3  # gravity
            p["life"] -= 1
        self.particles = [p for p in self.particles if p["life"] > 0]

    def spawn_particles(self):
        w, h = self.original_image.get_size()
        center_x = self.x
        center_y = self.y + (h * self.current_scale) // 2

        for _ in range(24):  # clean radial burst from center
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(6.0, 12.0)

            life = random.randint(20, 35)
            self.particles.append({
                "x": center_x,
                "y": center_y,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed - 1.5,
                "life": life,
                "max_life": life,
                "color": (255, 240, 180)
            })

    def draw(self, surface):
        # Draw particles
        for p in self.particles:
            fade_ratio = p["life"] / p.get("max_life", 25)
            alpha = max(0, min(255, int(255 * fade_ratio)))

            r, g, b = p["color"]
            particle_surf = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, (r, g, b, alpha), (2, 2), 2)
            surface.blit(particle_surf, (p["x"], p["y"]))

        # Draw item
        w, h = self.original_image.get_size()
        scaled_w = int(w * self.current_scale)
        scaled_h = int(h * self.current_scale)
        scaled = pygame.transform.smoothscale(self.original_image, (scaled_w, scaled_h))
        rotated = pygame.transform.rotate(scaled, self.current_angle)
        rotated_rect = rotated.get_rect(center=(self.x, self.y + scaled_h // 2))
        surface.blit(rotated, rotated_rect.topleft)

    



    def start_exit(self, target_pos, duration=40):
        self.exiting = True

        channel = pygame.mixer.find_channel()
        if channel:
            sound = pygame.mixer.Sound("assets/audio/effects/sliding_on_table.mp3")
            sound.set_volume(random.choice([0.3, 0.7]))
            channel.play(sound)
            self.sliding_channel = channel

        self.exit_frame = 0
        self.exit_duration = duration
        self.exit_start = pygame.Vector2(self.x, self.y)
        self.exit_target = pygame.Vector2(target_pos)
