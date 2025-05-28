import pygame

from .config import *
import os

IMAGE_DIR = os.path.join("assets", "images")

def load_image(name, scale_to=None, alpha=True):
    path = os.path.join(IMAGE_DIR, name)
    image = pygame.image.load(path)
    if alpha:
        image = image.convert_alpha()
    else:
        image = image.convert()
    if scale_to:
        image = pygame.transform.smoothscale(image, scale_to)
    return image

def load_half_image(name):
    full_image = load_image(name)
    size = full_image.get_size()
    return pygame.transform.smoothscale(full_image, (size[0] // 2, size[1] // 2))


class DwarfCursor:
    def __init__(self, cursor_frames, hotspot=(90, 120), delay=100):
        self.frames = cursor_frames
        self.hotspot = hotspot
        self.delay = delay
        self.current_index = 0
        self.last_update = pygame.time.get_ticks()
        self.grabbing = False
        self.animation_sequence = []
        self.animation_step = 0
        self.set_cursor(0)

    def set_cursor(self, index):
        if index == 0:
            self.hotspot = (5, 5)
        elif index == 1:
            self.hotspot = (20, 20)

        pygame.mouse.set_cursor(pygame.cursors.Cursor(self.hotspot, self.frames[index]))
        


    def set_idle(self):
        if not self.grabbing:
            self.current_index = 0
            self.set_cursor(0)

    def set_hover(self):
        if not self.grabbing:
            self.current_index = 1
            self.set_cursor(1)

    def grab(self):
        if self.grabbing:
            return
        self.grabbing = True
        self.animation_sequence = [2, 3, 2, 1]
        self.animation_step = 0
        self.last_update = pygame.time.get_ticks()
        self.set_cursor(2)  # start immediately

    def update(self):
        if self.grabbing:
            now = pygame.time.get_ticks()
            if now - self.last_update >= self.delay:
                self.last_update = now
                self.animation_step += 1
                if self.animation_step < len(self.animation_sequence):
                    self.set_cursor(self.animation_sequence[self.animation_step])
                else:
                    self.grabbing = False
    
    def getState(self):
        return self.current_index
    
    def hide(self):
        pygame.mouse.set_visible(False)

    def show(self):
        pygame.mouse.set_visible(True)
        self.set_cursor(self.current_index)







cursor_frames = [
    load_image("cursor\\hand\\cursor_hand_point.png", scale_to=(128, 128)),
    load_image("cursor\\hand\\cursor_hand_reach.png", scale_to=(128, 128)),
    load_image("cursor\\hand\\cursor_hand_fist.png", scale_to=(128, 128)),
    load_image("cursor\\hand\\cursor_hand_palm.png", scale_to=(128, 128)),
]
cursor = DwarfCursor(cursor_frames)

logo_sprite_sheet_image = load_image("start_menu\\logo_sprite_sheet.png")
start_background_image = load_image("background\\new\\start_background.jpg", (SCREEN_WIDTH, SCREEN_HEIGHT))
map_background_image = load_image("background\\new\\map_background.png", (SCREEN_WIDTH, SCREEN_HEIGHT))

sword_icon_image = load_image("icons\\sword.png") 
gear_icon_image = load_image("icons\\gear.png") 
book_icon_image = load_image("icons\\book.png")
music_icon_image = load_image("icons\\music.png") 

book_item_image = load_image("items\\closed_book.png") 
candle_item_image = load_image("items\\candle.png") 
key_item_image = load_image("items\\key.png") 
lock_item_image = load_image("items\\lock.png") 

cloud_image = load_image("util\\cloud.png")
rule_paper_image = load_image("start_menu\\paper\\rule_paper.png")

lvl1_background_image = load_image("background\\new\\lvl1_background.png", scale_to=(3000, 2000))
customize_book_image = load_image("util\\customize_book.png")
dwarf_stamp = load_image("util\\dwarf_stamp.png", scale_to=(400, 400))

cover_lvl1 = pygame.transform.smoothscale_by(load_image("covers\\cover_lvl1.png"), 0.7)
cover_lvl1_end = pygame.transform.smoothscale_by(load_image("covers\\cover_lvl1_end.png"), 0.7)

forrest_spirit_image = pygame.transform.smoothscale_by(load_image("characters\\npc\\spirit_sheet.png"), 0.3)
forrest_spirit_cloud_image = pygame.transform.smoothscale_by(load_image("characters\\npc\\spirit_cloud.png"), 0.1)


book_collectable_image = pygame.transform.smoothscale_by(load_image("items\\collectables\\book_collectable.png"), 0.2)
closed_book_image = pygame.transform.smoothscale_by(load_image("items\\lvl1_closed_book.png"), 0.1)
book_tray_image = pygame.transform.smoothscale_by(load_image("util\\book_tray.png"), 0.3)

hint_image = pygame.transform.smoothscale_by(load_image("start_menu\\paper\\rule_paper.png"), 0.3)
score_paper = pygame.transform.smoothscale_by(load_image("util\\score_paper.png"), 0.3)


paper_frames_path = [
            "assets/images/start_menu/paper/paper1.png",
            "assets/images/start_menu/paper/paper2.png",
            "assets/images/start_menu/paper/paper3.png",
            "assets/images/start_menu/paper/paper4.png"
        ]
base_paper_path = [
            "assets/images/start_menu/paper/base_paper1.png",
            "assets/images/start_menu/paper/base_paper2.png",
            "assets/images/start_menu/paper/base_paper3.png",
            "assets/images/start_menu/paper/base_paper4.png",
        ]

level_icons_images = [
    load_image("icons\\circle\\1_circle_icon.png", scale_to=(150, 150)),
    load_image("icons\\circle\\2_circle_icon.png", scale_to=(150, 150)),
    load_image("icons\\circle\\3_circle_icon.png", scale_to=(150, 150)),
    load_image("icons\\circle\\4_circle_icon.png", scale_to=(150, 150)),
    load_image("icons\\circle\\5_circle_icon.png", scale_to=(150, 150)),
    load_image("icons\\circle\\6_circle_icon.png", scale_to=(150, 150)),
    load_image("icons\\circle\\lock_circle_icon.png", scale_to=(150, 150))
]


impact_sounds = [
    pygame.mixer.Sound("assets/audio/effects/wood_hit/wood_hit_pitch1.mp3"),
    pygame.mixer.Sound("assets/audio/effects/wood_hit/wood_hit_pitch2.mp3"),
    pygame.mixer.Sound("assets/audio/effects/wood_hit/wood_hit_pitch3.wav"),
    pygame.mixer.Sound("assets/audio/effects/wood_hit/wood_hit_pitch4.mp3"),
]
paper_flutter_sounds = [
    pygame.mixer.Sound("assets/audio/effects/paper_flutter/paper_flutter_pitch1.mp3"),
    pygame.mixer.Sound("assets/audio/effects/paper_flutter/paper_flutter_pitch2.mp3"),
    pygame.mixer.Sound("assets/audio/effects/paper_flutter/paper_flutter_pitch3.mp3"),
]
paper_crumble_sounds = [
    pygame.mixer.Sound("assets/audio/effects/paper_crumble/paper_crumble_pitch1.mp3"),
    pygame.mixer.Sound("assets/audio/effects/paper_crumble/paper_crumble_pitch2.mp3"),
    pygame.mixer.Sound("assets/audio/effects/paper_crumble/paper_crumble_pitch3.mp3"),
]
lock_sounds = [
    pygame.mixer.Sound("assets/audio/effects/lock/lock_sound_pitch1.mp3"),
    pygame.mixer.Sound("assets/audio/effects/lock/lock_sound_pitch2.mp3"),
    pygame.mixer.Sound("assets/audio/effects/lock/lock_sound_pitch3.mp3"),
]
leaf_sound = pygame.mixer.Sound("assets/audio/effects/leaf.mp3")
book_shuffle_sound = pygame.mixer.Sound("assets/audio/effects/book_shuffle.mp3")


dwarf_animations = {
    "idle_front": load_half_image("characters\\dwarf\\dwarf_front.png"),
    "idle_up": load_half_image("characters\\dwarf\\dwarf_back.png"),
    "idle_left": load_half_image("characters\\dwarf\\dwarf_front.png"),
    "idle_right": pygame.transform.flip(load_half_image("characters\\dwarf\\dwarf_front.png"), True, False),
    "down": [
        load_half_image("characters\\dwarf\\dwarf_walk_front2.png"), 
        load_half_image("characters\\dwarf\\dwarf_front.png"),
        pygame.transform.flip(load_half_image("characters\\dwarf\\dwarf_walk_front2.png"), True, False),
        load_half_image("characters\\dwarf\\dwarf_front.png"),
    ],
    "up": [
        load_half_image("characters\\dwarf\\dwarf_walk_back1.png"),
        load_half_image("characters\\dwarf\\dwarf_back.png"),
        pygame.transform.flip(load_half_image("characters\\dwarf\\dwarf_walk_back1.png"), True, False),
        load_half_image("characters\\dwarf\\dwarf_back.png"),
    ],
    "right": [
        pygame.transform.flip(load_half_image("characters\\dwarf\\dwarf_walk_front1.png"), True, False), 
        pygame.transform.flip(load_half_image("characters\\dwarf\\dwarf_walk_front2.png"), True, False), 
        pygame.transform.flip(load_half_image("characters\\dwarf\\dwarf_walk_front3.png"), True, False)
    ],
    "left": [
        load_half_image("characters\\dwarf\\dwarf_walk_front1.png"), 
        load_half_image("characters\\dwarf\\dwarf_walk_front2.png"), 
        load_half_image("characters\\dwarf\\dwarf_walk_front3.png")
    ], 
    "hide": [
        pygame.transform.smoothscale_by(load_half_image("characters\\dwarf\\dwarf_numavezi.png"), 1.06)
    ]
}



goblin_animations = {
    "idle_left": pygame.transform.smoothscale_by(pygame.transform.flip(load_half_image("characters\\enemies\\goblin\\goblin3.png"), True, False), 0.6),
    "idle_right": pygame.transform.smoothscale_by(load_half_image("characters\\enemies\\goblin\\goblin3.png"), 0.6),
    "move_left": [
        pygame.transform.smoothscale_by(pygame.transform.flip(load_half_image("characters\\enemies\\goblin\\goblin1.png"), True, False), 0.6),
        pygame.transform.smoothscale_by(pygame.transform.flip(load_half_image("characters\\enemies\\goblin\\goblin2.png"), True, False), 0.6),
    ],
    "move_right": [
        pygame.transform.smoothscale_by(load_half_image("characters\\enemies\\goblin\\goblin1.png"), 0.6),
        pygame.transform.smoothscale_by(load_half_image("characters\\enemies\\goblin\\goblin2.png"), 0.6),
    ],
    "grab": [
        pygame.transform.smoothscale_by(load_half_image("characters\\enemies\\goblin\\goblin_grab.png"), 0.6),
    ]
}


writing_sound = pygame.mixer.Sound("assets/audio/effects/writing.mp3")
sliding_on_table_sound = pygame.mixer.Sound("assets/audio/effects/sliding_on_table.mp3")
wind_sound = pygame.mixer.Sound("assets/audio/effects/wind.mp3")
enter_level = pygame.mixer.Sound("assets/audio/effects/enter_level.mp3")
level_completed = pygame.mixer.Sound("assets/audio/effects/level_completed.mp3")
stamp_sound = pygame.mixer.Sound("assets/audio/effects/stamp.mp3")


narrator_rules_sound = pygame.mixer.Sound("assets/audio/narrator/narrator_rules.mp3")
narrator_intro_sound = pygame.mixer.Sound("assets/audio/narrator/narrator_intro.mp3")
narrator_oh_you_found_this_sound = pygame.mixer.Sound("assets/audio/narrator/narrator_oh_you_found_this.mp3")
narrator_lvl1_into_sound = pygame.mixer.Sound("assets/audio/narrator/narrator_lvl1_into.mp3")
narrator_lvl1_outro_sound = pygame.mixer.Sound("assets/audio/narrator/narrator_lvl1_outro.mp3")

walking_on_grass_sound = pygame.mixer.Sound("assets/audio/effects/walking_on_grass.mp3")
book_catch_sound =  pygame.mixer.Sound("assets/audio/effects/book_catch.mp3")
goblin_sounds =  [
    pygame.mixer.Sound("assets/audio/effects/goblin/goblin1.mp3"),
    pygame.mixer.Sound("assets/audio/effects/goblin/goblin2.mp3"),
    pygame.mixer.Sound("assets/audio/effects/goblin/goblin3.mp3"),
    pygame.mixer.Sound("assets/audio/effects/goblin/goblin4.mp3"),
    pygame.mixer.Sound("assets/audio/effects/goblin/goblin5.mp3"),
    pygame.mixer.Sound("assets/audio/effects/goblin/goblin6.mp3"),
    pygame.mixer.Sound("assets/audio/effects/goblin/goblin7.mp3"),
    pygame.mixer.Sound("assets/audio/effects/goblin/goblin8.mp3"),
]

wrong_answear_sound = pygame.mixer.Sound("assets/audio/effects/answear/wrong_sound.mp3")
correct_answear_sound = pygame.mixer.Sound("assets/audio/effects/answear/correct_sound.mp3")


map_size1 = (3000, 2000)


tree_tops_image = load_image("levels\\lvl1\\tree_tops.png", scale_to=map_size1)

# Match size of level background and expand
parallax_layers = []

scales = [0.59, 0.63, 0.65]
rotations = [0, 180, 0]

for s, rot in zip(scales, rotations):
    layer = pygame.transform.rotozoom(tree_tops_image, rot, s)
    parallax_layers.append(layer)






questions = [
    {
        "question_en": "Which is NOT a medieval work?",
        "question_ro": "Care NU este o lucrare medievală?",
        "answers_en": ["The Divine Comedy", "The Prince", "The Song of Roland", "The Canterbury Tales"],
        "answers_ro": ["Divina Comedie", "Principele", "Cântecul lui Roland", "Poveștile din Canterbury"],
        "hint_en": "This one is by Machiavelli, from the Renaissance.",
        "hint_ro": "Aceasta este scrisă de Machiavelli, din perioada Renașterii.",
        "correct_index": 1
    }
]

