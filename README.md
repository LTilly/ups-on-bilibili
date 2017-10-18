# Bilibili网站up主的数据可视化 #
## 数据爬取 ##
采用scrapy-redis分布式框架，利用up主之间的相互关注，分布式爬遍了B站上所有的up主，并记录了其中播放量达到一万的up主的信息。  
其中包含16个字段：ID、昵称、头像、签名、视频数、类型、等级、性别、关注数、粉丝数、播放量、认证、注册时间、生日、所在地和标签，并记录了每个up主所关注的up主的id信息。  
数据被存放到MySQL中。  
代码在bili文件夹中。
## 数据处理 ##
在stats文件夹中进行了简单的数据处理工作，用于之后的网络展示。
## 数据可视化 ##
利用Flask框架，配合Echarts以及D3，将数据的统计信息展示在网页上。