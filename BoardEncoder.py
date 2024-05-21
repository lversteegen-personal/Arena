import numpy as np
from Game import Game
from Action import Action
from Board import Board
from LogEntry import LogEntry
from Data import adjacency, MAX_MOVES, num_players

rng = np.random.default_rng()

def getTrainingExample(game: Game):

    logEntries = game.logEntries
    sigma = rng.permutation(len(logEntries))#np.arange(0,len(logEntries),dtype=int)[::-1] 
    for i in range(len(logEntries)):
        entry = logEntries[sigma[i]]
        example = convertLogEntry(entry)
        if example is not None:
            return example

    return None

def getAllTrainingExamples(game: Game):

    logEntries = game.logEntries
    examples = []
    for entry in logEntries:
        example = convertLogEntry(entry)
        if example is not None:
            examples.append(example)

    return examples

def convertLogEntry(logEntry: LogEntry):

    if not isinstance(logEntry.change, Action):
        return None
    else:
        board : Board = logEntry.board
        return encodeBoard(board)

nodes = adjacency.shape[0]
index = 0
ownership_indicices = np.arange(index,index+nodes)
index += nodes
unit_indices = np.arange(index,index+nodes)
index+=nodes
moveable_unit_indices = np.arange(index,index+nodes)
index+=nodes

turnId_index = index
index += 1
moves_index = index
index += 1
budget_index = index
index += 1

index_length = index

def encodeBoard(board:Board):

    ownershipOneHot = (np.arange(board.num_players) == board.ownership[:,None])
    situation = np.zeros((3,board.num_players))
    situation[0,board.turnId] = 1.0
    situation[1,board.turnId] = board.moves / MAX_MOVES
    situation[2,board.turnId] = board.budget
    return np.concatenate((ownershipOneHot,board.units,board.moveableUnits,situation)).reshape(-1)

def decodeBoard(array: np.ndarray):

    array = array.reshape(-1,num_players)
    nodes = adjacency.shape[0]

    index = 0

    ownership = array[ownership_indicices].argmax(axis=1)
    index += nodes
    units = array[unit_indices]
    index+=nodes
    moveable_units = array[moveable_unit_indices]
    index+=nodes

    turnId = array[turnId_index].argmax()
    index += 1
    moves = round(array[moves_index].max()) / MAX_MOVES
    index += 1
    budget = round(array[budget_index].max())

    return Board(num_players,ownership,units,moveable_units,turnId,moves,budget)

