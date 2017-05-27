import re
from itertools import chain
from collections import Counter, defaultdict

### ------------------------------------------------------------------------------------------- ###
### ------------------------------------------------------------------------------------------- ###
### ------------------------------------------------------------------------------------------- ###

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a + b for a in A for b in B]

### ------------------------------------------------------------------------------------------- ###
### ------------------------------------------------------------------------------------------- ###
### ------------------------------------------------------------------------------------------- ###

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    return {box:cols if val == '.' else val for box, val in zip(boxes, grid)}

### ------------------------------------------------------------------------------------------- ###
### ------------------------------------------------------------------------------------------- ###
### ------------------------------------------------------------------------------------------- ###

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    for r, row in enumerate(row_units):
        if r % 3 == 0 and r > 0:
            print('-' * 95)
        for c, box in enumerate(row):
            if c % 3 == 0 and c > 0:
                print(' | ', end='')
            print('{:^10}'.format(values[box]), end='')
        print()

### ------------------------------------------------------------------------------------------- ###
### ------------------------------------------------------------------------------------------- ###
### ------------------------------------------------------------------------------------------- ###

def eliminate(values):
    """
    Go through all the boxes, and whenever there is a box with a value, eliminate this value from the values of all its peers.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    # finds all boxes with only one value
    # then finds the peer boxes for each solved box
    # if a peer box contains the same number as the solved box, then that number gets removed
    solved_boxes = [box for box in boxes if len(values[box]) == 1]
    for box in solved_boxes:
        digit = values[box]
        for peer in peers[box]:
            values[peer] = values[peer].replace(digit,'')
    return values

### ------------------------------------------------------------------------------------------- ###
### ------------------------------------------------------------------------------------------- ###
### ------------------------------------------------------------------------------------------- ###

def only_choice(values):
    """
    Go through all the units, and whenever there is a unit with a value that only fits in one box, assign the value to this box.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    # iterate though each unit
    # inside each unit, iterate through the numbers 1 to 9
    # then, for example, look for the number "3" in each box in a particular unit
    # if only one box in a unit has a "3", then mark that box as "3"
    for unit in units:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
    return values

### ------------------------------------------------------------------------------------------- ###
### ------------------------------------------------------------------------------------------- ###
### ------------------------------------------------------------------------------------------- ###

def naked_twins(values):
    """
    Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # iterate through each unit, and then each box in that unit
    # create a dictionary, and if the value in a box has 2 numbers, like "35" then add "35" to the dictionary with a value of 1
    # increment this value, 1, if another "35" is found in the same unit
    # iterate over the dictionary, finding all the two-lettered keys, i.e., "35" or "78" which have been seen only twice in a unit
    # if another box in that unit contains the value, like "1357", then remove the "35", leaving only "17"
    for unit in units:
        d = defaultdict(int)
        for box in unit:
            val = values[box]
            if len(val) == 2:
                d[val] += 1
        for (a, b), count in d.items():
            if count == 2:
                for box in unit:
                    if values[box] != a + b:
                        values[box] = re.sub(a + '|' + b, '', values[box])
    return values

### ------------------------------------------------------------------------------------------- ###
### ------------------------------------------------------------------------------------------- ###
### ------------------------------------------------------------------------------------------- ###

def reduce_puzzle(values):
    """
    Runs one pass over each of the three elimination techniques.
    Input: A sudoku dictionary
    Output: A sudoku dictionary
    """
    # run through each elimination strategy once
    values = eliminate(values)
    values = only_choice(values)
    values = naked_twins(values)
    return values

### ------------------------------------------------------------------------------------------- ###
### ------------------------------------------------------------------------------------------- ###
### ------------------------------------------------------------------------------------------- ###

def search(values):
    """
    Finds the solution to Sudoku. It does it by repeated elminiation, until the Sudoku can no longer
    be reduced. Then it uses brute force search using recusing and depth-first-search (DFS)
    Input: A sudoku dictionary
    Output: On success a sudoku dictionary; On failure, False or None.
    """
    # first, keep reducing the search space, using elimination, until the dictionary doesn't change any more
    # then, if the game is solved, return the dictionary
    # if the board is no longer searchable, i.e., 81 remaining numbers, return false
    # else find the box with the smallest length, like "87" has length of 2
    # then guess the "8" and try and recursively solve using DFS. if that doesn't work, try the "7" and solve
    while True:
        reduced = reduce_puzzle(values.copy())
        if is_same(values, reduced): break
        values = reduced

    if is_solved(values):
        return values

    if not is_searchable(values):
        return False

    box = find_smallest_box(values)
    guesses = values[box]
    for guess in guesses:
        values[box] = guess
        result = search(values.copy())
        if result:
            return result

### ------------------------------------------------------------------------------------------- ###
### ------------------------------------------------------------------------------------------- ###
### ------------------------------------------------------------------------------------------- ###

def is_same(before, after):
    """
    Checks whether two dictionaries are the same using a hash function.
    Input: Two sudoku dictionaries.
    Output: Boolean
    """
    return hash(tuple(before.values())) == hash(tuple(after.values()))

### ------------------------------------------------------------------------------------------- ###
### ------------------------------------------------------------------------------------------- ###
### ------------------------------------------------------------------------------------------- ###

def is_searchable(values):
    """
    Determines if the sudoku board is still searchable.
    Input: A sudoku dictionary.
    Output: Boolean
    """
    return len(''.join(values.values())) > 81

### ------------------------------------------------------------------------------------------- ###
### ------------------------------------------------------------------------------------------- ###
### ------------------------------------------------------------------------------------------- ###

def is_solved(values):
    """
    Determines if the current board is a winner.
    Input: A sudoku dictionary.
    Output: Boolean
    """
    for unit in units:
        unit_values_list = list(map(lambda box: values[box], unit))
        unit_values_str = ''.join(sorted(''.join(unit_values_list)))
        if unit_values_str != '123456789': return False
    return True

### ------------------------------------------------------------------------------------------- ###
### ------------------------------------------------------------------------------------------- ###
### ------------------------------------------------------------------------------------------- ###

def find_smallest_box(values):
    """
    Finds the box, or cell, that has the smallest number of values.
    Input: A sudoku dictionary.
    Output: A string, representing the smallest box.
    """
    return min(values, key=lambda box: 10 if len(values[box]) == 1 else len(values[box]))

### ------------------------------------------------------------------------------------------- ###
### ------------------------------------------------------------------------------------------- ###
### ------------------------------------------------------------------------------------------- ###

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    return search(values)

### ------------------------------------------------------------------------------------------- ###
### ------------------------------------------------------------------------------------------- ###
### ------------------------------------------------------------------------------------------- ###

# begin globally defined variables
rows = 'ABCDEFGHI'
cols = '123456789'
boxes = cross(rows, cols)
row_units = [cross(row, cols) for row in rows]
col_units = [cross(rows, col) for col in cols]
square_units = [cross(xs, ys) for xs in ['ABC', 'DEF', 'GHI'] for ys in ['123', '456', '789']]
diag_tuples = [(row + col, row + str(abs(c - 9))) for r, row in enumerate(rows) for c, col in enumerate(cols) if r == c]
diag_units = [list(map(lambda t: t[0], diag_tuples)), list(map(lambda t: t[1], diag_tuples))]
units = row_units + col_units + square_units + diag_units
boxdict = {box: [unit for unit in units if box in unit] for box in boxes}
peers = {box: set(chain(*boxdict[box])) - set([box]) for box in boxes}
# end globally defined variables

if __name__ == '__main__':

    g1 = '9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................'
    g2 = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    g3 = '.......21.9...67.....27....8.1.679.............431.6.8....32.....75...1.48.......'
    g4 = '267584391159362748834917526496738215312495687578621439643159872925873164781246953'
    g5 = '..7.....11..3..74...........9..3..1.....................3....7....8...6.7..2..95.'

    display(solve(g1))
    display(solve(g2))
    display(solve(g3))
    display(solve(g4))
    display(solve(g5))

### ------------------------------------------------------------------------------------------- ###
### ------------------------------------------------------------------------------------------- ###
### ------------------------------------------------------------------------------------------- ###
