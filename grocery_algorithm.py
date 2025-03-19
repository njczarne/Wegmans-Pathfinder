# No other imports are allowed than these:
from time import perf_counter
from arrows import reportGraph
from wegmanScrape import fullSearch
import numpy as np
import matplotlib.pyplot as pt
from matplotlib import animation
from grocery_store_setup import *
import itertools as it # included in case you want to use it
import math # included in case you want to use it
import sqlite3
import os
import emoji

AISLE, CASHIER, CLEAN, FOOD = list(range(4))
SIZE = 10
grocery_total = 0
cleans = 0
class GroceryDomain:
    def __init__(self):
        num_rows, num_cols = SIZE, SIZE
        grid = CLEAN*np.ones((num_rows, num_cols), dtype=int)

        # initializing all AISLES
        grid[1:4, 1] = AISLE 
        grid[6:9, 1] = AISLE
        grid[1:4, 3] = AISLE 
        grid[6:9, 3] = AISLE
        grid[1:4, 5] = AISLE 
        grid[6:9, 5] = AISLE
        grid[1:4, 7] = AISLE  
        grid[6:9, 7] = AISLE
        grid[3, 9] = AISLE 
        grid[5, 9] = AISLE
        grid[7, 9] = AISLE 
        grid[9, 9] = AISLE
        # place the cash register
        grid[0 , 9] = CASHIER
        max_power = 2*SIZE + 1
        self.grid = grid
        self.max_power = max_power

    def pack(self, g, r, c, p):
        return (g.tobytes(), r, c, p)
    def unpack(self, state):
        grid, r, c, p = state
        grid = np.frombuffer(grid, dtype=int).reshape(self.grid.shape).copy()
        return grid, r, c, p

    def initial_state(self, grocery_position, food_positions):
        r, c = grocery_position
        grid = self.grid.copy()
        for dr, dc in food_positions: 
            grid[dr, dc] = FOOD
        return self.pack(grid, r, c, self.max_power)

    def render(self, ax, state, x=0, y=0):
        grid, r, c, p = self.unpack(state)
        num_rows, num_cols = grid.shape
        ax.imshow(grid, cmap='gray', vmin=0, vmax=3, extent=(x-.5,x+num_cols-.5, y+num_rows-.5, y-.5))
        for col in range(num_cols+1): pt.plot([x+ col-.5, x+ col-.5], [y+ -.5, y+ num_rows-.5], 'k-')
        for row in range(num_rows+1): pt.plot([x+ -.5, x+ num_cols-.5], [y+ row-.5, y+ row-.5], 'k-')
        pt.text(c-.25, r+.25, str(emoji.emojize(":beaming_face_with_smiling_eyes:")), fontsize=24)
        pt.tick_params(which='both', bottom=False, left=False, labelbottom=False, labelleft=False)

    def valid_actions(self, state):

        # r, c is the current row and column of the customer
        # grid[i,j] is AISLE, CASHIER, CLEAN or FOOD to indicate status at row i, column j.
        grid, r, c, p = self.unpack(state)
        num_rows, num_cols = grid.shape
        actions = []

        # staying put or not moving
        actions.append(((0, 0), 1)) 

        # moving left or right
        if r > 0 and grid[r-1, c] != AISLE: actions.append(((-1, 0), 1))
        if r < num_rows - 1 and grid[r+1, c] != AISLE: actions.append(((1, 0), 1))

        # moving up or down
        if c > 0 and grid[r, c-1] != AISLE: actions.append(((0,-1), 1))
        if c < num_cols-1 and grid[r, c+1] != AISLE: actions.append(((0,1), 1))

        # moving diagonally left
        # if r > 0 and c < num_cols-1 and grid[r-1,c+1] != AISLE: actions.append(((-1, 1),1))
        # if r > 0 and c > 0 and grid[r-1,c-1] != AISLE: actions.append(((-1, -1),1))

        # moving diagonally right 
        # if r < num_rows-1 and c < num_cols-1 and grid[r+1,c+1] != AISLE: actions.append(((1, 1),1))
        # if r < num_rows-1 and c > 0 and grid[r+1,c-1] != AISLE: actions.append(((1, -1),1))

        return actions
    
    def perform_action(self, state, action):
        grid, r, c, p = self.unpack(state)
        dr, dc = action # defining the new action
        r, c = r + dr, c + dc

        # connecting to .db file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_file_path = os.path.join(current_dir, 'grocery.db')
        connection = sqlite3.connect(db_file_path)
        cursor = connection.cursor()

        query = "SELECT Cost from groceries where XCord = ? and YCord = ?"
        cursor.execute(query, [c, r])
        result = cursor.fetchall()

        # Drainage
        if grid[r, c] != CASHIER and action != (0,0) and p != 0: p = p 
        # picking up the food item
        if grid[r, c] == FOOD and action == (0,0) and p != 0: grid[r, c] = CLEAN; p = p        
        # made it to the cashier
        if grid[r,c] == CASHIER and p!= self.max_power and action == (0,0): p = p
        # Stay on clean square
        if grid[r, c] == CLEAN and action == (0,0): p = p

        new_state = self.pack(grid, r, c, p)
        return new_state

    def is_goal(self, state):
        grid, r, c, p = self.unpack(state)

        # In a goal state, no grid cell should be food
        all_clean = (grid != FOOD).all() 
        at_cashier = grid[r,c] == CASHIER

        result = all_clean and at_cashier
        return result

    # our implemented heuristic pathfinder
    def better_heuristic(self, state):
        grid, r, c, p = self.unpack(state)
        food = list(zip(*np.nonzero(grid == FOOD)))

        if len(food) == 0: return 0
        else: num_food = len(food)

        dists = [max(np.fabs(dr-r), np.fabs(dc-c)) for (dr, dc) in food]
        return int(max(dists)) + num_food

def runrun():

    # Getting from ryans web scraper
    itemSearchList = fullSearch()
    print(itemSearchList)
    #{'Apples': {'Cost': '$1.58 /ea', 'Location': 18}, 'Coffee': {'Cost': '$9.99 /ea', 'Location': 13}}
    grocery_total = 0
    for key, value in itemSearchList.items():
        print(value)
        cost = value['Cost']
        if type(cost) == int:
            grocery_total += cost
        else:

            cost = cost.split(' ')[0]
            cost = cost[1:]
            cost = float(cost)
            grocery_total += cost

    inputGUIs = itemSearchList.keys()
    listR = []
    listC = []
    food = []
    cleans = 0

    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_file_path = os.path.join(current_dir, 'grocery.db')
    connection = sqlite3.connect(db_file_path)
    cursor = connection.cursor()

    # all strings to excute for now
    de = "drop table groceries"
    cursor.execute(de)
    cts = "Create table groceries (Item TEXT, XCord int, YCord int, Cost)"
    cursor.execute(cts)

    def locationToCoordinates(location):
        import random
        col = -1
        row = -1
        locToCol = {"1": 0, "2": 2, "3": 0, "4": 2, "5": 2, "6": 4, "7": 2, "8": 4, "9": 4, "10": 6, "11": 4, "12": 6, "13": 6, "14": 8, "15": 6, "16": 8, "17": 8, "18": 8, "19": 8, "20": 8}
        col = locToCol[str(location)]
        if location in [1, 2, 5, 6, 9, 10, 13, 14]: row = random.randint(1, 3)
        elif location in [3, 4, 7, 8, 11, 12, 15, 16]: row = random.randint(6, 8)
        elif location == 17: row = 3
        elif location == 18: row = 5
        elif location == 19: row = 7
        elif location == 20: row = 9
        return (row, col)

    query = "INSERT INTO groceries (Item, XCord, YCord, Cost) VALUES (?, ?, ?, ?)"
    for key, value in itemSearchList.items():
        row, col = locationToCoordinates(value["Location"])
        cursor.execute(query, (key, row, col, value["Cost"]))
    
    query = "SELECT XCord, YCord from groceries where Item = ?"
    for item in inputGUIs:
        cursor.execute(query, (item,))
        result = cursor.fetchall()
        print(result)
        listR.append(result[0][0])
        listC.append(result[0][1])
    connection.close()

    # set up initial state by placing the food squares in the grocery store
    for x in range(len(listR)):
        food.append((listR[x], listC[x]))
        
    domain = GroceryDomain()
    init = domain.initial_state(
        grocery_position = (0, 8),
        food_positions = food)

    problem = SearchProblem(domain, init, domain.is_goal)

    start = perf_counter()
    plan, node_count = a_star_search(problem, domain.better_heuristic)
    astar_time = perf_counter() - start
    # print("Our heuristic:")
    # print("astar_time", astar_time)
    # print("node count", node_count)
    # print("plan length", len(plan) - cleans)

    # Constructing the animation of person walking through the gorcery store
    states = [problem.initial_state]
    for a in range(len(plan)):
        states.append(domain.perform_action(states[-1], plan[a]))

    current_pos = (8, 0)  # Start position as per init with (y, x) coordinates
    path = [current_pos]

    for action in plan:
        # currently in the form of y, x, going to change right here
        y, x = action  # Extract row/col changes from action, which is currently (y, x) coordinates
        current_pos = (current_pos[0] + x, current_pos[1] + y)
        path.append(current_pos)

    # Convert the path to an array for plotting
    pathAnim = np.array(path)
    x = pathAnim[:, 0]  # Column coordinates (X-axis)
    y = pathAnim[:, 1]  # Row coordinates (Y-axis)

    # Animate the plan
    fig = pt.figure(figsize=(8, 8))
    def drawframe(n):
        pt.cla()
        domain.render(pt.gca(), states[n])

    anim = animation.FuncAnimation(fig, drawframe, frames=len(states), interval=500, blit=False)
    pt.show()
    print("Reached")

    # all that is needed to make the static report after the animation
    fig, ax = reportGraph(path)
    pt.show()

    print("plan length", len(plan) - len(food)) 
    print(f"Total price: ${grocery_total:.2f}")
    distance_traveled = ((len(plan) - len(food)) * 100) / 5280
    print(f"Average distance covered ≈ {distance_traveled:.2f} Miles")
    hours = distance_traveled // 3
    minutes = distance_traveled / 0.05
    if hours == 1:
        print(f"Total time ≈ {hours:.0f}Hr {minutes:.2f}Mins")
    else:
        print(f"Total time ≈ {hours:.0f} Hrs and {minutes:.2f} Mins")