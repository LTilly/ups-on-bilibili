'''
	网页框架
'''

import pymysql
import json
import time
from copy import deepcopy
import math
from flask import Flask,url_for,render_template,request

app = Flask(__name__)
app.config.from_object(__name__)

# 连接数据库的函数
def connectdb():
	db=pymysql.connect(host='127.0.0.1',user='root',passwd='456789',db='biliup',port=3306,charset='utf8',cursorclass=pymysql.cursors.DictCursor)
	db.autocommit(True)
	cursor=db.cursor()
	return (db,cursor)

# 关闭数据库的函数
def closedb(db,cursor):
	db.close()
	cursor.close()

# 首页/占比页面
@app.route('/')
def index():
	return render_template('index.html')

# 所在地页面
@app.route('/map/')
def map():
	return render_template('map.html')

# 类型页面
@app.route('/category/')
def category():
	return render_template('category.html')

# 数量页面
@app.route('/number/')
def number():
	(db,cursor)=connectdb()
	cursor.execute("select video,playNum,fans from biliup")
	ups=cursor.fetchall()
	closedb(db,cursor)
	data=[]
	for up in ups:
		data.append([up['video'],up['playNum'],up['fans']])
	ups=json.dumps({"ups":data})
	return render_template('number.html',ups=ups)

# 注册时间页面
@app.route('/regtime/')
def regtime():
	(db,cursor)=connectdb()
	cursor.execute("select category,regtime from biliup where regtime != 0")
	ups=cursor.fetchall()
	closedb(db,cursor)
	x=[]
	y={}
	z=0
	# 2009年5月~2017年9月的string，存入list x中，y记录每个string在x中的位置
	for i in range(5,13):
		if i<10:
			t='2009-0'+str(i)
		else:
			t='2009-'+str(i)
		x.append({'name':t,'value':[0,0]})
		y[t]=z
		z+=1
	for j in range(0,7):
		for i in range(1,13):
			if i<10:
				t='201'+str(j)+'-0'+str(i)
			else:
				t='201'+str(j)+'-'+str(i)
			x.append({'name':t,'value':[0,0]})
			y[t]=z
			z+=1
	for i in range(1,10):
		t='2017-0'+str(i)
		x.append({'name':t,'value':[0,0]})
		y[t]=z
		z+=1
	# value的第一个值为该月时间戳
	for i in y:
		x[y[i]]['value'][0]=time.mktime(time.strptime(i,'%Y-%m'))*1000
	# 每个类型均有一份数据记录
	reg={'all':deepcopy(x),'游戏':deepcopy(x),'生活':deepcopy(x),'动画':deepcopy(x),'音乐':deepcopy(x),\
		'娱乐':deepcopy(x),'科技':deepcopy(x),'电视剧':deepcopy(x),'舞蹈':deepcopy(x),'时尚':deepcopy(x),\
		'鬼畜':deepcopy(x),'电影':deepcopy(x),'番剧':deepcopy(x),'国创':deepcopy(x),'广告':deepcopy(x)}
	# value的第二个个值为该月的string
	for up in ups:
		t=time.localtime(up['regtime'])
		t=time.strftime('%Y-%m',t)
		reg['all'][y[t]]['value'][1]+=1 #总的人数+1
		if up['category'] in reg:
			reg[up['category']][y[t]]['value'][1]+=1 #对应类型的人数+1
	ups=json.dumps({"ups":reg})
	return render_template('regtime.html',ups=ups)

# 关注页面
@app.route('/follow/')
def follow():
	return render_template('follow.html')

# 搜索页面
@app.route('/search/')
def search():
	(db,cursor)=connectdb()
	ups={}
	cursor.execute("select * from biliup order by fans desc limit 20")
	ups['fans']=cursor.fetchall()
	cursor.execute("select * from biliup order by playNum desc limit 20")
	ups['playNum']=cursor.fetchall()
	cursor.execute("select * from biliup order by video desc limit 20")
	ups['video']=cursor.fetchall()
	closedb(db,cursor)
	for k in ups:
		for up in ups[k]:
			up['tags']=up['tags'].split('#')
			if up['regtime']!=0:
				t=time.localtime(up['regtime'])
				up['regtime']=time.strftime('%Y-%m-%d',t)
	return render_template('search.html',ups=ups)

# 搜索页面的搜索功能
@app.route('/keyword/',methods=['POST'])
def keyword():
	key=request.form['keyword']
	print(key)
	(db,cursor)=connectdb()
	cursor.execute("select * from biliup where name like '%%%s%%' order by fans desc" %key)
	ups=cursor.fetchall()
	closedb(db,cursor)
	for up in ups:
		up['tags']=up['tags'].split('#')
		if up['regtime']!=0:
			t=time.localtime(up['regtime'])
			up['regtime']=time.strftime('%Y-%m-%d',t)
	return json.dumps({'ups':ups})

if __name__=='__main__':
	app.run(debug=True)