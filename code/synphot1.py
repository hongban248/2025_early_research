from astropy import units as u
from synphot import units, SourceSpectrum
from synphot.models import BlackBodyNorm1D, GaussianFlux1D
import numpy as np
import matplotlib.pyplot as plt   # 新增


g_abs = SourceSpectrum(GaussianFlux1D, amplitude=1*u.mJy,
                       mean=4000, stddev=20)

g_em = SourceSpectrum(GaussianFlux1D,
                      total_flux=3.5e-13*u.erg/(u.cm**2 * u.s),
                      mean=3000, fwhm=100)
bb = SourceSpectrum(BlackBodyNorm1D, temperature=6000)
sp = 2 * bb + g_em - g_abs

sp.plot(left=1, right=7000)
plt.show() 

sp(0.3 * u.micron)