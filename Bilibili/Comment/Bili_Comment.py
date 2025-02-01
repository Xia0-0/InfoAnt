'''问题
1.数据量少了
'''

#导入模块
import requests
import re
import time
import csv
import random
import os


# 伪装模块
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
}


"""
统一的请求函数，失败时重试 max_retries 次，每次请求超时 timeout 秒
"""
def Safe_request(url, max_retries=3, timeout=10):
    for i in range(max_retries):
        try:
            print(f"请求 URL: {url}")
            response = requests.get(url, headers=headers, timeout=timeout)
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"请求失败，状态码: {response.status_code}，重试 {i+1}/{max_retries}")
        except requests.RequestException as e:
            print(f"请求错误: {e}，重试 {i+1}/{max_retries}")
        time.sleep(2)
    return None


"""
根据视频的 BV 号获取对应的 aid
"""
def Get_video_id(bv):
    url = f'https://api.bilibili.com/x/web-interface/view?bvid={bv}'
    data = Safe_request(url, timeout=10)
    if data:
        return data.get('data', {}).get('aid')
    else:
        print("错误: 获取视频ID失败")
        return None
 

    
"""
获取二级评论，最多爬取 max_pages 页
"""
def Fetch_comment_replies(video_id, comment_id, parent_user_name, max_pages=10):
    replies = []
    for page in range(1, max_pages + 1):
        url = f'https://api.bilibili.com/x/v2/reply/reply?oid={video_id}&type=1&root={comment_id}&ps=10&pn={page}'
        data = Safe_request(url, timeout=10)
        if not data:
            print(f"错误: 第 {page} 页二级评论数据获取失败，跳过")
            break
        data_content = data.get('data')
        if not data_content:
            print(f"警告: 第 {page} 页无二级评论数据，结束爬取")
            break
        replies_list = data_content.get('replies', [])
        if not replies_list:
            print(f"警告: 第 {page} 页无二级评论，结束爬取")
            break
        for reply in replies_list:
            # 检查必须的键是否存在
            if not reply.get('member') or not reply.get('content'):
                continue
            reply_info = {
                '用户昵称': reply['member'].get('uname', ''),
                '评论内容': reply['content'].get('message', ''),
                '被回复用户': parent_user_name,
                '评论层级': '二级评论',
                '性别': reply['member'].get('sex', ''),
                '用户当前等级': reply['member'].get('level_info', {}).get('current_level', ''),
                '点赞数量': reply.get('like', 0),
                '回复时间': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(reply.get('ctime', 0)))
            }
            replies.append(reply_info)
        time.sleep(random.uniform(0.5, 1))
    return replies



"""
获取一级评论，并对每个点赞数大于5的评论获取二级回复
"""
def Fetch_comments(video_id, max_pages=500):

    comments = []
    for page in range(1, max_pages + 1):
        url = f'https://api.bilibili.com/x/v2/reply?pn={page}&type=1&oid={video_id}&sort=2'
        data = Safe_request(url, timeout=10)
        if not data:
            print(f"错误: 第 {page} 页评论数据获取失败，跳过")
            continue
        data_content = data.get('data')
        if not data_content:
            print(f"警告: 第 {page} 页没有数据，结束爬取")
            break
        replies_list = data_content.get('replies', [])
        if not replies_list:
            print(f"警告: 第 {page} 页无评论数据，结束爬取")
            break
        for comment in replies_list:
            if not comment.get('member') or not comment.get('content'):
                print("警告: 跳过不完整的评论数据")
                continue
            comment_info = {
                '用户昵称': comment['member'].get('uname', ''),
                '评论内容': comment['content'].get('message', ''),
                '被回复用户': '',
                '评论层级': '一级评论',
                '性别': comment['member'].get('sex', ''),
                '用户当前等级': comment['member'].get('level_info', {}).get('current_level', ''),
                '点赞数量': comment.get('like', 0),
                '回复时间': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(comment.get('ctime', 0)))
            }
            comments.append(comment_info)
            # 若点赞数大于5，获取对应的二级评论
            if comment.get('like', 0) > 0:
                replies = Fetch_comment_replies(video_id, comment.get('rpid'), comment['member'].get('uname', ''), max_pages=10)
                comments.extend(replies)
        time.sleep(random.uniform(0.5, 1))
    return comments




"""
将评论数据保存到 CSV 文件中，保存目录为 ./result/
"""
def Save_comments_to_csv(comments, video_bv):

    save_dir = './result'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    file_path = os.path.join(save_dir, f'{video_bv}.csv')
    with open(file_path, mode='w', encoding='utf-8-sig', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=[
            '用户昵称', '性别', '评论内容', '被回复用户', 
            '评论层级', '用户当前等级', '点赞数量', '回复时间'
        ])
        writer.writeheader()
        for comment in comments:
            writer.writerow(comment)
    print(f"保存成功: {file_path}")



"""
从 CSV 文件中读取视频列表，依次爬取评论并保存到 CSV 文件中
"""
def main(filename='Video_list.csv'):
    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        header = next(reader)  # 跳过第一行标题
        for row in reader:
            if len(row) < 2:
                print("警告: 跳过格式错误的行", row)
                continue
            video_name, video_bv = row[0].strip(), row[1].strip()
            print(f'视频名字: {video_name}, video_bv: {video_bv}')
            video_id = Get_video_id(video_bv)
            if video_id:
                comments = Fetch_comments(video_id)
                Save_comments_to_csv(comments, video_name)
            else:
                print("错误: 获取视频ID失败", video_bv)




if __name__ == '__main__':
    main()
