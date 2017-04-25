assignments = []

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

# PROBLEM 1: NAKED TWINS

# Using the same units and peers dictionaries from the lectures.
# Using the same reduce_puzzle() function from the lectures.
def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers

    new_values = values.copy()
    naked_twins = []
    for box in new_values:
        if len(new_values[box]) == 2:
            for peer in peers[box]:
                if box < peer and new_values[peer] == new_values[box]:
                    naked_twins.append([box, peer])
    for nt in naked_twins:
        # Find the units that contains these two naked twins
        units = [u for u in unitlist if nt[0] in u and nt[1] in u]
        for unit in units:
            for box in unit:
                if box != nt[0] and box != nt[1]:
                    
                    new_values[box] = new_values[box].replace(new_values[nt[0]][0], '')
                    assign_value(new_values, box, new_values[box]) # viz
                    
                    new_values[box] = new_values[box].replace(new_values[nt[0]][1], '')
                    assign_value(new_values, box, new_values[box]) # viz
                    
    if len([box for box in new_values.keys() if len(new_values[box]) == 0]):
        return False
    return new_values

#PROBLEM 2: DIAGONAL SUDOKU

digits   = '123456789'
rows     = 'ABCDEFGHI'
cols     = digits

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a+b for a in A for b in B]

squares = cross(rows, cols)
unitlist = ([cross(rows, c) for c in cols] +
            [cross(r, cols) for r in rows] +
            [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')])
units = dict((s, [u for u in unitlist if s in u])
             for s in squares)
peers = dict((s, set(sum(units[s],[]))-set([s]))
             for s in squares)

diagonal1 = [a[0]+a[1] for a in zip(rows, cols)]
diagonal2 = [a[0]+a[1] for a in zip(rows, cols[::-1])]
diag_unitlist = unitlist + [diagonal1, diagonal2]
diag_units = dict((s, [u for u in diag_unitlist if s in u])
             for s in squares)
diag_peers = dict((s, set(sum(diag_units[s],[]))-set([s]))
             for s in squares)

def grid_values(grid, show_dots=False):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            if show_dots:
                chars.append('.')
            else:
                chars.append(digits)
    assert len(chars) == 81
    return dict(zip(squares, chars))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in squares)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    print()

def eliminate(values):
    '''
    Goes through all the boxes. If a box has only one available value,
    it will remove this value from all the peers of this box.
    '''
    new_values = values.copy()
    solved_values = [box for box in new_values.keys() if len(new_values[box]) == 1]
    for box in solved_values:
        digit = new_values[box]
        for peer in diag_peers[box]:
            new_values[peer] = new_values[peer].replace(digit,'')
            assign_value(new_values, peer, new_values[peer]) # viz
    return new_values

def only_choice(values):
    '''
    Goes through all the units u. If a unit has a certain value d that will only
    fit in one box of u, it will assign d to this box.
    '''
    new_values = values.copy()
    for unit in diag_unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in new_values[box]]
            if len(dplaces) == 1:
                new_values[dplaces[0]] = digit
                assign_value(new_values, dplaces[0], new_values[dplaces[0]]) # viz
    return new_values

def reduce_puzzle(values):
    '''
    It will apply eliminate and only_choice repeatedly.
    If at any point, there is a box with zero available values, it will return False.
    Otherwise, the loop will stop whenever the sudoku stays the same during one iteration.
    '''
    new_values = values.copy()
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        #display(values)
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in new_values.keys() if len(new_values[box]) == 1])
        # Use the Only Choice Strategy
        new_values = eliminate(new_values)
        # Use the Single Possibility Strategy
        new_values = only_choice(new_values)
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in new_values.keys() if len(new_values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in new_values.keys() if len(new_values[box]) == 0]):
            return False
    return new_values

def search(values):
    '''
    Using depth-first search and propagation, try all possible values.
    At any given point, it picks the box with fewer available values
    (if there is more than one, it will pick some box), and propagate over that box.
    '''
    new_values = reduce_puzzle(values.copy())
    if new_values is False:
        return False ## Failed earlier
    if all(len(new_values[s]) == 1 for s in squares):
        return new_values ## Solved!
    ## Chose the unfilled square s with the fewest possibilities
    n,s = min((len(new_values[s]), s) for s in squares if len(new_values[s]) > 1)
    for value in new_values[s]:
        new_sudoku = new_values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    grid = grid_values(grid)
    return search(grid)

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
        