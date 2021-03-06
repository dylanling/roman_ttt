# ❌⭕❌⭕❌⭕❌⭕❌

Apparently in Ancient Rome, a variant of tic-tac-toe was played where each player can only have at most three tokens on the board, and after the player's third move, the player would have to move an existing token.

This is a quick experiment to prove this variant is also a drawn game (or rather, that an infinite game can be forced since this variant has no winning terminal states).

## Proof
We can construct a directed graph of all possible game states by drawing edges from a state to all states that can legally follow, starting from the empty board state (for simplicity assume ❌ is always the first player).

Then, color all vertices in the graph as either red, blue, or uncolored. A vertex is colored red if the state leads to a guaranteed win for ❌, and is colored blue if the state leads to a guaranteed win for ⭕. Therefore a vertex V is red if any of the following are true (similar logic applies for determining if a vertex is blue):
- V has no edges to other vertices (terminal/leaf), and the state is already a win for ❌
- It is ❌'s turn at V, and _any_ of V's edges lead to a red vertex (perfect play from ❌ will always make a move towards a guaranteed win if possible).
- It is ⭕'s turn at V, and _all_ of V's edges lead to a red vertex (perfect play from ⭕ will never move towards a guaranteed loss if possible).

We can repeatedly traverse the graph using the above logic to color vertices, until a full traversal no longer colors any previously uncolored vertex.

If at the end of this process the vertex representing the empty board is red, then ❌ can always win with perfect play. If it is blue, then ⭕ can always win with perfect play. If it is uncolored, the game is drawn.


## Optimizations
A 3x3 board has 3^9 = 19683 possible states of ❌, ⭕, or empty cells. This is small enough to trivially compute the graph of states, but we can still apply some easy optimizations.

Firstly, many of those possible states are not relevant, i.e. a state that cannot be legally reached from the empty board state. For example, game states where 3 >= #❌= #⭕>= 0 or 3 >= #❌- 1 = #⭕>= 0 does not hold are invalid. Game states where both players have a three in a row are not valid.

Furthermore, many states are symmetric to other states and can be considered isomorphic for our purposes. The [dihedral group](https://en.wikipedia.org/wiki/Dihedral_group) of a square has 8 members, but it isn't quite right to just divide the number of states by 8. For example, there is only one state for this position:
```
  |   |
---------
  | X |
---------
  |   |
```

However, unlike in normal tic-tac-toe, the board is not enough to represent our game state, since after all 6 tokens have been placed the token count no longers tells us whose turn it is. State therefore must also encode the turn.

Accounting for turn-tracking and symmetry (where each state reduces to the "representative" member of its symmetric group), there are only 744 states in Roman tic-tac-toe, 42 of which are a win for ❌, 21 of which are a win for ⭕, and 137 of which do not lead to a guaranteed win for either player.


## View Graph
#### Get SigmaJS stuff (just dev build)
```
❯ wget https://github.com/jacomyal/sigma.js/releases/download/v1.2.0/build.zip && unzip build.zip && rm build.zip
```

#### Make Graph file
```
❯ ./generate_graph.py <classic or roman>
```

Then open `index.html`. This defaults to a tree view. You can declutter by uncommenting the forceAtlas2 section of the graph visualization.
