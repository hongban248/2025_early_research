from astropy.io import fits
import matplotlib.pyplot as plt

def plot_spectrum(file_path):
    """
    从spec_a0v.fits文件中读取光谱数据并绘制光谱图。
    
    参数:
        file_path (str): spec_a0v.fits文件的路径。
    """
    try:
        # 打开FITS文件
        with fits.open(file_path) as hdul:
            # 获取波长信息
            wavelength = hdul[3].data  # WAVELENGTH扩展
            print(wavelength[0].shape)
            for i in [27-j for j in range(28)]:
                print(i,wavelength[i])
            # 获取校正后的光谱数据
            spectrum = hdul[1].data  # SPEC_DIVIDE_A0V扩展
            
            # 绘制光谱图
            plt.figure(figsize=(15, 10))
            plt.plot(wavelength[1], spectrum[1], label='Corrected Spectrum')
            plt.xlabel('Wavelength (um)')
            plt.ylabel('Flux')
            plt.title('Spectrum')
            plt.legend()
            plt.grid(True)
            #plt.show()
            
    except FileNotFoundError:
        print(f"错误：文件 {file_path} 未找到。")
    except Exception as e:
        print(f"读取文件时发生错误：{e}")

# 示例调用
plot_spectrum("datas/20240203_0071/SDCH_20240203_0071.spec_a0v.fits")