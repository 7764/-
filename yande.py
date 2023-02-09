from ctypes.wintypes import tagMSG
import requests
import os
from lxml import html
from time import sleep
p=[]  # p 没找到的地址 
rp=[]  # r 重复的地址 
l=[]  # l过长文件的地址
n=[]  #n 累计下载了多少个
linked={} #linked 下载失败的
tag="piromizu"  #填tag
path = "D:/DOWNLOAD/爬虫/yande/"+tag+"/" #文件存放地址
pageNum=1 #从第几页开始 第一页为0，第二页为1....
def get_maxpage():
	"""获取网页总页数"""
	url = "https://yande.re/post?tags="+tag
	sp = requests.get(url).text
	tree = html.fromstring(sp)
	a = tree.xpath("//div[@class='pagination']/a/text()")
	sleep(1)
	print("变量url%s",url)
	if not os.path.exists(path.strip().rstrip("/")):
		os.makedirs(path.strip().rstrip("/"))
	
	return int(a[-2])
def get_links_and_download_images():
	"""获取图片链接，并下载到本地"""
	print("获取页数中")
	maxpage = get_maxpage()
	print("总页数为",maxpage,"。将从第",pageNum+1,"页开始")
	for w in range(1,maxpage-pageNum+1):
		links = []
		url = "https://yande.re/post?page={a}&tags=".format(a=w+pageNum)+tag
		sp = requests.get(url).text
		tree = html.fromstring(sp)
		href = tree.xpath("//ul[@id='post-list-posts']/li/div")
		print("正在爬取第",w+pageNum,"页")
		print("页面元素长度",len(href))
		for i in range(1,len(href)+1):
			print("获取第",w+pageNum,"页,第",i,"张链接")
			a = tree.xpath("//ul[@id='post-list-posts']/li["+str(i)+"]/div/a/@href")
			print("输出一下a",a)
			
			url2 = "https://yande.re"+a[0]
			sp2 = requests.get(url2).text
			tree2 = html.fromstring(sp2)
			a=tree2.xpath("//a[@id='png']/@href")
			print("url2等于",url2)
			if a:
				print("原图",a)
				links.append(a[0])
			else:
				a=tree2.xpath("//a[@id='highres']/@href")
				print("没有png原图,jpg地址为",a)
				print("------------------------------------------------------------------------------------------------------------------------------------------------------")
				links.append(a[0])
			print("获取第",w+pageNum,"页第",i,"张结束")
			print("")
		sleep(1)
		print("开始下载页面图片")
		links_dict = generate_filepath_and_check_repeat_file(links)
		download(links_dict)
		print("")
		print("")
		print("")
		print("")

		
def generate_filepath_and_check_repeat_file(links):
	"""生成文件名称"""
	print("生成文件名")
	links_dict = {}
	for i in range(0,len(links)):
		link = links[i]
		if link.find("image/")!=-1&link.find(".png")!=-1:
			star = link.find("image/")+len("image/")
			end = star + 32
			filename = link[star:end]+".png"#生成文件名
			filepath = path + filename#生成文件路径

			if len(filename) == 32+len(".png"):
				if os.path.exists(filepath) is True:
					print("出现重复文件")
					rp.append(link)
					print("------------------------------------------------------------------------------------------------------------------------------------------------------")
					print("-------------------------------------------------------------------------",link,"----------------------------------------------------------------------------")
					print("------------------------------------------------------------------------------------------------------------------------------------------------------")
					continue
				if os.path.exists(filepath) is not True:#文件不存在，则写入字典
					links_dict[filepath] = link 
					print("从",link,"下载的文件,存放在本地磁盘",filepath)
			elif len(filename) != 32 +len(".png"):
				print("文件名长度大于32",link)
				l.append(link)
				print("------------------------------------------------------------------------------------------------------------------------------------------------------")
				print("-------------------------------------------------------------------------",link,"----------------------------------------------------------------------------")
				print("------------------------------------------------------------------------------------------------------------------------------------------------------")
		elif link.find("image/")!=-1&link.find(".jpg")!=-1:
			star = link.find("image/")+len("image/")
			end = star + 32
			filename = link[star:end]+".jpg"#生成文件名
			filepath = path + filename#生成文件路径
			if len(filename) == 32+len(".jpg"):
				if os.path.exists(filepath) is True:
					print("出现重复文件")
					rp.append(link)
					print("------------------------------------------------------------------------------------------------------------------------------------------------------")
					print("-----------------------------------------------------------------------",link,"------------------------------------------------------------------------")
					print("------------------------------------------------------------------------------------------------------------------------------------------------------")
					continue
				if os.path.exists(filepath) is not True:#文件不存在，则写入字典
					links_dict[filepath] = link
					print("从",link,"下载的文件,存放在本地磁盘",filepath)
					
			elif len(filename) != 32+len(".jpg"):
				print("文件名长度大于32",link)
				l.append(link)
				print("------------------------------------------------------------------------------------------------------------------------------------------------------")
				print("-------------------------------------------------------------------------",link,"----------------------------------------------------------------------------")
				print("------------------------------------------------------------------------------------------------------------------------------------------------------")
		else:
			p.append(link)
			print("链接未找到",link)
			print("------------------------------------------------------------------------------------------------------------------------------------------------------")
			print("-------------------------------------------------------------------------",link,"----------------------------------------------------------------------------")
			print("------------------------------------------------------------------------------------------------------------------------------------------------------")
		print("")
	return links_dict
def download(links_dict):
	"""下载图片到本地"""
	
	filename_list = list(links_dict.keys())
	links = list(links_dict.values())
	# 下载失败的链接
	
	for num in range(0,len(filename_list)):
		try:
			link = links[num]
			r = requests.request(method="GET",url=link,stream=True)
			if r.status_code == 200:
				open(filename_list[num],"wb").write(r.content)
				print("下载到本地第",num+1,"张链接的文件地址",filename_list[num],"文件大小",r.headers["Content-Length"])
				n.append(filename_list[num])
				stats=os.stat(filename_list[num])
				print(stats.st_size,int(r.headers["Content-Length"]))
				if (stats.st_size==int(r.headers["Content-Length"])):
					print(filename_list[num],"文件一致")
				else:
					print("文件名",filename_list[num],"文件大小不一致,已添加到重新下载")
					linked[filename_list[num]]=links[num]
		except:
			print("第",num+1,"张链接的文件地址",filename_list[num],"下载失败")
			linked[filename_list[num]]=links[num]

	
		sleep(1)	
	
	print("结束一页下载")
def dataChek(file_path):
	print("开始检查数据完整度\n") #对比网站的图片大小是否一致
	folders = os.listdir(file_path)
	links={}
	i=0
	for file in folders:
		
        #遍历获取所有文件大小
		try:
			r = requests.request(method="GET",url="https://files.yande.re/image/"+file,stream=True)
			stats=os.stat(file_path+file)
			if (stats.st_size==int(r.headers["Content-Length"])):
				i=i+1
				print(i,file,"文件一致")

			else:
				i=i+1
				print(i,"文件名",file,"文件大小不一致,已添加到重新下载")
				links[file_path+file]="https://files.yande.re/image/"+file
		except:
			folders.append(file)
			i=i+1
			print(i,"文件名",file,"检查失败并再次添加到队尾,队列长度为",len(folders))

	print("全部检查完毕,正在重新下载")	
	
	download(links)
		

if __name__=="__main__":
	print("开始启动")
	
	get_links_and_download_images()
	
	# dataChek(path)
	print("运行结束,下载了",len(n),"个文件,共有")
	print(len(p),"个文件未找到",p)
	print(len(rp),"个文件重复文件",rp)
	print(len(l),"个文件过长",l)
	print("下载失败",linked)
	