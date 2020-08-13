import csv
import math
import random
import sys
from typing import List
from collections import namedtuple, OrderedDict


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

        self.all_nums_to_match = set(range(1, self.size + 1))
        self.all_nums_sum = sum(self.all_nums_to_match)

        self.board = board
        self.choices = OrderedDict({Cell(ii, jj): [] for ii in range(self.size) for jj in range(self.size)
                                    if self.board[ii][jj] == 0})
        self.update_choices()

    # @profile
    def solve_puzzle(self, last_modified_cell: Cell = Cell(0, 0)):
        """This uses the `self.choices` member to work its way through the puzzle starting with the cells with the
        fewest options to choose from, which should drastically increase performance"""
        self.update_choices()
        for cell, valid_nums in self.choices.items():
            if self.check_puzzle():
                return

            while self.board[cell.row][cell.col] == 0:
                if len(valid_nums) == 0:
                    self.board[cell.row][cell.col] = 0
                    self.board[last_modified_cell.row][last_modified_cell.col] = 0  # Reset to zero
                    self.update_choices()
                    return

                temp = random.choice(valid_nums)
                valid_nums.remove(temp)  # This also removes it from `self.choices`, so don't try to do it manually!

                self.board[cell.row][cell.col] = temp
                self.solve_puzzle(last_modified_cell=cell)

        if self.check_puzzle():
            return

    # @profile
    def check_puzzle(self):
        # Add up values in each row as a quick check
        for row in self.board:
            if sum(row) != self.all_nums_sum:
                return False
        for col_idx in range(self.size):
            col_sum = sum([row[col_idx] for row in self.board])
            if col_sum != self.all_nums_sum:
                return False

        # Now actually verify that each value appears just once in each row, column, and subsquare
        for row in self.board:
            if set(row) != self.all_nums_to_match:
                return False
        for col_idx in range(self.size):
            if set(self.get_nums_in_col(Cell(0, col_idx))) != self.all_nums_to_match:
                return False
        for subsquare_row_idx in range(0, self.size, self.subsquare_size):
            for subsquare_col_idx in range(0, self.size, self.subsquare_size):
                if set(self.get_nums_in_subsquare(Cell(subsquare_row_idx, subsquare_col_idx))) != self.all_nums_to_match:
                    return False
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
    def get_nums_in_row(self, cell: Cell) -> List[int]:
        return [x for x in self.board[cell.row] if x != 0]

    # @profile
    def get_nums_in_col(self, cell: Cell) -> List[int]:
        return [row[cell.col] for row in self.board if row[cell.col] != 0]

    # @profile
    def get_nums_in_subsquare(self, cell: Cell) -> List[int]:
        """Basically copies stuff from `check_intermediate_board()` which is okay for now"""
        subsquare_row_idx = cell.row // self.subsquare_size
        subsq_row_start = subsquare_row_idx * self.subsquare_size
        subsq_row_end = subsq_row_start + self.subsquare_size

        subsquare_col_idx = cell.col // self.subsquare_size
        subsq_col_start = subsquare_col_idx * self.subsquare_size
        subsq_col_end = subsq_col_start + self.subsquare_size

        subsquare = [row[subsq_col_start:subsq_col_end] for row in self.board[subsq_row_start:subsq_row_end]]

        # Flatten list of lists into single list and ignore zeros
        return [item for sublist in subsquare for item in sublist if item != 0]

    # @profile
    def update_choices(self):
        """Updates dict holding the possible valid numbers which each cell can hold"""
        for ii in range(self.size):
            for jj in range(self.size):
                if Cell(ii, jj) not in self.choices.keys():
                    continue
                invalid_values = self.get_nums_in_col(Cell(ii, jj)) + self.get_nums_in_row(Cell(ii, jj)) + \
                                 self.get_nums_in_subsquare(Cell(ii, jj))
                valid_values = [val for val in self.all_nums_to_match if val not in invalid_values]
                self.choices[Cell(ii, jj)] = valid_values

        # Sort based on number of valid choices, so we can start with the cells with the fewest valid choices first
        self.choices = OrderedDict(sorted(self.choices.items(), key=lambda kv: len(kv[1])))

    # @profile
    def remove_choices_for_cell(self, cell: Cell, choices: List[int]):
        """Removes from the list of valid numbers for a given cell"""
        for value in choices:
            self.choices[cell].remove(value)

    # @profile
    def add_choices_for_cell(self, cell: Cell, choices: List[int]):
        """Adds to the list of valid numbers for a given cell"""
        self.choices[cell].extend(choices)


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

    s = Sudoku(read_sample_puzzle("9x9_tough.csv"))
    s.solve_puzzle()
    print(s)

    # s = Sudoku(read_sample_puzzle("16x16_sample_puzzle.csv"))
    # s.solve_puzzle()
    # print(s)
    #
    # s = Sudoku(read_sample_puzzle("16x16_another_puzzle.csv"))
    # s.solve_puzzle()
    # print(s)
