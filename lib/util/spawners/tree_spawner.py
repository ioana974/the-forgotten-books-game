import pygame
import random
import math

class TreeSpawner:
    # Manually defined hitboxes for each tree variant (x, y, width, height)
    TREE_HITBOXES = [
        (229, 423, 85, 41),
        (185, 426, 104, 38),
        (205, 415, 88, 44),
        (181, 419, 96, 40),
    ]

    TREE_TOP_RECTS = [
        (71, 45, 384, 357),
        (48, 18, 395, 373),
        (62, 34, 395, 344),
        (30, 46, 412, 324),
    ]

    def __init__(self, tree_sheet_path, tile_size, area_width, area_height, num_trees=40, scale=1.0, min_distance=150):
        self.tree_sheet = pygame.image.load(tree_sheet_path).convert_alpha()
        self.tile_size = tile_size
        self.scale = scale
        self.num_trees = num_trees
        self.min_distance = min_distance

        self.area_width = area_width
        self.area_height = area_height

        self.trees = self._split_sheet()
        self.spawned = []  # List of (image, position, trunk_rect)

        self._generate_tree_positions()

    def _split_sheet(self):
        sheet_width, sheet_height = self.tree_sheet.get_size()
        tree_w = sheet_width // 2
        tree_h = sheet_height // 2

        trees = []
        for y in range(2):
            for x in range(2):
                rect = pygame.Rect(x * tree_w, y * tree_h, tree_w, tree_h)
                tree = self.tree_sheet.subsurface(rect)
                if self.scale != 1.0:
                    tree = pygame.transform.smoothscale(
                        tree,
                        (int(tree_w * self.scale), int(tree_h * self.scale))
                    )
                trees.append(tree)
        return trees

    def _generate_tree_positions(self):
        attempts = 0
        max_attempts = self.num_trees * 20

        while len(self.spawned) < self.num_trees and attempts < max_attempts:
            tree_img = random.choice(self.trees)
            tree_index = self.trees.index(tree_img)
            w, h = tree_img.get_size()

            # Favor areas away from center to simulate forest edges
            x = random.randint(100, self.area_width - w - 100)
            y = random.randint(100, self.area_height - h - 100)

            # Check spacing from existing trees
            too_close = False
            for _, (tx, ty), _, _ in self.spawned:
                if math.hypot(tx - x, ty - y) < self.min_distance:
                    too_close = True
                    break
            if too_close:
                attempts += 1
                continue

            # Use pre-defined hitbox relative to the image
            rel_x, rel_y, rel_w, rel_h = self.TREE_HITBOXES[tree_index]

            # Apply scaling
            rel_x = int(rel_x * self.scale)
            rel_y = int(rel_y * self.scale)
            rel_w = int(rel_w * self.scale)
            rel_h = int(rel_h * self.scale)

            # World-space hitbox
            trunk_rect = pygame.Rect(
                x + rel_x,
                y + rel_y,
                rel_w,
                rel_h
            )


            top_rel_x, top_rel_y, top_w, top_h = self.TREE_TOP_RECTS[tree_index]
            top_rel_x = int(top_rel_x * self.scale)
            top_rel_y = int(top_rel_y * self.scale)
            top_w = int(top_w * self.scale)
            top_h = int(top_h * self.scale)

            top_rect = pygame.Rect(x + top_rel_x, y + top_rel_y, top_w, top_h)


            self.spawned.append((tree_img, (x, y), trunk_rect, top_rect))
            attempts += 1

    def draw_hitboxes(self, surface, camera_x=0, camera_y=0):
        for _, _, trunk_rect, _ in self.spawned:
            debug_rect = trunk_rect.move(-camera_x, -camera_y)
            pygame.draw.rect(surface, (255, 0, 0), debug_rect, 2)

    def get_trunk_hitboxes(self):
        return [rect for _, _, rect, _ in self.spawned]
    
    def get_tree_top_rects(self):
        return [top_rect for _, _, _, top_rect in self.spawned]
