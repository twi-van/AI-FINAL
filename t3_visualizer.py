import tkinter as tk
from t3_problem import CSPProblem

CELL_SIZE = 60
PADDING = 20
GREEN = "#4CAF50"
RED = "#F44336"
BG = "#1e1e2e"
TEXT_COLOR = "#ffffff"
HEADER_COLOR = "#cdd6f4"
BORDER_COLOR = "#313244"
UNSOLVED_COLOR = "#45475a"

class CSPVisualizer:
    """Giao diện trực quan hóa bài toán CSP và kết quả."""

    def __init__(self, root, csp: CSPProblem, assignment: dict, stats: dict):
        self.root = root
        self.csp = csp
        self.assignment = assignment
        self.stats = stats
        self.root.title("Task 3 – CSP Visualizer")
        self.root.configure(bg=BG)
        self._build_ui()

    def _build_ui(self):
        title = tk.Label(
            self.root, text="CSP – Constraint Satisfaction Solver",
            font=("Consolas", 16, "bold"), bg=BG, fg=HEADER_COLOR
        )
        title.pack(pady=(15, 5))

        stats_text = (
            f"Biến: {self.stats['num_variables']}   "
            f"Clauses: {self.stats['num_clauses']}   "
            f"Ràng buộc: {self.stats['num_constraints']}"
        )
        tk.Label(self.root, text=stats_text, font=("Consolas", 10),
                 bg=BG, fg="#a6adc8").pack(pady=(0, 10))

        frame = tk.Frame(self.root, bg=BG)
        frame.pack(padx=PADDING, pady=5)

        left_frame = tk.Frame(frame, bg=BG)
        left_frame.pack(side=tk.LEFT, padx=20)
        tk.Label(left_frame, text="Ma trận đầu vào", font=("Consolas", 11, "bold"),
                 bg=BG, fg=HEADER_COLOR).pack(pady=(0, 5))
        self.canvas_input = tk.Canvas(
            left_frame, width=self.csp.cols * CELL_SIZE,
            height=self.csp.rows * CELL_SIZE, bg=BG, highlightthickness=0
        )
        self.canvas_input.pack()

        right_frame = tk.Frame(frame, bg=BG)
        right_frame.pack(side=tk.LEFT, padx=20)
        lbl_text = "Kết quả" if self.assignment else "Không có lời giải"
        tk.Label(right_frame, text=lbl_text, font=("Consolas", 11, "bold"),
                 bg=BG, fg=HEADER_COLOR).pack(pady=(0, 5))
        self.canvas_output = tk.Canvas(
            right_frame, width=self.csp.cols * CELL_SIZE,
            height=self.csp.rows * CELL_SIZE, bg=BG, highlightthickness=0
        )
        self.canvas_output.pack()

        legend_frame = tk.Frame(self.root, bg=BG)
        legend_frame.pack(pady=10)
        for color, label in [(GREEN, "Xanh (True)"), (RED, "Đỏ (False)")]:
            box = tk.Canvas(legend_frame, width=20, height=20, bg=BG, highlightthickness=0)
            box.create_rectangle(2, 2, 18, 18, fill=color, outline="")
            box.pack(side=tk.LEFT, padx=4)
            tk.Label(legend_frame, text=label, font=("Consolas", 10),
                     bg=BG, fg=TEXT_COLOR).pack(side=tk.LEFT, padx=(0, 15))

        self._draw_input()
        self._draw_output()

    def _draw_cell(self, canvas, i, j, fill_color, text="", text_color=TEXT_COLOR):
        x0 = j * CELL_SIZE + 2
        y0 = i * CELL_SIZE + 2
        x1 = x0 + CELL_SIZE - 4
        y1 = y0 + CELL_SIZE - 4
        canvas.create_rectangle(x0, y0, x1, y1, fill=fill_color, outline=BORDER_COLOR, width=1)
        if text:
            canvas.create_text(
                (x0 + x1) // 2, (y0 + y1) // 2,
                text=text, font=("Consolas", 13, "bold"), fill=text_color
            )

    def _draw_input(self):
        for i in range(self.csp.rows):
            for j in range(self.csp.cols):
                val = self.csp.matrix[i][j]
                text = str(val) if val is not None else "·"
                self._draw_cell(self.canvas_input, i, j, UNSOLVED_COLOR, text)

    def _draw_output(self):
        if not self.assignment:
            for i in range(self.csp.rows):
                for j in range(self.csp.cols):
                    self._draw_cell(self.canvas_output, i, j, UNSOLVED_COLOR, "?")
            return

        for i in range(self.csp.rows):
            for j in range(self.csp.cols):
                is_green = self.assignment.get((i, j), False)
                color = GREEN if is_green else RED
                val = self.csp.matrix[i][j]
                text = str(val) if val is not None else ""
                self._draw_cell(self.canvas_output, i, j, color, text)
