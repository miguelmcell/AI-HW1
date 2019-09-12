from OpenNero import *
from common import *

import Maze
from Maze.constants import *
import Maze.agent
from Maze.agent import *

class IdaStarSearchAgent(SearchAgent):
    def dfs_action(self, observations):
        r = observations[0]
        c = observations[1]
        #print(self.get_distance(r,c))
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
        # if we have been here before, check if we have other places to visit
        adjlist = self.adjlist[current_cell]
        k = 0
        while k < len(adjlist) and adjlist[k] in self.visited:
            k += 1
        # if we don't have other neighbors to visit, back up
        if k == len(adjlist):
            next_cell = self.parents[current_cell] 
        elif(self.get_distance(r,c) == self.bound):
            next_cell = self.starting_pos
            self.bound+=1
        else: # otherwise visit the next place
            next_cell = adjlist[k]
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
    IDA* algorithm
    """
    def __init__(self):
        # this line is crucial, otherwise the class is not recognized as an AgentBrainPtr by C++
        SearchAgent.__init__(self)
        self.visited = set([])
        self.adjlist = {}
        self.parents = {}
        self.bound = 3

    def reset(self):
        """
        Reset the agent
        """
        self.visited = set([])
        self.parents = {}
        self.backpointers = {}
        self.starting_pos = None

    def initialize(self, init_info):
        """
        Initializes the agent upon reset
        """
        self.constraints = init_info.actions
        return True

    def start(self, time, observations):
        """
        Called on the first move
        """
        # return action
        r = observations[0]
        c = observations[1]
        self.starting_pos = (r, c)
        get_environment().mark_maze_white(r, c)
        return self.dfs_action(observations)
    
    def act(self, time, observations, reward):
        """
        Called every time the agent needs to take an action
        """
        # print("IN ACT: ",self.get_distance(observations[0],observations[1]))
        # if((observations[0],observations[1]) == self.starting_pos and self.get_distance(observations[0],observations[1]) == bound):
        #     print("SUCCESS\n\n\n")
        #     self.bound += 1
        # else:
        return self.dfs_action(observations)

    def end(self, time, reward):
        """
        at the end of an episode, the environment tells us the final reward
        """
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

