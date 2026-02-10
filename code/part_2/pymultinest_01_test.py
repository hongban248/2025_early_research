import os
import sys
#sys.path.append("/data/users/zzhan485/python_scripts/")
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

def parament_to_filename(teff, logg, meta, alpha, mapfilepath="models/bt-settle/map"):
    """
    将给定的teff、logg、meta和alpha参数转换为对应的txt文件名格式。
    
    参数:
        teff (float): 有效温度。
        logg (float): 表面重力。
        meta (float): 金属丰度。
        alpha (float): α元素丰度。舍弃
    """
    map_name="btsettl_T{:.0f}_lg{:.1f}_m{:.1f}_a{:.1f}.map".format(teff, logg, meta, alpha)
    map_file_path=os.path.join(mapfilepath, map_name)
    #print(map_file_path)
    if os.path.exists(map_file_path):
        f=open(map_file_path,'r')
        text=f.readlines()
        f.close()
        file_path=text[0].strip()
        print("存在的文件名为：", map_file_path)
        return file_path
    else:
        print("文件不存在：", map_file_path)
        return None



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

import ctypes
lib_path='code/part_2/func_export.so'
lib = ctypes.CDLL(str(lib_path))

# def  vr_change_c(wavelength,flux,vr):
#     wave = np.asarray(wavelength, dtype=np.float64, order='C')
#     flux = np.asarray(flux,      dtype=np.float64, order='C')
#     wave = np.require(wave, requirements='CW')
#     n=wave.size
#     wave_vr = np.empty_like(wave)
#     #wave = np.require(wave, requirements='CW')
#     lib.vr_change_export.argtypes=(
#         ctypes.POINTER(ctypes.c_double),
#         ctypes.POINTER(ctypes.c_double),
#         ctypes.c_int,
#         ctypes.c_double,
#         ctypes.POINTER(ctypes.c_double)
#     )
#     lib.vr_change_export.restype=None

#     lib.vr_change_export(
#         wave.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
#         flux.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
#         ctypes.c_int(n),ctypes.c_double(vr),
#         wave_vr.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
#     )

#     return wave_vr

# def rot_int_cmj_c(w, s, vsini, eps=0.6, nr=10, ntheta=100, dif = 0.0):
#     wave = np.asarray(w, dtype=np.float64, order='C')
#     flux = np.asarray(s,      dtype=np.float64, order='C')
#     wave = np.require(wave, requirements='CW')
#     flux = np.require(flux, requirements='CW')
#     n=wave.size
#     ns=np.empty_like(wave)

#     lib.rot_int_cmj_export.argtypes=(
#         ctypes.POINTER(ctypes.c_double),
#         ctypes.POINTER(ctypes.c_double),
#         ctypes.c_int,
#         ctypes.c_double,
#         ctypes.c_double,ctypes.c_int,ctypes.c_int,ctypes.c_double,
#         ctypes.POINTER(ctypes.c_double)
#     )
#     lib.rot_int_cmj_export.restype=None

#     lib.rot_int_cmj_export(
#         wave.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
#         flux.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
#         ctypes.c_int(n),ctypes.c_double(vsini),
#         ctypes.c_double(eps),ctypes.c_int(nr),ctypes.c_int(ntheta),ctypes.c_double(dif),
#         ns.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
#     )
#     return ns

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
    ### 2. load BT-Settl models
    ## 2.1 parameter space #方阵
    teff_grid_points = np.array( list(np.arange(3000, 4001,100)) )
    logg_grid_points = np.arange(3, 5.51, 0.5)
    meta_grid_points = np.array( [ -0.5] )#guid
    alpha_grid_points = np.array( [0.2] )#改为动态调整
    # vr_grid_points = np.array( [0.0, 2.0, 4.0] ) #vr,vsini无需grid，可以连续变化的量
    # vsini_grid_points = np.array( [0.0, 5.0, 10.0] )
    #只关注模型参数teff,logg,meta的方阵，不考虑vr,vsini，R的方阵
    num_teff_points = len(teff_grid_points)
    num_logg_points = len(logg_grid_points)
    num_meta_points = len(meta_grid_points)
    num_alpha_points = len(alpha_grid_points)
    # num_vr_points = len(vr_grid_points)
    # num_vsini_points = len(vsini_grid_points)
    # print("%d teff points"%(num_teff_points))
    # print("%d logg points"%(num_logg_points))
    # print("%d meta points"%(num_meta_points))
    # print("%d alpha points"%(num_alpha_points))
    # print("%d vr points"%(num_vr_points))
    # print("%d vsini points"%(num_vsini_points))

    ## 2.2 grid points
    grid_point_list = []
    for teff in teff_grid_points:
        for logg in logg_grid_points:
            for meta in meta_grid_points:
                for alpha in alpha_grid_points:
                    # for vr in vr_grid_points:
                    #     for vsini in vsini_grid_points:

                            grid_point_list.append([teff, logg, meta, alpha])
    num_grid_points = len(grid_point_list)
    print("%d grid points in total"%(num_grid_points))
    ## 2.3 create empty arrays
    # fl_spec_array = np.ones((num_grid_points, num_pixel)) * np.nan
    # fl_phot_array = np.ones((num_grid_points, num_phot)) * np.nan


    for index in range(num_grid_points):  #为了获取num_full
        # 2.4.1 load file
        teff_val, logg_val,meta_val,alpha_val = grid_point_list[index]
        #mod_reader = np.genfromtxt(model_path + 'CEQ/spec_T%d_lg%.1f_CEQ.txt'%(teff_val, logg_val), skip_header=2)
        file_path=parament_to_filename(teff_val, logg_val, meta_val,alpha_val)
        raw_wl_mod,raw_fl_mod=get_cut(file_path)
        num_full=len(raw_wl_mod)
        break


    fl_full_array = np.ones((num_grid_points, num_full)) * np.nan
    ## 2.4 load models
    model_path='models/bt-settle'
    wl_full=None
    num=0
    for index in range(num_grid_points):
        # 2.4.1 load file
        teff_val, logg_val,meta_val,alpha_val = grid_point_list[index]
        #mod_reader = np.genfromtxt(model_path + 'CEQ/spec_T%d_lg%.1f_CEQ.txt'%(teff_val, logg_val), skip_header=2)
        file_path=parament_to_filename(teff_val, logg_val, meta_val,alpha_val)
        raw_wl_mod,raw_fl_mod=get_cut(file_path)  #先转换真空波长，再降低分辨率
        #raw_wl_mod = mod_reader[:,0]
        raw_fl_mod = (raw_fl_mod * u.erg / u.s / u.cm**2 / u.Angstrom).to(u.erg / u.s / u.cm**2 / u.Angstrom).value
        #这一步要把模型的单位转换为数据的单位
        # 2.4.2 spectrum
        # downgrade resolution
        #fl_mod = cg.downbin_spec(raw_fl_mod, raw_wl_mod, wl_mod, dlam=dwl_mod)
        wl_mod,fl_mod=raw_wl_mod,raw_fl_mod #get_cut(file_path)已经降分辨率了

        wl_mod=air_to_vacuum(wl_mod*1e4)/1e4  #转换为真空波长coconut
        #在把模型插值波长转换到coconut-2a上，H，K分开做

        # wl_mod=vr_change_c(wl_mod,fl_mod,vr_val)  #视向速度修正
        # fl_mod=rot_int_cmj_c(wl_mod,fl_mod,vsini_val)  #旋转变宽






        if wl_full is None:
            wl_full=wl_mod

        #id_good = np.where(np.isnan(fl_mod) == False)
        # re-sampling
        # fl_spec_array[index] = interp1d(wl_mod[id_good], fl_mod[id_good])(wl_c2b)
        # # 2.4.3 photometry
        # fl_phot_array[index] = cg.downbin_spec(raw_fl_mod, raw_wl_mod, wl_phot, dlam=dwl_phot)
        # 2.4.4 full specrum
        fl_full_array[index] = np.copy(raw_fl_mod)
        print("处理了%d/%d个模型"%(index+1,num_grid_points))
    
    # for i in range(len(wl_mod)):
    #     wl_full.append(wl_mod[i])
    # wl_full=np.array(wl_full)
    ## 2.5 save model spectra and grid points
    np.save('code/part_2/outcome_for_part2/pymultinest_outcome/bt-settle_points.npy', np.array(grid_point_list))#要存
    #np.save(main_path + 'processed/CEQ/ATMOP20_CEQ_spec.npy', np.vstack((wl_c2b, fl_spec_array)) )
    #np.save(main_path + 'processed/CEQ/ATMOP20_CEQ_phot.npy', np.vstack((wl_phot, fl_phot_array)) )
    np.save('code/part_2/outcome_for_part2/pymultinest_outcome/bt-settle_full.npy', np.vstack((wl_full, fl_full_array)) )