# -*- coding: utf-8 -*-
import json

from scrapy import Spider,Request

from zhihuser.items import ZhihuserItem

class ZhihuSpider(Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    start_user = 'excited-vczh'
    user_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'
    user_query = 'allow_message,is_followed,is_following,is_org,is_blocking,employments,answer_count,follower_count,articles_count,gender,badge[?(type=best_answerer)].topics'

    followee_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}'
    followee_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'

    def start_requests(self):
        yield Request(self.user_url.format(user=self.start_user,include=self.user_query),callback=self.parse_user)


    def parse_user(self,response):
        result = json.loads(response.text)
        item = ZhihuserItem()

        for field in item.fields:
            if field in result.keys():
                item[field] = result.get(field)
        yield item

        yield Request(self.followee_url.format(user=result.get('url_token'),include=self.followee_query,offset=0,limit=20),callback=self.parse_followee)

    def parse_followee(self,response):
        results = json.loads(response.text)
        if 'data' in results:
            for result in results.get('data'):
                yield Request(self.user_url.format(user=result.get('url_token'),include=self.user_query),callback=self.parse_user)

        if ('paging' in results) and (results.get('is_end') == False):
            next = results.get('paging').get('next')
            yield Request(next,callback=self.parse_followee)