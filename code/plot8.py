
#实现多种彩色来表示每一段的spectrum
'''
逐曲线计算信噪比 S/N = spectrum / √var。
整段信噪比全部 < 150 → 直接丢弃该段。
对剩余段，信噪比 < 100 的像素标记为无效（NaN）。

将每一个segment的光谱除以该段平均值，得到平均值≈1 的新光谱。

对于有效的部分，每个segment会有一部分重合，
先判断是否真有重叠，没有就直接拼起来，有的话双向插值加权
对于重合的部分这样处理：对于后一段光谱的采样点对应波长，
先利用前一段光谱相邻的两个采样点进行插值，然后根据这个采样点的原始数据和插值数据，
以信噪比为权重计算一个加权平均值，作为这个波长的真实数值。
不重合的部分，直接采用这个点的数据

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

    # 中图 #自己计算的信噪比
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

def make_overlap_mask(wavelength):
    """
    输入：wavelength 列表，每个元素是一维波长数组
    返回：mask_list   列表，形状与 wavelength 完全一致
          值：1 落在下一段区间
              2 落在上一段区间
              0 无重叠
    """
    mask_list = []
    n_seg = len(wavelength)

    for i, w in enumerate(wavelength):
        w = np.asarray(w)
        mask = np.zeros_like(w, dtype=int)

        # 上一段区间
        if i > 0:
            w_prev = np.asarray(wavelength[i-1])
            mask[np.logical_and(w >= w_prev.min(), w <= w_prev.max())] = 2

        # 下一段区间
        if i < n_seg - 1:
            w_next = np.asarray(wavelength[i+1])
            mask[np.logical_and(w >= w_next.min(), w <= w_next.max())] = 1

        mask_list.append(mask)
    return mask_list


def plot_mask(mask_list):
    """把 mask_list 画成热力图：每段一行"""
    max_len = max(m.size for m in mask_list)
    img = np.full((len(mask_list), max_len), np.nan)

    for i, m in enumerate(mask_list):
        img[i, :m.size] = m

    plt.figure(figsize=(10, 2 * len(mask_list)))
    plt.imshow(img, cmap='tab10', vmin=0, vmax=2, aspect='auto')
    cbar = plt.colorbar(ticks=[0, 1, 2])
    cbar.set_ticklabels(['None', 'Next', 'Prev'])
    plt.xlabel('Pixel index')
    plt.ylabel('Segment index')
    plt.title('Overlap Mask')
    plt.show()



def apply_interp_by_mask(wavelength, spectrum, mask_list,var):
    """
    手动左右两点线性插值版
    wavelength / spectrum / mask_list : 三段一一对应
    返回：插值后的光谱，形状不变
    """
    spec_new = []
    n = len(wavelength)

    for i, (w, f, mask) in enumerate(zip(wavelength, spectrum, mask_list)):
        w = np.asarray(w, dtype=float)
        f = np.asarray(f, dtype=float)
        new_f = f.copy()
        new_f=spectrum[i]  # 直接用原始光谱作为新光谱

        # ---------- 标记 2 → 用上一段 ----------
        if i > 0:
            w_prev = np.asarray(wavelength[i-1], dtype=float)
            f_prev = np.asarray(spectrum[i-1],   dtype=float)

            idx2 = (mask == 2)
            for k in np.where(idx2)[0]:
                x = w[k]
                # 找左右两点
                left  = np.searchsorted(w_prev, x, side='left') - 1
                right = left + 1
                if 0 <= left < len(w_prev) - 1:
                    x0, x1 = w_prev[left], w_prev[right]
                    y0, y1 = f_prev[left], f_prev[right]
                    new_f[k] = y0 + (x - x0) * (y1 - y0) / (x1 - x0)


                    ori= f[k]  # 原始值
                    ori_var = var[i][k]**0.5  # 原始方差
                    ori_var_left = var[i-1][left]**0.5  # 左侧方差
                    ori_var_right = var[i-1][right]**0.5  #
                    ori_pre=(ori_var_left + ori_var_right) / 2  # 左右方差平均
                    # 计算加权平均
                    temp= ori_var / (ori_var + ori_pre)
                    new_f[k] = temp * ori + (1 - temp) * new_f[k]
                

        # ---------- 标记 1 → 用下一段 ----------
        if i < n - 1:
            w_next = np.asarray(wavelength[i+1], dtype=float)
            f_next = np.asarray(spectrum[i+1],   dtype=float)

            idx1 = (mask == 1)
            for k in np.where(idx1)[0]:
                x = w[k]
                left  = np.searchsorted(w_next, x, side='left') - 1
                right = left + 1
                if 0 <= left < len(w_next) - 1:
                    x0, x1 = w_next[left], w_next[right]
                    y0, y1 = f_next[left], f_next[right]
                    new_f[k] = y0 + (x - x0) * (y1 - y0) / (x1 - x0)

                    ori= f[k]  # 原始值
                    ori_var = var[i][k]**0.5  # 原始方差
                    ori_var_left = var[i+1][left]**0.5  # 左侧方差
                    ori_var_right = var[i+1][right]**0.5  #
                    ori_pre=(ori_var_left + ori_var_right) / 2  # 左右方差平均
                    # 计算加权平均
                    temp= ori_var / (ori_var + ori_pre)
                    new_f[k] = temp * ori + (1 - temp) * new_f[k]
                

        spec_new.append(new_f)
    return spec_new


def flatten_spectrum(wavelength, spectrum):
    """
    把 list[np.ndarray] 形式的波长和光谱直接拼接成一维，
    保持波长-光谱的一一对应关系。
    
    Parameters
    ----------
    wavelength : list[np.ndarray]
    spectrum   : list[np.ndarray]
    
    Returns
    -------
    wave_1d : np.ndarray
    flux_1d : np.ndarray
    """
    wave_1d = np.concatenate([np.asarray(w) for w in wavelength])
    flux_1d = np.concatenate([np.asarray(f) for f in spectrum])
    return wave_1d, flux_1d


def plot_1d_spectrum(wave_1d, flux_1d):
    plt.figure(figsize=(12, 4))
    plt.plot(wave_1d, flux_1d, lw=1, color='k')
    plt.xlabel('Wavelength (μm)')
    plt.ylabel('Flux (normalized)')
    plt.title('Merged 1-D Spectrum')
    plt.tight_layout()
    plt.show()

if __name__=='__main__':
    
    path='datas/20240203_0071/SDCH_20240203_0071.spec_a0v.fits'
    path='datas/20240203_0071/SDCK_20240203_0071.spec_a0v.fits'
    # path_signal='datas/20240203_0071/SDCH_20240203_0071.sn.fits'
    # path_signal='datas/20240203_0071/SDCK_20240203_0071.sn.fits'

   # signal = get_signal(path_signal=path_signal)

    wavelength,spectrum=get_data(path=path)
    var=get_var(path=path)
    #print(var[15])

    #print(wavelength.shape)
    #plot_with_color(wavelength=wavelength,spectrum=spectrum)
    

    wavelength, spectrum, var = discard_bad_segments(
        wavelength=wavelength, spectrum=spectrum, var=var,
        sn_min_global=150, sn_min_pixel=100)
    

    spectrum = norm_each_segment(spectrum)

    

    plot_with_color_and_SToN(wavelength=wavelength,spectrum=spectrum,var=var)
    # wave_1d, flux_1d 是前面 merge_segments_to_1d 返回的一维 numpy 数组

    # 假设 wavelength 是已过滤后的 list[np.ndarray]
    mask = make_overlap_mask(wavelength)
    spectrum=apply_interp_by_mask(wavelength, spectrum, mask,var)
    #plot_mask(mask)
    plot_with_color_and_SToN(wavelength=wavelength,spectrum=spectrum,var=var)


    wave_1d, flux_1d = flatten_spectrum(wavelength, spectrum)

    plot_1d_spectrum(wave_1d, flux_1d)