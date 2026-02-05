import requests
import re
from bs4 import BeautifulSoup

url='https://svo2.cab.inta-csic.es/theory/newov2/index.php'

header={
    "user-agent":'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',

}

data={
    'params[bt-settl][teff][min]':2000,
    'params[bt-settl][teff][max]':5000,
    'params[bt-settl][logg][min]':3,
    'params[bt-settl][logg][max]':5.5,
    'params[bt-settl][meta][min]':-1,
    'params[bt-settl][meta][max]':0.5,
    'nres':'all',
    'boton':'Search',
    'reqmodels[]':'bt-settl'
}
#
res=requests.post(url=url,headers=header,data=data)
#print(res.text)

soup = BeautifulSoup(res.text, 'html.parser')
fids = set(re.findall(r'fid=(\d+)', str(soup)))

tids=sorted(map(int, fids))
# 结果
print(tids,len(tids))   # -> [13733, 13744, 13745, 13756]

for tid in tids:
    url = f'https://svo2.cab.inta-csic.es/theory/newov2/ssap.php?model=bt-settl&fid={tid}&format=ascii'
    

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(url,  headers=headers, timeout=30)
    r.raise_for_status()          # 若 404/503 会抛异常

    with open(f"/mnt/disk1/myresource/2023早期科研/models/bt-settl_{tid}.dat.xml", "wb") as f:
        f.write(r.content)

    print(f"下载成功，已保存为 bt-settl_{tid}.dat.xml")