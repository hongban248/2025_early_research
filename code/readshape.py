from astropy.io import fits


def readfile(path):
    with fits.open(path)as hdul:
        data=hdul[0].data
        print(data.shape)



if __name__=='__main__':
    path='datas/20240203_0071/SDCH_20240203_0071.sn.fits'
    readfile(path)
    path='datas/20240203_0071/SDCH_20240203_0071.spec.fits'
    readfile(path)
    path='datas/20240203_0071/SDCH_20240203_0071.spec2d.fits'
    readfile(path)
    path='datas/20240203_0071/SDCH_20240203_0071.var2d.fits'
    readfile(path)
    path='datas/20240203_0071/SDCH_20240203_0071.variance.fits'
    readfile(path)