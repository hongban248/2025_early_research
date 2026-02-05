import numpy as np
import ctypes
from pathlib import Path
import platform
import os
import matplotlib.pyplot as plt
import coronagraph as cg  #这个包还有疑似神秘小bug，需要修改一行代码才能调用
#print(cg.__version__)
import coronagraph as cg
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
# # 1. 库文件放在当前脚本同一目录下
# c_path = 'code/c/'           # 脚本所在文件夹
# lib_file = {'Linux':'func.so',
#             'Darwin':'libsort.dylib',
#             'Windows':'libsort.dll'}[platform.system()]
# #lib_path = here  lib_file   
# #              # 拼成完整路径
# #lib_path=c_path+lib_file
lib_path='code/part_2/func_export.so'
# 2. 加载
lib = ctypes.CDLL(str(lib_path))

def echo_a_fromc():
    lib.echo_a_export.argtypes=None
    lib.echo_a_export.restype=None

    lib.echo_a_export()

def sort_c(wave, flux, error):
    # 统一转成 float64 的可写 C 连续数组
    wave = np.asarray(wave, dtype=np.float64, order='C')
    flux = np.asarray(flux, dtype=np.float64, order='C')
    error = np.asarray(error, dtype=np.float64, order='C')
    n = wave.size
    if not (n == flux.size == error.size):
        raise ValueError('三个数组长度不一致')

    # 保证可写
    wave = np.require(wave, requirements='CW')
    flux = np.require(flux, requirements='CW')
    error = np.require(error, requirements='CW')

    # 设置函数签名
    lib.sort_export.argtypes = (
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_int)          # ← 不是 POINTER，只是值
    lib.sort_export.restype = None

    # 调用
    lib.sort_export(
        wave.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        flux.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        error.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        ctypes.c_int(n))

    return wave, flux, error
def get_txt(file_path):
    try:
        wavelength, flux, error = np.loadtxt(file_path,
                                     comments='#',      # 跳过所有 # 开头的行
                                     unpack=True)       # 直接拆成三列数组
        return wavelength[find_insert_position(wavelength,0.8):find_insert_position(wavelength,2.5)],flux[find_insert_position(wavelength,0.8):find_insert_position(wavelength,2.5)],error[find_insert_position(wavelength,0.8):find_insert_position(wavelength,2.5)]
    except:
        wavelength, flux = np.loadtxt(file_path,
                                     comments='#',      # 跳过所有 # 开头的行
                           unpack=True)       # 直接拆成2列数组
        wavelength=wavelength/1e4
        e=flux
        return wavelength[find_insert_position(wavelength,0.8):find_insert_position(wavelength,2.5)],flux[find_insert_position(wavelength,0.8):find_insert_position(wavelength,2.5)],e[find_insert_position(wavelength,0.8):find_insert_position(wavelength,2.5)]
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


def      vr_change_c(wavelength,flux,vr):
    wave = np.asarray(wavelength, dtype=np.float64, order='C')
    flux = np.asarray(flux,      dtype=np.float64, order='C')
    wave = np.require(wave, requirements='CW')
    n=wave.size
    wave_vr = np.empty_like(wave)
    #wave = np.require(wave, requirements='CW')
    lib.vr_change_export.argtypes=(
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_int,
        ctypes.c_double,
        ctypes.POINTER(ctypes.c_double)
    )
    lib.vr_change_export.restype=None

    lib.vr_change_export(
        wave.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        flux.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        ctypes.c_int(n),ctypes.c_double(vr),
        wave_vr.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    )

    return wave_vr

def rot_int_cmj_c(w, s, vsini, eps=0.6, nr=10, ntheta=100, dif = 0.0):
    wave = np.asarray(w, dtype=np.float64, order='C')
    flux = np.asarray(s,      dtype=np.float64, order='C')
    wave = np.require(wave, requirements='CW')
    flux = np.require(flux, requirements='CW')
    n=wave.size
    ns=np.empty_like(wave)

    lib.rot_int_cmj_export.argtypes=(
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_int,
        ctypes.c_double,
        ctypes.c_double,ctypes.c_int,ctypes.c_int,ctypes.c_double,
        ctypes.POINTER(ctypes.c_double)
    )
    lib.rot_int_cmj_export.restype=None

    lib.rot_int_cmj_export(
        wave.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        flux.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        ctypes.c_int(n),ctypes.c_double(vsini),
        ctypes.c_double(eps),ctypes.c_int(nr),ctypes.c_int(ntheta),ctypes.c_double(dif),
        ns.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    )
    return ns


def get_ck_gk_c(vr,vsini,wavelength_model,flux_model,
              wavelength_H,flux_H,error_H,
              wavelength_K,flux_K,error_K,):
    wave_model = np.asarray(wavelength_model, dtype=np.float64, order='C')
    flux_model = np.asarray(flux_model,      dtype=np.float64, order='C')
    wave_model = np.require(wave_model, requirements='CW')
    flux_model = np.require(flux_model, requirements='CW')
    n_model=wave_model.size

    wave_H = np.asarray(wavelength_H,dtype=np.float64, order='C')
    flux_H = np.asarray(flux_H,      dtype=np.float64, order='C')
    error_H=np.asanyarray(error_H,   dtype=np.float64, order='C')
    wave_H = np.require(wave_H, requirements='CW')
    flux_H = np.require(flux_H, requirements='CW')
    error_H=np.require(error_H, requirements='CW')
    n_H=wave_H.size

    wave_K = np.asarray(wavelength_K,dtype=np.float64, order='C')
    flux_K = np.asarray(flux_K,      dtype=np.float64, order='C')
    error_K=np.asanyarray(error_K,   dtype=np.float64, order='C')
    wave_K = np.require(wave_K, requirements='CW')
    flux_K = np.require(flux_K, requirements='CW')
    error_K=np.require(error_K, requirements='CW')
    n_K=wave_K.size

    #print("原始长度：",n_model,n_H,n_K)

    lib.get_ck_gk_export.argtypes=(
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_size_t, 
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_size_t, 
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_size_t, 
        ctypes.c_double,ctypes.c_double,
        ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double)
    )
    lib.get_ck_gk_export.restype=None
    ck_out = np.empty(1, dtype=np.float64)
    gk_out = np.empty(1, dtype=np.float64)
    lib.get_ck_gk_export(
        wave_model.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        flux_model.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        ctypes.c_size_t(n_model), 
        wave_H.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        flux_H.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        error_H.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        ctypes.c_size_t(n_H), 
        wave_K.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        flux_K.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        error_K.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        ctypes.c_size_t(n_K), 
        ctypes.c_double(vr),ctypes.c_double(vsini),
        ck_out.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        gk_out.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),

    )
   # print('ck结果：',ck_out[0],"Gk 结果:",gk_out[0])
    return ck_out[0],gk_out[0],vr,vsini

def get_cut(wave,flux):

    # 设置波长和分辨率参数# Set the wavelength and resolution parameters
    lammin = 0.8  # 最小波长 (μm)
    lammax = 2.5   # 最大波长 (μm)
    R = 45000      # 分辨率
    # model_path=file_path
    # wave,flux,error=get_txt(model_path)
    #print(wave,len(wave),flux,len(flux))


    # 构造低分辨率的波长网格
    wl, dwl = cg.noise_routines.construct_lam(lammin, lammax, R)

    # 使用 downbin_spec 函数将高分辨率光谱降采样到低分辨率
    flr = cg.downbin_spec(flux, wave, wl, dlam=dwl)

    # 剔除包含 NaN 的部分
    mask = ~np.isnan(wl) 
    wl_clean = wl[mask]
    flr_clean = flr[mask]
    mask = ~np.isnan(flr)
    wl_clean = wl[mask]
    flr_clean = flr[mask]
    wl,flr = wl_clean, flr_clean

    return wl,flr

def parallel_calculation():
    time1 = time.time()
    n=16
    
    # 使用ThreadPoolExecutor创建线程池
    with ThreadPoolExecutor(max_workers=n) as executor:
        # 创建10个任务，第一个参数从1到10
        futures = []
        for i in range(n):
            # 提交任务到线程池
            future = executor.submit(
                get_ck_gk_c, 
                i, 15, wave_model, flux_model, 
                wave_H, flux_H, error_H, 
                wave_K, flux_K, error_K
            )
            futures.append(future)
        
        # 等待所有任务完成
        for future in as_completed(futures):
            try:
                result = future.result()  # 获取计算结果
                print(result)
                #returm result
               # print(f"线程 {futures.index(future)+1} 完成")
            except Exception as e:
                print(f"线程出错: {e}")
    
    time2 = time.time()
    print("并行计算总用时：", time2-time1, ' s',"average: ",(time2-time1)/n,"s")

# 4. 测试
if __name__ == '__main__':
    


    #echo_a_fromc()

    H_path='code/part_2/data_for_part2/H_BC.txt'
    K_path='code/part_2/data_for_part2/K_BC.txt'
    model_path='models/bt-settle/bt-settl_131.dat.txt'

    wave_H,flux_H,error_H=get_txt(H_path)
    wave_K,flux_K,error_K=get_txt(K_path)
    wave_model,flux_model,error_model=get_txt(model_path)
    wave_H,flux_H,error_H=sort_c(wave_H,flux_H,error_H)
    wave_K,flux_K,error_K=sort_c(wave_K,flux_K,error_K)
    wave_model,flux_model,error_model=sort_c(wave_model,flux_model,error_model)

    wave_model,flux_model=get_cut(wave_model,flux_model)

    # time1=time.time()
    # get_ck_gk_c(10,15,wave_model,flux_model,wave_H,flux_H,error_H,wave_K,flux_K,error_K)
    # time2=time.time()
    # print("一次用时：",time2-time1,' s')

    parallel_calculation()

    

