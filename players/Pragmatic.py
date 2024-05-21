from enum import Enum
import numpy as np
from Board import Board
from Request import Request, RequestType, MoveUnitsRequest, PlaceUnitsRequest
from Action import Action
from players.Player import Player
import players.Utility as Utility
import players.PlacingNetwork as PlacingNetwork
import Estimator
import BoardEncoder

class Pragmatic(Player):

    def __init__(self, id, seed=0):

        super().__init__(id)
        if seed is None:
            self.rng = np.random.default_rng(seed)
        else:
            self.rng = np.random.default_rng(seed)

        self.estimator = Estimator.build()
        self.placing_network = PlacingNetwork.build(self.estimator)

    def placeUnits(self, board: Board, numUnits) -> PlaceUnitsRequest:

        encoded = BoardEncoder.encodeBoard(board)
        weights = self.placing_network(encoded[None,:])[0]
        ownershipMask = board.ownership == self.id
        myPositions: np.ndarray = np.nonzero(ownershipMask)[0]
        unitsToAdd = np.rint(weights * numUnits).astype(int) * ownershipMask
        
        balance = numUnits-unitsToAdd.sum()
        if balance >0:
            unitIndices = self.rng.choice(myPositions, balance, replace=True)
            np.add.at(unitsToAdd, unitIndices, 1)
        elif balance <0:
            reducePositions = np.nonzero(unitsToAdd)[0]
            unitIndices = self.rng.choice(reducePositions, -balance, replace=False)
            np.add.at(unitsToAdd, unitIndices, -1)

        return PlaceUnitsRequest(unitsToAdd)

    def train(self, logEntriesPerGame, estimatorEpochs=1,placingEpochs=1):

        xListEstimator = []
        yList = []
        xListPlacing = []

        for gameEntries in logEntriesPerGame:

            for e in gameEntries:
                encoded = BoardEncoder.encodeBoard(e.board)
                xListEstimator.append(encoded)
                if e.board.budget>0:
                    xListPlacing.append(encoded)

            finalBoard : Board = gameEntries[-1].board
            outcome = np.sum(np.arange(finalBoard.num_players)[:,None] == finalBoard.ownership[None,:],axis=1) / finalBoard.size
            yList.extend([outcome]*len(gameEntries))

        xEstimator = np.array(xListEstimator)
        xPlacing = np.array(xListPlacing)
        y = np.array(yList)

        split = y.shape[0] //10 *9
        x_train = xEstimator[:split]
        y_train = y[:split]
        x_test = xEstimator[split:]
        y_test = y[split:]

        self.estimator.fit(x_train,y_train,batch_size=32,epochs = estimatorEpochs,validation_data=(x_test,y_test))

        self.placing_network.fit(xPlacing, epochs = placingEpochs)


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
