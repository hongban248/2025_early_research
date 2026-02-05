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


## 5.1 parameters
parameters = ['Teff', 'logg','meta','vr','vsini']
num_grid_params = 3


teff_min = 3000
teff_max = 4000
logg_min = 4    #3到5.5，guidpoint也要加3-5.5
logg_max = 5.5
meta_min = -1.0
meta_max = 0.5
alpha_min = 0.0
alpha_max = 0.4
vr_min = 0.0
vr_max = 4.0
vsini_min = 0.0 
vsini_max = 10.0
# radius_min = 0.2  #注意这里是Rsun，不是Rjup
# radius_max = 0.8

def prior(cube, ndim, nparams):
    cube[0] = teff_min + (teff_max - teff_min) * cube[0]
    cube[1] = logg_min + (logg_max - logg_min) * cube[1]
    cube[2] = meta_min + (meta_max - meta_min) * cube[2]
    #cube[3] = alpha_min + (alpha_max - alpha_min) * cube[3]
    cube[3] = vr_min + (vr_max - vr_min) * cube[3]
    cube[4] = vsini_min + (vsini_max - vsini_min) * cube[4]
    #cube[5] = radius_min + (radius_max - radius_min) * cube[5]


### 6. log-likelihood
def loglike(cube, ndim, nparams):
    ## 6.1 current parameters
    teff = cube[0]
    logg = cube[1]
    meta = cube[2]
    #alpha = cube[3]
    vr = cube[3]
    vsini = cube[4]
    #radius = cube[5]

    ## 6.2 spectra
    # 6.2.1 interpolation  #随便给参数得到模型
    fl_mod_spec = 10 ** griddata(points = grid_points,
                                 values = np.log10(fl_mod_spec_combo),
                                 xi = np.array([ np.log10(teff), logg, meta ]),
                                 method = 'linear',
                                 fill_value = np.nan).reshape(-1)
    # 6.2.2 scaling by radius
    fl_mod_spec = fl_mod_spec * (radius * nc.r_jup / distance)**2
    # => incorporate vr and vsini
    wl_mod=vr_change_c(wl_mod,fl_mod_spec,vr)  #视向速度修正
    fl_mod_spec=rot_int_cmj_c(wl_mod,fl_mod_spec,vsini)  #旋转变宽
    #额外插值，再把模型wave转到数据wave上   先只fits H band
    # 6.2.3 likelihood 把模型和数据对比 flf2，err其实就是数据
    spec_sigma_squared = flerr_f2**2 + 10**log10b_spec
    spec_logl = - 0.5 * np.sum( (fl_mod_spec - fl_f2)**2 / spec_sigma_squared ) - 0.5 * np.sum( np.log(2 * np.pi * spec_sigma_squared) )
    ## 6.4 final likelihood
    #return spec_logl + phot_w1_logl + phot_w2_logl + phot_irac36_logl + phot_irac45_logl
    return spec_logl



