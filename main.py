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


def fetchCoursesBasedOnUsernameAndTerm(username, termcode, login, password):
	courses = []
	url = "https://prodweb.rose-hulman.edu/regweb-cgi/reg-sched.pl?termcode=" + termcode + "&view=tgrid&id1=" + username + "&bt1=ID%2FUsername&id4=&id5="
	html = urlfetch.fetch(url, headers={"Authorization": "Basic %s" % base64.b64encode(login + ":" + password)})
	soup = BeautifulSoup(html.content)
	count = 0
	for tr in soup.findAll(lambda tag: len(tag.contents) == 10 and tag.name == 'tr'):
		if not count == 0:
			courses.append({'course':convertToString(tr.contents[0].string), 'CRN':convertToString(tr.contents[1].string), 'description':convertToString(tr.contents[2].string), 'instructor':convertToString(tr.contents[3].string), 'credit':convertToString(tr.contents[4].string), 'enrl':convertToString(tr.contents[5].string), 'cap':convertToString(tr.contents[6].string), 'schedule':convertToString(tr.contents[7].string), 'comments':convertToString(tr.contents[8].string)})
		count = count + 1
	return {'content':courses}

def fetchCoursesBasedOnUnAccurateCourseID(courseID, termcode, login, password):
	courses = []
	url = "https://prodweb.rose-hulman.edu/regweb-cgi/reg-sched.pl?termcode=" + termcode + "&view=tgrid&id1=&id4=&id5=" + courseID + "&bt5=Course"
	html = urlfetch.fetch(url, headers={"Authorization": "Basic %s" % base64.b64encode(login + ":" + password)})
	soup = BeautifulSoup(html.content)
	count = 0
	for tr in soup.findAll(lambda tag: len(tag.contents) == 10 and tag.name == 'tr'):
		if not count == 0:
			courses.append({'course':convertToString(tr.contents[0].string), 'CRN':convertToString(tr.contents[1].string), 'description':convertToString(tr.contents[2].string), 'instructor':convertToString(tr.contents[3].string), 'credit':convertToString(tr.contents[4].string), 'enrl':convertToString(tr.contents[5].string), 'cap':convertToString(tr.contents[6].string), 'schedule':convertToString(tr.contents[7].string), 'comments':convertToString(tr.contents[8].string)})
		count = count + 1
	return {'content':courses}

def fetchRostersBasedOnCourseID(courseID, termcode, login, password):
	rosters = []
	url = "https://prodweb.rose-hulman.edu/regweb-cgi/reg-sched.pl?type=Roster&termcode="+ termcode + "&view=tgrid&id=" + courseID
	html = urlfetch.fetch(url, headers={"Authorization": "Basic %s" % base64.b64encode(login + ":" + password)})
	soup = BeautifulSoup(html.content)
	count = 0
	for tr in soup.findAll(lambda tag: len(tag.contents) == 8 and tag.name == 'tr'):
		if not count == 0:
			contents = tr.contents
			rosters.append({'username':convertToString(contents[0].string), 'name': convertToString(contents[1].string), 'CM': convertToString(contents[2].string), 'major': convertToString(contents[3].string), 'class': convertToString(contents[4].string), 'year':convertToString(contents[5].string), 'advisor':convertToString(contents[6].string), 'email':convertToString(contents[7].string)})
		count = count + 1
	return {'content':rosters}



def convertToString(uniString):
	return unicodedata.normalize('NFKD', uniString).encode('ascii','ignore')

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
		self.response.headers['Content-Type'] = 'application/json'
		self.response.headers.add_header("Access-Control-Allow-Origin", "*")
		# print output
		self.response.out.write(output)

	def post(self):
		global incoming_request
		incoming_request = SchedulePageRequest(username=self.request.get('username'), termcode=self.request.get('termcode'), login=self.request.get('login'), password=self.request.get('password'))
		self.redirect('/schedule')


incoming_request = None
class CoursesHandler(webapp2.RequestHandler):
	def get(self):
		courseID = incoming_request.courseID
		termcode = incoming_request.termcode
		login = incoming_request.login
		password = incoming_request.password
		output = fetchCoursesBasedOnUnAccurateCourseID(courseID, termcode, login, password)
		self.response.headers['Content-Type'] = 'application/json'
		self.response.headers.add_header("Access-Control-Allow-Origin", "*")
		self.response.out.write(output)
		
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
		self.response.headers['Content-Type'] = 'application/json'
		self.response.headers.add_header("Access-Control-Allow-Origin", "*")
		self.response.out.write(output)



	def post(self):
		global incoming_request
		incoming_request = CourseRostersRequest(courseID=self.request.get('courseID'), termcode=self.request.get('termcode'), login=self.request.get('login'), password=self.request.get('password'))
		self.redirect('/courseRosters')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/schedule', ScheduleHandler),
    ('/courses', CoursesHandler),
    ('/courseRosters', CourseRostersHandler)
], debug=True)
