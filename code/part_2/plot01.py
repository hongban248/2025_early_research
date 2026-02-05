#老师给的文件，仅仅参考
import numpy as np
import astropy.units as u
from synphot import SourceSpectrum, SpectralElement, Observation
from synphot.models import Empirical1D

# Your spectrum (wavelength in Angstrom, F_lambda in erg s^-1 cm^-2 Å^-1)
wave = np.loadtxt("my_spectrum.txt", usecols=0) * u.AA
flam = np.loadtxt("my_spectrum.txt", usecols=1) * (u.erg / u.s / u.cm**2 / u.AA)

# Make a source spectrum
src = SourceSpectrum(Empirical1D, points=wave, lookup_table=flam)

# Load a filter throughput you have locally (λ in Å, dimensionless T(λ))
filt_wave, filt_thru = np.loadtxt("filter_r.dat", unpack=True)  # two columns
band = SpectralElement(Empirical1D, points=filt_wave * u.AA, lookup_table=filt_thru)

# Observe (photon-weighted by default)
obs = Observation(src, band, force='extrapolate')

# Band-integrated flux density in F_lambda (effective monochromatic)
f_lambda_eff = obs.effstim('flam')        # erg s^-1 cm^-2 Å^-1
f_nu_eff     = obs.effstim('fnu')         # erg s^-1 cm^-2 Hz^-1

# Magnitudes
abmag  = obs.effstim('abmag')             # AB mag
vegamag = obs.effstim('vegamag')          # if Vega ref is configured
stmag = obs.effstim('stmag')
print(f"AB = {abmag:.3f},  f_lambda = {f_lambda_eff:.3e}")