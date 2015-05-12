import requests

import os #allows access to environmental variables

# import pdb; pdb.set_trace()

# payload = {'key1': 'value1', 'key2': 'value2'}
# r = requests.get("http://httpbin.org/get", params=payload)
# print(r.url)

# Note: you must run `source secrets.sh` before running this file
# to make sure these environmental variables are set.


#remember to run source secrets.sh in order to access this environmental variable
apikey = os.environ['LIBRARYTHING_DEVELOP_KEY']


def get_work_common_knowledge_by_isbn(apikey, isbn):
	"""This function takes the isbn of a work (book), and returns the XML of the common knowledge from librarything.
	"""
	#TO DO Next I'm going to determine how to parse the text and store important info to a table.
	#TO DO I also need to create a function for geting info by title.
	work_info = {"method" : "librarything.ck.getwork", "isbn" : isbn, "apikey" : apikey}
	# print work_info
	work_common_knowledge_text = requests.get('http://librarything.com/services/rest/1.1/', params=work_info)
	# print work_common_knowledge_text
	print work_common_knowledge_text
	return work_common_knowledge_text.text

# import requests
# r = requests.get('https://api.github.com/events')
# r.text



#To DO figure out what goes in here!
# if name == "__main__":
# 	pass