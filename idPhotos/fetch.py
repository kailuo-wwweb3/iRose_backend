import sys
import urllib, urllib2, base64
import json
sys.path.insert(0, 'libs')
from bs4 import BeautifulSoup
import unicodedata
from datetime import datetime
import time

f = open('usernames.txt', 'w')
def main():
	quarters = ['200810', '200910']
	usernames = []
	for quarter in quarters:
		url = 'https://prodweb.rose-hulman.edu/regweb-cgi/reg-sched.pl?termcode=' + quarter + '&view=tgrid&id1=&id4=&id5=clsk100&bt5=Course'
		courseIds = fetchCourseIDs(fetchHtml(url))
		for course in courseIds:
			fetchRosters(course, quarter)
	f.close()


def fetchCourseIDs(html):
	soup = BeautifulSoup(html)
	count = 0
	courseIds = []
	for course in soup.findAll(lambda tag: tag.name == 'tr' and len(tag.contents) == 10 and isAlphabet(tag.contents[0].string[-1])):
		if (not count == 0):
			courseIds.append(convertToString(course.contents[0].string))
		else:
			count = count + 1
	return courseIds

def isAlphabet(c):
	return c >= 'A' and c <= 'Z'

def fetchHtml(url):
	request = urllib2.Request(url)
	base64string = base64.encodestring('%s:%s' % ('luok', 'Goseater555555')).replace('\n', '')
	request.add_header("Authorization", "Basic %s" % base64string)   
	return urllib2.urlopen(request).read()


def convertToString(uniString):
	return unicodedata.normalize('NFKD', uniString).encode('ascii','ignore')

def fetchRosters(courseID, termcode):
	url = "https://prodweb.rose-hulman.edu/regweb-cgi/reg-sched.pl?type=Roster&termcode=" + termcode + "&view=tgrid&id=" + courseID

	rosters = []
	soup = BeautifulSoup(fetchHtml(url))
	count = 0
	for tr in soup.findAll(lambda tag: len(tag.contents) == 8 and tag.name == 'tr'):
		if not count == 0:
			contents = tr.contents
			# rosters.append({'username':convertToString(contents[0].string), 'name': convertToString(contents[1].string), 'CM': convertToString(contents[2].string), 'major': convertToString(contents[3].string), 'class': convertToString(contents[4].string), 'year':convertToString(contents[5].string), 'advisor':convertToString(contents[6].string), 'email':convertToString(contents[7].string)})
			username = convertToString(contents[0].string)
			rosters.append(username)
			f.write(username + '\n')
			print 'fetched ----- ' + convertToString(contents[0].string)

		else:
			count = count + 1
	return rosters

if __name__ == "__main__":
    main()