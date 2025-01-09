import pygame
import sys
import os
import pytmx
import math
import random
from pytmx import *

#remember that everything that is rendered has to be a pyobject

# Initialize pygame and set up screen
pygame.init()
screen_width, screen_height = 800, 800
screenrect = pygame.Rect(0, 0, screen_width, screen_height)
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("PYEngine")

# Set up directories and clock
script_dir = os.path.dirname(os.path.abspath(__file__))
clock = pygame.time.Clock()
FPS = 60
gamerunning = True
debug = False

# Key states and key constants
key_states = {}
keysa = [getattr(pygame, attr) for attr in dir(pygame) if attr.startswith('K_') and isinstance(getattr(pygame, attr), int)]

def draw_hero_life_bar(screen, hero):
    life_ratio = hero.life / hero.max_life
    bar_width = 200
    bar_height = 20
    bar_color = (0, 255, 0)
    pygame.draw.rect(screen, bar_color, (10, 10, bar_width * life_ratio, bar_height))
    life_text = font.render(f"{hero.life}/{hero.max_life}", True, "black")
    screen.blit(life_text, (10 + bar_width / 2 - life_text.get_width() / 2, 10 + bar_height / 2 - life_text.get_height() / 2))

def debuging():
    explosion.pos = mouse_pos
    if key_is_triggered(pygame.MOUSEMOTION):
        enemy = Enemy(pos=mouse_pos, size=(64, 64), sprites=spr_monster1, life=1, damage=10, speed=2, target=hero.pos)
    for objects in PyObject.all:
        temp_surface = pygame.Surface((objects.size), pygame.SRCALPHA)
        temp_surface.fill((0, 0, 255, 128))
        screen.blit(temp_surface, objects.rect[:2])

def update_key_states():
    keys = pygame.key.get_pressed()
    for key in keysa:
        if keys[key]:
            if key not in key_states or key_states[key]['state'] == 0:
                key_states[key] = {'state': 1, 'count': 1}
            else:
                key_states[key]['count'] += 1
        else:
            if key in key_states and key_states[key]['state'] == 1:
                key_states[key] = {'state': 0, 'count': 0}
            elif key in key_states:
                key_states[key]['count'] -= 1

def key_is_triggered(key):
    return key_states.get(key, {}).get('state') == 1 and key_states[key]['count'] == 1

def key_is_pressed(key):
    return key_states.get(key, {}).get('state') == 1

def key_is_dropped(key):
    return key_states.get(key, {}).get('state') == 0 and key_states[key]['count'] == 0

def key_is_released(key):
    return key_states.get(key, {}).get('state') == 0

def key_get_time(key):
    return key_states.get(key, {}).get('count', 0)

def spritesheet(image_file, rect=0, rows=1, cols=1):
    image_path = os.path.join(script_dir, image_file)
    sprite_sheet = pygame.image.load(image_path).convert_alpha()
    if rect == 0:
        rect = (0, 0, sprite_sheet.get_width(), sprite_sheet.get_height())
    sprite_width, sprite_height = rect[2] // cols, rect[3] // rows
    return [sprite_sheet.subsurface(pygame.Rect(rect[0] + col * sprite_width, rect[1] + row * sprite_height, sprite_width, sprite_height))
            for row in range(rows) for col in range(cols)]

class PyObject:
    all = []
    def __init__(self, pos, size, sprites=None, animfps=60):
        self.pos = pygame.Vector2(pos)
        self.size = pygame.Vector2(size)
        self.original_size = pygame.Vector2(size)
        self.rect = pygame.Rect(self.pos, self.size)
        self.sprites = sprites if isinstance(sprites, list) else [sprites]
        self.animfps = animfps
        self.sprite_index = 0
        self.frame_count = 0
        self.animation_speed = 60 // animfps
        self.current_sprite = self.sprites[self.sprite_index] if sprites else None
        self.rotation_angle = 0
        PyObject.all.append(self)

    @property
    def center(self):
        return self.rect.center

    def set_animfps(self, fps):
        self.animfps = fps
        self.animation_speed = 60 // fps
    
    def set_sprites(self, new_sprites, animfps=None):
        self.sprites = new_sprites if isinstance(new_sprites, list) else [new_sprites]
        self.sprite_index = 0
        self.frame_count = 0
        self.current_sprite = self.sprites[self.sprite_index]
        if animfps:
            self.set_animfps(animfps)

    def move(self, angle, speed):
        angle_rad = math.radians(angle - 90)
        delta_x = math.cos(angle_rad) * speed
        delta_y = math.sin(angle_rad) * speed
        self.pos.x += delta_x
        self.pos.y += delta_y

    def move_to(self, target_pos, speed):
        target_pos = pygame.Vector2(target_pos)
        direction = target_pos - self.pos
        distance = direction.length()
        if distance > speed:
            direction = direction.normalize()
            self.pos += direction * speed

    def update(self):
        if self.sprites:
            self.frame_count = (self.frame_count + 1) % self.animation_speed
            if self.frame_count == 0:
                self.sprite_index = (self.sprite_index + 1) % len(self.sprites)
                self.current_sprite = self.sprites[self.sprite_index]

    def rotate(self, angle):
        self.rotation_angle = (self.rotation_angle + angle) % 360

    def look_at(self, target, offset=0):
        if not isinstance(target, pygame.Vector2):
            target = pygame.Vector2(target)
        direction = target - self.pos - self.size / 2
        self.rotation_angle = direction.angle_to(pygame.Vector2(1, 0)) + offset

    def draw(self, screen, camera_pos, camera_zoom):
        transformed_pos = (self.pos - camera_pos) * camera_zoom
        transformed_size = self.size * camera_zoom
        self.rect = pygame.Rect(transformed_pos, transformed_size)
        intersection_rect = self.rect.clip(screenrect)
        if self.current_sprite and intersection_rect.width > 0 and intersection_rect.height > 0:
            if isinstance(self.current_sprite, list):
                self.current_sprite = self.current_sprite[0]
            sprite_clip = pygame.Rect(
                max(0, (intersection_rect.x - transformed_pos.x) / transformed_size.x * self.current_sprite.get_width()),
                max(0, (intersection_rect.y - transformed_pos.y) / transformed_size.y * self.current_sprite.get_height()),
                min(self.current_sprite.get_width(), intersection_rect.width / transformed_size.x * self.current_sprite.get_width()),
                min(self.current_sprite.get_height(), intersection_rect.height / transformed_size.y * self.current_sprite.get_height())
            )
            if sprite_clip.width > 0 and sprite_clip.height > 0:
                sprite_clip.width = min(sprite_clip.width, self.current_sprite.get_width() - sprite_clip.x)
                sprite_clip.height = min(sprite_clip.height, self.current_sprite.get_height() - sprite_clip.y)
                scaled_sprite_clip = pygame.transform.scale(
                    self.current_sprite.subsurface(sprite_clip),
                    (intersection_rect.width, intersection_rect.height)
                )
                if self.rotation_angle != 0:
                    scaled_sprite_clip = pygame.transform.rotate(scaled_sprite_clip, +self.rotation_angle)
                    blit_pos = scaled_sprite_clip.get_rect(center=self.rect.center)
                else:
                    blit_pos = intersection_rect.topleft
                screen.blit(scaled_sprite_clip, blit_pos)
        self.draw_life_bar(screen)

    def draw_life_bar(self, screen):
        if hasattr(self, 'life'):
            life_ratio = self.life / self.max_life
            bar_width = self.rect.width
            bar_height = 5
            bar_color = (0, 255, 0)
            pygame.draw.rect(screen, bar_color, (self.rect.left, self.rect.top - bar_height - 2, bar_width * life_ratio, bar_height))
            border_color = (255, 0, 0)
            pygame.draw.rect(screen, border_color, (self.rect.left, self.rect.top - bar_height - 2, bar_width, bar_height), 1)

class LifeBar(PyObject):
    def __init__(self, parent, offset=(0, -10), size=(50, 5)):
        super().__init__(pos=parent.pos + pygame.Vector2(offset), size=size)
        self.parent = parent
        self.offset = pygame.Vector2(offset)
        self.max_life = parent.max_life
        self.life = parent.life

    def update(self):
        self.pos = self.parent.pos + self.offset
        self.life = self.parent.life
        super().update()

    def draw(self, screen, camera_pos, camera_zoom):
        life_ratio = self.life / self.max_life
        bar_width = self.size.x * life_ratio
        bar_height = self.size.y
        bar_color = (0, 255, 0)
        border_color = (255, 0, 0)
        pygame.draw.rect(screen, bar_color, (self.pos.x - camera_pos.x, self.pos.y - camera_pos.y, bar_width * camera_zoom, bar_height * camera_zoom))
        pygame.draw.rect(screen, border_color, (self.pos.x - camera_pos.x, self.pos.y - camera_pos.y, self.size.x * camera_zoom, bar_height * camera_zoom), 1)

class Enemy(PyObject):
    all = []
    def __init__(self, pos, size, sprites, life, damage, speed, target):
        super().__init__(pos, size, sprites)
        self.life = life
        self.max_life = life
        self.damage = damage
        self.speed = speed
        self.target = target
        self.life_bar = LifeBar(self)
        Enemy.all.append(self)

    def update(self):
        self.move_to(self.target, self.speed)
        super().update()
        self.rect.topleft = self.pos.x, self.pos.y
        self.life_bar.update()

    def draw(self, screen, camera_pos, camera_zoom):
        super().draw(screen, camera_pos, camera_zoom)
        self.life_bar.draw(screen, camera_pos, camera_zoom)

    def take_damage(self, amount):
        self.life -= amount
        if self.life <= 0:
            self.die()

    def die(self):
        if self in PyObject.all:
            PyObject.all.remove(self)
        if self in Enemy.all:
            Enemy.all.remove(self)
        if self.life_bar in PyObject.all:
            PyObject.all.remove(self.life_bar)

class FastEnemy(Enemy):
    spawn_rate = 100  # Specific spawn rate for FastEnemy

    def __init__(self, pos, size, sprites, life, damage, speed, target):
        super().__init__(pos, size, sprites, life, damage, speed, target)
        self.speed *= 2  # Fast enemies move twice as fast

class StrongEnemy(Enemy):
    spawn_rate = 200  # Specific spawn rate for StrongEnemy

    def __init__(self, pos, size, sprites, life, damage, speed, target):
        super().__init__(pos, size, sprites, life, damage, speed, target)
        self.life *= 3  # Strong enemies have three times the life

class Missile(PyObject):
    all = []
    launch_interval_frames = 30
    launch_counter = 0
    launch_rate = 30  # Default launch rate for Missile

    def __init__(self, pos, size, sprites, target, speed=1, damage=10):
        super().__init__(pos, size, sprites)
        self.target = target
        self.speed = speed
        self.damage = damage  # Add damage attribute
        self.direction = (pygame.Vector2(target) - pygame.Vector2(pos)).normalize()
        self.rotation_angle = 90  # Rotate the base sprite by 90 degrees
        self.look_at(target)  # Make the missile look towards its target
        Missile.all.append(self)

    # Remove automatic missile launching
    # @classmethod
    # def try_launch_missile(cls, pos, size, sprites):
    #     cls.launch_counter += 1
    #     if cls.launch_counter >= cls.launch_rate:
    #         cls.launch_counter = 0
    #         closest_enemy = cls.find_closest_enemy(hero.pos)
    #         if closest_enemy:
    #             rocket = cls(pos, size, sprites, closest_enemy.pos)
    #     return None

    @staticmethod
    def find_closest_enemy(hero_pos):
        closest_enemy = None
        min_distance = float('inf')
        for obj in PyObject.all:
            if isinstance(obj, Enemy):
                distance = hero_pos.distance_to(obj.pos)
                if distance < min_distance:
                    min_distance = distance
                    closest_enemy = obj
        return closest_enemy
 
    def update(self):
        self.pos += self.direction * self.speed
        super().update()
        self.check_collision()
        self.check_out_of_bounds()

    def draw(self, screen, camera_pos, camera_zoom):
        super().draw(screen, camera_pos, camera_zoom)

    def check_collision(self):
        for enemy in PyObject.all:
            if isinstance(enemy, Enemy) and self.rect.colliderect(enemy.rect):
                self.on_collision(enemy)

    def on_collision(self, enemy):
        enemy.die()
        if self in PyObject.all : PyObject.all.remove(self)

    def check_out_of_bounds(self):
        if (self.pos.x < camera_pos.x - 100 or self.pos.x > camera_pos.x + screen_width + 100 or
                self.pos.y < camera_pos.y - 100 or self.pos.y > camera_pos.y + screen_height + 100):
            if self in PyObject.all : PyObject.all.remove(self)

    def look_at(self, target, offset=0):
        if not isinstance(target, pygame.Vector2):
            target = pygame.Vector2(target)
        direction = target - self.pos - self.size / 2
        self.rotation_angle = direction.angle_to(pygame.Vector2(1, 0)) + offset

class HomingMissile(Missile):
    spawn_rate = 150  # Specific spawn rate for HomingMissile
    launch_rate = 60  # Specific launch rate for HomingMissile

    def __init__(self, pos, size, sprites, target, speed=1, damage=10):
        super().__init__(pos, size, sprites, target, speed, damage)
        self.homing_speed = speed / 2  # Homing missiles move slower but adjust direction

    def update(self):
        self.direction = (pygame.Vector2(self.target) - self.pos).normalize()
        self.pos += self.direction * self.homing_speed
        super().update()

class ExplosiveMissile(Missile):
    spawn_rate = 150  # Specific spawn rate for ExplosiveMissile
    launch_rate = 90  # Specific launch rate for ExplosiveMissile

    def __init__(self, pos, size, sprites, target, speed=1, damage=10):
        super().__init__(pos, size, sprites, target, speed, damage)
        self.explosion_radius = 50  # Explosive missiles have an explosion radius

    def on_collision(self, enemy):
        for obj in PyObject.all:
            if isinstance(obj, Enemy) and self.pos.distance_to(obj.pos) <= self.explosion_radius:
                obj.take_damage(self.damage)
                newexp = Explosion(pos=self.pos, size=(self.explosion_radius, self.explosion_radius), sprite=spr_explosion, duration=10)
            if self in PyObject.all : PyObject.all.remove(self)

class Explosion(PyObject):
    def __init__(self, pos, size, sprite, duration):
        super().__init__(pos, size, [sprite])
        self.duration = duration
        self.timer = 0

    def update(self):
        self.timer += 1
        if self.timer > self.duration:
            PyObject.all.remove(self)

class Gun(PyObject):
    all = []
    def __init__(self, parent, offset, missile_speed, missile_size, missile_sprites, fire_rate):
        super().__init__(pos=parent.pos + offset, size=(43*3, 26*3), sprites=spr_gun1)
        self.parent = parent
        self.offset = pygame.Vector2(offset)
        self.missile_speed = missile_speed
        self.missile_size = missile_size
        self.missile_sprites = missile_sprites
        self.fire_rate = fire_rate
        self.fire_counter = 0
        Gun.all.append(self)

    def update(self):
        self.pos = self.parent.pos + self.offset.rotate(self.parent.rotation_angle)
        self.look_at_closest_enemy()
        self.fire_counter += 1
        if self.fire_counter >= self.fire_rate:
            self.fire_counter = 0
            self.shoot()
        super().update()
        self.rotate(180)

    def look_at_closest_enemy(self):
        closest_enemy = Missile.find_closest_enemy(self.pos)
        if closest_enemy:
            self.look_at(closest_enemy.pos)

    def shoot(self):
        closest_enemy = Missile.find_closest_enemy(self.pos)
        if closest_enemy:
            direction = (closest_enemy.pos - self.pos).normalize()
            missile = Missile(self.pos, self.missile_size, self.missile_sprites, closest_enemy.pos, self.missile_speed)
            missile.direction = direction

    def draw(self, screen, camera_pos, camera_zoom):
        super().draw(screen, camera_pos, camera_zoom)

def grid(grid_rect, rows=1, cols=1, h_offset=0, v_offset=0):
    cell_width = (grid_rect.width - (cols - 1) * h_offset) / cols
    cell_height = (grid_rect.height - (rows - 1) * v_offset) / rows
    grid_list = []
    for row in range(rows):
        for col in range(cols):
            x = grid_rect.x + col * (cell_width + h_offset)
            y = grid_rect.y + row * (cell_height + v_offset)
            pos = (x, y)
            size = (cell_width, cell_height)
            grid_list.append([pos, size])
    return grid_list

def load_tiles_from_tmx(tmx_file):
    tmx_data = tmx_file
    py_objects = []
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile_image = tmx_data.get_tile_image_by_gid(gid)
                if tile_image:
                    tile_width = tmx_data.tilewidth
                    tile_height = tmx_data.tileheight
                    pos = (x * tile_width, y * tile_height)
                    size = (tile_width + 1, tile_height + 1)
                    adjusted_pos = (round(pos[0]), round(pos[1]))
                    sprites = [tile_image]
                    py_object = PyObject(pos=adjusted_pos, size=size, sprites=sprites, animfps=FPS)
                    py_objects.append(py_object)
    return py_objects

def create_giant_sprite(tmx_data):
    map_width = tmx_data.width * tmx_data.tilewidth
    map_height = tmx_data.height * tmx_data.tileheight
    giant_sprite = pygame.Surface((map_width, map_height), pygame.SRCALPHA)
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile_image = tmx_data.get_tile_image_by_gid(gid)
                if tile_image:
                    tile_pos = (x * tmx_data.tilewidth, y * tmx_data.tileheight)
                    giant_sprite.blit(tile_image, tile_pos)
    map_pyobject = PyObject(pos=(0, 0), size=giant_sprite.get_size(), sprites=[giant_sprite])

def spawn_enemy_outside_screen(interval_frames, enemy_sprites, enemy_size, target, speed, life=100, damage=10):
    spawn_enemy_outside_screen.counter += 1
    if spawn_enemy_outside_screen.counter >= interval_frames:
        spawn_enemy_outside_screen.counter = 0
        screen_margin = 50
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            pos = pygame.Vector2(random.uniform(-screen_margin, screen_width + screen_margin), -screen_margin)
        elif side == 'bottom':
            pos = pygame.Vector2(random.uniform(-screen_margin, screen_width + screen_margin), screen_height + screen_margin)
        elif side == 'left':
            pos = pygame.Vector2(-screen_margin, random.uniform(-screen_margin, screen_height + screen_margin))
        elif side == 'right':
            pos = pygame.Vector2(screen_width + screen_margin, random.uniform(-screen_margin, screen_height + screen_margin))
        new_enemy = Enemy(pos=pos, size=enemy_size, sprites=enemy_sprites, life=life, damage=damage, speed=speed, target=target)
        PyObject.all.append(new_enemy)

spawn_enemy_outside_screen.counter = 0

def spawn_specific_enemy(enemy_class, enemy_sprites, enemy_size, target, speed, life=100, damage=10):
    if random.randint(1, enemy_class.spawn_rate) == 1:
        screen_margin = 50
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            pos = pygame.Vector2(random.uniform(-screen_margin, screen_width + screen_margin), -screen_margin)
        elif side == 'bottom':
            pos = pygame.Vector2(random.uniform(-screen_margin, screen_width + screen_margin), screen_height + screen_margin)
        elif side == 'left':
            pos = pygame.Vector2(-screen_margin, random.uniform(-screen_margin, screen_height + screen_margin))
        elif side == 'right':
            pos = pygame.Vector2(screen_width + screen_margin, random.uniform(-screen_margin, screen_height + screen_margin))
        new_enemy = enemy_class(pos=pos, size=enemy_size, sprites=enemy_sprites, life=life, damage=damage, speed=speed, target=target)
        PyObject.all.append(new_enemy)

class Sword(PyObject):
    def __init__(self, parent, sprites, offset=(50, 0)):
        super().__init__(pos=parent.pos + pygame.Vector2(offset), size=parent.size, sprites=sprites)
        self.parent = parent
        self.offset = pygame.Vector2(offset)
        self.is_attacking = False

    def attack(self):
        self.is_attacking = True
        self.set_sprites(spr_zelda_sword, 5)
        self.sprite_index = 0
        self.frame_count = 0

    def update(self):
        self.pos = self.parent.pos + self.offset.rotate(self.parent.rotation_angle)
        if self.is_attacking:
            self.frame_count = (self.frame_count + 1) % self.animation_speed
            if self.frame_count == 0:
                self.sprite_index += 1
                if self.sprite_index >= len(self.sprites):
                    self.sprite_index = 0
                    self.is_attacking = False
                self.current_sprite = self.sprites[self.sprite_index]
        super().update()

    def draw(self, screen, camera_pos, camera_zoom):
        super().draw(screen, camera_pos, camera_zoom)

def check_button_press():
    return pygame.key.get_pressed(), pygame.mouse.get_pressed()

def move_pyobject(obj, keys, speed=10):
    if keys[pygame.K_LEFT]:
        obj.move(270, speed)
    if keys[pygame.K_RIGHT]:
        obj.move(90, speed)
    if keys[pygame.K_UP]:
        obj.move(0, speed)
    if keys[pygame.K_DOWN]:
        obj.move(180, speed)
    if key_is_triggered(pygame.K_LEFT):
        obj.set_sprites(sprites[8:12])
    if key_is_triggered(pygame.K_RIGHT):
        obj.set_sprites(sprites[12:16])
    if key_is_triggered(pygame.K_UP):
        obj.set_sprites(sprites[4:8])
    if key_is_triggered(pygame.K_DOWN):
        obj.set_sprites(sprites[0:4])
 
camera_pos, camera_zoom = pygame.Vector2(0, 0), 1.0
sprites = spritesheet('walking.png', (0, 0, 1600, 2397), 4, 4)
spr_hero = spritesheet('walking_mini.png', (0, 0, 64, 96), 4, 4)
spr_zelda_sword = spritesheet('zelda.png', (112, 268, 75, 17), 1, 5)
spr_monster1 = spritesheet('plants.png', (1045, 455, 347, 316))
spr_monster2 = spritesheet('plants.png', (2429, 749, 288, 421))
spr_monster3 = spritesheet('plants.png', (2049, 825, 317, 348))
spr_village = spritesheet('village.png', (0, 0, 1600, 1600))
spr_rocket = spritesheet('guns.png', (951, 811, 39, 10))
spr_rocket2 = spritesheet('missiles.png', (98, 38, 78, 350))
spr_rocket3 = spritesheet('missiles.png', (190, 63, 36, 115))
spr_explosion = spritesheet('exp.png', 0, 2, 5)
spr_gun1 = spritesheet('guns.png', (561, 893, 43, 26))

rect2 = PyObject((200, 300), (100, 100), sprites=spr_hero[4:8], animfps=4)
rect3 = PyObject((400, 100), (100, 100), sprites=spr_hero[8:12], animfps=4)
rect4 = PyObject((200, 100), (100, 100), sprites=spr_hero[12:16], animfps=4)
hero = PyObject((400, 300), (100, 100), sprites=spr_hero[0:4], animfps=4)
hero.life = 100
hero.max_life = 100
enemy = Enemy(pos=(100, 100), size=(64, 64), sprites=spr_monster1, life=1, damage=10, speed=2, target=hero.pos)
rocket = Missile(hero.pos, (39, 10), spr_rocket, enemy.pos)
rocket.rotate(90)
explosion = PyObject((200, 300), (100, 100), sprites=spr_explosion[0:10], animfps=10)
sword = Sword(hero, spr_zelda_sword[0], offset=(50, 0))

fast_enemy = FastEnemy(pos=(150, 150), size=(64, 64), sprites=spr_monster3, life=1, damage=10, speed=2, target=hero.pos)
strong_enemy = StrongEnemy(pos=(200, 200), size=(64, 64), sprites=spr_monster2, life=1, damage=10, speed=2, target=hero.pos)
homing_missile = HomingMissile(hero.pos, (39, 10), spr_rocket2, enemy.pos, damage=10)
explosive_missile = ExplosiveMissile(hero.pos, (39, 10), spr_rocket3, enemy.pos, damage=10)
homing_missile.rotate(90)
explosive_missile.rotate(90)

guns = [
    Gun(hero, offset=(50, 0), missile_speed=10, missile_size=(39, 10), missile_sprites=spr_rocket, fire_rate=30),
    Gun(hero, offset=(-50, 0), missile_speed=10, missile_size=(39, 10), missile_sprites=spr_rocket, fire_rate=30),
    Gun(hero, offset=(0, 50), missile_speed=10, missile_size=(39, 10), missile_sprites=spr_rocket, fire_rate=30),
    Gun(hero, offset=(0, -50), missile_speed=10, missile_size=(39, 10), missile_sprites=spr_rocket, fire_rate=30)
]

font = pygame.font.SysFont(None, 36)
dragging = False
rect2.rotate(90)

while gamerunning:
    if key_is_triggered(pygame.K_F1):
        debug = not debug
    update_key_states()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
            dragging = True
            drag_start = pygame.Vector2(event.pos)
            camera_start = camera_pos.copy()
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 2:
            dragging = False
        elif event.type == pygame.MOUSEWHEEL:
            camera_zoom *= 1.1 if event.y > 0 else 0.9
        elif event.type == pygame.MOUSEMOTION and dragging:
            camera_pos = camera_start + (drag_start - pygame.Vector2(event.pos)) / camera_zoom
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                sword.attack()

    keys, _ = check_button_press()
    move_pyobject(hero, keys)

    mouse_pos = pygame.Vector2(pygame.mouse.get_pos()) / camera_zoom + camera_pos
    rect2.look_at(mouse_pos, -90)
    rect3.move_to(hero.pos, 5)
    camera_pos = hero.pos - pygame.Vector2(screen.get_size()) / 2 / camera_zoom

    # Remove automatic missile launching
    # new_missile = Missile.try_launch_missile(hero.pos, (64, 64), spr_rocket)
    # HomingMissile.try_launch_missile(hero.pos, (39, 10), spr_rocket2)
    # ExplosiveMissile.try_launch_missile(hero.pos, (39, 10), spr_rocket3)
    spawn_enemy_outside_screen(
        interval_frames=120,
        enemy_sprites=spr_monster1,
        enemy_size=(64, 64),
        target=hero.pos,
        speed=2,
        life=100,
        damage=10
    )

    spawn_specific_enemy(FastEnemy, spr_monster3, (64, 64), hero.pos, 2, life=100, damage=10)
    spawn_specific_enemy(StrongEnemy, spr_monster2, (64, 64), hero.pos, 2, life=100, damage=10)


    screen.fill("black")
    for obj in PyObject.all:
        obj.update()
        obj.draw(screen, camera_pos, camera_zoom)

    sword.update()
    sword.draw(screen, camera_pos, camera_zoom)

    for gun in Gun.all:
        gun.update()
        gun.draw(screen, camera_pos, camera_zoom)

    draw_hero_life_bar(screen, hero)
    
    fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, "white")
    screen.blit(fps_text, (10, 10))
    if debug: debuging()
    
    pygame.display.flip()
    clock.tick(FPS)
