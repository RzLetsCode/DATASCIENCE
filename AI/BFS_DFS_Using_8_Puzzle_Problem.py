import os
from collections import deque
import psutil
from graphviz import Digraph
import time


def g(state):
    goal_state = [1, 2, 3,
                  4, 5, 6,
                  7, 8, "_"]

     # Check if the current state matches the goal state
    return state == goal_state

def m(state):
    # Find the position of the empty space ("_")
    empty_index = state.index("_")
    row, col = empty_index // 3, empty_index % 3

    # Define possible moves: (row_delta, col_delta)
    moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    next_states = []

    for dr, dc in moves:
        new_row, new_col = row + dr, col + dc
        print("new row , new column is ",new_row,new_col)
        # Check if the new position is within the puzzle boundaries
        if 0 <= new_row < 3 and 0 <= new_col < 3:
            # Create a copy of the current state to avoid modifying it
            new_state = list(state)

            # Swap the empty space with the tile in the new position
            new_index = new_row * 3 + new_col
            new_state[empty_index], new_state[new_index] = new_state[new_index], new_state[empty_index]

            next_states.append(new_state)
            print("New State ",new_state)

 # Define the goal state as a list with the correct tile positions
    return next_states




def bfs(pt):
    vt = set()
    qt = deque([(pt, [])])
    dt = Digraph()
    dt.node(str(pt), str(pt))
    it = 0
    sm = psutil.Process(os.getpid()).memory_info().rss

    start_time = time.time()  # Renaming to start_time
    while qt:
        it += 1
        st, pa = qt.popleft()

        if g(st):
            et = time.time() - start_time
            em = psutil.Process(os.getpid()).memory_info().rss
            return pa + [st], dt, it, et, em - sm
        for ns in m(st):
            ts = tuple(ns)
            if ts not in vt:
                vt.add(ts)
                dt.node(str(ns), str(ns))
                dt.edge(str(st), str(ns))
                qt.append((ns, pa + [st]))

        print(f"Iteration: {it}, Percentage explored: {len(vt) / 362880 * 100:.2f}%")
    return None


def dfs(pt, dl):
    vt = set()
    sk = [(pt, [])]
    dt = Digraph()
    dt.node(str(pt), str(pt))
    it = 0
    sm = psutil.Process(os.getpid()).memory_info().rss

    start_time = time.time()  # Renaming to start_time
    while sk:
        it += 1
        st, pa = sk.pop()

        if len(pa) > dl:
            continue
        if g(st):
            et = time.time() - start_time
            em = psutil.Process(os.getpid()).memory_info().rss
            return pa + [st], dt, it, et, em - sm
        for ns in m(st):
            ts = tuple(ns)
            if ts not in vt:
                vt.add(ts)
                dt.node(str(ns), str(ns))
                dt.edge(str(st), str(ns))
                sk.append((ns, pa + [st]))

        print(f"Iteration: {it}, Percentage explored: {len(vt) / 362880 * 100:.2f}%")
    return None


pz = [1, 2, 3, 4, "_", 6, 7, 5, 8]

print("BFS:")
rs, dg, it, tt, mm = bfs(pz)
print(f"Total Iterations: {it}")
print(f"Time taken: {tt:.2f} seconds")
print(f"Memory used: {mm / (1024 ** 2):.2f} MB")
dg.view('bfs')
if rs:
    print(rs)
else:
    print("No solution.")

print("\nDFS:")
rs, dg, it, tt, mm = dfs(pz, 10)
print(f"Total Iterations: {it}")
print(f"Time taken: {tt:.2f} seconds")
print(f"Memory used: {mm / (1024 ** 2):.2f} MB")
dg.view('dfs')
if rs:
    print(rs)
else:
    print("No solution.")
