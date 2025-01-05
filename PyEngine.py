import pygame,sys,os,pytmx,math, random
from pytmx import *
#from ..Entrainements.gridtmx import *
 
entrainementfolder = "Entrainements"
 
pygame.init()
screen_width,screen_height = 800,800
screenrect = pygame.Rect(0,0,screen_width,screen_height)
#screenrect = pygame.Rect(0,0,400,400)
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("PYEngine")

script_dir = os.path.dirname(os.path.abspath(__file__))

#tmxmap = load_pygame(f"{script_dir}/basic.tmx")
#for layer in tmxmap.visible_layers:
#    print(layer.name, type(layer))

clock = pygame.time.Clock()
FPS = 60
gamerunning = True
debug = False
#                                       keys 
key_states = {}

keysa = [getattr(pygame, attr) for attr in dir(pygame) if attr.startswith('K_') and isinstance(getattr(pygame, attr), int)]

def debuging():
    explosion.pos = mouse_pos
    if key_is_triggered(pygame.MOUSEMOTION): enemy = Enemy(pos=mouse_pos, size=(64, 64), sprites=spr_monster1, life=1, damage=10, speed=2, target=hero.pos)

    for objects in PyObject.all:
        temp_surface = pygame.Surface((objects.size), pygame.SRCALPHA)
        temp_surface.fill((0, 0, 255, 128))  # RGB + Alpha

        # Blit the transparent square onto the main surface
        screen.blit(temp_surface, objects.rect[:2])
        #pygame.draw.rect(screen,"blue",objects.rect)#pygame.draw.rect(screen, "BLUE", objects.rect)

def update_key_states():
    keys = pygame.key.get_pressed()
    
    # Iterate over all possible key constants
    for key in keysa:
        if keys[key]:  # Key is currently pressed
            if key not in key_states or key_states[key]['state'] == 0:  # Triggered
                key_states[key] = {'state': 1, 'count': 1}
            else:
                key_states[key]['count'] += 1
        else:  # Key is not pressed
            if key in key_states and key_states[key]['state'] == 1:  # Dropped
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
#                                       spritesheets
def spritesheet(image_file, rect = 0, rows=1, cols=1):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, image_file)
    sprite_sheet = pygame.image.load(image_path).convert_alpha()
    if rect == 0 : rect = (0,0,sprite_sheet.get_width(),sprite_sheet.get_height())
    sprite_width, sprite_height = rect[2] // cols, rect[3] // rows
    return [sprite_sheet.subsurface(pygame.Rect(rect[0] + col * sprite_width, rect[1] + row * sprite_height, sprite_width, sprite_height))
            for row in range(rows) for col in range(cols)]
#                                       pyobject
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
        self.rotation_angle = 0  # Initialize rotation angle
        PyObject.all.append(self)

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
        # Convert angle to radians
        angle_rad = math.radians(angle-90)
        
        # Calculate the change in x and y using trigonometry
        delta_x = math.cos(angle_rad) * speed
        delta_y = math.sin(angle_rad) * speed
        
        # Update the position of the object
        self.pos.x += delta_x
        self.pos.y += delta_y

        # Update the rect position to match the new position
        #self.rect.topleft = self.pos

    def move_to(self, target_pos, speed):
        # Ensure the target position is a pygame.Vector2
        #if not isinstance(target_pos, pygame.Vector2):
        target_pos = pygame.Vector2(target_pos)
        
        # Calculate the direction vector towards the target
        direction = target_pos - self.pos
        distance = direction.length()
        
        # If the distance is greater than the speed, move towards the target
        if distance > speed:
            direction = direction.normalize()  # Get the unit vector
            self.pos += direction * speed
        
        # Update the rect position to match the new position
        #self.rect.topleft = self.pos

    def update(self):
        if self.sprites:
            self.frame_count = (self.frame_count + 1) % self.animation_speed
            if self.frame_count == 0:
                self.sprite_index = (self.sprite_index + 1) % len(self.sprites)
                self.current_sprite = self.sprites[self.sprite_index]

    def rotate(self, angle):
        self.rotation_angle = (self.rotation_angle + angle) % 360  # Update rotation angle (clockwise rotation)

    def look_at(self, target, offset=0):
        if not isinstance(target, pygame.Vector2):
            target = pygame.Vector2(target)
        direction = target - self.pos - self.size/2
        self.rotation_angle = direction.angle_to(pygame.Vector2(1, 0)) + offset

    def draw(self, screen, camera_pos, camera_zoom):
        transformed_pos = (self.pos - camera_pos) * camera_zoom
        transformed_size = self.size * camera_zoom
        self.rect = pygame.Rect(transformed_pos, transformed_size)
        #self.rect.topleft = self.pos
        # Calculate the intersection between the object's rect and the viewport
        intersection_rect = self.rect.clip(screenrect)

        if self.current_sprite and intersection_rect.width > 0 and intersection_rect.height > 0:
            # Determine the part of the sprite that should be visible based on the intersection
            sprite_clip = pygame.Rect(
                max(0, (intersection_rect.x - transformed_pos.x) / transformed_size.x * self.current_sprite.get_width()),
                max(0, (intersection_rect.y - transformed_pos.y) / transformed_size.y * self.current_sprite.get_height()),
                min(self.current_sprite.get_width(), intersection_rect.width / transformed_size.x * self.current_sprite.get_width()),
                min(self.current_sprite.get_height(), intersection_rect.height / transformed_size.y * self.current_sprite.get_height())
            )

            # Ensure the sprite_clip rectangle is within the bounds of the sprite
            if sprite_clip.width > 0 and sprite_clip.height > 0:
                sprite_clip.width = min(sprite_clip.width, self.current_sprite.get_width() - sprite_clip.x)
                sprite_clip.height = min(sprite_clip.height, self.current_sprite.get_height() - sprite_clip.y)
                # Scale the sprite clip to the size of the intersection
                scaled_sprite_clip = pygame.transform.scale(
                    self.current_sprite.subsurface(sprite_clip),
                    (intersection_rect.width, intersection_rect.height)
                )
                
                # Calculate the position for blitting the clipped sprite
                if self.rotation_angle!=0:
                    scaled_sprite_clip = pygame.transform.rotate(scaled_sprite_clip, +self.rotation_angle)  # Rotate in the correct direction
                    blit_pos = scaled_sprite_clip.get_rect(center=self.rect.center)
                else:
                    blit_pos = intersection_rect.topleft

                screen.blit(scaled_sprite_clip, blit_pos)
        
class Enemy(PyObject):
    def __init__(self, pos, size, sprites, life, damage, speed, target):
        super().__init__(pos, size, sprites)
        self.life = life
        self.damage = damage
        self.speed = speed
        self.target = target  # The target that the enemy will chase (e.g., the hero)
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])  # Rectangle for collision detection

    def update(self):
        # Move towards the target (hero)
        self.move_to(self.target, self.speed)
        
        # Call the parent class update method to handle animation if needed
        super().update()

        # Update the rect position
        self.rect.topleft = self.pos.x, self.pos.y

    def take_damage(self, amount):
        """Handle taking damage when hit by missiles."""
        self.life -= amount
        if self.life <= 0:
            self.die()

    def die(self):
        """Handle enemy death (e.g., remove from game, play death animation, etc.)"""
        print("Enemy has died!")
        PyObject.all.remove(self)  # Remove from game objects

    def __init__(self, pos, size, sprites, life, damage, speed, target):
        super().__init__(pos, size, sprites)
        self.life = life
        self.damage = damage
        self.speed = speed
        self.target = target  # The target that the enemy will chase (e.g., the hero)

    def update(self):
        # Move towards the target (hero)
        self.move_to(self.target, self.speed)
        
        # Call the parent class update method to handle animation if needed
        super().update()

    def take_damage(self, amount):
        self.life -= amount
        if self.life <= 0:
            self.die()

    def die(self):
        # Handle enemy death (e.g., remove from game, play death animation, etc.)
        print("Enemy has died!")
        PyObject.all.remove(self)

class Missile(PyObject):
    def __init__(self, pos, size, sprite, speed, direction, damage):
        super().__init__(pos, size, [sprite])  # We assume the missile sprite is a single image
        self.speed = 5
        self.direction = direction.normalize()  # Normalize direction for consistent speed
        self.damage = damage
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])  # Collision detection rectangle

    def update(self):
        """Update missile position and check for collisions with enemies."""
        self.pos += self.direction * self.speed
        self.rect.topleft = self.pos.x, self.pos.y  # Update rect position

        # Check for collisions with enemies
        for enemy in Enemy.all:  # Assuming `Enemy.all` is a list of all enemies
            if self.check_collision(enemy):
                self.on_collision(enemy)

        # Call the parent class update method (for animation, etc.)
        super().update()

    def draw(self, screen):
        """Draw the missile on the screen."""
        screen.blit(self.sprite[0], self.pos)

    def check_collision(self, enemy):
        """Check if the missile collides with the enemy."""
        if self.rect.colliderect(enemy.rect):
            return True
        return False

    def on_collision(self, enemy):
        """Handle the missile colliding with an enemy."""
        # Apply damage to the enemy
        enemy.take_damage(self.damage)

        # Trigger explosion or other effects
        self.trigger_explosion()

        # Remove the missile after collision
        PyObject.all.remove(self)

    def trigger_explosion(self):
        """Trigger an explosion effect after the missile hits the enemy."""
        # This is where you would create an explosion object, e.g., an animation or sprite.
        print("Boom! Explosion triggered.")

    all = []
    launch_interval_frames = 30  # Class-level attribute for launch interval (120 frames)
    launch_counter = 0  # Static frame counter to control launches

    def __init__(self, pos, size, sprites, target,speed=1):
        super().__init__(pos, size, sprites)
        self.target = target  # The enemy or object the missile will target
        self.speed = speed
        Missile.all.append(self)

    @classmethod
    def try_launch_missile(cls, pos, size, sprites, target):
        """Launches a missile if enough frames have passed."""
        cls.launch_counter += 1
        if cls.launch_counter >= cls.launch_interval_frames:
            cls.launch_counter = 0  # Reset counter after launching
            rocket = Missile(hero.pos,(39,10),spr_rocket,enemy.pos)
        return None  # No missile launched yet

    def update(self):
        # Move towards the enemy target
        self.move_to(self.target, self.speed)

        # Rotate the missile to face the enemy
        self.look_at(self.target, offset=-180)

        # Call super to handle any inherited behavior
        super().update()

    def draw(self, screen, camera_pos, camera_zoom):
        super().draw(screen, camera_pos, camera_zoom)

class Explosion(PyObject):
    def __init__(self, pos, size, sprite, duration):
        super().__init__(pos, size, [sprite])
        self.duration = duration
        self.timer = 0

    def update(self):
        """Update the explosion (countdown for removal)."""
        self.timer += 1
        if self.timer > self.duration:
            PyObject.all.remove(self)  # Remove the explosion after the duration

    def draw(self, screen):
        """Draw the explosion on the screen."""
        screen.blit(self.sprite[0], self.pos)
#                                       grid
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
            grid_list.append([pos,size])

    return grid_list
#                                       tiles loader
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

                    # Snap position to nearest integer
                    adjusted_pos = (round(pos[0]), round(pos[1]))
                    sprites = [tile_image]  # Assuming each tile has a single sprite

                    # Create the PyObject instance with pos, size, and sprites
                    py_object = PyObject(pos=adjusted_pos, size=size, sprites=sprites, animfps=FPS)
                    py_objects.append(py_object)

    return py_objects

def create_giant_sprite(tmx_data):
    # Calculate the size of the entire map
    map_width = tmx_data.width * tmx_data.tilewidth
    map_height = tmx_data.height * tmx_data.tileheight
    giant_sprite = pygame.Surface((map_width, map_height), pygame.SRCALPHA)

    # Blit each tile onto the giant sprite
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile_image = tmx_data.get_tile_image_by_gid(gid)
                if tile_image:
                    tile_pos = (x * tmx_data.tilewidth, y * tmx_data.tileheight)
                    giant_sprite.blit(tile_image, tile_pos)

    # Create a PyObject with the giant sprite
    map_pyobject = PyObject(pos=(0, 0), size=giant_sprite.get_size(), sprites=[giant_sprite])

    #return map_pyobject

def spawn_enemy_outside_screen(interval_frames, enemy_sprites, enemy_size, target, speed, life=100, damage=10):
    spawn_enemy_outside_screen.counter += 1

    if spawn_enemy_outside_screen.counter >= interval_frames:
        spawn_enemy_outside_screen.counter = 0

        # Determine the spawn location outside the screen
        screen_margin = 50  # Spawn enemies slightly beyond the screen boundary
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            pos = pygame.Vector2(random.uniform(-screen_margin, screen_width + screen_margin), -screen_margin)
        elif side == 'bottom':
            pos = pygame.Vector2(random.uniform(-screen_margin, screen_width + screen_margin), screen_height + screen_margin)
        elif side == 'left':
            pos = pygame.Vector2(-screen_margin, random.uniform(-screen_margin, screen_height + screen_margin))
        elif side == 'right':
            pos = pygame.Vector2(screen_width + screen_margin, random.uniform(-screen_margin, screen_height + screen_margin))

        # Create and add the new enemy to the game
        new_enemy = Enemy(pos=pos, size=enemy_size, sprites=enemy_sprites, life=life, damage=damage, speed=speed, target=target)
        PyObject.all.append(new_enemy)

spawn_enemy_outside_screen.counter = 0

# Example usage:
tmx_file = "your_map.tmx"  # Replace with your TMX file path
#py_objects = create_giant_sprite(tmxmap)

class Sword(PyObject):
    def __init__(self, parent, sprites, offset=(50, 0)):
        super().__init__(pos=parent.pos + pygame.Vector2(offset), size=parent.size, sprites=sprites)
        self.parent = parent  # The object that the sword will follow
        self.offset = pygame.Vector2(offset)
        self.is_attacking = False

    def attack(self):
        self.is_attacking = True
        self.set_sprites(spr_zelda_sword,5)
        self.sprite_index = 0
        self.frame_count = 0

    def update(self):
        # Update the position to follow the parent
        self.pos = self.parent.pos + self.offset.rotate(self.parent.rotation_angle)
        
        # Update the animation if attacking
        if self.is_attacking:
            self.frame_count = (self.frame_count + 1) % self.animation_speed
            if self.frame_count == 0:
                self.sprite_index += 1
                if self.sprite_index >= len(self.sprites):
                    self.sprite_index = 0
                    self.is_attacking = False
                self.current_sprite = self.sprites[self.sprite_index]

        super().update()  # Call the parent class update method to handle animation if needed

    def draw(self, screen, camera_pos, camera_zoom):
        super().draw(screen, camera_pos, camera_zoom)  # Use the draw method from PyObject

def check_button_press():
    return pygame.key.get_pressed(), pygame.mouse.get_pressed()

def move_pyobject(obj, keys, speed=10):
    if keys[pygame.K_LEFT]: 
        obj.move(270,speed)
    if keys[pygame.K_RIGHT]: 
        obj.move(90,speed)
    if keys[pygame.K_UP]: 
        obj.move(0,speed)
    if keys[pygame.K_DOWN]: 
        obj.move(180,speed)
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
spr_zelda_sword = spritesheet('zelda.png', (112, 268, 75, 17), 1, 5)  # Load sword spritesheet
spr_monster1 = spritesheet('plants.png', (1045, 455, 347, 316))
spr_village = spritesheet('village.png', (0,0, 1600, 1600))
spr_rocket = spritesheet('guns.png', (951, 811, 39, 10))
spr_explosion = spritesheet('exp.png', 0,2,5)


#village = PyObject((0, 0), (8000, 8000), sprites=spr_village)
rect2 = PyObject((200, 300), (100, 100), sprites=spr_hero[4:8], animfps=4)
rect3 = PyObject((400, 100), (100, 100), sprites=spr_hero[8:12], animfps=4)
rect4 = PyObject((200, 100), (100, 100), sprites=spr_hero[12:16], animfps=4)
#monster = PyObject((500, 100), (200, 200), sprites=spr_monster1)
hero = PyObject((400, 300), (100, 100), sprites=spr_hero[0:4], animfps=4)
enemy = Enemy(pos=(100, 100), size=(64, 64), sprites=spr_monster1, life=1, damage=10, speed=2, target=hero.pos)
rocket = Missile(hero.pos,(39,10),spr_rocket,enemy.pos)
explosion = PyObject((200, 300), (100, 100), sprites=spr_explosion[0:10], animfps=10)

# Create sword and attach it to rect1
sword = Sword(hero, spr_zelda_sword[0], offset=(50, 0))  # Pass a single sprite

# Create font object
font = pygame.font.SysFont(None, 36)

dragging = False

rect2.rotate(90)

while gamerunning:
    if key_is_triggered(pygame.K_F1): debug = not debug
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
                sword.attack()  # Trigger sword attack animation

    keys, _ = check_button_press()
    move_pyobject(hero, keys)

    # Rotate rect2 to face the mouse
    mouse_pos = pygame.Vector2(pygame.mouse.get_pos()) / camera_zoom + camera_pos
    rect2.look_at(mouse_pos, -90)
    rect3.move_to(hero.pos, 5)

    # Update camera to follow rect1
    camera_pos = hero.pos - pygame.Vector2(screen.get_size()) / 2 / camera_zoom

    new_missile = Missile.try_launch_missile(hero.pos, (64, 64), spr_rocket, enemy.pos)
    spawn_enemy_outside_screen(
    interval_frames=120,          # Spawn an enemy every 120 frames (2 seconds at 60 FPS)
    enemy_sprites=spr_monster1,   # Use the monster sprites
    enemy_size=(64, 64),          # Enemy size
    target=hero.pos,              # Hero's position as the target
    speed=2,                      # Movement speed of the enemy
    life=100,                     # Enemy life
    damage=10                     # Enemy damage
    )


    # Update and draw objects
    screen.fill("black")
    for obj in PyObject.all:
        obj.update()
        obj.draw(screen, camera_pos, camera_zoom)

    # Update and draw the sword
    sword.update()
    sword.draw(screen, camera_pos, camera_zoom)
    #pygame.draw.rect(screen,"blue",hero.rect)
    #print(hero.rect)
    
    # Display FPS
    fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, "white")
    screen.blit(fps_text, (10, 10))
    if debug: debuging()
    
    pygame.display.flip()
    clock.tick(FPS)
