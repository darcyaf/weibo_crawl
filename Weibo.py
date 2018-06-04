import requests
import datetime
from pymongo import MongoClient

# 微博类


class Weibo:
    get_index_url = 'https://m.weibo.cn/api/container/getIndex'
    get_comment_url = 'https://m.weibo.cn/api/comments/show'

    def __init__(self, uid,start_page, max_page=50):
        self.uid = uid
        self.max_page = max_page
        database = MongoClient('127.0.0.1', 27017).weibo
        self.database = database
        self.crawled = 0
        self.start_page = start_page
        self.max_comment_page = 10

    #  登陆操作
    def login(self):
        pass
    # 获取首页用户信息

    def _getCards(self, page):
        params = {
            'uid': self.uid,
            'luicode': 10000011,
            'lfid': 1076031098618600,
            'type': 'uid',
            'value': self.uid,
            'containerid': 1076031098618600,
            'page': page
        }
        weibo_list_result = requests.get(self.get_index_url, params).json()
        cards = weibo_list_result['data']['cards']
        len_of_cards = len(cards)
        if len_of_cards <= 0:
            return 0
        cardlistInfo = weibo_list_result['data']['cardlistInfo']
        self.total = cardlistInfo['total']
        self.crawled = self.crawled + len(cards)
        self.page = page
        now = str(datetime.datetime.now())
        log_message_tpl = """ {now} 当前是第 {page} 页，本次抓取到{len_of_cards} 条微博, 总共已经抓取了{crawled} 条 """
        log_message = log_message_tpl.format(
            **{"page": page, "len_of_cards": len_of_cards, 'crawled': self.crawled, 'now': now})
        print(log_message)
        for card in cards:
            if 'mblog' not in card.keys():
                continue
            weibo_id = card['mblog']['idstr']
            comments = self.getComments(weibo_id)
            card['comments'] = comments
        self.database.cards.insert_many(cards)
        return len_of_cards

    # 获取微博列表信息

    def getCards(self):
        for page in range(self.start_page, self.max_page + 1):
            has_next = self._getCards(page)
            if has_next <= 0:
                break
    # 获取评论

    def getComments(self, weibo_id):
        page = 1
        comments = []
        while page <= self.max_comment_page:
            page_comments = self.getComment(weibo_id, page)
            page = page + 1
            comments = comments + page_comments
        return comments

    # 获取单页的评论
    def getComment(self, weibo_id, page):
        params = {
            'id': weibo_id,
            'page': page
        }
        comments = []
        comment_list_result = requests.get(self.get_comment_url, params).json()
        if 'data' not in comment_list_result.keys():
            return comments
        if 'data' not in comment_list_result['data'].keys():
            return comments
        comments = comment_list_result['data']['data']
        #self.max_comment_page = comment_list_result['data']['max']
        log_message_tpl = """当前是 {weibo_id} 第 {page}页的评论, 总页数为{max_comment_page}"""
        log_message = log_message_tpl.format(
            **{'page': page, 'max_comment_page': self.max_comment_page, 'weibo_id': weibo_id})
        print(log_message)
        return comments

    def start(self):
        self.login()
        self.getCards()


wb = Weibo(1098618600, 6,10)
wb.start()
