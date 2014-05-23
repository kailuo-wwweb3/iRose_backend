import urllib
import urllib2

url = 'http://localhost:8080/schedule'
values = {'login' : 'luok', 'password' : 'Goseater555555', 'username' : 'luok', 'termcode' : '201210'}

data = urllib.urlencode(values)
req = urllib2.Request(url, data)
print req.get_full_url()
response = urllib2.urlopen(req)
the_page = response.read()
print the_page