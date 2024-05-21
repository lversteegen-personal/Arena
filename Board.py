import numpy as np
import itertools
from Data import adjacency, neighborhoods
from enum import Enum

class Board:

    def __init__(self, num_players, ownership, units, moveableUnits, turnId:int, moves:int, budget:int):

        self.size = adjacency.shape[0]

        self.num_players = num_players
        self.ownership: np.ndarray = ownership
        self.units: np.ndarray = units
        self.moveableUnits : np.ndarray = moveableUnits
        self.budget = budget
        self.moves = moves
        self.turnId = turnId

    def nodesAdjacent(self, origin, target):

        return adjacency[origin, target]

    def getNeighbors(self, node):

        return neighborhoods[node]

    def moveUnits(self, origin, target, playerId, numUnits):

        if numUnits > 0:
            self.units[origin, playerId] -= numUnits
            self.moveableUnits[origin, playerId] -= numUnits
            self.units[target, playerId] += numUnits
            self.ownership[target] = self.ownership[origin]

    def killUnits(self, node,playerId, numUnits):

        self.units[node, playerId] = max(0, self.units[node, playerId]-numUnits)
        self.moveableUnits[node, playerId] = max(0, self.moveableUnits[node, playerId]-numUnits)

    def refreshUnits(self, id=-1):

        if id == -1:
            id = self.turnId
        self.moveableUnits[:,id] = self.units[:,id].copy()

    def copy(self):

        b = Board(self.num_players,self.ownership.copy(), self.units.copy(),self.moveableUnits.copy(),
                  self.turnId, self.moves, self.budget)
        return b

    def randomSetup(num_players, seed=0):

        rng : np.random.default_rng = None
        if seed is None:
            rng = np.random.default_rng(seed)
        else:
            rng = np.random.default_rng(seed)

        size = adjacency.shape[0]

        ownership = rng.integers(0, num_players, size)
        units = np.zeros((size,num_players),dtype=int)
        np.put_along_axis(units,ownership[:,None],1,axis=1)

        b = Board(num_players, ownership, units, units.copy(),turnId=0,moves=0, budget=0)

        return b

    def nodesOwned(self, playerId):

        return np.count_nonzero(self.ownership == playerId)
