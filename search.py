import math
import random
import time
class SimulatedAnnealing:
    def __init__(self,Z):
        self.Z = Z 
        #CHIỀU CAO VÀ CHIỀU RỘNG CỦA ẢNH
        self.max_y = len(Z)
        self.max_x = len(Z[0])
    def get_neighbors(self, x, y):
        neighbors = []

        #danh sách 8 hướng đi có thể
        direct = [(0,-1),(0,1),(1,0),(-1,0),#N,S,E,W
                (-1,-1),(-1,1),(1,-1),(1,1) ]  # NW, SW, NE, SE
        
        for dx,dy in direct:
            new_x = x + dx
            new_y = y + dy
            
            #check viền (BORDERS) bằng cách lấy self.max_x
            if 0 <= new_x < self.max_x and 0 <= new_y < self.max_y:
                neighbors.append((new_x,new_y))
                
        return neighbors

    def sd1(self,t):
        # t là số bước nhảy hiện hành
        T_first = 1000.0

        T = T_first * (0.95**t)
        return T
    def sd2(self,t,slope):
        T_first = 1000.0
        # Tính tỷ lệ nghịch với độ dốc, tránh lỗi chia bằng không (slope + 0.1)
        # Kết hợp thêm giảm theo thời gian t cho nó chốt hạ hội tụ về 0
        T = (T_first / (slope + 0.1)) * (0.95 ** t)
        return T
    def run_search(self,mode='sd1'):
        #ĐIỂM CHUẨN BỊ XUẤT PHÁT
        #bắt đầu từ gốc 0(0,0)
        current_x,current_y = 0,0
        current_z = self.Z[current_y][current_x]

        #KHAI BÁO BIẾN THỜI GIAN VÀ ĐƯỜNG ĐI LIST
        t = 1
        path = [(current_x, current_y)]

        #VÒNG LẶP (LEO)
        while True: #vô hạn
            #bốc 8 túi hàng xóm ra,lấy random 1 tọa độ Next
            neighbors = self.get_neighbors(current_x,current_y)
            next_x,next_y = random.choice(neighbors) #trong hộp chứa 8 hướng , bốc ra 1 hướng
            next_z = self.Z[next_y][next_x] 

            #Đo chênh lệch độ cao giữa đích đến và chỗ đứng => điểm mới-điểm cũ >0
            delta_E = int(next_z) - int(current_z)

            #Đo nhiệt độ T current
            if mode == 'sd1':
                T = self.sd1(t)
            elif mode == 'sd2':
                slope = abs(delta_E)
                T = self.sd2(t,slope)

            #ĐÓNG BĂNG DỪNG CỖ MÁY DƯỚI NÀY NẰM THẲNG HÀNG VỚI KHỐI IF MODE Ở TRÊN
            if T < 0.0001:
                break
                
            #QUYẾT ĐỊNH ĐI HAY KHÔNG MỚI LÀ CỦA CHUNG
            if delta_E > 0:
                current_x,current_y,current_z = next_x,next_y,next_z

                path.append((current_x, current_y))
            else:
                xs = math.exp(delta_E / T)
                if random.random() < xs:
                    current_x, current_y, current_z = next_x, next_y, next_z
                    path.append((current_x, current_y))
                    
            
            t += 1
        return (current_x,current_y,current_z,t,path)

if __name__ == '__main__':
    from viz3d import load_state_space
    import numpy as np
    import matplotlib.pyplot as plt

    print("Đang nạp ảnh Monalisa biến thành núi 3D...")
    X, Y, Z = load_state_space('monalisa.jpg')
    
    print("\nKhởi động ...")
    agent = SimulatedAnnealing(Z)
    
    # CHẠY THỬ SD1 
    print("BẮT ĐẦU CHẠY THỬ NGHIỆM SD1")
    kq_sd1 = agent.run_search('sd1')
    print(f"Chót đỉnh SD1 tìm được: x = {kq_sd1[0]}, y = {kq_sd1[1]}")
    print(f"Độ cao Z tại đỉnh đó:  {kq_sd1[2]} / 255")
    print(f"Mất bao lâu leo vòng lặp: {kq_sd1[3]} bước")

    # CHẠY THỬ SD2
    print("BẮT ĐẦU CHẠY THỬ NGHIỆM SD2")
    kq_sd2 = agent.run_search('sd2')
    print(f"Chót đỉnh SD2 tìm được: x = {kq_sd2[0]}, y = {kq_sd2[1]}")
    print(f"Độ cao Z tại đỉnh đó: {kq_sd2[2]} / 255")
    print(f"Mất bao lâu leo vòng lặp: {kq_sd2[3]} bước")

    print("\n[Đã hoàn thành xong nhiệm vụ tính toán - đang chuyển qua vẽ 3D...]")

    X_mesh,Y_mesh = np.meshgrid(X,Y) #tạo lưới đan trục tọa độ
    fig = plt.figure(figsize=(10,8))
    ax = plt.axes(projection='3d')

    ax.plot_surface(X_mesh,Y_mesh,Z, cmap='viridis', edgecolor='none', alpha=0.9)
    
    # Kéo mảng đường đi của SD1 ra vẽ màu đỏ
    path_sd1 = kq_sd1[4]
    px1 = [p[0] for p in path_sd1] #Mọi chùm X
    py1 = [p[1] for p in path_sd1] #Mọi chùm Y
    pz1 = [Z[p[1]][p[0]] for p in path_sd1] #mảng Z

    ax.plot(px1,py1,pz1,'r-',zorder=3,linewidth=2.5,label='Đường đi SD1 (Đỏ)') #đường nối màu đỏ nét liền

    # Kéo mảng đường đi của SD2 ra vẽ màu vàng

    path_sd2 = kq_sd2[4] 
    px2 = [p[0] for p in path_sd2] 
    py2 = [p[1] for p in path_sd2]
    pz2 = [Z[p[1]][p[0]] for p in path_sd2]

    ax.plot(px2,py2,pz2,'y-',zorder=3,linewidth=2.5,label='Đường đi SD2 (Vàng)') #đường nối màu đỏ nét liền

    plt.legend()
    plt.title('Mô phỏng leo núi Simulated Annealing (SD1 VS SD2)')
    plt.show()


    