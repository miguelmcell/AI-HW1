from OpenNero import *
from common import *

import Maze
from Maze.constants import *
import Maze.agent
from Maze.agent import *
import sys

class IdaStarSearchAgent(SearchAgent):
    cutoff = -1
    # Bug: Sometimes Revisits visited places twice for some reason 

    def manhattan_heuristic(r, c):
        return abs(ROWS - 1 - r) + abs(COLS - 1 - c)

    def dfs_action(self, observations):
        global cutoff

        r = observations[0]
        c = observations[1]
        current_cell = (r, c)
        # if we have not been here before, build a list of other places we can go
        if current_cell not in self.visited:
            tovisit = []
            for m, (dr, dc) in enumerate(MAZE_MOVES):
                r2, c2 = r + dr, c + dc
                if not observations[2 + m]: # can we go that way?
                    if (r2, c2) not in self.visited:
                        tovisit.append((r2, c2))
                        self.parents[(r2, c2)] = current_cell
            # remember the cells that are adjacent to this one
            self.adjlist[current_cell] = tovisit
        #  ^ This generates self.adjlist for the current cell index

        # if we have been here before, check if we have other places to visit
        adjlist = self.adjlist[current_cell]
        k = 0
        while k < len(adjlist) and adjlist[k] in self.visited:
            k += 1

        print("*****CUTOFF: " + str(cutoff) + " DISTANCE: " + str(self.get_distance(r,c)), k,len(adjlist))

        # if we don't have other neighbors to visit, back up
        # also applies when we have reached the cutoff value
        # When we arrive at the origin with no more paths left 
        if current_cell == self.starting_pos and k == len(adjlist):
            print("STARTING POINT!!!")
            cutoff+=2
            self.reset()
        elif k == len(adjlist):
            next_cell = self.parents[current_cell]
        elif self.get_distance(r,c) == cutoff:
            print("**** REACHED CUTOFF")
            next_cell = self.parents[current_cell]          
        else: # otherwise visit the next place
            next_cell = self.findBestAdjCell(adjlist,k)
            # next_cell = adjlist[k]
        self.visited.add(current_cell) # add this location to visited list
        if current_cell != self.starting_pos:
            get_environment().mark_maze_blue(r, c) # mark it as blue on the maze
        v = self.constraints.get_instance() # make the action vector to return
        dr, dc = next_cell[0] - r, next_cell[1] - c # the move we want to make
        v[0] = get_action_index((dr, dc))
        # remember how to get back
        if next_cell not in self.backpointers:
            self.backpointers[next_cell] = current_cell
        return v

    """
    Calculates best cell from adjlist based on manhattan heuristic
    """
    def findBestAdjCell(self, adjlist, k):
        # minCell will return k if no better cell is found, default behavious for DFS
        minCell = k
        minHeuristicValue = sys.maxsize
        for cell in adjlist:
            tempHeuristicValue = manhattan_heuristic(cell[0],cell[1])
            if tempHeuristicValue < minHeuristicValue and (cell not in self.visited):
                minCell = cell
                minHeuristicValue = tempHeuristicValue
        return minCell
    """
    IDA* algorithm
    """
    def __init__(self):
        """
        A new Agent
t        """
        global cutoff
        cutoff = manhattan_heuristic(0,0)
        # this line is crucial, otherwise the class is not recognized as an AgentBrainPtr by C++
        SearchAgent.__init__(self)
        self.visited = set([])
        self.adjlist = {}
        self.parents = {}
        

    def initialize(self, init_info):
        self.constraints = init_info.actions
        return True

    def start(self, time, observations):

        # return action
        r = observations[0]
        c = observations[1]
        # ******************************** This gets called again when "episode2 starts"
        #                                   therefore resets the cutoff again 
        # cutoff = 3
        self.starting_pos = (r, c)
        get_environment().mark_maze_white(r, c)


        return self.dfs_action(observations)

    def reset(self):
        self.visited = set([])
        # self.parents = {}
        # self.backpointers = {}
        # self.starting_pos = None

    def initialize(self, init_info):
        """
        Initializes the agent upon reset
        """
        self.constraints = init_info.actions
        return True

    
    def act(self, time, observations, reward):
        # return action
        return self.dfs_action(observations)

    def end(self, time, reward):
        print  "Final reward: %f, cumulative: %f" % (reward[0], self.fitness[0])
        self.reset()
        return True
        
    def mark_path(self, r, c):
        get_environment().mark_maze_white(r,c)

    def destroy(self):
        """
        After one or more episodes, this agent can be disposed of
        """
        return True

