# 2025_early_research
啊啊啊啊啊啊啊
# 2025年度早期研究项目

## 项目简介

本项目是一个天文光谱数据分析研究项目，主要专注于棕矮星（Brown Dwarfs）和低质量恒星的光谱特征分析。项目包含了数据处理、模型构建、结果可视化等完整的研究流程。

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


