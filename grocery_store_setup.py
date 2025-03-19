# No other imports are allowed than these:
import numpy as np
import heapq as hq
from collections import deque
import itertools as it
import math
import sqlite3
import os

class SearchNode(object):
    def __init__(self, problem, state, parent=None, action=None, step_cost=0, depth=0):
        self.problem = problem
        self.state = state
        self.parent = parent
        self.action = action
        self.step_cost = step_cost
        self.path_cost = step_cost + (0 if parent is None else parent.path_cost)
        self.path_risk = self.path_cost + problem.heuristic(state)
        self.depth = depth
        self.child_list = []
    def is_goal(self):
        return self.problem.is_goal(self.state)
    def children(self):
        if len(self.child_list) > 0: return self.child_list
        domain = self.problem.domain
        for action, step_cost in domain.valid_actions(self.state):
            new_state = domain.perform_action(self.state, action)
            self.child_list.append(
                SearchNode(self.problem, new_state, self, action, step_cost, depth=self.depth+1))
        return self.child_list
    def path(self):
        if self.parent == None: return []
        return self.parent.path() + [self.action]

class SearchProblem(object):
    def __init__(self, domain, initial_state, is_goal = None):
        if is_goal is None: is_goal = lambda s: False
        self.domain = domain
        self.initial_state = initial_state
        self.is_goal = is_goal
        self.heuristic = lambda s: 0
    def root_node(self):
        return SearchNode(self, self.initial_state)

class FIFOFrontier:
    def __init__(self):
        self.queue_nodes = deque()
        self.queue_states = set()
    def __len__(self):
        return len(self.queue_states)
    def push(self, node):
        if node.state not in self.queue_states:
            self.queue_nodes.append(node)
            self.queue_states.add(node.state)
    def pop(self):
        node = self.queue_nodes.popleft()
        self.queue_states.remove(node.state)
        return node
    def is_not_empty(self):
        return len(self.queue_nodes) > 0

class PriorityHeapFIFOFrontier(object):
    """
    Implementation using heapq 
    https://docs.python.org/3/library/heapq.html
    """
    def __init__(self):
        self.heap = []
        self.state_lookup = {}
        self.count = 0

    def push(self, node):
        if node.state in self.state_lookup:
            entry = self.state_lookup[node.state] # = [risk, count, node, removed]
            if entry[0] <= node.path_risk: return
            entry[-1] = True # mark removed
        new_entry = [node.path_risk, self.count, node, False]
        hq.heappush(self.heap, new_entry)
        self.state_lookup[node.state] = new_entry
        self.count += 1

    def pop(self):
        while len(self.heap) > 0:
            risk, count, node, already_removed = hq.heappop(self.heap)
            if not already_removed:
                self.state_lookup.pop(node.state)
                return node

    def is_not_empty(self):
        return len(self.heap) > 0

    def states(self):
        return list(self.state_lookup.keys())

def queue_search(frontier, problem):
    node_count = 0
    explored = set()
    root = problem.root_node()
    frontier.push(root)
    while frontier.is_not_empty():
        node = frontier.pop()
        if node:
            node_count += 1
        if node.is_goal(): break
        explored.add(node.state)
        for child in node.children():
            if child.state in explored: continue
            frontier.push(child)
    plan = node.path() if node.is_goal() else []
    return plan, node_count

def a_star_search(problem, heuristic):
    problem.heuristic = heuristic
    return queue_search(PriorityHeapFIFOFrontier(), problem)

