import csv, urllib2, requests
from httpcache import CachingHTTPAdapter
import xml.etree.cElementTree as ET

def searchXML(term, root):
	values = []
	for item in root.iter(term):
		values.append(item.text)

	if(len(values)==1):
		return values.pop()
	else:
		return values

def XMLRequest(issn):
	current_session = requests.Session()
	current_session.mount('http://', CachingHTTPAdapter())
	requestUrl = 'http://www.sherpa.ac.uk/romeo/api29.php?issn=' + issn + '&ak=KmBygYx06X6'
	response = current_session.get(requestUrl)
	xmlRoot = ET.fromstring(response.text.encode('utf-8'))
	
	return xmlRoot

def AskSherpa(issn):
	root = XMLRequest(issn)
	output = {}
	output['journal'] = searchXML('jtitle', root)
	output['publisher'] = searchXML('romeopub', root)
	output['publisher_url'] = searchXML('homeurl', root)
	output['submitted'] = searchXML('prearchiving', root)
	output['accepted'] = searchXML('postarchiving', root)
	output['published'] = searchXML('pdfversion', root)
	output['permission_link'] = searchXML('copyrightlinkurl', root)
	output['permission_text'] = searchXML('condition', root)
	output['outcome'] = searchXML('outcome', root)

	return output

