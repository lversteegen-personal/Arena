import numpy as np
from Board import Board

from Data import adjacency

distanceMatrix = None
pathMatrix = None

n = adjacency.shape[0]
distanceMatrix = np.ones(adjacency.shape, dtype=int) * n
pathMatrix = np.ones(adjacency.shape, dtype=int)

for u in range(n):
    distanceMatrix[u,u] = 0
    pathMatrix[u,u] = u
    for v in range(u+1,n):
        if adjacency[u,v]:
            distanceMatrix[u,v] = 1
            pathMatrix[u,v] = v
            distanceMatrix[v,u] = 1
            pathMatrix[v,u] = u

for k in range(n):
    for u in range(n):
        for v in range(u+1,n):
            if distanceMatrix[u,v] > distanceMatrix[u,k] + distanceMatrix[k,v]:
                distanceMatrix[u,v] = distanceMatrix[u,k] + distanceMatrix[k,v]
                pathMatrix[u,v] = pathMatrix[u,k]
                distanceMatrix[v,u] = distanceMatrix[u,k] + distanceMatrix[k,v]
                pathMatrix[v,u] = pathMatrix[v,k]

def findPath(board: Board, id :int, startingPoint):

    indices = np.argwhere(id != board.ownership)[:,0]
    target = indices[np.argmin(
        distanceMatrix[startingPoint, indices])]

    return pathMatrix[startingPoint, target]