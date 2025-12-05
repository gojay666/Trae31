import json

# 原始请求头文本
raw_headers = """accept
 text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
 accept-encoding
 gzip, deflate, br, zstd
 accept-language
 zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
 cache-control
 max-age=0
 connection
 keep-alive
 cookie
 nouse=nouse; costumerid=costumeridprifixgKCNaUwwk; costumeridprifixgKCNaUwwk=0; ValidateNumber="n1mCFEcBtjY="
 host
 www.scpublic.cn
 referer
 `https://www.scpublic.cn/` 
 sec-ch-ua
 "Chromium";v="142", "Microsoft Edge";v="142", "Not_A Brand";v="99"
 sec-ch-ua-mobile
 ?0
 sec-ch-ua-platform
 "Windows"
 sec-fetch-dest
 document
 sec-fetch-mode
 navigate
 sec-fetch-site
 same-origin
 sec-fetch-user
 ?1
 upgrade-insecure-requests
 1
 user-agent
 Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0"""

def parse_headers_to_json(raw_text):
    """解析原始请求头文本并转换为JSON格式"""
    # 移除首尾空白
    raw_text = raw_text.strip()
    
    # 分割成键值对行
    lines = raw_text.split('\n')
    headers_dict = {}
    
    i = 0
    while i < len(lines):
        # 获取键（去除空白）
        key = lines[i].strip()
        if key:
            # 下一行是值
            i += 1
            if i < len(lines):
                value = lines[i].strip()
                # 移除可能的反引号
                value = value.replace('`', '')
                headers_dict[key] = value
        i += 1
    
    # 转换为JSON
    headers_json = json.dumps(headers_dict, indent=2, ensure_ascii=False)
    
    return headers_json

# 执行转换
headers_json = parse_headers_to_json(raw_headers)

# 输出结果
print("=== 请求头JSON格式 ===")
print(headers_json)

# 保存到文件以便用户使用
with open('headers_output.json', 'w', encoding='utf-8') as f:
    f.write(headers_json)

print("\nJSON数据已保存到 headers_output.json 文件")
