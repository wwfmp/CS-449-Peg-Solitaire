import tkinter as tk
from tkinter import messagebox
from dataclasses import dataclass
from typing import List, Optional, Tuple


Coord = Tuple[int, int]


@dataclass(frozen=True)
class Move:
    src: Coord
    mid: Coord
    dst: Coord


class SolitaireGame:
    """
    Game logic class for Peg Solitaire.
    This class contains no Tkinter/UI code.
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
            raise ValueError("English board currently supports size 7 in Sprint 2.")
        board = [[1 for _ in range(size)] for _ in range(size)]

        invalid_cells = [
            (0, 0), (0, 1), (1, 0), (1, 1),
            (0, 5), (0, 6), (1, 5), (1, 6),
            (5, 0), (5, 1), (6, 0), (6, 1),
            (5, 5), (5, 6), (6, 5), (6, 6)
        ]

        for r, c in invalid_cells:
            board[r][c] = None

        board[size // 2][size // 2] = 0
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
            raise ValueError("Hexagon board currently supports size 7 in Sprint 2.")

    # More balanced hexagon-like layout for a 7x7 visual grid
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

    # Center hole starts empty
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
        size = len(self.board)

        for r in range(size):
            for c in range(size):
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

        return Move(src, (mid_r, mid_c), dst)

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


class SolitaireGUI(tk.Tk):
    """
    Tkinter UI class.
    This class handles drawing, selection, and button/radio/spinbox events.
    """

    CELL_SIZE = 60
    PADDING = 20

    def __init__(self):
        super().__init__()
        self.title("Sprint 2 Solitaire")

        self.board_size_var = tk.IntVar(value=7)
        self.board_type_var = tk.StringVar(value="English")
        self.status_var = tk.StringVar(value="Welcome to Solitaire")
        self.selected: Optional[Coord] = None

        self.game = SolitaireGame(
            board_size=self.board_size_var.get(),
            board_type=self.board_type_var.get()
        )

        self._build_ui()
        self._draw_board()
        self._update_status()

    def _build_ui(self) -> None:
        container = tk.Frame(self, padx=12, pady=12)
        container.pack(fill="both", expand=True)

        controls = tk.Frame(container)
        controls.grid(row=0, column=0, sticky="nw", padx=(0, 15))

        # Board size
        size_frame = tk.Frame(controls)
        size_frame.pack(anchor="w", pady=(0, 10))
        tk.Label(size_frame, text="Board size").pack(side="left")

        self.size_spinbox = tk.Spinbox(
            size_frame,
            from_=5,
            to=9,
            increment=2,
            width=5,
            textvariable=self.board_size_var
        )
        self.size_spinbox.pack(side="left", padx=(8, 0))

        # Board type
        type_frame = tk.LabelFrame(controls, text="Board Type")
        type_frame.pack(anchor="w", fill="x", pady=(0, 10))

        for board_type in ["English", "Hexagon", "Diamond"]:
            tk.Radiobutton(
                type_frame,
                text=board_type,
                value=board_type,
                variable=self.board_type_var
            ).pack(anchor="w")

        # Buttons
        tk.Button(
            controls,
            text="New Game",
            width=12,
            command=self.start_new_game
        ).pack(anchor="w", pady=(5, 10))

        tk.Label(
            controls,
            textvariable=self.status_var,
            justify="left",
            wraplength=220
        ).pack(anchor="w", pady=(5, 0))

        # Canvas
        self.canvas = tk.Canvas(container, width=500, height=500, bg="white", highlightthickness=1)
        self.canvas.grid(row=0, column=1, sticky="nsew")
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)

    def start_new_game(self) -> None:
        try:
            board_size = self.board_size_var.get()
            board_type = self.board_type_var.get()
            self.game.reset(board_size=board_size, board_type=board_type)
            self.selected = None
            self._draw_board()
            self._update_status("New game started.")
        except ValueError as error:
            messagebox.showerror("Invalid Settings", str(error))

    def _update_status(self, extra_message: str = "") -> None:
        board_size = self.game.board_size
        board_type = self.game.board_type
        marble_count = self.game.count_marbles()

        lines = [
            f"Board size: {board_size}",
            f"Board type: {board_type}",
            f"Marbles left: {marble_count}"
        ]

        if self.selected is not None:
            lines.append(f"Selected: {self.selected}")

        if self.game.is_game_over():
            lines.append("Game Over")
            lines.append(f"Rating: {self.game.performance_rating()}")

        if extra_message:
            lines.append(extra_message)

        self.status_var.set("\n".join(lines))

    def on_canvas_click(self, event) -> None:
        cell = self._pixel_to_cell(event.x, event.y)
        if cell is None:
            return

        row, col = cell
        cell_value = self.game.get_cell(row, col)

        if cell_value == 1:
            self.selected = cell
            self._draw_board()
            self._update_status("Marble selected.")
            return

        if cell_value == 0 and self.selected is not None:
            moved = self.game.try_move(self.selected, cell)
            if moved:
                self.selected = None
                self._draw_board()
                if self.game.is_game_over():
                    self._update_status("Move completed. No valid moves remain.")
                else:
                    self._update_status("Move completed.")
            else:
                self._update_status("Invalid move.")
            return

    def _pixel_to_cell(self, x: int, y: int) -> Optional[Coord]:
        board_rows = len(self.game.board)
        board_cols = len(self.game.board[0])

        x0 = x - self.PADDING
        y0 = y - self.PADDING

        if x0 < 0 or y0 < 0:
            return None

        col = x0 // self.CELL_SIZE
        row = y0 // self.CELL_SIZE

        if not (0 <= row < board_rows and 0 <= col < board_cols):
            return None

        if self.game.get_cell(int(row), int(col)) is None:
            return None

        return int(row), int(col)

    def _draw_board(self) -> None:
        self.canvas.delete("all")

        rows = len(self.game.board)
        cols = len(self.game.board[0])

        canvas_width = self.PADDING * 2 + cols * self.CELL_SIZE
        canvas_height = self.PADDING * 2 + rows * self.CELL_SIZE
        self.canvas.config(width=canvas_width, height=canvas_height)

        # Draw grid lines
        for r in range(rows + 1):
            y = self.PADDING + r * self.CELL_SIZE
            self.canvas.create_line(self.PADDING, y, self.PADDING + cols * self.CELL_SIZE, y)

        for c in range(cols + 1):
            x = self.PADDING + c * self.CELL_SIZE
            self.canvas.create_line(x, self.PADDING, x, self.PADDING + rows * self.CELL_SIZE)

        # Draw title text
        self.canvas.create_text(
            self.PADDING,
            8,
            anchor="w",
            text=f"{self.game.board_type} board, size {self.game.board_size}"
        )

        # Draw cells
        for r in range(rows):
            for c in range(cols):
                value = self.game.get_cell(r, c)

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
                elif value == 0:
                    self.canvas.create_oval(
                        cx - radius, cy - radius, cx + radius, cy + radius,
                        outline="black", fill="white"
                    )


if __name__ == "__main__":
    app = SolitaireGUI()
    app.mainloop()