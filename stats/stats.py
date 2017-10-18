import json
import pymysql
import math
import time
from decimal import Decimal

# 连接数据库
db=pymysql.connect(host='127.0.0.1', user='root', passwd='456789', db='biliup', port=3306, charset='utf8', cursorclass = pymysql.cursors.DictCursor)
db.autocommit(True)
cursor=db.cursor()

# 获取类型相关的统计
# 先获取所有类型
cursor.execute('select distinct category from biliup')
cate=list(map(lambda x:x['category'],cursor.fetchall()))
cate.remove('公告') #就一个人，情况也比较特殊，就不管他了
cate.remove('无') #没有类型也不管了
print(cate)
# 各类型的相关统计
categories={}
for cat in cate:
	cursor.execute('select count(*) as num,avg(follow) as follow,avg(fans) as fans,avg(video) as video,\
					avg(playNum) as playNum from biliup where category = %s',cat)
	categories[cat]=cursor.fetchone()
	# 性别比例需排除保密的up
	cursor.execute('select avg(sex) as sex from biliup where category = %s and sex != 0',cat)
	categories[cat].update(cursor.fetchone())
print(categories)
# 打印信息用于主页
for k,v in categories.items():
	print(k+":"+str(v['num']))
category=[]
# 打印信息用于类型页面
for cat in categories:
	# 性别改为百分比
	categories[cat]['sex']=(categories[cat]['sex']-1)*100
	for x in categories[cat]:
		if x!='num':
			# Decimal转float
			categories[cat][x]=float(categories[cat][x])
	y=categories[cat].copy()
	del y['num']
	y['name']=cat
	category.append(y)
print(category)
# 打印不分类的统计信息，用于类型页面的平均数
cursor.execute('select avg(video) as video,avg(follow) as follow,avg(fans) as fans,avg(playNum) as playNum from biliup')
average=cursor.fetchone()
cursor.execute('select avg(sex) as sex from biliup where sex != 0') #性别比例需排除保密的up
average.update(cursor.fetchone())
average['sex']=(average['sex']-1)*100 #性别改为百分比
for avg in average:
	average[avg]=float(average[avg]) #Decimal转float
print(average)

# 打印性别信息用于主页
sexes={}
for sex in range(0,3):
	cursor.execute('select count(*) from biliup where sex = %s',sex)
	sexes[sex]=cursor.fetchone()['count(*)']
print(sexes)

# 打印等级信息用于主页
levels={}
for lev in range(0,7):
	cursor.execute('select count(*) from biliup where level = %s',lev)
	levels[lev]=cursor.fetchone()['count(*)']
print(levels)

# 打印星座信息用于主页
date2star=[20,19,21,20,21,22,23,23,23,24,23,22]
star=["摩羯座","水瓶座","双鱼座","白羊座","金牛座","双子座","巨蟹座","狮子座","处女座","天秤座","天蝎座","射手座","摩羯座"]
stars={} #用于记录各星座的dict
for sta in star:
	stars[sta]=0 #初始为0
# 取出生日信息
cursor.execute('select birth from biliup')
birth=list(map(lambda x:x['birth'],cursor.fetchall()))
for bir in birth:
	# 排除生日保密或系统默认值（01-01）的
	if bir !=' none' and bir !='01-01':
		# 生日转星座
		bir=bir.split('-')
		month=int(bir[0])
		day=int(bir[1])
		sta=star[month-1] if day<date2star[month-1] else star[month]
		stars[sta]+=1
print(stars)

# 获取所在地相关的统计
place=['北京','上海','天津','重庆','广东','福建','浙江','江苏','山东','辽宁','江西','四川','陕西','湖北','河南','河北',\
		'山西','内蒙古','吉林','黑龙江','安徽','湖南','广西','海南','云南','贵州','西藏','甘肃','宁夏','青海','新疆',\
		'香港','澳门','台湾']
places={}
for pla in place:
	cursor.execute('select count(*) as num,avg(playNum) as playNum,avg(level) as level,avg(follow) as follow,\
					avg(fans) as fans,avg(video) as video from biliup where place like %s',pla+'%')
	places[pla]=cursor.fetchone()
	# 性别比例需排除保密的
	cursor.execute('select avg(sex) as sex from biliup where place like %s and sex != 0',pla+'%')
	places[pla].update(cursor.fetchone())
print(places)
# 打印信息用于地图页面
place=[]
for p in places:
	for x in places[p]:
		if x!='num':
			places[p][x]=float(places[p][x]) #Decimal转float
	y=places[p]
	y['name']=p
	place.append(y)
print(place)

# 记录信息到json用于关注页面
# 各类up关注的类型喜好前三
follow={}
for cat in cate:
	cursor.execute('select category,count(*) as num from biliup a inner join\
				(select to_id from followids f inner join biliup b on f.from_id=b.id where b.category=%s) t\
				where a.id=t.to_id group by category order by num desc limit 3',cat)
	follow[cat]=cursor.fetchall()
# 不分类、所有人的关注类型喜好
cursor.execute('select category,count(*)/24978 as num from biliup a inner join\
				(select to_id from followids f inner join biliup b on f.from_id=b.id) t\
				where a.id=t.to_id group by category order by num desc')
follow['所有人']=cursor.fetchall()
print(follow)
# follow={'音乐': [{'category': '音乐', 'num': 24491}, {'category': '游戏', 'num': 12329}, {'category': '生活', 'num': 11688}], 
# 		'动画': [{'category': '动画', 'num': 40321}, {'category': '游戏', 'num': 19659}, {'category': '生活', 'num': 13371}], 
# 		'游戏': [{'category': '游戏', 'num': 61688}, {'category': '生活', 'num': 22806}, {'category': '动画', 'num': 14736}], 
# 		'国创': [{'category': '生活', 'num': 1060}, {'category': '动画', 'num': 1020}, {'category': '游戏', 'num': 901}], 
# 		'鬼畜': [{'category': '鬼畜', 'num': 15792}, {'category': '游戏', 'num': 7583}, {'category': '生活', 'num': 4530}], 
# 		'舞蹈': [{'category': '舞蹈', 'num': 13816}, {'category': '生活', 'num': 4111}, {'category': '音乐', 'num': 3858}], 
# 		'科技': [{'category': '科技', 'num': 11746}, {'category': '生活', 'num': 9235}, {'category': '游戏', 'num': 8203}], 
# 		'生活': [{'category': '生活', 'num': 35442}, {'category': '游戏', 'num': 16124}, {'category': '科技', 'num': 10297}], 
# 		'番剧': [{'category': '番剧', 'num': 3103}, {'category': '游戏', 'num': 2170}, {'category': '生活', 'num': 1700}], 
# 		'电视剧': [{'category': '电视剧', 'num': 15407}, {'category': '生活', 'num': 6509}, {'category': '电影', 'num': 4926}], 
# 		'电影': [{'category': '电影', 'num': 4324}, {'category': '生活', 'num': 3606}, {'category': '游戏', 'num': 2214}], 
# 		'娱乐': [{'category': '娱乐', 'num': 16096}, {'category': '生活', 'num': 8434}, {'category': '电视剧', 'num': 4481}], 
# 		'时尚': [{'category': '时尚', 'num': 13868}, {'category': '生活', 'num': 5999}, {'category': '游戏', 'num': 1646}], 
# 		'广告': [{'category': '生活', 'num': 84}, {'category': '科技', 'num': 77}, {'category': '游戏', 'num': 69}],
# 		'所有人': [{'category': '游戏', 'num': 5.723}, {'category': '生活', 'num': 5.207}, {'category': '动画', 'num': 3.349},
# 				{'category': '音乐', 'num': 3.293}, {'category': '科技', 'num': 2.475}, {'category': '鬼畜', 'num': 1.645},
# 				{'category': '电影', 'num': 1.506}, {'category': '时尚', 'num': 1.458}, {'category': '娱乐', 'num': 1.448},
# 				{'category': '电视剧', 'num': 1.245}, {'category': '舞蹈', 'num': 1.215}, {'category': '番剧', 'num': 0.531},
# 				{'category': '国创', 'num': 0.358}, {'category': '广告', 'num': 0.018}],}
data=[]
# 小数精度取3，修改数据格式，存入data的list
for cat in follow:
	if cat!='所有人':
		for i in range(0,3):
			follow[cat][i]['num']=round(follow[cat][i]['num']/categories[cat]['num'],3)
			follow[cat][i]['cat']=cat
			data.append(follow[cat][i])
for i in follow['所有人']:
	i['num']=round(i['num'],3)
	i['cat']='所有人'
	data.append(i)
print(follow)
# 存入json
f=open("../web/static/js/category.json",'w')
json.dump(data,f)
f.close()

# 获取粉丝数前100的up关注情况，存入json，用于关注页面的力导向图
cursor.execute("select from_id as source,to_id as target from followids where from_id in\
				(select id from (select id from biliup order by fans desc limit 100) t) and to_id in\
				(select id from (select id from biliup order by fans desc limit 100) t);")
links=cursor.fetchall() #连线信息
cursor.execute("select id,fans/10000 as radius,category,name from biliup order by fans desc limit 100")
nodes=cursor.fetchall() #节点信息
groups=['游戏','生活','动画','音乐','娱乐','科技','电视剧','舞蹈','时尚','鬼畜','电影','番剧','国创','广告']
for node in nodes:
	node['radius']=int(math.log(node['radius'],5)*5) #根据粉丝数计算绘图时的半径
	try:
		node['category']=groups.index(node['category']) #类型转换为数字，方便填色
	except:
		node['category']=14 #公告 或 无
print(nodes)
print(links)
# 存入json
f=open("../web/static/js/follow.json",'w')
json.dump({"nodes":nodes,"links":links},f)
f.close()

# 粉丝数前100的up详细信息，用于关注页面的展示
cursor.execute("select name,sign,video,level,sex,follow,fans,playNum,description,regtime,birth,place,tags\
				from biliup order by fans desc limit 100;")
ups=cursor.fetchall()
data={}
for up in ups:
	data[up['name']]=up
	del up['name']
	# 性别 数字转字符
	if up['sex']==1:
		up['sex']='男'
	elif up['sex']==2:
		up['sex']='女'
	# 标签 list转、分隔的string
	up['tags']='、'.join(up['tags'].split('#'))
	if up['regtime']!=0: #未设置注册时间不可见
		t=time.localtime(up['regtime'])
		up['regtime']=time.strftime('%Y-%m-%d',t) #注册时间 时间戳转string
print(data)
# 存入json
f=open("../web/static/js/ups.json",'w')
json.dump(data,f)
f.close()

# 关闭数据库连接
cursor.close()
db.close()