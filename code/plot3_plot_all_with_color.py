
#实现多种彩色来表示每一段的spectrum

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

def plot_with_color_and_dev(wavelength,spectrum,var):
    colors = ['red', 'green', 'blue', 'purple', 'orange'] 
    plt.rc('axes', prop_cycle=(cycler('color', colors)))
    plt.figure(figsize=(15, 10))
    for i in range(len(wavelength)):
        plt.plot(wavelength[i], spectrum[i])
    
    # 添加图例
    plt.legend()

    # colors = ['black'] 
    # plt.rc('axes', prop_cycle=(cycler('color', colors)))
    for i in range(len(wavelength)):
        plt.plot(wavelength[i], var[i]**0.5,linestyle='--')
        

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
    #var=get_var(path=path)
    #print(var[15])

    #print(wavelength.shape)
    #plot_with_color(wavelength=wavelength,spectrum=spectrum)
    plot_with_color(wavelength=wavelength,spectrum=spectrum)
