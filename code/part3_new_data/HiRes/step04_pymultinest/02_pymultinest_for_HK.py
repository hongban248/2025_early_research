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

def interpret_model_to_data(wl_mod,fl_mod,wl_data):
    #额外插值，再把模型wave转到数据wave上   先只fits H band
    fl_mod_spec_interp=np.interp(wl_data,wl_mod,fl_mod)
    return fl_mod_spec_interp


r_sun=6.957e10  # cm
grid_points = np.load('code/part3_new_data/HiRes/step04_pymultinest/bt-settle_points_HK_true.npy', allow_pickle=True)
fl_mod_spec_combo = np.load('code/part3_new_data/HiRes/step04_pymultinest/bt-settle_full_HK_true.npy', allow_pickle=True)[1:]
wl_mod_ori=np.load('code/part3_new_data/HiRes/step04_pymultinest/bt-settle_full_HK_true.npy', allow_pickle=True)[0]

H_path='code/part3_new_data/step10_pymultinest/H_BC.txt'
wavelength_H,flux_H,error_H=get_txt(H_path)

K_path='code/part3_new_data/step10_pymultinest/K_BC.txt'
wavelength_K,flux_K,error_K=get_txt(K_path)

## 5.1 parameters
parameters = ['Teff', 'logg','meta','vr','vsini','radius','log10b_spec']  #log10b_spec是模型不确定性的对数，单位是flux
num_grid_params = 3 #不包含vr和vsini

teff_min = 3000
teff_max = 4000
logg_min = 3    #3到5.5，guidpoint也要加3-5.5
logg_max = 5.5
meta_min = -1
meta_max = 1
# alpha_min = 0
# alpha_max = 0
vr_min = -30  #-30----+30
vr_max = 30
vsini_min =0 # 0-30
vsini_max = 30
radius_min = 0.2  #注意这里是Rsun，不是Rjup
radius_max = 0.6# 使用了mamajek table来估计半径范围

log10b_spec_min=2*np.log10(0.1*np.min(error_K))  #模型不应该小于这个值
log10b_spec_max=2*np.log10(10*np.max(error_K))  #模型不应该大于这个值  

def prior(cube, ndim, nparams):
    cube[0] = teff_min + (teff_max - teff_min) * cube[0]
    cube[1] = logg_min + (logg_max - logg_min) * cube[1]
    cube[2] = meta_min + (meta_max - meta_min) * cube[2]
    cube[3] = vr_min + (vr_max - vr_min) * cube[3]
    cube[4] = vsini_min + (vsini_max - vsini_min) * cube[4]
    cube[5] = radius_min + (radius_max - radius_min) * cube[5]
    cube[6] = log10b_spec_min + (log10b_spec_max - log10b_spec_min) * cube[6]

def loglike_K(cube, ndim, nparams):

    

    ## 6.1 current parameters
    teff = cube[0]
    logg = cube[1]
    meta = cube[2]
   # alpha = cube[3]
    vr = cube[3]
    vsini = cube[4]
    radius = cube[5]
    log10b_spec = cube[6]
    
    new_grid_points = np.copy(grid_points)
    new_grid_points[:, 0] = np.log10(new_grid_points[:, 0])  # 对 Teff 取对数
    ## 6.2 spectra
    # 6.2.1 interpolation  #随便给参数得到模型
    fl_mod_spec = 10 ** griddata(points = new_grid_points,
                                 values = np.log10(fl_mod_spec_combo),
                                 xi = np.array([ np.log10(teff), logg, meta ]),
                                 method = 'linear',
                                 fill_value = np.nan).reshape(-1)
    

    

    # 6.2.2 scaling by radius
    
    fl_mod_spec = fl_mod_spec * (radius * r_sun / (10.888 *u.pc ).to(u.cm))**2  #距离10.888秒差距转换成厘米，然后去除单位
    
    #确保所有量都是纯 numpy 数组，使用 .value 剥离单位
    fl_mod_spec = fl_mod_spec.value if hasattr(fl_mod_spec, 'value') else fl_mod_spec
    flux_K_data = flux_K.value if hasattr(flux_K, 'value') else flux_K


    wl_mod=vr_change(wl_mod_ori,fl_mod_spec,vr)  #视向速度修正
    fl_mod_spec=rot_int_cmj(wl_mod,fl_mod_spec,vsini)  #旋转变宽


    #额外插值，再把模型wave转到数据wave上   先只fits H band
    fl_mod_spec=interpret_model_to_data(wl_mod,fl_mod_spec,wavelength_K)
    #########################################################################
    

    #print(len(fl_mod_spec),len(flux_K))
    # 6.2.3 likelihood 把模型和数据对比 flf2，err其实就是数据
    spec_sigma_squared = error_K**2 + 10**log10b_spec
    #spec_sigma_squared= error_H**2
    #spec_logl = - 0.5 * np.sum( (fl_mod_spec - flux_H)**2 / spec_sigma_squared ) - 0.5 * np.sum( np.log(2 * np.pi * spec_sigma_squared) )
    
    spec_sigma_sq = spec_sigma_squared.value if hasattr(spec_sigma_squared, 'value') else spec_sigma_squared
    
    # 现在进行无单位计算
    spec_logl = -0.5 * np.sum((fl_mod_spec - flux_K_data)**2 / spec_sigma_sq) \
                - 0.5 * np.sum(np.log(2 * np.pi * spec_sigma_sq))
    ## 6.4 final likelihood
    #return spec_logl + phot_w1_logl + phot_w2_logl + phot_irac36_logl + phot_irac45_logl

    #print('1111')
    alpha=0  #暂时不考虑alpha
    print('teff, logg, meta,alpha, vr, vsini, radius, log10b_spec,log_l:', teff, logg, meta, alpha, vr, vsini, radius, log10b_spec,spec_logl)

    return spec_logl


def loglike_H(cube, ndim, nparams):

    

    ## 6.1 current parameters
    teff = cube[0]
    logg = cube[1]
    meta = cube[2]
    #alpha = cube[3]
    vr = cube[3]
    vsini = cube[4]
    radius = cube[5]
    log10b_spec = cube[6]
    
    new_grid_points = np.copy(grid_points)
    new_grid_points[:, 0] = np.log10(new_grid_points[:, 0])  # 对 Teff 取对数
    ## 6.2 spectra
    # 6.2.1 interpolation  #随便给参数得到模型
    fl_mod_spec = 10 ** griddata(points = new_grid_points,
                                 values = np.log10(fl_mod_spec_combo),
                                 xi = np.array([ np.log10(teff), logg, meta ]),
                                 method = 'linear',
                                 fill_value = np.nan).reshape(-1)
    

    

    # 6.2.2 scaling by radius
    #print(fl_mod_spec)
    fl_mod_spec = fl_mod_spec * (radius * r_sun / (10.888 *u.pc ).to(u.cm))**2  #距离10.888秒差距转换成厘米，然后去除单位
    # => incorporate vr and vsiniH=
    #确保所有量都是纯 numpy 数组，使用 .value 剥离单位
    fl_mod_spec = fl_mod_spec.value if hasattr(fl_mod_spec, 'value') else fl_mod_spec
    flux_K_data = flux_H.value if hasattr(flux_H, 'value') else flux_H 


    wl_mod=vr_change(wl_mod_ori,fl_mod_spec,vr)  #视向速度修正
    fl_mod_spec=rot_int_cmj(wl_mod,fl_mod_spec,vsini)  #旋转变宽


    #额外插值，再把模型wave转到数据wave上   先只fits H band
    fl_mod_spec=interpret_model_to_data(wl_mod,fl_mod_spec,wavelength_H)
    #########################################################################
    

    #print(len(fl_mod_spec),len(flux_K))
    # 6.2.3 likelihood 把模型和数据对比 flf2，err其实就是数据
    spec_sigma_squared = error_H**2 + 10**log10b_spec
    #spec_sigma_squared= error_H**2
    #spec_logl = - 0.5 * np.sum( (fl_mod_spec - flux_H)**2 / spec_sigma_squared ) - 0.5 * np.sum( np.log(2 * np.pi * spec_sigma_squared) )
    
    spec_sigma_sq = spec_sigma_squared.value if hasattr(spec_sigma_squared, 'value') else spec_sigma_squared
    
    # 现在进行无单位计算
    spec_logl = -0.5 * np.sum((fl_mod_spec - flux_K_data)**2 / spec_sigma_sq) \
                - 0.5 * np.sum(np.log(2 * np.pi * spec_sigma_sq))
    ## 6.4 final likelihood
    #return spec_logl + phot_w1_logl + phot_w2_logl + phot_irac36_logl + phot_irac45_logl

    #print('1111')
    alpha=0  #暂时不考虑alpha

    print('teff, logg, meta, alpha, vr, vsini, radius, log10b_spec,log_l:', teff, logg, meta, alpha, vr, vsini, radius, log10b_spec,spec_logl)

    return spec_logl

def loglike(cube, ndim, nparams):
    logl_H = loglike_H(cube, ndim, nparams)
    logl_K = loglike_K(cube, ndim, nparams)
    return logl_H + logl_K


import time
import re
import shutil

### 7. run forward modeling
if __name__ == "__main__":
    ## 7.1 preparation for pymultinest
    output_path='code/part3_new_data/HiRes/step04_pymultinest/2/'
    n_params = len(parameters)
    json.dump(parameters, open(output_path + '_%s_params.json'%(str(time.time())), 'w'))
    pymultinest.run(loglike, prior, n_params, 
                    outputfiles_basename=output_path+'bt-settle-test-',
                    resume = True, verbose = True,#换数据重跑要删output文件夹
                    n_live_points = 400, #越多越好 400测试，一般2000-4000
                    sampling_efficiency = 0.8,
                    const_efficiency_mode=False)
    ## 7.3 post-run analysis
    analyzer = pymultinest.Analyzer(n_params = n_params, outputfiles_basename = output_path+'HiRes-test-')

    s = analyzer.get_stats()
    json.dump(s, open(output_path + 'stats.json', 'w'), indent=4)
    print('  marginal likelihood:')
    print('    ln Z = %.1f +- %.1f' % (s['global evidence'], s['global evidence error']))
    print('  parameters:')

    for p, m in zip(parameters, s['marginals']):
        lo, hi = m['1sigma']
        med = m['median']
        sigma = (hi - lo) / 2
        if sigma == 0:
            i = 3
        else:
            i = max(0, int(-np.floor(np.log10(sigma))) + 1)
        fmt = '%%.%df' % i
        fmts = '\t'.join(['    %-15s' + fmt + " +- " + fmt])
        print(fmts % (p, med, sigma))







