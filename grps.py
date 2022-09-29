from __future__ import annotations

from typing import Tuple, List, Dict, NoReturn, Union, Optional
from random import randint
from itertools import product
from networkx import DiGraph as DG
import networkx as nx
import pydot
import matplotlib.pyplot as plt

_EDGE = Tuple[int, int]
_NAMED_EDGE = Tuple[str, str]


class GRPS:
    """
    Generalized Rock Paper Scissors

    lists of possible games:
        ('scissors', 'paper', 'rock')
        ('scissors', 'paper', 'rock', 'lizard', 'spock')

    one can enter a random list of names and then invent why each node wins over the other node.

    To play the classic rock, paper, scissors game:
        >>> game = GRPS.classic()
        >>> game.play('rock') # single player vs. random draw
        >>> game.play('rock', 'scissors') # player1 vs. player 2

    To play the extended version 'rock, paper, scissors, lizard, spock':
        >>> game = GRPS.spock_version()

    To create a generalized game:

        >>> game = GRPS(7) # or any odd number greater than 2
        >>> game.play(1, 2)

        The numbers denote node indices (0,1,...N-1) for GRPS(N) see below how the winner is resolved

    To provide some names to a generalized game:

        >>> game = GRPS(7)
        >>> game.node_names = ('Jim', 'Dwight', 'Michael', 'Pam', 'Kevin', 'Andy', 'Angela')

        Use the below command to list all the counters:
        >>> game.get_named_edge_indices()

        Create the "verb" one node does to another to counter it. It should be a dict like:
        >>> dct = {(0, 1): 'paper clips', (0, 2): 'nudges', ...}

        Then set it with:
        >>> game.edge_verbs = dct

        And game on!:
        >>> game.play('Jim', 'Dwight')

        One can also use the builder to create the verb one by one
        >>> game.edge_verb_builder()


    Some math:

        For an odd list of nodes [0, 1, 2, ... N], N = 2k+1
        A game G(N) is a graph where every directed edge n0 -> n1 is a counter ('rock' smashes 'scissors')
        The missing n0 <- n1 node is considered as an anti-counter.

        Property 1: Each node n_i will have (N-1)/2 counters and the same number of anti-counters.
        Property 2: The graph G(N) is contained within G(N+2)

        The 'winning' node in an edge (n0, n1) is determined by:
        if both n0, n1 have parity, namely, they are either both odd or both even
        The winner will be max(n0, n1)
        Otherwise: min(n0, n1)

        Source: https://math.stackexchange.com/questions/3229686/generalizing-rock-paper-scissors-game
    """

    def __init__(self, n: int):

        self.n = n
        self.ne = int(self.n * (self.n - 1) / 2)
        assert self.n > 2, f"gRPS is undefined for lists of nodes smaller than 3, got {self.n=}"
        assert self.n % 2 == 1, f"numebr of nodes must be odd, got {self.n=}"

        self._edge_verbs = None
        self._node_names = None

    @classmethod
    def classic(cls) -> GRPS:
        """the classic rock, paper, scissors"""
        game = GRPS(3)
        game.node_names = ('scissors', 'paper', 'rock')
        game.edge_verbs = {(0, 1): 'cuts', (1, 2): 'wraps', (2, 0): 'smashes'}
        return game

    @classmethod
    def spock_version(cls) -> GRPS:
        """the extended version"""
        game = GRPS(5)
        game.node_names = ('scissors', 'paper', 'rock', 'lizard', 'spock')
        game.edge_verbs = {**GRPS.classic().edge_verbs, **{(0, 3): 'cuts', (1, 4): 'proves', (2, 3): 'smashes',
                                                           (3, 1): 'eats', (3, 4): 'poisons', (4, 0): 'breaks',
                                                           (4, 2): 'vaporizes'}}
        return game

    @classmethod
    def the_office_version(cls) -> GRPS:
        game = GRPS(7)
        game.node_names = ('Jim', 'Dwight', 'Michael', 'Pam', 'Kevin', 'Andy', 'Angela')
        game.edge_verbs = {(0, 1): 'fools',
                           (0, 3): 'marries',
                           (0, 5): 'triggers',
                           (1, 2): 'annoys',
                           (1, 4): 'insults',
                           (1, 6): 'courts',
                           (2, 0): 'ruins sale for',
                           (2, 3): 'sexually harasses',
                           (2, 5): 'ignores',
                           (3, 1): 'becomes friends with',
                           (3, 4): 'is disgusted by',
                           (3, 6): 'retaliates',
                           (4, 0): 'annoys',
                           (4, 2): 'wants cake from',
                           (4, 5): 'teams up with',
                           (5, 1): 'steals Angels from',
                           (5, 3): 'snobs',
                           (5, 6): 'sings to',
                           (6, 0): 'insults',
                           (6, 2): 'is mad at',
                           (6, 4): 'is disgusted by'}
        return game

    def get_edge_indices(self) -> List[_EDGE]:
        """returns the list of possible 'counter' moves or edges"""

        def f(elem: Tuple[int, int]) -> bool:
            outcome = self._resolve_outcome(elem[0], elem[1])
            return elem[0] == outcome

        return [elem for elem in product(range(self.n), range(self.n)) if f(elem)]

    def get_named_edge_indices(self) -> List[Tuple[_EDGE, _NAMED_EDGE]]:
        """returns the list of possible 'counter' moves and their named edges, if it is defined"""
        if self.node_names is None:
            raise Exception('node_names are None')
        else:
            idx = self.get_edge_indices()
            return list(map(lambda p: (p, (self.node_names[p[0]], self.node_names[p[1]])), idx))

    @property
    def node_names(self) -> List[str]:
        return self._node_names

    @node_names.setter
    def node_names(self, value) -> NoReturn:
        assert len(value) == self.n
        assert len(set(value)) == len(value)
        self._node_names = value

    @property
    def edge_verbs(self) -> Dict[_EDGE, str]:
        return self._edge_verbs

    @edge_verbs.setter
    def edge_verbs(self, value: Dict[_EDGE, str]) -> NoReturn:
        assert len(value) == self.ne
        self._edge_verbs = value

    def edge_verb_builder(self) -> NoReturn:
        if self.node_names is None:
            raise Exception('please define the list of node names first')
        dct = {}
        itr = 0
        for ((i, j), (n0, n1)) in self.get_named_edge_indices():
            itr += 1
            print(f'edge #{itr}/{self.ne}: {i} -> {j}, {n0} vs. {n1}')
            dct[(i, j)] = input(f'enter the verb for {n0} -> {n1}')
        self.edge_verbs = dct
        print('Your game is now complete.')

    def _sample_move(self):
        """samples from the list of available moves"""
        return randint(0, self.n - 1)

    def _resolve_outcome(self, n0: int, n1: int) -> int:
        """
        given 2 indices
        n0 - index of 'left' node
        n1 - index of 'right' node
        will return winning index or -1 when there's a tie"""

        assert 0 <= n0 <= self.n - 1
        assert 0 <= n1 <= self.n - 1

        if n0 == n1:
            return -1
        elif (n0 % 2) == (n1 % 2):
            return max(n0, n1)
        else:
            return min(n0, n1)

    def _play_int(self, i: int, i2: Optional[int] = None) -> Tuple[int, Tuple[int, int]]:
        """returns winning index, and a tuple of the moves (player, pc)"""
        assert 0 <= i < self.n, f"i is not in the game's range. n={self.n}, got {i=}"
        if i2 is None:
            i2 = self._sample_move()
        else:
            assert 0 <= i2 < self.n, f"i2 is not in the game's range. n={self.n}, got {i2=}"

        outcome = self._resolve_outcome(n0=i, n1=i2)
        return outcome, (i, i2)

    def _play_str(self, node: str, node2: Optional[str] = None) -> Tuple[int, Tuple[int, int]]:
        assert node in self.node_names
        if node2 is not None:
            assert node2 in self.node_names
            return self._play_int(self.node_names.index(node), self.node_names.index(node2))
        else:
            return self._play_int(self.node_names.index(node))

    def play(self, move: Union[int, str], move2: Optional[Union[int, str]] = None):
        if isinstance(move, int):
            assert isinstance(move2, int) or move2 is None
            return self._play_int(move, move2)

        elif isinstance(move, str):
            assert isinstance(move2, str) or move2 is None
            assert self.node_names is not None
            assert self.edge_verbs is not None
            (result, (player_idx, pc_idx)) = self._play_str(move, move2)
            player = self.node_names[player_idx]
            pc = self.node_names[pc_idx]

            if result == -1:
                msg = f'{pc} vs. {pc}, tie!'
            elif result == player_idx:
                verb = self.edge_verbs[(player_idx, pc_idx)]
                if move2 is None:
                    msg = f'{player} {verb} {pc}, you win!'
                else:
                    msg = f'{player} {verb} {pc}, player1 wins!'
            else:
                verb = self.edge_verbs[(pc_idx, player_idx)]
                if move2 is None:
                    msg = f'{pc} {verb} {player}, you lose!'
                else:
                    msg = f'{pc} {verb} {player}, player2 wins!'
            print(msg)

    def get_pydot(self):
        graph = pydot.Dot(graph_type='digraph', strict=True)
        for i in range(self.n):
            node = pydot.Node(name=i, label=self.node_names[i])
            graph.add_node(node)
        for i, j in self.get_edge_indices():
            edge = pydot.Edge(i, j, label=self.edge_verbs[(i, j)])
            graph.add_edge(edge)
        return graph

    def get_nx(self):
        graph = DG()
        for i in range(self.n):
            graph.add_node(self.node_names[i])
        for i, j in self.get_edge_indices():
            graph.add_edge(self.node_names[i], self.node_names[j])
        return graph

    def get_nx_edge_labels(self):
        ei = self.get_named_edge_indices()
        ev = self.edge_verbs
        out = {}
        for k, v in ei:
            verb = ev[(k[0], k[1])]
            out[v] = verb
        return out
