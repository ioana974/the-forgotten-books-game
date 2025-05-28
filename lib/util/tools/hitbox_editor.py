import pygame
import sys

pygame.init()

# Config
TREE_SHEET = "assets/images/levels/lvl1/tree.png"
ROWS, COLS = 2, 2
SCALE = 1.0
SCREEN_SIZE = (400, 400)

# Setup
screen = pygame.display.set_mode(SCREEN_SIZE)
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 18)

sheet = pygame.image.load(TREE_SHEET).convert_alpha()
sheet_width, sheet_height = sheet.get_size()
tree_w = sheet_width // COLS
tree_h = sheet_height // ROWS

# Extract trees
trees = []
for y in range(ROWS):
    for x in range(COLS):
        rect = pygame.Rect(x * tree_w, y * tree_h, tree_w, tree_h)
        tree = sheet.subsurface(rect)
        if SCALE != 1.0:
            tree = pygame.transform.smoothscale(
                tree,
                (int(tree_w * SCALE), int(tree_h * SCALE))
            )
        trees.append(tree)

hitboxes = []

# Selection state
current_index = 0
selecting = False
start_pos = None
current_rect = None

def draw_tree():
    screen.fill((30, 30, 30))
    tree = trees[current_index]
    tw, th = tree.get_size()
    screen.blit(tree, ((SCREEN_SIZE[0] - tw) // 2, (SCREEN_SIZE[1] - th) // 2))

    if current_rect:
        pygame.draw.rect(screen, (255, 0, 0), current_rect, 2)

    label = font.render(f"Tree {current_index + 1}/{len(trees)}", True, (255, 255, 255))
    screen.blit(label, (10, 10))

running = True
while running:
    draw_tree()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            selecting = True
            start_pos = pygame.mouse.get_pos()

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            selecting = False
            end_pos = pygame.mouse.get_pos()
            x1, y1 = start_pos
            x2, y2 = end_pos
            rx, ry = min(x1, x2), min(y1, y2)
            rw, rh = abs(x2 - x1), abs(y2 - y1)

            # Convert screen coords to image-relative coords
            tree = trees[current_index]
            tree_x = (SCREEN_SIZE[0] - tree.get_width()) // 2
            tree_y = (SCREEN_SIZE[1] - tree.get_height()) // 2
            image_rect = pygame.Rect(rx - tree_x, ry - tree_y, rw, rh)

            hitboxes.append((
                image_rect.x,
                image_rect.y,
                image_rect.width,
                image_rect.height
            ))

            current_index += 1
            current_rect = None

            if current_index >= len(trees):
                running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    if selecting and start_pos:
        x1, y1 = start_pos
        x2, y2 = pygame.mouse.get_pos()
        rx, ry = min(x1, x2), min(y1, y2)
        rw, rh = abs(x2 - x1), abs(y2 - y1)
        current_rect = pygame.Rect(rx, ry, rw, rh)

    pygame.display.flip()
    clock.tick(60)

# Output results
print("\nTREE_HITBOXES = [")
for hb in hitboxes:
    print(f"    {hb},")
print("]")
