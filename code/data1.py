#把数据保存成各种格式

from astropy.io import fits
import numpy as np
import pandas as pd
import csv
import math
import json

def get_data(path):
    with fits.open(path) as hdul:
        wavelength = hdul[3].data  # WAVELENGTH扩展
        spectrum = hdul[1].data  # SPEC_DIVIDE_A0V扩

    return wavelength,spectrum

def get_var(path):
    with fits.open(path)as hdul:
        data=hdul[2].data
    return data


def make_txt(path,wavelength,spectrum,dev,stn):
    with open(path,mode='w') as f:
        f.write('index  wavelength  spectrum    dev signalToNoise \n')
        for i in range(len(wavelength)):
            for j in range(len(wavelength[i])):
                f.write(f'{i}   {wavelength[i][j]}  {spectrum[i][j]}    {dev[i][j]} {stn[i][j]}\n')



def make_csv(path, wavelength, spectrum, dev, stn):
    with open(path, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['index', 'wavelength', 'spectrum', 'dev', 'signalToNoise'])
        for i in range(len(wavelength)):
            for j in range(len(wavelength[i])):
                writer.writerow([i, wavelength[i][j], spectrum[i][j], dev[i][j], stn[i][j]])
def make_json(path, wavelength, spectrum, dev, stn):
    data = []
    for i in range(len(wavelength)):
        for j in range(len(wavelength[i])):
            data.append({
                'index': i,
                'wavelength': wavelength[i][j],
                'spectrum': spectrum[i][j],
                'dev': dev[i][j],
                'signalToNoise': stn[i][j]
            })
    
    with open(path, mode='w') as f:
        json.dump(data, f, indent=4)

def make_fits(path, wavelength, spectrum, dev, stn):
    # 将数据转换为 NumPy 数组
    wavelength2 = np.array(wavelength).flatten()
    spectrum = np.array(spectrum).flatten()
    dev = np.array(dev).flatten()
    stn = np.array(stn).flatten()
    index = []
    for i in range(len(wavelength)):
        for j in range(len(wavelength[i])):
            index.append(i)  # 每个子数组的索引

    index = np.array(index)

    # 创建 FITS 表
    col1 = fits.Column(name='index', format='K', array=index)
    col2 = fits.Column(name='wavelength', format='E', array=wavelength2)
    col3 = fits.Column(name='spectrum', format='E', array=spectrum)
    col4 = fits.Column(name='dev', format='E', array=dev)
    col5 = fits.Column(name='signalToNoise', format='E', array=stn)

    cols = fits.ColDefs([col1, col2, col3, col4, col5])
    tbhdu = fits.BinTableHDU.from_columns(cols)

    # 写入 FITS 文件
    tbhdu.writeto(path, overwrite=True)

if __name__=='__main__':
    path='datas/20240203_0071/SDCH_20240203_0071.spec_a0v.fits'
    path='datas/20240203_0071/SDCK_20240203_0071.spec_a0v.fits'

    wavelength,spectrum=get_data(path=path)
    var=get_var(path=path)
    dev=var**0.5

    stn=spectrum/dev

    # make_txt('code/outcome/SDCK_20240203_0071.txt',wavelength,spectrum,dev,stn)
    # make_csv('code/outcome/SDCK_20240203_0071.csv',wavelength,spectrum,dev,stn)
    # make_json('code/outcome/SDCK_20240203_0071.json',wavelength,spectrum,dev,stn)
    make_fits('code/outcome/SDCK_20240203_0071.fits',wavelength,spectrum,dev,stn)

    
