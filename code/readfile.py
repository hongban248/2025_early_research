from astropy.io import fits
import argparse

def read_fits_header(file_path):
    """
    读取FITS文件的头信息并打印。
    
    参数:
        file_path (str): FITS文件的路径。
    """
    try:
        # 打开FITS文件
        with fits.open(file_path) as hdul:
            # 获取主扩展的头信息
            header = hdul[0].header
            print("FITS文件头信息：")
            print(header)
            # seen_comments = set()  # 用于记录已经打印过的注释内容
            # for key in header.keys():
            #     if key in ['COMMENT', 'HISTORY']:
            #         # 如果是注释或历史记录，直接打印
            #         for comment in header[key]:
            #             if comment not in seen_comments:
            #                 print(f"{key}: {comment}")
            #                 seen_comments.add(comment)
            #     else:
            #         # 打印其他键值对
            #         print(f"{key}: {header[key]}")
            
    except FileNotFoundError:
        print(f"错误：文件 {file_path} 未找到。")
    except Exception as e:
        print(f"读取文件时发生错误：{e}")

if __name__ == "__main__":
    # 创建命令行参数解析器
    # parser = argparse.ArgumentParser(description="读取FITS文件的头信息。")
    # parser.add_argument("file_path", type=str, help="FITS文件的路径。")
    # args = parser.parse_args()

    path='datas/20240203_0071/SDCH_20240203_0071.spec_a0v.fits'
    # 调用函数读取FITS文件头信息
    read_fits_header(path)
