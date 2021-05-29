import pygame
import math
from queue import PriorityQueue
import time 

width = 800
window = pygame.display.set_mode((width, width))
pygame.display.set_caption("A* Path Finding Algorithm")


RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    def is_in_closed(self):
        return self.color == GREEN

    def is_in_open(self):
        return self.color == RED

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == PURPLE

    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = ORANGE

    def make_closed(self):
        self.color = GREEN

    def make_open(self):
        self.color = RED

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = PURPLE

    def make_path(self):
        self.color = TURQUOISE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): 
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False

def hueristic(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(arr_from, current, draw): # draws path
    while current in arr_from:
        current = arr_from[current]
        current.make_path()
        draw()


def algorithm(draw, grid, start, end):
    number = 0 
    open_set = PriorityQueue()
    open_set.put((0, number, start)) # put start node in open set
    arr_from = {} # which previous node current node came from
    g_score = {node: float("inf") for row in grid for node in row} # g score 
    g_score[start] = 0 # start node g score
    f_score = {node: float("inf") for row in grid for node in row} # f score
    f_score[start] = hueristic(start.get_pos(), end.get_pos()) # inital f score is the hueristic

    open_set_hash = {start} # keeps track of open set

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current_pair_in_set = open_set.get()[2] 
        open_set_hash.remove(current_pair_in_set)

        if current_pair_in_set == end:
            reconstruct_path(arr_from, end, draw)
            end.make_end()
            return True

        for neighbor in current_pair_in_set.neighbors: # updates g score
            temporary_g_score = g_score[current_pair_in_set] + 1

            if temporary_g_score < g_score[neighbor]: # finding f score
                arr_from[neighbor] = current_pair_in_set
                g_score[neighbor] = temporary_g_score
                f_score[neighbor] = temporary_g_score + hueristic(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    number = number + 1
                    open_set.put((f_score[neighbor], number, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if current_pair_in_set != start:
            current_pair_in_set.make_closed()

    return False

def get_clicked_position(pos, rows, width):
    gap = width // rows
    y, x = pos
    row = y // gap
    col = x // gap

    return row, col


def make_map(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)

    return grid


def draw_map(win, rows, width):
    gap = width // rows
    for x in range(rows):
        pygame.draw.line(win, GREY, (0, x * gap), (width, x * gap))
        for y in range(rows):
            pygame.draw.line(win, GREY, (y * gap, 0), (y * gap, width))


def draw_everything(window, grid, rows, width):
    window.fill(WHITE)

    for row in grid:
        for node in row:
            node.draw(window)

    draw_map(window, rows, width)
    pygame.display.update()


def main(window, width):
    
    
    ROWS = 25
    grid = make_map(ROWS, width)

    start = None
    end = None
    
    run = True
    while run:
        draw_everything(window, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_position(pos, ROWS, width)
                node = grid[row][col]
                if not start and node != end:
                    start = node
                    start.make_start()

                elif not end and node != start:
                    end = node
                    end.make_end()

                elif node != end and node != start:
                    node.make_barrier()

            elif pygame.mouse.get_pressed()[2]: 
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_position(pos, ROWS, width)
                node = grid[row][col]
                node.reset()
                if node == start:
                    start = None
                elif node == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)

                    algorithm(lambda: draw_everything(window, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_BACKSPACE:
                    start = None
                    end = None
                    grid = make_map(ROWS, width)

    pygame.quit()

main(window, width)