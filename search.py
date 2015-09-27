import sys
import time

from board import Board
from priority_queue import PriorityQueue
import heuristic as heuristics


class DepthFirstSearch:
    def __init__(self, start):
        self.start = start
        self.nodes_visited = 0
        self.space = 0

    def search(self, state=None, path=None, depth=1):
        self.nodes_visited += 1

        if not state and not path:
            state = self.start
            path = []

        if state.is_goal():
            self.space = depth
            yield path

        for move, board in state.successors():
            yield from self.search(board, path + [move], depth + 1)


class BreadthFirstSearch:
    def __init__(self, start, check_duplicates):
        self.start = start
        self.check_duplicates = check_duplicates
        self.visited = []
        self.nodes_visited = 0
        self.space = 0

    def search(self):
        queue = [(self.start, [])]

        while queue:
            self.space = max(self.space, len(queue))
            (state, path) = queue.pop(0)
            self.nodes_visited += 1

            for move, board in state.successors():
                if self.check_duplicates and board in self.visited:
                    continue
                elif self.check_duplicates:
                    self.visited = self.visited + [board]

                if board.is_goal():
                    yield path + [move]
                else:
                    queue.append((board, path + [move]))


class AStar:
    def __init__(self, start, heuristic, check_duplicates):
        self.start = start
        self.heuristic = heuristic
        self.check_duplicates = check_duplicates
        self.visited = []
        self.nodes_visited = 0
        self.space = 0

    def search(self):
        pq = PriorityQueue(self.heuristic)
        pq.put((self.start, []))
        while not pq.empty():
            self.space = max(self.space, len(pq))

            state, path = pq.get()
            self.nodes_visited += 1

            if state.is_goal():
                yield path
            for move, board in state.successors():
                if self.check_duplicates and board in self.visited:
                    continue
                elif self.check_duplicates:
                    self.visited = self.visited + [board]

                pq.put((board, path + [move]))


class IterativeDeepeningAStar:
    def __init__(self, start, heuristic):
        self.start = start
        self.heuristic = heuristic
        self.nodes_visited = 0
        self.space = 0

    def search(self):
        bound = self.heuristic(self.start)
        while True:
            t = self.depth_limited_astar(self.start, bound, [])
            if t is not None:
                return t
            elif t is float('inf'):
                return None
            bound = t

    def depth_limited_astar(self, node, bound, path):
        cost = len(path) + self.heuristic(node)
        if cost > bound:
            return None, cost
        if node.is_goal():
            return path, cost
        min_score = float('inf')

        for move, board in node.successors():
            child_path, child_cost = self.depth_limited_astar(board, bound, path + [move])
            if child_path is not None:
                return child_path, child_cost
            min_score = min(min_score, child_cost)
        return None, min_score

    """
    def search(self):
        x = None
        bound = 0
        while x is None:
            x, bound = self.depth_limited_astar(bound, self.start, [], self.heuristic)
            if x is not None:
                self.space = len(x)
                return x
            elif bound == float('inf'):
                return None

    def depth_limited_astar(self, bound, state, path, heuristic):
        self.nodes_visited += 1

        score = len(path) + heuristic(state)
        if score > bound:
            return None, score
        if state.is_goal():
            return path, score

        min_score = float('inf')
        for move, board in state.successors():
            search_path, score = self.depth_limited_astar(bound, board, path + [move], heuristic)
            min_score = min(min_score, score)

            if search_path is not None:
                return search_path, score
        return None, min_score
    """

def main():
    start_board = Board.board_from_file(sys.argv[1])
    tree_or_graph = sys.argv[2]
    method = sys.argv[3]
    heuristic = ''

    check_duplicates = 'graph' in tree_or_graph

    if 'star' in method:
        heuristic = sys.argv[4]

        if heuristic == 'max_moves':
            heuristic = heuristics.max_moves
        elif heuristic == 'min_moves':
            heuristic = heuristics.min_moves
        elif heuristic == 'max_movable_pegs':
            heuristic = heuristics.max_movable_pegs
        else:
            print('You did not pick a viable heuristic. Exiting...')
            return

    start = time.time()
    if method == 'dfs':
        seeker = DepthFirstSearch(start_board)
        try:
            path = next(seeker.search())
        except StopIteration:
            path = None

    elif method == 'bfs':
        seeker = BreadthFirstSearch(start_board, check_duplicates)
        try:
            path = next(seeker.search())
        except StopIteration:
            path = None

    elif method == 'astar':
        seeker = AStar(start_board, heuristic, check_duplicates)
        try:
            path = next(seeker.search())
        except StopIteration:
            path = None

    elif method == 'idastar':
        seeker = IterativeDeepeningAStar(start_board, heuristic)
        path = seeker.search()

    else:
        print('You must choose a valid search method. Exiting...')
        return

    end = time.time()

    print('Search:', sys.argv[2], 'on', sys.argv[3])
    print('Input File:', sys.argv[1])

    for step in path:
        print(step[0], '-->', step[1])

    print('Duration: {0:.4f} seconds'.format(end - start))
    print('Nodes Visited:', seeker.nodes_visited)
    print('Space: {} nodes'.format(seeker.space))

    if hasattr(seeker, 'visited') and 'graph' in tree_or_graph:
        print('Visited Size:', len(seeker.visited))


if __name__ == '__main__':
    main()
