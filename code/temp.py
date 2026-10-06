from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt


# ========== 更简洁的版本（假设已知列顺序） ==========

def read_fire(filename):
    """
    
    """
    with fits.open(filename) as hdul:
        header = hdul[1].header
        data=hdul[1].data

    print(header)
    print(data,data.shape)

    wave=[i[2]/1e4 for i in data]
    #print(wave,len(wave))
    counts=[i[3] for i in data]
    #print(counts)

    var=[i[5] for i in data]

    return wave,counts,var
    
    


# ========== 使用示例 ==========
wave, counts, var = read_fire("fire/spec1d_fire_0074-COCONUTS-2A_FIRE_85970523T110233.000.fits")

plt.figure(figsize=(12, 4))
plt.plot(wave, counts, 'k-', lw=0.5)
plt.xlabel('Wavelength (um)')
plt.ylabel('Counts')
plt.title('Optimal Extraction Spectrum')    
plt.show()
# plt.figure(figsize=(12, 4))
# plt.plot(wave, counts, 'k-', lw=0.5)
# plt.xlabel('Wavelength (Angstrom)')
# plt.ylabel('Counts')
# plt.title('Optimal Extraction Spectrum')
# plt.show()