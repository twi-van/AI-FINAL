class CSPProblem:
    """Biểu diễn bài toán CSP tô màu ma trận."""
    def __init__(self, matrix):
        self.matrix = matrix
        self.rows = len(matrix)
        self.cols = len(matrix[0]) if self.rows > 0 else 0
        self.variables = [(i, j) for i in range(self.rows) for j in range(self.cols)]
        self.constraints = self._generate_constraints()

    def get_neighbors(self, i, j):
        """Trả về tất cả ô kề (bao gồm chính nó) trong vùng 3x3."""
        neighbors = []
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                ni, nj = i + di, j + dj
                if 0 <= ni < self.rows and 0 <= nj < self.cols:
                    neighbors.append((ni, nj))
        return neighbors

    def _generate_constraints(self):
        """Sinh ràng buộc (center_cell, k, neighbors) cho các ô có số."""
        constraints = []
        for i in range(self.rows):
            for j in range(self.cols):
                val = self.matrix[i][j]
                if val is not None:
                    neighbors = self.get_neighbors(i, j)
                    constraints.append(((i, j), val, neighbors))
        return constraints

    def load_from_file(self, filename):
        """Đọc ma trận từ file. '.' là ô trống, số nguyên là giá trị ràng buộc."""
        matrix = []
        with open(filename, 'r') as f:
            for line in f:
                row = []
                for token in line.strip().split():
                    if token == '.':
                        row.append(None)
                    else:
                        row.append(int(token))
                if row:
                    matrix.append(row)
        self.matrix = matrix
        self.rows = len(matrix)
        self.cols = len(matrix[0]) if self.rows > 0 else 0
        self.variables = [(i, j) for i in range(self.rows) for j in range(self.cols)]
        self.constraints = self._generate_constraints()