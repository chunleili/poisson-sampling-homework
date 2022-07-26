import taichi as ti
import taichi.math as tm
ti.init(arch=ti.cpu)

grid_n = 400
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
    for i in range(max(0, x - 2), min(grid_n, x + 3)):
        for j in range(max(0, y - 2), min(grid_n, y + 3)):
            if grid[i, j] != -1:
                q = samples[grid[i, j]]
                if (q - p).norm() < radius - 1e-6:
                    collision = True
    return collision

@ti.kernel
def poisson_disk_sample(desired_samples: int) -> int:
    samples[0] = tm.vec2(0.5)
    grid[int(grid_n * 0.5), int(grid_n * 0.5)] = 0
    head, tail = 0, 1
    while head < tail and head < desired_samples:
        source_x = samples[head]
        head += 1

        for _ in range(100):
            theta = ti.random() * 2 * tm.pi
            offset = tm.vec2(tm.cos(theta), tm.sin(theta)) * (1 + ti.random()) * radius
            new_x = source_x + offset
            new_index = int(new_x * inv_dx)

            if 0 <= new_x[0] < 1 and 0 <= new_x[1] < 1:
                collision = check_collision(new_x, new_index)
                if not collision and tail < desired_samples:
                    samples[tail] = new_x
                    grid[new_index] = tail
                    tail += 1
    return tail

@ti.kernel
def leak_filling(s :int) -> int:
    the_num_samples = s
    for i in range(grid_n):
        for j in range(grid_n): #先遍历所有网格
            if grid[i,j] == -1 : #假如发现了漏下的
                # print(f"find the leaked {i},{j}")
                grid_base = tm.vec2(i*dx, j*dx) #该网格左下角坐标
                for _ in range(100): #就在这个网格内洒它个100次点
                    p = tm.vec2(ti.random(), ti.random()) + grid_base
                    collision = check_collision(p, tm.vec2(i,j))
                    if not collision:   #假如洒到了缝隙
                        the_num_samples+=1
                        samples[the_num_samples] = p # 那就记录下点的位置
                        break   
                    else:
                        print(f"I can't pinpoint it in {i},{j}!")
    return the_num_samples

num_samples = poisson_disk_sample(desired_samples)
new_num_samples = leak_filling(num_samples)
gui = ti.GUI("Poisson Disk Sampling", res=800, background_color=0xFFFFFF)
count = 0
speed = 300
while gui.running:
    gui.circles(samples.to_numpy()[:min(count * speed, new_num_samples)],
                color=0x000000,
                radius=1.5)
    count += 1
    gui.show()
