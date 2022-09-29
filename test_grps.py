from grps import GRPS
from unittest import TestCase
from typing import Dict


class TestGRPS(TestCase):

    def assert_single_winner(self, game: GRPS, index: int, expected: str):
        self.assertTrue(game.node_names[index] == expected, msg=f'{index}, {expected}')

    def assert_dict_winner(self, game: GRPS, dct: Dict):
        for ((left, right), expected) in dct.items():
            index, _ = game._play_str(left, right)
            self.assert_single_winner(game, index, expected)
            index, _ = game._play_str(right, left)
            self.assert_single_winner(game, index, expected)

    def test_sanity(self):
        game = GRPS.classic()
        dct = {
            ('scissors', 'paper'): 'scissors',
            ('paper', 'scissors'): 'scissors',
            ('paper', 'rock'): 'paper',
            ('rock', 'paper'): 'paper',
            ('rock', 'scissors'): 'rock',
            ('scissors', 'rock'): 'rock',
        }
        self.assert_dict_winner(game, dct)

        game = GRPS.spock_version()
        dct = {
            ('scissors', 'paper'): 'scissors',
            ('scissors', 'lizard'): 'scissors',
            ('paper', 'rock'): 'paper',
            ('paper', 'spock'): 'paper',
            ('paper', 'lizard'): 'lizard',
            ('rock', 'scissors'): 'rock',
            ('rock', 'lizard'): 'rock',
            ('spock', 'lizard'): 'lizard',
            ('spock', 'paper'): 'paper',
            ('spock', 'rock'): 'spock',
            ('spock', 'scissors'): 'spock',
        }
        self.assert_dict_winner(game, dct)

