from enum import Enum
import numpy as np
from Board import Board
from Request import Request, RequestType, MoveUnitsRequest, PlaceUnitsRequest
from Action import Action
from players.Player import Player
import players.Utility as Utility


class PragmaticRandom(Player):

    def __init__(self, id, seed=0):

        super().__init__(id)
        if seed is None:
            self.rng = np.random.default_rng(seed)
        else:
            self.rng = np.random.default_rng(seed)

    def placeUnits(self, board: Board, numUnits) -> PlaceUnitsRequest:

        myPositions: np.ndarray = np.nonzero(board.ownership == self.id)[0]
        unitIndices = self.rng.choice(myPositions, numUnits, replace=True)
        unitsToAdd = np.zeros(board.size, dtype=int)
        np.add.at(unitsToAdd, unitIndices, 1)
        return PlaceUnitsRequest(unitsToAdd)

    def chooseMove(self, board: Board) -> Request:

        if board.moves == 0:
            return self.placeUnits(board,board.budget)

        if np.all(board.ownership == self.id):
            return Request(RequestType.QUIT_TURN)
        myUnits = np.nonzero(board.moveableUnits[:, self.id] > 0)[0]
        for u in myUnits:

            neighbors = board.getNeighbors(u)
            enemyContact = False
            for v in neighbors:
                if board.ownership[v] != self.id:
                    enemyContact = True
                    if board.units[v].sum() < 0.7 * board.moveableUnits[u, self.id]:
                        return MoveUnitsRequest(u, v, board.moveableUnits[u, self.id])

            if not enemyContact:
                return MoveUnitsRequest(u, Utility.findPath(board,self.id,u),board.moveableUnits[u, self.id])


        return Request(RequestType.QUIT_TURN)

    def giveFeedback(self, action: Action):

        pass
