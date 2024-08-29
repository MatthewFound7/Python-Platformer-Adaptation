import pygame
import os
import random
import math
from os import listdir
from os.path import isfile, join
import time
from timer import Timer

pygame.init()

pygame.display.set_caption("Pixel Jump")

# Main Variables
WIDTH, HEIGHT = 950, 760
FPS = 60
PLAYER_VEL = 5

input_state_R = False
input_state_L = False

window = pygame.display.set_mode((WIDTH, HEIGHT))

# Control Wall jump state
def input_state_control():
    global input_state_R, input_state_L
    input_state_R = False
    input_state_L = False

timer = Timer(800, input_state_control)


# Flip each sprite individually
def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

# Loads and splits each sprite sheet into individual sprites + checks for direction if flipping
def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png","") + "_right"] = sprites
            all_sprites[image.replace(".png","") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png","")] = sprites

    return all_sprites

def load_sprite_sheets_2(dir1, dir2, dir3, width, height, direction=False):
    path = join("assets", dir1, dir2, dir3)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png","") + "_right"] = sprites
            all_sprites[image.replace(".png","") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png","")] = sprites

    return all_sprites

# Get a block from the terrain sheet and scales it (Grass Block)
def get_block(size, terrain_x, terrain_y):
    path = join("assets","Terrain","Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(terrain_x, terrain_y, size, size)
    surface.blit(image, (0,0), rect)
    return pygame.transform.scale2x(surface)

# Get text from text sheet
def get_text(size_x, size_y, character_x, character_y):
    path = join("assets","Menu","Text","Text (Black) (8x10).png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size_x, size_y), pygame.SRCALPHA, 32)
    rect = pygame.Rect(character_x, character_y, size_x, size_y)
    surface.blit(image, (0,0), rect)
    return pygame.transform.scale_by(surface,10)

# Get menu item from Button image
def get_menu_item(dir1, dir2, width, height):
    path = join("assets",dir1,dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]
    all_sprites = {}
    for image in images:
        sprite = pygame.image.load(join(path, image)).convert_alpha()
        sprite = pygame.transform.scale(sprite, (width, height))
        all_sprites[image.replace(".png","")] = sprite
    
    return all_sprites


# Player Characteristics: inherits from sprite
class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "NinjaFrog", 32, 32, True)
    ANIMATION_DELAY = 5

    # Initiate player attributes
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def wall_jump(self):
        self.y_vel = -self.GRAVITY * 13
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True
        self.hit_count = 0

    def move_left(self, vel):

        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    # Updates player state each frame
    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()
        
    # Resets fall and jump counts when landing
    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    # Updates players sprite based on current state
    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        if self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
            elif self.jump_count == 3:
                sprite_sheet = "wall_jump"
                if input_state_L:
                    self.direction = "right"
                elif input_state_R:
                    self.direction = "left"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    # Updates the player's rect and mask
    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    # Actual drawing of player on window
    def draw(self, win, offset_x, offset_y):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))

# Object Characteristics: for all objects in game
class Object(pygame.sprite.Sprite):
    # Initialises object attributes
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    # Actual drawing of object on window
    def draw(self, win, offset_x, offset_y):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))

# Represents block in game
class Block(Object):

    def __init__(self, x, y, size, terrain_x, terrain_y):
        super().__init__(x, y, size, size)
        block = get_block(size, terrain_x, terrain_y)
        self.image.blit(block, (0,0))
        self.mask = pygame.mask.from_surface(self.image)

# Represents text objects
class TextSprite(pygame.sprite.Sprite):
    # Initialises object attributes
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win):
        win.blit(self.image, (self.rect.x, self.rect.y))

class Text(TextSprite):

    def __init__(self, x, y, size_x, size_y, character_x, character_y):
        super().__init__(x, y, size_x, size_y)
        block = get_text(size_x, size_y, character_x, character_y)
        self.image.blit(block, (0,0))
        self.mask = pygame.mask.from_surface(self.image)

    

# Menu Items
class MenuItemSprite(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win):
        win.blit(self.image, (self.rect.x, self.rect.y))

class menu_item(MenuItemSprite):

    def __init__(self, x, y, size, item_name):
        super().__init__(x, y, size, size)
        self.item_name = item_name
        self.items = get_menu_item("Menu", "Buttons", size, size)
        self.image.blit(self.items[self.item_name], (0,0))
        self.mask = pygame.mask.from_surface(self.image)

    def select_item(self, item_name):
        self.item_name = item_name
        self.image = self.items[self.item_name]
        self.mask = pygame.mask.from_surface(self.image)

class level_item(MenuItemSprite):

    def __init__(self, x, y, size_x, size_y, item_name):
        super().__init__(x, y, size_x, size_y)
        self.item_name = item_name
        self.items = get_menu_item("Menu", "Levels", size_x, size_y)
        self.image.blit(self.items[self.item_name], (0,0))
        self.mask = pygame.mask.from_surface(self.image)

    def select_item(self, item_name):
        self.item_name = item_name
        self.image = self.items[self.item_name]
        self.mask = pygame.mask.from_surface(self.image)

# Represents fire trap in game
class Fire(Object):

    ANIMATION_DELAY = 3

    # Initialises  object attributes
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    # Updates fire animation each frame
    def loop(self):
        
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count //
                         self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class Spike(Object):

    ANIMATION_DELAY = 3

    # Initialises  object attributes
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "spike")
        self.spike = load_sprite_sheets("Traps", "Spikes", width, height)
        self.image = self.spike["Idle"][0]
        self.mask = pygame.mask.from_surface(self.image)

class Win_cup(Object):

    ANIMATION_DELAY = 6
    SPRITES = load_sprite_sheets_2("Items", "Checkpoints","End", 64, 45)

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "cup")
        self.cup = load_sprite_sheets_2("Items", "Checkpoints","End", width, height)
        self.image = self.cup["End (Idle)"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "End (Idle)"
        self.touch = False
        self.cup_count = 0

    def hit_cup(self):
        self.touch = True
        self.cup_count = 0


    def loop(self, fps):

        if self.touch:
            self.cup_count += 1
        if self.cup_count > fps * 2:
            self.touch = False
            self.cup_count = 0

        sprite_sheet = "End (Idle)"
        if self.touch:
            sprite_sheet = "End (Pressed) (64x64)"
        
        sprites = self.SPRITES[sprite_sheet]
        sprite_index = (self.animation_count //
                         self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        self.update()

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

# Loads background and tile positions
def get_background(name):
    image = pygame.image.load(join("assets","Background",name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image

# Draws background, objects, player, then updates
def draw(window, background, bg_image, player, objects, offset_x, offset_y):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x, offset_y)

    player.draw(window, offset_x, offset_y)

    pygame.display.update()

# Draws Homescreen
def draw_homescreen(window, background_purple, bg_image_purple, objects):
    for tile in background_purple:
        window.blit(bg_image_purple, tile)

    for obj in objects:
        obj.draw(window)

    pygame.display.update()

# Colission Handling
# Vertical collisions
def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects

# Horizontal collisions, move player forward temporarily, and then back
def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object

# Handles player movement and collisions based on Key Presses
def handle_move(player, objects, cup_1):
    # global input_state_R, input_state_L
    global input_state_R, input_state_L
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)
    
    if collide_right:
        input_state_L = True
        input_state_R = False  # Ensure right jump doesn't interfere
    elif collide_left:
        input_state_R = True
        input_state_L = False  # Ensure left jump doesn't interfere

    if input_state_L and player.jump_count == 3:
        if not timer.active:
            timer.activate()
        player.move_left(PLAYER_VEL)

    elif input_state_R and player.jump_count == 3:
        if not timer.active:
            timer.activate()
        player.move_right(PLAYER_VEL)

    elif keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    elif keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:

        if (obj and obj.name == "fire" and obj.animation_name == "on"):
            player.make_hit()
        if obj and obj.name == "spike":
            player.make_hit()
        if obj and obj.name == "cup"and keys[pygame.K_RETURN]:
            cup_1.hit_cup()

            

def main(window):
    
    game_active = False
    home_active = True
    levels_active = False
    achievements_active = False
    settings_active = False
    game_over_active = False
    game_active_01 = False
    game_active_02 = False
    game_active_03 = False
    mission_success = False
    # Frame Rate Control
    clock = pygame.time.Clock()
    # Load Background
    background, bg_image = get_background("Blue.png")
    # Load Homescreen
    background_purple, bg_image_purple = get_background("Purple.png")
    background_brown, bg_image_brown = get_background("Brown.png")
    background_green, bg_image_green = get_background("Green.png")


    # Game graphics: based on pre-determined graphics
    block_size = 96
    brick_x, brick_y = 272, 64
    grass_x, grass_y = 96, 0

    # Player, fire characteristic inputs
    player = Player(400,600,50,50)
    fire_1 = Fire(100, HEIGHT - block_size - 64,16,32)
    fire_1.on()
    spike_1 = Spike(200, HEIGHT - block_size - 32,16,32)
    cup_1 = Win_cup((WIDTH) - 300, HEIGHT - block_size - 90,64,45)
    cup_2 = Win_cup((WIDTH * 6), HEIGHT - block_size - 90,64,45)


    # Create floor blocks
    floor = [Block(i * block_size, HEIGHT - block_size, block_size, grass_x, grass_y) 
             for i in range(-WIDTH // block_size, (WIDTH * 3) // block_size)]
    floor_single = [Block(i * block_size, HEIGHT - block_size, block_size, grass_x, grass_y) 
                    for i in range(3200 // block_size, 3500 // block_size)]
    
    # List of all game objects
    objects = [*floor, 
               Block(0, HEIGHT - block_size * 2, block_size, grass_x, grass_y), 
               Block(block_size * 3, HEIGHT - block_size * 4, block_size, grass_x, grass_y),
               Block(block_size * 6, HEIGHT - block_size * 6, block_size, grass_x, grass_y),
               Block(block_size * 2, HEIGHT - block_size * 8, block_size, grass_x, grass_y),
               Block(block_size * 6, HEIGHT - block_size * 10, block_size, grass_x, grass_y), 
               Block(block_size * 10, HEIGHT - block_size * 3, block_size, brick_x, brick_y),
               Block(block_size * 10, HEIGHT - block_size * 4, block_size, brick_x, brick_y ),
               Block(block_size * 10, HEIGHT - block_size * 5, block_size, brick_x, brick_y),
               Block(block_size * 10, HEIGHT - block_size * 6, block_size, brick_x, brick_y),
               Block(block_size * 10, HEIGHT - block_size * 7, block_size, brick_x, brick_y),
               Block(block_size * 10, HEIGHT - block_size * 8, block_size, brick_x, brick_y),
               Block(block_size * 10, HEIGHT - block_size * 9, block_size, brick_x, brick_y ),
               Block(block_size * 10, HEIGHT - block_size * 10, block_size, brick_x, brick_y),
               Block(block_size * 10, HEIGHT - block_size * 11, block_size, brick_x, brick_y),
               Block(block_size * 10, HEIGHT - block_size * 12, block_size, brick_x, brick_y),
               Block(block_size * 13, HEIGHT - block_size * 3, block_size, brick_x, brick_y),
               Block(block_size * 13, HEIGHT - block_size * 4, block_size, brick_x, brick_y),
               Block(block_size * 13, HEIGHT - block_size * 5, block_size, brick_x, brick_y),
               Block(block_size * 13, HEIGHT - block_size * 6, block_size, brick_x, brick_y),
               Block(block_size * 13, HEIGHT - block_size * 7, block_size, brick_x, brick_y),
               Block(block_size * 13, HEIGHT - block_size * 8, block_size, brick_x, brick_y),
               Block(block_size * 13, HEIGHT - block_size * 9, block_size, brick_x, brick_y),
               Block(block_size * 13, HEIGHT - block_size * 10, block_size, brick_x, brick_y),
               Block(block_size * 13, HEIGHT - block_size * 11, block_size, brick_x, brick_y),
               Block(block_size * 13, HEIGHT - block_size * 12, block_size, brick_x, brick_y),
               Block(block_size * 20, HEIGHT - block_size * 2, block_size, brick_x, brick_y),
               Block(block_size * 14, HEIGHT - block_size * 4, block_size, brick_x, brick_y),
               Block(block_size * 15, HEIGHT - block_size * 4, block_size, brick_x, brick_y),
               Block(block_size * 16, HEIGHT - block_size * 4, block_size, brick_x, brick_y),
               Block(block_size * 17, HEIGHT - block_size * 4, block_size, brick_x, brick_y),
               Block(block_size * 20, HEIGHT - block_size * 3, block_size, brick_x, brick_y),
               Block(block_size * 20, HEIGHT - block_size * 4, block_size, brick_x, brick_y),
               Block(block_size * 20, HEIGHT - block_size * 5, block_size, brick_x, brick_y),
               fire_1, spike_1,
               *floor_single,
               cup_1]
    
    floor_01 = [Block(i * block_size, HEIGHT - block_size, block_size, grass_x, grass_y) 
                for i in range(-WIDTH // block_size, (WIDTH * 10) // block_size)]
    objs_01 = [*floor_01,
               Block(block_size * 17, HEIGHT - block_size * 2, block_size, brick_x, brick_y),
               Block(block_size * 18, HEIGHT - block_size * 3, block_size, brick_x, brick_y),
               Block(block_size * 19, HEIGHT - block_size * 2, block_size, brick_x, brick_y),
               Block(block_size * 27, HEIGHT - block_size * 2, block_size, brick_x, brick_y),
               Block(block_size * 27, HEIGHT - block_size * 3, block_size, brick_x, brick_y),
               Block(block_size * 35, HEIGHT - block_size * 2, block_size, brick_x, brick_y),
               Block(block_size * 36, HEIGHT - block_size * 2, block_size, brick_x, brick_y),
               Block(block_size * 37, HEIGHT - block_size * 2, block_size, brick_x, brick_y),
               Block(block_size * 38, HEIGHT - block_size * 2, block_size, brick_x, brick_y),
               Block(block_size * 39, HEIGHT - block_size * 2, block_size, brick_x, brick_y),
               Block(block_size * 40, HEIGHT - block_size * 2, block_size, brick_x, brick_y),
               Block(block_size * 40, HEIGHT - block_size * 3, block_size, brick_x, brick_y),
               Block(block_size * 40, HEIGHT - block_size * 4, block_size, brick_x, brick_y),
               Block(block_size * 40, HEIGHT - block_size * 5, block_size, brick_x, brick_y),
               Block(block_size * 40, HEIGHT - block_size * 6, block_size, brick_x, brick_y),
               Block(block_size * 40, HEIGHT - block_size * 7, block_size, brick_x, brick_y),
               Block(block_size * 40, HEIGHT - block_size * 8, block_size, brick_x, brick_y),
               Block(block_size * 40, HEIGHT - block_size * 9, block_size, brick_x, brick_y),
               Block(block_size * 40, HEIGHT - block_size * 10, block_size, brick_x, brick_y),
               Block(block_size * 40, HEIGHT - block_size * 11, block_size, brick_x, brick_y),
               Block(block_size * 40, HEIGHT - block_size * 12, block_size, brick_x, brick_y),
               Block(block_size * 37, HEIGHT - block_size * 5, block_size, brick_x, brick_y),
               Block(block_size * 35, HEIGHT - block_size * 6, block_size, brick_x, brick_y),
               Block(block_size * 31, HEIGHT - block_size * 7, block_size, brick_x, brick_y),
               Block(block_size * 39, HEIGHT - block_size * 3, block_size, brick_x, brick_y),
               Block(block_size * 35, HEIGHT - block_size * 9, block_size, brick_x, brick_y),
               Block(block_size * 36, HEIGHT - block_size * 9, block_size, brick_x, brick_y),
               Block(block_size * 37, HEIGHT - block_size * 9, block_size, brick_x, brick_y),
               Block(block_size * 36, HEIGHT - block_size * 11, block_size, brick_x, brick_y),
               Block(block_size * 35, HEIGHT - block_size * 11, block_size, brick_x, brick_y),
               Block(block_size * 52, HEIGHT - block_size * 2, block_size, brick_x, brick_y),
               Block(block_size * 52, HEIGHT - block_size * 3, block_size, brick_x, brick_y),
               Block(block_size * 52, HEIGHT - block_size * 4, block_size, brick_x, brick_y),
               Block(block_size * 52, HEIGHT - block_size * 5, block_size, brick_x, brick_y),
               Block(block_size * 49, HEIGHT - block_size * 4, block_size, brick_x, brick_y),
               Block(block_size * 48, HEIGHT - block_size * 4, block_size, brick_x, brick_y),
               Block(block_size * 47, HEIGHT - block_size * 4, block_size, brick_x, brick_y),
               Block(block_size * 46, HEIGHT - block_size * 4, block_size, brick_x, brick_y),
               Block(block_size * 46, HEIGHT - block_size * 5, block_size, brick_x, brick_y),
               Block(block_size * 46, HEIGHT - block_size * 6, block_size, brick_x, brick_y),
               Block(block_size * 46, HEIGHT - block_size * 7, block_size, brick_x, brick_y),
               Block(block_size * 46, HEIGHT - block_size * 8, block_size, brick_x, brick_y),
               Block(block_size * 49, HEIGHT - block_size * 7, block_size, brick_x, brick_y),
               Block(block_size * 50, HEIGHT - block_size * 7, block_size, brick_x, brick_y),
               Block(block_size * 46, HEIGHT - block_size * 8, block_size, brick_x, brick_y),
               Block(block_size * 46, HEIGHT - block_size * 9, block_size, brick_x, brick_y),
               Block(block_size * 52, HEIGHT - block_size * 6, block_size, brick_x, brick_y),
               Block(block_size * 46, HEIGHT - block_size * 10, block_size, brick_x, brick_y),
               Block(block_size * 47, HEIGHT - block_size * 10, block_size, brick_x, brick_y),
               Block(block_size * 48, HEIGHT - block_size * 10, block_size, brick_x, brick_y),
               Block(block_size * 49, HEIGHT - block_size * 10, block_size, brick_x, brick_y),
               Block(block_size * 50, HEIGHT - block_size * 10, block_size, brick_x, brick_y),
               Block(block_size * 51, HEIGHT - block_size * 10, block_size, brick_x, brick_y),
               Block(block_size * 52, HEIGHT - block_size * 10, block_size, brick_x, brick_y),
               Block(block_size * 52, HEIGHT - block_size * 7, block_size, brick_x, brick_y),
               Block(block_size * 51, HEIGHT - block_size * 7, block_size, brick_x, brick_y),
               Block(block_size * 46, HEIGHT - block_size * 11, block_size, brick_x, brick_y),
               Block(block_size * 46, HEIGHT - block_size * 12, block_size, brick_x, brick_y),
               Block(block_size * 46, HEIGHT - block_size * 13, block_size, brick_x, brick_y),
               cup_2]
    
    # Home_screen graphics
    # Letters
    text_size_x = 80
    text_size_y = 100

    black_A_x, black_A_y = 0,  0
    black_B_x, black_B_y = 8,  0
    black_C_x, black_C_y = 16, 0
    black_D_x, black_D_y = 24, 0
    black_E_x, black_E_y = 32, 0
    black_F_x, black_F_y = 40, 0
    black_G_x, black_G_y = 48, 0
    black_H_x, black_H_y = 56, 0
    black_I_x, black_I_y = 64, 0
    black_J_x, black_J_y = 72, 0
    black_K_x, black_K_y = 0,  10
    black_L_x, black_L_y = 8,  10
    black_M_x, black_M_y = 16, 10
    black_N_x, black_N_y = 24, 10
    black_O_x, black_O_y = 32, 10
    black_P_x, black_P_y = 40, 10
    black_Q_x, black_Q_y = 48, 10
    black_R_x, black_R_y = 56, 10
    black_S_x, black_S_y = 64, 10
    black_T_x, black_T_y = 72, 10
    black_U_x, black_U_y = 0,  20
    black_V_x, black_V_y = 8,  20
    black_W_x, black_W_y = 16, 20
    black_X_x, black_X_y = 24, 20
    black_Y_x, black_Y_y = 32, 20
    black_Z_x, black_Z_y = 40, 20
    black_0_x, black_0_y = 0,  30
    black_1_x, black_1_y = 8,  30
    black_2_x, black_2_y = 16, 30
    black_3_x, black_3_y = 24, 30
    black_4_x, black_4_y = 32, 30
    black_5_x, black_5_y = 40, 30
    black_6_x, black_6_y = 48, 30
    black_7_x, black_7_y = 56, 30
    black_8_x, black_8_y = 64, 30
    black_9_x, black_9_y = 72, 30
    black_dot_x, black_dot_y = 0,  40
    black_comma_x, black_comma_y = 8,  40
    black_colon_x, black_colon_y = 16, 40
    black_question_x, black_question_y = 24, 40
    black_exclamation_x, black_exclamation_y = 32, 40
    black_openbrack_x, black_openbrack_y = 40, 40
    black_closebrack_x, black_closebrack_y = 48, 40
    black_plus_x, black_plus_y = 56, 40
    black_minus_x, black_minus_y = 64, 40


    # Button Stores
    play_button = menu_item(422.5, 340, 105, "Play")
    levels_button = menu_item(307.5, 540, 105, "Levels")
    achievements_button = menu_item(422.5, 540, 105, "Achievements")
    settings_button = menu_item(537.5, 540, 105, "Settings")
    back_button = menu_item(422.5, 640, 105, "Back")
    home_button = menu_item(422.5, 540, 105, "Home")
    level_scale_x = 95
    level_scale_y = 85
    start_x = 67
    start_y = 120
    level_grid = [level_item(start_x + x, start_y + y, level_scale_x, level_scale_y, f"{i:02}") for i, (x, y) in enumerate(((x * 180, y * 96) for y in range(5) for x in range(5)), start=1)]
    

    # List of homescreen objects
    home_text = [Text(75, 150, text_size_x, text_size_y, black_P_x, black_P_y),
                 Text(155, 150, text_size_x, text_size_y, black_I_x, black_I_y),
                 Text(235, 150, text_size_x, text_size_y, black_X_x, black_X_y),
                 Text(315, 150, text_size_x, text_size_y, black_E_x, black_E_y),
                 Text(395, 150, text_size_x, text_size_y, black_L_x, black_L_y),
                 Text(555, 150, text_size_x, text_size_y, black_J_x, black_J_y),
                 Text(635, 150, text_size_x, text_size_y, black_U_x, black_U_y),
                 Text(715, 150, text_size_x, text_size_y, black_M_x, black_M_y),
                 Text(795, 150, text_size_x, text_size_y, black_P_x, black_P_y),
                 play_button,
                 levels_button,
                 achievements_button,
                 settings_button] 
    
    game_over_text = [Text(115, 150, text_size_x, text_size_y, black_G_x, black_G_y),
                      Text(195, 150, text_size_x, text_size_y, black_A_x, black_A_y),
                      Text(275, 150, text_size_x, text_size_y, black_M_x, black_M_y),
                      Text(355, 150, text_size_x, text_size_y, black_E_x, black_E_y),
                      Text(515, 150, text_size_x, text_size_y, black_O_x, black_O_y),
                      Text(595, 150, text_size_x, text_size_y, black_V_x, black_V_y),
                      Text(675, 150, text_size_x, text_size_y, black_E_x, black_E_y),
                      Text(755, 150, text_size_x, text_size_y, black_R_x, black_R_y),
                      home_button]
    
    mission_success_text = [Text(70, 150, text_size_x, text_size_y, black_L_x, black_L_y),
                            Text(150, 150, text_size_x, text_size_y, black_E_x, black_E_y),
                            Text(230, 150, text_size_x, text_size_y, black_V_x, black_V_y),
                            Text(310, 150, text_size_x, text_size_y, black_E_x, black_E_y),
                            Text(390, 150, text_size_x, text_size_y, black_L_x, black_L_y),
                            Text(180, 270, text_size_x, text_size_y, black_C_x, black_C_y),
                            Text(260, 270, text_size_x, text_size_y, black_O_x, black_O_y),
                            Text(340, 270, text_size_x, text_size_y, black_M_x, black_M_y),
                            Text(420, 270, text_size_x, text_size_y, black_P_x, black_P_y),
                            Text(500, 270, text_size_x, text_size_y, black_L_x, black_L_y),
                            Text(580, 270, text_size_x, text_size_y, black_E_x, black_E_y),
                            Text(660, 270, text_size_x, text_size_y, black_T_x, black_T_y),
                            Text(740, 270, text_size_x, text_size_y, black_E_x, black_E_y),
                            Text(820, 270, text_size_x, text_size_y, black_exclamation_x, black_exclamation_y),
                            home_button]
    

    #levels_text = [level_item(100,100,level_scale_x,level_scale_y,"01")]
    levels_text = level_grid[:25]
    levels_text.append(back_button)

    # Scrolling Variables
    offset_x = 0
    offset_y = 0
    scroll_area_width_x = 200
    scroll_area_width_y = 200

    game_states = {f'game_active_{i+1:02}': False for i in range(25)}
    player_ready_01 = False

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            
            # Handle for jumping key
            if event.type == pygame.KEYDOWN: 
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()
                if game_active:
                    if event.key == pygame.K_SPACE and (collide(player, objects, -PLAYER_VEL * 2) or collide(player, objects, PLAYER_VEL * 2)) and (1 < player.jump_count < 3):
                        player.wall_jump()
                        player.y_vel = -player.GRAVITY * 14
                if game_states["game_active_01"]:
                    if event.key == pygame.K_SPACE and (collide(player, objs_01, -PLAYER_VEL * 2) or collide(player, objs_01, PLAYER_VEL * 2)) and (1 < player.jump_count < 3):
                        player.wall_jump()
                        player.y_vel = -player.GRAVITY * 14
                    
            
            # if player.fall_count == 1:
            #     player.jump_count = 3
        
        timer.update()

        if game_active:
            # Update states, handles movement and collisions, draws game

            if player_ready_01 == False:
                player = Player(400,600,50,50)
                player_ready_01 = True
                

            player.loop(FPS)
            fire_1.loop()
            cup_1.loop(FPS)

            handle_move(player, objects, cup_1)
            draw(window, background, bg_image, player, objects, offset_x, offset_y)

            # Conditions for scrolling
            if((player.rect.right - offset_x >= WIDTH - scroll_area_width_x) and player.x_vel > 0) or (
                (player.rect.left - offset_x  <= scroll_area_width_x) and player.x_vel < 0):
                offset_x += player.x_vel

            if (player.rect.bottom >= HEIGHT - block_size):
                offset_y = 0
            else:
                if((player.rect.bottom - offset_y >= HEIGHT - scroll_area_width_y) and player.y_vel > 0) or (
                    (player.rect.top - offset_y  <= scroll_area_width_y) and player.y_vel < 0):
                    offset_y += player.y_vel

            if offset_y > 0:
                offset_y = 0

            if (player.rect.bottom >= HEIGHT + 3000) or player.hit_count == 120:
                game_over_active = True
                game_active = False
                player_ready_01 = False
                offset_x = 0
                offset_y = 0
            if cup_1.cup_count == 120:
                game_over_active = True
                game_active = False
                player_ready_01 = False
                offset_x = 0
                offset_y = 0
            
        elif home_active:
            
            draw_homescreen(window, background_purple, bg_image_purple, home_text)

            play_button.select_item("Play")
            levels_button.select_item("Levels")
            achievements_button.select_item("Achievements")
            settings_button.select_item("Settings")

            

            if event.type == pygame.MOUSEMOTION:
                if play_button.rect.collidepoint(event.pos):
                    play_button.select_item("PlayClick")
                else:
                    play_button.select_item("Play")
                if levels_button.rect.collidepoint(event.pos):
                    levels_button.select_item("LevelsClick")
                else:
                    levels_button.select_item("Levels")
                if achievements_button.rect.collidepoint(event.pos):
                    achievements_button.select_item("AchievementsClick")
                else:
                    achievements_button.select_item("Achievements")
                if settings_button.rect.collidepoint(event.pos):
                    settings_button.select_item("SettingsClick")
                else:
                    settings_button.select_item("Settings")
                
                
            if event.type == pygame.MOUSEBUTTONUP:
                if play_button.rect.collidepoint(event.pos):
                    game_active = True
                    home_active = False
                if levels_button.rect.collidepoint(event.pos):
                    levels_active = True
                    home_active = False
            
        elif levels_active:      
            draw_homescreen(window, background_purple, bg_image_purple, levels_text)

            back_button.select_item("Back")

            if event.type == pygame.MOUSEMOTION:
                if back_button.rect.collidepoint(event.pos):
                    back_button.select_item("BackClick")
                else:
                    back_button.select_item("Back")

                for level_button in levels_text[:3]:
                    if level_button.rect.collidepoint(event.pos):
                        if not level_button.item_name.endswith("Click"):
                            level_button.select_item(level_button.item_name + "Click")
                    else:
                        if level_button.item_name.endswith("Click"):
                            level_button.select_item(level_button.item_name[:-5])

            if event.type == pygame.MOUSEBUTTONUP:
                if back_button.rect.collidepoint(event.pos):
                    home_active = True
                    levels_active = False

                for i, level_button in enumerate(levels_text[:25],0):
                    if level_button.rect.collidepoint(event.pos):
                        game_states[f'game_active_{i+1:02}'] = True
                        levels_active = False
                        break
                
        elif game_over_active:
            draw_homescreen(window, background_brown, bg_image_brown, game_over_text)
                        
            home_button.select_item("Home")

            if event.type == pygame.MOUSEMOTION:
                if home_button.rect.collidepoint(event.pos):
                    home_button.select_item("HomeClick")
                else:
                    home_button.select_item("Home")

            if event.type == pygame.MOUSEBUTTONUP:
                if home_button.rect.collidepoint(event.pos):
                    home_active = True
                    game_over_active = False

        elif mission_success:
            draw_homescreen(window, background_green, bg_image_green, mission_success_text)
            home_button.select_item("Home")

            if event.type == pygame.MOUSEMOTION:
                if home_button.rect.collidepoint(event.pos):
                    home_button.select_item("HomeClick")
                else:
                    home_button.select_item("Home")

            if event.type == pygame.MOUSEBUTTONUP:
                if home_button.rect.collidepoint(event.pos):
                    home_active = True
                    mission_success = False

        if game_states['game_active_01']:
            # Update states, handles movement and collisions, draws game
            if player_ready_01 == False:
                player = Player(400,-200,50,50)
                player_ready_01 = True

            player.loop(FPS)
            fire_1.loop()
            cup_2.loop(FPS)
            handle_move(player, objs_01, cup_2)
            draw(window, background, bg_image, player, objs_01, offset_x, offset_y)

            # Conditions for scrolling
            if((player.rect.right - offset_x >= WIDTH - scroll_area_width_x) and player.x_vel > 0) or (
                (player.rect.left - offset_x  <= scroll_area_width_x) and player.x_vel < 0):
                offset_x += player.x_vel

            if (player.rect.bottom >= HEIGHT - block_size):
                offset_y = 0
            else:
                if((player.rect.bottom - offset_y >= HEIGHT - scroll_area_width_y) and player.y_vel > 0) or (
                    (player.rect.top - offset_y  <= scroll_area_width_y) and player.y_vel < 0):
                    offset_y += player.y_vel

            if offset_y > 0:
                offset_y = 0

            if (player.rect.bottom >= HEIGHT + 3000) or player.hit_count == 120:
                game_over_active = True
                game_states["game_active_01"] = False
                player_ready_01 = False
                offset_x = 0
                offset_y = 0

            if cup_2.cup_count == 120:
                mission_success = True
                game_states["game_active_01"] = False
                player_ready_01 = False
                offset_x = 0
                offset_y = 0
            
    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window)























































































