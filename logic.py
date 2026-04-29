import graphviz

class Clause:
    def __init__(self,line):

        parts = line.strip().split() #

        self.premises = [] #giả thiết
        self.conclusion = None  #kết luận

        for p in parts : #lấy từng chữ cái trong mảng parts
            if p.startswith('-'):
                self.premises.append(p[1:]) #nếu có dấu (-) -> nó là giả thiết.Cắt bỏ dấu trừ [1:] , lấy từ ký tự thứ 1 bỏ 0 là dấu trừ đến hết và bỏ vào premises
            else:
                self.conclusion = p #không có dấu (-) gắn thẳng vào kết luận
        self.count = len(self.premises) #biến đếm premises 

    def is_fact(self):
        #nếu không cần điều kiện gì cả -> nó là một SỰ THẬT
        return self.count == 0
#khai báo biến đọc file và vẽ
class LogicGraph:
    def __init__(self,data):
        self.clauses = []
        with open(data,'r') as f: #mở file có quyền là 'r' READ- chỉ đọc
            for line in f:
                if line.strip(): #kiểm tra dòng đó có chứa chữ không và bỏ qua nếu là dòng trống 
                    self.clauses.append(Clause(line))
    #Hàm vẽ đồ thị
    def draw(self,output_name='knowledge_graph'):
        #DIGRAPH : DIRECTED GRAPH SƠ ĐỒ MŨI TÊN 1 CHIỀU
        dot = graphviz.Digraph(comment ='Knowledge Base') #gọi lệnh DIGRAPH của thư viện GRAPHVIZ

        #dấu chấm đen 
        dot_counter = 0

        for c in self.clauses:
            if c.is_fact(): #gọi hàm is_fact() kiểm tra c có phải là 1 conclusion hay không
                dot.node(c.conclusion,c.conclusion) #lệnh .node(tên_id,chữ_hiển_thị): nếu có xoay 1 VÒNG TRÒN ĐỨNG 1 MÌNH
            else: #nếu c là 1 quy tắc (có giả thiết)
                dot_id = f'dot_{dot_counter}'
                #vẽ chấm đen
                dot.node(dot_id,label='',shape='point',width='0.1')
                dot_counter += 1
                
                for pre in c.premises: #vòng lặp lấy từng chữ trong PREMISES của c
                    dot.node(pre,pre) #tạo vòng tròn
                    dot.edge(pre,dot_id) #kéo mũi tên edge() pre  -> dot_id
                # KẾT LUẬN
                dot.node(c.conclusion,c.conclusion)
                dot.edge(dot_id,c.conclusion)

        dot.render(output_name,view=True,format='png') #hàm .render() ra lệnh xuất file, tự động mở lên(view=True)

if __name__ == '__main__':
    kb_graph = LogicGraph('data.txt')
    kb_graph.draw()
