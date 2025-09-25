from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def get_data(path):
    with fits.open(path) as hdul:
        wavelength = hdul[3].data  # WAVELENGTH扩展
        spectrum = hdul[1].data  # SPEC_DIVIDE_A0V扩

    return wavelength,spectrum


def data_process(data1,data2):
    # 获取data1排序后的索引
    sorted_indices = np.argsort(data1)
    
    # 使用排序索引重新排列data1和data2
    sorted_data1 = data1[sorted_indices]
    sorted_data2 = data2[sorted_indices]
    
    return sorted_data1, sorted_data2

def try_plot(data1,data2):
    # 绘制光谱图
            plt.figure(figsize=(15, 10))
            plt.plot(data1, data2, label='Corrected Spectrum')
            plt.xlabel('Wavelength (um)')
            plt.ylabel('Flux')
            plt.title('Spectrum')
            plt.legend()
            plt.grid(True)
            plt.show()


if __name__=='__main__':
    
    path='datas/20240203_0071/SDCH_20240203_0071.spec_a0v.fits'
    #path='datas/20240203_0071/SDCK_20240203_0071.spec_a0v.fits'
    wavelength,spectrum=get_data(path=path)

    data1 =wavelength.flatten()
    data2 =spectrum.flatten()
    #print(data1.shape,28*2048,wavelength[0][3],data1[3])

    #try_plot([1,2,5,10],[1,1,5,4])
    data3,data4=data_process(data1,data2)
    try_plot(data3,data4)



    # print(wavelength[0])
    # print(wavelength[1])
    # print(type(spectrum[3][4]))

    # num=0
    # index=0
    # for i in spectrum[0]:
    #     #print(index,i)
        
    #     if str(i)=='nan':
    #         num=num+1
    #         print(index,i)
    #     index=index+1
    # print(num)

