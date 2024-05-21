import pygame
from pygame.locals import *
import Graphics
from Game import Game

class App:
    def __init__(self, game : Game, replay :bool = True):

        self.game = game
        self.replay = replay
        self.replayFrame = 0

        self._running = True
        self._display_surf = None
        self.size = self.weight, self.height = 500, 500
 
    def on_init(self):
        pygame.init()
        _display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True
        self.graphics = Graphics.Graphics(_display_surf)
 
    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
            if self.replay:
                if self.replayFrame < len(self.game.logEntries)-1:
                    print(str(self.game.logEntries[self.replayFrame]))
                    self.replayFrame += 1
            else:
                self.game.playTurn()

    def on_loop(self):
        pass

    def on_render(self):
        if self.replay:
            self.graphics.drawBoard(self.game.logEntries[self.replayFrame].board)
        else:
            self.graphics.drawBoard(self.game.board)
        
    def on_cleanup(self):
        pygame.quit()
 
    def on_execute(self):
        if self.on_init() == False:
            self._running = False
 
        while( self._running ):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()