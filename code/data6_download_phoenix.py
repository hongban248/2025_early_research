import requests
import re
from bs4 import BeautifulSoup


header={
    "user-agent":'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',

}

teffs=['2300','2400','2500','2600','2700','2800','2900','3000',
       '3100','3200','3300','3400','3500','3600','3700','3800',
       '3900','4000','4100','4200','4300','4400','4500','4600',
       '4700','4800','4900','5000']
loggs=['3.0','3.5','4.0','4.5','5.0','5.5']
fehs=['-1.0','-0.5','0.0','+0.5','+1.0']
alphaMs=['-0.2','0.0','+0.2']

for teff in teffs:
    for logg in loggs:
        for feh in fehs:
            for alphaM in alphaMs:
                url=f'https://phoenix.astro.physik.uni-goettingen.de/wp-content/plugins/phxweb/ajax/request.php?Type=HiRes&Teff={teff}&logg={logg}&FeH={feh}&alphaM={alphaM}'

                try:
                    res=requests.get(url=url,headers=header)
                    
                    ftp_links = re.findall(r'ftp://[^\s"]+\.fits', res.text)
                    
                    if ftp_links:
                        https_links = [
                            link.replace(
                                "ftp://phoenix.astro.physik.uni-goettingen.de/HiResFITS/",
                                "https://phoenix.astro.physik.uni-goettingen.de/data/HiResFITS/"
                            ) for link in ftp_links
                        ]
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
                except Exception as e:
                    print(f"请求失败: {url} with params Teff={teff}, logg={logg}, FeH={feh}, alphaM={alphaM}. 错误: {e}")
                    continue