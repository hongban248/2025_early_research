#对比前后两次拼接的H波段光谱

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
import glob
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
    plt.fill_between(wavelength1, flux1 - error1, flux1 + error1, color='red', alpha=0.3, label='H波段误差带')
    #plt.plot(wavelength2, flux2, color='green', label='K波段')
    plt.plot(wavelength, flux, color='blue', linestyle='--', label='其他恒星光谱')
    plt.xlabel('Wavelength (μm)')
    plt.ylabel('Flux (normalized)')
    plt.tight_layout()
    
    plt.show()


def process2(wavelength,flux,error,wavelength1,flux1,error1):
    # flux1_sca///////ror1*scale

    # for i in range(len(wavelength2)):
    #     flux2_new=interp_1d(wavelength,flux,wavelength2[i])
    #     flux2_scale.append(flux2_new)
    # scale=np.mean(flux2_scale)/np.mean(flux2)
    # flux2=flux2*scale
    # error2=error2*scale

    plt.figure(figsize=(20, 15))
    plt.plot(wavelength1, flux1, color='red', label='H波段')
    plt.fill_between(wavelength1, flux1 - error1, flux1 + error1, color='red', alpha=0.3, label='H波段误差带')
    #plt.plot(wavelength2, flux2, color='green', label='K波段')
    plt.plot(wavelength, flux, color='blue', linestyle='--', label='其他恒星光谱')
    plt.xlabel('Wavelength (μm)')
    plt.ylabel('Flux (normalized)')
    plt.tight_layout()
    
    plt.show()

if __name__ == '__main__':

    # 1. 观测文件固定
    obv_path1 = 'code/outcome/SDCH_20240203_0071_middle.back5/outcome.csv'
    obv_path2 = 'code/outcome/SDCH_20240203_0071_middle.back4/outcome.csv'

    # 2. 读取并裁剪 H、K 波段（只读一次，后面所有模型共用）
    datas1 = pd.read_csv(obv_path1)
    wavelength_H, flux_H, error_H = sort(
        datas1['wavelength'], datas1['spectrum'], datas1['dev'])
    left_H, right_H = find_insert_position(wavelength_H, 1.52), \
                      find_insert_position(wavelength_H, 1.70)
    wavelength_H, flux_H, error_H = \
        wavelength_H[left_H:right_H], flux_H[left_H:right_H], error_H[left_H:right_H]

    datas2 = pd.read_csv(obv_path2)
    wavelength_K, flux_K, error_K = sort(
        datas2['wavelength'], datas2['spectrum'], datas2['dev'])
    left_K, right_K = find_insert_position(wavelength_K, 1.52), \
                      find_insert_position(wavelength_K, 1.70)
    wavelength_K, flux_K, error_K = \
        wavelength_K[left_K:right_K], flux_K[left_K:right_K], error_K[left_K:right_K]

    process(wavelength_H, flux_H, error_H, wavelength_K, flux_K, error_K)
