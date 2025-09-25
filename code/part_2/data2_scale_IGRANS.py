
import numpy as np
import pandas as pd
#画出其他模型、观测结果的光谱，和H波段，K波段的结果（仅仅scale对比）

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


def plot_1d_spectrum(wave_1d, flux_1d):
    plt.figure(figsize=(12, 4))
    plt.plot(wave_1d, flux_1d, lw=1, color='k')
    plt.xlabel('Wavelength (μm)')
    plt.ylabel('Flux (normalized)')
    plt.title('Merged 1-D Spectrum')
    plt.tight_layout()
    plt.show()

def sort(wavelength_1d,spectrum_1d,var_1d):
    wavelength_1d=np.asarray(wavelength_1d)
    spectrum_1d=np.asarray(spectrum_1d)
    var_1d=np.asarray(var_1d)

    idx = np.argsort(wavelength_1d)

    # 2. 重新排序三个数组
    wavelength_sorted = wavelength_1d[idx]
    spectrum_sorted   = spectrum_1d[idx]
    var_sorted        = var_1d[idx]

    return wavelength_sorted, spectrum_sorted, var_sorted

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

def interp_1d(x, y, x_new, kind='linear', extrapolate=False):
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
if __name__ == '__main__':

    obv_path1='code/outcome/SDCH_20240203_0071_middle.back4/outcome.csv'
    datas1 = pd.read_csv(obv_path1)
    wavelength_H, flux_H, error_H = sort(
        datas1['wavelength'], datas1['spectrum'], datas1['dev'])
    left_H, right_H = find_insert_position(wavelength_H, 1.52), \
                      find_insert_position(wavelength_H, 1.70)
    wavelength_H, flux_H, error_H = \
        wavelength_H[left_H:right_H], flux_H[left_H:right_H], error_H[left_H:right_H]

    k_path='code/outcome/SDCK_20240203_0071_middle/outcome.csv'
    datas2 = pd.read_csv(k_path)
    wavelength_K, flux_K, error_K = sort(
        datas2['wavelength'], datas2['spectrum'], datas2['dev'])
    left_K, right_K = find_insert_position(wavelength_K, 2.10), \
                      find_insert_position(wavelength_K, 2.36)
    wavelength_K, flux_K, error_K = \
        wavelength_K[left_K:right_K], flux_K[left_K:right_K], error_K[left_K:right_K]

    np.savetxt('code/part_2/data_for_part2/H.txt', np.c_[wavelength_H, flux_H*2.2956761795482373e-19, error_H], 
                   header='# wavelength(micron) flux(erg/s/cm2/micron) error(erg/s/cm2/micron)')

    np.savetxt('code/part_2/data_for_part2/K.txt', np.c_[wavelength_K, flux_K*2.560234668985841e-19, error_K], 
                   header='# wavelength(micron) flux(erg/s/cm2/micron) error(erg/s/cm2/micron)')