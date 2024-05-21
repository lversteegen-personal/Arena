import Game
from players.Player import Player
from players.RandomPlayer import RandomPlayer 
from players.DeathstackPlayer import DeathstackPlayer
from players.DeathstackPlayerV2 import DeathstackPlayerV2
from players.Pragmatic import Pragmatic
from App import App

players = [Pragmatic(0), Pragmatic(1)]
game = Game.Game(players,seed=1)

for t in range(200):
    game.playTurn()
    if game.survivingPlayers < 2:
        break

if __name__ == "__main__" :
    theApp = App(game, replay=True)
    theApp.on_execute()