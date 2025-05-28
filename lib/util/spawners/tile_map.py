import pygame
import random

class TileMap:
    def __init__(self, tile_sheet_path, tile_size, area_width, area_height, scale=1.0, crop=0):
        self.tile_sheet = pygame.transform.smoothscale(
            pygame.image.load(tile_sheet_path).convert_alpha(),
            (4 * tile_size, 4 * tile_size)
            )

        self.original_tile_size = tile_size
        self.crop = crop
        self.scale = scale

        # Final display size of a tile after cropping and scaling
        self.tile_size = int((tile_size - 2 * crop) * scale)

        # Area coverage
        self.columns = (area_width // self.tile_size) + 1
        self.rows = (area_height // self.tile_size) + 1

        self.tiles = self._load_tiles(rows=2, cols=2)  # 2x2 sprite sheet
        self.map_data = self._generate_map_data()

    def _generate_map_data(self):
        return [[random.randint(0, len(self.tiles) - 1) for _ in range(self.columns)] for _ in range(self.rows)]

    def _load_tiles(self, rows, cols):
        tiles = []
        for row in range(rows):
            for col in range(cols):
                x = col * self.original_tile_size + self.crop
                y = row * self.original_tile_size + self.crop
                size = self.original_tile_size - 2 * self.crop
                tile = self.tile_sheet.subsurface(pygame.Rect(x, y, size, size))
                if self.scale != 1:
                    tile = pygame.transform.smoothscale(tile, (self.tile_size, self.tile_size))
                tiles.append(tile)
        return tiles

    def draw(self, surface, camera_x=0, camera_y=0):
        # Calculate visible tile range
        start_col = max(0, camera_x // self.tile_size)
        end_col = min(self.columns, (camera_x + surface.get_width()) // self.tile_size + 1)

        start_row = max(0, camera_y // self.tile_size)
        end_row = min(self.rows, (camera_y + surface.get_height()) // self.tile_size + 1)

        # Draw only tiles in view
        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                tile_idx = self.map_data[row][col]
                if tile_idx < len(self.tiles):
                    tile = self.tiles[tile_idx]
                    x = col * self.tile_size - camera_x
                    y = row * self.tile_size - camera_y
                    surface.blit(tile, (x, y))
