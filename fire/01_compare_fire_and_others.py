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

def process(wavelength,flux,error,wavelength1,flux1,error1,wavelength2,flux2,error2,modes_name,save_dir="code/part3_new_data/outcomes_5/IRTF_compare"):
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




def read_fire(filename):
    """
    
    """
    with fits.open(filename) as hdul:
        header = hdul[1].header
        data=hdul[1].data

    #print(header)
    #print(data,data.shape)

    wave=[i[0]/1e4 for i in data]
    print(wave,len(wave))
    counts=[i[1] for i in data]
    #print(counts)

    var=[i[1]/i[3] for i in data]

    return wave,counts,var

def compare(fire_wave,leo_wave,H_wave,fire_flux,leo_flux,H_flux):
    '''将leo的光谱插值到fire的波长上，然后进行比较'''

    leo_wave=leo_wave[:find_insert_position(leo_wave,2.16)]
    leo_flux=leo_flux[:find_insert_position(leo_wave,2.16)]


    leo_wave_new=fire_wave[find_insert_position(fire_wave,leo_wave[0]):find_insert_position(fire_wave,leo_wave[-1])]
    H_wave_new=fire_wave[find_insert_position(fire_wave,H_wave[0]):find_insert_position(fire_wave,H_wave[-1])]
    leo_flux_interp = interp_1d(leo_wave, leo_flux, leo_wave_new, kind='linear', extrapolate=True)
    H_flux_interp = interp_1d(H_wave, H_flux, H_wave_new, kind='linear', extrapolate=True)

    scale_leo = np.mean(fire_flux[find_insert_position(fire_wave,leo_wave[0]):find_insert_position(fire_wave,leo_wave[-1])]) / np.mean(leo_flux_interp)
    scale_H = np.mean(fire_flux[find_insert_position(fire_wave,H_wave[0]):find_insert_position(fire_wave,H_wave[-1])]) / np.mean(H_flux_interp)

    print(f"Scale factor for AD Leo: {scale_leo}")
    print(f"Scale factor for H_BC: {scale_H}")

    leo_flux_interp *= scale_leo
    H_flux_interp *= scale_H



    plt.figure(figsize=(12, 4))
    plt.plot(fire_wave, fire_flux, color='blue', label='FIRE Spectrum')
    plt.plot(leo_wave_new, leo_flux_interp, color='red', label='AD Leo Spectrum')
    plt.plot(H_wave_new, H_flux_interp, color='green', label='H_BC Spectrum    ')
    plt.xlabel('Wavelength (μm)')
    plt.ylabel('Flux (normalized)')
    plt.title('Comparison of FIRE, AD Leo, and H_BC Spectra')
    plt.legend()
    plt.tight_layout()
    plt.show()

    

    





fire_path='/mnt/disk1/myresource/fire_reduction/magellan_fire_long_A/flux/spec1d_fire_0074-COCONUTS-2A_FIRE_85970523T110233.000_tellcorr.fits'
wave_fire, flux_fire, var_fire = read_fire(fire_path)

leo_path='code/part3_new_data/datas/AD_Leo_M3V.txt'
H_path='code/part3_new_data/datas/H_BC.txt'

leo_wave, leo_flux, leo_error = get_txt(leo_path)
H_wave, H_flux, H_error = get_txt(H_path)


# plot_1d_spectrum(wave_fire, flux_fire)
# plot_1d_spectrum(leo_wave, leo_flux)
# plot_1d_spectrum(H_wave, H_flux)
compare(wave_fire, leo_wave, H_wave, flux_fire, leo_flux, H_flux)