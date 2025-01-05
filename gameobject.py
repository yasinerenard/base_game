import pygame
import sys
import os

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Resizable pyobject with Camera Controls")

clock = pygame.time.Clock()
FPS = 60
gamerunning = True

key_states = {}
#                                       keys options
def update_key_states():
    keys = pygame.key.get_pressed()
    
    for key in range(pygame.K_SPACE, pygame.K_z + 1):
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
#                                       sprite sheets
def spritesheet(image_file, rect, rows=1, cols=1):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, image_file)
    sprite_sheet = pygame.image.load(image_path).convert_alpha()
    sprite_width, sprite_height = rect[2] // cols, rect[3] // rows
    return [sprite_sheet.subsurface(pygame.Rect(rect[0] + col * sprite_width, rect[1] + row * sprite_height, sprite_width, sprite_height))
            for row in range(rows) for col in range(cols)]
#                                       pyobject
class PyObject:
    all_objects = []
    
    def __init__(self, pos, size, sprites=None, animfps=FPS):
        self.pos = pygame.Vector2(pos)
        self.size = pygame.Vector2(size)
        self.original_size = pygame.Vector2(size)
        self.sprites = sprites
        self.animfps = animfps
        self.sprite_index = 0
        self.frame_count = 0
        self.animation_speed = FPS // animfps
        self.current_sprite = self.sprites[self.sprite_index] if sprites else None
        self.rotation_angle = 0  # Initialize rotation angle
        self.lookat_offset = 0  # Initialize lookat offset
        PyObject.all_objects.append(self)

    def set_animfps(self, fps):
        self.animfps = fps
        self.animation_speed = FPS // fps

    def update(self):
        if self.sprites:
            self.frame_count = (self.frame_count + 1) % self.animation_speed
            if self.frame_count == 0:
                self.sprite_index = (self.sprite_index + 1) % len(self.sprites)
                self.current_sprite = self.sprites[self.sprite_index]

    def rotate(self, angle):
        self.rotation_angle = (self.rotation_angle + angle) % 360  # Update rotation angle

    def look_at(self, target):
        direction = target - self.pos
        self.rotation_angle = direction.angle_to(pygame.Vector2(1, 0)) + self.lookat_offset  # Calculate angle to target with offset

    def set_lookat_offset(self, offset):
        self.lookat_offset = offset

    def set_sprites(self, new_sprites, animfps=None):
        self.sprites = new_sprites
        self.sprite_index = 0
        self.frame_count = 0
        self.current_sprite = self.sprites[self.sprite_index]
        if animfps:
            self.set_animfps(animfps)

    def draw(self, screen, camera_pos, camera_zoom):
        transformed_pos = (self.pos - camera_pos) * camera_zoom
        transformed_size = self.original_size * camera_zoom

        if self.current_sprite:
            # Scale the sprite to the transformed size
            scaled_sprite = pygame.transform.scale(self.current_sprite, (int(transformed_size.x), int(transformed_size.y)))
            # Rotate the scaled sprite
            rotated_sprite = pygame.transform.rotate(scaled_sprite, +self.rotation_angle)  # Rotate in the correct direction
            # Calculate the position for blitting the sprite
            blit_pos = rotated_sprite.get_rect(center=(int(transformed_pos.x), int(transformed_pos.y)))
            screen.blit(rotated_sprite, blit_pos.topleft)
        else:
            pygame.draw.rect(screen, "white", (*transformed_pos, *transformed_size))

def check_button_press():
    return pygame.key.get_pressed(), pygame.mouse.get_pressed()

camera_pos, camera_zoom = pygame.Vector2(0, 0), 1.0
sprites = spritesheet('walking.png', (0, 0, 1600, 2397), 4, 4)
gun1 = spritesheet('guns.png', (130, 20, 70, 15))
sprites_link = spritesheet('walking.png', (0, 0, 665, 166), 4, 6)
rect1 = PyObject((400, 300), (100, 100), sprites=sprites[0:4], animfps=4)
gun = PyObject((200, 300), (100, 100), sprites=gun1, animfps=4)
rect3 = PyObject((400, 100), (100, 100), sprites=sprites[8:12], animfps=4)
rect4 = PyObject((200, 100), (100, 100), sprites=sprites[12:16], animfps=4)

def move_pyobject(obj, keys, speed=5):
    if keys[pygame.K_LEFT]: 
        obj.pos.x -= speed
    if keys[pygame.K_RIGHT]: 
        obj.pos.x += speed
    if keys[pygame.K_UP]: 
        obj.pos.y -= speed
    if keys[pygame.K_DOWN]: 
        obj.pos.y += speed
    if key_is_triggered(pygame.K_LEFT):
        obj.sprites=sprites[8:12]
        print("a")
    if key_is_triggered(pygame.K_RIGHT):
        obj.sprites=sprites[12:16]
    if key_is_triggered(pygame.K_UP):
        obj.sprites=sprites[4:8]
    if key_is_triggered(pygame.K_DOWN):
        obj.sprites=sprites[0:4]


# Create font object
font = pygame.font.SysFont(None, 36)

dragging = False

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

    keys, _ = check_button_press()
    move_pyobject(rect1, keys)

    # Rotate rect2 to face the mouse
    mouse_pos = pygame.Vector2(pygame.mouse.get_pos()) / camera_zoom + camera_pos
    gun.look_at(mouse_pos)

    # Switch animations for rect2 using A and S keys
    if keys[pygame.K_a]:
        gun.set_sprites(sprites[4:8], animfps=4)
    if keys[pygame.K_s]:
        gun.set_sprites(sprites_link[0:4], animfps=4)

    screen.fill("black")
    for obj in PyObject.all_objects:
        obj.update()
        obj.draw(screen, camera_pos, camera_zoom)
    
    # Display FPS
    fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, "white")
    screen.blit(fps_text, (10, 10))
    
    pygame.display.flip()
    clock.tick(FPS)
