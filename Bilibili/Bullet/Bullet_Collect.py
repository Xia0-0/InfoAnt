'''
用简单化的方法爬取B站视频数据,视频前加个i,直接用别人的接口
'''
#导入模块
import requests
import json
import re  #正则表达式模块

#发送请求
url="https://api.bilibili.com/x/v1/dm/list.so?oid=1512400473"
headers ={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
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
with open('弹幕.txt',mode='a',encoding='utf-8') as f:
    f.write('\n\n\n弹幕数据：\n\n')
    f.write(comments)

#输出状态码和响应内容
print(response.status_code)  # 输出状态码，200表示成功
print(html_data)  



