import unittest
from Sprint2 import SolitaireGame


class TestSolitaireGame(unittest.TestCase):

    def test_new_game_english_board_center_is_empty(self):
        game = SolitaireGame(board_size=7, board_type="English")
        self.assertEqual(game.get_cell(3, 3), 0)

    def test_valid_move_updates_board_correctly(self):
        game = SolitaireGame(board_size=7, board_type="English")
        moved = game.try_move((3, 1), (3, 3))
        self.assertTrue(moved)
        self.assertEqual(game.get_cell(3, 1), 0)
        self.assertEqual(game.get_cell(3, 2), 0)
        self.assertEqual(game.get_cell(3, 3), 1)

    def test_game_is_over_when_no_valid_moves_exist(self):
        game = SolitaireGame(board_size=7, board_type="English")

        for r in range(len(game.board)):
            for c in range(len(game.board[r])):
                if game.board[r][c] is not None:
                    game.board[r][c] = 0

        game.board[3][3] = 1
        self.assertTrue(game.is_game_over())


if __name__ == "__main__":
    unittest.main()