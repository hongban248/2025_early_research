#尝试这个降分变率
import coronagraph as cg  #这个包还有疑似神秘小bug，需要该一行代码才能调用
#print(cg.__version__)
import coronagraph as cg
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from cycler import cycler
import math
from scipy.interpolate import interp1d, CubicSpline


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


def get_cut(file_path):

    # 设置波长和分辨率参数# Set the wavelength and resolution parameters
    lammin = 0.8  # 最小波长 (μm)
    lammax = 2.5   # 最大波长 (μm)
    R = 45000      # 分辨率


    model_path=file_path
    wave,flux,error=get_txt(model_path)
    #print(wave,len(wave),flux,len(flux))


    # 构造低分辨率的波长网格
    wl, dwl = cg.noise_routines.construct_lam(lammin, lammax, R)

    # 使用 downbin_spec 函数将高分辨率光谱降采样到低分辨率
    flr = cg.downbin_spec(flux, wave, wl, dlam=dwl)

    # 剔除包含 NaN 的部分
    mask = ~np.isnan(wl) 
    wl_clean = wl[mask]
    flr_clean = flr[mask]
    mask = ~np.isnan(flr)
    wl_clean = wl[mask]
    flr_clean = flr[mask]
    wl,flr = wl_clean, flr_clean

    return wl,flr


def get_scale(wavelength_K,flux_K,error_K,wavelength1,flux1,error1):

    #IGRANS 是BT-settle的scale倍
    left_index=find_insert_position(wavelength1,wavelength_K[0])
    right_index=find_insert_position(wavelength1,wavelength_K[-1])
    aver1=np.nanmean(flux1[left_index:right_index])
    mask=~np.isnan(flux_K) 
    wavelength_K_clean = wavelength_K[mask]
    flux_K_clean = flux_K[mask]
    error_K_clean = error_K[mask]

    weight=1/error_K_clean**2
    aver2=np.nansum(flux_K_clean*weight)/np.nansum(weight)
    scale=aver2/aver1
    return scale
        
def interp_spec(wavelength_K,flux_K,error_K,wavelength1,flux1,error1):
    # 对高分辨率光谱进行插值到K上波段的波长点
    left_index=find_insert_position(wavelength1,wavelength_K[0])
    right_index=find_insert_position(wavelength1,wavelength_K[-1])

    wavelength_temp=[]
    flux_temp=[]
    error_temp=[]
    # for i in range(left_index,right_index):
    #     wavelength_temp.append(wavelength_K[i-left_index])
    #     flux_new=interp_1d(wavelength_K,flux_K,wavelength1[i],kind='linear',extrapolate=True)
    #     error_new=interp_1d(wavelength_K,error_K,error1[i],kind='linear',extrapolate=True)
    #     flux_temp.append(flux_new)
    #     error_temp.append(error_new)
    for i in range(len(wavelength_K)):
        wavelength_temp.append(wavelength_K[i])

        flux_new=interp_1d(wavelength1[left_index:right_index],flux1[left_index:right_index],wavelength_K[i],kind='linear',extrapolate=True)
        error_new=interp_1d(wavelength1[left_index:right_index],error1[left_index:right_index],wavelength_K[i],kind='linear',extrapolate=True)

        flux_temp.append(flux_new)
        error_temp.append(error_new)

    wavelength=wavelength1[0:left_index].tolist()+wavelength_temp+wavelength1[right_index:].tolist()
    flux=flux1[0:left_index].tolist()+flux_temp+flux1[right_index:].tolist()
    error=error1[0:left_index].tolist()+error_temp+error1[right_index:].tolist()
    return np.array(wavelength),np.array(flux),np.array(error)



if __name__=='__main__':
    

    k_path='code/part_2/data_for_part2/K.txt'
    
    wavelength_K, flux_K, error_K = get_txt(k_path)
    wavelength_K, flux_K, error_K = sort(wavelength_K, flux_K, error_K)
    
    
    # plt.plot(wavelength_K, flux_K, color='blue', label='K波段')
    # plt.show()
    nub=1
    input_dir = 'models/bt-settle' # 替换为你的文件夹路径
    for file_name in os.listdir(input_dir):
        if file_name.endswith('.txt'):
            file_path = os.path.join(input_dir, file_name)
            print(file_path)
    #file_path = 'models/bt-settle/bt-settl_131.dat.txt'  
            wl,flr=get_cut(file_path)

            scale=get_scale(wavelength_K,flux_K,error_K,wl,flr,np.full(len(flr),0.1))
            print(scale)
            flr=flr*scale

            wl,flr,error=interp_spec(wavelength_K,flux_K,error_K,wl,flr,np.full(len(flr),0.1))

            # plt.figure(figsize=(20, 15))
            # plt.plot(wl, flr, color='blue', label='BT-Settle')
            # plt.plot(wavelength_K, flux_K, color='green', label='K')
            # plt.xlabel('Wavelength (μm)')
            # plt.ylabel('Flux (normalized)')
            # plt.tight_layout()  
            # plt.legend()
            # plt.show()



            # 保存结果
            output_path_dir = 'code/part_2/data_for_part2/bt_settle_cut'
            output_path=os.path.join(output_path_dir, file_path.split('/')[-1].replace('.txt','_cut.txt'))
            if not os.path.exists(output_path_dir):
                os.makedirs(output_path_dir)
            np.savetxt(output_path, np.c_[wl, flr, np.zeros_like(flr)], 
                    header='# wavelength(micron) flux(erg/s/cm2/micron) error(erg/s/cm2/micron)')
            print(f"降采样后的数据已保存到 {output_path}",nub)
            nub=nub+1

    # plt.figure(figsize=(20, 15))
    # plt.plot(wl, flr, color='blue', label='BT-Settle')
    # plt.plot(wavelength_K, flux_K, color='green', label='K')
    # plt.xlabel('Wavelength (μm)')
    # plt.ylabel('Flux (normalized)')
    # plt.tight_layout()  
    # plt.legend()
    # plt.show()









    # print(wl,len(wl),flr,len(flr))
    # plt.figure(figsize=(10, 6))
    # plt.plot(wl, flr, label='Low-Resolution', alpha=0.5)
    # plt.xlabel(r"Wavelength [$\mu$m]")
    # plt.ylabel(r"Flux [erg/s/cm$^2$/$\mu$m]")       
    # plt.show()




#print(wl,len(wl),flr,len(flr))
# 绘制结果
# plt.figure(figsize=(10, 6))
# plt.plot(wave, flux, label='High-Resolution', alpha=0.5)
# plt.plot(wl, flr, label='Low-Resolution', alpha=0.5)
# plt.xlabel(r"Wavelength [$\mu$m]")
# plt.ylabel(r"Flux [erg/s/cm$^2$/$\mu$m]")
# plt.legend()
# plt.title(f"High-Resolution vs Low-Resolution Spectrum (R={R})")
# plt.show()










