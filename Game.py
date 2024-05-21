from Board import Board
from players.Player import Player
from players.RandomPlayer import RandomPlayer
from Action import *
from Request import *
from LogEntry import LogEntry
from Data import *
import numpy as np

class Game:

    def __init__(self, players, seed = 0):
        self.players = players
        self.board = Board.randomSetup(len(players), seed)

        if seed is None:
            self.rng = np.random.default_rng(seed)
        else:
            self.rng = np.random.default_rng(seed)
        self.logEntries = []
        self.survivingPlayers = len(players)
        self.turns = 0

        for p in self.players:
            p.setup(self.board.copy())

    def playTurn(self):

        while self.move():
            pass

    def move(self):

        board = self.board
        playerId = board.turnId
        p : Player = self.players[playerId]

        if board.moves == 0:
            board.refreshUnits()
            tilesOwned = np.count_nonzero(self.board.ownership == playerId)
            board.budget = BASE_UNITS_PER_TURN + int(UNITS_PER_TILE*tilesOwned)

        request = p.chooseMove(self.board.copy())
        preBoard = self.board.copy()

        action = None

        if request.requestType == RequestType.QUIT_TURN:
            action = QuitTurn(playerId,request)
        elif request.requestType == RequestType.PLACE_UNITS:
            action = self.processPlaceUnitsRequest(playerId, request)
        elif request.requestType == RequestType.MOVE_UNITS:
            action = self.processMoveRequest(playerId, request)

        p.giveFeedback(action)
        self.logEntries.append(LogEntry(preBoard, action, self.turns))

        board.moves += 1
        if board.moves == MAX_MOVES or isinstance(action, QuitTurn) or isinstance(action,RequestDenial):
            self.survivingPlayers = np.unique(self.board.ownership).size
            self.logEntries.append(LogEntry(self.board.copy(),f"End of turn for {PlayerString(playerId)}. {self.survivingPlayers} players survive.", self.turns))
            self.turns += 1
            board.moves = 0
            board.turnId = (board.turnId+1)%board.num_players
            return False
        else:
            return True

    def processMoveRequest(self, playerId, request:MoveUnitsRequest) -> Action:

        board = self.board
        playerString = PlayerString(playerId)

        origin = request.origin
        target = request.target
        numUnits = request.numUnits

        if board.ownership[origin] != playerId:
            return RequestDenial(playerId, request, f"{playerString} tried to move units from a tile that was not owned.")
        elif origin == target:
            return RequestDenial(playerId, request, f"{playerString} tried to move units from tile to itself.")
        elif not board.nodesAdjacent(origin,target):
            return RequestDenial(playerId, request, f"{playerString} tried to move units between non-adjacent tiles.")
        elif board.moveableUnits[origin, playerId] < numUnits:
            return RequestDenial(playerId, request, f"{playerString} tried to move more units than may be moved from origin tile.")
        elif board.ownership[target] == playerId:
            board.moveUnits(origin, target, playerId, numUnits)
            return UnitTransfer(playerId, request)
        elif board.ownership[target] == -1:
            board.moveUnits(origin, target, playerId, numUnits)
            return OccupyNeutral(playerId, request)
        else:
            defenderId = board.ownership[target]

            numDefenders = board.units[target, defenderId]
            numAttackers = numUnits #min(numUnits, COMBAT_WIDTH_RATIO * (1+numDefenders))
            damageAtkOnDef = round(np.exp(self.rng.normal(
                LOG_ATK_DAMAGE_AVG_PER_UNIT, LOG_ATK_DAMAGE_STDV_PER_UNIT))*numAttackers)
            damageDefOnAtk = round(np.exp(self.rng.normal(
                LOG_DEF_DAMAGE_AVG_PER_UNIT, LOG_DEF_DAMAGE_STDV_PER_UNIT))*numDefenders)

            board.killUnits(target,defenderId, damageAtkOnDef)
            board.killUnits(origin,playerId, damageDefOnAtk)
            defendersLeft = max(0,numDefenders-damageAtkOnDef)
            attackersLeft = max(0,numAttackers-damageDefOnAtk)


            if attackersLeft > 0 and defendersLeft <= 0:
                board.moveUnits(origin,target,playerId, numUnits-damageDefOnAtk)
                return Attack(playerId,request,defenderId,Attack.Outcome.ATTACKERS_WON,numAttackers,numDefenders,attackersLeft,defendersLeft)

            elif defendersLeft > 0:

                board.moveUnits(origin,origin,playerId, numUnits-damageDefOnAtk)
                return Attack(playerId,request,defenderId,Attack.Outcome.DEFENDERS_WON,numAttackers,numDefenders,attackersLeft,defendersLeft)

            elif attackersLeft <= 0 and defendersLeft <= 0:

                board.moveUnits(origin,origin,playerId, numUnits-damageDefOnAtk)
                return Attack(playerId,request,defenderId,Attack.Outcome.NO_SURVIVORS,numAttackers,numDefenders,attackersLeft,defendersLeft)

    def processPlaceUnitsRequest(self,playerId:int, request:PlaceUnitsRequest)-> Action:

        p : Player = self.players[playerId]
        newUnits = request.newUnits
        totalUnits = newUnits.sum()

        if totalUnits > self.board.budget:
            return RequestDenial(playerId, request, "Requested more units than permitted. No units were placed.")
        else:
            if np.any(newUnits[self.board.ownership != playerId].nonzero()):
                newUnits[self.board.ownership != playerId] = 0

            self.board.units[:,playerId] += newUnits
            self.board.moveableUnits[:,playerId] += newUnits
            self.board.budget -= totalUnits
            return PlaceUnits(playerId, request, self.board.budget, newUnits)
