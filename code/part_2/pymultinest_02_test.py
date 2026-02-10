import os
import sys
#sys.path.append("/data/users/zzhan485/python_scripts/")
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

r_sun=6.957e10  # cm

## 5.1 parameters
parameters = ['Teff', 'logg','meta','alpha','vr','vsini']
num_grid_params = 4  #不包含vr和vsini


teff_min = 3000
teff_max = 4000
logg_min = 4    #3到5.5，guidpoint也要加3-5.5
logg_max = 5.5
meta_min = -0.5
meta_max = -0.5
alpha_min = 0.2 #改
alpha_max = 0.2
vr_min = 0.0  #-30----+30
vr_max = 4.0
vsini_min = 0.0 # 0-30
vsini_max = 10.0
# radius_min = 0.2  #注意这里是Rsun，不是Rjup
# radius_max = 0.6# 使用了mamajek table来估计半径范围

def prior(cube, ndim, nparams):
    cube[0] = teff_min + (teff_max - teff_min) * cube[0]
    cube[1] = logg_min + (logg_max - logg_min) * cube[1]
    cube[2] = meta_min + (meta_max - meta_min) * cube[2]
    cube[3] = alpha_min + (alpha_max - alpha_min) * cube[3]
    cube[4] = vr_min + (vr_max - vr_min) * cube[4]
    cube[5] = vsini_min + (vsini_max - vsini_min) * cube[5]
    #cube[6] = radius_min + (radius_max - radius_min) * cube[6]

#下面两行存疑
grid_points = np.load('code/part_2/outcome_for_part2/pymultinest_outcome/bt-settle_points.npy', allow_pickle=True)
fl_mod_spec_combo = np.load('code/part_2/outcome_for_part2/pymultinest_outcome/bt-settle_full.npy', allow_pickle=True)[1:]

#更新过后跑3中模拟，H，K，H+K
K_path='code/part_2/data_for_part2/K_BC.txt'
wavelength_K,flux_K,error_K=get_txt(K_path)

### 6. log-likelihood
def loglike_H(cube, ndim, nparams):
    ## 6.1 current parameters
    teff = cube[0]
    logg = cube[1]
    meta = cube[2]
    alpha = cube[3]
    vr = cube[4]
    vsini = cube[5]
    #radius = cube[6]

    ## 6.2 spectra
    # 6.2.1 interpolation  #随便给参数得到模型
    fl_mod_spec = 10 ** griddata(points = grid_points,
                                 values = np.log10(fl_mod_spec_combo),
                                 xi = np.array([ np.log10(teff), logg, meta ]),
                                 method = 'linear',
                                 fill_value = np.nan).reshape(-1)
    # 6.2.2 scaling by radius
    fl_mod_spec = fl_mod_spec * (radius * r_sun / distance)**2  #距离10.88秒差距转换成厘米
    # => incorporate vr and vsini
    wl_mod=vr_change(wl_mod,fl_mod_spec,vr)  #视向速度修正
    fl_mod_spec=rot_int_cmj(wl_mod,fl_mod_spec,vsini)  #旋转变宽
    #额外插值，再把模型wave转到数据wave上   先只fits H band
    #########################################################################


    


    print(len(fl_mod_spec),len(flux_K))
    # 6.2.3 likelihood 把模型和数据对比 flf2，err其实就是数据
    #spec_sigma_squared = flerr_f2**2 + 10**log10b_spec
    spec_sigma_squared= error_K**2
    spec_logl = - 0.5 * np.sum( (fl_mod_spec - flux_K)**2 / spec_sigma_squared ) - 0.5 * np.sum( np.log(2 * np.pi * spec_sigma_squared) )
    ## 6.4 final likelihood
    #return spec_logl + phot_w1_logl + phot_w2_logl + phot_irac36_logl + phot_irac45_logl
    return spec_logl

def loglike_K():
    return 0.0

def loglike():
    return loglike_H()+loglike_K()


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


if __name__ == "__main1111__":

    output_path='code/part_2/outcome_for_part2/pymultinest_outcome/'
    n_params = len(parameters)
    json.dump(parameters, open(output_path + '_%s_params.json'%(time.time()), 'w'))
    pymultinest.run(loglike, prior, n_params, 
                    outputfiles_basename=output_path+'bt-settle-test-',
                    resume = True, verbose = True,
                    n_live_points = 400,
                    sampling_efficiency = 0.8,
                    const_efficiency_mode=False)
    
    
    
    
    analyzer = pymultinest.Analyzer(n_params = n_params,outputfiles_basename = output_path+'bt-settle-test-')
    
    
    # 修复所有可能的输出文件
    base_path = output_path + 'bt-settle-test-'
    for suffix in ['post_equal_weights.dat', 'phys_live.points', 'live.points', 'ev.dat']:
        file_path = base_path + suffix
        fix_scientific_notation_inplace(file_path)
    
    #s = analyzer.get_stats()
    analyzer = pymultinest.Analyzer(n_params = n_params,outputfiles_basename = output_path+'bt-settle-test-')
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

if __name__ == "__main__":

    output_path='code/part_2/outcome_for_part2/pymultinest_outcome/'
    n_params = len(parameters)
    json.dump(parameters, open(output_path + '_%s_params.json'%(str(time.time())), 'w'))
    pymultinest.run(loglike, prior, n_params, 
                    outputfiles_basename=output_path+'bt-settle-test-',
                    resume = True, verbose = True,
                    n_live_points = 4000, #越多越好 400测试，一般2000-4000
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