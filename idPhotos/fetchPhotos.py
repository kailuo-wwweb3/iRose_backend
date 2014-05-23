import mechanize
import sys
sys.path.insert(0, 'libs')
from bs4 import BeautifulSoup
import urllib

def main():
	f = open('usernames.txt', 'r')
	for username in f.readlines():
		fetchPhoto(username[:-1])


def fetchPhoto(username):
	br = mechanize.Browser()
	br.set_handle_robots(False)
	page = br.open('http://angel.rose-hulman.edu/home.asp')
	br.select_form(name="frmLogon")
	br['username'] = 'luok'
	br['password'] = 'Goseater555555'
	br.submit()
	page = br.open('http://angel.rose-hulman.edu/UserInfo.asp?id=' + username + '&ONEXIT=%2Fsection%2Fpeople%2Fdefault%2Easp')
	soup = BeautifulSoup(page.read())
	count = 0
	for imgTag in soup.findAll(lambda tag: tag.name == 'img'):
		if count == 1:
			break
		count += 1
	urllib.urlretrieve('http://angel.rose-hulman.edu' + imgTag['src'], '../oldPhotos/' + username + ".jpg")
	print 'fetched .....' + username



if __name__ == "__main__":
    main()