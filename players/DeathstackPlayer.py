from enum import Enum
import numpy as np
from Board import Board
from Request import Request, RequestType, MoveUnitsRequest, PlaceUnitsRequest
from Action import *
from players.Player import Player

class DeathstackPlayer(Player):

    def __init__(self, id, seed=0):
        
        super().__init__(id)

        self.deathstackNode = None
        if seed is None:
            self.rng = np.random.default_rng(seed)
        else:
            self.rng = np.random.default_rng(seed)
        self.moved = False

    def placeUnits(self, board : Board, numUnits) -> PlaceUnitsRequest:

        myPositions : np.ndarray = np.nonzero(board.ownership == self.id)[0]
        if self.deathstackNode is None or board.ownership[self.deathstackNode] != self.id:
            self.deathstackNode = myPositions[0]

        unitsToAdd = np.zeros(board.size,dtype=int)
        unitsToAdd[self.deathstackNode] = numUnits

        self.moved = False

        return PlaceUnitsRequest(unitsToAdd)

    def chooseMove(self, board:Board) -> Request:

        if board.moves == 0:
            return self.placeUnits(board,board.budget)

        units = board.moveableUnits[self.deathstackNode, self.id]
        if units == 0 or self.moved:
            return Request(RequestType.QUIT_TURN)

        neighbors = board.getNeighbors(self.deathstackNode)
        for v in neighbors:
            if board.ownership[v] != self.id:
                return MoveUnitsRequest(self.deathstackNode,v,units)

        self.moved = True

        return MoveUnitsRequest(self.deathstackNode,self.rng.choice(neighbors),units)

    def giveFeedback(self, action: Action):

        if action.request.requestType == RequestType.MOVE_UNITS:
            if isinstance(action,OccupyNeutral) or isinstance(action,UnitTransfer):
                self.deathstackNode = action.target
            if isinstance(action,Attack) and action.outcome == Attack.Outcome.ATTACKERS_WON:
                self.deathstackNode = action.target