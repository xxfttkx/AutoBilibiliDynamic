import os
import requests
import hashlib
from dotenv import load_dotenv

load_dotenv()  # 自动读取 .env 文件

SESSDATA = os.getenv("SESSDATA")
BILI_JCT = os.getenv("BILI_JCT")

if not SESSDATA or not BILI_JCT:
    print("请检查环境变量 SEESDATA 或 BILI_JCT 是否设置正确")
    exit(1)
else:
    print("环境变量 SEESDATA 和 BILI_JCT 已设置")

# GitHub 上图片的原始链接（Raw）
img_url = "https://raw.githubusercontent.com/xxfttkx/splatoon_SalmonRun_weapons/main/output.png"

# 本地路径
local_img = "output.png"
temp_img = "temp.png"

cookies = {
    "SESSDATA": SESSDATA,
    "bili_jct": BILI_JCT,
}
headers = {
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://t.bilibili.com/',
    'Origin': 'https://t.bilibili.com/',
}

# 下载图片为 temp.png
r = requests.get(img_url)
with open(temp_img, 'wb') as f:
    f.write(r.content)

# 计算 MD5 用于比较是否相同
def file_md5(path):
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

need_update = False
if not os.path.exists(local_img):
    need_update = True
else:
    if file_md5(local_img) != file_md5(temp_img):
        need_update = True

# 如果需要更新
if need_update:
    print("图片不同，准备上传到 B 站...")
    # 覆盖 output.png
    os.replace(temp_img, local_img)

    # Step 1: 上传图片
    upload_url = "https://api.bilibili.com/x/dynamic/feed/draw/upload_bfs"
    files = {
        'file_up': open(local_img, 'rb')
    }
    data = {
        'category': 'daily',
        'csrf': cookies['bili_jct'],
    }
    upload_resp = requests.post(upload_url, headers=headers, cookies=cookies, files=files, data=data)
    print(upload_resp.status_code)
    print(upload_resp.text)  # 打印原始响应内容
    image_url = upload_resp.json()['data']['image_url'] 
    print("上传成功，图像 URL:", image_url)

    # Step 2: 发布动态
    post_url = "https://api.bilibili.com/x/dynamic/feed/create/dyn?csrf="+cookies['bili_jct']
    dyn_req = {
        'scene': 2,  # 图文
        'content': {
            'contents':[
                {
                    "raw_text": "早上好",
                    "type": 1,
                    "biz_id": ""
                }
            ]
        },
        'pics': [{'img_src':image_url}],
    }
    payload = {
        'dyn_req':dyn_req
    }
    post_resp = requests.post(post_url, headers=headers, cookies=cookies, json=payload)
    print("发布结果：", post_resp.json())
else:
    print("图片未变，无需上传。")