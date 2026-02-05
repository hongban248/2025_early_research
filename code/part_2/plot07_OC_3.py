import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from cycler import cycler
import math
from scipy.interpolate import interp1d, CubicSpline
import tkinter as tk
import coronagraph as cg

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


def plot_OC(wavelength_model,flux_model,wavelength_data,flux_data,error_data,ck,output_path=False,double=False):

    plt.figure(figsize=(20, 15))
    plt.subplot(3, 1, 1)
    if double==False:
        plt.plot(wavelength_data, flux_data, label='Observed Spectrum', color='blue')
        plt.plot(wavelength_model, flux_model*ck, label='Model Spectrum', color='red')
    else:
        plt.plot(wavelength_data[0], flux_data[0], label='Observed Spectrum H band', color='blue')
        plt.plot(wavelength_data[1], flux_data[1], label='Observed Spectrum K band', color='cyan')
        plt.plot(wavelength_model[0], flux_model[0]*ck, label='Model Spectrum H band', color='red')
        plt.plot(wavelength_model[1], flux_model[1]*ck, label='Model Spectrum K band', color='green')
    plt.xlabel('Wavelength (um)')
    plt.ylabel('Flux')
    plt.title('Spectrum Comparison')
    plt.legend()

    plt.subplot(3, 1, 2)
    if double==False:
        plt.plot(wavelength_data, flux_data - interp_1d(wavelength_model, flux_model*ck, wavelength_data), label='O-C', color='black')
    else:
        plt.plot(wavelength_data[0], flux_data[0] - interp_1d(wavelength_model[0], flux_model[0]*ck, wavelength_data[0]), label='O-C H band', color='black')
        plt.plot(wavelength_data[1], flux_data[1] - interp_1d(wavelength_model[1], flux_model[1]*ck, wavelength_data[1]), label='O-C K band', color='gray')
    plt.xlabel('Wavelength (um)')
    plt.ylabel('O-C')
    plt.title('Observed - Model')
    plt.legend()    
    plt.xlabel('Wavelength (um)')

    plt.subplot(3, 1, 3)
    if double==False:
        plt.plot(wavelength_data, (flux_data - interp_1d(wavelength_model, flux_model*ck, wavelength_data))/error_data, label='(O-C)/Error', color='purple')
    else:
        plt.plot(wavelength_data[0], (flux_data[0] - interp_1d(wavelength_model[0], flux_model[0]*ck, wavelength_data[0]))/error_data[0], label='(O-C)/Error H band', color='purple')
        plt.plot(wavelength_data[1], (flux_data[1] - interp_1d(wavelength_model[1], flux_model[1]*ck, wavelength_data[1]))/error_data[1], label='(O-C)/Error K band', color='magenta')
    plt.xlabel('Wavelength (um)')
    plt.ylabel('(O-C)/Error')
    plt.title('Normalized Residuals')   
    plt.legend()

    if output_path:
        plt.savefig(output_path)
    plt.show()

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

def vacuum_to_air(wl_Ang):
    '''
        Converts vacuum wavelengths to air wavelengths using the Ciddor 1996 formula.

        :param wl: input vacuum wavelengths
        :type wl: np.array

        :returns: **wl_air** (*np.array*) - the wavelengths converted to air wavelengths

        .. note::

        CA Prieto recommends this as more accurate than the IAU standard.'''

    sigma = (1e4 / wl_Ang) ** 2
    f = 1.0 + 0.05792105 / (238.0185 - sigma) + 0.00167917 / (57.362 - sigma)
    return wl_Ang / f
def air_to_vacuum(wl_Ang):
    ''' convert air wavelength to vacuum wavelength using the Ciddor 1996 formula
    
        when computing sigma, I simply assume vacuum and air wavelength are the same (as sigma are anyway computed from wavelength in um)
    '''
    sigma = (1e4 / wl_Ang)**2
    f = 1.0 + 0.05792105 / (238.0185 - sigma) + 0.00167917 / (57.362 - sigma)
    return wl_Ang * f


def modfile_model(model_path,vr,vsini):
    #对模型光谱进行径向速度平移和旋转
    #wavelength_model,flux_model,error_model=sort(*get_txt(model_path))
    wavelength,flux=get_cut(model_path)
    
    wavelength_model1=air_to_vacuum(wavelength*1e4)/1e4
    wavelength_model_vr=vr_change(wavelength_model1,flux,vr)
    flux_model_vr_vsini=rot_int_cmj(wavelength_model_vr,flux,vsini)
    return wavelength_model_vr,flux_model_vr_vsini


def plot_OC_all(wavelength_model,flux_model,wave_H,flux_H,error_H,wave_K,flux_K,error_K,ck,output_path=False,temp_flux=None):

    plt.figure(figsize=(20, 15))
    plt.subplot(3, 1, 1)

    plt.plot(wave_H, flux_H, label='Observed Spectrum H band', color='blue')
    plt.plot(wave_K, flux_K, label='Observed Spectrum K band', color='cyan')
    plt.plot(wavelength_model, flux_model*ck, label='Model Spectrum', color='red')
    if temp_flux is not None:
        print(temp_flux)
        plt.plot(wavelength_model, temp_flux*ck, label='Temp Model Spectrum', color='orange')


    plt.xlabel('Wavelength (um)')
    plt.ylabel('Flux')
    plt.title('Spectrum Comparison')
    plt.legend()

    plt.subplot(3, 1, 2)

    plt.plot(wave_H, flux_H - interp_1d(wavelength_model, flux_model*ck, wave_H), label='O-C H band', color='black')
    plt.plot(wave_K, flux_K - interp_1d(wavelength_model, flux_model*ck, wave_K), label='O-C K band', color='gray')

    plt.xlabel('Wavelength (um)')
    plt.ylabel('O-C')
    plt.title('Observed - Model')
    plt.legend()    
    plt.xlabel('Wavelength (um)')

    plt.subplot(3, 1, 3)

    plt.plot(wave_H, (flux_H - interp_1d(wavelength_model, flux_model*ck, wave_H))/error_H, label='(O-C)/Error H band', color='purple')
    plt.plot(wave_K, (flux_K - interp_1d(wavelength_model, flux_model*ck, wave_K))/error_K, label='(O-C)/Error K band', color='magenta')

    plt.xlabel('Wavelength (um)')
    plt.ylabel('(O-C)/Error')
    plt.title('Normalized Residuals')   
    plt.legend()

    if output_path:
        plt.savefig(output_path)
    plt.show()


def plot_H_OC(wavelength_model,flux_model,wave_H,flux_H,error_H,ck,output_path=False):

    # wavelength_model=wavelength_model[find_insert_position(wavelength_model,wave_H[0]):find_insert_position(wavelength_model,wave_H[-1])]
    # flux_model=flux_model[find_insert_position(wavelength_model,wave_H[0]):find_insert_position(wavelength_model,wave_H[-1])]
    plt.figure(figsize=(20, 15))
    plt.subplot(2, 1, 1)

    plt.plot(wave_H, flux_H, label='Observed Spectrum H band', color='blue')
    plt.plot(wavelength_model[find_insert_position(wavelength_model,wave_H[0]):find_insert_position(wavelength_model,wave_H[-1])], flux_model[find_insert_position(wavelength_model,wave_H[0]):find_insert_position(wavelength_model,wave_H[-1])]*ck, label='Model Spectrum', color='red')

    text='teff=3600 logg=5.5 meta=-0.5 alpha=0.2 vr=2.0 vsini=1.0'
    plt.xlabel('Wavelength (um)')
    plt.ylabel('Flux')
    plt.title(f'Spectrum Comparison H band,{text}')
    #plt.text(0.5, 0.5, 'aaaa', transform=plt.gca().transAxes)
    plt.legend()

    # plt.subplot(2, 1, 2)

    # plt.plot(wave_H, flux_H - interp_1d(wavelength_model, flux_model*ck, wave_H), label='O-C H band', color='black')

    # plt.xlabel('Wavelength (um)')
    # plt.ylabel('O-C')
    # plt.title('Observed - Model H band')
    # plt.legend()    
    # plt.xlabel('Wavelength (um)')

    plt.subplot(2, 1, 2)

    plt.plot(wave_H, (flux_H - interp_1d(wavelength_model, flux_model*ck, wave_H))/error_H, label='(O-C)/Error H band', color='purple')
    plt.axhline(y=0, color='black', linewidth=2)  # 黑色粗线

    plt.xlabel('Wavelength (um)')
    plt.ylabel('(O-C)/Error')
    plt.title('Normalized Residuals H band')   
    plt.legend()

    if output_path:
        plt.savefig(output_path)
    plt.show()

def plot_K_OC(wavelength_model,flux_model,wave_K,flux_K,error_K,ck,output_path=False):

    plt.figure(figsize=(20, 15))
    plt.subplot(2, 1, 1)

    plt.plot(wave_K, flux_K, label='Observed Spectrum K band', color='cyan')
    plt.plot(wavelength_model[find_insert_position(wavelength_model,wave_K[0]):find_insert_position(wavelength_model,wave_K[-1])], flux_model[find_insert_position(wavelength_model,wave_K[0]):find_insert_position(wavelength_model,wave_K[-1])]*ck, label='Model Spectrum', color='green')

    text='teff=3600 logg=5.5 meta=-0.5 alpha=0.2 vr=2.0 vsini=1.0'
    plt.xlabel('Wavelength (um)')
    plt.ylabel('Flux')
    plt.title(f'Spectrum Comparison K band,{text}')
    plt.legend()

    plt.subplot(2, 1, 2)

    plt.plot(wave_K, (flux_K - interp_1d(wavelength_model, flux_model*ck, wave_K))/error_K, label='(O-C)/Error K band', color='magenta')
    plt.axhline(y=0, color='black', linewidth=2)  # 黑色粗线

    plt.xlabel('Wavelength (um)')
    plt.ylabel('(O-C)/Error')
    plt.title('Normalized Residuals K band')   
    plt.legend()

    if output_path:
        plt.savefig(output_path)
    plt.show()

if __name__ == "__main__":
    data_file_H='code/part_2/data_for_part2/H_BC.txt'
    data_file_K='code/part_2/data_for_part2/K_BC.txt'

    # model_file_H='models/bt-settle_H_vr_vsini/bt-settl_131.dat.txt_vr0_vsini10.txt'
    # model_file_K='models/bt-settle_K_vr_vsini/bt-settl_131.dat.txt_vr0_vsini10.txt'
    ck=5.79314E-19
    model_file='models/bt-settle/bt-settl_1754.dat.txt'
    wavelength_data_H,flux_data_H,error_data_H=sort(*get_txt(data_file_H))
    wavelength_data_K,flux_data_K,error_data_K=sort(*get_txt(data_file_K))
    #wavelength_model_temp=sort(*get_cut(model_file),np.zeros(len(get_cut(model_file)[0])))
    wavelength_model,flux_model=modfile_model(model_file,vr=2,vsini=1)

    #wavelength_model_temp,flux_model_temp=modfile_model(model_file,vr=0,vsini=0)
    #print(flux_model_temp)

    #plot_OC_all(wavelength_model,flux_model,wavelength_data_H,flux_data_H,error_data_H,wavelength_data_K,flux_data_K,error_data_K,ck,output_path='code/part_2/outcome_for_part2/middle_figure/OC_plot_HK_combined.png',temp_flux=None)
    plot_H_OC(wavelength_model,flux_model,wavelength_data_H,flux_data_H,error_data_H,ck,output_path='code/part_2/outcome_for_part2/middle_figure/OC_plot_H_only.png')
    plot_K_OC(wavelength_model,flux_model,wavelength_data_K,flux_data_K,error_data_K,ck,output_path='code/part_2/outcome_for_part2/middle_figure/OC_plot_K_only.png')

























    # wavelength_data_H,flux_data_H,error_data_H=sort(*get_txt(data_file_H))
    # wavelength_data_K,flux_data_K,error_data_K=sort(*get_txt(data_file_K))
    # wavelength_model_H,flux_model_H,error_model_H=sort(*get_txt(model_file_H))
    # wavelength_model_K,flux_model_K,error_model_K=sort(*get_txt(model_file_K))

    # #print(wavelength_settle_H)
    # ck=1.4697491053000887e-18

    # plot_OC(wavelength_model_H,flux_model_H,wavelength_data_H,flux_data_H,error_data_H,ck,output_path='code/part_2/outcome_for_part2/middle_figure/OC_plot_H.png',double=False)
    # plot_OC(wavelength_model_K,flux_model_K,wavelength_data_K,flux_data_K,error_data_K,ck,output_path='code/part_2/outcome_for_part2/middle_figure/OC_plot_K.png',double=False)
    # #plot_OC(np.array([wavelength_model_H,wavelength_model_K]),np.array([flux_model_H,flux_model_K]),np.array([wavelength_data_H,wavelength_data_K]),np.array([flux_data_H,flux_data_K]),np.array([error_data_H,error_data_K]),ck,output_path='code/part_2/outcome_for_part2/middle_figure/OC_plot_HK.png',double=True)    
    # plot_OC((wavelength_model_H,wavelength_model_K),(flux_model_H,flux_model_K),(wavelength_data_H,wavelength_data_K),(flux_data_H,flux_data_K),(error_data_H,error_data_K),ck,output_path='code/part_2/outcome_for_part2/middle_figure/OC_plot_HK.png' ,double=True )

