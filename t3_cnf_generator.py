from itertools import combinations
from pysat.solvers import Glucose3
from t3_problem import CSPProblem

class CNFGenerator:
    """Sinh CNF clauses từ CSPProblem và giải bằng Glucose3."""

    def __init__(self, csp: CSPProblem):
        self.csp = csp
        self.var_map = {}
        self.rev_map = {}
        for idx, (i, j) in enumerate(csp.variables, start=1):
            self.var_map[(i, j)] = idx
            self.rev_map[idx] = (i, j)
        self.clauses = []

    def _cell_var(self, i, j):
        return self.var_map[(i, j)]

    def generate_clauses(self):
        """Sinh CNF clauses bằng tổ hợp at-least-k và at-most-k, loại trùng bằng set."""
        clause_set = set()

        for (ci, cj), k, neighbors in self.csp.constraints:
            n = len(neighbors)
            var_list = [self._cell_var(r, c) for (r, c) in neighbors]

            # At-least-k
            if k > 0:
                size = n - k + 1
                if 1 <= size <= n:
                    for combo in combinations(var_list, size):
                        clause_set.add(tuple(sorted(combo)))

            # At-most-k
            if k < n:
                size = k + 1
                for combo in combinations(var_list, size):
                    clause_set.add(tuple(sorted(-v for v in combo)))

        self.clauses = [list(c) for c in clause_set]
        return self.clauses

    def solve(self):
        """Giải bằng Glucose3. Trả về dict {(i,j): bool} hoặc None."""
        solver = Glucose3()
        for clause in self.clauses:
            solver.add_clause(clause)

        if solver.solve():
            model = solver.get_model()
            assignment = {cell: False for cell in self.csp.variables}
            for lit in model:
                if abs(lit) in self.rev_map:
                    cell = self.rev_map[abs(lit)]
                    assignment[cell] = (lit > 0)
            solver.delete()
            return assignment
        else:
            solver.delete()
            return None

    def get_stats(self):
        return {
            "num_variables": len(self.csp.variables),
            "num_clauses": len(self.clauses),
            "num_constraints": len(self.csp.constraints),
        }