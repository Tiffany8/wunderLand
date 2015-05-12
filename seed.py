import requests

import os #allows access to environmental variables

from bs4 import BeautifulSoup #beautifulsoup library parses html/xml documents

from model import connect_to_db, db

from sys import argv

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
	
	# turns common knowledge into a unicdoe
	work_common_knowledge_unicode = work_common_knowledge.text
	#TO DO -- figure out how to change the unicode to text!!!
	work_common_knowledge_text.encode('utf-8')
	#save the common knowledge text to a file
	# store_text_common_knowledge(work_common_knowledge_text.text, isbn)
	print type(work_common_knowledge_text)
	print type(work_common_knowledge_text.text)
	# return work_common_knowledge_text.text



def store_text_common_knowledge(text,isbn):
 	"""This function runs through the get_work_common_knowledge_by_isbn(),
 	takes the common knowledge of a work and saves it to a text file."""
 	
 	file_name = str(isbn) + ".txt"
 	# import pdb; pdb.set_trace()
 	file = open(file_name, "w")
 	file.write(text)
 	file.close()



#To DO figure out what goes in here!
if __name__ == "__main__":
	# connect_to_db(app)

    # db.create_all()

    script, isbn = argv

    get_work_common_knowledge_by_isbn(apikey, isbn)
   