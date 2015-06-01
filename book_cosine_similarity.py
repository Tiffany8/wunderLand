from server import app
from model import Book, Author, Location, Category, Event, Award, connect_to_db, db
from flask_sqlalchemy import SQLAlchemy

import nltk
import string
import re
from nltk.corpus import stopwords


def main_func():
	list_of_book_objects = Book.query.filter(Book.title.ilike('war%')).all()

	for book_obj in list_of_book_objects:

		if book_obj.description:

			print "book title", book_obj.title
			tokens_list = get_tokens(book_obj)
			print "tokens list", len(tokens_list), tokens_list
			print "#" * 20
			tokens_list_filtered = remove_stopwords(tokens_list)
			print "filtered tokens list", len(tokens_list_filtered), tokens_list_filtered
			print "#" * 20
			stemmed_tokens = stem_tokens(tokens_list_filtered)
			print "stemmed tokens", stemmed_tokens
			print "#" * 40

def get_tokens(book_obj):

		#remove all punctuation except ' and - and lowercases words
		book_descrip_no_punc = re.split(r"[^\w]", book_obj.description.lower()) 
	
		return book_descrip_no_punc

def remove_stopwords(tokens_list):

	tokens_list_filtered = [word for word in tokens_list if not word in stopwords.words('english')]
	
	return tokens_list_filtered

def stem_tokens(tokens_list_filtered):
	stemmer = nltk.stem.porter.PorterStemmer()
	stemmed_tokens = [stemmer.stem_word(word) for word in tokens_list_filtered]
	return stemmed_tokens


if __name__ == "__main__":
    connect_to_db(app)
    db.create_all()
    main_func()