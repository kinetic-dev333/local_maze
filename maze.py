import math
import os
import pygame
import random
import sys
import vec2d

#------------------------------------------------------------------------------
class Character(pygame.sprite.Sprite):
    def __init__(self, game, image_filename, x, y, speed):
        self.game = game
        self.image_filename = image_filename
        if image_filename != None:
            self.image = pygame.image.load(self.image_filename).convert_alpha()
        self.x = x
        self.y = y
        self.radius = 16
        self.speed = speed
        self.last_key = None
        self.vector = vec2d.vec2d(0, 0)
        self.last_position = (self.x, self.y)
        self.key_is_down = False
        self.rect = self.image.get_rect()
        self.last_rect = self.image.get_rect()
        
    def keydown(self, event):
        keys = pygame.key.get_pressed()
        
        self.key_is_down = True
        if keys[pygame.K_DOWN] and keys[pygame.K_LEFT]:
            self.vector = vec2d.vec2d(-1, 1)
            return True
        elif keys[pygame.K_DOWN] and keys[pygame.K_RIGHT]:
            self.vector = vec2d.vec2d(1, 1)
            return True
        elif keys[pygame.K_UP] and keys[pygame.K_LEFT]:
            self.vector = vec2d.vec2d(-1, -1)
            return True
        elif keys[pygame.K_UP] and keys[pygame.K_RIGHT]:
            self.vector = vec2d.vec2d(1, -1)
            return True
        
        elif keys[pygame.K_DOWN]:
            self.vector = vec2d.vec2d(0, 1)
            return True
        elif keys[pygame.K_LEFT]:
            self.vector = vec2d.vec2d(-1, 0)
            return True
        elif keys[pygame.K_RIGHT]:
            self.vector = vec2d.vec2d(1, 0)
            return True
        elif keys[pygame.K_UP]:
            self.vector = vec2d.vec2d(0, -1)
            return True
        else:
            self.vector = vec2d.vec2d(0, 0)
            return False
        
    def keyup(self, event):
        self.key_is_down = False
        self.vector = vec2d.vec2d(0, 0)
        self.keydown(event)
    
    def move(self, dx, dy):
        if dx < 0:
            if self.x - dx > 0:
                self.x += dx
        else:
            if self.x + self.image.get_rect().right + dx < self.game.screen_width:
                self.x += dx
                
        if dy < 0:
            if self.y - dy > 0:
                self.y += dy
        else:
            if self.y + self.image.get_rect().bottom + dx < self.game.screen_height:
                self.y += dy

        self.last_rect = self.rect.copy()
        self.rect.left = self.x
        self.rect.top = self.y

    def move_back(self):
        self.rect = self.last_rect
        self.x = self.last_rect.left
        self.y = self.last_rect.top
    def update(self):

        self.move(self.vector.x * self.speed, self.vector.y * self.speed)
        self.last_position = (self.x, self.y)

    def blitme(self):
        self.update()
        draw_pos = self.image.get_rect().move(self.x, self.y)
        self.game.screen.blit(self.image, draw_pos)
#------------------------------------------------------------------------------
class Creep(Character):
    def __init__(   
        self, screen, img_filename, init_position, 
        init_direction, speed):
        pygame.sprite.Sprite.__init__(self)
        
        self.screen = screen
        self.speed = speed
        self.radius = 8
        self.rect = pygame.Rect(init_position[0], init_position[1], 8, 8)
        
        # base_image holds the original image, positioned to
        # angle 0.
        # image will be rotated.
        #
        self.base_image = pygame.image.load(img_filename).convert_alpha()
        self.image = self.base_image
        
        # A vector specifying the creep's position on the screen
        #
        self.pos = vec2d.vec2d(init_position)

        # The direction is a normalized vector
        #
        self.direction = vec2d.vec2d(init_direction).normalized()
            
    def update(self, time_passed):
        """ Update the creep.
        
            time_passed:
                The time passed (in ms) since the previous update.
        """
        # Maybe it's time to change the direction ?
        #
        self._change_direction(time_passed)
        
        # Make the creep point in the correct direction.
        # Since our direction vector is in screen coordinates 
        # (i.e. right bottom is 1, 1), and rotate() rotates 
        # counter-clockwise, the angle must be inverted to 
        # work correctly.
        #
        self.image = pygame.transform.rotate(
            self.base_image, -self.direction.angle)
        
        # Compute and apply the displacement to the position 
        # vector. The displacement is a vector, having the angle
        # of self.direction (which is normalized to not affect
        # the magnitude of the displacement)
        #
        displacement = vec2d.vec2d(    
            self.direction.x * self.speed * time_passed,
            self.direction.y * self.speed * time_passed)
        
        self.pos += displacement
        self.rect.left = self.pos.x
        self.rect.top = self.pos.y
        
        # When the image is rotated, its size is changed.
        # We must take the size into account for detecting 
        # collisions with the walls.
        #
        
        
        self.image_w, self.image_h = self.image.get_size()
        bounds_rect = self.screen.get_rect().inflate(
                        -self.image_w, -self.image_h)
        
        if self.pos.x < bounds_rect.left:
            self.pos.x = bounds_rect.left
            self.direction.x *= -1
        elif self.pos.x > bounds_rect.right:
            self.pos.x = bounds_rect.right
            self.direction.x *= -1
        elif self.pos.y < bounds_rect.top:
            self.pos.y = bounds_rect.top
            self.direction.y *= -1
        elif self.pos.y > bounds_rect.bottom:
            self.pos.y = bounds_rect.bottom
            self.direction.y *= -1
    
    def blitme(self):
        """ Blit the creep onto the screen that was provided in
            the constructor.
        """
        # The creep image is placed at self.pos.
        # To allow for smooth movement even when the creep rotates
        # and the image size changes, its placement is always
        # centered.
        #
        draw_pos = self.image.get_rect().move(
            self.pos.x - self.image_w / 2, 
            self.pos.y - self.image_h / 2)
        self.screen.blit(self.image, draw_pos)
           
    #------------------ PRIVATE PARTS ------------------#
    
    _counter = 0
    
    def _change_direction(self, time_passed):
        """ Turn by 45 degrees in a random direction once per
            0.4 to 0.5 seconds.
        """
        self._counter += time_passed
        if self._counter > random.randint(400, 500):
            self.direction.rotate(45 * random.randint(-1, 1))
            self._counter = 0
#---------------------------------------------------
#------------------------------------------------------------------------------
class Hero(Character):
    def __init__(self, game):
        super(Hero, self).__init__(game, "hero.png", 10, game.screen_height/2, 1)

#------------------------------------------------------------------------------
class Maze:
    def __init__(self, walls = None):
        self.walls = walls if walls else []
    def add_wall(self, wall):
        self.walls.append(wall)

class Wall:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        
#------------------------------------------------------------------------------
 
class Game:
    def __init__(self, screen_width, screen_height, bg_color):
        pygame.init()
        self.screen = pygame.display.set_mode(
                (screen_width, screen_height), 0, 32)
        self.clock = pygame.time.Clock()
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.bg_color = bg_color
        
        # Create N_CREEPS random creeps.
        self.creeps = []    
        self.hero = None
        self.maze = None

        self.running = True
        
    def place_maze(self, maze):
        self.maze = maze
        
    def add_creep(self, creep):
        self.creeps.append(creep)
    
    def add_hero(self, hero):
        self.hero = hero    
    
    def start(self):
        while self.running:
            time_passed = self.clock.tick(200)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_game()
                elif event.type == pygame.KEYDOWN:
                    self.hero.keydown(event)
                elif event.type == pygame.KEYUP:
                    self.hero.keyup(event)
        
            # Redraw the background
            self.screen.fill(self.bg_color)
            
            # Update and redraw all creeps
            for creep in self.creeps:
                creep.update(time_passed)
                if pygame.sprite.collide_circle(creep, self.hero):
                    self.running = False
                creep.blitme()

            #draw walls
            if self.maze:
                for wall in self.maze.walls:
                    pygame.draw.rect(self.screen, pygame.color.Color(110,20,30), wall.rect, 0)
                    if pygame.sprite.collide_rect(wall, self.hero):
                        self.hero.move_back()

            self.hero.blitme()

            pygame.display.flip()

    def exit_game(self):
        sys.exit()
    

#------------------------------------------------------------------------------
def run():
    screen_width    = 800
    screen_height   = 600
    bg_color        = (100, 150, 150)
    
    game = Game(screen_width, screen_height, bg_color)
    
    n_creeps = 10
    for i in range(n_creeps):
        creep = Creep(
                      game.screen,
                      "graycreep.png",
                      (   random.randint(0, screen_width), 
                          random.randint(0, screen_height)),
                      (random.choice((-1,1)), random.choice((-1,1))),
                      0.1
                      )
        game.add_creep(creep)
    
    hero = Hero(game)
    game.add_hero(hero)
    
    walls = [
             Wall(100,100,10, 100),
             Wall(100,200,100, 10),
             #Wall(120,30,-50, 0),
            # Wall(10,70,80, 20)
             ]
    maze = Maze(walls)
    
    game.place_maze(maze)
    
    game.start()
    
run()