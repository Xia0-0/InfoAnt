'''
爬取B站视频评论，模块化分工，便于之后封装
'''
#导入模块
import requests
import json
import re


#请求模块
def Get_Response(url, date):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
    'Referer': 'https://www.bilibili.com/'
    #'cookie': 'SESSDATA=; bili_jct=; DedeUserID=; DedeUserID__ckMd5=; sid=; CURRENT_FNVAL=; rpdid=; LIVE_BUVID=; CURRENT_QUALITY=; CURRENT_BLACKGAP=; bp_t_offset
}#模拟请求头 
    response= requests.get(url=url, params=date, headers=headers)
    return response



#获取模块
def Get_Content():
    
    link = "https://api.bilibili.com/x/v2/reply/wbi/main" # 请求网址
    params = {
        'oid': 1153355619,
        'type': 1,
        'mode': 3,
        'pagination_str': {'offset': ''},
        'plat': 1,
        'seek_rpid': '',
        'web_location': 1315875,
        'w_rid': 'fb5fecedefb9fbee056517e4fbc41f66',
        'wts': 1737777153
    } #查询参数

    Get_Response(url=link, date=params)#调用发送请求函数
    response= requests.get(url=link, params=params, headers=headers)
    
    JsonDate = response.json() #获取json数据
    
    # 解析数据
    replies=JsonDate['data']['replies']
    print(replies)
    return replies
    

    response.encoding = 'utf-8'  #转码
    html_data = response.text
    
    # 使用正则表达式提取弹幕内容，非贪婪匹配
    pattern = r'<d p=".*?">(.*?)</d>'
    content_list = re.findall(pattern, html_data)
    return content_list

#保存数据
def save_comments(comments):
    """保存弹幕到文件

    Args:
        comments (list): 弹幕内容列表
    """
    with open('弹幕.txt', mode='a', encoding='utf-8') as f:
        # 在文件中添加标题和空行以分隔不同批次的弹幕
        f.write('\n\n\n弹幕数据：\n\n')
        # 将列表中的弹幕内容写入文件，每行一个弹幕
        f.write('\n'.join(comments))

# 主函数
def main():date
    """主函数，用于执行爬取弹幕的流程"""
    url = "https://api.bilibili.com/x/v2/reply/wbi/main?oid=1153355619&type=1&mode=3&pagination_str=%7B%22offset%22:%22%22%7D&plat=1&seek_rpid=&web_location=1315875&w_rid=8f4cfe108dc09524609408b385fdb8f1&wts=1737772836"
    response = Get_Response(url, date)
    comments = process_response(response)
    save_comments(comments)
    

    # 输出状态码和响应内容，用于调试和检查请求是否成功
    print(response.status_code)  # 输出状态码，200表示成功
    print(response.text)

    
    
    
    
if __name__ == "__main__":
    Get_Content()
    
    '''