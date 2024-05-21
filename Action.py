from Data import PlayerString, NODE_NAMES
from Request import Request, MoveUnitsRequest, PlaceUnitsRequest, RequestType
import numpy as np
from enum import Enum

class Action:

    def __init__(self, playerId, request: Request):

        self.playerId = playerId
        self.playerString = PlayerString(self.playerId)
        self.request = request

        # if self.request.requestType == RequestType.PLACE_UNITS:
        #     self.phase = Action.Phase.UNIT_PLACEMENT
        # else:
        #     self.phase = Action.Phase.MAIN_ACTION


class RequestDenial(Action):

    def __init__(self, playerId: int, request: Request, reason):
        super().__init__(playerId, request)
        self.reason = reason

    def __str__(self) -> str:
        return f"{self.playerString} made the following request:\n {self.request}\n The request was denied for the following reason:\n {self.reason}"

class QuitTurn(Action):

    def __init__(self, playerId: int, request: Request):
        super().__init__(playerId, request)

    def __str__(self) -> str:
        return f"{self.playerString} opted to end their turn."


class PlaceUnits(Action):

    def __init__(self, playerId: int, request: PlaceUnitsRequest, budget: int, newUnits: np.ndarray):
        super().__init__(playerId, request)

        self.newUnits = newUnits
        self.unitsPlaced = newUnits.sum()
        self.budget = budget

    def __str__(self) -> str:
        return f"{self.playerString} placed {self.unitsPlaced} units and may place {self.budget} more units this turn."


class UnitTransfer(Action):

    def __init__(self, playerId, request: MoveUnitsRequest):
        super().__init__(playerId, request)
        self.numUnits = request.numUnits
        self.origin = request.origin
        self.target = request.target

    def __str__(self) -> str:
        return f"{self.playerString} moved {self.numUnits} units from {NODE_NAMES[self.origin]} to {NODE_NAMES[self.target]}."


class OccupyNeutral(Action):

    def __init__(self, playerId, request: MoveUnitsRequest):
        super().__init__(playerId, request)
        self.playerId = request.playerId
        self.numUnits = request.numUnits
        self.origin = request.origin
        self.target = request.target

    def __str__(self) -> str:
        return f"{self.playerString} moved {self.numUnits} units from {NODE_NAMES[self.origin]} to {NODE_NAMES[self.target]}. Occupied new tile."


class Attack(Action):

    class Outcome(Enum):

        ATTACKERS_WON = 0
        DEFENDERS_WON = 1
        NO_SURVIVORS = 2

    def __init__(self, playerId: int, request: MoveUnitsRequest, defenderId: int, outcome: Outcome, activeAttackers: int, numDefenders, attackersLeft: int, defendersLeft: int):
        super().__init__(playerId, request)

        self.origin = request.origin
        self.target = request.target
        self.numAttackers = request.numUnits

        self.defenderId = defenderId

        self.outcome = outcome
        self.activeAttackers = activeAttackers
        self.numDefenders = numDefenders
        self.attackersLeft = attackersLeft
        self.defendersLeft = defendersLeft

    def __str__(self) -> str:

        if self.outcome == Attack.Outcome.ATTACKERS_WON:
            return f"{self.playerString} sent {self.numAttackers} units from {NODE_NAMES[self.origin]} to conquer {NODE_NAMES[self.target]} "\
                    f"from {PlayerString(self.defenderId)}, which was defended by {self.numDefenders} units.\n"\
                     f"The attackers won. {self.numAttackers} attackers participated in the fight, and {self.attackersLeft} of them survived."

        elif self.outcome == Attack.Outcome.DEFENDERS_WON:
            return f"{self.playerString} sent {self.numAttackers} units from {NODE_NAMES[self.origin]} to conquer {NODE_NAMES[self.target]} "\
                    f"from {PlayerString(self.defenderId)}, which was defended by {self.numDefenders} units.\n"\
                     f"The attack was repelled, with {self.defendersLeft} defenders surviving.\n"\
                     f"{self.numAttackers} attackers participated in the fight, and {self.attackersLeft} of them survived."
        elif self.outcome == Attack.Outcome.NO_SURVIVORS:
            return f"{self.playerString} sent {self.numAttackers} units from {NODE_NAMES[self.origin]} to conquer {NODE_NAMES[self.target]} "\
                f"from {PlayerString(self.defenderId)}, which was defended by {self.numDefenders} units.\n"\
                     f"There was a stalemate because neither side had survivors."
        else:
            raise(ValueError())
