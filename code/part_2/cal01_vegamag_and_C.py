#计算常数c

#9.23增加验证环节

import numpy as np
import astropy.units as u
from synphot import SourceSpectrum, SpectralElement, Observation
from synphot.models import Empirical1D
import matplotlib.pyplot as plt

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


def get_txt(file_path):
    try:
        wavelength, flux, error = np.loadtxt(file_path,
                                     comments='#',      # 跳过所有 # 开头的行
                                     unpack=True)       # 直接拆成三列数组
        return wavelength[find_insert_position(wavelength,1.0):find_insert_position(wavelength,2.5)],flux[find_insert_position(wavelength,1.0):find_insert_position(wavelength,2.5)],error[find_insert_position(wavelength,1.0):find_insert_position(wavelength,2.5)]
    except:
        wavelength, flux = np.loadtxt(file_path,
                                     comments='#',      # 跳过所有 # 开头的行
                           unpack=True)       # 直接拆成2列数组
        wavelength=wavelength/1e4
        e=flux
        return wavelength[find_insert_position(wavelength,1.0):find_insert_position(wavelength,2.5)],flux[find_insert_position(wavelength,1.0):find_insert_position(wavelength,2.5)],e[find_insert_position(wavelength,1.0):find_insert_position(wavelength,2.5)]

def remove_negative(wave, flux, error):
    # 创建一个布尔掩码，标记 flux >= 0 的位置
    mask = flux >= 0
    
    # 使用布尔掩码过滤 wave, flux, error
    wave = wave[mask]
    flux = flux[mask]
    error = error[mask]
    
    return wave, flux, error

def get_vegamag(wavelength, flux, filter_path):
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

def get_vegamag_all(filter_path,txt_path,constant=1.0):
    wavelength, flux, error = get_txt(txt_path)
    wavelength, flux, error = remove_negative(wavelength, flux, error)
    veg=get_vegamag(wavelength, flux*constant, filter_path)
    return veg


def get_constant(IRTF_veg, coconuts_veg):
    # IRTF_veg=float(IRTF_veg)
    # coconuts_veg=float(coconuts_veg)
    #IRTF_veg_value = IRTF_veg.to_value(u.VEGA)
    IRTF_veg_value = IRTF_veg.value
    #coconuts_veg_value = coconuts_veg.to_value(u.VEGA)
    constant=10**((IRTF_veg_value-coconuts_veg)/2.5)
    return constant
  

coconuts_2a_veg_J=7.406 # 2MASS J
coconuts_2a_veg_H=6.86 # 2MASS H
coconuts_2a_veg_K=6.579 # 2MASS K

filter_path_J='datas/20240203_0071/filters/2MASS_2MASS.J.dat'
filter_path_H='datas/20240203_0071/filters/2MASS_2MASS.H.dat'
filter_path_K='datas/20240203_0071/filters/2MASS_2MASS.Ks.dat'

txt_path_M3='models/other_V/AD_Leo_M3V.txt'
#txt_path_M3='code/part_2/data_for_part2/AD_Leo_M3V.txt'
txt_path_M3='code/part_2/data_for_part2/bt_settle_cut/bt-settl_1066.dat_cut.txt'
txt_path_M2_5='models/other_V/Gl_381_M2.5V.txt'

veg_J_M3=get_vegamag_all(filter_path_J,txt_path_M3)
veg_H_M3=get_vegamag_all(filter_path_H,txt_path_M3)
veg_K_M3=get_vegamag_all(filter_path_K,txt_path_M3)

veg_J_M2_5=get_vegamag_all(filter_path_J,txt_path_M2_5)
veg_H_M2_5=get_vegamag_all(filter_path_H,txt_path_M2_5) 
veg_K_M2_5=get_vegamag_all(filter_path_K,txt_path_M2_5)

print("AD_Leo_M3V: J=",veg_J_M3,"H=",veg_H_M3,"K=",veg_K_M3)
print("Gl_381_M2.5V: J=",veg_J_M2_5,"H=",veg_H_M2_5,"K=",veg_K_M2_5)

#print(type(str(veg_K_M2_5)),str(veg_K_M2_5))  #0.6  0.2
#print(type(veg_K_M2_5),veg_K_M2_5)

constant_J_M3=get_constant(veg_J_M3,coconuts_2a_veg_J)
constant_H_M3=get_constant(veg_H_M3,coconuts_2a_veg_H)
constant_K_M3=get_constant(veg_K_M3,coconuts_2a_veg_K)

constant_J_M2_5=get_constant(veg_J_M2_5,coconuts_2a_veg_J)
constant_H_M2_5=get_constant(veg_H_M2_5,coconuts_2a_veg_H)
constant_K_M2_5=get_constant(veg_K_M2_5,coconuts_2a_veg_K)
print("常数c:")
print("AD_Leo_M3V: J=",constant_J_M3,"H=",constant_H_M3,"K=",constant_K_M3)
print("Gl_381_M2.5V: J=",constant_J_M2_5,"H=",constant_H_M2_5,"K=",constant_K_M2_5)



# veg_J_M3=veg_J_M3.value-2.5*np.log10(constant_J_M3)
# veg_H_M3=veg_H_M3.value-2.5*np.log10(constant_H_M3)
# veg_K_M3=veg_K_M3.value-2.5*np.log10(constant_K_M3)

# veg_J_M2_5=veg_J_M2_5.value-2.5*np.log10(constant_J_M2_5)
# veg_H_M2_5=veg_H_M2_5.value-2.5*np.log10(constant_H_M2_5)
# veg_K_M2_5=veg_K_M2_5.value-2.5*np.log10(constant_K_M2_5)

veg_J_M3=get_vegamag_all(filter_path_J,txt_path_M3,constant_J_M3)
veg_H_M3=get_vegamag_all(filter_path_H,txt_path_M3,constant_H_M3)
veg_K_M3=get_vegamag_all(filter_path_K,txt_path_M3,constant_K_M3)

veg_J_M2_5=get_vegamag_all(filter_path_J,txt_path_M2_5,constant_J_M2_5)
veg_H_M2_5=get_vegamag_all(filter_path_H,txt_path_M2_5,constant_H_M2_5)
veg_K_M2_5=get_vegamag_all(filter_path_K,txt_path_M2_5,constant_K_M2_5)

print("修正后星等:")
print("AD_Leo_M3V: J=",veg_J_M3,"H=",veg_H_M3,"K=",veg_K_M3)
print("Gl_381_M2.5V: J=",veg_J_M2_5,"H=",veg_H_M2_5,"K=",veg_K_M2_5)