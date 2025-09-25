import requests

url='https://xiaoce.fun/api/v0/quiz/daily/guessDisease/sendMessage'

headers={
    'Cookie':'fun_ticket=fsRvug4Dd0nuEz5ARNTQ7m890AYBwWakFstSPe6x7DoN4lkRUQrkh_TfYSlWaHsYYiCYeWsDyY4dtJqVRfAQpQ; Hm_lvt_367e22c6d5b5a12a4d06746488e29b3f=1752588522,1752933318,1754313203,1754402209; Hm_lpvt_367e22c6d5b5a12a4d06746488e29b3f=1754402209; HMACCOUNT=889AA003ECD22469; SESSION=ODYxY2MwNDUtZmY0Zi00NGQ0LTgxYWYtYjNlMjM0MDRkYjIx',
    'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
}

while True:
    try:
        text1=input('请输入内容:')
        data = {
            'date': '20250805',
            'chatId': 'd2282830-7207-11f0-a545-65d77d0ebee4',
            'message': text1
        }

        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()
        #print(data)
        
        if data['success']==True:
            print(data['data']['answer'])

            with open('/mnt/disk1/myresource/2023早期科研/caiyan/story1/save.txt', 'a', encoding='utf-8') as f:
                
                f.write(f"医生：{text1} \n 患者：{data['data']['answer']}\n")
        
        
    except requests.RequestException as e:
        print("请求异常:", e)

