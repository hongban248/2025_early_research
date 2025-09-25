#实现多种彩色来表示每一段的spectrum,而且每一段被'掐头'的同时在条件允许的情况下也‘掐尾’。添加标准差，信噪比（光谱/标准差）。
#实线——光谱
#点划线-.-.标准差
#虚线----信噪比
# 专门画、或者两个图，看重复的信噪比
#不同的重复的地方1.去明显的cut2.2.仍然重复的

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

def plot_with_color3(wavelength,spectrum,var):
    colors = ['red', 'green', 'blue', 'purple', 'orange'] 
    plt.rc('axes', prop_cycle=(cycler('color', colors)))
    plt.figure(figsize=(15, 10))
    for i in range(1,len(wavelength)-1):
        #print(i)

        position1=find_insert_position(wavelength[i],wavelength[i+1][-1])
        #position2=find_insert_position(wavelength[i],wavelength[i-1][0])
        print(position1)
        if(position1>200):

            plt.plot(wavelength[i][position1-150:-150:], spectrum[i][position1-150:-150:], color=colors[i % len(colors)])
            plt.plot(wavelength[i][position1-150:-150:], var[i][position1-150:-150:]**0.5, color='black',linestyle='-.')
            plt.plot(wavelength[i][position1-150:-150:], spectrum[i][position1-150:-150:]/var[i][position1-150:-150:]**0.5, color='brown',linestyle='--')
        else:
            plt.plot(wavelength[i][position1::], spectrum[i][position1::], color=colors[i % len(colors)])
            plt.plot(wavelength[i][position1::], var[i][position1::]**0.5, color='black',linestyle='-.')
            plt.plot(wavelength[i][position1::], spectrum[i][position1::]/var[i][position1::]**0.5, color='brown',linestyle='--')
    
    plt.plot(wavelength[-1], spectrum[-1],color='purple')
    
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
    var=get_var(path=path)
    
    plot_with_color3(wavelength=wavelength,spectrum=spectrum,var=var)