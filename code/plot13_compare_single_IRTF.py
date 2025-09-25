#画出其他模型、观测结果的光谱，和H波段，K波段的结果（仅仅scale对比）

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import csv
from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from cycler import cycler
import math
from scipy.interpolate import interp1d, CubicSpline
import os
import subprocess
import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import numpy as np
import pandas as pd

def get_txt(file_path):
    try:
        wavelength, flux, error = np.loadtxt(file_path,
                                     comments='#',      # 跳过所有 # 开头的行
                                     unpack=True)       # 直接拆成三列数组
        return wavelength[find_insert_position(wavelength,1.5):find_insert_position(wavelength,2.5)],flux[find_insert_position(wavelength,1.5):find_insert_position(wavelength,2.5)],error[find_insert_position(wavelength,1.5):find_insert_position(wavelength,2.5)]
    except:
        wavelength, flux = np.loadtxt(file_path,
                                     comments='#',      # 跳过所有 # 开头的行
                           unpack=True)       # 直接拆成2列数组
        wavelength=wavelength/1e4
        e=flux
        return wavelength[find_insert_position(wavelength,1.5):find_insert_position(wavelength,2.5)],flux[find_insert_position(wavelength,1.5):find_insert_position(wavelength,2.5)],e[find_insert_position(wavelength,1.5):find_insert_position(wavelength,2.5)]


def plot_1d_spectrum(wave_1d, flux_1d):
    plt.figure(figsize=(12, 4))
    plt.plot(wave_1d, flux_1d, lw=1, color='k')
    plt.xlabel('Wavelength (μm)')
    plt.ylabel('Flux (normalized)')
    plt.title('Merged 1-D Spectrum')
    plt.tight_layout()
    plt.show()

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

def process(wavelength,flux,error,wavelength1,flux1,error1,wavelength2,flux2,error2):
    flux1_scale=[]
    flux2_scale=[]
    error1_scale=[]
    error2_scale=[]

    for i in range(len(wavelength1)):
        flux1_new=interp_1d(wavelength,flux,wavelength1[i])
        flux1_scale.append(flux1_new)
    scale=np.mean(flux1_scale)/np.mean(flux1)
    print('scale1:',scale)
    flux1=flux1*scale
    error1=error1*scale

    for i in range(len(wavelength2)):
        flux2_new=interp_1d(wavelength,flux,wavelength2[i])
        flux2_scale.append(flux2_new)
    scale=np.mean(flux2_scale)/np.mean(flux2)
    flux2=flux2*scale
    error2=error2*scale
    print('scale2:',scale)

    plt.figure(figsize=(20, 15))
    plt.plot(wavelength1, flux1, color='red', label='H波段')
    plt.plot(wavelength2, flux2, color='green', label='K波段')
    plt.plot(wavelength, flux, color='blue', label='其他恒星光谱')
    plt.xlabel('Wavelength (μm)')
    plt.ylabel('Flux (normalized)')
    plt.tight_layout()
    
    plt.show()



# -------------------- GUI --------------------
class SpecGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("光谱批处理")
        self.geometry("600x320")

        # 变量
        self.model_path = tk.StringVar(value='models/other_V')
        self.csv1_path  = tk.StringVar(value='code/outcome/SDCH_20240203_0071_middle.back4/outcome.csv')
        self.csv2_path  = tk.StringVar(value='code/outcome/SDCK_20240203_0071_middle/outcome.csv')

        # 布局
        self.build_ui()

    def build_ui(self):
        pad = {'padx': 6, 'pady': 6, 'sticky': 'ew'}

        # 模型文件
        ttk.Label(self, text="模型光谱 (.txt):").grid(row=0, column=0, **pad)
        ttk.Entry(self, textvariable=self.model_path, width=50).grid(row=0, column=1, **pad)
        ttk.Button(self, text="浏览", command=self.browse_model).grid(row=0, column=2, **pad)

        # H-band CSV
        ttk.Label(self, text="H 波段 CSV:").grid(row=1, column=0, **pad)
        ttk.Entry(self, textvariable=self.csv1_path, width=50).grid(row=1, column=1, **pad)
        ttk.Button(self, text="浏览", command=lambda: self.browse_csv(1)).grid(row=1, column=2, **pad)

        # K-band CSV
        ttk.Label(self, text="K 波段 CSV:").grid(row=2, column=0, **pad)
        ttk.Entry(self, textvariable=self.csv2_path, width=50).grid(row=2, column=1, **pad)
        ttk.Button(self, text="浏览", command=lambda: self.browse_csv(2)).grid(row=2, column=2, **pad)

        # 运行按钮
        ttk.Button(self, text="运行主流程", command=self.run_main).grid(row=3, column=0, columnspan=3, pady=15)

    # --------------- 浏览回调 ---------------
    def browse_model(self):
        fn = filedialog.askopenfilename(
            title="选模型光谱",
            initialdir='models/other_V',   # ← 默认打开这个文件夹
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if fn:
            self.model_path.set(fn)

    def browse_csv(self, which):
        fn = filedialog.askopenfilename(
            title=f"选 {'H' if which==1 else 'K'}-band CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if fn:
            (self.csv1_path if which==1 else self.csv2_path).set(fn)

    # --------------- 主流程 ---------------
    def run_main(self):
        try:
            
            
            w,f, e = get_txt(self.model_path.get())
            

            f[f < 0] = np.nan

            # 2. 读 H 波段
            df = pd.read_csv(self.csv1_path.get())
            wH, fH, eH = sort(df['wavelength'].values,
                              df['spectrum'].values,
                              df['dev'].values)
            left, right = find_insert_position(wH, 1.53), find_insert_position(wH, 1.711)
            wH, fH, eH = wH[left:right], fH[left:right], eH[left:right]

            # 3. 读 K 波段
            df = pd.read_csv(self.csv2_path.get())
            wK, fK, eK = sort(df['wavelength'].values,
                              df['spectrum'].values,
                              df['dev'].values)
            left, right = find_insert_position(wK, 2.05), find_insert_position(wK, 2.36)
            wK, fK, eK = wK[left:right], fK[left:right], eK[left:right]

            # 4. 调用 process
            process(w, f, e, wH, fH, eH, wK, fK, eK)

        except Exception as ex:
            messagebox.showerror("运行出错", str(ex))

# -------------------- 入口 --------------------
if __name__ == '__main__':
    SpecGUI().mainloop()