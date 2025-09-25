#画出其他模型的光谱

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

def process(wavelength,flux,error,wavelength1,flux1,error1,wavelength2,flux2,error2,modes_name,save_dir="code/outcome/IRTF_compare"):
    flux1_scale=[]
    flux2_scale=[]
    error1_scale=[]
    error2_scale=[]

    for i in range(len(wavelength1)):
        flux1_new=interp_1d(wavelength,flux,wavelength1[i])
        flux1_scale.append(flux1_new)
    scale=np.mean(flux1_scale)/np.mean(flux1)
    flux1=flux1*scale
    error1=error1*scale

    print(scale)
    for i in range(len(wavelength2)):
        flux2_new=interp_1d(wavelength,flux,wavelength2[i])
        flux2_scale.append(flux2_new)
    scale=np.mean(flux2_scale)/np.mean(flux2)
    flux2=flux2*scale
    error2=error2*scale
    print(scale)

    plt.figure(figsize=(20,16))
    plt.plot(wavelength1, flux1, color='red', label='H波段')
    plt.plot(wavelength2, flux2, color='green', label='K波段')
    plt.plot(wavelength, flux, color='blue', label='其他恒星光谱')
    plt.title(modes_name)
    plt.xlabel('Wavelength (μm)')
    plt.ylabel('Flux (normalized)')
    plt.tight_layout()
    
    plt.savefig(os.path.join(save_dir,f'{modes_name}_compare.png'))
    plt.show()
    plt.close()


# if __name__=='__main__':

#     model_path='models/other_V/AD_Leo_M3V.txt'
#     wavelength,flux,error=get_txt(file_path=model_path)
#     for i in range(len(flux)):
#         if flux[i]<0:
#             flux[i]=np.nan
#     #plot_1d_spectrum(wavelength,flux)

#     obv_path1='code/outcome/SDCH_20240203_0071_middle/outcome.csv'
#     obv_path2='code/outcome/SDCK_20240203_0071_middle/outcome.csv'

#     datas1=pd.read_csv(obv_path1)
#     wavelength_H=datas1['wavelength']
#     #
#     flux_H=datas1['spectrum']
#     error_H=datas1['dev']

#     wavelength_H,flux_H,error_H=sort(wavelength_H,flux_H,error_H)
#     left_H=find_insert_position(wavelength_H,1.53)
#     right_H=find_insert_position(wavelength_H,1.72)
#     wavelength_H,flux_H,error_H=wavelength_H[left_H:right_H],flux_H[left_H:right_H],error_H[left_H:right_H]
    

#     # print(wavelength_H)
#     # plot_1d_spectrum(wavelength_H,flux_H)
#     datas2=pd.read_csv(obv_path2)
#     wavelength_K=datas2['wavelength']
#     flux_K=datas2['spectrum']
#     error_K=datas2['dev']

#     wavelength_K,flux_K,error_K=sort(wavelength_K,flux_K,error_K)
#     #plot_1d_spectrum(wavelength_K,flux_K)#2.03,2.36
#     left_K=find_insert_position(wavelength_K,2.05)
#     right_K=find_insert_position(wavelength_K,2.36)
#     wavelength_K,flux_K,error_K=wavelength_K[left_K:right_K],flux_K[left_K:right_K],error_K[left_K:right_K]

#     #plot_1d_spectrum(wavelength_K,flux_K)#2.03,2.36
#     process(wavelength,flux,error,wavelength_H,flux_H,error_H,wavelength_K,flux_K,error_K)

if __name__ == '__main__':

    # 1. 观测文件固定
    obv_path1 = 'code/outcome/SDCH_20240203_0071_middle/outcome.csv'
    obv_path2 = 'code/outcome/SDCK_20240203_0071_middle/outcome.csv'

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
    left_K, right_K = find_insert_position(wavelength_K, 2.10), \
                      find_insert_position(wavelength_K, 2.36)
    wavelength_K, flux_K, error_K = \
        wavelength_K[left_K:right_K], flux_K[left_K:right_K], error_K[left_K:right_K]

    # 3. 遍历 models/other_V/ 下所有 txt
    model_dir = 'models/other_V'
    for model_file in glob.glob(os.path.join(model_dir, '*.txt')):
        print(f'\n===== Processing model: {os.path.basename(model_file)} =====')

        wavelength, flux, error = get_txt(file_path=model_file)
        flux = np.where(flux < 0, np.nan, flux)   # 一行替代 for-loop

        process(wavelength, flux, error,
                wavelength_H, flux_H, error_H,
                wavelength_K, flux_K, error_K,
                modes_name=os.path.basename(model_file))
