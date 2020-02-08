from board import EMPTY_BOARD, to_string, transitions


def full_graph():
    known_states = set()
    graph = dict()

    def _populate(state):
        if state in known_states:
            return
        known_states.add(state)
        graph[state] = transitions(state)
        for child in graph[state]:
            _populate(child)

    _populate(EMPTY_BOARD)
    return graph


def has_cycle(graph, root):
    visited = set()

    def _traverse(state):
        if state in visited:
            return True
        visited.add(state)
        children = graph.get(state, ())
        for state in children:
            if _traverse(state):
                return True
        return False

    return _traverse(root)


graph = full_graph()
winning_states = [state for state in graph if not graph[state]]
print(
    f"Full tree has {len(graph)} states, {len(winning_states)} of which are won positions."
)

if has_cycle(graph, EMPTY_BOARD):
    print("Starting from an empty board, an infinitely long game can be forced.")
else:
    print("Starting from an empty board, a win can be forced.")
