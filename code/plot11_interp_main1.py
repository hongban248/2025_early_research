



from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from cycler import cycler
import math
from scipy.interpolate import interp1d, CubicSpline
import os
import subprocess
import csv
#subprocess.run(['pwd'], check=True,shell=True)
def get_data(path):
    with fits.open(path) as hdul:
        wavelength = hdul[3].data  # WAVELENGTH扩展
        spectrum = hdul[1].data  # SPEC_DIVIDE_A0V扩

    return wavelength[3:26,:],spectrum[3:26,:]

def get_var(path):
    with fits.open(path)as hdul:
        data=hdul[2].data
    return data[3:26,:]

def plot_1d_spectrum(wave_1d, flux_1d):
    plt.figure(figsize=(12, 4))
    plt.plot(wave_1d, flux_1d, lw=1, color='k')
    plt.xlabel('Wavelength (μm)')
    plt.ylabel('Flux (normalized)')
    plt.title('Merged 1-D Spectrum')
    plt.tight_layout()
    plt.show()

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


def process_data(wavelength,spectrum,var,save_path):
    var=var**0.5 
    uncer=var  #标准差

    tail_index_1=len(wavelength[0])-1

    wavelength_id=[]
    spectrum_id=[]
    var_id=[]
    
    for i in range(len(wavelength)-1):
        # 画图
        plt.figure(figsize=(15, 10))
        plt.plot(wavelength[i][0:find_insert_position(wavelength[i],wavelength[i+1][-1])], spectrum[i][0:find_insert_position(wavelength[i],wavelength[i+1][-1])], color='blue', label='Dataset 1')
        plt.plot(wavelength[i+1][find_insert_position(wavelength[i+1],wavelength[i][0]):-1], spectrum[i+1][find_insert_position(wavelength[i+1],wavelength[i][0]):-1], color='red', label='Dataset 2')

        # 添加图例和标题
        plt.legend()
        plt.title("Two datasets on the same plot")
        plt.xlabel("X-axis")
        plt.ylabel("Y-axis")
        picked = []  # 用来存两次点击的横坐标

        def on_click(event):
            # 忽略：坐标轴外侧、正在拖动/缩放、双击
            if (event.inaxes is None or
                event.canvas.toolbar.mode != '' or
                event.dblclick):
                print("请在坐标轴内单击选择点（非双击），按两次 Esc 键结束选择")
                return

            picked.append(float(event.xdata))
            print(f"已记录第 {len(picked)} 个点：{picked[-1]:.3f}")

            if len(picked) == 2:
                event.canvas.mpl_disconnect(cid)
                plt.close(event.canvas.figure)   # 只关这一次

        # 先注册回调，再 show
        cid = plt.gcf().canvas.mpl_connect('button_press_event', on_click)
        plt.show()   # 阻塞等待交互

        # 此时回调已执行完，picked 一定有两个元素
        number_1, number_2 = picked

        # # 解析两次点击的横坐标
        # number_1 = float(pts[0][0])   # 第一次点击的 x
        # number_2 = float(pts[1][0])   # 第二次点击的 x

        #number_1=float(input("请输入第一个数据集的头部波长："))
        head_index_1=find_insert_position(wavelength[i],number_1)
        middle_index_2=find_insert_position(wavelength[i+1],number_1)

        #number_2=float(input("请输入第二个数据集的尾部波长："))
        middle_index_1=find_insert_position(wavelength[i],number_2)
        tail_index_2=find_insert_position(wavelength[i+1],number_2)

        for j in range(middle_index_1,tail_index_1+1):
            wavelength_id.append(wavelength[i][j])
            spectrum_id.append(spectrum[i][j])
            var_id.append(var[i][j])

        average_1=np.mean(spectrum[i][head_index_1:middle_index_1+1])  #各自加权平均
        temp_spectrum=[]
        for j in range(head_index_1,middle_index_1):
            spectrum_new=interp_1d(wavelength[i+1],spectrum[i+1],wavelength[i][j],kind='linear',extrapolate=True)
            temp_spectrum.append(spectrum_new)
        average_2=np.mean(temp_spectrum)   #各自加权平均
        #加权？求scale其实不需要插值，只在乎加权平均值的
        scale=average_1/average_2
        for j in range(len(wavelength[i+1])):
            spectrum[i+1][j]=spectrum[i+1][j]*scale
            var[i+1][j]=var[i+1][j]*scale**2
        print(f"scale={scale}, average_1={average_1}, average_2={average_2}")

        temp_spectrum_id=[]
        temp_wavelength_id=[]
        temp_var_id=[]

        for j in range(head_index_1,middle_index_1):
            y1=interp_1d(wavelength[i+1],spectrum[i+1],wavelength[i][j],kind='linear',extrapolate=True)
            y2=spectrum[i][j]

            var1=interp_1d(wavelength[i+1],var[i+1],wavelength[i][j],kind='linear',extrapolate=True)
            var2=var[i][j]

            y_new=(y1/var1**2+ y2/var2**2)/(1/var1**2+1/var2**2)
            var_new=(1/var1**2+1/var2**2)**-0.5
            temp_spectrum_id.append(y_new)
            temp_wavelength_id.append(wavelength[i][j])
            temp_var_id.append(var_new)

            spectrum_id.append(y_new)
            wavelength_id.append(wavelength[i][j])
            var_id.append(var_new)

        plt.figure(figsize=(20, 15))
        #plt.text(2, 0.8,f"scale={scale}, average_1={average_1}, average_2={average_2}", fontsize=30, color='black')

        # 上图
        plt.subplot(4, 1, 1)
        plt.plot(wavelength[i][head_index_1:middle_index_1], spectrum[i][head_index_1:middle_index_1], color='blue', label='Dataset 1')
        plt.plot(wavelength[i+1][middle_index_2:tail_index_2], spectrum[i+1][middle_index_2:tail_index_2], color='red', label='Dataset 2')
        plt.axvspan(xmin=number_1, xmax=number_2, color='green', alpha=0.3, label='Selected Range')
        plt.xlabel('Wavelength (μm)')
        plt.ylabel('Flux (normalized)')
        plt.title(f'Spectrum Comparison_scale={scale}')

        # 中图
        plt.subplot(4, 1, 2)
        plt.plot(temp_wavelength_id, temp_spectrum_id, color='purple', label='Merged Spectrum')
        plt.plot(wavelength[i][middle_index_1:find_insert_position(wavelength[i],wavelength[i+1][-1])],spectrum[i][middle_index_1:find_insert_position(wavelength[i],wavelength[i+1][-1])], color='blue', label='Dataset 1')
        plt.plot(wavelength[i+1][find_insert_position(wavelength[i+1],wavelength[i][0]):middle_index_2], spectrum[i+1][find_insert_position(wavelength[i+1],wavelength[i][0]):middle_index_2], color='red', label='Dataset 2')
        plt.xlabel('Wavelength (μm)')
        plt.ylabel('Flux (normalized)')
        plt.axvspan(xmin=number_1, xmax=number_2, color='green', alpha=0.3, label='Selected Range')

        # 下图
        plt.subplot(4, 1, 3)
        signal_to_noise_1=np.array(temp_spectrum_id)/np.array(temp_var_id)
        stn_before=spectrum[i][middle_index_1:find_insert_position(wavelength[i],wavelength[i+1][-1])]/var[i][middle_index_1:find_insert_position(wavelength[i],wavelength[i+1][-1])]
        stn_after=spectrum[i+1][find_insert_position(wavelength[i+1],wavelength[i][0]):middle_index_2]/var[i+1][find_insert_position(wavelength[i+1],wavelength[i][0]):middle_index_2]
        plt.plot(temp_wavelength_id, signal_to_noise_1, color='blue', label='Dataset 1 Variance')


        plt.plot(wavelength[i][middle_index_1:find_insert_position(wavelength[i],wavelength[i+1][-1])],stn_before, color='blue', label='Dataset 1')
        plt.plot(wavelength[i+1][find_insert_position(wavelength[i+1],wavelength[i][0]):middle_index_2], stn_after, color='red', label='Dataset 2')
        
        plt.xlabel('Wavelength (μm)')
        plt.ylabel('signal to noise ratio')
        plt.axvspan(xmin=number_1, xmax=number_2, color='green', alpha=0.3, label='Selected Range')

        # 最下图
        plt.subplot(4, 1, 4)
        
        plt.plot(wavelength[i][0:find_insert_position(wavelength[i],wavelength[i+1][-1])], spectrum[i][0:find_insert_position(wavelength[i],wavelength[i+1][-1])], color='blue', label='Dataset 1')
        plt.plot(wavelength[i+1][find_insert_position(wavelength[i+1],wavelength[i][0]):-1], spectrum[i+1][find_insert_position(wavelength[i+1],wavelength[i][0]):-1], color='red', label='Dataset 2')
        plt.axvspan(xmin=number_1, xmax=number_2, color='green', alpha=0.3, label='Selected Range')
        plt.xlabel('Wavelength (μm)')
        plt.ylabel('Flux (normalized)')
        plt.tight_layout()
        save_path1=os.path.join(save_path, f'SDCH_20240203_0071_middle_{i}.png')
        plt.savefig(save_path1)
        plt.show()

        tail_index_1=middle_index_2

    return wavelength_id, spectrum_id, var_id


def make_csv(path, wavelength, spectrum, dev):
    with open(path, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['wavelength', 'spectrum', 'dev'])
        
        for j in range(len(wavelength)):
            writer.writerow([ wavelength[j], spectrum[j], dev[j]])


        
        

if __name__=='__main__':
    
    path='datas/20240203_0071/SDCH_20240203_0071.spec_a0v.fits'
    #path='datas/20240203_0071/SDCK_20240203_0071.spec_a0v.fits'

    

    wavelength,spectrum=get_data(path=path)
    var=get_var(path=path)

    wavelength_id, spectrum_id, var_id=process_data(wavelength,spectrum,var,'code/outcome/SDCH_20240203_0071_middle')
    wavelength_id, spectrum_id, var_id=sort(wavelength_id, spectrum_id, var_id)

    make_csv('code/outcome/SDCH_20240203_0071_middle/outcome.csv', wavelength_id, spectrum_id, var_id)

