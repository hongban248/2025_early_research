# 2025_early_research
啊啊啊啊啊啊啊
# 2025年度早期研究项目

## 项目简介

本项目是一个天文光谱数据分析研究项目，主要专注于棕矮星（Brown Dwarfs）和低质量恒星的光谱特征分析。项目包含了数据处理、模型构建、结果可视化等完整的研究流程。

## 文件结构
2025_early_research/
│
├── .gitattributes          # Git属性配置文件
├── .gitignore             # Git忽略文件配置
├── .vscode/               # VS Code编辑器配置目录
│
├── README.md              # 项目说明文件（本文件）
│
├── code/                  # 核心代码目录
│   ├── init.py        # Python包初始化文件
│   ├── .ipynb_checkpoints/ # Jupyter Notebook检查点
│   ├── pycache/       # Python缓存目录
│   ├── outcome/           # 输出结果目录
│   ├── part_2/            # 第二部分代码目录
│   │
│   ├── 数据处理脚本
│   │   ├── data1.py       # 数据预处理脚本1
│   │   ├── data2.py       # 数据预处理脚本2
│   │   ├── data3_download_btsettl.py  # BT-Settl模型数据下载
│   │   ├── data4.py       # 数据预处理脚本4
│   │   ├── data5.py       # 数据预处理脚本5
│   │   ├── data6_download_phoenix.py  # Phoenix模型数据下载
│   │   └── data7_download_IRTF.py     # IRTF数据下载脚本
│   │
│   ├── 可视化绘图脚本
│   │   ├── plot1读取光谱数据.py      # 光谱数据读取
│   │   ├── plot2_plot_all_only_one_color.py  # 单色绘图
│   │   ├── plot3_plot_all_with_color.py      # 彩色绘图
│   │   ├── plot4.py       # 基础绘图4
│   │   ├── plot5.py       # 基础绘图5
│   │   ├── plot6_plot_color_and_noise.py     # 颜色与噪声分析
│   │   ├── plot7.py       # 高级绘图7
│   │   ├── plot8.py       # 高级绘图8
│   │   ├── plot9.py       # 高级绘图9
│   │   ├── plot10.py      # 高级绘图10
│   │   ├── plot11_interp_main1.py      # 插值分析1
│   │   ├── plot11_interp_main2.py      # 插值分析2
│   │   ├── plot11_interp_main3.py      # 插值分析3
│   │   ├── plot12_compare_IRTF.py      # IRTF数据比较
│   │   ├── plot13_compare_single_IRTF.py  # 单IRTF比较
│   │   └── plot14_compare_2IRTF.py     # 双IRTF比较
│   │
│   ├── 工具脚本
│   │   ├── readfile.py    # 文件读取工具
│   │   ├── readshape.py   # 形状读取工具
│   │   ├── synphot1.py    # 合成光度工具1
│   │   ├── temp.py        # 临时工具脚本
│   │   ├── synphot2.ipynb # 合成光度分析Notebook2
│   │   └── synphot3.ipynb # 合成光度分析Notebook3
│   │
│   └── 其他文件
│       └── .githubignore  # Git忽略配置
│
├── datas/                 # 数据目录
│   ├── .githubignore      # Git忽略配置
│   └── 20240203_0071/     # 观测数据目录
│
├── models/                # 模型目录
│   ├── HiRes/            # 高分辨率模型
│   ├── bt-settle/        # BT-Settl大气模型
│   └── other_V/          # 其他V波段模型
│
├── reference/             # 参考文献目录
│   ├── .githubignore      # Git忽略配置
│   ├── Cushing_2008_ApJ_678_1372.pdf     # Cushing et al. 2008论文
│   ├── Zhang_2021_ApJL_916_L11.pdf       # Zhang et al. 2021论文
│   ├── Zhang_2025_AJ_169_9.pdf           # Zhang et al. 2025论文
│   └── bd-intro/         # 棕矮星介绍资料
│
├── caiyan/               # 其他分析目录
├── infomation/           # 项目信息目录
└── models/               # 模型文件目录



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
   实则远远不够


