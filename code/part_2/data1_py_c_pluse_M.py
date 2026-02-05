import numpy as np
import astropy.units as u
from synphot import SourceSpectrum, SpectralElement, Observation
from synphot.models import Empirical1D
import matplotlib.pyplot as plt
import os

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

        return remove_negative(wavelength[find_insert_position(wavelength,1.0):find_insert_position(wavelength,2.5)],flux[find_insert_position(wavelength,1.0):find_insert_position(wavelength,2.5)],error[find_insert_position(wavelength,1.0):find_insert_position(wavelength,2.5)])
    except:
        wavelength, flux = np.loadtxt(file_path,
                                     comments='#',      # 跳过所有 # 开头的行
                           unpack=True)       # 直接拆成2列数组
        wavelength=wavelength/1e4
        e=flux
        return remove_negative(wavelength[find_insert_position(wavelength,1.0):find_insert_position(wavelength,2.5)],flux[find_insert_position(wavelength,1.0):find_insert_position(wavelength,2.5)],e[find_insert_position(wavelength,1.0):find_insert_position(wavelength,2.5)])

def remove_negative(wave, flux, error):
    # 创建一个布尔掩码，标记 flux >= 0 的位置
    mask = flux >= 0
    
    # 使用布尔掩码过滤 wave, flux, error
    wave = wave[mask]
    flux = flux[mask]
    error = error[mask]
    
    return wave, flux, error

def process_and_save(file_path, constant, output_dir):
    """
    处理文件并保存修正后的数据
    :param file_path: 输入文件路径
    :param constant: 修正常数
    :param output_dir: 输出目录
    """
    # 获取文件名
    name = file_path.split('/')[-1]
    # 构造新的文件路径
    new_file_path = os.path.join(output_dir, name)
    
    # 读取数据
    wave, flux, error = get_txt(file_path)
    
    # 修正通量
    flux = flux * constant
    
    # 保存修正后的数据
    np.savetxt(new_file_path, np.c_[wave, flux, error], 
               header='# wavelength(micron) flux(erg/s/cm2/micron) error(erg/s/cm2/micron)')
    print(f"修正后的数据已保存到 {new_file_path}")

if __name__=='__main__':
    
    c1=0.015688945613546456
    c2=0.06812425032464571
    c3=0.049893239378711214

    # AD Leo M3V
    txt_path_M3='models/other_V/AD_Leo_M3V.txt'
    # Gl_381_M2.5V
    txt_path_M2_5_1='models/other_V/Gl_381_M2.5V.txt' 
    #HO_Lib_M2.5V
    txt_path_M2_5_2='models/other_V/HO_Lib_M2.5V.txt'

    # wave1,flux1,error1=get_txt(txt_path_M3)
    # name1=txt_path_M3.split('/')[-1]
    # name1_new=os.path.join('code/part_2/data_for_part2',name1)
    # flux1=flux1*c1
    # np.savetxt(name1_new,np.c_[wave1,flux1,error1],header='# wavelength(micron) flux(erg/s/cm2/micron) error(erg/s/cm2/micron)')

    process_and_save(txt_path_M3, c1, 'code/part_2/data_for_part2')
    process_and_save(txt_path_M2_5_1, c2, 'code/part_2/data_for_part2')
    process_and_save(txt_path_M2_5_2, c3, 'code/part_2/data_for_part2')

    # plt.plot(wave,flux)
    # plt.fill_between(wave, flux-error, flux+error, color='gray', alpha=0.5)
    # plt.xlabel('Wavelength (microns)')
    # plt.ylabel('Flux')
    # plt.title('Spectrum with Error Shading')    
    # plt.show()
