import os
import sys

def extract_values_from_txt(file_path):
    """
    从指定的txt文件中提取teff、logg、meta和alpha的数值。
    
    参数:
        file_path (str): txt文件的路径。
    
    返回:
        dict: 包含teff、logg、meta和alpha的字典。
    """
    # 初始化一个字典来存储提取的数值
    values = {
        "teff": None,
        "logg": None,
        "meta": None,
        "alpha": None
    }
    
    try:
        # 打开文件并逐行读取
        with open(file_path, "r") as file:
            for line in file:
                # 去掉行首和行尾的空白字符
                line = line.strip()
                # 检查是否包含teff
                if "teff" in line:
                    # 提取teff的数值
                    values["teff"] = float(line.split("=")[1].split("K")[0].strip())
                # 检查是否包含logg
                elif "logg" in line:
                    # 提取logg的数值
                    values["logg"] = float(line.split("=")[1].split("log")[0].strip())
                # 检查是否包含meta
                elif "meta" in line:
                    # 提取meta的数值
                    values["meta"] = float(line.split("=")[1].split('(')[0].strip())
                # 检查是否包含alpha
                elif "alpha" in line:
                    # 提取alpha的数值
                    values["alpha"] = float(line.split("=")[1].split('(')[0].strip())
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到。")
    except Exception as e:
        print(f"读取文件时发生错误：{e}")
    
    return values



if __name__ == "__main__":
    model_path="models/bt-settle"
    for filename in os.listdir(model_path ):
        if not filename.endswith(".txt"):
            continue  # 只处理txt文件
        file_path = os.path.join(model_path , filename)
        print(file_path)
        #text=open(file_path,'r').readlines()
        values = extract_values_from_txt(file_path)
        #single_data=[filename,values["teff"],values["logg"],values["meta"],values["alpha"]]

        #print(single_data)
        map_name="btsettl_T{:.0f}_lg{:.1f}_m{:.1f}_a{:.1f}.map".format(values["teff"],values["logg"],values["meta"],values["alpha"])
        print(map_name)

        # with open("models/bt-settle/map" + map_name, "w") as f:
        #     f.write(filename + "\n")
        f=open("models/bt-settle/map/"+map_name, "w")
        f.write(file_path + "\n")
        f.close()

        #break  # 仅处理第一个文件以示例展示
                        

        

