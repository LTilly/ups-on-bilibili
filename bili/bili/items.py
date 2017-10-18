# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BiliItem(scrapy.Item):
    # define the fields for your item here like:
    face=scrapy.Field() #头像 varchar 255
    name=scrapy.Field() #昵称 varchar 100
    sign=scrapy.Field() #签名 varchar 150
    video=scrapy.Field() #视频数 int unsigned
    category=scrapy.Field() #类型 varchar 10
    level=scrapy.Field() #等级 tinyint unsigned
    sex=scrapy.Field() #性别 tinyint unsigned 0 保密 1男 2女

    follow=scrapy.Field() #关注数 int unsigned
    followids=scrapy.Field() #关注列表 单独存在另一表中
    fans=scrapy.Field() #粉丝数 int unsigned
    playNum=scrapy.Field() #播放量 int unsigned
    
    description=scrapy.Field() #认证 varchar 100
    mid=scrapy.Field() #id int unsigned
    regtime=scrapy.Field() #注册时间 int unsigned
    birth=scrapy.Field() #生日 varchar 5 
    place=scrapy.Field() #地点 varchar 20
    tags=scrapy.Field() #标签 text
