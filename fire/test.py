from astropy.io import fits
import numpy as np
from matplotlib import pyplot as plt

path='/mnt/disk1/myresource/fire_reduction/fluxing/sens_fire_0079-HD62139_FIRE_85970523T112011.000.fits'

with fits.open(path) as hdul:

    data1 = hdul[1].data
    header1 = hdul[1].header

    plot_wave0=data1[0][0]
    plot_data0 = data1[0][1] #1D data


    data2 = hdul[2].data
    header2 = hdul[2].header

    print("Data shape:", data2[0][0])
    #print("Header:", header2)
    plot_wave=data2[0][12]
    plot_data = data2[0][13] #1D data


    plt.figure(figsize=(10, 6))
    plt.plot(plot_wave0, plot_data0, label='Data from HDU 1', alpha=0.7)
    plt.plot(plot_wave, plot_data, label='Data from HDU 2', alpha=0.7)
    plt.xlabel('Wavelength (Angstroms)')
    plt.ylabel('Intensity')
    plt.title('FITS Spectrum')
    plt.legend()



    plt.show()


    