'''
用简单化的方法爬取B站视频数据,视频前加个i
'''
#导入模块
import requests
import json
import re

#发送请求
url="https://api.bilibili.com/x/v1/dm/list.so?oid=1512400877"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://www.bilibili.com/'
}#设置请求头


#获取响应内容    
response=requests.get(url,headers=headers)

#数据处理
response.encoding='utf-8' # 转码
html_data=response.text

pattern = '<d p=".*?">(.*?)</d>'  #正则表达式匹配,非贪婪
content_list=re.findall(pattern,html_data)


comments='\n'.join(content_list) #列表合并字符串

#输出结果
with open('弹幕.txt','w',encoding='utf-8') as f:
    f.write(comments)

#输出状态码和响应内容
print(response.status_code)  # 输出状态码，200表示成功
print(response.text[:500])   # 输出前500个字符的响应内容，检查是否返回了数据




