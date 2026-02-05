import requests
import re
from bs4 import BeautifulSoup


header={
    "user-agent":'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',

}

url='https://phoenix.astro.physik.uni-goettingen.de/wp-content/plugins/phxweb/ajax/request.php?Type=HiRes&Teff=5000&logg=4.5&FeH=0.0&alphaM=0.0'

datas={
    'Type':'HiRes',
    'Teff':'5000',
    'logg':'4.5',
    'FeH':'+0.0',
    'alphaM':'+0.0'
}

res=requests.get(url=url,headers=header)

#print(res.text)
ftp_links = re.findall(r'ftp://[^\s"]+\.fits', res.text)
#print(ftp_links)

# 批量替换所有ftp链接为https+data路径
https_links = [
    link.replace(
        "ftp://phoenix.astro.physik.uni-goettingen.de/HiResFITS/",
        "https://phoenix.astro.physik.uni-goettingen.de/data/HiResFITS/"
    ) for link in ftp_links
]

# 输出所有https链接

need_link = https_links[0]

# 下载need_link指向的文件并保存到models/HiRes/目录下
import os
save_dir = os.path.join("models", "HiRes")
os.makedirs(save_dir, exist_ok=True)
filename = need_link.split("/")[-1]
save_path = os.path.join(save_dir, filename)

file_res = requests.get(need_link, stream=True)
with open(save_path, "wb") as f:
    for chunk in file_res.iter_content(chunk_size=8192):
        if chunk:
            f.write(chunk)
print(f"已保存: {save_path}")