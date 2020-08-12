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

        self.all_nums_to_match = list(range(1, self.size + 1))

        self.board = board

    # @profile
    def solve_puzzle(self, last_modified_cell: Cell = Cell(0, 0)):
        for ii, row in enumerate(self.board):
            if ii < last_modified_cell.row:
                continue
            for jj, cell in enumerate(row):
                # Used to avoid random num generator picking same nums repeatedly
                if self.size <= 9:
                    untried_cell_values = [x for x in self.all_nums_to_match if x not in row]
                else:
                    untried_cell_values = [x for x in self.all_nums_to_match
                                           if x not in self.get_nums_in_row(Cell(ii, jj)) and
                                              x not in self.get_nums_in_col(Cell(ii, jj)) and
                                              x not in self.get_nums_in_subsquare(Cell(ii, jj))
                                           ]

                while self.board[ii][jj] == 0:
                    if untried_cell_values == []:  # If we've tried everything and nothing worked, return and backtrack
                        self.board[last_modified_cell.row][last_modified_cell.col] = 0  # Reset to zero
                        return

                    temp = random.choice(untried_cell_values)
                    untried_cell_values.remove(temp)

                    self.board[ii][jj] = temp
                    if self.check_intermediate_board(modified_cell=Cell(ii, jj)):
                        self.solve_puzzle(last_modified_cell=Cell(ii, jj))
                    else:
                        self.board[ii][jj] = 0

        if self.check_puzzle():
            return

    # @profile
    def check_puzzle(self):
        # Add up values in each row as a quick check
        for row in self.board:
            if sum(row) != (self.size * (self.size + 1) / 2):
                return False
        for col_idx in range(self.size):
            col_sum = sum([row[col_idx] for row in self.board])
            if col_sum != (self.size * (self.size + 1) / 2):
                return False

        # Now actually verify that each value appears just once in each row, column, and subsquare
        for row in self.board:
            if sorted(row) != self.all_nums_to_match:
                return False
        for col_idx in range(self.size):
            if sorted([row[col_idx] for row in self.board]) != self.all_nums_to_match:
                return False
        for subsquare_row_idx in range(self.subsquare_size):
            for subsquare_col_idx in range(self.subsquare_size):
                subsquare = [row[subsquare_col_idx:subsquare_col_idx + self.subsquare_size]
                             for row in self.board[subsquare_row_idx: subsquare_row_idx + self.subsquare_size]]
                subsquare_nums = [item for sublist in subsquare for item in sublist]
                if sorted(subsquare_nums) != self.all_nums_to_match:
                    return False

        return True

    # @profile
    def check_intermediate_board(self, modified_cell: Cell):
        """Sort of duplicates some of the code from `check_board()` but that's okay for now.  Checks to make sure there
        only at most one of each number in each row, column, and subsquare
        """
        non_zeros_row = self.get_nums_in_row(modified_cell)
        if len(set(non_zeros_row)) != len(non_zeros_row):
            return False

        non_zeros_col = self.get_nums_in_col(modified_cell)
        if len(set(non_zeros_col)) != len(non_zeros_col):
            return False

        non_zeros_subsquare = self.get_nums_in_subsquare(modified_cell)
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

    # @profile
    def get_nums_in_row(self, cell: Cell):
        return [x for x in self.board[cell.row] if x != 0]

    # @profile
    def get_nums_in_col(self, cell: Cell):
        return [row[cell.col] for row in self.board if row[cell.col] != 0]

    # @profile
    def get_nums_in_subsquare(self, cell: Cell):
        """Basically copies stuff from `check_intermediate_board()` which is okay for now"""
        subsquare_row_idx = cell.row // self.subsquare_size
        subsq_row_start = subsquare_row_idx * self.subsquare_size
        subsq_row_end = subsq_row_start + self.subsquare_size

        subsquare_col_idx = cell.col // self.subsquare_size
        subsq_col_start = subsquare_col_idx * self.subsquare_size
        subsq_col_end = subsq_col_start + self.subsquare_size

        subsquare = [row[subsq_col_start:subsq_col_end] for row in self.board[subsq_row_start:subsq_row_end]]

        # Flatten list of lists into single list and ignore zeros
        subsquare_non_zeros = [item for sublist in subsquare for item in sublist if item != 0]
        return subsquare_non_zeros

def read_sample_puzzle(file_name):
    puzzle = []
    with open(file_name, 'r') as infile:
        reader = csv.reader(infile, delimiter=',')
        for line in reader:
            puzzle.append([int(x) for x in line])

    if len(puzzle) != set([len(row) for row in puzzle]).pop():
        raise ValueError(f"Input sudoku must be a square!  This is not!")
    return puzzle


if __name__ == '__main__':
    s = Sudoku(read_sample_puzzle("sample_puzzle.csv"))
    s.solve_puzzle()
    print(s)

    # s = Sudoku(read_sample_puzzle("9x9_tough.csv"))
    # s.solve_puzzle()
    # print(s)

    # s = Sudoku(read_sample_puzzle("16x16_sample_puzzle.csv"))
    # s.solve_puzzle(s.board)
    # print(s)

    # s = Sudoku(read_sample_puzzle("16x16_another_puzzle.csv"))
    # s.solve_puzzle(s.board)
    # print(s)
