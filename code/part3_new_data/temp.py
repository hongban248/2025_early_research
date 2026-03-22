from astropy.io import fits

fits_path='datas/SDCK_20240203_0071.flux_a0v.fits'
with fits.open(fits_path) as hdul:
    data = hdul[0].data
    header = hdul[0].header
    print(header)