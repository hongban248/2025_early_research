import pymultinest
import numpy as np

# 定义一个简单的二维高斯函数作为测试目标函数
def myloglike(cube, ndim, nparams):
    x = cube[0]
    y = cube[1]
    return -0.5 * ((x - 5)**2 + (y - 5)**2)

# 定义参数的边界
def myprior(cube, ndim, nparams):
    for i in range(ndim):
        cube[i] = cube[i] * 10

# 配置 MultiNest
n_params = 2
pymultinest.run(myloglike, myprior, n_params, outputfiles_basename='/tmp/mn-test-', resume=False, verbose=True)

# 读取结果
a = pymultinest.Analyzer(n_params, outputfiles_basename='/tmp/mn-test-')
s = a.get_stats()

# 打印结果
print("Global Evidence:\n\t%.15e +- %.15e" % (s['global evidence'], s['global evidence error']))