#本文件先cut原始的bt-settle模型，然后进行vr，vsini处理，最后插值到观测波段
#本脚本仅仅演示单一处理过程的图像绘制


#尝试这个降分变率
import coronagraph as cg  #这个包还有疑似神秘小bug，需要修改一行代码才能调用
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


       
def interp_spec(wavelength_K,flux_K,error_K,wavelength1,flux1,error1):
    # 对高分辨率光谱进行插值到K上波段的波长点
    left_index=find_insert_position(wavelength1,wavelength_K[0])
    print("left_index:",left_index)
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

    # wavelength=wavelength1[0:left_index].tolist()+wavelength_temp+wavelength1[right_index:].tolist()
    # flux=flux1[0:left_index].tolist()+flux_temp+flux1[right_index:].tolist()
    # error=error1[0:left_index].tolist()+error_temp+error1[right_index:].tolist()
    #return np.array(wavelength),np.array(flux),np.array(error)
    return wavelength_temp,flux_temp,error_temp



def rot_int_cmj(w, s, vsini, eps=0.6, nr=10, ntheta=100, dif = 0.0):
    '''
    A routine to quickly rotationally broaden a spectrum in linear time.

    INPUTS:
    s - input spectrum

    w - wavelength scale of the input spectrum
    
    vsini (km/s) - projected rotational velocity
    
    OUTPUT:
    ns - a rotationally broadened spectrum on the wavelength scale w

    OPTIONAL INPUTS:
    eps (default = 0.6) - the coefficient of the limb darkening law
    
    nr (default = 10) - the number of radial bins on the projected disk
    
    ntheta (default = 100) - the number of azimuthal bins in the largest radial annulus
                            note: the number of bins at each r is int(r*ntheta) where r < 1
    
    dif (default = 0) - the differential rotation coefficient, applied according to the law
    Omeg(th)/Omeg(eq) = (1 - dif/2 - (dif/2) cos(2 th)). Dif = .675 nicely reproduces the law
    proposed by Smith, 1994, A&A, Vol. 287, p. 523-534, to unify WTTS and CTTS. Dif = .23 is
    similar to observed solar differential rotation. Note: the th in the above expression is
    the stellar co-latitude, not the same as the integration variable used below. This is a
    disk integration routine.
    
    
    
    Reference:
    RNAAS: Carvalho & Johns-Krull (2023)
    '''

    ns = np.copy(s)*0.0
    tarea = 0.0
    dr = 1./nr
    for j in range(0, nr):
        r = dr/2.0 + j*dr
        area = ((r + dr/2.0)**2 - (r - dr/2.0)**2)/int(ntheta*r) * (1.0 - eps + eps*np.cos(np.arcsin(r)))
        for k in range(0,int(ntheta*r)):
            th = np.pi/int(ntheta*r) + k * 2.0*np.pi/int(ntheta*r)
            if dif != 0:
                vl = vsini * r * np.sin(th) * (1.0 - dif/2.0 - dif/2.0*np.cos(2.0*np.arccos(r*np.cos(th))))
                ns += area * np.interp(w + w*vl/2.9979e5, w, s)
                tarea += area
            else:
                vl = r * vsini * np.sin(th)
                ns += area * np.interp(w + w*vl/2.9979e5, w, s)
                tarea += area
          
    return ns/tarea

def vr_change(wavelength,flux,vr):
    #对光谱进行径向速度平移
    wavelength_vr=wavelength*(1+vr/299792.458)
    return wavelength_vr

if __name__=='__main__':
    

    k_path='code/part_2/data_for_part2/K.txt'
    
    
    plt.figure(figsize=(20,16))
    
    wavelength_K, flux_K, error_K = get_txt(k_path)
    wavelength_K, flux_K, error_K = sort(wavelength_K, flux_K, error_K)
    plt.plot(wavelength_K, flux_K, color='blue', label='K波段')
    plt.xlabel('Wavelength (μm)')
    plt.ylabel('Flux (normalized)')
    plt.title('K波段光谱')
    plt.legend()    

    wavelength_K_vr=vr_change(wavelength_K,flux_K,vr=30)
    plt.plot(wavelength_K_vr, flux_K, color='orange', label='K波段 vr=30km/s')
    plt.xlabel('Wavelength (μm)')
    plt.ylabel('Flux (normalized)')
    plt.title('K波段光谱径向速度平移')
    plt.legend() 

    flux_K_vsini=rot_int_cmj(wavelength_K,flux_K,vsini=30)
    plt.plot(wavelength_K, flux_K_vsini, color='green', label='K波段 vsini=30km/s')
    plt.xlabel('Wavelength (μm)')
    plt.ylabel('Flux (normalized)')
    plt.title('K波段光谱旋转变宽')
    plt.legend()

    
    plt.tight_layout()  
    plt.show()