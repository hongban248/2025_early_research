import os
import sys
sys.path.append("/data/users/zzhan485/python_scripts/")
import numpy as np
import pymultinest
import json
import pandas as pd
from astropy import units as u
from astropy.io import fits
from scipy.interpolate import griddata
import scipy.stats
import random

from petitRADTRANS import nat_cst as nc
from assist_fm_C2b import syn_phot, filter_info




######################################
### CHANGE FOR DIFFERENT GRID MODELS
######################################
### 4. load models
### 5. parameters and priors
## 5.1 parameters
parameters = ['Teff', 'logg', 'R', 'log10b_spec']
num_grid_params = 2
## 5.2 priors
teff_min = 200
teff_max = 800
logg_min = 2.5
logg_max = 5.5
radius_min = 0.5
radius_max = 2.5
log10b_spec_min = 2 * np.log10( 0.1 * np.min(flerr_f2) )
log10b_spec_max = 2 * np.log10( 100 * np.max(flerr_f2) )
print("log10b range: %.3e - %.3e"%(10**(log10b_spec_min/2), 10**(log10b_spec_max/2)))
## 5.3 function
def prior(cube, ndim, nparams):
    cube[0] = teff_min + (teff_max - teff_min) * cube[0]
    cube[1] = logg_min + (logg_max - logg_min) * cube[1]
    cube[2] = radius_min + (radius_max - radius_min) * cube[2]
    cube[3] = log10b_spec_min + (log10b_spec_max - log10b_spec_min) * cube[3]
    


### 6. log-likelihood
def loglike(cube, ndim, nparams):
    ## 6.1 current parameters
    teff = cube[0]
    logg = cube[1]
    radius = cube[2]
    log10b_spec = cube[3]
    ## 6.2 spectra
    # 6.2.1 interpolation
    fl_mod_spec = 10 ** griddata(points = grid_points,
                                 values = np.log10(fl_mod_spec_combo),
                                 xi = np.array([ np.log10(teff), logg ]),
                                 method = 'linear',
                                 fill_value = np.nan).reshape(-1)
    # 6.2.2 scaling by radius
    fl_mod_spec = fl_mod_spec * (radius * nc.r_jup / distance)**2
    # => incorporate vr and vsini
    # 6.2.3 likelihood
    spec_sigma_squared = flerr_f2**2 + 10**log10b_spec
    spec_logl = - 0.5 * np.sum( (fl_mod_spec - fl_f2)**2 / spec_sigma_squared ) - 0.5 * np.sum( np.log(2 * np.pi * spec_sigma_squared) )
    '''## 6.3 photometry
    # 6.3.1 interpolation
    fl_mod_phot = 10 ** griddata(points = grid_points,
                                 values = np.log10(fl_mod_phot_combo),
                                 xi = np.array([ np.log10(teff), logg ]),
                                 method = 'linear',
                                 fill_value = np.nan).reshape(-1)
    # 6.3.2 scaling by radius
    fl_mod_phot = fl_mod_phot * (radius * nc.r_jup / distance)**2
    # 6.3.3 synthesize photometry
    fl_w1_mod = syn_phot(wl_mod_phot, fl_mod_phot, "W1_Vega", filter_response_path = filter_response_path)
    fl_w2_mod = syn_phot(wl_mod_phot, fl_mod_phot, "W2_Vega", filter_response_path = filter_response_path)
    fl_irac36_mod = syn_phot(wl_mod_phot, fl_mod_phot, "IRAC36_Vega", filter_response_path = filter_response_path)
    fl_irac45_mod = syn_phot(wl_mod_phot, fl_mod_phot, "IRAC45_Vega", filter_response_path = filter_response_path)
    # 6.3.3 likelihood for spectra
    phot_w1_logl = -0.5 * (fl_w1_mod - fl_w1)**2 / flerr_w1**2  - 0.5 * np.sum( np.log(2 * np.pi * flerr_w1**2 ) )
    phot_w2_logl = -0.5 * (fl_w2_mod - fl_w2)**2 / flerr_w2**2 - 0.5 * np.sum( np.log(2 * np.pi * flerr_w2**2) )
    phot_irac36_logl = -0.5 * (fl_irac36_mod - fl_irac36)**2 / flerr_irac36**2 - 0.5 * np.sum( np.log(2 * np.pi * flerr_irac36**2) )
    phot_irac45_logl = -0.5 * (fl_irac45_mod - fl_irac45)**2 / flerr_irac45**2 - 0.5 * np.sum( np.log(2 * np.pi * flerr_irac45**2) )'''
    ## 6.4 final likelihood
    #return spec_logl + phot_w1_logl + phot_w2_logl + phot_irac36_logl + phot_irac45_logl
    return spec_logl


    

### 7. run forward modeling
if platform == 'lux':
    ## 7.1 preparation for pymultinest
    n_params = len(parameters)
    resume = True
    sampling_efficiency = 0.8
    const_efficiency_mode = False
    n_live_points = 4000
    json.dump(parameters, open(output_path + '_%s_params.json'%(label), 'w'))
    ## 7.2 run pymultinest
    pymultinest.run(loglike,
                    prior,
                    n_params,
                    outputfiles_basename= output_path + '_%s_'%(label),
                    resume = resume,
                    verbose = True,
                    sampling_efficiency = sampling_efficiency,
                    const_efficiency_mode = const_efficiency_mode,
                    n_live_points = n_live_points)
    ## 7.3 post-run analysis
    analyzer = pymultinest.Analyzer(n_params = n_params,
                                    outputfiles_basename = output_path + '_%s_'%(label))
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




# == == == == == ==



### 2. load BT-Settl models
## 2.1 parameter space #方阵
teff_grid_points = np.array( list(np.arange(200, 601, 50)) + list(np.arange(700, 801, 100)) )
logg_grid_points = np.arange(2.5, 5.51, 0.5)
meta_grid_points =
alpha_grid_points =
## 2.2 grid points
grid_point_list = []
for teff in teff_grid_points:
    for logg in logg_grid_points:
        grid_point_list.append([teff, logg])
num_grid_points = len(grid_point_list)
print("%d grid points in total"%(num_grid_points))
## 2.3 create empty arrays
fl_spec_array = np.ones((num_grid_points, num_pixel)) * np.nan
fl_phot_array = np.ones((num_grid_points, num_phot)) * np.nan
fl_full_array = np.ones((num_grid_points, num_full)) * np.nan
## 2.4 load models
for index in range(num_grid_points):
    # 2.4.1 load file
    teff_val, logg_val = grid_point_list[index]
    mod_reader = np.genfromtxt(model_path + 'CEQ/spec_T%d_lg%.1f_CEQ.txt'%(teff_val, logg_val), skip_header=2)
    raw_wl_mod = mod_reader[:,0]
    raw_fl_mod = (mod_reader[:,1] * u.W / u.m**2 / u.micron).to(u.erg / u.s / u.cm**2 / u.Angstrom).value
    # 2.4.2 spectrum
    # downgrade resolution
    fl_mod = cg.downbin_spec(raw_fl_mod, raw_wl_mod, wl_mod, dlam=dwl_mod)
    id_good = np.where(np.isnan(fl_mod) == False)
    # re-sampling
    fl_spec_array[index] = interp1d(wl_mod[id_good], fl_mod[id_good])(wl_c2b)
    # 2.4.3 photometry
    fl_phot_array[index] = cg.downbin_spec(raw_fl_mod, raw_wl_mod, wl_phot, dlam=dwl_phot)
    # 2.4.4 full specrum
    fl_full_array[index] = np.copy(raw_fl_mod)
## 2.5 save model spectra and grid points
np.save(main_path + 'processed/CEQ/ATMOP20_CEQ_grid_points.npy', np.array(grid_point_list))
np.save(main_path + 'processed/CEQ/ATMOP20_CEQ_spec.npy', np.vstack((wl_c2b, fl_spec_array)) )
#np.save(main_path + 'processed/CEQ/ATMOP20_CEQ_phot.npy', np.vstack((wl_phot, fl_phot_array)) )
np.save(main_path + 'processed/CEQ/ATMOP20_CEQ_full.npy', np.vstack((wl_full, fl_full_array)) )
