class ASTAR:
    def __init__(self,start:object, goal:object, map, heuristic):
        self.map = map
        self.start = start
        self.goal = goal
        if heuristic ==1:
            self.heuristic = 1
        else:
            self.heuristic = 2