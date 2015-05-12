import requests

import os #allows access to environmental variables

from bs4 import BeautifulSoup, SoupStrainer #beautifulsoup library parses html/xml documents

from model import connect_to_db, db

from sys import argv

import xml.etree.ElementTree as ET

# Note: you must run `source secrets.sh` before running this file
# to make sure these environmental variables are set.


#remember to run source secrets.sh in order to access this environmental variable
apikey = os.environ['LIBRARYTHING_DEVELOP_KEY']


def get_work_common_knowledge_by_isbn(apikey, isbn):
	"""This function takes the isbn of a work (book), and returns the XML of the common knowledge from librarything.
	"""
	#TO DO Next I'm going to determine how to parse the text and store important info to a table.
	#TO DO I also need to create a function for geting info by title, but for now, ISBN is pretty good...
	#maybe I will create a function that generates the ISBN of a book based on title
	work_info = {"method" : "librarything.ck.getwork", "isbn" : isbn, "apikey" : apikey}
	# creates a class 'requests.models.Response' - prints common work
	work_common_knowledge = requests.get('http://librarything.com/services/rest/1.1/', params=work_info)
	
	# turns common knowledge into a unicode
	work_common_knowledge_unicode = work_common_knowledge.text
	
	#unicode turned into utf8 in order to write into a file
	work_common_knowledge_utf8 = work_common_knowledge_unicode.encode('utf-8')
	# import pdb; pdb.set_trace()
	#save the common knowledge text to a file
	store_text_common_knowledge(work_common_knowledge_utf8, isbn)

	return work_common_knowledge_unicode


def store_text_common_knowledge(text,isbn):
 	"""This function runs through the get_work_common_knowledge_by_isbn(),
 	takes the common knowledge of a work and saves it to a text file."""
 	
 	file_name = str(isbn) + ".xml"
 	# import pdb; pdb.set_trace()
 	file = open(file_name, "w")
 	file.write(text)
 	file.close()


def parse_common_knowledge_unicode(isbn):
	file_to_parse = open(str(isbn)+".xml").read()
	tree = ET.parse(str(isbn)+".xml")
	root = tree.getroot()
	ns={'lt':'http://www.librarything.com/'}
	root.findall("lt:ltml", ns)
	# import pdb; pdb.set_trace()
	# return root.findall("lt:ltml", ns)

	for placesmentioned in root.findall("./lt:ltml/lt:item/lt:commonknowledge/lt:fieldList/lt:field[@name='placesmentioned']/lt:versionList/lt:version/lt:factList/*",ns):
		print placesmentioned.text
	# root = ET.fromstring(file_to_parse)
	# test = root.findall("./ltml/item/commonknowledge/fieldList")
	# import pdb; pdb.set_trace()
	# return test


	# file_to_parse = open(str(isbn)+".xml").read()
	# soup = BeautifulSoup(file_to_parse, 'xml')
	
	# placesmentioned = soup.find("field", attrs={"name":"placesmentioned"})

	# only_placesmentioned_name = SoupStrainer(name="placesmentioned")
	# # placesmentioned = soup.find_all("field")
	# import pdb; pdb.set_trace()

	# # test = placesmentioned.contents
	# # print getattr(placesmentioned)
	# print type(placesmentioned)
	# print placesmentioned

	

#To DO figure out what goes in here!
if __name__ == "__main__":
	# connect_to_db(app)

    # db.create_all()

    script, isbn = argv
    # import pdb; pdb.set_trace()
    # get_work_common_knowledge_by_isbn(apikey, isbn)

    parse_common_knowledge_unicode(isbn)
   