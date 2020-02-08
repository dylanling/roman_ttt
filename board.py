X, O, E = "X", "O", " "
EMPTY_BOARD = ((E, E, E), (E, E, E), (E, E, E))
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
    return "\n---------\n".join([" | ".join(state[i]) for i in range(3)])


def flatten(state):
    return sum(state, ())


def unflatten(flattened):
    return (flattened[:3], flattened[3:6], flattened[6:])


def replace(flat, idx, token):
    return tuple(token if idx == i else value for i, value in enumerate(flat))


def symmetry_group(state):
    # Reflections
    up_down = state[::-1]
    left_right = tuple(row[::-1] for row in state)
    diagonal = tuple(zip(*state))
    antidiagonal = tuple(zip(*tuple(row[::-1] for row in up_down)))

    # Rotations
    ninety_degrees = tuple(zip(*up_down))
    one_hundred_eighty_degrees = tuple(zip(*ninety_degrees[::-1]))
    two_hundred_seventy_degrees = tuple(zip(*one_hundred_eighty_degrees[::-1]))

    symmetries = {
        state,
        up_down,
        left_right,
        diagonal,
        antidiagonal,
        ninety_degrees,
        one_hundred_eighty_degrees,
        two_hundred_seventy_degrees,
    }

    return sorted(symmetries)[0]


def is_won(state):
    xs, os = tuple(
        tuple(i for i, token in enumerate(flatten(state)) if token == symbol)
        for symbol in (X, O)
    )
    return xs in WINNING_POSITIONS or os in WINNING_POSITIONS


def transitions(state):
    if is_won(state):
        return set()

    cells = flatten(state)
    x_count = sum(1 if token == X else 0 for token in cells)
    o_count = sum(1 if token == O else 0 for token in cells)

    token = X if x_count == o_count else O  # Assume X goes first
    token_additions = [
        (idx, replace(cells, idx, token))
        for idx, value in enumerate(cells)
        if value == E
    ]

    if o_count == 3:  # Assume X goes first
        token_removals = [
            [
                replace(new_state, idx, E)
                for idx, value in enumerate(new_state)
                if value == token and idx != new_idx
            ]
            for new_idx, new_state in token_additions
        ]
        new_states = [new_state for nested in token_removals for new_state in nested]
    else:
        new_states = [new_state for _, new_state in token_additions]
    return set(symmetry_group(unflatten(new_state)) for new_state in new_states)
