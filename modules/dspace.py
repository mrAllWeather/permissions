from HTMLParser import HTMLParser
import urllib2

class MyHTMLParser(HTMLParser):
	myDict = {}
	currentHeader = None
	def handle_starttag(self, tag, attrs):
		#print "Start tag:", tag
		if tag == 'meta':	
			self.currentHeader = attrs[0][1]

			if self.currentHeader in self.myDict:
				self.myDict[self.currentHeader].append(attrs[1][1])
			else:
				self.myDict[self.currentHeader] = [attrs[1][1],]

			#for attr in attrs:
			#print "     attr:", attr


	def handle_endtag(self, tag):
		return
		#print "End tag  :", tag

	def handle_data(self, data):
		return
		#print "Data     :", data

if __name__ == "__main__":
	f = urllib2.urlopen('http://hdl.handle.net/2440/79437')
	parser = MyHTMLParser()
	parser.feed(f.read())
	for key, value in parser.myDict.iteritems() :
		print key, value
