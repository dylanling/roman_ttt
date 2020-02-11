#!/usr/bin/env python

import json
import sys

"""
A state is characterized by a board position and whether or not it is X's turn to move.

A state is equal to another state if the board positions are symmetrically equivalent (in the same group),
and if the turn is the same.
"""

X, O, E = "X", "O", "E"
EMPTY_BOARD = ((E, E, E), (E, E, E), (E, E, E))
STARTING_STATE = (EMPTY_BOARD, True)
WINNING_POSITIONS = {
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
}


def to_string(state):
    board_state, x_turn = state
    board = "\n---------\n".join([" | ".join(board_state[i]) for i in range(3)])
    return f"{board}\nTurn: {X if x_turn else O}\n"


def flatten(board_state):
    return sum(board_state, ())


def unflatten(flattened):
    return (flattened[:3], flattened[3:6], flattened[6:])


def replace(flat, idx, token):
    return tuple(token if idx == i else value for i, value in enumerate(flat))


def symmetry_group(board_state):
    # Reflections
    up_down = board_state[::-1]
    left_right = tuple(row[::-1] for row in board_state)
    diagonal = tuple(zip(*board_state))
    antidiagonal = tuple(zip(*tuple(row[::-1] for row in up_down)))

    # Rotations
    ninety_degrees = tuple(zip(*up_down))
    one_hundred_eighty_degrees = tuple(zip(*ninety_degrees[::-1]))
    two_hundred_seventy_degrees = tuple(zip(*one_hundred_eighty_degrees[::-1]))

    symmetries = {
        board_state,
        up_down,
        left_right,
        diagonal,
        antidiagonal,
        ninety_degrees,
        one_hundred_eighty_degrees,
        two_hundred_seventy_degrees,
    }

    return sorted(symmetries)[0]


def winner(board_state):
    xs, os = tuple(
        tuple(i for i, token in enumerate(flatten(board_state)) if token == symbol)
        for symbol in (X, O)
    )
    if xs in WINNING_POSITIONS:
        return X
    elif os in WINNING_POSITIONS:
        return O
    return None


def transitions_classic(state):
    board_state, x_turn = state
    if winner(board_state):
        return set()

    cells = flatten(board_state)
    token = X if x_turn else O
    token_additions = [
        (idx, replace(cells, idx, token))
        for idx, value in enumerate(cells)
        if value == E
    ]
    new_board_states = [new_board_state for _, new_board_state in token_additions]
    new_board_states = set(
        symmetry_group(unflatten(new_board_state))
        for new_board_state in new_board_states
    )
    return {(new_board_state, not x_turn) for new_board_state in new_board_states}


def transitions_roman(state):
    board_state, x_turn = state
    if winner(board_state):
        return set()

    cells = flatten(board_state)
    x_count = sum(1 if token == X else 0 for token in cells)
    o_count = sum(1 if token == O else 0 for token in cells)

    token = X if x_turn else O
    token_additions = [
        (idx, replace(cells, idx, token))
        for idx, value in enumerate(cells)
        if value == E
    ]

    if o_count == 3:  # Assumes X goes first
        token_removals = [
            [
                replace(new_board_state, idx, E)
                for idx, value in enumerate(new_board_state)
                if value == token and idx != new_idx
            ]
            for new_idx, new_board_state in token_additions
        ]
        new_board_states = [
            new_board_state for nested in token_removals for new_board_state in nested
        ]
    else:
        new_board_states = [new_board_state for _, new_board_state in token_additions]
    new_board_states = set(
        symmetry_group(unflatten(new_board_state))
        for new_board_state in new_board_states
    )
    return {(new_board_state, not x_turn) for new_board_state in new_board_states}


def full_graph(transitions, root=STARTING_STATE):
    traversed = set()
    graph = dict()

    def dfs(state):
        if state in traversed:
            return
        traversed.add(state)
        graph[state] = transitions(state)
        for child in graph[state]:
            dfs(child)

    dfs(root)
    return graph


def colors(graph, root):
    red_states = set()
    blue_states = set()

    done_painting = False

    def paint():
        traversed = set()
        reds, blues = len(red_states), len(blue_states)

        def dfs(state):
            if state in traversed:
                return
            traversed.add(state)
            board_state, x_turn = state
            winning_token = winner(board_state)

            if (
                winning_token == X
                or (any(child in red_states for child in graph[state]) and x_turn)
                or (all(child in red_states for child in graph[state]) and graph[state])
            ):
                red_states.add(state)
            elif (
                winning_token == O
                or (any(child in blue_states for child in graph[state]) and not x_turn)
                or (
                    all(child in blue_states for child in graph[state]) and graph[state]
                )
            ):
                blue_states.add(state)

            for child in graph[state]:
                dfs(child)

        dfs(root)
        return reds == len(red_states) and blues == len(blue_states)

    while not done_painting:
        done_painting = paint()

    return red_states, blue_states


def state_id(state):
    board_state, x_turn = state
    return "".join(flatten(board_state)) + (X if x_turn else O)


game = "classic"
games = {"classic": transitions_classic, "roman": transitions_roman}
if len(sys.argv) >= 2:
    game = sys.argv[1]

filename = "graph.js"

graph = full_graph(games[game])
red, blue = colors(graph, STARTING_STATE)

empty_counts = {}
for board_state, _ in graph:
    count = flatten(board_state).count(E)
    if count not in empty_counts:
        empty_counts[count] = 0
    empty_counts[count] += 1

steps = {
    empties: [x * (1 / n) for x in range(n)] for empties, n in empty_counts.items()
}
adjusted_steps = {
    empties: iter(
        [
            (p + (1 / (2 * len(points))))
            if len(points) % 2 == 0
            else (p + (0.5 - points[len(points) // 2]))
            for p in points
        ]
    )
    for empties, points in steps.items()
}

nodes = [
    {
        "id": state_id(state),
        "board_state": "".join(flatten(state[0])),
        "x_turn": state[1],
        "x_win_guaranteed": state in red,
        "o_win_guaranteed": state in blue,
        "x_win": winner(state[0]) == X,
        "o_win": winner(state[0]) == O,
        "empty_squares": state_id(state).count(E),
        "x_default_tree": next(adjusted_steps[state_id(state).count(E)]),
        "y_default_tree": 1 - (state_id(state).count(E) / 10.0),
    }
    for state in graph
]
edges = [
    item
    for sublist in [
        [
            {
                "id": state_id(state) + state_id(child),
                "source": state_id(state),
                "target": state_id(child),
            }
            for child in children
        ]
        for state, children in graph.items()
    ]
    for item in sublist
]
data = {"nodes": nodes, "edges": edges}

print(f"writing graph to {filename}")
print(f"made {len(nodes)} nodes and {len(edges)} edges")

with open(filename, "w", encoding="utf-8") as f:
    f.write("var graph = ")
    json.dump(data, f, indent=4)
    f.write(";")
