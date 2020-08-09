import csv
import math
import random
import sys
from typing import List
from collections import namedtuple

Cell = namedtuple("Cell", ["row", "col"])
sys.setrecursionlimit(100000)

class Sudoku:
    def __init__(self, board: List[List[int]]):
        size = len(board)
        if size != len(board[0]):  # If board doesn't have same side lengths
            raise ValueError(f"Board width {len(board[0])} must equal height {size}")
        elif math.sqrt(size) != int(math.sqrt(size)):  # If `size` isn't a perfect square...
            raise ValueError(f"Sudoku board size must be a perfect square, but {size} is not.")

        self.size = size
        self.subsquare_size = int(math.sqrt(size))

        self.board = board
        self.recursive_levels = 0

    def solve_puzzle(self, curr_board: List[List[int]], last_modified_cell: Cell = []):
        self.recursive_levels += 1
        for ii, row in enumerate(curr_board):
            for jj, cell in enumerate(row):
                # Used to avoid random num generator picking same nums repeatedly
                untried_cell_values = list(range(1, self.size + 1))

                while curr_board[ii][jj] == 0:
                    if untried_cell_values == []:  # If we've tried everything and nothing worked, return and backtrack
                        self.recursive_levels -= 1
                        curr_board[last_modified_cell.row][last_modified_cell.col] = 0  # Reset to zero
                        return
                    temp = random.choice(untried_cell_values)
                    untried_cell_values.remove(temp)
                    curr_board[ii][jj] = temp
                    # if self.check_intermediate_board(curr_board, modified_cell=[jj, ii]):
                    #     self.solve_puzzle(curr_board, last_modified_cell=[ii, jj])
                    if self.check_intermediate_board(curr_board, modified_cell=Cell(ii, jj)):
                        self.solve_puzzle(curr_board, last_modified_cell=Cell(ii, jj))
                    else:
                        curr_board[ii][jj] = 0

        if self.check_puzzle(curr_board):
            self.__repr__()
            return

    def check_puzzle(self, board: List[List[int]]):
        # Add up values in each row as a quick check
        for row in board:
            if sum(row) != (self.size * (self.size + 1) / 2):
                return False
        for col_idx in range(self.size):
            col_sum = sum([row[col_idx] for row in board])
            if col_sum != (self.size * (self.size + 1) / 2):
                return False

        # Now actually verify that each value appears just once in each row, column, and subsquare
        for row in board:
            if sorted(row) != list(range(1, self.size + 1)):
                return False
        for col_idx in range(self.size):
            if sorted([row[col_idx] for row in board]) != list(range(1, self.size + 1)):
                return False
        for subsquare_row_idx in range(self.subsquare_size):
            for subsquare_col_idx in range(self.subsquare_size):
                subsquare = [row[subsquare_col_idx:subsquare_col_idx + self.subsquare_size]
                             for row in board[subsquare_row_idx: subsquare_row_idx + self.subsquare_size]]
                subsquare_nums = [item for sublist in subsquare for item in sublist]
                if sorted(subsquare_nums) != list(range(self.size)):
                    return False

        return True

    def check_intermediate_board(self, board: List[List[int]], modified_cell: Cell = []):
        """Sort of duplicates some of the code from `check_board()` but that's okay for now.  Checks to make sure there
        only at most one of each number in each row, column, and subsquare
        """
        for ii, row in enumerate(board):
            if modified_cell != [] and ii != modified_cell.row:  # Don't check if nothing has changed for this row
                continue
            non_zeros_row = [x for x in row if x != 0]
            if len(set(non_zeros_row)) != len(non_zeros_row):  # Checks for duplicate numbers in row (ignoring zeros)
                return False
        for jj, col_idx in enumerate(range(self.size)):  # Don't check if nothing has changed for this col
            if modified_cell != [] and jj != modified_cell.col:
                continue
            non_zeros_col = [x for x in [row[col_idx] for row in board] if x != 0]
            if len(set(non_zeros_col)) != len(non_zeros_col):
                return False
        for subsquare_row_idx in range(self.subsquare_size):
            for subsquare_col_idx in range(self.subsquare_size):
                # Make sure the subsquare we're checking is the one that was modified, if the modified cell was provided
                if modified_cell != [] and \
                        (modified_cell.col not in range(subsquare_col_idx * self.subsquare_size,
                                                        subsquare_col_idx * self.subsquare_size + self.subsquare_size) or
                         modified_cell.row not in range(subsquare_row_idx * self.subsquare_size,
                                                        subsquare_row_idx * self.subsquare_size + self.subsquare_size)):
                    continue

                subsquare = [row[subsquare_col_idx * self.subsquare_size:subsquare_col_idx * self.subsquare_size + self.subsquare_size]
                             for row in board[subsquare_row_idx * self.subsquare_size: subsquare_row_idx * self.subsquare_size + self.subsquare_size]]
                subsquare_nums = [item for sublist in subsquare for item in sublist]
                non_zeros_subsquare = [x for x in subsquare_nums if x != 0]
                if len(set(non_zeros_subsquare)) != len(non_zeros_subsquare):
                    return False

        # If we reach here, then there are no conflicting (i.e., duplicate) numbers in any row, column, or subsquare
        return True

    def __repr__(self):
        """Prints the current game board. Leaves unassigned spots blank."""
        s = ""
        for row in self.board:
            for val in row:
                s += str(val) + " "
            s += "\n"
        return s

def read_sample_puzzle(file_name):
    puzzle = []
    with open(file_name, 'r') as infile:
        reader = csv.reader(infile, delimiter=',')
        for line in reader:
            puzzle.append([int(x) for x in line])

    return puzzle


if __name__ == '__main__':
    s = Sudoku(read_sample_puzzle("sample_puzzle.csv"))
    s.solve_puzzle(s.board)
    print(s)
