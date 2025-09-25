
#实现多种彩色来表示每一段的spectrum
#同时画出了光谱和对应的用两种方法计算的信噪比

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

    return wavelength,spectrum

def get_var(path):
    with fits.open(path)as hdul:
        data=hdul[2].data
    return data

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


def plot_with_color_and_SToN(wavelength, spectrum, var, signal):
    colors = ['red', 'green', 'blue', 'purple', 'orange']
    plt.rc('axes', prop_cycle=cycler('color', colors))

    plt.figure(figsize=(20, 15))

    # 上图
    plt.subplot(3, 1, 1)
    for wl, sp in zip(wavelength, spectrum):
        plt.plot(wl, sp)
    plt.ylabel('Flux')
    plt.title('Spectrum')
    plt.legend()

    # 中图 #自己计算的信噪比
    plt.subplot(3, 1, 2, sharex=plt.gca())  # 共享 x 轴
    #print(var.mean(), spectrum.mean())
    SToN1 = spectrum / var**0.5  # 计算信噪比
    for wl, v in zip(wavelength, SToN1):
        plt.plot(wl, v, linestyle='--')
    plt.xlabel('Wavelength (μm)')
    plt.ylabel('Signal-to-Noise Ratio (S/N)1')

    #下图，文件中的信噪比
    plt.subplot(3, 1, 3, sharex=plt.gca())
    SToN2 = signal  # 从文件中读取的信噪比
    for wl, sn in zip(wavelength, SToN2):
        plt.plot(wl, sn, linestyle='--')
    plt.xlabel('Wavelength (μm)')
    plt.ylabel('Signal-to-Noise Ratio (S/N)2')

    plt.tight_layout()
    plt.show()


if __name__=='__main__':
    
    path='datas/20240203_0071/SDCH_20240203_0071.spec_a0v.fits'
    path='datas/20240203_0071/SDCK_20240203_0071.spec_a0v.fits'
    path_signal='datas/20240203_0071/SDCH_20240203_0071.sn.fits'
    signal = get_signal(path_signal=path_signal)

    wavelength,spectrum=get_data(path=path)
    var=get_var(path=path)
    #print(var[15])

    #print(wavelength.shape)
    #plot_with_color(wavelength=wavelength,spectrum=spectrum)
    plot_with_color_and_SToN(wavelength=wavelength,spectrum=spectrum,var=var, signal=signal)


