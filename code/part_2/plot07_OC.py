import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from cycler import cycler
import math
from scipy.interpolate import interp1d, CubicSpline
import tkinter as tk


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
        return wavelength[find_insert_position(wavelength,0.8):find_insert_position(wavelength,2.5)],flux[find_insert_position(wavelength,0.8):find_insert_position(wavelength,2.5)],error[find_insert_position(wavelength,0.8):find_insert_position(wavelength,2.5)]
    except:
        wavelength, flux = np.loadtxt(file_path,
                                     comments='#',      # 跳过所有 # 开头的行
                           unpack=True)       # 直接拆成2列数组
        wavelength=wavelength/1e4
        e=flux
        return wavelength[find_insert_position(wavelength,0.8):find_insert_position(wavelength,2.5)],flux[find_insert_position(wavelength,0.8):find_insert_position(wavelength,2.5)],e[find_insert_position(wavelength,0.8):find_insert_position(wavelength,2.5)]
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


def plot_OC(wavelength_model,flux_model,wavelength_data,flux_data,error_data,ck,output_path=False,double=False):

    plt.figure(figsize=(20, 15))
    plt.subplot(3, 1, 1)
    if double==False:
        plt.plot(wavelength_data, flux_data, label='Observed Spectrum', color='blue')
        plt.plot(wavelength_model, flux_model*ck, label='Model Spectrum', color='red')
    else:
        plt.plot(wavelength_data[0], flux_data[0], label='Observed Spectrum H band', color='blue')
        plt.plot(wavelength_data[1], flux_data[1], label='Observed Spectrum K band', color='cyan')
        plt.plot(wavelength_model[0], flux_model[0]*ck, label='Model Spectrum H band', color='red')
        plt.plot(wavelength_model[1], flux_model[1]*ck, label='Model Spectrum K band', color='green')
    plt.xlabel('Wavelength (um)')
    plt.ylabel('Flux')
    plt.title('Spectrum Comparison')
    plt.legend()

    plt.subplot(3, 1, 2)
    if double==False:
        plt.plot(wavelength_data, flux_data - interp_1d(wavelength_model, flux_model*ck, wavelength_data), label='O-C', color='black')
    else:
        plt.plot(wavelength_data[0], flux_data[0] - interp_1d(wavelength_model[0], flux_model[0]*ck, wavelength_data[0]), label='O-C H band', color='black')
        plt.plot(wavelength_data[1], flux_data[1] - interp_1d(wavelength_model[1], flux_model[1]*ck, wavelength_data[1]), label='O-C K band', color='gray')
    plt.xlabel('Wavelength (um)')
    plt.ylabel('O-C')
    plt.title('Observed - Model')
    plt.legend()    
    plt.xlabel('Wavelength (um)')

    plt.subplot(3, 1, 3)
    if double==False:
        plt.plot(wavelength_data, (flux_data - interp_1d(wavelength_model, flux_model*ck, wavelength_data))/error_data, label='(O-C)/Error', color='purple')
    else:
        plt.plot(wavelength_data[0], (flux_data[0] - interp_1d(wavelength_model[0], flux_model[0]*ck, wavelength_data[0]))/error_data[0], label='(O-C)/Error H band', color='purple')
        plt.plot(wavelength_data[1], (flux_data[1] - interp_1d(wavelength_model[1], flux_model[1]*ck, wavelength_data[1]))/error_data[1], label='(O-C)/Error K band', color='magenta')
    plt.xlabel('Wavelength (um)')
    plt.ylabel('(O-C)/Error')
    plt.title('Normalized Residuals')   
    plt.legend()

    if output_path:
        plt.savefig(output_path)
    plt.show()


if __name__ == "__main__":
    data_file_H='code/part_2/data_for_part2/H_BC.txt'
    data_file_K='code/part_2/data_for_part2/K_BC.txt'

    model_file_H='models/bt-settle_H_vr_vsini/bt-settl_131.dat.txt_vr0_vsini10.txt'
    model_file_K='models/bt-settle_K_vr_vsini/bt-settl_131.dat.txt_vr0_vsini10.txt'

    wavelength_data_H,flux_data_H,error_data_H=sort(*get_txt(data_file_H))
    wavelength_data_K,flux_data_K,error_data_K=sort(*get_txt(data_file_K))
    wavelength_model_H,flux_model_H,error_model_H=sort(*get_txt(model_file_H))
    wavelength_model_K,flux_model_K,error_model_K=sort(*get_txt(model_file_K))

    #print(wavelength_settle_H)
    ck=1.4697491053000887e-18

    plot_OC(wavelength_model_H,flux_model_H,wavelength_data_H,flux_data_H,error_data_H,ck,output_path='code/part_2/outcome_for_part2/middle_figure/OC_plot_H.png',double=False)
    plot_OC(wavelength_model_K,flux_model_K,wavelength_data_K,flux_data_K,error_data_K,ck,output_path='code/part_2/outcome_for_part2/middle_figure/OC_plot_K.png',double=False)
    #plot_OC(np.array([wavelength_model_H,wavelength_model_K]),np.array([flux_model_H,flux_model_K]),np.array([wavelength_data_H,wavelength_data_K]),np.array([flux_data_H,flux_data_K]),np.array([error_data_H,error_data_K]),ck,output_path='code/part_2/outcome_for_part2/middle_figure/OC_plot_HK.png',double=True)    
    plot_OC((wavelength_model_H,wavelength_model_K),(flux_model_H,flux_model_K),(wavelength_data_H,wavelength_data_K),(flux_data_H,flux_data_K),(error_data_H,error_data_K),ck,output_path='code/part_2/outcome_for_part2/middle_figure/OC_plot_HK.png' ,double=True )





