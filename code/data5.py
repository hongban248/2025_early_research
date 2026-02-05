import os
from astropy.io import fits
import matplotlib.pyplot as plt
# 目标文件路径


def get(path):    # 目标文件路径
    #file_path = os.path.join("models", "HiRes", "lte05000-4.50-0.0.PHOENIX-ACES-AGSS-COND-2011-HiRes.fits")
    file_path = path
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
    else:
        # 读取FITS文件
        with fits.open(file_path) as hdul:
            print(f"FITS文件包含 {len(hdul)} 个HDU")
            data=hdul[0].data  # 获取第一个HDU的数据
            print(f"数据形状: {data.shape}")  # 打印数据的形
            #print(hdul[0].header)  # 打印头部信息
            
            return data

spectrum = get("models/HiRes/lte05000-4.50-0.0.PHOENIX-ACES-AGSS-COND-2011-HiRes.fits")
wavelength = get("models/HiRes/WAVE_PHOENIX-ACES-AGSS-COND-2011.fits")/1e4

def plot_1d_spectrum(wave_1d, flux_1d):
    plt.figure(figsize=(12, 4))
    plt.plot(wave_1d, flux_1d, lw=1, color='k')
    plt.xlabel('Wavelength (μm)')
    plt.ylabel('Flux (normalized)')
    plt.title('Hires-Merged 1-D Spectrum')
    plt.tight_layout()
    plt.show()

print(wavelength.shape)
print(spectrum.shape)

plot_1d_spectrum(wavelength, spectrum)