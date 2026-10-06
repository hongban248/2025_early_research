'''
针对k波段的结果，提取出最大似然参数保存到txt文件中
Maximum Likelihood Parameters
Dim No.        Parameter
   1    0.354188345331214578E+04
   2    0.548231204118078530E+01
   3    0.491506219831362667E+00
   4    0.224614087110010274E+01
   5    0.846348113833129645E+01
   6    0.363410187030987986E+00
   7   -0.290178110671464822E+02
'''



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
import matplotlib.pyplot as plt
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

def get_txt(file_path):
    try:
        wavelength, flux, error = np.loadtxt(file_path,
                                     comments='#',      # 跳过所有 # 开头的行
                                     unpack=True)       # 直接拆成三列数组
        return wavelength[find_insert_position(wavelength,0.3):find_insert_position(wavelength,2.5)],flux[find_insert_position(wavelength,0.3):find_insert_position(wavelength,2.5)],error[find_insert_position(wavelength,0.3):find_insert_position(wavelength,2.5)]
    except:
        wavelength, flux = np.loadtxt(file_path,
                                     comments='#',      # 跳过所有 # 开头的行
                           unpack=True)       # 直接拆成2列数组
        wavelength=wavelength/1e4
        e=flux
        return wavelength[find_insert_position(wavelength,0.3):find_insert_position(wavelength,2.5)],flux[find_insert_position(wavelength,0.3):find_insert_position(wavelength,2.5)],e[find_insert_position(wavelength,0.3):find_insert_position(wavelength,2.5)]
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

def interpret_model_to_data(wl_mod,fl_mod,wl_data):
    #额外插值，再把模型wave转到数据wave上   先只fits H band
    fl_mod_spec_interp=np.interp(wl_data,wl_mod,fl_mod)
    return fl_mod_spec_interp

r_sun=6.957e10  # cm
grid_points = np.load('code/part3_new_data/step10_pymultinest/bt-settle_points.npy', allow_pickle=True)
fl_mod_spec_combo = np.load('code/part3_new_data/step10_pymultinest/bt-settle_full.npy', allow_pickle=True)[1:]
wl_mod_ori=np.load('code/part3_new_data/step10_pymultinest/bt-settle_full.npy', allow_pickle=True)[0]
fl_mod_spec_combo_gaia = np.load('code/part3_new_data/step10_pymultinest/bt-settle_full_SED.npy', allow_pickle=True)[1:]
wl_mod_ori_gaia=np.load('code/part3_new_data/step10_pymultinest/bt-settle_full_SED.npy', allow_pickle=True)[0]

wl_mod_ori_SED=np.load('code/part3_new_data/step10_pymultinest/bt-settle_full_SED_true.npy', allow_pickle=True)[0]
fl_mod_ori_SED=np.load('code/part3_new_data/step10_pymultinest/bt-settle_full_SED_true.npy', allow_pickle=True)[1:]    



def get_txt_SED(file_path):
    try:
        wavelength, flux, error = np.loadtxt(file_path,
                                     comments='#',      # 跳过所有 # 开头的行
                                     unpack=True)       # 直接拆成三列数组
        return wavelength,flux,error
    except:
        wavelength, flux = np.loadtxt(file_path,
                                     comments='#',      # 跳过所有 # 开头的行
                           unpack=True)       # 直接拆成2列数组
        wavelength=wavelength/1e4
        e=flux
        return wavelength,flux,e

import astropy.units as u
from synphot import SourceSpectrum, SpectralElement, Observation
from synphot.models import Empirical1D
import matplotlib.pyplot as plt
def get_vegamag(wavelength, flux, filter_path):
    wavelength = np.asarray(wavelength)
    flux = np.asarray(flux)
    wave= wavelength * u.um.to(u.AA)
    flam = flux * (u.erg / u.s / u.cm**2 / u.AA)

    # Make a source spectrum
    src = SourceSpectrum(Empirical1D, points=wave, lookup_table=flam)

    # Load a filter throughput you have locally (λ in Å, dimensionless T(λ))
    filt_wave, filt_thru = np.loadtxt(filter_path, unpack=True)  # two columns
    band = SpectralElement(Empirical1D, points=filt_wave * u.AA, lookup_table=filt_thru)

    # Observe (photon-weighted by default)
    observation = Observation(src, band, force='extrapolate')

    

    # 计算观测光谱的 VEGAMAG 星等
    # 加载内置的 Vega 光谱
    vegaspec = SourceSpectrum.from_vega()

    # 计算观测光谱的 VEGAMAG 星等
    vegamag = observation.effstim('vegamag', vegaspec=vegaspec)
    #print("VEGAMAG 星等：", vegamag)

    return vegamag

def get_constant(IRTF_veg_value, coconuts_veg):
    # 强制转换为 float（兼容 astropy Quantity 和普通数值）
    irtf = float(IRTF_veg_value.value if hasattr(IRTF_veg_value, 'value') else IRTF_veg_value)
    coco = float(coconuts_veg.value if hasattr(coconuts_veg, 'value') else coconuts_veg)
    
    constant = 10**((irtf - coco) / 2.5)
    return constant


H_path='code/part3_new_data/step10_pymultinest/H_BC.txt'
wavelength_H,flux_H,error_H=get_txt(H_path)

K_path='code/part3_new_data/step10_pymultinest/K_BC.txt'
wavelength_K,flux_K,error_K=get_txt(K_path)

SED_path1='code/part3_new_data/datas/coconuts-2A-gaia-xp_vegamag.txt'
wavelength_gaia,flux_gaia,error_gaia=get_txt(SED_path1)

SED_path='datas/SED.txt'
wavelength_SED,flux_SED,error_SED=get_txt_SED(SED_path)



## 5.1 parameters
parameters = ['Teff', 'logg','meta','vr','vsini','radius','log10b_spec']  #log10b_spec是模型不确定性的对数，单位是flux
num_grid_params = 3  #不包含vr和vsini


'''
针对k波段的结果，提取出最大似然参数保存到txt文件中
Maximum Likelihood Parameters
Dim No.        Parameter
   1    0.354188345331214578E+04
   2    0.548231204118078530E+01
   3    0.491506219831362667E+00
   4    0.224614087110010274E+01
   5    0.846348113833129645E+01
   6    0.363410187030987986E+00
   7   -0.290178110671464822E+02
'''

teff_min = 0.354188345331214578E+04
teff_max = 0.354188345331214578E+04
logg_min = 0.548231204118078530E+01    #3到5.5，guidpoint也要加3-5.5
logg_max = 0.548231204118078530E+01
meta_min = 0.491506219831362667E+00
meta_max = 0.491506219831362667E+00
# alpha_min = 0.2 #改
# alpha_max = 0.2
vr_min = 0.224614087110010274E+01  #-30----+30
vr_max = 0.224614087110010274E+01
vsini_min =0.846348113833129645E+01 # 0-30
vsini_max = 0.846348113833129645E+01
radius_min = 0.363410187030987986E+00 #注意这里是Rsun，不是Rjup
radius_max = 0.363410187030987986E+00# 使用了mamajek table来估计半径范围

log10b_spec_min=-0.290178110671464822E+02  #模型不应该小于这个值
log10b_spec_max=-0.290178110671464822E+02  #模型不应该大于这个值    



def prior(cube, ndim, nparams):
    cube[0] = teff_min + (teff_max - teff_min) * cube[0]
    cube[1] = logg_min + (logg_max - logg_min) * cube[1]
    cube[2] = meta_min + (meta_max - meta_min) * cube[2]
    #cube[3] = alpha_min + (alpha_max - alpha_min) * cube[3]
    cube[3] = vr_min + (vr_max - vr_min) * cube[3]
    cube[4] = vsini_min + (vsini_max - vsini_min) * cube[4]
    cube[5] = radius_min + (radius_max - radius_min) * cube[5]
    cube[6] = log10b_spec_min + (log10b_spec_max - log10b_spec_min) * cube[6]
#下面两行存疑


#print(fl_mod_spec_combo.shape,np.log10(fl_mod_spec_combo))
#aaaaaa

def picture_model_data(wavelength,flux,fl_mod_spec):
    plt.figure(figsize=(10,6))
    plt.plot(wavelength, flux, label='Observed Spectrum', color='blue')
    plt.plot(wavelength, fl_mod_spec, label='Model Spectrum', color='orange')
    plt.xlabel('Wavelength (microns)')
    plt.ylabel('Flux')
    plt.title('Model vs Observed Spectrum')
    plt.legend()
    plt.grid()
    plt.show()

def picture_model_data_oc(wavelength, flux, fl_mod_spec, error, wave_photo, model_photo_flux, data_photo_flux, error_photo):
    plt.figure(figsize=(10, 6))
    
    # 原有光谱曲线
    plt.plot(wavelength, flux, label='Observed Spectrum', color='blue')
    plt.plot(wavelength, fl_mod_spec, label='Model Spectrum', color='orange')
    
    # 增加测光点和误差棒
    plt.errorbar(wave_photo, data_photo_flux, yerr=error_photo, 
                 fmt='o', color='blue', ecolor='blue', capsize=4, 
                 label='Observed Photometry', zorder=5)
    plt.scatter(wave_photo, model_photo_flux, 
                marker='s', color='orange', s=60, 
                label='Model Photometry', zorder=5)
    
    plt.xlabel('Wavelength (microns)')
    plt.ylabel('Flux')
    plt.title('Model vs Observed Spectrum')
    plt.legend()
    plt.grid()
    plt.show()

def picture_model_data_oc(wavelength, flux, fl_mod_spec, error, wave_photo, model_photo_flux, data_photo_flux, error_photo):
    # 创建上下两幅图，共享x轴，高度比例 2:1
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True, 
                                    gridspec_kw={'height_ratios': [2, 1]})
    
    # ========== 上图：光谱 + 测光 ==========
    ax1.plot(wavelength, flux, label='Observed Spectrum', color='blue')
    ax1.plot(wavelength, fl_mod_spec, label='Model Spectrum', color='orange')
    ax1.errorbar(wave_photo, data_photo_flux, yerr=error_photo, 
                 fmt='o', color='blue', ecolor='blue', capsize=4, 
                 label='Observed Photometry', zorder=5)
    ax1.scatter(wave_photo, model_photo_flux, 
                marker='s', color='orange', s=60, 
                label='Model Photometry', zorder=5)
    ax1.set_ylabel('Flux')
    ax1.set_title('Model vs Observed Spectrum')
    ax1.legend(loc='best')
    ax1.grid(True)
    
    # ========== 下图：残差 (数据 - 模型) / 误差 ==========
    residual = (flux - fl_mod_spec) / error
    ax2.plot(wavelength, residual, color='green', alpha=0.7, label='Residual')
    ax2.axhline(y=0, color='black', linewidth=2)  # y=0 粗黑线
    ax2.set_xlabel('Wavelength (microns)')
    ax2.set_ylabel('(Data - Model) / Error')
    ax2.grid(True)
    
    plt.tight_layout()
    plt.show()



def picture_model_data_oc2(wave_model,flux_model,wave_1,flux_1,error_1,wave_2,flux_2,error_2,wave_3,flux_3,error_3,wave_photo,model_photo_flux,data_photo_flux,error_photo,wave_model_2,flux_model_2):
   # 创建上下两幅图，共享x轴，高度比例 2:1
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True, 
                                    gridspec_kw={'height_ratios': [2, 1]})
    
    # 绘制模型光谱
    ax1.plot(wave_model, flux_model, label='Model Spectrum', color='orange')
    ax1.plot(wave_model_2, flux_model_2, label='Model Spectrum', color='orange')
    # 绘制数据1
    ax1.plot(wave_1, flux_1,  color='blue', label='gaia-xp')
    
    # 绘制数据2
    ax1.errorbar(wave_2, flux_2, color='green',label='IGRANCE H')
    
    # 绘制数据3
    ax1.errorbar(wave_3, flux_3, color='red',  label='IGRANCE K')
    
    # 绘制测光点
    ax1.errorbar(wave_photo, data_photo_flux, yerr=error_photo, fmt='D', color='purple', ecolor='purple', capsize=4, label='Photometry')
    ax1.scatter(wave_photo, model_photo_flux, marker='X', color='black', s=100, label='Model Photometry')
    
    ax1.set_xlabel('Wavelength (microns)')
    ax1.set_ylabel('Flux')
    ax1.set_title('Model vs Observed Data')
    ax1.legend(size=20)
    ax1.grid()

    # ========== 下图：残差 (数据 - 模型) / 误差 ==========
    residual_1 = (flux_1 - np.interp(wave_1, wave_model, flux_model)) / error_1
    residual_2 = (flux_2 - np.interp(wave_2, wave_model, flux_model)) / error_2
    residual_3 = (flux_3 - np.interp(wave_3, wave_model, flux_model)) / error_3
    ax2.plot(wave_1, residual_1, color='blue', alpha=0.7, label='Residual Gaia-XP')
    ax2.plot(wave_2, residual_2, color='green', alpha=0.7, label='Residual IGRANCE H')
    ax2.plot(wave_3, residual_3, color='red', alpha=0.7, label='Residual IGRANCE K')
    ax2.axhline(y=0, color='black', linewidth=2)  # y=0 粗黑线
    ax2.set_xlabel('Wavelength (microns)')
    ax2.set_ylabel('(Data - Model) / Error')
    ax2.legend(size=20)
    ax2.grid(True)
    plt.show()
    
def picture_model_data_oc3(wave_1,flux_model_1,flux_data_1,error_1,wave_2,flux_model_2,flux_data_2,error_2,wave_3,flux_model_3,flux_data_3,error_3,wave_photo,model_photo_flux,data_photo_flux,error_photo):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True, 
                                    gridspec_kw={'height_ratios': [2, 1]})
    
    # 绘制数据1和模型1
    ax1.plot(wave_1, flux_model_1, label='Model Spectrum', color='orange')
    ax1.plot(wave_1, flux_data_1, color='blue',   label='gaia-xp')
    
    # 绘制数据2和模型2
    ax1.plot(wave_2, flux_model_2, label='Model Spectrum', color='orange')
    ax1.errorbar(wave_2, flux_data_2, color='green',   label='IGRANCE H')
    
    # 绘制数据3和模型3
    ax1.plot(wave_3, flux_model_3, label='Model Spectrum', color='orange')
    ax1.errorbar(wave_3, flux_data_3, color='red',  label='IGRANCE K')
    
    # 绘制测光点
    ax1.errorbar(wave_photo, data_photo_flux, yerr=error_photo, fmt='D', color='purple', ecolor='purple', capsize=4, label='Photometry')
    ax1.scatter(wave_photo, model_photo_flux, marker='X', color='black', s=100, label='Model Photometry')
    
    ax1.set_xlabel('Wavelength (microns)')
    ax1.set_ylabel('Flux')
    ax1.set_title('Model vs Observed Data')
    ax1.legend(fontsize=20)
    ax1.grid()

    # ========== 下图：残差 (数据 - 模型) / 误差 ==========
    residual_1 = (flux_data_1 - flux_model_1) / error_1
    residual_2 = (flux_data_2 - flux_model_2) / error_2
    residual_3 = (flux_data_3 - flux_model_3) / error_3
    ax2.plot(wave_1, residual_1, color='blue', alpha=0.7, label='Residual Gaia-XP')
    ax2.plot(wave_2, residual_2, color='green', alpha=0.7, label='Residual IGRANCE H')
    ax2.plot(wave_3, residual_3, color='red', alpha=0.7, label='Residual IGRANCE K')
    ax2.axhline(y=0, color='black', linewidth=2)  # y=0 粗黑线
    ax2.set_xlabel('Wavelength (microns)')
    ax2.set_ylabel('(Data - Model) / Error')
    ax2.legend(fontsize=20)
    ax2.grid(True)
    plt.show()

### 6. log-likelihood
def loglike_K(cube, ndim, nparams):

    

    ## 6.1 current parameters
    teff = 0.348865694188151610E+04
    logg = 0.549997947278569299E+01
    meta=0.181153818043602310E+00
    #alpha = cube[3]
    vr=0.155803747549053995E+01
    vsini = 0.355702023513865573E+01
    radius=0.377199503524839108E+00
    log10b_spec = -0.282560622175626115E+02
    
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
    # => incorporate vr and vsini
    #确保所有量都是纯 numpy 数组，使用 .value 剥离单位
    fl_mod_spec = fl_mod_spec.value if hasattr(fl_mod_spec, 'value') else fl_mod_spec
    flux_K_data = flux_K.value if hasattr(flux_K, 'value') else flux_K


    wl_mod=vr_change(wl_mod_ori,fl_mod_spec,vr)  #视向速度修正
    fl_mod_spec=rot_int_cmj(wl_mod,fl_mod_spec,vsini)  #旋转变宽
#保存model成fits

    #额外插值，再把模型wave转到数据wave上   先只fits H band
    fl_mod_spec=interpret_model_to_data(wl_mod,fl_mod_spec,wavelength_K)
    #########################################################################

    print('teff, logg, meta, vr, vsini, radius, log10b_spec:', teff, logg, meta, vr, vsini, radius, log10b_spec)
    print('fl_mod_spec:', fl_mod_spec.shape)
    print('wl_mod:', wl_mod.shape)
    print('flux_K_data:', flux_K_data.shape)
    print('wavelength_K:', wavelength_K.shape)

    picture_model_data(wavelength_K, flux_K_data, fl_mod_spec)



    
    sys.exit(0) # 正常退出


    aaaaa#下面的代码废弃
    

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
        
    print('teff, logg, meta, vr, vsini, radius, log10b_spec,log_l:', teff, logg, meta, vr, vsini, radius, log10b_spec,spec_logl)

    return spec_logl

def loglike_for_data(cube,ndim,nparams):
    #这个函数是为了单纯计算数据的似然值，给定一个参数组合，看看模型和数据的对比情况
    # 6.1 current parameters
    teff = 0.348865694188151610E+04
    logg = 0.549997947278569299E+01
    meta=0.181153818043602310E+00
    #alpha = cube[3]
    vr=0.155803747549053995E+01
    vsini = 0.355702023513865573E+01
    radius=0.377199503524839108E+00
    log10b_spec = -0.282560622175626115E+02

    new_grid_points = np.copy(grid_points)
    new_grid_points[:, 0] = np.log10(new_grid_points[:, 0])  # 对 Teff 取对数
    ## 6.2 spectra
    # 6.2.1 interpolation  #随便给参数得到模型
    fl_mod_spec_HK = 10 ** griddata(points = new_grid_points,
                                 values = np.log10(fl_mod_spec_combo),
                                 xi = np.array([ np.log10(teff), logg, meta ]),
                                 method = 'linear',
                                 fill_value = np.nan).reshape(-1)
    fl_mod_spec_gaia= 10 ** griddata(points = new_grid_points,
                                 values = np.log10(fl_mod_spec_combo_gaia),
                                 xi = np.array([ np.log10(teff), logg, meta ]),
                                 method = 'linear',
                                 fill_value = np.nan).reshape(-1)
    fl_mod_spec_SED = 10 ** griddata(points = new_grid_points,
                                 values = np.log10(fl_mod_ori_SED),
                                 xi = np.array([ np.log10(teff), logg, meta ]),
                                 method = 'linear',
                                 fill_value = np.nan).reshape(-1)   
    
    fl_mod_spec_HK = fl_mod_spec_HK * (radius * r_sun / (10.888 *u.pc ).to(u.cm))**2  #距离10.888秒差距转换成厘米，然后去除单位
    fl_mod_spec_HK = fl_mod_spec_HK.value if hasattr(fl_mod_spec_HK, 'value') else fl_mod_spec_HK
    wl_mod_HK=vr_change(wl_mod_ori,fl_mod_spec_HK,vr)  #视向速度修正
    fl_mod_spec_HK=rot_int_cmj(wl_mod_HK,fl_mod_spec_HK,vsini)  #旋转变宽

    fl_mod_spec_gaia=fl_mod_spec_gaia * (radius * r_sun / (10.888 *u.pc ).to(u.cm))**2  #距离10.888秒差距转换成厘米，然后去除单位
    fl_mod_spec_gaia = fl_mod_spec_gaia.value if hasattr(fl_mod_spec_gaia, 'value') else fl_mod_spec_gaia
    wl_mod_gaia=vr_change(wl_mod_ori_gaia,fl_mod_spec_gaia,vr)  #视向速度修正
    fl_mod_spec_gaia=rot_int_cmj(wl_mod_gaia,fl_mod_spec_gaia,vsini)  #旋转变宽

    fl_mod_spec_SED=fl_mod_spec_SED * (radius * r_sun / (10.888 *u.pc ).to(u.cm))**2  #距离10.888秒差距转换成厘米，然后去除单位
    fl_mod_spec_SED = fl_mod_spec_SED.value if hasattr(fl_mod_spec_SED, 'value') else fl_mod_spec_SED
    wl_mod_SED=vr_change(wl_mod_ori_SED,fl_mod_spec_SED,vr)  #视向速度修正
    fl_mod_spec_SED=rot_int_cmj(wl_mod_SED,fl_mod_spec_SED,vsini)  #旋转变宽

    fl_mod_spec_H=interpret_model_to_data(wl_mod_HK,fl_mod_spec_HK,wavelength_H)
    fl_mod_spec_K=interpret_model_to_data(wl_mod_HK,fl_mod_spec_HK,wavelength_K)
    fl_mod_spec_gaia=interpret_model_to_data(wl_mod_gaia,fl_mod_spec_gaia,wavelength_gaia)

    fl_mod_all=np.concatenate([fl_mod_spec_gaia,fl_mod_spec_H,fl_mod_spec_K])
    flux_all=np.concatenate([flux_gaia,flux_H,flux_K])
    error_all=np.concatenate([error_H,error_K,error_gaia])
    wavelength_all=np.concatenate([wavelength_gaia,wavelength_H,wavelength_K])

    #picture_model_data(wavelength_all,flux_all,fl_mod_all)
    ###############################################################
    filter_response_paths=['datas/filters/Misc_UCAC.B.dat','datas/filters/Misc_UCAC.sdss_g.dat','datas/filters/Misc_UCAC.V.dat',
                            'datas/filters/Misc_UCAC.sdss_r.dat','datas/filters/Misc_UCAC.sdss_i.dat','datas/filters/2MASS_2MASS.J.dat',
                            'datas/filters/2MASS_2MASS.H.dat','datas/filters/2MASS_2MASS.Ks.dat','datas/filters/WISE_WISE.W1.dat',
                            'datas/filters/WISE_WISE.W2.dat']
    
    fl_mods_photo=[get_vegamag(wl_mod_SED, fl_mod_spec_SED, path) for path in filter_response_paths]
    
    
    #把星等转换为流量flux
    fl_mods_vega=[i.value for i in fl_mods_photo]
    flux_SED_true_vega=[get_vegamag([wavelength_SED[i],wavelength_SED[i]*(1+1e-6)],
                                          [flux_SED[i],flux_SED[i]],filter_response_paths[i]) for i in range(len(wavelength_SED))]
    # print('原始星等AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAModel magnitudes in filters:', fl_mods_vega)
    # print('原始星等AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAObserved magnitudes in filters:', flux_SED_true_vega)
    #fl_mods=[10**(-0.4*i) for i in fl_mods]
    constants=[get_constant(fl_mods_vega[i],flux_SED_true_vega[i]) for i in range(len(fl_mods_vega))]
    #print('常数AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA:', constants)

    fl_mods_photo=[flux_SED[i]/constants[i] for i in range(len(fl_mods_vega))]

    #picture_model_data_oc(wavelength_all,flux_all,fl_mod_all,error_all,wavelength_SED,fl_mods_photo,flux_SED,error_SED)

    #picture_model_data_oc2(wl_mod_HK,fl_mod_spec_HK,wavelength_gaia,flux_gaia,error_gaia,wavelength_H,flux_H,error_H,wavelength_K,flux_K,error_K,wavelength_SED,fl_mods_photo,flux_SED,error_SED,wavelength_gaia,fl_mod_spec_gaia)
    picture_model_data_oc3(wavelength_gaia,fl_mod_spec_gaia,flux_gaia,error_gaia,wavelength_H,fl_mod_spec_H,flux_H,error_H,wavelength_K,fl_mod_spec_K,flux_K,error_K,wavelength_SED,fl_mods_photo,flux_SED,error_SED)
    
    
    



import time
import re
import shutil

def fix_scientific_notation_inplace(filepath):
        """修复文件中缺失 'e' 的科学计数法，例如 -0.123-308 → -0.123e-308"""
        if not os.path.exists(filepath):
            return
        
        # 创建备份
        backup_path = filepath + '.backup'
        shutil.copy2(filepath, backup_path)
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            if line.strip().startswith('#') or not line.strip():
                fixed_lines.append(line)
                continue
            
            fields = line.split()
            fixed_fields = []
            
            for field in fields:
                # 检测损坏的科学计数法：包含两个符号但没有 e/E
                if ('e' not in field.lower() and 
                    len([c for c in field if c in '+-']) >= 2 and
                    re.match(r'^[+-]?[0-9]*\.[0-9]+[+-][0-9]+$', field)):
                    # 修复：在指数前添加 e
                    field = re.sub(r'^([+-]?[0-9]*\.[0-9]+)([+-][0-9]+)$', r'\1e\2', field)
                fixed_fields.append(field)
            
            fixed_lines.append(' '.join(fixed_fields))
        
        with open(filepath, 'w') as f:
            f.write('\n'.join(fixed_lines))



if __name__ == "__main__":


    
    output_path='code/part3_new_data/step10_pymultinest/4/'
    n_params = len(parameters)
    json.dump(parameters, open(output_path + '_%s_params.json'%(str(time.time())), 'w'))
    pymultinest.run(loglike_for_data, prior, n_params, 
                    outputfiles_basename=output_path+'bt-settle-test-',
                    resume = True, verbose = True,#换数据重跑要删output文件夹
                    n_live_points = 400, #越多越好 400测试，一般2000-4000
                    sampling_efficiency = 0.8,
                    const_efficiency_mode=False)
    
    # ====== 修复科学计数法格式错误 ======
    import re
    import glob
    
    def fix_scientific_notation(filepath):
        """修复文件中缺失 'e' 的科学计数法，例如 -0.123-308 → -0.123e-308"""
        if not os.path.exists(filepath):
            return
        
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        fixed_count = 0
        fixed_lines = []
        
        for line in lines:
            original = line
            # 修复格式：数字后直接跟+-指数（缺少e）的情况
            # 匹配模式：浮点数后跟+-号和数字，中间没有e
            # 例如：-0.139051973236273472-308 → -0.139051973236273472e-308
            pattern = r'([0-9])([+-])([0-9]{2,3})([^0-9]|$)'
            
            def replace_func(match):
                num_end = match.group(1)
                sign = match.group(2)
                exp = match.group(3)
                tail = match.group(4)
                # 检查前面是否是数字（避免重复修复）
                start = match.start()
                if start > 0 and line[start-1:start].isdigit():
                    return num_end + 'e' + sign + exp + tail
                return match.group(0)
            
            # 更简单的替换：数字后跟-308或+308这种模式的
            new_line = re.sub(r'(\d)([+-]\d{2,3})\b', r'\1e\2', line)
            
            if new_line != line:
                fixed_count += 1
            fixed_lines.append(new_line)
        
        if fixed_count > 0:
            with open(filepath, 'w') as f:
                f.writelines(fixed_lines)
            print(f"Fixed {fixed_count} lines in {filepath}")
    
    # 修复所有相关文件（关键是 .txt 文件）
    base_path = output_path + 'bt-settle-test-'
    files_to_fix = glob.glob(base_path + '*.txt') + glob.glob(base_path + '*.dat')
    
    for file_path in set(files_to_fix):  # 去重
        fix_scientific_notation(file_path)
    
    # ====== 修复结束 ======
    
    analyzer = pymultinest.Analyzer(n_params = n_params, outputfiles_basename = output_path+'bt-settle-test-')
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