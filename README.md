# 2025_early_research
啊啊啊啊啊啊啊
# 2025年度早期研究项目

## 项目简介

本项目是一个天文光谱数据分析研究项目，主要专注于棕矮星Coconuts-2a（Brown Dwarfs）和低质量恒星的光谱特征分析。项目包含了数据处理、模型构建、结果可视化等完整的研究流程。反正蛮复杂的。




## 文件结构

2025\_early\_research/  
│  
├── .gitattributes          # Git 属性配置  
├── .gitignore              # Git 忽略规则  
├── .vscode/                # VS Code 工作区设置  
│  
├── README.md               # 项目说明（本文件）  
│  
├── code/                   # 核心代码  
│   ├── \_\_init\_\_.py  
│   ├── .ipynb\_checkpoints/  
│   ├── \_\_pycache\_\_/  
│   ├── outcome/            # 运行结果  
│   ├── part\_2/            # 第二阶段代码  
│   │  
│   ├── 数据处理脚本  
│   │   ├── data1.py  
│   │   ├── data2.py  
│   │   ├── data3\_download\_btsettl.py   # 下载 BT-Settl 模型  
│   │   ├── data4.py  
│   │   ├── data5.py  
│   │   ├── data6\_download\_phoenix.py  # 下载 Phoenix 模型  
│   │   └── data7\_download\_IRTF.py     # 下载 IRTF 模板  
│   │  
│   ├── 可视化绘图脚本  
│   │   ├── plot1读取光谱数据.py  
│   │   ├── plot2\_plot\_all\_only\_one\_color.py  
│   │   ├── plot3\_plot\_all\_with\_color.py  
│   │   ├── plot4.py  
│   │   ├── plot5.py  
│   │   ├── plot6\_plot\_color\_and\_noise.py  
│   │   ├── plot7.py  
│   │   ├── plot8.py  
│   │   ├── plot9.py  
│   │   ├── plot10.py  
│   │   ├── plot11\_interp\_main1.py  
│   │   ├── plot11\_interp\_main2.py  
│   │   ├── plot11\_interp\_main3.py  
│   │   ├── plot12\_compare\_IRTF.py  
│   │   ├── plot13\_compare\_single\_IRTF.py  
│   │   └── plot14\_compare\_2IRTF.py  
│   │  
│   ├── 工具脚本  
│   │   ├── readfile.py  
│   │   ├── readshape.py  
│   │   ├── synphot1.py  
│   │   ├── temp.py  
│   │   ├── synphot2.ipynb  
│   │   └── synphot3.ipynb  
│   │  
│   └── .githubignore  
│  
├── datas/                  # 观测与模板数据  
│   ├── .githubignore  
│   └── 20240203\_0071/     # 2024-02-03 观测数据  
│  
├── models/                 # 大气模型  
│   ├── HiRes/              # 高分辨率模板  
│   ├── bt-settle/          # BT-Settl 模型  
│   └── other\_V/           # 其他 V 波段模型  
│  
├── reference/              # 参考文献  
│   ├── .githubignore  
│   ├── Cushing\_2008\_ApJ\_678\_1372.pdf  
│   ├── Zhang\_2021\_ApJL\_916\_L11.pdf  
│   ├── Zhang\_2025\_AJ\_169\_9.pdf  
│   └── bd-intro/           # 棕矮星简介资料  
│  
├── caiyan/                 # 备用分析脚本  
├── infomation/             # 项目记录与说明  
└── models/                 # 备用模型文件  



## 主要功能模块

### 1. 数据处理模块 (`code/data*.py`)
- 天文光谱数据的预处理和分析
- 支持多种数据格式（FITS、ASCII等）
- 自动下载和更新标准模型数据（BT-Settl、Phoenix、IRTF）

### 2. 可视化模块 (`code/plot*.py`)
- 光谱数据的可视化展示
- 多波段光度分析
- 颜色-星等图绘制
- 模型与观测数据的对比分析

### 3. 合成光度分析 (`code/synphot*.py/ipynb`)
- 合成光度计算
- 滤波器响应分析
- Jupyter Notebook交互式分析

### 4. 工具函数 (`code/read*.py`)
- 数据文件读取
- 辅助分析函数

## 数据说明

- **观测数据**：包含2024年2月3日的观测数据（目录`datas/20240203_0071/`）
- **模型数据**：包括高分辨率大气模型、BT-Settl模型等
- **参考数据**：IRTF标准库、Phoenix模型库等

## 依赖环境

- Python 3.12
- 主要科学计算库：numpy, scipy, matplotlib, astropy
- 天文专用库：specutils, synphot, astroquery
- Jupyter Notebook环境

## 使用说明

1. **环境配置**：
   ```bash
   pip install numpy scipy matplotlib astropy specutils synphot astroquery jupyter 
   ```
   实则远远不够


## 处理流程

1.使用code/plot04_inter_record.py来记录不同探测器选择的重合区域
2.使用code/part_2/plot04_interp_method01.py和code/part_2/plot04_interp_method02.py来拼接数据
3.运行code/part_2/plot03_compare_combines.py对比两种拼接的方法
4.运行code/plot12_compare_IRTF.py将拼接结果conbine到各个IRTF上进行对比,然后运行code/outcome/IRTF_compare/pngToPDF.py制作到一个PDF里
5.（这一步无需IRGANS）把IRTF用根据星等乘一个倍数，把它变成‘真实的’数据。
6.使用code/plot13_compare_single_IRTF.py得到把IGRANS 乘到上述真实数据上的因子。#留这一步的图
7.根据这样因子把IGRANCE数据也变成“真实的”,存在code/part_2/data_for_part2/H.txt和code/part_2/data_for_part2/K.txt里面
8.使用code/part_2/cut01.py和cut02.py 对bt-settle数据进行降采样，裁剪和放在同一波长空间，结果存在models/bt-settle_H和K里面。
  画一下“bt-settle”处理前后的对比图像。
9.计算ck和gk
10.进行vr和vsini修正


## 日志 

10.15更新
记了那个重复区域的波长范围，记录在code/part_2/outcome_for_part2/record_wave_H（K）.txt里面

11.20更新
plot_03的中间过程存在code/outcome/plot03_middle
留第六步的图在code/outcome/plot03_middle
bt-settle 前后对比图,选择models/bt-settle_H/bt-settl_1907.dat_cut.txt
    使用code/part_2/plot05_btsettle_compare.py，结果存在code/part_2/outcome_for_part2/bt_settle_compare
单单做一次H波段和K波段的ck，gk。存在code/part_2/outcome_for_part2/H_ckgk.xlsx  code/part_2/outcome_for_part2/K_ckgk.xlsx


vsini,projected rotational velocity
 vr

11.26更新

bt-settle处理前后的图，仅在h，k附近画。使用code/part_2/plot06_btsettle_compare.py，结果在code/part_2/outcome_for_part2/middle_figure/btsettle_H_compare.png（k）

更改了一个bug，5.步骤没有scale error

比较模型和拟合前后的数据，绘制上部分2光谱，下部分O-C.代码(code/part_2/plot07_OC.py)，结果在code/part_2/outcome_for_part2/middle_figure/OC_plot_HK.png

进行vr，vsini修正，修正演示在code/part_2/plot08_vr_vsini_single.py，修正处理单片在code/part_2/plot08_single.py
全部处理使用code/part_2/plot08_all_ck_gk_modified.py，最后结果在code/part_2/outcome_for_part2、ck_gk_vr_vsini_modified.xlsx里面


然后做一个barycentric correction   如果shift_data为正,把data右移这个值
barycentric correction Barycentric correction (m/s):  6432.836292164912
    使用code/part_2/data3_barycentric_correction.py进行，结果存在code/part_2/data_for_part2/H_BC.txt,以后使用这个修正的数据（K）


bt_settle需要修正air_to_vacuum
    修正处理单片在code/part_2/plot08_single_air_bc.py
    保存文件到： models/bt-settle_H_vr_vsini/bt-settl_131.dat.txt_vr0_vsini10.txt 发现这个文件画一个OC H段趋势不符合，但吸收线基本位置对上了。
    修正处理code/part_2/plot08_all_ck_gk_modified_air_bc.py
    
    

写一写做了哪些事情，最好用英文写
下一次暂定1.14

1.13:
将一部分函数使用c实现，函数存在code/part_2/func_export.so
主要研究了一些针对bt-settle模型的并行运算，使用code/part_2/paraller_02.py，结果存在code/part_2/outcome_for_part2/ck_gk_vr_vsini_modified_BC_paraller.xlsx





1.14会议
1.画有vr和vsini之后的O-C，   写成函数（第一优先级）
2.重复只分别在H和K的和H+K

3.使用另外模型，H，K，H+K
4.https://www.fdr.uni-hamburg.de/record/17935 模之后的型


5.加入测光点，研究如何星等→流量。

6.pymultinest（第二优先级）
v=写一写做了哪些事情，最好用英文写


1.28更新

code/part_2/plot07_OC_2.py是最新的OC画法，包含了vr，vsini等,code/part_2/outcome_for_part2/middle_figure/OC_plot_HK_combined.png是结果。
code/part_2/pymultinest_01_help.py做了文件参数→名称的映射，存在文件夹/models/bt-settle/map/下
code/part_2/pymultinest_01_help2.py则可以利用上述结果做方阵检查，发现alpha缺少太多，无法形成方阵

code/part_2/pymultinest_01_test.py准备好了全部数据，存在code/outcome/bt-settle_full.npy


OC展现，单独做H或K，加label表示模型参数是什么，做2张图，最近尽快做完。

对于alpha，应该检查是否能够固定到同样一个值，如0.0

找光谱的单位，确认flux的unit，参考code/part_2/cal02_get_c_average.py

明天画O-C，留nmomonixed,明天交，下周四2.5晚上8点见面



meta和alpha的参数固定为
meta_grid_points = np.array( [ -0.5 ] )  #组合2
alpha_grid_points = np.array( [ 0.2 ] )
c
重做了，code/part_2/pymultinest_01_test.py
结果存在code/part_2/outcome_for_part2/pymultinest_outcome/bt-settle_points.npy和bt-settle_full.npy
共44个模型
code/part_2/pymultinest_02_test.py也跑出来了


2.5还是希望meta是一个guid，但alpha对应内嵌固定下来
logg 3-5.5
raw_wl_mod,raw_fl_mod=get_cut(file_path)  #先转换真空波长，再降低分辨率

最后再存三套模型矩阵，H，K，H+K

log likelyhood#再额外插值，再把模型wave转到数据wave上

学习corner.py，画出code/part_2/outcome_for_part2/pymultinest_outcome/bt-settle-test-post_equal_weights.dat的分布，画一个7*7的图，H，K，H+K都画，

看那一行对应loglikehood最大，即为最大似然值，画出插值后的最好模型和数据对比图

考虑别的2套模型

之后考虑加入covariance matrix


3.11拿到了新数据，准备重做上述工作。

3.12  H band可能还是有问题，2个月后拿一个新的数据对比，以后只分析K band
pymultinest重做一版只有K band的，使用新数据，修改代码名称
重新整理新数据的代码的结构，结果的结构，

对于pymultinest，new_grid_point Teff取log10  H band 改K band再跑一遍，然后把数据微信发上去，保留数据结构，写一下如何改路径
考虑pymultinest加入datas/coconuts-2A-SED.txt的内容
再做一个merge，把IGRANS的数据也降采样到2000、6000再和IRTF对比
去http://svo2.cab.inta-csic.es/svo/theory/fps/index.php?id=GAIA/GAIA0.G 找滤光片

3.23
重做了新的数据，bc不变，数据存在修正后的数据已保存到 code/part3_new_data/datas/H_BC.txt
下面针对新数据的K波段进行chi2拟合,修改成了只针对K波段的存在 code/part3_new_data/outcomes/ck_gk_vr_vsini_modified.xlsx

3.26
pymultinest采样率2000live points
1.针对pymultinest作图 模型和数据比较图，使用maximum对应的参数来画code/part3_new_data/step10_pymultinest/1/stats.json
根据模型的参数弄出一个光谱，并保存,K和H+K分别作图,微信
2.后面再画corner.py

分析IGRINS+测光

datas/coconuts-2A-gaia-xp.txt,单位：纳米，
datas/coconuts-2A-SED.txt，单位A
用SED前5个filter算出gaia xp对应的flux，每一个波段算一个比值，使用这个比值的average乘上gaia，得到最终纠正过的光谱
把gaia-xp和K band合在一起做一个pymultinest，问一下gaia-xp的resolvtion，需要针对gaia-xp做一个新的npy模型
希望把gaia-xp和K band+测光数据都加进去，需要三套不同分辨率的code/part3_new_data/step10_pymultinest/bt-settle_full.npy，
测光对应的分辨率设为100，

4月9号
针对第三份数据再重做

4.14根据xp制作了新的code/part3_new_data/datas/coconuts-2A-gaia-xp_vegamag.txt，
并以此制作新的code/part3_new_data/step10_pymultinest/bt-settle_full_SED.npy

4.20code/part3_new_data/step03_2_compare_with_template.py做了新旧数据和M3的对比
code/part3_new_data/step10_pymultinest/pymultinest_04_get_data.py做了最似然模型和数据的对比，用了取巧的方法


4.23可以做一个SED+H+K模型和数据的对比

code/part3_new_data/step10_pymultinest/3/bt-settle-test-post_equal_weights.dat 前面列对应参数，最后一列对应likelyhood，从这个文件里面可以自动读取出最大的likelyhood和对应的参数
然后把数据都载入进去
然后把最大似然的模型参数填入griddata函数，然后填入R，vr，vsini，在插值之前保存一下model。插值后保存模型数据，针对H和K可以做OC图
可以把模型在每一个波段的测光也计算出来，最终画model+SED+HK，下图为测光-model，H-model，K-model


加入SED：再弄一套npy，波长范围取决于SED 0.3微米-6微米，resolution 可以100或50，然后拿模型数据生成一个测光
本周：加测光，了解模型哪里仍有问题；找到logg的合理范围，使用演化模型，读文章section5
做第四版数据，看看有没有斜率问题
5.7做第四版数据,仍然有斜率问题，但似乎更接近m1？

6.2进行HiRes模型
分辨率10e6数量级   该模型的：BUNIT   = 'erg/s/cm^2/cm'，其他地方：BUNIT   = 'erg s-1 cm-2 micron-1' / Flux Units ,为真空波长，无需额外处理


6.4再跑一遍HiRes的，改文件名称，画图。


新数据处理：MAGELLAN /fire
模式1.分辨率300，0.8微米-2.5微米 不存在order问题
模式2.分辨率6000  
pypeit
先学习教程，然后再处理数据
下载
https://www.dropbox.com/scl/fo/1i9f21qwcd8ft7ospxxve/AJ9GG-e3NQGYbofj_UF5y3I?rlkey=kl0gaprlp6f1cgl4hqv9hqk7y&dl=0

红框框起来的数据是需要的
74-77   COCONUTS-2A: science target
78         NeArNe: wavelength calibration for COCONUTS-2A
79-86   HD62139: A0V telluric standard star
87         NeArNe: wavelength calibration for HD62139

magellan_fire
MagellanFIREEchelleSpectrograph
MAGELLAN
FIRE

pypeit_identify Calibrations/Arc_A_0_DET01.fits Calibrations/Slits_A_0_DET01.fits.gz   --lamps NeI,ArI -s

telluric correction

7.29更新
pypeit→fluxing→coadd 1D→telluric correction

7.30    修改calib_id， science 0110  standard 2332  其它也用ABBA   所有标准星和目标单独分开处理
 把8个标准星都flux处理，看看响应函数,  可以多给，没必要   
 可以针对fire数据处理步骤写一个note
 下周开会

 https://iopscience.iop.org/article/10.3847/1538-4357/ad06ba/pdf
 2.1    研究pypeit_flux_setup
 看看https://github.com/pypeit/PypeIt-development-suite的

10.6
得到了fire数据见fire/coadded_spectrum.txt
接下来对比fire，IGRINS,ADleo数据，1.52-1.7






