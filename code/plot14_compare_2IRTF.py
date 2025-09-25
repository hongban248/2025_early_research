#对比M2.5和M3的光谱型

import numpy as np
from synphot import SourceSpectrum, SpectralElement
from synphot.models import Empirical1D
import numpy as np
import matplotlib.pyplot as plt
from synphot import SourceSpectrum
from synphot.models import Empirical1D
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import csv
from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from cycler import cycler
import math
from scipy.interpolate import interp1d, CubicSpline
import os
import subprocess
import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import numpy as np
import pandas as pd

def find_insert_position(arr, target):
    """
    使用二分查找算法查找目标数字在升序数组中的插入位置。
    如果目标数字已经在数组中，返回其索引；如果目标数字不在数组中，
    返回目标数字应该插入的位置，使得插入后数组仍然保持升序。

    :param arr: 升序数组
    :param target: 要查找的目标数字
    :return: 目标数字在数组中的插入位置
    """
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = (left + right) // 2  # 计算中间索引

        if arr[mid] == target:
            return mid  # 找到目标数字，返回其索引
        elif arr[mid] < target:
            left = mid + 1  # 目标在右侧子数组
        else:
            right = mid - 1  # 目标在左侧子数组

    # 如果未找到目标数字，left 的位置即为插入位置
    return left

def interp_1d(x, y, x_new, kind='linear', extrapolate=True):
    """
    一维插值函数

    参数:
        x (array-like): 原始横坐标（一维）
        y (array-like): 原始纵坐标（一维）
        x_new (array-like): 需要插值的新横坐标
        kind (str): 插值类型，可选 'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic', 或 'cubic_spline'
        extrapolate (bool): 是否允许外推（超出原始范围时）

    返回:
        np.ndarray: 插值后的纵坐标
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    x_new = np.asarray(x_new, dtype=float)

    if len(x) != len(y):
        raise ValueError("x 和 y 的长度必须相同")

    if kind == 'cubic_spline':
        spline = CubicSpline(x, y, extrapolate=extrapolate)
        return spline(x_new)
    else:
        f = interp1d(
            x, y,
            kind=kind,
            bounds_error=not extrapolate,
            fill_value='extrapolate' if extrapolate else np.nan
        )
        return f(x_new)


def get_txt(file_path):
    try:
        wavelength, flux, error = np.loadtxt(file_path,
                                     comments='#',      # 跳过所有 # 开头的行
                                     unpack=True)       # 直接拆成三列数组
        return wavelength[find_insert_position(wavelength,1.5):find_insert_position(wavelength,2.5)],flux[find_insert_position(wavelength,1.5):find_insert_position(wavelength,2.5)],error[find_insert_position(wavelength,1.5):find_insert_position(wavelength,2.5)]
    except:
        wavelength, flux = np.loadtxt(file_path,
                                     comments='#',      # 跳过所有 # 开头的行
                           unpack=True)       # 直接拆成2列数组
        wavelength=wavelength/1e4
        e=flux
        return wavelength[find_insert_position(wavelength,1.5):find_insert_position(wavelength,2.5)],flux[find_insert_position(wavelength,1.5):find_insert_position(wavelength,2.5)],e[find_insert_position(wavelength,1.5):find_insert_position(wavelength,2.5)]

def process(wavelength,flux,error,wavelength1,flux1,error1):
    flux1_scale=[]
    flux2_scale=[]
    error1_scale=[]
    error2_scale=[]

    for i in range(len(wavelength1)):
        flux1_new=interp_1d(wavelength,flux,wavelength1[i])
        flux1_scale.append(flux1_new)
        #print(flux1_new)
    scale=np.nanmean(flux1_scale)/np.nanmean(flux1)
    print(np.nanmean(flux1_scale),np.nanmean(flux1))
    #print(scale)
    flux1=flux1*scale
    error1=error1*scale

    # for i in range(len(wavelength2)):
    #     flux2_new=interp_1d(wavelength,flux,wavelength2[i])
    #     flux2_scale.append(flux2_new)
    # scale=np.mean(flux2_scale)/np.mean(flux2)
    # flux2=flux2*scale
    # error2=error2*scale

    plt.figure(figsize=(20, 15))
    plt.plot(wavelength1, flux1, color='red', label='H波段')
    #plt.plot(wavelength2, flux2, color='green', label='K波段')
    plt.plot(wavelength, flux, color='blue', label='其他恒星光谱')
    plt.xlabel('Wavelength (μm)')
    plt.ylabel('Flux (normalized)')
    plt.tight_layout()
    
    plt.show()




wave1, flux1, error1 = get_txt('models/other_V/AD_Leo_M3V.txt')

wave2, flux2, error2 = get_txt('models/other_V/Gl_381_M2.5V.txt')

for i in range(len(flux1)):
    if flux1[i]<0:
        flux1[i]=np.nan

for i in range(len(flux2)):
    if flux2[i]<0:
        flux2[i]=np.nan

# 2) 如果 wave 单位已经是微米，把它转成 Å
wave1_AA = wave1 * 1e4        # μm -> Å
wave2_AA = wave2 * 1e4

# 3) 创建 synphot 光谱对象
spec1 = SourceSpectrum(Empirical1D, points=wave1_AA, lookup_table=flux1)
spec2 = SourceSpectrum(Empirical1D, points=wave2_AA, lookup_table=flux2)

fig, ax = plt.subplots(figsize=(8, 4))

# 统一用微米做横轴
x_plot = wave1        # 已经是微米
ax.plot(x_plot, flux1, label='AD Leo (M3V)', color='tab:blue')


x_plot2 = wave2       # 已经是微米
ax.plot(x_plot2, flux2, label='Gl 381 (M2.5V)', color='tab:red')


ax.set_xlabel('Wavelength (μm)')
ax.set_ylabel('Flux (erg s⁻¹ cm⁻² Å⁻¹)')
ax.legend()
ax.set_title('Model spectra')
plt.tight_layout()
plt.show()


process(wave1,flux1,error1,wave2,flux2,error2)