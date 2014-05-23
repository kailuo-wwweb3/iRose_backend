#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import sys
import urllib, urllib2, base64
import json
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
sys.path.insert(0, 'libs')
from bs4 import BeautifulSoup
import unicodedata
from datetime import datetime
import time
import mechanize


incoming_request = None
idPhotoUserName = None

class Request(ndb.Model):
	login = ndb.StringProperty(default='')
	password = ndb.StringProperty(default='')

class SchedulePageRequest(Request):
	username = ndb.StringProperty(default='')
	termcode = ndb.StringProperty(default='')



class CoursesPageRequest(Request):
	courseID = ndb.StringProperty(default='')
	termcode = ndb.StringProperty(default='')

class CourseRostersRequest(Request):
	courseID = ndb.StringProperty(default='')
	termcode = ndb.StringProperty(default='')

class AdvisorRostersRequest(Request):
	advisorID = ndb.StringProperty(default='')
	termcode = ndb.StringProperty(default='')


def parseRosters(url, advisorID, login, password):
	rosters = []
	html = urlfetch.fetch(url, headers={"Authorization": "Basic %s" % base64.b64encode(login + ":" + password)})
	soup = BeautifulSoup(html.content)
	count = 0
	print advisorID

	for tr in soup.findAll(lambda tag: len(tag.contents) == (8 if advisorID == None else 7) and tag.name == 'tr'):
		if not count == 0:
			contents = tr.contents
			if advisorID == None:
				rosters.append({'username':convertToString(contents[0].string), 'name': convertToString(contents[1].string), 'CM': convertToString(contents[2].string), 'major': convertToString(contents[3].string), 'class': convertToString(contents[4].string), 'year':convertToString(contents[5].string), 'advisor':convertToString(contents[6].string), 'email':convertToString(contents[7].string)})
			else:
				rosters.append({'username':convertToString(contents[0].string), 'name': convertToString(contents[1].string), 'CM': convertToString(contents[2].string), 'major': convertToString(contents[3].string), 'class': convertToString(contents[4].string), 'year':convertToString(contents[5].string), 'advisor': advisorID, 'email':convertToString(contents[6].string)})
		count = count + 1
	return {'content':rosters}

def parseCourses(url, login, password):
	courses = []
	html = urlfetch.fetch(url, headers={"Authorization": "Basic %s" % base64.b64encode(login + ":" + password)})
	soup = BeautifulSoup(html.content)
	count = 0
	for tr in soup.findAll(lambda tag: len(tag.contents) == 10 and tag.name == 'tr'):
		if not count == 0:
			courses.append({'course':convertToString(tr.contents[0].string), 'CRN':convertToString(tr.contents[1].string), 'description':convertToString(tr.contents[2].string), 'instructor':convertToString(tr.contents[3].string), 'credit':convertToString(tr.contents[4].string), 'enrl':convertToString(tr.contents[5].string), 'cap':convertToString(tr.contents[6].string), 'schedule':convertToString(tr.contents[7].string), 'comments':convertToString(tr.contents[8].string)})
		count = count + 1
	return {'content':courses}

def fetchTerms(login, password):
	terms = []
	url = "https://prodweb.rose-hulman.edu/regweb-cgi/reg-sched.pl"
	html = urlfetch.fetch(url, headers={"Authorization": "Basic %s" % base64.b64encode(login + ":" + password)})
	soup = BeautifulSoup(html.content)
	for term in soup.findAll(lambda tag : tag.name == 'option' and isInteger(tag['value'])):
		terms.append({"termCode" : convertToString(term['value']), "termName" : convertToString(term.contents[0])})
	return {'content':terms}

def fetchLatestTerm(login, password):
	terms = []
	url = "https://prodweb.rose-hulman.edu/regweb-cgi/reg-sched.pl"
	html = urlfetch.fetch(url, headers={"Authorization": "Basic %s" % base64.b64encode(login + ":" + password)})
	soup = BeautifulSoup(html.content)
	count = 0
	for term in soup.findAll(lambda tag : tag.name == 'option' and isInteger(tag['value'])):
		if count == 0:
			terms.append({"termCode" : convertToString(term['value']), "termName" : convertToString(term.contents[0])})
		else:
			break
	return {'content':terms}

def isInteger(s):
	try:
		int(s)
		return True
	except ValueError:
		return False

def renderJson(output, s):
	s.response.headers['Content-Type'] = 'application/json'
	s.response.headers.add_header("Access-Control-Allow-Origin", "*")
	s.response.out.write(json.dumps(output))

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

	# urllib.urlretrieve('http://angel.rose-hulman.edu' + imgTag['src'], 'photos/' + username + ".jpg")
	return 'http://angel.rose-hulman.edu' + imgTag['src']


def fetchCoursesBasedOnUsernameAndTerm(username, termcode, login, password):
	url = "https://prodweb.rose-hulman.edu/regweb-cgi/reg-sched.pl?termcode=" + termcode + "&view=tgrid&id1=" + username + "&bt1=ID%2FUsername&id4=&id5="
	return parseCourses(url, login, password)

def fetchCoursesBasedOnUnAccurateCourseID(courseID, termcode, login, password):
	url = "https://prodweb.rose-hulman.edu/regweb-cgi/reg-sched.pl?termcode=" + termcode + "&view=tgrid&id1=&id4=&id5=" + courseID + "&bt5=Course"
	return parseCourses(url, login, password)

def fetchRostersBasedOnAdvisor(advisorID, termcode, login, password):
	url = "https://prodweb.rose-hulman.edu/regweb-cgi/reg-sched.pl?type=Advisor&termcode="+ termcode + "&view=tgrid&id=" + advisorID
	return parseRosters(url, advisorID, login, password)

def fetchRostersBasedOnCourseID(courseID, termcode, login, password):
	url = "https://prodweb.rose-hulman.edu/regweb-cgi/reg-sched.pl?type=Roster&termcode="+ termcode + "&view=tgrid&id=" + courseID
	return parseRosters(url, None, login, password)



def convertToString(uniString):
	return unicodedata.normalize('NFKD', uniString).encode('ascii','ignore')

def fetchIDPhoto(username):
	url = "http://angel.rose-hulman.edu/section/default.asp?id=GROUP-ALL"
	html = urlfetch.fetch(url)
	return html.content

class MainHandler(webapp2.RequestHandler):
	def get(self):
		self.response.out.write("this works!")
		



class ScheduleHandler(webapp2.RequestHandler):
	def get(self):
		username = incoming_request.username
		termcode = incoming_request.termcode
		login = incoming_request.login
		password = incoming_request.password
		output = fetchCoursesBasedOnUsernameAndTerm(username, termcode, login, password)
		renderJson(output, self)

	def post(self):
		global incoming_request
		print self.request
		incoming_request = SchedulePageRequest(username=self.request.get('username'), termcode=self.request.get('termcode'), login=self.request.get('login'), password=self.request.get('password'))
		self.redirect('/schedule')



class CoursesHandler(webapp2.RequestHandler):
	def get(self):
		courseID = incoming_request.courseID
		termcode = incoming_request.termcode
		login = incoming_request.login
		password = incoming_request.password
		output = fetchCoursesBasedOnUnAccurateCourseID(courseID, termcode, login, password)
		renderJson(output, self)

	def post(self):
		global incoming_request
		incoming_request = CoursesPageRequest(courseID=self.request.get('courseID'), termcode=self.request.get('termcode'), login=self.request.get('login'), password=self.request.get('password'))
		self.redirect('/courses')


class CourseRostersHandler(webapp2.RequestHandler):
	def get(self):
		courseID = incoming_request.courseID
		termcode = incoming_request.termcode
		login = incoming_request.login
		password = incoming_request.password
		output = fetchRostersBasedOnCourseID(courseID, termcode, login, password)
		renderJson(output, self)

	def post(self):
		global incoming_request
		incoming_request = CoursesPageRequest(courseID=self.request.get('courseID'), termcode=self.request.get('termcode'), login=self.request.get('login'), password=self.request.get('password'))
		print incoming_request
		self.redirect('/courseRosters')

class AdvisorRostersHandler(webapp2.RequestHandler):
	def get(self):
		print "aaaaaa"
		advisorID = incoming_request.advisorID
		termcode = incoming_request.termcode
		login = incoming_request.login
		password = incoming_request.password
		output = fetchRostersBasedOnAdvisor(advisorID, termcode, login, password)
		renderJson(output, self)


	def post(self):
		global incoming_request
		incoming_request = AdvisorRostersRequest(advisorID=self.request.get('advisorID'), termcode=self.request.get('termcode'), login=self.request.get('login'), password=self.request.get('password'))
		self.redirect('/advisorRosters')

class TermsFetcherHandler(webapp2.RequestHandler):
	def get(self):
		login = incoming_request.login
		password = incoming_request.password
		renderJson(fetchTerms(login, password), self)

	def post(self):
		global incoming_request
		print "getting here!!!"
		print self.request
		incoming_request = Request(login=self.request.get('login'), password=self.request.get('password'))
		self.redirect('/terms')



class IDphotoFetcherHandler(webapp2.RequestHandler):
	def get(self):
		imageUrl = fetchPhoto(idPhotoUserName)
		self.response.out.write(imageUrl)


	def post(self):
		global idPhotoUserName
		idPhotoUserName = self.request.get('username')
		self.redirect('/IDphoto')

class LoginValidation(webapp2.RequestHandler):
	def get(self):
		response = urlfetch.fetch('https://prodweb.rose-hulman.edu/regweb-cgi/reg-sched.pl', headers={"Authorization": "Basic %s" % base64.b64encode('luok' + ":" + 'Goseater555555')})
		if (response.status_code == 200):
			self.response.out.write('valid')
		else:
			self.response.out.write('invalid')

	def post(self):
		global incoming_request
		incoming_request = Request(login=self.request.get('login'), password=self.request.get('password'))
		self.redirect('/validateLogin')



app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/schedule', ScheduleHandler),
    ('/courses', CoursesHandler),
    ('/courseRosters', CourseRostersHandler),
    ('/advisorRosters', AdvisorRostersHandler),
    ('/terms', TermsFetcherHandler),
    ('/IDphoto', IDphotoFetcherHandler),
    ('/validateLogin', LoginValidation)
], debug=True)
