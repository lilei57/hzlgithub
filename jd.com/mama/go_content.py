#coding:utf-8
import requests,sys,re,pycurl,StringIO,time,xlrd,xlwt,HeaderData,md5,json
from bs4 import BeautifulSoup
import urllib
from selenium import webdriver
reload(sys) 
sys.setdefaultencoding('utf-8')

categoryID = '000'

def get_title_md5(title):
	m1 = md5.new()
	m1.update(title)			
	md5_str = m1.hexdigest()[8:-8]#取中间16位
	
	return md5_str	
	
	
	
def clear_html(content_str):
	content_str = str(content_str)	
	
	content_str = re.sub(r'<div[\s\S]*?>','<div>',content_str)
	content_str = re.sub(r'<p[\s\S]*?>','<p>',content_str)
	content_str = re.sub(r'<strong[\s\S]*?>','<strong>',content_str)
	content_str = re.sub(r'<span[\s\S]*?>','<span>',content_str)
	
	#清除有style样式的标签样式
	content_str = re.sub(r'style=[\s\S]*?>','>',content_str)
	
	#清除文章内的a链接
	content_str = re.sub(r'<a[\s\S]*?>','',content_str)
	content_str = re.sub(r'</a>','',content_str)	
	
	#清除table里的标签样式	
	content_str = re.sub(r'<table[\s\S]*?>','<table>',content_str)
	content_str = re.sub(r'<tbody[\s\S]*?>','<tbody>',content_str)
	content_str = re.sub(r'<tr[\s\S]*?>','<tr>',content_str)
	content_str = re.sub(r'<th[\s\S]*?>','<th>',content_str)
	content_str = re.sub(r'<td[\s\S]*?>','<td>',content_str)
	content_str = re.sub(r'<col[\s\S]*?>','<col>',content_str)
	content_str = re.sub(r'<colgroup[\s\S]*?>','<colgroup>',content_str)		
	#制表、换行
	content_str = content_str.replace('\t','').replace('\n','')			
	
	#敏感词
	content_str = content_str.replace('阿里巴巴','')
	content_str = content_str.replace('淘宝','')
	content_str = content_str.replace('天猫','')
	content_str = content_str.replace('国美','')
	content_str = content_str.replace('苏宁','')
	content_str = content_str.replace('ali','')
	content_str = content_str.replace('alibaba','')
	content_str = content_str.replace('taobao','')
	content_str = content_str.replace('tmall','')
	content_str = content_str.replace('gome','')
	content_str = content_str.replace('suning','')
	content_str = content_str.replace('美乐乐','')
	content_str = content_str.replace('小编','')
	content_str = content_str.replace('【','')
	content_str = content_str.replace('】','')
	content_str = content_str.replace('（','')
	content_str = content_str.replace('）','')	
	content_str = content_str.replace('<span></span>','')	
	

	return content_str	
	
def get_tag(title):	
	tag = ''
	url = '?pagesize=1&qp_disable=no&client=&key=%s'%urllib.quote(title.encode('gbk'))
	r = requests.get(url)
	#JSON.Head.Query.WordSearchInfo.ShowWordOne
	try:
		j_data = json.loads(r.content.decode('gbk').encode('utf-8'))
		tag = j_data["Head"]["Query"]["WordSearchInfo"]["ShowWordOne"]	
	except Exception,e:
		print e		
	if tag:
		return tag
	else:
		return 'jd'	
		
def main():	
	wb = xlwt.Workbook()
	sheet = wb.add_sheet('sheet1')
	sheet.write(0,0,'categoryID')#categoryID帮助中心
	sheet.write(0,1,'status')#status未审核
	sheet.write(0,2,'recommend')#recommend未推荐
	sheet.write(0,3,'type')#type运营添加
	sheet.write(0,4,'tag')#tag标签
	sheet.write(0,5,'source')#文章来源
	sheet.write(0,6,'writer')#作者
	sheet.write(0,7,'md5_id')
	sheet.write(0,8,'title')
	sheet.write(0,9,'description')
	sheet.write(0,10,'content')	
	sheet.write(0,11,'origin_url')
	
	#www.ixinwei.com/2018/01/09/86590.html
	content_url_list = [url.strip() for url in open('z_art_url.txt')]
	
	
	
	for index,k in enumerate(content_url_list):	
		content_str = ''
		content_txt = ''
		title = ''
		try:
			url = k.split(',')[2]
			r = requests.get(url,headers=HeaderData.get_header(),timeout=60)
			s = BeautifulSoup(r.content,"lxml")				
			title = s.find('h1').get_text()
			content_str = s.find('div',attrs={"class":"mod-ctn"})				
			content_txt = str(s.find('div',attrs={"class":"mod-ctn"}).get_text()[0:250]).decode('utf-8')	
			content_str = clear_html(content_str)
		except Exception,e:
			print e			
			with open('error.txt',r'a+') as my:
				my.write(k.strip()+'\n')
		#抓正文规则
		try:			
			sheet.write(index+1,0,categoryID)#categoryID帮助中心
			sheet.write(index+1,1,'1')#status未审核
			sheet.write(index+1,2,'1')#recommend未推荐
			sheet.write(index+1,3,'0')#type运营添加
			sheet.write(index+1,4,get_tag(title))#tag标签
			sheet.write(index+1,5,'jd')#文章来源
			sheet.write(index+1,6,'jd')#作者
			sheet.write(index+1,7,get_title_md5(title))
			sheet.write(index+1,8,title.decode('utf-8'))
			sheet.write(index+1,9,content_txt)
			if len(content_str) < 32767:
				sheet.write(index+1,10,content_str.decode('utf-8'))
			else:
				sheet.write(index+1,10,'String longer than 32767 characters')
				
			sheet.write(index+1,11,k)
			wb.save("result_mama.cn.xls")
		except Exception,e:
			print e		
		print index,url
		#time.sleep(0.5)
if __name__ == '__main__':
	main()
