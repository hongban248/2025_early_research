#!/usr/bin/env python3
# make_pdf.py
import os
from PIL import Image

def pngs_to_pdf(output_pdf='merged.pdf'):
    # 1. 收集当前目录所有 .png 文件（忽略大小写）
    png_files = [f for f in os.listdir('.')
                 if f.lower().endswith('.png')]
    if not png_files:
        print('当前目录下没有 .png 文件。')
        return

    # 2. 按文件名排序（可按需要改成按修改时间等）
    png_files.sort()

    # 3. 用 PIL/Pillow 打开所有图片
    images = [Image.open(f).convert('RGB') for f in png_files]

    # 4. 第一个图作为封面，其余图片追加进去
    images[0].save(output_pdf, save_all=True, append_images=images[1:])
    print(f'已生成 {output_pdf}，共 {len(images)} 页。')

if __name__ == '__main__':
    pngs_to_pdf()
