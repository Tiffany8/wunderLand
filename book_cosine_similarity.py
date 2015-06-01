import nltk
import string
import re

def main_func():
	list_of_book_objects = Book.query.filter(Book.title.ilike('war%')).all()
	for book_obj in list_of_book_objects:
		tokens = get_tokens()
		print tokens

def get_tokens():
			#remove all punctuation except ' and - and lowercases words
			book_descrip_no_punc = re.split(r"[^\w'-]", book_obj.description.lower()) 
			#or should I remove all punctuation, including apostrophes and dashes?
			
			return book_descrip_no_punc