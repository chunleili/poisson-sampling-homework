# My README

本着最小化修改原则（能不改就不改，尽量增加而不修改，不去破坏原有代码逻辑结构）进行了修改
## easy解法
切换到分支easy可以查看easy代码
```
git checkout easy
```
与原代码相比，easy只做了如下修改

首先更改下网格的大小，增加一个grid_ny
![easy1](pic/easy1.png)
然后把所有原本grid_n的地方都换成grid_nx和grid_ny
![easy2](pic/easy2.png)
![easy3](pic/easy3.png)
最后（也是最关键的），把new_x(代表的是新落点的位置)的边界更改一下
![easy4](pic/easy4.png)

效果为：
![easy_demo](pic/easy_demo.gif)

也就是只是洒落了半边。既然这是可以的，你可以选定任意区域撒点。只要修改上面那个if中（44行）的边界即可。


## medium解法
先跳过，既然numpy和numba都以及写好了，暂时还想不出有什么其他的python数值计算库

## hard解法
原文中有这句话：
![hard1](pic/hard1.png)

>当这 100 个点都检查完毕后，我们可以认为 samples[head] 这个点的周围已经没有空白区域可以放置新的点，所以将 head 增加 1，并重新检查下一个 samples[head] 附近的区域。

问题是：
真的是这样吗？

泊松圆盘采样留着空隙的原因在于它是随机撒点的。只要是随机撒点，就不能保证每个网格内都有一个点。很有可能在两个圆形的空隙处没有被撒点。

可以看一下这个博客的动画
https://bl.ocks.org/mbostock/dbb02448b0f93e4c82c3


我盯了半天，发现留着缝隙的可能性还是有的。因为撒点的终止条件是随机撒点的次数（比如taichi这个代码就是在每个圆环内撒了100次，不管是不是保证每个网格都洒了，只要撒了100次就终止）

比如下面这个小缝隙。怎么样？很刁钻吧！这里是很难撒点的！
![hard2](pic/hard2.png)


那么我们就有两个方案：
1. 提升撒点的次数（洒点100次不能洒满，那我就多洒一些呗），这就让留缝隙的几率变小了。

这有点类似于**蒙特卡洛**的思想（实际上Poisson disk确实就是一种蒙特卡洛法）。但是很遗憾这显然不是题目所期望的，而且这也可能大幅提升计算量。


2. 检查一下还有哪个网格没点，没点的地方就去洒呗。

我们将采用方案2， 这种方案能够保证“最大化采样”，也就是每个网格一定会被洒点，不能留下空白的网格。

下面我们着手实践！

首先把代码回复到最原始的状态，这样可以追踪到我们改了哪里。

我们有两种方案来检查并且补漏
1. 记录下哪些网格被洒了，哪些没有。等点都洒完了，再去查漏补缺。
2. 在洒点的过程中就去专门地找还没被洒点的网格。

第一种方案看起来简单一些，我们就这么干。

首先，我们需要一个数组来记录哪些已经被洒了点的。幸运的是，这个数组已经有了，那就是grid数组。假如grid中某个元素为-1，则它还是未被填充的。

然后我们定义一个查漏补缺的函数。就叫他leak_filling吧！在这个函数中遍历所有的网格，看看有没有漏掉的网格。如果有，那么就把它填充上。

填充的地方还是有点难办的。因为就那么小一个缝隙，很难去找到留有缝隙的位置。我暂时没想到什么好的解决方案，就暴力解法吧。洒它个几百几千次，反正洒上了就OK，洒不上就算我倒霉。

检测是否是缝隙的方法和原来一样，就是拒绝采样法，用check_collision把不符合条件的reject掉。














## 参考文献

1. 太极微信公众号文章
https://mp.weixin.qq.com/s/OpMTkCX-J6_SzSumHJcVJg

2. taichi关于泊松圆盘采样的代码
https://github.com/taichi-dev/taichi_elements/blob/master/engine/voxelizer.py

3. 一个关于泊松圆盘采样的技术博客（javascript)
https://bl.ocks.org/mbostock/dbb02448b0f93e4c82c3

4. 一个关于泊松圆盘采样的技术博客(c#)
https://sighack.com/post/poisson-disk-sampling-bridsons-algorithm

5. 一个关于泊松圆盘采样的技术博客(除了泊松圆盘，还有另一个算法：加权消除采样）
https://medium.com/@hemalatha.psna/implementation-of-poisson-disc-sampling-in-javascript-17665e406ce1

6. 一个关于泊松圆盘采样的YouTube视频（Unity)
https://youtu.be/7WcmyxyFO7o

7. Robert Bridson 2007年提出该算法的原始文献
https://www.cs.ubc.ca/~rbridson/docs/bridson-siggraph07-poissondisk.pdf
以及ACM DL（附件含C++代码）
https://dl.acm.org/doi/10.1145/1278780.1278807


**The bellowing is the old README**
-------

# The challenge

Challenge 1 (easy): modify the code so that it works for any resolution `(width, height)`, e.g. `640 x 480`.

Challenge 2 (medium): implement Bridson's Poisson disk sampling algorithm with other Python packages, use the same config with this repo (400x400 grid and 100K desired points) and whatever acceleration tricks. See if you can beat the speed of Taichi. (the compile time will not be counted)

Challenge 3 (hard): improve the code so that the result is a maximal Poisson sampling, that is, there won't be any room left to insert new points.

Please submit your work in this [issue](https://github.com/taichi-dev/poisson-sampling-homework/issues/1).

# Install taichi

```
pip3 install -r requirements.txt  
```

# An interative animation

Mouse and keyboard control:

1. Click mouse to choose an initial point.
2. Press `p` to save screenshots.

Example:

<p align="center">
  <img src="./demo.jpg" width="400" ></img>
</p>


# Benchmark with NumPy and Numba

See this repo:

https://github.com/taichi-dev/taichi_benchmark/tree/main/poisson

You are encouraged to implement a faster one to beat ours!
