import unittest
from Sprint2 import SolitaireGame


class TestSolitaireGame(unittest.TestCase):

    def test_new_game_english_board_center_is_empty(self):
        game = SolitaireGame(board_size=7, board_type="English")

        self.assertEqual(game.board_size, 7)
        self.assertEqual(game.board_type, "English")
        self.assertEqual(game.get_cell(3, 3), 0)  # center hole should be empty

    def test_new_game_diamond_board_center_is_empty(self):
        game = SolitaireGame(board_size=7, board_type="Diamond")

        self.assertEqual(game.board_size, 7)
        self.assertEqual(game.board_type, "Diamond")
        self.assertEqual(game.get_cell(3, 3), 0)

    def test_valid_move_updates_board_correctly(self):
        game = SolitaireGame(board_size=7, board_type="English")

        # On a standard English board:
        # (3,1) -> (3,3) jumps over (3,2)
        self.assertEqual(game.get_cell(3, 1), 1)
        self.assertEqual(game.get_cell(3, 2), 1)
        self.assertEqual(game.get_cell(3, 3), 0)

        moved = game.try_move((3, 1), (3, 3))
        self.assertTrue(moved)

        self.assertEqual(game.get_cell(3, 1), 0)  # source now empty
        self.assertEqual(game.get_cell(3, 2), 0)  # jumped marble removed
        self.assertEqual(game.get_cell(3, 3), 1)  # destination now filled

    def test_invalid_move_is_rejected(self):
        game = SolitaireGame(board_size=7, board_type="English")

        # Invalid because destination is not exactly 2 spaces away
        moved = game.try_move((3, 1), (3, 2))
        self.assertFalse(moved)

        # Board should remain unchanged
        self.assertEqual(game.get_cell(3, 1), 1)
        self.assertEqual(game.get_cell(3, 2), 1)
        self.assertEqual(game.get_cell(3, 3), 0)

    def test_marble_count_decreases_after_valid_move(self):
        game = SolitaireGame(board_size=7, board_type="English")
        before = game.count_marbles()

        moved = game.try_move((3, 1), (3, 3))
        after = game.count_marbles()

        self.assertTrue(moved)
        self.assertEqual(after, before - 1)

    def test_game_is_not_over_at_start_of_new_game(self):
        game = SolitaireGame(board_size=7, board_type="English")
        self.assertFalse(game.is_game_over())

    def test_performance_rating_outstanding_for_one_marble(self):
        game = SolitaireGame(board_size=7, board_type="English")

        # Force a simple one-marble board state
        for r in range(len(game.board)):
            for c in range(len(game.board[r])):
                if game.board[r][c] is not None:
                    game.board[r][c] = 0

        game.board[3][3] = 1
        self.assertEqual(game.count_marbles(), 1)
        self.assertEqual(game.performance_rating(), "Outstanding")

    def test_reset_changes_board_type(self):
        game = SolitaireGame(board_size=7, board_type="English")
        game.reset(board_size=7, board_type="Diamond")

        self.assertEqual(game.board_type, "Diamond")
        self.assertEqual(game.board_size, 7)
        self.assertEqual(game.get_cell(3, 3), 0)

    def test_invalid_english_board_size_raises_error(self):
        with self.assertRaises(ValueError):
            SolitaireGame(board_size=5, board_type="English")

    def test_invalid_hexagon_board_size_raises_error(self):
        with self.assertRaises(ValueError):
            SolitaireGame(board_size=5, board_type="Hexagon")


if __name__ == "__main__":
    unittest.main()