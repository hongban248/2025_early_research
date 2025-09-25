import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt

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


if __name__ == "__main__":

# 读取Excel文件
    file_path = 'code/part_2/outcome_for_part2/Gks.xlsx'  # 替换为你的文件路径
    df = pd.read_excel(file_path)

    # 提取Teff，logg，Gk三列数据
    teff = df['teff'].values
    logg = df['logg'].values
    gk = df['Gk'].values

    teff, logg, gk = sort(teff, logg, gk)

    # 获取不同的logg值
    unique_logg = np.unique(logg)

    # 创建一个图形和轴
    fig, ax = plt.subplots()

    # 为每个logg值绘制一条线
    for logg_value in unique_logg:
        # 找到当前logg值的索引
        indices = np.where(logg == logg_value)
        # 绘制线图
        ax.plot(teff[indices], gk[indices], label=f'log g = {logg_value}', marker='o')

    # 设置图表标题和坐标轴标签
    ax.set_title('Teff vs Gk by log g')
    ax.set_xlabel('Teff')
    ax.set_ylabel('Gk')

    # 添加图例
    ax.legend()

    # 显示图表
    plt.show()

    # # 打印结果，查看是否正确提取
    # print("Teff:", len(teff))
    # print("Logg:", len(logg))
    # print("Gk:", len(gk))