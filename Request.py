from enum import Enum
import numpy as np

class RequestType(Enum):
    QUIT_TURN = 0
    PLACE_UNITS = 1
    MOVE_UNITS = 2


class Request:

    def __init__(self, requestType: RequestType) -> None:

        self.requestType = requestType

class MoveUnitsRequest(Request):

    def __init__(self, origin, target, numUnits) -> None:

        super().__init__(RequestType.MOVE_UNITS)

        self.origin = origin
        self.target = target
        self.numUnits = numUnits

class PlaceUnitsRequest(Request):

    def __init__(self, newUnits:np.ndarray):

        super().__init__(RequestType.PLACE_UNITS)

        self.newUnits = newUnits