from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt

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

def get_txt_fire(file_path):
    try:
        wavelength, flux, error = np.loadtxt(file_path,
                                     comments='#',      # 跳过所有 # 开头的行
                                     unpack=True)       # 直接拆成三列数组
        wavelength=wavelength/1
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

def read_fire1(filename):
    """
    
    """
    with fits.open(filename) as hdul:
        header = hdul[1].header
        data=hdul[1].data

    #print(header)
    #print(data,data.shape)

    wave=[i[0]/1e4 for i in data]
    #print(wave,len(wave))
    counts=[i[1] for i in data]
    #print(counts)

    var=[i[1]/i[3] for i in data]

    min_index=find_insert_position(wave,1.5)
    max_index=find_insert_position(wave,2.5)

    return wave[min_index:max_index],counts[min_index:max_index],var[min_index:max_index]


def read_fire2(filename):
    """
    
    """
    with fits.open(filename) as hdul:
        header = hdul[1].header
        data=hdul[1].data

    #print(header)
    #print(data,data.shape)

    wave=[i[2]/1e4 for i in data]
    #print(wave,len(wave))
    counts=[i[3] for i in data]
    #print(counts)

    var=[i[1]/i[3] for i in data]

    min_index=find_insert_position(wave,1.5)
    max_index=find_insert_position(wave,2.5)

    return wave[min_index:max_index],counts[min_index:max_index],var[min_index:max_index]

def compare(wave_fire, flux_fire,H_wave, H_flux,K_wave, K_flux,leo_wave, leo_flux):

    scale_H=0
    scale_K=0

    scale_leo=0


    mean_H=np.mean(H_flux)
    mean_K=np.mean(K_flux)
    mean_leo=np.mean(leo_flux)

    mean_H_fire=np.mean(flux_fire[find_insert_position(wave_fire,H_wave[0]):find_insert_position(wave_fire,H_wave[-1])])
    mean_K_fire=np.mean(flux_fire[find_insert_position(wave_fire,K_wave[0]):find_insert_position(wave_fire,K_wave[-1])])
    mean_leo_fire=np.mean(flux_fire[find_insert_position(wave_fire,leo_wave[0]):find_insert_position(wave_fire,leo_wave[-1])])
    scale_H=mean_H_fire/mean_H
    scale_K=mean_K_fire/mean_K
    scale_leo=mean_leo_fire/mean_leo

    print(f"Scale factor for H_BC: {scale_H}")
    print(f"Scale factor for K_BC: {scale_K}")
    print(f"Scale factor for Leo: {scale_leo}")

    H_flux_scaled = H_flux * scale_H
    K_flux_scaled = K_flux * scale_K
    leo_flux_scaled = leo_flux * scale_leo

    plt.figure(figsize=(12, 4))
    plt.plot(H_wave, H_flux_scaled, color='green', label='H_BC Spectrum')
    plt.plot(K_wave, K_flux_scaled, color='orange', label='K_BC Spectrum')
    plt.plot(wave_fire, flux_fire, color='blue', label='FIRE Spectrum')
    
    plt.plot(leo_wave, leo_flux_scaled, color='red', label='Leo Spectrum')
    plt.xlabel('Wavelength (μm)')
    plt.ylabel('Flux (normalized)')
    plt.title('Comparison of FIRE, H_BC, K_BC, and Leo Spectra')
    plt.legend()
    plt.tight_layout()
    plt.show()

fire_path='fire/coadded_spectrum.txt'
#wave_fire, flux_fire, var_fire = read_fire1(fire_path)#读取tellricorr之后的
wave_fire, flux_fire, var_fire = get_txt_fire(fire_path) #读取tellricorr之后的

#wave_fire,flux_fire,var_fire=read_fire2('/mnt/disk1/myresource/fire_reduction/magellan_fire_long_A/74/spec1d_fire_0074-COCONUTS-2A_FIRE_85970523T110233.000.fits') #读取tellricorr之后的



H_path='code/part3_new_data/datas/H_BC.txt'
K_path='code/part3_new_data/datas/K_BC.txt'
H_wave, H_flux, H_error = get_txt(H_path)
K_wave, K_flux, K_error = get_txt(K_path)

leo_path='code/part3_new_data/datas/AD_Leo_M3V.txt'
leo_wave, leo_flux, leo_error = get_txt(leo_path)
a=1.52
b=1.70
leo_wave=leo_wave[find_insert_position(leo_wave,a):find_insert_position(leo_wave,b)]
leo_flux=leo_flux[find_insert_position(leo_wave,a):find_insert_position(leo_wave,b)]
leo_error=leo_error[find_insert_position(leo_wave,a):find_insert_position(leo_wave,b)]

compare(wave_fire, flux_fire,H_wave, H_flux,K_wave, K_flux,leo_wave, leo_flux)


