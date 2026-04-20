import numpy as np
import astropy.units as u
from synphot import SourceSpectrum, SpectralElement, Observation
from synphot.models import Empirical1D

'''
VEGAMAG B星等： 12.861036032504945 mag(VEGA)
VEGAMAG g星等： 12.15954168307861 mag(VEGA)
VEGAMAG V星等： 11.297231579158183 mag(VEGA)
VEGAMAG r星等： 10.551654544198119 mag(VEGA)
VEGAMAG i星等： 9.048026480325403 mag(VEGA)
'''


def get_vegamag(wavelength, flux, filter_path):
    wave= wavelength * u.um.to(u.AA)
    flam = flux * (u.erg / u.s / u.cm**2 / u.AA)

    # Make a source spectrum
    src = SourceSpectrum(Empirical1D, points=wave, lookup_table=flam)

    # Load a filter throughput you have locally (λ in Å, dimensionless T(λ))
    filt_wave, filt_thru = np.loadtxt(filter_path, unpack=True)  # two columns
    band = SpectralElement(Empirical1D, points=filt_wave * u.AA, lookup_table=filt_thru)

    # Observe (photon-weighted by default)
    observation = Observation(src, band, force='extrapolate')

    

    # 计算观测光谱的 VEGAMAG 星等
    # 加载内置的 Vega 光谱
    vegaspec = SourceSpectrum.from_vega()

    # 计算观测光谱的 VEGAMAG 星等
    vegamag = observation.effstim('vegamag', vegaspec=vegaspec)
    #print("VEGAMAG 星等：", vegamag)

    return vegamag


wave_B = np.array([0.429924, 0.429924 + 1e-16])
flux_B = np.array([4.683E-14, 4.683E-14])

wave_g = np.array([0.463927, 0.463927 + 1e-16])
flux_g = np.array([7.584E-14, 7.584E-14])

wave_V = np.array([0.539385, 0.539385 + 1e-16])
flux_V = np.array([1.132E-13, 1.132E-13])

wave_r = np.array([0.612196, 0.612196 + 1e-16])
flux_r = np.array([1.518E-13, 1.518E-13])

wave_i = np.array([0.743889, 0.743889 + 1e-16])
flux_i = np.array([3.358E-13, 3.358E-13])


print(wave_B.dtype)
veg_B = get_vegamag(wave_B, flux_B, 'datas/filters/Misc_UCAC.B.dat')
veg_g = get_vegamag(wave_g, flux_g, 'datas/filters/Misc_UCAC.sdss_g.dat')
veg_V = get_vegamag(wave_V, flux_V, 'datas/filters/Misc_UCAC.V.dat')
veg_r = get_vegamag(wave_r, flux_r, 'datas/filters/Misc_UCAC.sdss_r.dat')
veg_i = get_vegamag(wave_i, flux_i, 'datas/filters/Misc_UCAC.sdss_i.dat')   
print("VEGAMAG B星等：", veg_B)
print("VEGAMAG g星等：", veg_g)
print("VEGAMAG V星等：", veg_V)
print("VEGAMAG r星等：", veg_r)
print("VEGAMAG i星等：", veg_i)