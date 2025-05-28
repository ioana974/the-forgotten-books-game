import pygame
import sys

# Initializare Pygame
pygame.init()

# Setări ecran
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Regatul Cronogrilor: Pădurea Cărților Pierdute")

# Culori
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Fonturi
font_small = pygame.font.Font(None, 20)
font_medium = pygame.font.Font(None, 30)
font_large = pygame.font.Font(None, 40)

# Încărcare imagini cu verificare de erori
def incarca_imagine(nume_fisier):
    try:
        return pygame.image.load(nume_fisier).convert_alpha()
    except pygame.error:
        print(f"Eroare la încărcarea imaginii: {nume_fisier}")
        sys.exit()

player_img = incarca_imagine("image-proxy.png")
goblin_img = incarca_imagine("caprapiti.png")
book_img = incarca_imagine("image-proxy3.png")
sadogandul_img = incarca_imagine("caprapiti.png")
padure_img = incarca_imagine("image-proxy4.png").convert()
capcana_img = incarca_imagine("image-proxy5.png")
text_bubble_img = incarca_imagine("image-proxy2.png")

# Redimensionare imagini (optional, dar recomandat pentru a controla dimensiunile)
player_img = pygame.transform.scale(player_img, (40, 60))
goblin_img = pygame.transform.scale(goblin_img, (30, 50))
book_img = pygame.transform.scale(book_img, (20, 30))
sadogandul_img = pygame.transform.scale(sadogandul_img, (80, 120))
capcana_img = pygame.transform.scale(capcana_img, (30, 30))


# Clasa Player
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed = 5
        self.inventory = []

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed = 5
        self.inventory = []

    def update(self, keys, camera_x, camera_y):
        dx = 0
        dy = 0
        if keys[pygame.K_LEFT]:
            dx -= self.speed
        if keys[pygame.K_RIGHT]:
            dx += self.speed
        if keys[pygame.K_UP]:
            dy -= self.speed
        if keys[pygame.K_DOWN]:
            dy += self.speed

        # Actualizează poziția jucătorului, luând în considerare limitele lumii
        self.rect.x = max(0, min(world_width - self.rect.width, self.rect.x + dx))
        self.rect.y = max(0, min(world_height - self.rect.height, self.rect.y + dy))

        # Returnează noua poziție a camerei
        return self.rect.x - camera_x, self.rect.y - camera_y

# Clasa Goblin
class Goblin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = goblin_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 2
        self.direction = 1  # 1 inseamna dreapta, -1 inseamna stanga
        self.original_x = x  # Pozitia initiala pentru a se intoarce

    def update(self, camera_x, camera_y):
        # Misca Goblinul stanga-dreapta
        self.rect.x += self.speed * self.direction

        # Verifica daca Goblinul a ajuns la o margine
        if self.rect.x <= self.original_x - 50 or self.rect.x >= self.original_x + 50:
            self.direction *= -1  # Schimba directia

        # Ajusteaza pozitia cu camera
        self.rect.x -= camera_x
        self.rect.y -= camera_y
# Clasa Book
class Book(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = book_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.collected = False

    def update(self, camera_x, camera_y):
        self.rect.x -= camera_x
        self.rect.y -= camera_y

# Clasa Sadogandul
class Sadogandul(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = sadogandul_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.dialogue = [
            "Bine ai venit, mic pitic!",
            "Goblinul Cenzurii a furat cărțile!",
            "Recuperează-le pentru mine."
        ]
        self.dialogue_index = 0
        self.show_dialogue = False

    def update(self, camera_x, camera_y):
        self.rect.x -= camera_x
        self.rect.y -= camera_y

    def start_dialogue(self):
        self.show_dialogue = True
        self.dialogue_index = 0  # Reseteaza indexul la inceputul dialogului

    def next_dialogue(self):
        self.dialogue_index += 1
        if self.dialogue_index >= len(self.dialogue):
            self.show_dialogue = False

    def draw_dialogue(self, screen):
        if self.show_dialogue:
            text_surface = font_medium.render(self.dialogue[self.dialogue_index], True, BLACK)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            screen.blit(text_bubble_img, (text_rect.x - 20, text_rect.y - 10)) #deseneaza text_bubble
            screen.blit(text_surface, text_rect)

#Clasa Capcana
class Capcana(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = capcana_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.activated = False
        self.visible = True

    def update(self, camera_x, camera_y):
        self.rect.x -= camera_x
        self.rect.y -= camera_y

    def activate(self):
        self.activated = True
        self.visible = False

    def draw(self, screen):
        if self.visible:
            screen.blit(self.image, (self.rect.x, self.rect.y))


# Grupuri de sprites
all_sprites = pygame.sprite.Group()
goblin_group = pygame.sprite.Group()
book_group = pygame.sprite.Group()
capcana_group = pygame.sprite.Group()

# Dimensiunile lumii (mai mari decat ecranul, pentru scrolling)
world_width = 2000  # Exemplu, poti ajusta
world_height = 1000 # Exemplu, poti ajusta


# Creare Player
player = Player()
all_sprites.add(player)

# Creare Goblin
goblin1 = Goblin(600, 450)
goblin2 = Goblin(1200, 300)
all_sprites.add(goblin1, goblin2)
goblin_group.add(goblin1, goblin2)

# Creare Carti
book1 = Book(300, 200)
book2 = Book(800, 100)
book3 = Book(1500, 400)
all_sprites.add(book1, book2, book3)
book_group.add(book1, book2, book3)

# Creare Sadogandul
sadogandul = Sadogandul(1800, 350)
all_sprites.add(sadogandul)

#Creare Capcane
capcana1 = Capcana(400, 500)
capcana2 = Capcana(900, 250)
all_sprites.add(capcana1, capcana2)
capcana_group.add(capcana1, capcana2)


#pozitii initiale
book1_initial_x = book1.rect.x
book1_initial_y = book1.rect.y
book2_initial_x = book2.rect.x
book2_initial_y = book2.rect.y
book3_initial_x = book3.rect.x
book3_initial_y = book3.rect.y

# Setari camera
camera_x = 0
camera_y = 0

# Text narativ la sfarsit
story_text = [
    "NIVEL 1: Pădurea Cărților Pierdute",
    "Sadogândul, spiritul pădurii, scrie povești pe frunze.",
    "Goblinul Cenzurii a furat cărțile magice ale epocii interbelice!",
    "Ajută-l pe Sadogândul să le recupereze și să învețe istoria literară!"
]

history_lesson = [
    "Lecție: Cultura și literatura interbelică",
    "Anii 1920–1940 au fost o perioadă de efervescență culturală în România.",
    "Scriitori ca Tudor Arghezi, Lucian Blaga, Hortensia Papadat-Bengescu, Camil Petrescu au definit epoca.",
    "Mihail Sadoveanu, unul dintre cei mai prolifici autori, scria romane de inspirație istorică și rurală.",
    "Au apărut reviste literare importante precum *Gândirea*, *Viața Românească*, *Contimporanul*.",
    "Aceste publicații au reflectat curente moderne, tradiționaliste, simboliste și avangardiste."
]

# Stare joc
running = True
level_complete = False
show_history = False
dialogue_active = False  # Variabila pentru a urmari daca dialogul este activ

# Functie pentru afisare text
def draw_text(surface, text, x, y, color):
    text_surface = font_medium.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_surface, text_rect)

# Functie pentru mini-quiz
def quiz(screen):
    question = "Care revistă literară a fost importantă în perioada interbelică?"
    options = [
        ("1. Gândirea", pygame.K_1),
        ("2. Viața Românească", pygame.K_2),
        ("3. Contimporanul", pygame.K_3)
    ]
    correct_key = pygame.K_1  # Doar Gândirea e corectă în acest exemplu

    waiting_for_answer = True
    result = None

    while waiting_for_answer:
        screen.fill(BLACK)
        draw_text(screen, question, SCREEN_WIDTH // 2, 100, WHITE)

        for i, (option_text, _) in enumerate(options):
            draw_text(screen, option_text, SCREEN_WIDTH // 2, 180 + i * 40, YELLOW)

        draw_text(screen, "Apasă 1, 2 sau 3 pentru a răspunde", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80, WHITE)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == correct_key:
                    result = True
                    waiting_for_answer = False
                elif event.key in [k for _, k in options]:
                    result = False
                    waiting_for_answer = False

    return result


# Game loop
clock = pygame.time.Clock()  # Crează un obiect de tip Clock
while running:
    # Evenimente
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and sadogandul.show_dialogue:
                sadogandul.next_dialogue()  # Avansăm la următorul mesaj
            if event.key == pygame.K_e and sadogandul.rect.colliderect(player.rect):
                sadogandul.start_dialogue()


    keys = pygame.key.get_pressed()

    # Actualizare
    if not level_complete:
        # Actualizeaza player si obtine noua pozitie a camerei
        player_x, player_y = player.update(keys, camera_x, camera_y)

        # Calculeaza deplasarea camerei astfel incat playerul sa fie centrat
        camera_x = player_x - SCREEN_WIDTH // 2
        camera_y = player_y - SCREEN_HEIGHT // 2

        # Limiteaza camera sa nu arate in afara lumii
        camera_x = max(0, min(camera_x, world_width - SCREEN_WIDTH))
        camera_y = max(0, min(camera_y, world_height - SCREEN_HEIGHT))

        # Actualizeaza celelalte sprite-uri cu pozitia camerei
        for sprite in all_sprites:
                sprite.RenderUpdates.draw
              #actualizeaza sprite-urile cu camera
            # PROBLEMA AICI ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

        #Verifica coliziuni
        for book in book_group:
            if player.rect.colliderect(book.rect):
                book.collected = True
                book_group.remove(book)
                all_sprites.remove(book)
                player.inventory.append("Carte")

        #Verifica coliziune cu capcane
        for capcana in capcana_group:
            if player.rect.colliderect(capcana.rect) and not capcana.activated:
                capcana.activate()
                print("Capcana activată!")

        # Verifica coliziunea cu Goblin
        if pygame.sprite.spritecollideany(player, goblin_group):
            print("Ai fost prins de un Goblin!")
            running = False  # sau reseteaza jocul, etc.

        # Verifica interactiunea cu Sadogandul
        if player.rect.colliderect(sadogandul.rect):
             if keys[pygame.K_e]: # apasa "e" pt dialog
                dialogue_active = True
                sadogandul.start_dialogue()

        # Verifica daca toate cartile au fost colectate
        if len(player.inventory) == 3:
            level_complete = True
            print("Nivel complet! Ai colectat toate cărțile!")

    # Desenare
    # Deseneaza fundalul (imaginea de padure)
    screen.blit(padure_img, (-camera_x, -camera_y))


    # deseneaza toate sprite-urile (inclusiv playerul, goblinii, cartile, Sadogandul)
    for sprite in all_sprites:
        if isinstance(sprite, Capcana): #deseneaza capcanele separat, pentru a putea fi "invizibile"
            sprite.draw(screen)
        else:
            screen.blit(sprite.image, (sprite.rect.x, sprite.rect.y))

    if sadogandul.show_dialogue:
        sadogandul.draw_dialogue(screen)

    # Afiseaza text informativ
    draw_text(screen, f"Carti colectate: {len(player.inventory)}/3", 150, 30, WHITE)


    if level_complete:
        draw_text(screen, "Nivel complet! Apasă SPACE pentru a continua...", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, GREEN)
        if keys[pygame.K_SPACE]:
            show_history = True

    if show_history:
        screen.fill(BLACK)
        y_offset = 50
        for line in history_lesson:
            draw_text(screen, line, SCREEN_WIDTH // 2, y_offset, WHITE)
            y_offset += 30
        draw_text(screen, "Apasă SPACE pentru a face quiz-ul!", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50, YELLOW)
        if keys[pygame.K_SPACE]:
            if quiz(screen):
                print("Felicitări! Ai trecut quiz-ul!")
                running = False  # sau incarca urmatorul nivel
            else:
                print("Mai încearcă!")
                show_history = False


    # Actualizare ecran
    pygame.display.flip()

    # Frame rate
    clock.tick(60)  # Limitează jocul la 60 FPS

# Inchidere Pygame
pygame.quit()
sys.exit()