# encoding: utf-8
'''
Created on 2018年10月4日

@author: winston
'''
import copy
import glob
import os

import numpy
import pygame, random


pygame.font.init() 
myfont = pygame.font.Font(pygame.font.get_default_font(), 10)
# textsurface = myfont.render('Some Text', False, (0, 0, 0))

SCREENWIDTH=800
SCREENHEIGHT=600


GREEN = (20, 255, 140)
GREY = (210, 210 ,210)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
PURPLE = (255, 0, 255)

base_path = '/backup/books/tmp/m/reanim/'
images = glob.glob(base_path + "*.png")
images.sort()

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

def renderTextCenteredAt(text, font, colour, x, y, screen, allowed_width):
    # first, split the text into words
    words = text.split()

    # now, construct lines out of these words
    lines = []
    while len(words) > 0:
        # get as many words as will fit within allowed_width
        line_words = []
        while len(words) > 0:
            line_words.append(words.pop(0))
            fw, fh = font.size(' '.join(line_words + words[:1]))
            if fw > allowed_width:
                break

        # add a line consisting of those words
        line = ' '.join(line_words)
        lines.append(line)

    # now we've split our text into lines that fit into the width, actually
    # render them

    # we'll render each line below the last, so we need to keep track of
    # the culmative height of the lines we've rendered so far
    y_offset = 0
    for line in lines:
        fw, fh = font.size(line)

        # (tx, ty) is the top-left of the font surface
        tx = x - fw / 2
        ty = y + y_offset

        font_surface = font.render(line, True, colour)
        screen.blit(font_surface, (tx, ty))

        y_offset += fh
class BaseSprite(pygame.sprite.Sprite):
    def onClicked(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())
    
    def isSelected(self):
        return self.index == 1

    def isAtLeft(self):
        return self.rect.x < 400
    
#     def update(self, *args):
#         index = self.index
#         if self.rect.x >= 400:
#             index = index + 1
#         self.image = self.image_list[index]
#         self.rect.width = self.image.get_width()
#         self.rect.height = self.image.get_height()
#         
#         pygame.sprite.Sprite.update(self, *args)
        
    def moveUp(self, pixels):
        self.moveXy(0, -pixels)

    def moveDown(self, pxiels):
        self.moveXy(0, pxiels)
    
    def moveRight(self, pixels):
        self.moveXy(pixels, 0)

    def moveLeft(self, pixels):
        self.moveXy(-pixels, 0)
        
    def moveXy(self, x, y):
        self.rect.x += x
        self.rect.y +=y
        self.rect.x = min(max(self.rect.x, 0),SCREENWIDTH - self.rect.width) 
        self.rect.y = min(max(self.rect.y, 0),SCREENHEIGHT - self.rect.height)

    def onSelected(self, selected=False):
        self.index = selected

        index = self.index
        if self.rect.x >= 400:
            index = index + 1
        self.image = self.image_list[index]
        self.rect.width = self.image.get_width()
        self.rect.height = self.image.get_height()
        self.update()

    def onDragDrop(self, event):
        self.moveXy(*event.rel)


class MySprite(BaseSprite):
    #This class represents a car. It derives from the "Sprite" class in Pygame.
    
    def __init__(self, image_fname=None):
        # Call the parent class (Sprite) constructor
#         super(pygame.sprite.Sprite, self).__init__()
        pygame.sprite.Sprite.__init__(self)
        self.index = 0
        self.image_list = []
        
        if image_fname is None:
            return
        
        self.image, self.rect = load_png(image_fname)
        
#         self.image_list.append(self.image.copy())
        
        image_icon = pygame.surface.Surface((100, 100))
        w = self.rect.width
        h = self.rect.height
        x = (100 - w) / 2
        y = (100 - h) / 2
        image_icon.blit(self.image, (x,y))
        
        text = os.path.basename(image_fname)[:-4].replace('_', ' ')
        
#         renderTextCenteredAt(text, myfont, WHITE, 0, self.rect.height, image_icon, self.rect.width)
        
        text = myfont.render(text, False, WHITE)
        w, h = text.get_width(), text.get_height()
        
        x = (100 - w) / 2
        
        y = (y - h) / 2 + 100 - y
        
        image_icon.blit(text, (x, y))

        
        
        
        
        image_raw = self.image.copy()
        
        pygame.draw.rect(self.image, RED, self.rect, 1)
        
        image_selected = self.image
         
        self.image_list.append(image_icon)
        self.image_list.append(image_raw)
        self.image_list.append(image_selected)
        self.onSelected(False)
        
        
#         self.image_list.append(self.image.)
#         pygame.draw.rect(self.image, color, self.rect, 1)
#         pygame.draw.rect(self.image, color, [0, 0, width, height])
    
    def clone(self):
        new_sprite = MySprite()
        new_sprite.index = self.index
        new_sprite.image_list = self.image_list
        new_sprite.rect = copy.copy(self.rect)
        new_sprite.image = self.image
        
        return new_sprite
    

        


class MySpriteList(pygame.sprite.LayeredUpdates):
    def __init__(self):
        pygame.sprite.LayeredUpdates.__init__(self)
        self.selected = None
    
    def onSelected(self):
        self.selected = None
        for x in self:
            if self.selected is None and x.onClicked():
                self.selected = x
                self.move_to_front(x)
                x.onSelected(True)
            else:
                x.onSelected(False)
                
#         print self.selected, self.selected.isAtLeft()
        if self.selected is not None and self.selected.isAtLeft():
            selected_cloned = self.selected.clone()
#             print id(self.selected), id(selected_cloned)  
            self.selected.onSelected(False)
            selected_cloned.onSelected(True)
            
            x = (self.selected.rect.width - selected_cloned.rect.width) / 2
            y = (self.selected.rect.height - selected_cloned.rect.height) / 2
#             print x, y
            selected_cloned.moveXy(x,y)
            self.selected = selected_cloned
            self.add(self.selected)
            
        
    def clearAllLeft(self):
        for x in self:
            if x.isAtLeft():
                self.remove(x)
    
    def onDragDrop(self, event):
        if self.selected:
            self.selected.onDragDrop(event)
            
            if isinstance(self.selected, ScrollBar):
                self.clearAllLeft()
                self.add_sprites_by_images(self.selected.getViewPortFiles())
    
    def add_and_move_to_position(self, sprite):
#         print sprites, kwargs
#         assert len(sprites) == 1
        n = len(self)
        y = (n / 4) * 100
        x = (n % 4) * 100
        sprite.moveXy(x,y)
        pygame.sprite.LayeredUpdates.add(self, sprite)
        
    def add_sprites_by_images(self, fnames):
        for x in fnames:
            self.add_and_move_to_position(MySprite(x))
        
class ScrollBar(BaseSprite):
    def __init__(self, file_list):
        self.file_list = file_list
        self.index = 0
        self.image_list = []
        self.h = h = 600 * 24.0/ len(file_list)
#         print "高度是:", h
        image = pygame.surface.Surface((10, h))
        self.rect = pygame.Rect(0, 0, 10, h)
        
        image_icon = image.copy()
        
        pygame.draw.rect(image_icon, GREY, self.rect, 0)
        image_selected = image.copy()
        pygame.draw.rect(image_selected, RED, self.rect, 0)
        self.image_list.append(image_icon)
        self.image_list.append(image_icon)
        self.image_list.append(image_selected)
        self.image = image_icon
        
        self.rect.x = 401
        pygame.sprite.Sprite.__init__(self)
        
    def getViewIndex(self):
        y = self.rect.y + self.h
        i = int(y/self.h) - 1
        return i * 24
        
    def getViewPortFiles(self):
        i = self.getViewIndex()
        return self.file_list[i:i+24]
    
    def isSelected(self):
        return False

    def onDragDrop(self, event):
        self.moveXy(0, event.rel[1])
        
            
pygame.init()

        

size = (SCREENWIDTH, SCREENHEIGHT)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("精灵制作 @状牛软件!")

#This will be a list that will contain all the sprites we intend to use in our game.

scrollbar = ScrollBar(images)

all_sprites_list = MySpriteList()

all_sprites_list.add(scrollbar)

all_sprites_list.add_sprites_by_images(images[:24])
print images[0]
# all_sprites_list.add_sprites_by_images(scrollbar.getViewPortFiles())



# helmet = MySprite("/backup/books/tmp/m/reanim/GatlingPea_helmet.png")
# 
# head = MySprite("/backup/books/tmp/m/reanim/GatlingPea_head.png")
# 
# mouth = MySprite("/backup/books/tmp/m/reanim/GatlingPea_mouth.png")


# all_sprites_list.add_and_move_to_position(head)
# all_sprites_list.add_and_move_to_position(mouth)
# all_sprites_list.add_and_move_to_position(helmet)


#Allowing the user to close the window...
carryOn = True
clock=pygame.time.Clock()

while carryOn:
        sprite_selected = None     
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                carryOn=False
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_x: #Pressing the x Key will quit the game
                    carryOn=False
            elif event.type == pygame.MOUSEBUTTONUP:
                if all_sprites_list.selected is not None and all_sprites_list.selected.isAtLeft():
                    x = all_sprites_list.selected
                    x.onSelected(False)
                    all_sprites_list.remove(x)
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                all_sprites_list.onSelected()
                
#                 print 'mouse down', pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEMOTION:
#                 if event.buttons[pygame.HAT_LEFTDOWN]
                if pygame.mouse.get_pressed()[0] == 1:
                    all_sprites_list.onDragDrop(event)
#                     print 'mouse motion', pygame.mouse.get_pos(), pygame.mouse.get_pressed()
#                     print 'mouse motion', event.rel
#                     sprite_dragdrop = None
#                     for x in all_sprites_list:
#                         if x.isDragDrop():
#                             x.moveXy(*event.rel)
#                             break
#                         
                        
                

        keys = pygame.key.get_pressed()
        
        
        sprite_selected = filter(lambda x:x.isSelected(), all_sprites_list)
         
        sprite_selected = sprite_selected[0] if sprite_selected else None
        
        pixles = 1
        
#         print sprite_selected
        if sprite_selected:
            if keys[pygame.K_LEFT]:
                sprite_selected.moveLeft(pixles)
            
            elif keys[pygame.K_RIGHT]:
                sprite_selected.moveRight(pixles)
                
            elif keys[pygame.K_UP]:
                sprite_selected.moveUp(pixles)
                
            elif keys[pygame.K_DOWN]:
                sprite_selected.moveDown(pixles)
        
        #Game Logic
        all_sprites_list.update()

        #Drawing on Screen
        screen.fill(GREEN)
        #Draw The Road
        pygame.draw.rect(screen, BLACK, [0,0, 400,600])
        
#         for i in range(3):
#             pygame.draw.line(screen, GREY, [100 * (i + 1),0],[100 * (i +1),600],1)
#             
#         for i in range(5):
#             pygame.draw.line(screen, GREY, [0, 100 * (i + 1)],[400, 100 * (i +1)],1)
            
        
#         pygame.draw.line(screen, GREY, [200,0],[200,600],1)
#         
#         pygame.draw.line(screen, GREY, [300,0],[300,600],1)
#         pygame.draw.line(screen, WHITE, [140,0],[140,300],5)
        
        #Now let's draw all the sprites in one go. (For now we only have 1 sprite!)
        all_sprites_list.draw(screen)

        #Refresh Screen
        pygame.display.flip()

        #Number of frames per secong e.g. 60
#         clock.tick(60)

pygame.quit() 