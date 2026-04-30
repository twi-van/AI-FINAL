from collections import deque
from logic import Clause, LogicGraph   

class ForwardChaining:
    def __init__(self, clauses):
        self.clauses = clauses   #danh sách các mệnh đề (Clause) trong KB

    def entails(self, q):
        #count[c] là số literal trong premise của mệnh đề c chưa được thỏa mãn
        count = {i: c.count for i, c in enumerate(self.clauses)}      #dùng index i để đánh dấu từng clause

        #đánh dấu symbol s đã được suy diễn hay chưa
        inferred = {}

        #hàng đợi (queue) chứa các symbol đã biết là true
        agenda = deque()

        #đưa tất cả FACT (mệnh đề không có premise) vào agenda
        for c in self.clauses:
            if c.is_fact():   #nếu là fact (không có điều kiện)
                symbol = c.conclusion
                if not inferred.get(symbol, False):
                    agenda.append(symbol)

        inferred_order = []   #lưu thứ tự suy diễn (để debug / phân tích)

        while agenda:
            p = agenda.popleft()   # lấy phần tử đầu hàng đợi (FIFO)

            # nếu đã suy ra được q -> kết luận KB |= q
            if p == q:
                return True, inferred_order

            #nếu p chưa được đánh dấu là đã suy diễn
            if not inferred.get(p, False):
                inferred[p] = True          #đánh dấu p đã suy diễn
                inferred_order.append(p)    #lưu lại thứ tự

                #duyệt tất cả các clause có chứa p trong premise
                for i, c in enumerate(self.clauses):
                    if p in c.premises:     #nếu p là điều kiện của clause c
                        count[i] -= 1       #giảm số điều kiện chưa thỏa

                        #nếu tất cả điều kiện đã thỏa -> suy ra conclusion
                        if count[i] == 0:
                            agenda.append(c.conclusion)

        #nếu duyệt hết mà không suy ra q -> KB không entail q
        return False, inferred_order

if __name__ == '__main__':
    kb = LogicGraph('data.txt')
    fc = ForwardChaining(kb.clauses)
 
    for q in ['p', 'q', 'l', 'm']:
        result, nodes = fc.entails(q)
        print(f"FC: KB |= '{q}' => {result}  |  inferred: {nodes}")
