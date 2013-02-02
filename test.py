import maze
import vec2d
import pygame

class Game:
    def __init__(self, screen_width, screen_height):
        self.screen_height = screen_height
        self.screen_width = screen_width
        
class Rect:
    top = 0
    left = 0
    bottom = 30
    right = 30
    
class Image:
    def get_rect(self):
        image = Rect()
        return image
    
pygame.init()  
screen_width = 500
screen_height = 500
pygame.display.set_mode((screen_width, screen_height), 0, 32)  
c = maze.Character(Game(screen_width, screen_height), "hero.png", 0, 0, 10)
tests = {
         "Top Left" : (0, 0),
         "Top Center" : (screen_width/2, 0),
         "Top Right" : (screen_width - c.image.get_rect().right, 0),
         "Middle Left" : (0, screen_height/2),
         "Middle Right" : (screen_width - c.image.get_rect().right, screen_height/2),
         "Bottom Left" : (0, screen_height - c.image.get_rect().bottom),
         "Bottom Center" : (screen_width/2, screen_height - c.image.get_rect().bottom),
         "Bottom Right" : (screen_width - c.image.get_rect().right, screen_height - c.image.get_rect().bottom)
         }

for test, coord in tests.items():
    c = maze.Character(Game(screen_width, screen_height), "hero.png", coord[0], coord[1], 10)
    print "\n\n\n----------------------------------\n" + test + "\n----------------------------------\n"
    print "up, left : " + str(c.can_move("up, left") )
    print "up : " + str(c.can_move("up") )
    print "up, right : " + str(c.can_move("up, right") )
    print "left : " + str(c.can_move("left") )
    print "right : " + str(c.can_move("right"))
    print "down, left : " + str(c.can_move("down, left"))
    print "down : " + str(c.can_move("down"))
    print "down, right : " + str(c.can_move("down, right"))
