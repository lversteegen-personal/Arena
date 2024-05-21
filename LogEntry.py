from Action import Action

class LogEntry:

    EntryCount = 0

    def __init__(self, board, change, turn):

        self.board = board
        self.change = change
        self.entryId = LogEntry.EntryCount
        self.turn = turn
        LogEntry.EntryCount += 1


    def __str__(self) -> str:
        
        return str(self.change)
