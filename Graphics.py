import pygame
from pygame.locals import *
from Board import Board
import itertools
import Data

player_colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255),(0,255,255)]
tile_width, tile_height = 100,100
sword_x,sword_y = 10,36
font_x, font_y = 50, 50

class Graphics:
    def __init__(self, screen):
        self.screen = screen
        self.warriorImage = pygame.image.load('images/sword.png').convert()
        self.warriorImage.set_colorkey((255,255,255))

        self.font = pygame.font.Font(None, 30)
        self.textColor = (0,0,0)

        Data.BOARD_WIDTH, Data.BOARD_HEIGHT = Data.BOARD_WIDTH, Data.BOARD_HEIGHT

    def drawBoard(self, board:Board):
        screen = self.screen
        screen.fill((255,255,255))

        units = board.units.sum(axis=1).reshape((Data.BOARD_WIDTH,Data.BOARD_HEIGHT))
        ownership = board.ownership.reshape((Data.BOARD_WIDTH,Data.BOARD_HEIGHT))

        for (x,y) in itertools.product(range(Data.BOARD_WIDTH),range(Data.BOARD_HEIGHT)):
            pygame.draw.rect(screen, color=player_colors[ownership[y,x]], rect=(x*tile_width,y*tile_height,tile_width,tile_height))
            if(units[y,x] != 0):
                screen.blit(self.warriorImage, (x*tile_width+sword_x,y*tile_height+sword_y))
                self.drawText("x "+str(units[y,x]),screen,x*tile_width+font_x,y*tile_height+font_y)
                    
            pygame.draw.rect(screen, (0,0,0), (x*tile_width,y*tile_height,tile_width,tile_height),1)

        pygame.display.flip()

    def drawText(self, text, screen, x , y):
        text_surface = self.font.render(text, False, self.textColor)
        text_rect = text_surface.get_rect()
        text_rect.midleft = (x, y)
        screen.blit(text_surface, text_rect)