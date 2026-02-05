#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#计算光谱的vegamag星等

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

def get_vegamag_all(filter_path,txt_path):
    wavelength, flux, error = get_txt(txt_path)
    wavelength, flux, error = remove_negative(wavelength, flux, error)
    veg=get_vegamag(wavelength, flux, filter_path)
    return veg
    
    

if __name__ == "__main__":
    #file_path = "datas/20240203_0071/SDCH_20240203_0071.spec_a0v.fits"
    txt_path = "models/other_V/AD_Leo_M3V.txt"
    wavelength, flux, error = get_txt(txt_path)
    #wavelength=wavelength*2
    wavelength, flux, error = remove_negative(wavelength, flux, error)

    

    

    veg=get_vegamag(wavelength, flux, 'datas/20240203_0071/filters/2MASS_2MASS.H.dat')
    #veg2=get_vegamag(wavelength, flux*2, 'datas/20240203_0071/filters/2MASS_2MASS.H.dat')
    print(veg)
    #print(type(veg))

    







