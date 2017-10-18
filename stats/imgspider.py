'''
	不知道为什么，up主的头像，即域名为：
	http://i0.hdslb.com 、 http://i1.hdslb.com 、 http://i2.hdslb.com
	的图片不能用网址直接加载是加载不出来的，
	换了几个浏览器都这样

	但是在其他网页缓存了头像的图片后，刷新页面就有该头像了。。。

	而且把编好的html以文件的形式用浏览器打开能加载图片，
	只是用Flask就不行了。。。

	实在没有办法，于是就决定把他们头像全部爬下来了。

	有人知道原因可以告诉我吗。。。
'''

import pymysql
import urllib.request

# 从数据库中获取所有头像地址
db=pymysql.connect(host='127.0.0.1', user='root', passwd='456789', db='biliup', port=3306, charset='utf8', cursorclass = pymysql.cursors.DictCursor)
db.autocommit(True)
cursor=db.cursor()
cursor.execute("select id,face from biliup")
faces=cursor.fetchall()
print(faces)

# 爬取头像
for face in faces:
	print(str(face['id']))
	urllib.request.urlretrieve(face['face'],'../web/static/img/%s.jpg' % face['id'])

# 关闭数据库连接
cursor.close()
db.close()