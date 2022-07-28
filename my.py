import taichi as ti
import taichi.math as tm
ti.init(arch=ti.cpu)

grid_n = 20
res = (grid_n, grid_n)
dx = 1 / res[0]
inv_dx = res[0]
radius = dx * ti.sqrt(2)
desired_samples = 100000
grid = ti.field(dtype=int, shape=res)
samples = ti.Vector.field(2, float, shape=desired_samples)

grid.fill(-1)

@ti.func
def check_collision(p, index):
    x, y = index
    collision = False
    for i in range(max(x-2, 0), min(x+3,grid_n)):
        for j in range(max(y-2, 0), min(y+3,grid_n)):
            if grid[i,j] != -1:
                q = samples[grid[i,j]]
                if (q-p).norm() < radius - 1e-6:
                    collision = True
    return collision

@ti.kernel
def poisson_disk_sample(desired_samples: int) -> int:
    #head 代表的是当前的种子的编号
    #tail 代表的是目前已经钉住的点
    head, tail = 0, 1
    samples[0] = tm.vec2(0.5, 0.5)

    while head < tail and tail < desired_samples:
        source_x = samples[head] #新种子的位置
        head +=1 

        for _ in range(100):
            theta = ti.random() * 2 * tm.pi
            offset =  tm.vec2(tm.cos(theta), tm.sin(theta)) * (1 + ti.random()) * radius

            new_x = source_x + offset
            new_index = int(new_x * inv_dx)

            if 0<= new_x[0] <= 1 and 0<=new_x[1] <=1: 
                collision = check_collision(new_x, new_index)
                if not collision and tail < desired_samples:
                    samples[tail] = new_x
                    grid[new_index] = tail
                    tail+=1
    return tail

def draw_grid():
    import numpy as np
    X = []
    Y = []
    dy=dx
    for i in range(grid_n):
        X.append([dx*i,0])
        Y.append([dx*i,1])
    for i in range(grid_n):
        X.append([0, dy*i])
        Y.append([1, dy*i])
    X = np.array(X)
    Y = np.array(Y)
    gui.lines(begin=X, end=Y, radius=1, color=0x000000)


num_samples = poisson_disk_sample(desired_samples)
gui = ti.GUI("Poisson Disk Sampling", res=800, background_color=0xFFFFFF)
count = 0
speed = 1
while gui.running:
    gui.circles(samples.to_numpy()[:min(count * speed, num_samples)],
                color=0xababab,
                radius= radius * 800)
    gui.circles(samples.to_numpy()[:min(count * speed, num_samples)],
                color=0xFF0000,
                radius=3)
    draw_grid()
    count += 1
    gui.show()
