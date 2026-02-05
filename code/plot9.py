
#实现多种彩色来表示每一段的spectrum
#同时画出了光谱和误差
#分别去除了前3个和后3个区域的数据

from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from cycler import cycler
import math

def get_data(path):
    with fits.open(path) as hdul:
        wavelength = hdul[3].data  # WAVELENGTH扩展
        spectrum = hdul[1].data  # SPEC_DIVIDE_A0V扩

    return wavelength[3:26,:],spectrum[3:26,:]

def get_var(path):
    with fits.open(path)as hdul:
        data=hdul[2].data
    return data[3:26,:]

def get_signal(path_signal):
    with fits.open(path_signal) as hdul:
        signal = hdul[0].data  # SN扩展
        # print(signal.shape)
        # print(signal[0])
    return signal

def plot_with_color(wavelength,spectrum):
    colors = ['red', 'green', 'blue', 'purple', 'orange'] 
    plt.rc('axes', prop_cycle=(cycler('color', colors)))
    plt.figure(figsize=(15, 10))
    for i in range(len(wavelength)):
        plt.plot(wavelength[i], spectrum[i])
    
    # 添加图例
    plt.legend()

    colors = ['black'] 
    plt.rc('axes', prop_cycle=(cycler('color', colors)))

    # 添加标题和坐标轴标签
    plt.xlabel('Wavelength (um)')
    plt.ylabel('Flux')
    plt.title('Spectrum')

    # 显示图形
    plt.show()


def plot_with_color_and_variance(wavelength, spectrum, var):
    colors = ['red', 'green', 'blue', 'purple', 'orange']
    plt.rc('axes', prop_cycle=cycler('color', colors))

    plt.figure(figsize=(20, 15))

    # 上图
    plt.subplot(2, 1, 1)
    for wl, sp in zip(wavelength, spectrum):
        plt.plot(wl, sp)
    plt.ylabel('Flux')
    plt.title('Spectrum')
    plt.legend()

    # 中图 #自己计算的信噪比
    plt.subplot(2, 1, 2, sharex=plt.gca())  # 共享 x 轴
    #print(var.mean(), spectrum.mean())
    #SToN1 = spectrum / var**0.5  # 计算信噪比
    for wl, v in zip(wavelength, var**0.5):
        plt.plot(wl, v, linestyle='--')
    plt.xlabel('Wavelength (μm)')
    plt.ylabel('variance')

    

    plt.tight_layout()
    plt.show()

def make_overlap_mask(wavelength):
    """
    输入：wavelength 列表，每个元素是一维波长数组
    返回：mask_list   列表，形状与 wavelength 完全一致
          值：1 落在下一段区间
              2 落在上一段区间
              0 无重叠
    """
    mask_list = []
    n_seg = len(wavelength)

    for i, w in enumerate(wavelength):
        w = np.asarray(w)
        mask = np.zeros_like(w, dtype=int)

        # 上一段区间
        if i > 0:
            w_prev = np.asarray(wavelength[i-1])
            mask[np.logical_and(w >= w_prev.min(), w <= w_prev.max())] = 2

        # 下一段区间
        if i < n_seg - 1:
            w_next = np.asarray(wavelength[i+1])
            mask[np.logical_and(w >= w_next.min(), w <= w_next.max())] = 1

        mask_list.append(mask)
    return mask_list


def plot_mask(mask_list):
    """把 mask_list 画成热力图：每段一行"""
    max_len = max(m.size for m in mask_list)
    img = np.full((len(mask_list), max_len), np.nan)

    for i, m in enumerate(mask_list):
        img[i, :m.size] = m

    plt.figure(figsize=(10, 2 * len(mask_list)))
    plt.imshow(img, cmap='tab10', vmin=0, vmax=2, aspect='auto')
    cbar = plt.colorbar(ticks=[0, 1, 2])
    cbar.set_ticklabels(['None', 'Next', 'Prev'])
    plt.xlabel('Pixel index')
    plt.ylabel('Segment index')
    plt.title('Overlap Mask')
    plt.show()




if __name__=='__main__':
    
    path='datas/20240203_0071/SDCH_20240203_0071.spec_a0v.fits'
    #path='datas/20240203_0071/SDCK_20240203_0071.spec_a0v.fits'

    #path_signal='datas/20240203_0071/SDCH_20240203_0071.sn.fits'
    #signal = get_signal(path_signal=path_signal)

    wavelength,spectrum=get_data(path=path)
    var=get_var(path=path)
    #print(var[15])

    #print(wavelength.shape)
    #plot_with_color(wavelength=wavelength,spectrum=spectrum)
    plot_with_color_and_variance(wavelength=wavelength,spectrum=spectrum,var=var)


    mask= make_overlap_mask(wavelength=wavelength)
    
    plot_mask(mask_list=mask)