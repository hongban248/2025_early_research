#实现多种彩色来表示每一段的spectrum,而且每一段被'掐头'。

from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from cycler import cycler
import math


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

def get_data(path):
    with fits.open(path) as hdul:
        wavelength = hdul[3].data  # WAVELENGTH扩展
        spectrum = hdul[1].data  # SPEC_DIVIDE_A0V扩

    return wavelength,spectrum

def get_var(path):
    with fits.open(path)as hdul:
        data=hdul[2].data
    return data

def plot_with_color2(wavelength,spectrum):
    colors = ['red', 'green', 'blue', 'purple', 'orange'] 
    plt.rc('axes', prop_cycle=(cycler('color', colors)))
    plt.figure(figsize=(15, 10))
    for i in range(len(wavelength)-1):

        position=find_insert_position(wavelength[i],wavelength[i+1][-1])

        plt.plot(wavelength[i][position::], spectrum[i][position::])
    
    plt.plot(wavelength[-1], spectrum[-1])
    
    # 添加图例
    plt.legend()

    # 添加标题和坐标轴标签
    plt.xlabel('Wavelength (um)')
    plt.ylabel('Flux')
    plt.title('Spectrum')

    # 显示图形
    plt.show()



if __name__=='__main__':
    
    path='datas/20240203_0071/SDCH_20240203_0071.spec_a0v.fits'
    #path='datas/20240203_0071/SDCK_20240203_0071.spec_a0v.fits'


    wavelength,spectrum=get_data(path=path)
    
    plot_with_color2(wavelength=wavelength,spectrum=spectrum)