import os

import pygame

WHITE = (255, 255, 255)

def load_png(name):
    """ Load image and return image object"""
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    return image, image.get_rect()

class Car(pygame.sprite.Sprite):
    #This class represents a car. It derives from the "Sprite" class in Pygame.
    
    def __init__(self, color, width, height):
        # Call the parent class (Sprite) constructor
#         super(pygame.sprite.Sprite, self).__init__()
        pygame.sprite.Sprite.__init__(self)
        self.index = 0
        self.image_list = []
        
#         # Pass in the color of the car, and its x and y position, width and height.
#         # Set the background color and set it to be transparent
#         self.image = pygame.Surface([width, height])
#         self.image.fill(WHITE)
#         self.image.set_colorkey(WHITE)
#  
#         # Draw the car (a rectangle!)
        
#         
#         # Instead we could load a proper pciture of a car...
#         # self.image = pygame.image.load("car.png").convert_alpha()
#  
#         # Fetch the rectangle object that has the dimensions of the image.
#         self.rect = self.image.get_rect()

        self.image, self.rect = load_png('/backup/books/tmp/m/reanim/GatlingPea_head.png')
#         self.image_list.append(self.image.)
        pygame.draw.rect(self.image, color, self.rect, 1)
#         pygame.draw.rect(self.image, color, [0, 0, width, height])
    
    def onClicked(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            print 'clicked'

    def moveRight(self, pixels):
        self.rect.x += pixels

    def moveLeft(self, pixels):
        self.rect.x -= pixels