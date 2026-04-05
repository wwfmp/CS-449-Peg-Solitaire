import unittest
from Sprint3 import SolitaireBoard, ManualGameMode, AutomatedGameMode


class TestManualGameMode(unittest.TestCase):

    def test_manual_mode_valid_move_updates_board(self):
        board = SolitaireBoard(board_size=7, board_type="English")
        mode = ManualGameMode(board)

        self.assertEqual(board.get_cell(3, 1), 1)
        self.assertEqual(board.get_cell(3, 2), 1)
        self.assertEqual(board.get_cell(3, 3), 0)

        moved = mode.make_move((3, 1), (3, 3))
        self.assertTrue(moved)

        self.assertEqual(board.get_cell(3, 1), 0)
        self.assertEqual(board.get_cell(3, 2), 0)
        self.assertEqual(board.get_cell(3, 3), 1)

    def test_manual_mode_invalid_move_is_rejected(self):
        board = SolitaireBoard(board_size=7, board_type="English")
        mode = ManualGameMode(board)

        moved = mode.make_move((3, 1), (3, 2))
        self.assertFalse(moved)

        self.assertEqual(board.get_cell(3, 1), 1)
        self.assertEqual(board.get_cell(3, 2), 1)
        self.assertEqual(board.get_cell(3, 3), 0)

    def test_manual_mode_randomize_changes_or_advances_board(self):
        board = SolitaireBoard(board_size=7, board_type="English")
        mode = ManualGameMode(board)

        before = board.count_marbles()
        applied = mode.randomize(steps=3)
        after = board.count_marbles()

        self.assertGreaterEqual(applied, 0)
        self.assertLessEqual(after, before)

    def test_manual_mode_game_over_detected(self):
        board = SolitaireBoard(board_size=7, board_type="English")
        mode = ManualGameMode(board)

        for r in range(len(board.board)):
            for c in range(len(board.board[r])):
                if board.board[r][c] is not None:
                    board.board[r][c] = 0

        board.board[3][3] = 1
        self.assertTrue(mode.is_over())


class TestAutomatedGameMode(unittest.TestCase):

    def test_automated_mode_choose_move_returns_valid_move(self):
        board = SolitaireBoard(board_size=7, board_type="English")
        mode = AutomatedGameMode(board)

        move = mode.choose_move()
        self.assertIsNotNone(move)

        if move is not None:
            self.assertEqual(board.get_cell(move.src[0], move.src[1]), 1)
            self.assertEqual(board.get_cell(move.mid[0], move.mid[1]), 1)
            self.assertEqual(board.get_cell(move.dst[0], move.dst[1]), 0)

    def test_automated_mode_make_move_changes_board(self):
        board = SolitaireBoard(board_size=7, board_type="English")
        mode = AutomatedGameMode(board)

        before = board.count_marbles()
        moved = mode.make_move()
        after = board.count_marbles()

        self.assertTrue(moved)
        self.assertEqual(after, before - 1)

    def test_automated_mode_game_over_detected(self):
        board = SolitaireBoard(board_size=7, board_type="English")
        mode = AutomatedGameMode(board)

        for r in range(len(board.board)):
            for c in range(len(board.board[r])):
                if board.board[r][c] is not None:
                    board.board[r][c] = 0

        board.board[3][3] = 1
        self.assertTrue(mode.is_over())

    def test_automated_mode_make_move_returns_false_when_no_moves_exist(self):
        board = SolitaireBoard(board_size=7, board_type="English")
        mode = AutomatedGameMode(board)

        for r in range(len(board.board)):
            for c in range(len(board.board[r])):
                if board.board[r][c] is not None:
                    board.board[r][c] = 0

        board.board[3][3] = 1

        self.assertFalse(mode.make_move())


if __name__ == "__main__":
    unittest.main()
