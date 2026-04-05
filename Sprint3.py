import tkinter as tk
from tkinter import messagebox
from dataclasses import dataclass
from typing import List, Optional, Tuple
import random


Coord = Tuple[int, int]


@dataclass(frozen=True)
class Move:
    src: Coord
    mid: Coord
    dst: Coord


class SolitaireBoard:
    """
    Shared board/game-state logic.
    This class knows nothing about Tkinter.
    """

    DIRECTIONS = [
        (-1, 0), (1, 0), (0, -1), (0, 1),      # orthogonal
        (-1, -1), (-1, 1), (1, -1), (1, 1)     # diagonal
    ]

    def __init__(self, board_size: int = 7, board_type: str = "English"):
        self.board_size = board_size
        self.board_type = board_type
        self.board: List[List[Optional[int]]] = []
        self.reset(board_size, board_type)

    def reset(self, board_size: Optional[int] = None, board_type: Optional[str] = None) -> None:
        if board_size is not None:
            self.board_size = board_size
        if board_type is not None:
            self.board_type = board_type

        if self.board_type == "English":
            self.board = self._make_english_board(self.board_size)
        elif self.board_type == "Diamond":
            self.board = self._make_diamond_board(self.board_size)
        elif self.board_type == "Hexagon":
            self.board = self._make_hexagon_board(self.board_size)
        else:
            raise ValueError(f"Unsupported board type: {self.board_type}")

    def _make_english_board(self, size: int) -> List[List[Optional[int]]]:
        if size != 7:
            raise ValueError("English board currently supports size 7.")

        board = [[1 for _ in range(size)] for _ in range(size)]
        invalid_cells = [
            (0, 0), (0, 1), (1, 0), (1, 1),
            (0, 5), (0, 6), (1, 5), (1, 6),
            (5, 0), (5, 1), (6, 0), (6, 1),
            (5, 5), (5, 6), (6, 5), (6, 6)
        ]
        for r, c in invalid_cells:
            board[r][c] = None

        board[3][3] = 0
        return board

    def _make_diamond_board(self, size: int) -> List[List[Optional[int]]]:
        if size < 5 or size % 2 == 0:
            raise ValueError("Diamond board size must be an odd number >= 5.")

        center = size // 2
        board = [[None for _ in range(size)] for _ in range(size)]

        for r in range(size):
            for c in range(size):
                if abs(r - center) + abs(c - center) <= center:
                    board[r][c] = 1

        board[center][center] = 0
        return board

    def _make_hexagon_board(self, size: int) -> List[List[Optional[int]]]:
        if size != 7:
            raise ValueError("Hexagon board currently supports size 7.")

        mask_rows = [
            "..###..",
            ".#####.",
            "#######",
            "#######",
            "#######",
            ".#####.",
            "..###..",
        ]

        board = [[None for _ in range(7)] for _ in range(7)]
        for r in range(7):
            for c in range(7):
                if mask_rows[r][c] == "#":
                    board[r][c] = 1

        board[3][3] = 0
        return board

    def in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < len(self.board) and 0 <= col < len(self.board[0])

    def get_cell(self, row: int, col: int) -> Optional[int]:
        return self.board[row][col]

    def count_marbles(self) -> int:
        return sum(1 for row in self.board for cell in row if cell == 1)

    def valid_moves(self) -> List[Move]:
        moves: List[Move] = []
        rows = len(self.board)
        cols = len(self.board[0])

        for r in range(rows):
            for c in range(cols):
                if self.get_cell(r, c) != 1:
                    continue

                for dr, dc in self.DIRECTIONS:
                    mid_r, mid_c = r + dr, c + dc
                    dst_r, dst_c = r + 2 * dr, c + 2 * dc

                    if not self.in_bounds(mid_r, mid_c) or not self.in_bounds(dst_r, dst_c):
                        continue

                    if self.get_cell(mid_r, mid_c) == 1 and self.get_cell(dst_r, dst_c) == 0:
                        moves.append(Move((r, c), (mid_r, mid_c), (dst_r, dst_c)))

        return moves

    def is_valid_move(self, src: Coord, dst: Coord) -> Optional[Move]:
        src_r, src_c = src
        dst_r, dst_c = dst

        if not self.in_bounds(src_r, src_c) or not self.in_bounds(dst_r, dst_c):
            return None
        if self.get_cell(src_r, src_c) != 1:
            return None
        if self.get_cell(dst_r, dst_c) != 0:
            return None

        dr = dst_r - src_r
        dc = dst_c - src_c

        orthogonal = (abs(dr) == 2 and dc == 0) or (abs(dc) == 2 and dr == 0)
        diagonal = abs(dr) == 2 and abs(dc) == 2

        if not (orthogonal or diagonal):
            return None

        mid_r, mid_c = src_r + dr // 2, src_c + dc // 2
        if self.get_cell(mid_r, mid_c) != 1:
            return None

        return Move((src_r, src_c), (mid_r, mid_c), (dst_r, dst_c))

    def apply_move(self, move: Move) -> None:
        src_r, src_c = move.src
        mid_r, mid_c = move.mid
        dst_r, dst_c = move.dst

        self.board[src_r][src_c] = 0
        self.board[mid_r][mid_c] = 0
        self.board[dst_r][dst_c] = 1

    def try_move(self, src: Coord, dst: Coord) -> bool:
        move = self.is_valid_move(src, dst)
        if move is None:
            return False
        self.apply_move(move)
        return True

    def is_game_over(self) -> bool:
        return len(self.valid_moves()) == 0

    def performance_rating(self) -> str:
        marbles = self.count_marbles()
        if marbles == 1:
            return "Outstanding"
        if marbles == 2:
            return "Very Good"
        if marbles == 3:
            return "Good"
        return "Average"

    def randomize_state(self, steps: int = 10) -> int:
        """
        Randomize the board by making a number of random valid moves.
        Returns the number of moves actually applied.
        """
        applied = 0
        for _ in range(steps):
            moves = self.valid_moves()
            if not moves:
                break
            move = random.choice(moves)
            self.apply_move(move)
            applied += 1
        return applied


class GameMode:
    """
    Base class for manual and automated modes.
    Shared behavior goes here.
    """

    def __init__(self, board: SolitaireBoard):
        self.board = board

    def start_new_game(self, board_size: int, board_type: str) -> None:
        self.board.reset(board_size, board_type)

    def is_over(self) -> bool:
        return self.board.is_game_over()

    def mode_name(self) -> str:
        raise NotImplementedError


class ManualGameMode(GameMode):
    """
    Manual mode: user selects and plays moves.
    """

    def mode_name(self) -> str:
        return "Manual"

    def make_move(self, src: Coord, dst: Coord) -> bool:
        return self.board.try_move(src, dst)

    def randomize(self, steps: int = 10) -> int:
        return self.board.randomize_state(steps)


class AutomatedGameMode(GameMode):
    """
    Automated mode: program chooses moves automatically.
    """

    def mode_name(self) -> str:
        return "Automated"

    def choose_move(self) -> Optional[Move]:
        moves = self.board.valid_moves()
        if not moves:
            return None
        return random.choice(moves)

    def make_move(self) -> bool:
        move = self.choose_move()
        if move is None:
            return False
        self.board.apply_move(move)
        return True


class SolitaireGUI(tk.Tk):
    CELL_SIZE = 60
    PADDING = 20

    def __init__(self):
        super().__init__()
        self.title("Sprint 3 Solitaire")

        self.board_size_var = tk.IntVar(value=7)
        self.board_type_var = tk.StringVar(value="English")
        self.game_mode_var = tk.StringVar(value="Manual")
        self.status_var = tk.StringVar(value="Welcome to Solitaire")

        self.board = SolitaireBoard(7, "English")
        self.game_mode: GameMode = ManualGameMode(self.board)

        self.selected: Optional[Coord] = None
        self.autoplay_running = False

        self._build_ui()
        self._draw_board()
        self._update_status("Ready.")

    def _build_ui(self) -> None:
        container = tk.Frame(self, padx=12, pady=12)
        container.pack(fill="both", expand=True)

        controls = tk.Frame(container)
        controls.grid(row=0, column=0, sticky="nw", padx=(0, 15))

        size_frame = tk.Frame(controls)
        size_frame.pack(anchor="w", pady=(0, 8))
        tk.Label(size_frame, text="Board size").pack(side="left")
        tk.Spinbox(
            size_frame,
            from_=5,
            to=9,
            increment=2,
            width=5,
            textvariable=self.board_size_var
        ).pack(side="left", padx=(8, 0))

        type_frame = tk.LabelFrame(controls, text="Board Type")
        type_frame.pack(anchor="w", fill="x", pady=(0, 8))
        for board_type in ["English", "Hexagon", "Diamond"]:
            tk.Radiobutton(
                type_frame,
                text=board_type,
                value=board_type,
                variable=self.board_type_var
            ).pack(anchor="w")

        mode_frame = tk.LabelFrame(controls, text="Game Mode")
        mode_frame.pack(anchor="w", fill="x", pady=(0, 8))
        for mode in ["Manual", "Automated"]:
            tk.Radiobutton(
                mode_frame,
                text=mode,
                value=mode,
                variable=self.game_mode_var
            ).pack(anchor="w")

        tk.Button(controls, text="New Game", width=12, command=self.start_new_game).pack(anchor="w", pady=(4, 6))
        tk.Button(controls, text="Randomize", width=12, command=self.randomize_manual_game).pack(anchor="w", pady=(0, 6))
        tk.Button(controls, text="Autoplay", width=12, command=self.start_autoplay).pack(anchor="w", pady=(0, 10))

        tk.Label(
            controls,
            textvariable=self.status_var,
            justify="left",
            wraplength=240
        ).pack(anchor="w", pady=(6, 0))

        self.canvas = tk.Canvas(container, width=520, height=520, bg="white", highlightthickness=1)
        self.canvas.grid(row=0, column=1, sticky="nsew")
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)

    def _set_game_mode(self) -> None:
        mode_name = self.game_mode_var.get()
        if mode_name == "Manual":
            self.game_mode = ManualGameMode(self.board)
        else:
            self.game_mode = AutomatedGameMode(self.board)

    def start_new_game(self) -> None:
        try:
            self.autoplay_running = False
            self.selected = None
            board_size = self.board_size_var.get()
            board_type = self.board_type_var.get()
            self._set_game_mode()
            self.game_mode.start_new_game(board_size, board_type)
            self._draw_board()
            self._update_status("New game started.")
        except ValueError as error:
            messagebox.showerror("Invalid Settings", str(error))

    def randomize_manual_game(self) -> None:
        if not isinstance(self.game_mode, ManualGameMode):
            self._update_status("Randomize is only available in Manual mode.")
            return

        applied = self.game_mode.randomize(steps=8)
        self.selected = None
        self._draw_board()

        if self.game_mode.is_over():
            self._update_status(f"Randomized with {applied} move(s). Game Over.")
        else:
            self._update_status(f"Randomized with {applied} move(s).")

    def start_autoplay(self) -> None:
        if not isinstance(self.game_mode, AutomatedGameMode):
            self._update_status("Switch to Automated mode to use Autoplay.")
            return

        if self.game_mode.is_over():
            self._update_status("Automated game is already over.")
            return

        self.autoplay_running = True
        self._autoplay_step()

    def _autoplay_step(self) -> None:
        if not self.autoplay_running:
            return

        if not isinstance(self.game_mode, AutomatedGameMode):
            self.autoplay_running = False
            return

        moved = self.game_mode.make_move()
        self.selected = None
        self._draw_board()

        if not moved or self.game_mode.is_over():
            self.autoplay_running = False
            self._update_status("Autoplay finished. Automated game is over.")
            return

        self._update_status("Autoplay moved one step.")
        self.after(350, self._autoplay_step)

    def on_canvas_click(self, event) -> None:
        if not isinstance(self.game_mode, ManualGameMode):
            self._update_status("Board clicks are disabled in Automated mode.")
            return

        cell = self._pixel_to_cell(event.x, event.y)
        if cell is None:
            return

        row, col = cell
        cell_value = self.board.get_cell(row, col)

        if cell_value == 1:
            self.selected = cell
            self._draw_board()
            self._update_status("Marble selected.")
            return

        if cell_value == 0 and self.selected is not None:
            moved = self.game_mode.make_move(self.selected, cell)
            if moved:
                self.selected = None
                self._draw_board()
                if self.game_mode.is_over():
                    self._update_status("Move completed. Manual game is over.")
                else:
                    self._update_status("Move completed.")
            else:
                self._update_status("Invalid move.")

    def _pixel_to_cell(self, x: int, y: int) -> Optional[Coord]:
        rows = len(self.board.board)
        cols = len(self.board.board[0])

        x0 = x - self.PADDING
        y0 = y - self.PADDING
        if x0 < 0 or y0 < 0:
            return None

        col = x0 // self.CELL_SIZE
        row = y0 // self.CELL_SIZE

        if not (0 <= row < rows and 0 <= col < cols):
            return None

        if self.board.get_cell(int(row), int(col)) is None:
            return None

        return int(row), int(col)

    def _update_status(self, extra_message: str = "") -> None:
        lines = [
            f"Mode: {self.game_mode.mode_name()}",
            f"Board size: {self.board.board_size}",
            f"Board type: {self.board.board_type}",
            f"Marbles left: {self.board.count_marbles()}",
        ]

        if self.selected is not None:
            lines.append(f"Selected: {self.selected}")

        if self.board.is_game_over():
            if isinstance(self.game_mode, AutomatedGameMode):
                lines.append("Automated game over")
            else:
                lines.append("Manual game over")
            lines.append(f"Rating: {self.board.performance_rating()}")

        if extra_message:
            lines.append(extra_message)

        self.status_var.set("\n".join(lines))

    def _draw_board(self) -> None:
        self.canvas.delete("all")

        rows = len(self.board.board)
        cols = len(self.board.board[0])

        canvas_width = self.PADDING * 2 + cols * self.CELL_SIZE
        canvas_height = self.PADDING * 2 + rows * self.CELL_SIZE
        self.canvas.config(width=canvas_width, height=canvas_height)

        for r in range(rows + 1):
            y = self.PADDING + r * self.CELL_SIZE
            self.canvas.create_line(self.PADDING, y, self.PADDING + cols * self.CELL_SIZE, y)

        for c in range(cols + 1):
            x = self.PADDING + c * self.CELL_SIZE
            self.canvas.create_line(x, self.PADDING, x, self.PADDING + rows * self.CELL_SIZE)

        self.canvas.create_text(
            self.PADDING,
            8,
            anchor="w",
            text=f"{self.board.board_type} board, size {self.board.board_size}, mode {self.game_mode.mode_name()}"
        )

        for r in range(rows):
            for c in range(cols):
                value = self.board.get_cell(r, c)

                x1 = self.PADDING + c * self.CELL_SIZE
                y1 = self.PADDING + r * self.CELL_SIZE
                x2 = x1 + self.CELL_SIZE
                y2 = y1 + self.CELL_SIZE

                if value is None:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#eeeeee", outline="#eeeeee")
                    continue

                if self.selected == (r, c):
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#fff2a8", outline="")

                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2
                radius = self.CELL_SIZE * 0.22

                if value == 1:
                    self.canvas.create_oval(
                        cx - radius, cy - radius, cx + radius, cy + radius,
                        fill="black"
                    )
                else:
                    self.canvas.create_oval(
                        cx - radius, cy - radius, cx + radius, cy + radius,
                        outline="black", fill="white"
                    )


if __name__ == "__main__":
    app = SolitaireGUI()
    app.mainloop()
