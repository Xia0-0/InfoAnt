#引入模块
import requests  # 发送 HTTP 请求，获取网页内容
import re  # 使用正则表达式提取数据
import time  # 控制请求间隔，避免被封
import csv  # 处理 CSV 文件


# 伪装模块
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
}


# 获取视频的 aid
def Get_video_id(bv):
    url = f'https://api.bilibili.com/x/web-interface/view?bvid={bv}'
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', {}).get('aid')
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"请求错误: {e}")
        return None



# 获取一级评论
def Fetch_comments(video_id, max_pages=100):
    comments = []
    for page in range(1, max_pages + 1):
        url = f'https://api.bilibili.com/x/v2/reply?pn={page}&type=1&oid={video_id}&sort=2'
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json().get('data', {})
                for comment in data.get('replies', []):
                    comment_info = {
                        '用户昵称': comment['member']['uname'],
                        '评论内容': comment['content']['message'],
                        '被回复用户': '',
                        '评论层级': '一级评论',
                        '性别': comment['member']['sex'],
                        '用户当前等级': comment['member']['level_info']['current_level'],
                        '点赞数量': comment['like'],
                        '回复时间': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(comment['ctime']))
                    }
                    comments.append(comment_info)
                    # 获取二级评论
                    replies = Fetch_comment_replies(video_id, comment['rpid'], comment['member']['uname'])
                    comments.extend(replies)
        except requests.RequestException as e:
            print(f"请求错误: {e}")
            break
        time.sleep(2)
    return comments


# 获取二级评论
def Fetch_comment_replies(video_id, comment_id, parent_user_name, max_pages=100):
    replies = []
    for page in range(1, max_pages + 1):
        url = f'https://api.bilibili.com/x/v2/reply/reply?oid={video_id}&type=1&root={comment_id}&ps=10&pn={page}'
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json().get('data', {})
                for reply in data.get('replies', []):
                    reply_info = {
                        '用户昵称': reply['member']['uname'],
                        '评论内容': reply['content']['message'],
                        '被回复用户': parent_user_name,
                        '评论层级': '二级评论',
                        '性别': reply['member']['sex'],
                        '用户当前等级': reply['member']['level_info']['current_level'],
                        '点赞数量': reply['like'],
                        '回复时间': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(reply['ctime']))
                    }
                    replies.append(reply_info)
        except requests.RequestException as e:
            print(f"请求错误: {e}")
            break
        time.sleep(2)
    return replies


# 保存评论数据到 CSV 文件
def Save_comments_to_csv(comments, video_bv):
    with open(f'./result/{video_bv}.csv', mode='w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['用户昵称', '性别', '评论内容', '被回复用户', '评论层级', '用户当前等级', '点赞数量', '回复时间'])
        writer.writeheader()
        for comment in comments:
            writer.writerow(comment)



# 读取视频列表并爬取评论
def main(filename='./video_list.csv'):
    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # 跳过第一行（标题行）
        for row in reader:
            video_name, video_bv = row[0], row[1]
            print(f'视频名字: {video_name}, video_bv: {video_bv}')
            video_id = Get_video_id(video_bv)
            if video_id:
                comments = Fetch_comments(video_id)
                Save_comments_to_csv(comments, video_name)


if __name__ == '__main__':
    main()  # 执行主函数
