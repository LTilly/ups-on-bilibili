# -*- coding: utf-8 -*-

import scrapy
import json
from scrapy import FormRequest,Request
from scrapy_redis.spiders import RedisSpider
from ..items import BiliItem

class BiliupSpider(RedisSpider):
#class BiliupSpider(scrapy.Spider):
    name = 'biliup'
    allowed_domains = ['space.bilibili.com','api.bilibili.com']
    #redis_key='biliup:start_urls'

    # 找了个关注数比较多的up主，从他开始爬取
    def start_requests(self):
        url="https://space.bilibili.com/ajax/member/GetInfo"
        headers={'Referer':'https://space.bilibili.com/2#1'}
        yield FormRequest(url=url,formdata={'mid':'808171','csrf':'null'},callback=self.parse,headers=headers)

    # 爬取GetInfo里面的所有信息，并返回下一个请求
    def parse(self, response):
        data=json.loads(response.body_as_unicode())['data']
        print('-----------'+data['mid']+'-------------')
        # 用日志记录一下，以防意外
        self.logger.debug('\nmid'+data['mid']+'\n')
        # 如果播放量小于10000，那这个up根本不算大佬，只是萌新，咱就放过他了
        if data['playNum']<100000:
            self.logger.debug('\nnotmid'+data['mid']+'\n')
            return
        # 将信息记录到item中
        up=BiliItem()
        up['face']=data['face']
        up['name']=data['name']
        up['sign']=data['sign']
        sex={'男':1,'女':2,'保密':0,'':0}
        up['sex']=sex[data['sex']]
        up['level']=data['level_info']['current_level']
        # 由于up主可以同时设置以下三个信息不可见，所以GetInfo中可能没有
        up['birth']=data.get('birthday',' none')[-5:] #看了下，绝大多数up设置的生日中，年份都是假的，所以就不要年份了
        up['place']=data.get('place','')
        up['regtime']=data.get('regtime','0')
        up['mid']=data['mid']
        up['playNum']=data['playNum']
        up['description']=data['description']
        # 下一个有关视频信息的请求的url
        url='https://space.bilibili.com/ajax/member/getSubmitVideos?pagesize=1&mid='+data['mid']
        return Request(url,callback=self.parse_video,meta={'up':up})

    # 爬取getSubmitVideos里面的有关信息，并返回下一个请求
    def parse_video(self, response):
        data=json.loads(response.body_as_unicode())['data']
        up=response.meta['up'] #取出item
        up['video']=data['count'] #视频数
        tlist=data['tlist']
        try:
            # 以up主投稿视频中数量最多的类型，决定up主类型
            cat=max(tlist,key=lambda x:tlist[x]['count'])
            up['category']=tlist[cat]['name']
        except:
            up['category']='无' #个别up主似乎退隐江湖了，删了所有视频。。。
        # 下一个有关关注信息的请求的url
        url='https://api.bilibili.com/x/relation/stat?vmid='+up['mid']
        return Request(url,callback=self.parse_follow,meta={'up':up})

    # 爬取stat里面的有关信息，并返回下一个请求
    def parse_follow(self, response):
        data=json.loads(response.body_as_unicode())['data']
        up=response.meta['up'] #取出item
        up['follow']=data['following']
        up['fans']=data['follower']
        # 下一个关有标签信息的请求的url
        url='https://space.bilibili.com/ajax/member/getTags?mids='+up['mid']
        return Request(url,callback=self.parse_tags,meta={'up':up})

    # 爬取getTags里面的有关信息，并返回下一个请求
    def parse_tags(self, response):
        tags=json.loads(response.body_as_unicode())['data'][0]['tags']
        up=response.meta['up'] #取出item
        up['tags']=tags
        # 下一个关有关注列表的请求的url
        url='https://api.bilibili.com/x/relation/followings?vmid='+up['mid']
        return Request(url,callback=self.parse_followids,meta={'up':up})

    # 爬取followings里面的有关信息，并返回待爬取的up主的GetInfo的请求
    def parse_followids(self, response):
        lst=json.loads(response.body_as_unicode())['data']['list']
        followids=[] #关注列表
        for follow in lst:
            followids.append(follow['mid'])
        up=response.meta['up'] #取出item
        up['followids']=followids
        # 日志记录下完成爬取了的up主
        self.logger.debug('\nnotmid'+up['mid']+'\n')
        yield up #返回item到pipeline中
        url="https://space.bilibili.com/ajax/member/GetInfo"
        # 返回待爬取的up主的GetInfo的请求
        for follow in followids:
            yield FormRequest(url=url,formdata={'mid':str(follow),'csrf':'null'},callback=self.parse)

