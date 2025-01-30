import requests
import csv
import time
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict

# 常量配置
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'Referer': 'https://www.bilibili.com/'
}
API_BASE = {
    'view': 'https://api.bilibili.com/x/web-interface/view',  # 获取视频基本信息
    'main_reply': 'https://api.bilibili.com/x/v2/reply/main',  # 获取主评论
    'reply_detail': 'https://api.bilibili.com/x/v2/reply/reply'  # 获取子评论
}
REQUEST_INTERVAL = 1.5  # 设置请求间隔，避免请求过于频繁
MAX_RETRY = 3  # 最大重试次数

# 数据模型
class Comment:
    """评论数据模型，存储评论信息"""
    def __init__(self, data: Dict, parent_user: str = ""):
        self.rpid: int = data['rpid']  # 评论ID
        self.user_name: str = data['member']['uname']  # 用户昵称
        self.content: str = data['content']['message']  # 评论内容
        self.parent_user: str = parent_user  # 父评论用户
        self.level: str = '一级评论' if parent_user == "" else '二级评论'  # 评论层级
        self.gender: str = data['member']['sex']  # 用户性别
        self.user_level: int = data['member']['level_info']['current_level']  # 用户等级
        self.likes: int = data['like']  # 点赞数
        self.ctime: str = datetime.fromtimestamp(data['ctime']).strftime('%Y-%m-%d %H:%M:%S')  # 评论时间
        
    def to_dict(self) -> Dict:
        """将评论对象转换为字典"""
        return self.__dict__

# 核心功能模块
class BiliCommentCrawler:
    def __init__(self):
        self.session = requests.Session()  # 使用Session提高性能
        self.session.headers.update(HEADERS)  # 更新请求头

    def get_aid(self, bvid: str) -> int:
        """通过BV号获取视频的aid"""
        params = {'bvid': bvid}
        for _ in range(MAX_RETRY):
            try:
                resp = self.session.get(API_BASE['view'], params=params, timeout=10)
                if resp.status_code == 200:
                    return resp.json()['data']['aid']
            except Exception as e:
                print(f"获取aid失败: {e}")
                time.sleep(REQUEST_INTERVAL)
        return 0

    def fetch_comments(self, oid: int) -> List[Comment]:
        """获取视频的所有评论，包括子评论"""
        comments = []
        next_page = 0
        
        while True:
            params = {
                'oid': oid,
                'type': 1,  # 评论类型：1 表示视频评论
                'mode': 3,  # 获取评论模式
                'next': next_page  # 分页参数
            }
            
            try:
                resp = self.session.get(API_BASE['main_reply'], params=params)
                data = resp.json().get('data', {})
                
                # 处理主评论
                if 'replies' in data:
                    for reply in data['replies']:
                        comments.append(Comment(reply))
                        comments.extend(self._fetch_sub_replies(oid, reply['rpid'], reply['member']['uname']))  # 获取二级评论
                
                # 分页控制
                if data.get('cursor', {}).get('is_end', True):
                    break
                next_page = data.get('cursor', {}).get('next', 0)
                
            except Exception as e:
                print(f"获取评论失败: {e}")
                break
            
            time.sleep(REQUEST_INTERVAL)
        
        return comments

    def _fetch_sub_replies(self, oid: int, root_rpid: int, parent_user: str) -> List[Comment]:
        """获取子评论"""
        sub_comments = []
        page = 1
        
        while True:
            params = {
                'oid': oid,
                'type': 1,
                'root': root_rpid,
                'pn': page  # 当前页数
            }
            
            try:
                resp = self.session.get(API_BASE['reply_detail'], params=params)
                data = resp.json().get('data', {})
                
                # 没有子评论时退出
                if not data.get('replies', []):
                    break
                
                for reply in data['replies']:
                    sub_comments.append(Comment(reply, parent_user))
                
                # 如果所有子评论都已经获取完毕，退出循环
                if page >= data['page']['count']:
                    break
                page += 1
                
            except Exception as e:
                print(f"获取子评论失败: {e}")
                break
            
            time.sleep(REQUEST_INTERVAL)
        
        return sub_comments

    def save_to_csv(self, comments: List[Comment], filename: str):
        """将评论保存到CSV文件"""
        Path("./result").mkdir(exist_ok=True)  # 确保存储目录存在
        with open(f"./result/{filename}.csv", "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=Comment().__dict__.keys())
            writer.writeheader()  # 写入表头
            for comment in comments:
                writer.writerow(comment.to_dict())  # 写入每条评论数据

# 执行模块
def main():
    crawler = BiliCommentCrawler()
    
    # 读取视频列表并爬取评论
    with open('./video_list.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)  # 跳过标题行
        
        for row in reader:
            video_name, bvid = row[0], row[1]
            print(f"正在处理: {video_name} ({bvid})")
            
            # 获取视频aid并爬取评论
            aid = crawler.get_aid(bvid)
            if aid:
                comments = crawler.fetch_comments(aid)
                crawler.save_to_csv(comments, video_name)
                print(f"已保存 {len(comments)} 条评论")
            else:
                print(f"获取aid失败: {bvid}")

if __name__ == "__main__":
    main()
