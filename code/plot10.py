
#实现多种彩色来表示每一段的spectrum
#同时画出了光谱和误差
#分别去除了前3个和后3个区域的数据
#进行一维插值，画一维图像并保存为CSV文件


from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from cycler import cycler
import math
from scipy.interpolate import interp1d, CubicSpline

def get_data(path):
    with fits.open(path) as hdul:
        wavelength = hdul[3].data  # WAVELENGTH扩展
        spectrum = hdul[1].data  # SPEC_DIVIDE_A0V扩

    return wavelength[3:26,:],spectrum[3:26,:]

def get_var(path):
    with fits.open(path)as hdul:
        data=hdul[2].data
    return data[3:26,:]

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


def plot_with_color_and_variance(wavelength, spectrum, var):
    colors = ['red', 'green', 'blue', 'purple', 'orange']
    plt.rc('axes', prop_cycle=cycler('color', colors))

    plt.figure(figsize=(20, 15))

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
    for wl, v in zip(wavelength, var**0.5):
        plt.plot(wl, v, linestyle='--')
    plt.xlabel('Wavelength (μm)')
    plt.ylabel('variance')

    

    plt.tight_layout()
    plt.show()

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


def interp_1d(x, y, x_new, kind='linear', extrapolate=False):
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


def interpret(wavelength,spectrum,varience,mask):
    var=varience**0.5

    wavelength_1d=[]
    spectrum_1d=[]
    var_1d=[]

    for i in range(len(wavelength)-1):
        for j in range(len(wavelength[i])):
            if mask[i][j]==0:
                if str(spectrum[i][j])!='nan' and str(var[i][j])!='nan':
                    wavelength_1d.append(wavelength[i][j])
                    spectrum_1d.append(spectrum[i][j])
                    var_1d.append(var[i][j])
            if mask[i][j]==1:
                if str(spectrum[i][j])!='nan' and str(var[i][j])!='nan':
                    outcome_spec= interp_1d(x=wavelength[i+1], y=spectrum[i+1], x_new=wavelength[i][j], kind='linear', extrapolate=True)
                    new_spectrum = (outcome_spec+spectrum[i][j])*0.5
                    outcome_var = interp_1d(x=wavelength[i+1], y=var[i+1], x_new=wavelength[i][j], kind='linear', extrapolate=True)
                    new_var = (outcome_var+var[i][j])*0.5
                    wavelength_1d.append(wavelength[i][j])
                    spectrum_1d.append(new_spectrum)
                    var_1d.append(new_var)
            if mask[i][j]==2:
                pass
    for i in range(len(wavelength[-1])):
        if mask[-1][i]!=2:
            if str(spectrum[-1][i])!='nan' and str(var[-1][i])!='nan':
                wavelength_1d.append(wavelength[-1][i])
                spectrum_1d.append(spectrum[-1][i])
                var_1d.append(var[-1][i])

    wavelength_1d=np.asarray(wavelength_1d)
    spectrum_1d=np.asarray(spectrum_1d)
    var_1d=np.asarray(var_1d)

    idx = np.argsort(wavelength_1d)

    # 2. 重新排序三个数组
    wavelength_sorted = wavelength_1d[idx]
    spectrum_sorted   = spectrum_1d[idx]
    var_sorted        = var_1d[idx]

    return wavelength_sorted, spectrum_sorted, var_sorted

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
    #path='datas/20240203_0071/SDCK_20240203_0071.spec_a0v.fits'

    #path_signal='datas/20240203_0071/SDCH_20240203_0071.sn.fits'
    #signal = get_signal(path_signal=path_signal)

    wavelength,spectrum=get_data(path=path)
    var=get_var(path=path)
    #print(var[15])

    #print(wavelength.shape)
    #plot_with_color(wavelength=wavelength,spectrum=spectrum)
    #plot_with_color_and_variance(wavelength=wavelength,spectrum=spectrum,var=var)


    mask= make_overlap_mask(wavelength=wavelength)
    
    # plot_mask(mask_list=mask)
    # x = [1, 2, 3, 4, 5]
    # y = [10, 20, 15, 25, 30]
    # new_x=3.5
    # interpolated_value = interp_1d(x, y, new_x, kind='linear', extrapolate=True)
    # print(f"Interpolated value at {new_x}: {interpolated_value}")

    wavelength_1d, spectrum_1d, var_1d= interpret(wavelength=wavelength, spectrum=spectrum, varience=var, mask=mask)
    # print(wavelength_1d.shape, spectrum_1d.shape, var_1d.shape)
    plot_1d_spectrum(wave_1d=wavelength_1d, flux_1d=spectrum_1d)
    plot_1d_spectrum(wave_1d=wavelength_1d, flux_1d=var_1d)

    
    

    # 3. 保存为 CSV
    df = pd.DataFrame({
        'wavelength': wavelength_1d,
        'spectrum':   spectrum_1d,
        'var':        var_1d
    })
    df.to_csv('code/outcome/SDCH_20240203_0071_outcome.csv', index=False)
    #df.to_csv('code/outcome/SDCK_20240203_0071_outcome.csv', index=False)