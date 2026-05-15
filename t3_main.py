import sys
import tkinter as tk
sys.stdout.reconfigure(encoding='utf-8')
from t3_problem import CSPProblem
from t3_cnf_generator import CNFGenerator
from t3_visualizer import CSPVisualizer

SAMPLE_MATRIX = [
    [None, None, None, 4,    None, None],
    [None, None, None, None, 8,    5   ],
    [4,    6,    7,    6,    6,    None],
    [3,    6,    7,    6,    None, None],
    [None, 4,    None, 4,    4,    None],
    [None, None, None, None, None, 3   ],
]


def print_solution(csp, assignment):
    print("\n=== Ma trận gốc ===")
    for row in csp.matrix:
        print(" ".join(str(v) if v is not None else "." for v in row))

    if assignment is None:
        print("\n[!] Không tìm được lời giải.")
        return

    print("\n=== Kết quả tô màu (G=Xanh, R=Đỏ) ===")
    for i in range(csp.rows):
        row_str = ""
        for j in range(csp.cols):
            row_str += "G " if assignment.get((i, j)) else "R "
        print(row_str)

    print("\n=== Kiểm tra ràng buộc ===")
    all_ok = True
    for (ci, cj), k, neighbors in csp.constraints:
        green = sum(1 for cell in neighbors if assignment.get(cell, False))
        status = "OK" if green == k else "FAIL"
        if status == "FAIL":
            all_ok = False
        print(f"  Ô ({ci},{cj}) cần {k} xanh, có {green} → {status}")
    print(">>> Tất cả ràng buộc:", "THỎA MÃN ✓" if all_ok else "CÓ VI PHẠM ✗")


def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else None

    if filename:
        csp = CSPProblem([])
        csp.load_from_file(filename)
        print(f"[*] Đã đọc file: {filename}")
    else:
        csp = CSPProblem(SAMPLE_MATRIX)
        print("[*] Dùng ma trận mẫu.")

    print(f"[*] Kích thước: {csp.rows} x {csp.cols}")
    print(f"[*] Số biến: {len(csp.variables)}")
    print(f"[*] Số ràng buộc: {len(csp.constraints)}")

    gen = CNFGenerator(csp)
    gen.generate_clauses()
    stats = gen.get_stats()
    print(f"[*] Số CNF clauses (sau khử trùng): {stats['num_clauses']}")

    assignment = gen.solve()
    print_solution(csp, assignment)

    print("\n[*] Mở giao diện trực quan...")
    root = tk.Tk()
    CSPVisualizer(root, csp, assignment, stats)
    root.mainloop()


if __name__ == "__main__":
    main()
