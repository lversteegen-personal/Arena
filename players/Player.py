from enum import Enum
import numpy as np
from Board import Board
from Request import Request, RequestType, MoveUnitsRequest, PlaceUnitsRequest
from Action import Action

#The base class for players behaving completely passively
class Player:

    def __init__(self, id):
        
        self.id = id

    def setup(self, board:Board):

        pass

    def chooseMove(self, board:Board) -> Request:

        return Request(RequestType.QUIT_TURN)

    def giveFeedback(self, action: Action):

        pass