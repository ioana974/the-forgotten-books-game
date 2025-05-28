import pygame
import sys

# Inițializare
pygame.init()

# Setări ecran
WIDTH, HEIGHT = 1152, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Escape Room - Cetatea Industrială")

# FPS și ceas
clock = pygame.time.Clock()
FPS = 60

# Fundal și redimensionare
background = pygame.image.load("atelier.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Fonturi și culori
font = pygame.font.SysFont("arial", 24)
BIG_FONT = pygame.font.SysFont("arial", 36)
WHITE = (255, 255, 255)
YELLOW = (255, 215, 0)

# Sunete (opțional)
click_sound = None
success_sound = None
try:
    click_sound = pygame.mixer.Sound("click.wav")
    success_sound = pygame.mixer.Sound("success.wav")
except:
    print("Sunetele nu au fost încărcate (opțional)")

# Cursor custom (opțional)
pygame.mouse.set_cursor(*pygame.cursors.broken_x)

# Obiecte și inventar
inventory = []
MAX_INVENTORY = 5

# NOU: Obiecte cu poziții corecte în funcție de imaginea atelier.png
objects = {
    "cheie": {
        "rect": pygame.Rect(550, 715, 50, 25),     # pe covor
        "found": False,
        "desc": "O cheie ruginită"
    },
    "ciocan": {
        "rect": pygame.Rect(100, 490, 80, 30),     # pe masa stânga
        "found": False,
        "desc": "Un ciocan vechi"
    },
    "roata": {
        "rect": pygame.Rect(1010, 675, 40, 40),    # sub masa dreapta
        "found": False,
        "desc": "O rotiță de cupru"
    }
}

# Seif - pe perete stânga
safe_rect = pygame.Rect(50, 250, 100, 140)

# NOU: Feedback vizual îmbunătățit
def draw_interactive_feedback():
    for name, data in objects.items():
        if data["found"]:
            pygame.draw.rect(screen, (0, 200, 0), data["rect"], 2)  # discret, doar după ce e găsit

    if safe_opened:
        pygame.draw.rect(screen, (0, 255, 0), safe_rect, 3)


# Seiful
safe_rect = pygame.Rect(50, 270, 90, 120)
safe_opened = False

# Final
game_completed = False

def draw_inventory():
    pygame.draw.rect(screen, (40, 40, 40), (0, HEIGHT - 80, WIDTH, 80))
    draw_text("Inventar:", (10, HEIGHT - 70), WHITE)
    for idx, item in enumerate(inventory):
        draw_text(item, (150 + idx * 150, HEIGHT - 50), YELLOW)

def draw_text(text, pos, color=WHITE, font_override=None):
    f = font_override if font_override else font
    screen.blit(f.render(text, True, color), pos)

def handle_click(pos):
    global safe_opened, game_completed

    # Obiecte
    for name, data in objects.items():
        if data["rect"].collidepoint(pos) and not data["found"]:
            data["found"] = True
            inventory.append(name)
            if click_sound: click_sound.play()
            print(f"Ai găsit {name} - {data['desc']}")

    # Seif
    if safe_rect.collidepoint(pos):
        if "cheie" in inventory and not safe_opened:
            safe_opened = True
            if success_sound: success_sound.play()
            print("Ai deschis seiful!")
        elif not safe_opened:
            print("Seiful e încuiat...")

    # Finalizare joc
    if safe_opened and len(inventory) == len(objects):
        game_completed = True

def draw_interactive_feedback():
    for name, data in objects.items():
        if data["found"]:
            pygame.draw.rect(screen, (0, 255, 0), data["rect"], 2)

    if safe_opened:
        pygame.draw.rect(screen, (0, 255, 0), safe_rect, 3)
    else:
        pygame.draw.rect(screen, (255, 0, 0), safe_rect, 2)

# MAIN LOOP
running = True
while running:
    clock.tick(FPS)
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            handle_click(event.pos)

    draw_inventory()
    draw_interactive_feedback()

    # Mesaje status
    if game_completed:
        draw_text("Felicitări! Ai evadat din atelier!", (WIDTH // 2 - 250, 50), YELLOW, BIG_FONT)
    elif safe_opened:
        draw_text("Seiful e deschis! Ceva e înăuntru...", (WIDTH // 2 - 200, 50))
    else:
        draw_text("Caută indicii în atelier...", (WIDTH // 2 - 150, 50))

    pygame.display.flip()

pygame.quit()
sys.exit()
