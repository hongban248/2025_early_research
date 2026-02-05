import os
import numpy as np


def parament_to_filename(teff, logg, meta, alpha, mapfilepath="models/bt-settle/map"):
    """
    将给定的teff、logg、meta和alpha参数转换为对应的txt文件名格式。
    
    参数:
        teff (float): 有效温度。
        logg (float): 表面重力。
        meta (float): 金属丰度。
        alpha (float): α元素丰度。舍弃
    """
    map_name="btsettl_T{:.0f}_lg{:.1f}_m{:.1f}_a{:.1f}.map".format(teff, logg, meta, alpha)
    map_file_path=os.path.join(mapfilepath, map_name)
    #print(map_file_path)
    if os.path.exists(map_file_path):
        f=open(map_file_path,'r')
        text=f.readlines()
        f.close()
        file_path=text[0].strip()
        print("存在的文件名为：", map_file_path)
        return file_path
    else:
        print("文件不存在：", map_file_path)
        return None

if __name__ == "__main__":
    # # 示例参数
    # teff = 3600
    # logg = 5.5
    # meta = -0.5
    # alpha = 0.2

    # # 获取对应的文件名
    # filename = parament_to_filename(teff, logg, meta, alpha)
    # if filename:
    #     print("对应的文件名为：", filename)
    #方阵检查
    teff_grid_points = np.array( list(np.arange(3000, 4001,100)) )
    logg_grid_points = np.arange(4, 5.51, 0.5)


    meta_grid_points = np.array( [0.0, 0.3,0.5] )  #组合1
    alpha_grid_points = np.array( [0.0] )#应该给一个固定值


    meta_grid_points = np.array( [ -1] )  #组合3
    alpha_grid_points = np.array( [0.4] )


    #组合2(之前工作最接近)
    meta_grid_points = np.array( [ -0.5] )  #组合2
    alpha_grid_points = np.array( [0.2] )

    


    vr_grid_points = np.array( [0.0, 2.0, 4.0] )
    vsini_grid_points = np.array( [0.0, 5.0, 10.0] )
    num_teff_points = len(teff_grid_points)
    num_logg_points = len(logg_grid_points)
    num_meta_points = len(meta_grid_points)
    num_alpha_points = len(alpha_grid_points)
    num_vr_points = len(vr_grid_points)
    num_vsini_points = len(vsini_grid_points)
    grid_point_list = []
    for teff in teff_grid_points:
        for logg in logg_grid_points:
            for meta in meta_grid_points:
                for alpha in alpha_grid_points:
                    a=parament_to_filename(teff, logg, meta,alpha)
                    for vr in vr_grid_points:
                        for vsini in vsini_grid_points:

                            grid_point_list.append([teff, logg, meta, alpha, vr, vsini])

