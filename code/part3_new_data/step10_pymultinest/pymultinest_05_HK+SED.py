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
import astropy.units as u
from synphot import SourceSpectrum, SpectralElement, Observation
from synphot.models import Empirical1D
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

def get_txt(file_path):
    try:
        wavelength, flux, error = np.loadtxt(file_path,
                                     comments='#',      # 跳过所有 # 开头的行
                                     unpack=True)       # 直接拆成三列数组
        return wavelength[find_insert_position(wavelength,0):find_insert_position(wavelength,2.5)],flux[find_insert_position(wavelength,0):find_insert_position(wavelength,2.5)],error[find_insert_position(wavelength,0):find_insert_position(wavelength,2.5)]
    except:
        wavelength, flux = np.loadtxt(file_path,
                                     comments='#',      # 跳过所有 # 开头的行
                           unpack=True)       # 直接拆成2列数组
        wavelength=wavelength/1e4
        e=flux
        return wavelength[find_insert_position(wavelength,0):find_insert_position(wavelength,2.5)],flux[find_insert_position(wavelength,0):find_insert_position(wavelength,2.5)],e[find_insert_position(wavelength,0):find_insert_position(wavelength,2.5)]
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
fl_mod_spec_combo_SED = np.load('code/part3_new_data/step10_pymultinest/bt-settle_full_SED.npy', allow_pickle=True)[1:]
wl_mod_ori_SED=np.load('code/part3_new_data/step10_pymultinest/bt-settle_full_SED.npy', allow_pickle=True)[0]

wl_mod_ori_SED_true=np.load('code/part3_new_data/step10_pymultinest/bt-settle_full_SED_true.npy', allow_pickle=True)[0]
fl_mod_ori_SED_true=np.load('code/part3_new_data/step10_pymultinest/bt-settle_full_SED_true.npy', allow_pickle=True)[1:]    


#fl_mod_spec_combo=fl_mod_spec_combo.T
#更新过后跑3中模拟，H，K，H+K  #把数据载入单独放一块
# H_path='code/part3_new_data/step10_pymultinest/H_BC.txt'
# wavelength_H,flux_H,error_H=get_txt(H_path)
H_path='code/part3_new_data/step10_pymultinest/H_BC.txt'
wavelength_H,flux_H,error_H=get_txt(H_path)

K_path='code/part3_new_data/step10_pymultinest/K_BC.txt'
wavelength_K,flux_K,error_K=get_txt(K_path)

SED_path='code/part3_new_data/datas/coconuts-2A-gaia-xp_vegamag.txt'
wavelength_SED,flux_SED,error_SED=get_txt(SED_path)

SED_path='datas/SED.txt'
wavelength_SED_true,flux_SED_true,error_SED_true=get_txt_SED(SED_path)

#print(wavelength_SED_true,wavelength_SED_true.shape)
#aaa
## 5.1 parameteras
parameters = ['Teff', 'logg','meta','vr','vsini','radius','log10b_spec']  #log10b_spec是模型不确定性的对数，单位是flux
num_grid_params = 3  #不包含vr和vsini


teff_min = 3000
teff_max = 4000
logg_min = 3    #3到5.5，guidpoint也要加3-5.5
logg_max = 5.5
meta_min = -1
meta_max = 0.5
# alpha_min = 0.2 #改
# alpha_max = 0.2
vr_min = -30  #-30----+30
vr_max = 30
vsini_min =0 # 0-30
vsini_max = 30
radius_min = 0.2  #注意这里是Rsun，不是Rjup
radius_max = 0.6# 使用了mamajek table来估计半径范围

log10b_spec_min=2*np.log10(0.1*np.min(error_K))  #模型不应该小于这个值
log10b_spec_max=2*np.log10(10*np.max(error_K))  #模型不应该大于这个值    


#print(log10b_spec_max,log10b_spec_min)
#aaaaaaaaa
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





### 6. log-likelihood
def loglike_K(cube, ndim, nparams):

    

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
    # => incorporate vr and vsini
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
        
    print('teff, logg, meta, vr, vsini, radius, log10b_spec,log_l:', teff, logg, meta, vr, vsini, radius, log10b_spec,spec_logl)

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
        
    print('teff, logg, meta, vr, vsini, radius, log10b_spec,log_l:', teff, logg, meta, vr, vsini, radius, log10b_spec,spec_logl)

    return spec_logl


def loglike_gaia(cube, ndim, nparams):

    

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
                                 values = np.log10(fl_mod_spec_combo_SED),
                                 xi = np.array([ np.log10(teff), logg, meta ]),
                                 method = 'linear',
                                 fill_value = np.nan).reshape(-1)
    

    

    # 6.2.2 scaling by radius
    #print(fl_mod_spec)
    fl_mod_spec = fl_mod_spec * (radius * r_sun / (10.888 *u.pc ).to(u.cm))**2  #距离10.888秒差距转换成厘米，然后去除单位
    # => incorporate vr and vsiniH=
    #确保所有量都是纯 numpy 数组，使用 .value 剥离单位
    fl_mod_spec = fl_mod_spec.value if hasattr(fl_mod_spec, 'value') else fl_mod_spec
    flux_K_data = flux_SED.value if hasattr(flux_SED, 'value') else flux_SED

    # print(wl_mod_ori_SED.shape,fl_mod_spec.shape)
    # aaaa
    wl_mod=vr_change(wl_mod_ori_SED,fl_mod_spec,vr)  #视向速度修正
    fl_mod_spec=rot_int_cmj(wl_mod,fl_mod_spec,vsini)  #旋转变宽


    #额外插值，再把模型wave转到数据wave上   先只fits H band
    fl_mod_spec=interpret_model_to_data(wl_mod,fl_mod_spec,wavelength_SED)
    #########################################################################
    

    #print(len(fl_mod_spec),len(flux_K))
    # 6.2.3 likelihood 把模型和数据对比 flf2，err其实就是数据
    spec_sigma_squared = error_SED**2 + 10**log10b_spec
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

def loglike_SED(cube, ndim, nparams):
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
    # 6.2.1 interpolation  #随便给参数得到模型
    fl_mod_spec = 10 ** griddata(points = new_grid_points,
                                 values = np.log10(fl_mod_ori_SED_true),
                                 xi = np.array([ np.log10(teff), logg, meta ]),
                                 method = 'linear',
                                 fill_value = np.nan).reshape(-1)
    # 6.2.2 scaling by radius
    #print(fl_mod_spec)
    fl_mod_spec = fl_mod_spec * (radius * r_sun / (10.888 *u.pc ).to(u.cm))**2  #距离10.888秒差距转换成厘米，然后去除单位
    # => incorporate vr and vsiniH=
    #确保所有量都是纯 numpy 数组，使用 .value 剥离单位
    fl_mod_spec = fl_mod_spec.value if hasattr(fl_mod_spec, 'value') else fl_mod_spec
    #flux_SED_true = flux_SED_true.value if hasattr(flux_SED_true, 'value') else flux_SED_true

    # print(wl_mod_ori_SED.shape,fl_mod_spec.shape)
    # aaaa
    wl_mod=vr_change(wl_mod_ori_SED_true,fl_mod_spec,vr)  #视向速度修正
    fl_mod_spec=rot_int_cmj(wl_mod,fl_mod_spec,vsini)  #旋转变宽

    #额外插值，再把模型wave转到数据wave上   
    #fl_mod_spec=interpret_model_to_data(wl_mod,fl_mod_spec,wavelength_SED_true)
    #print('DDDDDDDDDDDDDDDDDDDDDDDModel fluxes in SED:', wl_mod[0],wl_mod[-1],len(fl_mod_spec),np.mean(fl_mod_spec),np.min(fl_mod_spec),np.max(fl_mod_spec))

    #########################################################################
    filter_response_paths=['datas/filters/Misc_UCAC.B.dat','datas/filters/Misc_UCAC.sdss_g.dat','datas/filters/Misc_UCAC.V.dat',
                            'datas/filters/Misc_UCAC.sdss_r.dat','datas/filters/Misc_UCAC.sdss_i.dat','datas/filters/2MASS_2MASS.J.dat',
                            'datas/filters/2MASS_2MASS.H.dat','datas/filters/2MASS_2MASS.Ks.dat','datas/filters/WISE_WISE.W1.dat',
                            'datas/filters/WISE_WISE.W2.dat']
    
    fl_mods=[get_vegamag(wl_mod, fl_mod_spec, path) for path in filter_response_paths]
    
    
    #把星等转换为流量flux
    fl_mods_vega=[i.value for i in fl_mods]
    flux_SED_true_vega=[get_vegamag([wavelength_SED_true[i],wavelength_SED_true[i]*(1+1e-6)],
                                          [flux_SED_true[i],flux_SED_true[i]],filter_response_paths[i]) for i in range(len(wavelength_SED_true))]
    # print('原始星等AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAModel magnitudes in filters:', fl_mods_vega)
    # print('原始星等AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAObserved magnitudes in filters:', flux_SED_true_vega)
    #fl_mods=[10**(-0.4*i) for i in fl_mods]
    constants=[get_constant(fl_mods_vega[i],flux_SED_true_vega[i]) for i in range(len(fl_mods_vega))]
    #print('常数AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA:', constants)

    fl_mods=[flux_SED_true[i]/constants[i] for i in range(len(fl_mods_vega))]

    #fl_mods=[i.value for i in fl_mods]
    # print('BBBBBBBBBBBBBBBBBBBBBBBBBBBBModel magnitudes in filters:', fl_mods,len(fl_mods))
    # print('CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCObserved magnitudes in filters:', flux_SED_true,len(flux_SED_true))
    
#phot_w1_logl = -0.5 * (fl_w1_mod - fl_w1)**2 / flerr_w1**2  - 0.5 * np.sum( np.log(2 * np.pi * flerr_w1**2 ) )
    phot_logl =[-0.5* (fl_mods[i] - flux_SED_true[i])**2 / error_SED_true[i]**2 - 0.5 * np.log(2 * np.pi * error_SED_true[i]**2) for i in range(len(fl_mods))]
    return sum(phot_logl)


    




def loglike(cube, ndim, nparams):
    logl_H = loglike_H(cube, ndim, nparams)
    logl_K = loglike_K(cube, ndim, nparams)
    log_gaia = loglike_gaia(cube, ndim, nparams)
    log_SED=loglike_SED(cube, ndim, nparams)
    return logl_H + logl_K + log_gaia+log_SED

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


    
    output_path='code/part3_new_data/step10_pymultinest/5/'
    n_params = len(parameters)
    json.dump(parameters, open(output_path + '_%s_params.json'%(str(time.time())), 'w'))
    pymultinest.run(loglike, prior, n_params, 
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