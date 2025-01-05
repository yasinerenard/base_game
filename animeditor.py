import pygame
import sys
import os
import json
import pyperclip

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("AnimEditor")

# Initialize variables
image = None
rect = pygame.Rect(0, 0, 0, 0)
dragging = False
dragging_image = False
dragging_edge = None
dragging_square = False
sprite_sheets = []
zoom = 1.0
camera_pos = pygame.Vector2(0, 0)

# Button definitions
buttons = {
    "save": pygame.Rect(10, 10, 100, 30),
    "clear_squares": pygame.Rect(120, 10, 100, 30),
    "clear_image": pygame.Rect(230, 10, 100, 30)
}

def load_image(file_path):
    global image
    image = pygame.image.load(file_path).convert_alpha()

def save_sprite_sheets(file_path):
    with open(file_path, 'w') as f:
        json.dump(sprite_sheets, f)

def load_sprite_sheets(file_path):
    global sprite_sheets
    with open(file_path, 'r') as f:
        sprite_sheets = json.load(f)

def delete_sprite_sheet(index):
    if 0 <= index < len(sprite_sheets):
        del sprite_sheets[index]

def save_presets_to_clipboard():
    preset = f"sprites = spritesheet('image.png', {rect.topleft + rect.size})"
    pyperclip.copy(preset)

def clear_squares():
    global sprite_sheets, rect
    sprite_sheets = []
    rect = pygame.Rect(0, 0, 0, 0)

def clear_image():
    global image
    image = None

def main():
    global dragging, dragging_image, dragging_edge, dragging_square, rect, zoom, camera_pos
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.DROPFILE:
                load_image(event.file)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button, button_rect in buttons.items():
                    if button_rect.collidepoint(event.pos):
                        if button == "save":
                            save_presets_to_clipboard()
                        elif button == "clear_squares":
                            clear_squares()
                        elif button == "clear_image":
                            clear_image()
                        break
                else:
                    image_pos = (pygame.Vector2(event.pos) + camera_pos) / zoom
                    if event.button == 1:
                        if rect.collidepoint(image_pos):
                            dragging_edge = get_dragging_edge(image_pos)
                            if not dragging_edge:
                                dragging_square = True
                                drag_start = image_pos - rect.topleft
                        else:
                            rect.topleft = image_pos
                            dragging = True
                            sprite_sheets.clear()
                    elif event.button == 2:
                        dragging_image = True
                        drag_start = pygame.Vector2(event.pos)
                        camera_start = camera_pos.copy()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
                    dragging_edge = None
                    dragging_square = False
                    sprite_sheets.clear()
                    sprite_sheets.append(rect.copy())
                elif event.button == 2:
                    dragging_image = False
            elif event.type == pygame.MOUSEMOTION:
                image_pos = (pygame.Vector2(event.pos) + camera_pos) / zoom
                if dragging:
                    rect.size = image_pos[0] - rect.x, image_pos[1] - rect.y
                elif dragging_image:
                    camera_pos = camera_start + (drag_start - pygame.Vector2(event.pos)) / zoom
                elif dragging_square:
                    rect.topleft = image_pos - drag_start
            elif event.type == pygame.MOUSEWHEEL:
                if pygame.key.get_mods() & pygame.KMOD_CTRL:
                    zoom *= 1.1 if event.y > 0 else 0.9

        screen.fill((255, 255, 255))
        if image:
            visible_rect = pygame.Rect(camera_pos, (screen.get_width() / zoom, screen.get_height() / zoom))
            visible_rect.clamp_ip(image.get_rect())  # Ensure visible_rect is within image bounds
            visible_rect.size = (min(visible_rect.width, image.get_width()), min(visible_rect.height, image.get_height()))  # Adjust visible_rect size if necessary
            visible_image = image.subsurface(visible_rect).copy()
            transformed_image = pygame.transform.scale(visible_image, (int(visible_rect.width * zoom), int(visible_rect.height * zoom)))
            screen.blit(transformed_image, (0, 0))
        for sheet in sprite_sheets:
            adjusted_rect = pygame.Rect(
                (pygame.Vector2(sheet.topleft) - camera_pos) * zoom,
                pygame.Vector2(sheet.size) * zoom
            )
            pygame.draw.rect(screen, (0, 255, 0), adjusted_rect, 2)
        if dragging or dragging_edge or dragging_square:
            adjusted_rect = pygame.Rect(
                (pygame.Vector2(rect.topleft) - camera_pos) * zoom,
                pygame.Vector2(rect.size) * zoom
            )
            pygame.draw.rect(screen, (255, 0, 0), adjusted_rect, 2)

        # Draw buttons
        pygame.draw.rect(screen, (200, 200, 200), buttons["save"])
        pygame.draw.rect(screen, (200, 200, 200), buttons["clear_squares"])
        pygame.draw.rect(screen, (200, 200, 200), buttons["clear_image"])
        font = pygame.font.SysFont(None, 24)
        screen.blit(font.render("Save", True, (0, 0, 0)), (20, 15))
        screen.blit(font.render("Clear Squares", True, (0, 0, 0)), (130, 15))
        screen.blit(font.render("Clear Image", True, (0, 0, 0)), (240, 15))

        # Fill the square with green at half opacity if the mouse is over it
        mouse_pos = (pygame.Vector2(pygame.mouse.get_pos()) + camera_pos) / zoom
        if rect.collidepoint(mouse_pos):
            green_surface = pygame.Surface((pygame.Vector2(rect.size) * zoom))
            green_surface.set_alpha(128)
            green_surface.fill((0, 255, 0))
            screen.blit(green_surface, (rect.topleft - camera_pos) * zoom)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

def get_dragging_edge(pos):
    edges = {
        "left": pygame.Rect(rect.left - 5, rect.top, 10, rect.height),
        "right": pygame.Rect(rect.right - 5, rect.top, 10, rect.height),
        "top": pygame.Rect(rect.left, rect.top - 5, rect.width, 10),
        "bottom": pygame.Rect(rect.left, rect.bottom - 5, rect.width, 10)
    }
    for edge, edge_rect in edges.items():
        if edge_rect.collidepoint(pos):
            return edge
    return None

def resize_rect(pos):
    if dragging_edge == "left":
        rect.width += rect.left - pos[0]
        rect.left = pos[0]
    elif dragging_edge == "right":
        rect.width = pos[0] - rect.left
    elif dragging_edge == "top":
        rect.height += rect.top - pos[1]
        rect.top = pos[1]
    elif dragging_edge == "bottom":
        rect.height = pos[1] - rect.top

if __name__ == "__main__":
    main()
