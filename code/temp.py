#code/outcome/bt-settle_full.npy

import numpy as np
a=np.load('code/part_2/outcome_for_part2/pymultinest_outcome/bt-settle_full.npy',allow_pickle=True)
# wl_full=a[0]
# fl_full_array=a[1:]
# print("波长数组长度：", len(wl_full))
# print("光谱数组形状：", fl_full_array.shape)
b=np.load('code/part_2/outcome_for_part2/pymultinest_outcome/bt-settle_points.npy',allow_pickle=True)
print("参数点数组形状：", b.shape)
print("前五个参数点：", b[:5])
