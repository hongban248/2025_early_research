
#实现多种彩色来表示每一段的spectrum
'''
逐曲线计算信噪比 S/N = spectrum / √var。
整段信噪比全部 < 150 → 直接丢弃该段。
对剩余段，信噪比 < 100 的像素标记为无效（NaN）。



'''
from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from cycler import cycler
import math
from scipy.interpolate import interp1d
from scipy.interpolate import interp1d


def get_data(path):
    with fits.open(path) as hdul:
        wavelength = hdul[3].data  # WAVELENGTH扩展
        spectrum = hdul[1].data  # SPEC_DIVIDE_A0V扩

    return wavelength,spectrum

def get_var(path):
    with fits.open(path)as hdul:
        data=hdul[2].data
    return data

def get_signal(path_signal):
    with fits.open(path_signal) as hdul:
        signal = hdul[0].data  # SN扩展
        # print(signal.shape)
        # print(signal[0])
    return signal

def plot_with_color(wavelength,spectrum):
    colors = ['red', 'green', 'blue', 'purple', 'orange'] 
    plt.rc('axes', prop_cycle=(cycler('color', colors)))
    plt.figure(figsize=(15, 10))
    for i in range(len(wavelength)):
        plt.plot(wavelength[i], spectrum[i])
    
    # 添加图例
    plt.legend()

    colors = ['black'] 
    plt.rc('axes', prop_cycle=(cycler('color', colors)))

    # 添加标题和坐标轴标签
    plt.xlabel('Wavelength (um)')
    plt.ylabel('Flux')
    plt.title('Spectrum')

    # 显示图形
    plt.show()


def plot_with_color_and_SToN(wavelength, spectrum, var):
    colors = ['red', 'green', 'blue', 'purple', 'orange']
    plt.rc('axes', prop_cycle=cycler('color', colors))

    plt.figure(figsize=(20, 10))

    # 上图
    plt.subplot(2, 1, 1)
    for wl, sp in zip(wavelength, spectrum):
        plt.plot(wl, sp)
    plt.ylabel('Flux')
    plt.title('Spectrum')
    plt.legend()

    # 下图 #自己计算的信噪比
    plt.subplot(2, 1, 2, sharex=plt.gca())  # 共享 x 轴
    #print(var.mean(), spectrum.mean())
    #SToN1 = spectrum / var**0.5  # 计算信噪比
    SToN_segments = []
    for sp, va in zip(spectrum, var):
        sp = np.asarray(sp, float)
        va = np.asarray(va, float)

        # 把 <=0 或 NaN 的误差置 NaN
        den = np.sqrt(np.where(va > 0, va, np.nan))
        stn = np.divide(sp, den,
                    out=np.full_like(sp, np.nan, dtype=float),
                    where=~np.isnan(den))
        SToN_segments.append(stn)
    for wl, v in zip(wavelength, SToN_segments):
        plt.plot(wl, v, linestyle='--')
    plt.xlabel('Wavelength (μm)')
    plt.ylabel('Signal-to-Noise Ratio (S/N)1')
    

    plt.tight_layout()
    plt.show()
    

def extract_best_1d(wavelength, spectrum, var,
                    sn_min_global=100,
                    sn_min_pixel=50,
                    csv_path='best_spectrum.csv'):
    """
    将多段 1-D 光谱按信噪比规则整合为一条 1-D 光谱。

    参数
    ----
    wavelength : list/array-like，每条曲线 1-D
    spectrum   : 同上
    var        : 同上，与 spectrum 一一对应
    sn_min_global : 整段最大 S/N 低于此值 → 整段丢弃
    sn_min_pixel  : 单像素 S/N 低于此值 → 该像素 NaN
    csv_path      : 输出 csv 路径

    返回
    ----
    wave_out, flux_out : 1-D ndarray
    同时写入 csv_path
    """

    # 1. 统一转 ndarray，方便后续
    wl_list   = [np.asarray(w,  float) for w  in wavelength]
    flux_list = [np.asarray(sp, float) for sp in spectrum]
    var_list  = [np.asarray(v,  float) for v  in var]

    valid_wl, valid_flux, valid_sn = [], [], []

    # 2. 逐段过滤
    for wl, fl, va in zip(wl_list, flux_list, var_list):
        sn = fl / np.sqrt(va)

        # 段级过滤
        if np.mean(sn) < sn_min_global:
            continue

        # 像素级过滤
        mask = sn >= sn_min_pixel
        valid_wl.append(wl[mask])
        valid_flux.append(fl[mask])
        valid_sn.append(sn[mask])
    
    print('有效段数:', len(valid_wl))

    if not valid_wl:
        raise ValueError('所有段都被丢弃，无可用数据！')

    # 3. 输出波长网格 = 所有有效波长的并集（去重并排序）
    wave_out = np.unique(np.concatenate(valid_wl))

    # 4. 加权平均：累加分子与分母
    numer = np.zeros_like(wave_out, dtype=float)
    denom = np.zeros_like(wave_out, dtype=float)

    for wl_i, fl_i, sn_i in zip(valid_wl, valid_flux, valid_sn):
        # 线性插值到公共网格
        fl_interp = np.interp(wave_out, wl_i, fl_i, left=np.nan, right=np.nan)
        sn_interp = np.interp(wave_out, wl_i, sn_i, left=0.0,  right=0.0)

        # 累加
        numer += fl_interp * sn_interp
        denom += sn_interp

    # 5. 计算加权平均
    with np.errstate(divide='ignore', invalid='ignore'):
        flux_out = np.where(denom > 0, numer / denom, np.nan)

    # 6. 去掉 NaN
    mask = ~np.isnan(flux_out)
    wave_out, flux_out = wave_out[mask], flux_out[mask]

    # 7. 保存 CSV
    print('保留点数:', wave_out.size)
    print('wave_out:', wave_out)
    pd.DataFrame({'wavelength(um)': wave_out,
                  'flux':           flux_out}).to_csv(csv_path, index=False)

    return wave_out, flux_out

import numpy as np

def discard_bad_segments(wavelength, spectrum, var,
                         sn_min_global=100,
                         sn_min_pixel=50):
    """
    只做“丢弃”这一步：
    返回三个 list，分别对应保留下来的
    wavelength, spectrum, var（已把低 S/N 像素置 NaN）
    """

    wl_clean, sp_clean, var_clean = [], [], []

    for wl, sp, va in zip(wavelength, spectrum, var):
        wl, sp, va = map(np.asarray, (wl, sp, va))

        sn = sp / np.sqrt(va)

        # 1. 整段最大 S/N 判断
        if np.nanmax(sn) < sn_min_global:
            print('丢弃整段光谱:', wl)
            continue                   # 整段丢弃

        # 2. 像素级过滤
        sp = np.where(sn >= sn_min_pixel, sp, np.nan)
        va = np.where(sn >= sn_min_pixel, va, np.nan)

        wl_clean.append(wl)
        sp_clean.append(sp)
        var_clean.append(va)

    return wl_clean, sp_clean, var_clean

def norm_each_segment(spectrum):
    """
    将 spectrum (list of 1-D array-like) 的每一段除以该段平均值，得到平均值≈1 的新光谱。
    空值 (NaN) 不参与平均计算并保留。
    返回同样结构的 list[np.ndarray]。
    """
    spectrum_norm = []
    for sp in spectrum:
        sp = np.asarray(sp, dtype=float)
        # 只用非 NaN 像素求平均
        mean_val = np.nanmean(sp)
        if mean_val == 0 or np.isnan(mean_val):
            # 整段都是 0/NaN 时保持原样，避免除零
            spectrum_norm.append(sp)
        else:
            spectrum_norm.append(sp / mean_val)
    return spectrum_norm



def merge_segments_to_1d(wavelength, spectrum, var,
                         interp_kind='linear',
                         sn_power=1.0):
    """
    把多段光谱按“后段在前段上插值 + 信噪比加权”合并为一维。
    返回 wave_1d, flux_1d
    """
    # 第一段直接作为初始结果
    w_all = wavelength[0].astype(float)
    f_all = spectrum[0].astype(float)
    sn_all = f_all / np.sqrt(np.maximum(var[0], 1e-12))

    for w_cur, f_cur, v_cur in zip(wavelength[1:], spectrum[1:], var[1:]):
        w_cur = w_cur.astype(float)
        f_cur = f_cur.astype(float)
        v_cur = v_cur.astype(float)

        sn_cur = f_cur / np.sqrt(np.maximum(v_cur, 1e-12))

        # 在前一段上插值
        f_prev = interp1d(w_all, f_all, kind=interp_kind,
                          bounds_error=False, fill_value=np.nan)(w_cur)
        s_prev = interp1d(w_all, sn_all, kind=interp_kind,
                          bounds_error=False, fill_value=0.0)(w_cur)

        # 权重
        w_prev = s_prev ** sn_power
        w_curr = sn_cur ** sn_power
        w_sum  = w_prev + w_curr
        mask   = w_sum > 0

        f_weight = np.full_like(f_cur, np.nan)
        f_weight[mask] = (f_prev * w_prev + f_cur * w_curr)[mask] / w_sum[mask]

        # 合并
        w_all = np.concatenate([w_all, w_cur])
        f_all = np.concatenate([f_all, f_weight])
        sn_all = np.concatenate([sn_all, sn_cur])

        # 排序
        idx = np.argsort(w_all)
        w_all, f_all, sn_all = w_all[idx], f_all[idx], sn_all[idx]

    return w_all, f_all

if __name__=='__main__':
    
    path='datas/20240203_0071/SDCH_20240203_0071.spec_a0v.fits'
    path='datas/20240203_0071/SDCK_20240203_0071.spec_a0v.fits'
    path_signal='datas/20240203_0071/SDCH_20240203_0071.sn.fits'
    signal = get_signal(path_signal=path_signal)

    wavelength,spectrum=get_data(path=path)
    var=get_var(path=path)
    #print(var[15])

    #print(wavelength.shape)
    #plot_with_color(wavelength=wavelength,spectrum=spectrum)
    

    wavelength, spectrum, var = discard_bad_segments(
        wavelength=wavelength, spectrum=spectrum, var=var,
        sn_min_global=150, sn_min_pixel=50)
    #spectrum = norm_each_segment(spectrum)

    wavelength_oned,spectrum_oned = merge_segments_to_1d(
        wavelength=wavelength, spectrum=spectrum, var=var,
        interp_kind='linear', sn_power=1.0)


    plot_with_color_and_SToN(wavelength=wavelength,spectrum=spectrum,var=var)