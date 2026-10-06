import os
import sys
import numpy as np
import pymultinest
import json
import pandas as pd
from astropy import units as u
from astropy.io import fits
from scipy.interpolate import griddata
from scipy.interpolate import interp1d, RegularGridInterpolator
from scipy.ndimage import gaussian_filter1d
from scipy.signal import fftconvolve
import coronagraph as cg
from scipy.interpolate import interp1d, CubicSpline



def get_HiRes_data(HiRes_data_path,a=0.8,b=2.5,wavelength_path='models/HiRes/WAVE_PHOENIX-ACES-AGSS-COND-2011.fits'):
    with fits.open(HiRes_data_path) as hdul:
        HiRes_data=hdul[0].data
        #HiRes_header=hdul[1].header
        #print(HiRes_header)
        #print(HiRes_data.shape)

    with fits.open(wavelength_path) as hdul:
        HiRes_wavelength=hdul[0].data
        #HiRes_wave_header=hdul[0].header
        #(HiRes_wave_header)
        #print(HiRes_wave_header)
    HiRes_wavelength=HiRes_wavelength/10000


    return HiRes_wavelength[find_insert_position(HiRes_wavelength,a):find_insert_position(HiRes_wavelength,b)],\
        HiRes_data[find_insert_position(HiRes_wavelength,a):find_insert_position(HiRes_wavelength,b)]/1e8

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

def get_txt(file_path,a=0.8,b=2.5): #有裁剪
    try:
        wavelength, flux, error = np.loadtxt(file_path,
                                     comments='#',      # 跳过所有 # 开头的行
                                     unpack=True)       # 直接拆成三列数组
        #return wavelength,flux,error
        return wavelength[find_insert_position(wavelength,a):find_insert_position(wavelength,b)],flux[find_insert_position(wavelength,a):find_insert_position(wavelength,b)],error[find_insert_position(wavelength,a):find_insert_position(wavelength,b)]
    except:
        wavelength, flux = np.loadtxt(file_path,
                                     comments='#',      # 跳过所有 # 开头的行
                           unpack=True)       # 直接拆成2列数组
        wavelength=wavelength/1e4
        e=flux
        #return wavelength,flux,e
        return wavelength[find_insert_position(wavelength,a):find_insert_position(wavelength,b)],flux[find_insert_position(wavelength,a):find_insert_position(wavelength,b)],e[find_insert_position(wavelength,a):find_insert_position(wavelength,b)]
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

def HiRes_from_paraments_to_path(teff,logg,meta,alpha,map_dir='models/HiRes/map'):
    if meta==0.0:
        meta='-0.0'

    map_name=f'HiRes_teff{teff}_logg{logg}_meta{meta}_alpha{alpha}.map'
    map_path=os.path.join(map_dir,map_name)
    if os.path.exists(map_path):
        with open(map_path,'r') as f:
            file_path=f.readline().strip()
        return file_path
    else:
        print(f"未找到映射文件: {map_path}")
        return None

def get_cut(file_path,a=0.8,b=2.5,R=45000): #分辨率100

    # 设置波长和分辨率参数# Set the wavelength and resolution parameters
    lammin = a  # 最小波长 (μm)
    lammax = b   # 最大波长 (μm)
    #R = 50      # 分辨率


    model_path=file_path
    wave,flux=get_HiRes_data(model_path)
    print('cccccc',len(wave),len(flux))


    # 构造低分辨率的波长网格
    wl, dwl = cg.noise_routines.construct_lam(lammin, lammax, R)

    print('ddddd',len(wl),dwl)

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


if 1:
    teff_grid_points = np.array([3000,3100,3200,3300,3400,3500,3600,3700,3800,3900,4000] )
    logg_grid_points = np.array( [3.0,3.5,4.0,4.5,5.0,5.5] )
    meta_grid_points = np.array( [-1.0,-0.5,0.0,0.5,1.0] )
    #alpha_grid_points = np.array( [0.0] )

    num_teff_points = len(teff_grid_points)
    num_logg_points = len(logg_grid_points)
    num_meta_points = len(meta_grid_points)
    #num_alpha_points = len(alpha_grid_points)

    grid_point_list = []
    for teff in teff_grid_points:
        for logg in logg_grid_points:
            for meta in meta_grid_points:
                #for alpha in alpha_grid_points:
                 

                            grid_point_list.append([teff, logg, meta])
    num_grid_points = len(grid_point_list)
    print("%d grid points in total"%(num_grid_points)) #330

    for index in range(num_grid_points):  #为了获取num_full
        # 2.4.1 load file
        teff_val, logg_val,meta_val = grid_point_list[index]
        #mod_reader = np.genfromtxt(model_path + 'CEQ/spec_T%d_lg%.1f_CEQ.txt'%(teff_val, logg_val), skip_header=2)
        file_path=HiRes_from_paraments_to_path(teff_val, logg_val, meta_val,0.0)
        raw_wl_mod,raw_fl_mod=get_cut(file_path)  #先转换真空波长，再降低分辨率
        num_full=len(raw_wl_mod)
        print('aaaaaa',num_full)
        break

    fl_full_array = np.ones((num_grid_points, num_full)) * np.nan

    ## 2.4 load models
    model_path='models/HiRes'
    wl_full=None
    num=0

    for index in range(num_grid_points):
        # 2.4.1 load file
        teff_val, logg_val,meta_val = grid_point_list[index]
        file_path=HiRes_from_paraments_to_path(teff_val, logg_val, meta_val,0.0)
        
        raw_wl_mod,raw_fl_mod=get_cut(file_path)  #，再降低分辨率
        print("正在处理模型 %d/%d: teff=%d, logg=%.1f, meta=%.1f"%(index+1,num_grid_points,teff_val, logg_val,meta_val))
        raw_fl_mod = (raw_fl_mod * u.erg / u.s / u.cm**2 / u.Angstrom).to(u.erg / u.s / u.cm**2 / u.Angstrom).value
        #这一步要把模型的单位转换为数据的单位
        # 2.4.2 spectrum
        # downgrade resolution
        wl_mod,fl_mod=raw_wl_mod,raw_fl_mod #get_cut(file_path)已经降分辨率了


        if wl_full is None:
            wl_full=wl_mod

        print('bbbbb',fl_mod.shape,fl_full_array.shape)
        fl_full_array[index] = np.copy(raw_fl_mod)
        print("处理了%d/%d个模型"%(index+1,num_grid_points))
    
    # for i in range(len(wl_mod)):
    #     wl_full.append(wl_mod[i])
    # wl_full=np.array(wl_full)
    ## 2.5 save model spectra and grid points
    np.save('code/part3_new_data/HiRes/step04_pymultinest/bt-settle_points_HK_true.npy', np.array(grid_point_list))#要存
    #np.save(main_path + 'processed/CEQ/ATMOP20_CEQ_spec.npy', np.vstack((wl_c2b, fl_spec_array)) )
    #np.save(main_path + 'processed/CEQ/ATMOP20_CEQ_phot.npy', np.vstack((wl_phot, fl_phot_array)) )
    np.save('code/part3_new_data/HiRes/step04_pymultinest/bt-settle_full_HK_true.npy', np.vstack((wl_full, fl_full_array)) )



 