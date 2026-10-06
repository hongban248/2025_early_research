#这个脚本用来创建HiRes数据集的映射文件
import os
import json
import re

model_dir='models/HiRes'
map_dir=os.path.join(model_dir,'map')

if not os.path.exists(map_dir):
    os.makedirs(map_dir)
#创建映射文件

for files in os.listdir(model_dir):
    if files.endswith('.fits'):
        file_path=os.path.join(model_dir,files)
        #提取文件名中的信息
        #print(file_path,files)
        pattern = r'lte(\d{5})-([\d.]+)([+-]\d+\.?\d*)(?:\.Alpha=([+-]?\d+\.?\d*))?'

       # files='models/HiRes/lte04600-3.50+0.5.PHOENIX-ACES-AGSS-COND-2011-HiRes.fits'
        match = re.search(pattern, files)
        if match:
            teff  = match.group(1)           # 05000
            logg  = match.group(2)           # 5.50
            meta  = match.group(3)           # -0.5
            alpha = match.group(4) or "0"    # -0.20，无则默认 "0"

            teff=int(teff)
            logg=float(logg)
            meta=float(meta)
            alpha=float(alpha)
            
            print(f"Teff: {teff}, logg: {logg}, meta: {meta}, Alpha: {alpha}")
            #aaaa
        else:
            print(f"文件名 {files} 不匹配预期的模式。")
            continue
        map_name=f'HiRes_teff{teff}_logg{logg}_meta{meta}_alpha{alpha}.map'
        map_path=os.path.join(map_dir,map_name)
        #创建映射文件
        with open(map_path,'w') as f:
            f.write(f"{file_path}\n")