# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from twisted.enterprise import adbapi 
import pymysql.cursors

class BiliPipeline(object):
	def __init__(self, dbpool):
	    self.dbpool = dbpool

	@classmethod
	def from_settings(cls, settings):
	# 会被scrapy调用的类方法,返回一个dbpoll对象传递给MysqlTwistedPipeline类,构建新实例
	    params = dict(host = settings['MYSQL_HOST'],
	    	            port = settings['MYSQL_PORT'],
	                    db = settings['MYSQL_DB'],
	                    user = settings['MYSQL_USER'],
	                    passwd = settings['MYSQL_PASSWORD'],
	                    charset = 'utf8',
	                    cursorclass = pymysql.cursors.DictCursor
	                    )
	    # 第一个参数,操作的数据库,利用反射原理,第二个参数MySQL初始化的一些参数,格式固定
	    dbpool = adbapi.ConnectionPool('pymysql', **params)
	    print("_______________________from_settings______________________")
	    # 返货一个MysqlTwistedPipeline的实例对象
	    return cls(dbpool)

	def process_item(self, item, spider):
	    ("_______________________process_item______________________")
	    # 处理item 通过runInteraction执行异步操作,第一个参数是具体的操作过程,第二个参数是操作数据
	    # 并返回一个query,query是Deferred类的实例,调用其中的addErrback方法处理异常
	    query = self.dbpool.runInteraction(self.do_insert, item)
	    query.addErrback(self.handle_error, item, spider)
	    return item

	def handle_error(self, failure, item , spider ):
	    # 处理MySQL异常
	    print (failure)

	def do_insert(self, cursor, item):
	    # 执行MySQL语句，记录信息
	    print("_______________________do_insert______________________")
	    # 记录基本信息
	    sql = """
	        INSERT INTO biliup(id,name,face,sign,video,category,
	        level,sex,follow,fans,playNum,description,regtime,
	        birth,place,tags) 
	        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
	        """

	    string=''
	    for t in item['tags']:
	    	string=string+t+'#'
	    string=string[:-1]
	    args=(item['mid'],item['name'],item['face'],item['sign'],
	    	item['video'],item['category'],item['level'],item['sex'],
	    	item['follow'],item['fans'],item['playNum'],item['description'],
	    	item['regtime'],item['birth'],item['place'],string)
	    cursor.execute(sql,args)

	    # 记录关注列表信息
	    sql="INSERT INTO followids(from_id,to_id) VALUES(%s,%s)"
	    for followid in item['followids']:     
	        cursor.execute(sql,(item['mid'],followid))
