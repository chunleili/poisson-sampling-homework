import taichi as ti
import taichi.math as tm
ti.init(arch=ti.cpu)

max_num = 10000
radius = 0.01
dx = radius / ti.sqrt(2)
bound = 1.0
grid_n = (int) (bound/dx)
samples = ti.Vector.field(2,float, max_num)
grid = ti.field(dtype=int, shape=(grid_n, grid_n))
# grid = ti.Vector.field(2, float, (grid_n, grid_n))
active = ti.Vector.field(2,float, max_num)

# @ti.func
# def check_collision(p, index):
#     x, y = index
#     collision = False
#     for i in range(max(0, x - 2), min(grid_n, x + 3)):
#         for j in range(max(0, y - 2), min(grid_n, y + 3)):
#             if grid[i, j] != -1:
#                 q = samples[grid[i, j]]
#                 if (q - p).norm() < radius - 1e-6:
#                     collision = True
#     return collision

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
def poisson_disk_sample()->int:
    active[0] = tm.vec2(0.5, 0.5)
    samples[0] = tm.vec2(0.5, 0.5)
    num_active = 1
    sampleID = 1

    while num_active != 0:
        #take the active[num_active] as seed and scatter in the ring
        for _ in range(30):
            theta = ti.random() * 2 * tm.pi
            offset = tm.vec2(tm.cos(theta), tm.sin(theta)) * (1 + ti.random()) * radius

            p = active[num_active] + offset
            grid_index = int(p/dx)

            flag = check_collision(p, grid_index)

            if not flag:
                print(f"------")
                print(f"sampleID {sampleID} is added")
                print(f"position is {p.x},{p.y}")
                print(f"grid_index is {grid_index.x},{grid_index.y}")
                #add to the samples
                samples[sampleID] = p
                sampleID +=1
                
                #add to the activation list
                active[num_active] = p
                num_active += 1

                #add to the grid
                grid[grid_index] = sampleID

                break

        #after seed, deactivate the seed
        num_active -= 1


    return sampleID

        
    
grid.fill(-1)
num_samples =  poisson_disk_sample()
gui = ti.GUI("Poisson Disk Sampling", res=800, background_color=0xFFFFFF)
count = 0
speed = 300
while gui.running:
    gui.circles(samples.to_numpy()[:min(count * speed, num_samples)],
                color=0x000000,
                radius=1.5)
    count += 1
    gui.show()
