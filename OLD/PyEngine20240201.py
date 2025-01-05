import pygame,sys,os,pytmx
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

tmxmap = load_pygame(f"{script_dir}/basic.tmx")
for layer in tmxmap.visible_layers:
    print(layer.name, type(layer))

clock = pygame.time.Clock()
FPS = 60
gamerunning = True
#                                       keys 
key_states = {}

keysa = [getattr(pygame, attr) for attr in dir(pygame) if attr.startswith('K_') and isinstance(getattr(pygame, attr), int)]

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
def spritesheet(image_file, rect, rows=1, cols=1):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, image_file)
    sprite_sheet = pygame.image.load(image_path).convert_alpha()
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
        
        intersection_rect = self.rect.clip(screenrect)
        if self.current_sprite and intersection_rect.width > 0 and intersection_rect.height > 0:
            sprite_clip = pygame.Rect(
                max(0, (intersection_rect.x - transformed_pos.x) / transformed_size.x * self.current_sprite.get_width()),
                max(0, (intersection_rect.y - transformed_pos.y) / transformed_size.y * self.current_sprite.get_height()),
                min(self.current_sprite.get_width(), intersection_rect.width / transformed_size.x * self.current_sprite.get_width()),
                min(self.current_sprite.get_height(), intersection_rect.height / transformed_size.y * self.current_sprite.get_height())
            )

            if sprite_clip.width > 0 and sprite_clip.height > 0:
                visible_sprite = self.current_sprite.subsurface(sprite_clip)
                scaled_sprite = pygame.transform.scale(visible_sprite, (intersection_rect.width, intersection_rect.height))
                rotated_sprite = pygame.transform.rotate(scaled_sprite, -self.rotation_angle)  # Rotate in the same direction as the second code

                blit_pos = rotated_sprite.get_rect(center=self.rect.center)
                screen.blit(rotated_sprite, blit_pos)


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
                    size = (tile_width, tile_height)
                    sprites = [tile_image]  # Assuming each tile has a single sprite

                    # Create the PyObject instance with pos, size, and sprites
                    py_object = PyObject(pos=pos, size=size, sprites=sprites, animfps=FPS)
                    py_objects.append(py_object)

    return py_objects

# Example usage:
tmx_file = "your_map.tmx"  # Replace with your TMX file path
py_objects = load_tiles_from_tmx(tmxmap)

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
        obj.pos.x -= speed
    if keys[pygame.K_RIGHT]: 
        obj.pos.x += speed
    if keys[pygame.K_UP]: 
        obj.pos.y -= speed
    if keys[pygame.K_DOWN]: 
        obj.pos.y += speed
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
monster1 = spritesheet('plants.png', (1045, 455, 347, 316))
spr_village = spritesheet('village.png', (0,0, 1600, 1600))


#village = PyObject((0, 0), (8000, 8000), sprites=spr_village)
rect2 = PyObject((200, 300), (100, 100), sprites=spr_hero[4:8], animfps=4)
rect3 = PyObject((400, 100), (100, 100), sprites=spr_hero[8:12], animfps=4)
rect4 = PyObject((200, 100), (100, 100), sprites=spr_hero[12:16], animfps=4)
monster = PyObject((500, 100), (200, 200), sprites=monster1)
hero = PyObject((400, 300), (100, 100), sprites=spr_hero[0:4], animfps=4)

# Create sword and attach it to rect1
sword = Sword(hero, spr_zelda_sword[0], offset=(50, 0))  # Pass a single sprite

# Create font object
font = pygame.font.SysFont(None, 36)

dragging = False

rect2.rotate(90)

while gamerunning:
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

    # Update camera to follow rect1
    camera_pos = hero.pos - pygame.Vector2(screen.get_size()) / 2 / camera_zoom

    # Update and draw objects
    screen.fill("black")
    for obj in PyObject.all:
        obj.update()
        obj.draw(screen, camera_pos, camera_zoom)

    # Update and draw the sword
    sword.update()
    sword.draw(screen, camera_pos, camera_zoom)
    
    # Display FPS
    fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, "white")
    screen.blit(fps_text, (10, 10))
    
    pygame.display.flip()
    clock.tick(FPS)
