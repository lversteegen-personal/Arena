from enum import Enum
import numpy as np
from Board import Board
from Request import Request, RequestType, MoveUnitsRequest, PlaceUnitsRequest
from Action import Action
from players.Player import Player

class RandomPlayer(Player):

    def __init__(self, id, seed = 0):

        super().__init__(id)
        if seed is None:
            self.rng = np.random.default_rng(seed)
        else:
            self.rng = np.random.default_rng(seed)

    def placeUnits(self, board : Board, numUnits) -> PlaceUnitsRequest:

        myPositions : np.ndarray = np.nonzero(board.ownership == self.id)[0]
        unitIndices = self.rng.choice(myPositions,numUnits,replace=True)
        unitsToAdd = np.zeros(board.size,dtype=int)
        np.add.at(unitsToAdd,unitIndices, 1)
        return PlaceUnitsRequest(unitsToAdd)

    def chooseMove(self, board:Board) -> Request:

        if board.moves == 0:
            return self.placeUnits(board,board.budget)

        myUnits = np.nonzero(board.moveableUnits[:,self.id] > 0)[0]
        if myUnits.size == 0 or self.rng.integers(0,2) == 0:
            return Request(RequestType.QUIT_TURN)
        else:
            i = self.rng.integers(myUnits.size)
            origin = myUnits[i]

            N = board.getNeighbors(origin)
            target = N[self.rng.integers(len(N))]
            numUnits = board.moveableUnits[origin,self.id]
            return MoveUnitsRequest(origin,target,numUnits)

    def giveFeedback(self, action: Action):

        pass