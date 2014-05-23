import sys
import urllib, urllib2, base64
sys.path.insert(0, 'libs')
from bs4 import BeautifulSoup
import mechanize

def main():
	br = mechanize.Browser()
	br.set_handle_robots(False)
	page = br.open('http://y.qq.com/#type=soso&p=%3Fmid%3D1%26p%3D1%26catZhida%3D1%26lossless%3D0%26t%3D100%26searchid%3D26711531258859451%26remoteplace%3Dtxt.yqqlist.top%26utf8%3D1%26w%3D%25E5%2591%25A8%25E6%259D%25B0%25E4%25BC%25A6')
	print page.read()




if __name__ == "__main__":
    main()