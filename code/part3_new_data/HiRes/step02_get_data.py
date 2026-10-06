#这个脚本用来读取HiRes的数据

import os
import numpy as np
from astropy.io import fits
from matplotlib import pyplot as plt
from cycler import cycler
import math
from scipy.interpolate import interp1d, CubicSpline
def get_HiRes_data(HiRes_data_path,wavelength_path='models/HiRes/WAVE_PHOENIX-ACES-AGSS-COND-2011.fits'):
    with fits.open(HiRes_data_path) as hdul:
        HiRes_data=hdul[0].data
        #HiRes_header=hdul[1].header
        #print(HiRes_header)
        #print(HiRes_data.shape)

    with fits.open(wavelength_path) as hdul:
        HiRes_wavelength=hdul[0].data
        #HiRes_wave_header=hdul[0].header
        #(HiRes_wave_header)
        #print(HiRes_wave_header)
    
    return HiRes_data/1e8,HiRes_wavelength/10000

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

def HiRes_from_paraments_to_path(teff,logg,meta,alpha,map_dir='models/HiRes/map'):
    if meta==0.0:
        meta='-0.0'

    map_name=f'HiRes_teff{teff}_logg{logg}_meta{meta}_alpha{alpha}.map'
    map_path=os.path.join(map_dir,map_name)
    if os.path.exists(map_path):
        with open(map_path,'r') as f:
            file_path=f.readline().strip()
        return file_path
    else:
        print(f"未找到映射文件: {map_path}")
        return None
    



if __name__ == "__main__":
    HiRes_data_path=HiRes_from_paraments_to_path(teff=3500,logg=5.5,meta=0.0,alpha=-0.20)
    print(HiRes_data_path)
    HiRes_data,HiRes_wavelength=get_HiRes_data(HiRes_data_path)
    print(HiRes_data.shape)
    print(HiRes_wavelength.shape)
    print(HiRes_wavelength)

    btsteel_path='models/bt-settle/bt-settl_1591.dat.txt'
    btsteel_wavelength,btsteel_flux,aaaaaa=get_txt(btsteel_path)

    data_path='code/part3_new_data/datas/H_BC.txt'
    data_wavelength,data_flux,data_var=get_txt(data_path)
    scale=np.median(HiRes_data)/np.median(data_flux)
    data_flux=data_flux*scale

    #绘制光谱图
    plt.figure(figsize=(10, 6))
    plt.plot(HiRes_wavelength, HiRes_data, label='HiRes Spectrum')
    plt.plot(btsteel_wavelength, btsteel_flux, label='BT-Settl Spectrum')
    plt.plot(data_wavelength, data_flux, label='Observed Spectrum')
    plt.xlabel('Wavelength (um)')
    plt.ylabel('Flux')
    plt.title('HiRes Spectrum')
    plt.legend()
    # plt.xlim(3000, 25000)  # 根据需要调整波长范围
    # plt.ylim(0, 1.2)  # 根据需要调整通量范围
    plt.grid()
    plt.show()
