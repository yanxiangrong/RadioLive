import json
import sys
import time

import requests

headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}

# 1. 获取所有地区列表
district_list_url = "https://apppc.cnr.cn/local/list"
resp = requests.post(district_list_url, headers=headers, json={})
resp.encoding = "utf-8"
districts = resp.json().get("liveChannelPlace", [])

# 2. 获取国家广播
national_url = "https://apppc.cnr.cn/national"
national_resp = requests.post(national_url, headers=headers, json={})
national_resp.encoding = "utf-8"
national_data = national_resp.json().get("data", {})
national_radios = [
    item
    for category in national_data.get("categories", [])
    for item in category.get("detail", [])
]


# 3. 获取所有地方广播
local_url = "https://apppc.cnr.cn/local"
all_local_radios = {}
for district in districts:
    district_id = district["id"]
    district_name = district["name"]
    local_resp = requests.post(local_url, headers=headers, json={"id": district_id})
    local_resp.encoding = "utf-8"
    local_data = local_resp.json().get("data", {})
    all_local_radios[district_name] = [
        item
        for category in local_data.get("categories", [])
        for item in category.get("detail", [])
    ]
    time.sleep(0.2)  # 防止接口被限速

# 4. 整理成需要的格式
result = [
    {
        "name": "国家广播",
        "radios": [
            {
                "name": item.get("name"),
                "description": item.get("description"),
                "full_name": item.get("other_info25"),
                "streams": [
                    {
                        "url": stream.get("url"),
                        "description": stream.get("resolution"),
                    }
                    for stream in item.get("other_info11", [])
                ],
            }
            for item in national_radios
        ],
    },
    {
        "name": "地方广播",
        "children": [
            {
                "name": district,
                "radios": [
                    {
                        "name": item.get("name"),
                        "description": item.get("description"),
                        "full_name": item.get("other_info25"),
                        "streams": [
                            {
                                "url": stream.get("url"),
                                "description": stream.get("resolution"),
                            }
                            for stream in item.get("other_info11", [])
                        ],
                    }
                    for item in radios
                ],
            }
            for district, radios in all_local_radios.items()
            if radios
        ],
    },
]

# 5. 保存，result直接输出到标准输出流
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
print("\n", file=sys.stdout)  # 确保结尾换行
print("完成！已保存为 radios.json", file=sys.stderr)
