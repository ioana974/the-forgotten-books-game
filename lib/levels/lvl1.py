import pygame
from lib.assets import *
from lib.config import *
from lib.util.spawners.tile_map import *
from lib.characters.dawrf_player import DwarfPlayer
from lib.util.spawners.tree_spawner import *
from lib.util.animations.tree_transition import *
from lib.characters.enemies.goblin import *
from lib.collectables.book import *
from lib.characters.sadogandul import *
from lib.util.popup.goblin_popup import *


class LevelOne:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.running = True
        self.dialogue_visible = False

        self.map_width, self.map_height = map_size1
        self.camera_x = self.camera_y = 0
        self.black = (0, 0, 0)

        self.level_completed = game_data["lvl1_completed"]
        self.goblin_popup = GoblinPopup()
        self.create_entities()

        self.goblin_popup_cooldown = 0

    

    def reset_level(self):
        self.level_completed = False
        self.create_entities()
        self.player.collected_books = 0

    def create_entities(self):
        self.tile_map = TileMap(
            tile_sheet_path="assets/images/levels/lvl1/forrest_ground_tiles.png",
            tile_size=128,
            area_width=3000,
            area_height=2000,
            scale=1,
            crop=10
        )

        self.tree_spawner = TreeSpawner(
            "assets/images/levels/lvl1/tree.png",
            tile_size=128,
            area_width=self.map_width,
            area_height=self.map_height,
            num_trees=50,
            scale=0.8,
            min_distance=380
        )

        self.player = self.spawn_player()
        self.goblins = self.spawn_goblins(count=5)
        self.books = self.spawn_books(count=12)
        
        tree_tops = self.tree_spawner.get_tree_top_rects()
        wizard_pos = self.find_sadogandul_position(self.player.rect, tree_tops, self.map_width, self.map_height)
        self.sadogandul = Sadogandul(pos=wizard_pos)

    def spawn_player(self):
        trunks = self.tree_spawner.get_trunk_hitboxes()
        while True:
            spawn_x = random.randint(200, self.map_width - 200)
            spawn_y = random.randint(200, self.map_height - 200)
            temp = DwarfPlayer(spawn_x, spawn_y)
            if not any(temp.get_tree_hitbox().colliderect(trunk) for trunk in trunks):
                return temp

    def spawn_goblins(self, count):
        goblins = pygame.sprite.Group()
        trunks = self.tree_spawner.get_trunk_hitboxes()

        for _ in range(count):
            for _ in range(100):  # Try 100 times
                x, y = random.randint(100, self.map_width - 100), random.randint(100, self.map_height - 100)
                goblin = Goblin(x, y)
                gob_rect = goblin.get_tree_hitbox()
                too_close_to_player = pygame.Vector2(x, y).distance_to(self.player.rect.center) < goblin.reach_radius + 60
                collides_trees = any(gob_rect.colliderect(t) for t in trunks)
                collides_others = any(gob_rect.colliderect(g.get_tree_hitbox()) for g in goblins)

                if not (too_close_to_player or collides_trees or collides_others):
                    goblins.add(goblin)
                    break
        return goblins

    def spawn_books(self, count):
        books = pygame.sprite.Group()
        trunks = self.tree_spawner.get_trunk_hitboxes()
        tree_tops = self.tree_spawner.get_tree_top_rects()
        existing_rects = trunks + [self.player.rect]

        border_margin = 200
        min_distance_between_books = 300

        while len(books) < count:
            x = random.randint(border_margin, self.map_width - border_margin)
            y = random.randint(border_margin, self.map_height - border_margin)
            book = Book(pos=(x, y))
            book_rect = book.rect.inflate(80, 80)

            too_close_to_existing = any(book_rect.colliderect(r.inflate(80, 80)) for r in existing_rects)
            too_close_to_books = any(
                pygame.Vector2(x, y).distance_to(b.rect.center) < min_distance_between_books
                for b in books
            )
            under_tree_top = any(book_rect.colliderect(top_rect) for top_rect in tree_tops)

            if not too_close_to_existing and not too_close_to_books and not under_tree_top:
                books.add(book)
                existing_rects.append(book.rect)

        return books

    def find_sadogandul_position(self, player_rect, tree_top_rects, map_width, map_height, max_distance=120):
        border_margin = 100
        attempts = 0

        while attempts < 200:
            angle = random.uniform(0, 2 * 3.14159)
            distance = random.randint(60, max_distance)
            offset = pygame.Vector2(distance, 0).rotate_rad(angle)

            x = player_rect.centerx + offset.x
            y = player_rect.centery + offset.y

            if not (border_margin <= x <= map_width - border_margin and border_margin <= y <= map_height - border_margin):
                attempts += 1
                continue

            wizard_rect = pygame.Rect(x - 20, y - 40, 40, 80)
            if any(wizard_rect.colliderect(tree_rect) for tree_rect in tree_top_rects):
                attempts += 1
                continue

            return pygame.Vector2(x, y)

        return pygame.Vector2(player_rect.center)



    def run(self):
        if self.level_completed:
            self.reset_level()
            
        self.update()
        self.draw()

        TreeTransition("assets/images/levels/lvl1/tree_tops.png").exit(background=screen.copy())
        if game_data["music_on"]:
            music_manager.load(1)
            music_manager.play()

        self.running = True
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        music_manager.pause()
        TreeTransition("assets/images/levels/lvl1/tree_tops.png").enter(background=screen.copy(), level_completed = self.level_completed, score=self.player.score)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_world = (
                    pygame.mouse.get_pos()[0] + self.camera_x,
                    pygame.mouse.get_pos()[1] + self.camera_y
                )
                self.player.check_click(mouse_world, self.map_width)
            elif event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_BACKSPACE, pygame.K_ESCAPE]:
                    if event.key == pygame.K_ESCAPE:
                        save_progress()
                        pygame.quit()
                        sys.exit()
                    self.running = False

    def update(self):
        if self.goblin_popup.visible:
            self.goblin_popup.update()
            return
        elif self.goblin_popup_cooldown > 0:
            self.goblin_popup_cooldown -= self.clock.get_time()

        
        dt = self.clock.get_time()
        keys = pygame.key.get_pressed()
        mouse_world = (
            pygame.mouse.get_pos()[0] + self.camera_x,
            pygame.mouse.get_pos()[1] + self.camera_y
        )

        dist_to_wizard = pygame.Vector2(self.player.rect.center).distance_to(self.sadogandul.position)
        self.dialogue_visible = dist_to_wizard < 120  # show dialogue if close

        if self.player.collected_books >= 12:
            if dist_to_wizard < 80:
                self.level_completed = True

                walking_on_grass_sound.fadeout(300)
                channel = level_completed.play()

                # Wait 800ms first
                pygame.time.delay(800)

                # Then fade out over 500ms
                channel.fadeout(200)

                # Optionally, wait for fadeout to finish
                while channel.get_busy():
                    pygame.time.delay(10)
                    pygame.event.pump()


                self.running = False

        self.player.update(dt, keys, mouse_world)
        self.player.check_book_collision(
            self.books,
            tree_spawner=self.tree_spawner,
            map_width=self.map_width,
            map_height=self.map_height
        )
        self.clamp_to_bounds(self.player.rect)

        self.resolve_tree_collision(self.player)

        if self.goblin_popup_cooldown <= 0:
            self.update_goblins(dt)
        self.books.update(dt)
        self.sadogandul.update(dt)

        center_x = self.player.rect.centerx

        self.camera_x = max(0, min(center_x - SCREEN_WIDTH // 2, self.map_width - SCREEN_WIDTH))
        self.camera_y = max(0, min(self.player.rect.centery - SCREEN_HEIGHT // 2, self.map_height - SCREEN_HEIGHT))

    def update_goblins(self, dt):
        trunks = self.tree_spawner.get_trunk_hitboxes()
        for goblin in self.goblins:
            goblin.player_hitbox = self.player.get_tree_hitbox()
            self.check_goblin_flee(goblin)

            goblin.update(
                        dt, 
                        self.player.get_tree_hitbox(),
                        self.tree_spawner.get_trunk_hitboxes(), 
                        self.player.has_books()
            )

            for trunk in trunks:
                if goblin.get_tree_hitbox().colliderect(trunk):
                    goblin.undo_last_movement()
                    break
            else:
                for other in self.goblins:
                    if other is not goblin and goblin.get_tree_hitbox().colliderect(other.get_tree_hitbox()):
                        goblin.undo_last_movement()
                        break
                else:
                    goblin.last_pos = goblin.rect.topleft

    def resolve_tree_collision(self, entity):
        for trunk in self.tree_spawner.get_trunk_hitboxes():
            if entity.get_tree_hitbox().colliderect(trunk):
                entity.undo_last_movement()
                break

    def clamp_to_bounds(self, rect):
        rect.left = max(0, rect.left)
        rect.right = min(self.map_width, rect.right)
        rect.top = max(0, rect.top)
        rect.bottom = min(self.map_height, rect.bottom)

    def draw(self):
        screen.fill(self.black)
        self.tile_map.draw(screen, self.camera_x, self.camera_y)

        drawables = []

        # Add trees
        for img, (x, y), _, _ in self.tree_spawner.spawned:
            drawables.append({
                "image": img,
                "x": x,
                "y": y,
                "sort_y": y + img.get_height(),
                "type": "tree"
            })

        # Add player
        drawables.append({
            "image": self.player.image,
            "x": self.player.rect.x,
            "y": self.player.rect.y,
            "sort_y": self.player.rect.bottom,
            "type": "player"
        })

        # Add goblins and books
        drawables += [
            {
                "image": goblin.image, 
                "x": goblin.rect.x, 
                "y": goblin.rect.y, 
                "sort_y": goblin.rect.bottom,
                "type": "goblin"
                }
            for goblin in self.goblins
        ]
        drawables += [
            {
                "image": book.image, 
                "x": book.rect.x, 
                "y": book.rect.y, 
                "sort_y": book.rect.bottom,
                "type": "book"
                }
            for book in self.books
        ]

        drawables += [self.sadogandul.get_sprite()]

        # Sort by Y
        drawables.sort(key=lambda d: d["sort_y"])

        #self.player.draw_hitbox(self.camera_x, self.camera_y)
        #self.tree_spawner.draw_hitboxes(screen, self.camera_x, self.camera_y)

        # Blit everything with flipping
        for item in drawables:
            if item.get("custom_draw"):
                self.sadogandul.draw(screen, self.camera_x, self.camera_y)
                continue

            is_env = item.get("type") in ("tree", "book", "goblin")  # We'll tag these later
            draw_x = self.get_draw_position(item["x"], item["image"].get_width(), flip=self.player.flip if is_env else False)
            draw_y = item["y"] - self.camera_y
            screen.blit(item["image"], (draw_x, draw_y))

        self.draw_wizard_dialogue()
        self.draw_parallax_layers()
        self.draw_book_counter()
        self.player.draw_score_hud()

        self.goblin_popup.draw(screen)


    def draw_parallax_layers(love):
        px_ratio_x = love.player.rect.centerx / love.map_width
        px_ratio_y = love.player.rect.centery / love.map_height

        if love.player.flip:
            px_ratio_x = 1 - px_ratio_x

        for i, layer in enumerate(parallax_layers):
            lw, lh = layer.get_size()
            strength = int((i + 1) ** 1.3 * 60)

            offset_x = int((px_ratio_x - 0.5) * strength)
            offset_y = int((px_ratio_y - 0.5) * strength)

            pos_x = (SCREEN_WIDTH - lw) // 2 + offset_x
            pos_y = (SCREEN_HEIGHT - lh) // 2 + offset_y

            screen.blit(layer, (pos_x, pos_y))


    def calculate_edge_offset(self, cam_pos, map_limit, screen_limit, zone):
        if cam_pos < zone:
            return min((zone - cam_pos) / zone, 1)
        elif cam_pos > map_limit - screen_limit - zone:
            return min((cam_pos - (map_limit - screen_limit - zone)) / zone, 1)
        return 0



    def check_goblin_flee(self, goblin):
        if not goblin.fleeing:
            return

        goblin_center = pygame.Vector2(goblin.get_hitbox().center)

        # Generate a flee target only once
        if goblin.flee_target is None:
            tree_tops = self.tree_spawner.get_tree_top_rects()
            trunks = self.tree_spawner.get_trunk_hitboxes()
            existing_rects = [b.rect for b in self.books] + trunks + [self.player.rect]
            border_margin = 200

            for _ in range(170):  # Try up to 100 valid targets
                angle = random.uniform(0, 2 * math.pi)
                direction = pygame.Vector2(math.cos(angle), math.sin(angle)).normalize()
                distance = random.randint(900, 1600)

                target = goblin_center + direction * distance
                target.x = max(border_margin, min(self.map_width - border_margin, target.x))
                target.y = max(border_margin, min(self.map_height - border_margin, target.y))

                book_rect = pygame.Rect(int(target.x), int(target.y), 40, 40).inflate(80, 80)
                too_close = any(book_rect.colliderect(r.inflate(80, 80)) for r in existing_rects)
                under_tree_top = any(book_rect.colliderect(t) for t in tree_tops)

                if not too_close and not under_tree_top:
                    self.player.wrong_streak += 1
                    penalty = 50 + self.player.wrong_streak * 10
                    self.player.score =  max(0, self.player.score - penalty)
                    self.player.collected_books = max(0, self.player.collected_books - 1)

                    if not self.player.has_books():
                        for g in self.goblins:
                            g.aggroed = False

                    goblin.flee_target = target
                    goblin.has_stolen_book = True
                    goblin.state = "walking"

                    self.goblin_popup.show()
                    self.goblin_popup_cooldown = 300

                    if self.player.moving:
                        walking_on_grass_sound.fadeout(300)


                    circular = goblin.get_tree_circular_avoidance(
                        goblin_center, direction, trunks
                    )
                    flee_dir = (direction + circular * 2).normalize()

                    goblin.direction = flee_dir
                    goblin.velocity = flee_dir * goblin.speed

                    break


        # Move toward target
        to_target = goblin.flee_target - goblin_center
        if to_target.length_squared() > 25:
            flee_dir = to_target.normalize()
            circular = goblin.get_tree_circular_avoidance(
                goblin_center, flee_dir, self.tree_spawner.get_trunk_hitboxes()
            )
            final_dir = (flee_dir + circular * 1).normalize()

            goblin.velocity = final_dir * goblin.speed
            goblin.rect.x += int(goblin.velocity.x)
            goblin.rect.y += int(goblin.velocity.y)
            goblin.direction = final_dir
        else:
            # Goblin has arrived
            if goblin.has_stolen_book:
                self.books.add(Book(pos=(int(goblin.rect.centerx), int(goblin.rect.centery))))

            goblin.fleeing = False
            goblin.state = "idle"
            goblin.velocity = pygame.Vector2(0, 0)
            goblin.flee_target = None
            goblin.has_stolen_book = False
    

    def draw_book_counter(self):
        book_spacing = 29
        max_stack = 12
        total_books = max_stack
        collected = self.player.collected_books

        tray_img = book_tray_image
        book_img = closed_book_image

        tray_width = tray_img.get_width()
        tray_height = tray_img.get_height()
        tray_x = (SCREEN_WIDTH - tray_width) // 2
        tray_y = -100

        screen.blit(tray_img, (tray_x, tray_y))
        book_y_offset = (tray_height - book_img.get_height()) // 2

        for i in range(total_books):
            x = tray_x + tray_width - 95 - (i + 1) * book_spacing
            y = tray_y + book_y_offset

            if i < collected:
                # Normal book
                screen.blit(book_img, (x, y))
            else:
                # Transparent (ghost) book
                ghost = book_img.copy()
                ghost.set_alpha(60)  # Adjust transparency as needed
                screen.blit(ghost, (x, y))


    def get_draw_position(self, world_x, image_width, flip=False):
        if not flip:
            return world_x - self.camera_x
        flipped_cam_x = self.map_width - self.camera_x - SCREEN_WIDTH
        return SCREEN_WIDTH - (world_x - flipped_cam_x + image_width)

    def draw_wizard_dialogue(self):
        if not self.dialogue_visible:
            return

        lines = [
            "Seek out the 12 lost books...",
            "Bring them back to me,",
            "and the magic book shall be yours."
        ]

        font = pygame.font.SysFont("georgia", 20, bold=True)
        rendered_lines = [font.render(line, True, (255, 228, 180)) for line in lines]

        line_height = rendered_lines[0].get_height()
        total_height = line_height * len(lines)
        width = max(line.get_width() for line in rendered_lines)

        padding = 10
        bg_rect = pygame.Rect(0, 0, width + padding * 2, total_height + padding * 2)

        # Position above wizard
        screen_x = self.sadogandul.position.x - self.camera_x
        screen_y = self.sadogandul.position.y - self.camera_y - 80
        bg_rect.center = (screen_x, screen_y)

        # Colors matching the sprite style
        bg_color = (70, 40, 20)
        border_color = (200, 120, 60)

        # Shadow
        shadow_rect = bg_rect.copy().move(3, 3)
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=8)

        # Box
        pygame.draw.rect(screen, bg_color, bg_rect, border_radius=8)
        pygame.draw.rect(screen, border_color, bg_rect, width=2, border_radius=8)

        # Draw text lines
        for i, line_surf in enumerate(rendered_lines):
            line_pos = (
                bg_rect.left + (bg_rect.width - line_surf.get_width()) // 2,
                bg_rect.top + padding + i * line_height
            )
            screen.blit(line_surf, line_pos)

