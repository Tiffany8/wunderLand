
from model import Book, connect_to_db, db
from flask_sqlalchemy import SQLAlchemy

from server import app
from sqlalchemy import exc
import pickle
import re

def seed_keywords():
    all_book_objs = Book.query.all()

    keyword_dictionary = {}

    #create a gigantic list of ALL of the book objects
    for book_obj in all_book_objs:
        print "Starting iteration through book: ", book_obj.title
        print "book obj: ", book_obj
        print 
        print
        #pull out the descriptions for each book object
        description_string = book_obj.description
        print "book description: ", description_string
        print
        print
        #use regular expressions to remove all punctuation except ' and -
        #may check out NLTK
        if description_string:
            description_string = description_string.replace("--", " ")
            print "description string after replacement: ", description_string
            print
            print
            description_list = re.split(r"[^\w'-]", description_string)
            print "description list after regex: ", description_list
            print
            print

            #for each word in the description, add it as a key to the dictionary
            #and hold the tally as the value
            for word in description_list:
                print "word", word
                print 
                print
                keyword_dictionary[word] = keyword_dictionary.get(word.lower(), 0) + 1
        print "Done with, ", book_obj.title
        print "#" * 40
        print "#" * 40
        print "#" * 40
    pickle.dump(keyword_dictionary, open( "keyword_dictionary.p", "wb" ))

            #   if not keyword_dictionary[word]:
            #     keyword_dictionary[word] = 1
            # else:
            #     keyword_dictionary[word] = keyword_dictionary[word] + 1

            ### How to keep track of books I've already tallied?? --- print statements
            ### should I remove the spaces??
            ### do I import the dictionary file? -- file write

if __name__ == "__main__":
    connect_to_db(app)
    seed_keywords()
