import requests

import os #allows access to environmental variables

from bs4 import BeautifulSoup, SoupStrainer #beautifulsoup library parses html/xml documents

from model import Book, Author, Location, Category, connect_to_db, db

from sys import argv

from server import app

import xml.etree.ElementTree as ET

#from Google Books
import pprint
import sys
from apiclient.discovery import build

# Note: you must run `source secrets.sh` before running this file
# to make sure these environmental variables are set.


#remember to run source secrets.sh in order to access this environmental variable
# API provided from OS environment dictionary
apikey = os.environ['LIBRARYTHING_DEVELOP_KEY']
google_api_key = os.environ['GOOGLE_API_KEY']

def book_database_seeding(google_api_key, apikey, query):
    response = google_book_search(query)
    isbn_list = create_book_author_instance(response)
    list_tuples_commknow_isbn = get_LT_book_info(apikey, isbn_list)
    create_location_instance(list_tuples_commknow_isbn)
    db.session.commit()

def google_book_search(query):
    """Using the Google Books API to query for books and store information about them."""

    print query

    # The apiclient.discovery.build() function returns an instance of an API service
    # object that can be used to make API calls. The object is constructed with
    # methods specific to the books API. The arguments provided are:
      # name of the API ('books')
      # version of the API you are using ('v1')
      # API key
    service = build('books', 'v1', developerKey=google_api_key)

    # # The books API has a volumes().list() method that is used to list books
    # # given search criteria. Arguments provided are:
    # #   volumes source ('public')
    # #   search query ('android')
    # # The method returns an apiclient.http.HttpRequest object that encapsulates
    # # all information needed to make the request, but it does not call the API.
    request = service.volumes().list(source='public', 
                                    orderBy='relevance', 
                                    printType='books', 
                                    q=query, 
                                    startIndex=0,
                                    maxResults=5,
                                    fields="items(volumeInfo(description,pageCount,categories,publishedDate,imageLinks/thumbnail,title,previewLink,industryIdentifiers,authors,mainCategory))")

    # # The execute() function on the HttpRequest object actually calls the API.
    # # It returns a Python object built from the JSON response. You can print this
    # # object or refer to the Books API documentation to determine its structure.
    response = request.execute()
    print "googled books and results returned"
    return response
   

    # # Accessing the response like a dict object with an 'items' key returns a list
    # # of item objects (books). The item object is a dict object with a 'volumeInfo'
    # # key. The volumeInfo object is a dict with keys 'title' and 'authors'.
def create_book_author_instance(response):
    isbn_list = []
    #this "for loop" iterates through the response dictionary, which consists of books and a 
    #dictionary of information about the books (volumeInfo) as the key and value pair
    for book_dict in response.get('items', []):
        #I only want to store the book if it has an ISBN associated with it (could be an actual value
        # or a None)
        if book_dict.get('volumeInfo', {}).get('industryIdentifiers'):
            isbn_type = book_dict.get('volumeInfo', {}).get('industryIdentifiers')[0].get('type')
            isbn = book_dict.get('volumeInfo', {}).get("industryIdentifiers")[0].get('identifier')
            print isbn
            #Since the value could be "None", this "if" checks for an actual isbn value
            if isbn:
                title = book_dict.get('volumeInfo', {}).get('title')
                print "The title: ", title
                bookauthors = book_dict.get('volumeInfo', {}).get('authors')
                print "Authors: ", bookauthors
                if book_dict.get('volumeInfo').get('categories'):
                    categories = book_dict.get('volumeInfo').get('categories')
                else:
                    categories = None
                print "Categories: ", categories
                description = book_dict.get('volumeInfo', {}).get('description')
                print "Description: ", description
                thumbnail = book_dict.get('volumeInfo', {}).get('imageLinks', {}).get('thumbnail')
                print "Thumbnail link: ", thumbnail
                publishedDate = book_dict.get('volumeInfo', {}).get('publishedDate')
                print "Publication Date: ", publishedDate
                previewLink = book_dict.get('volumeInfo', {}).get("previewLink") 
                print "PreviewLink: ", previewLink
                pageCount = book_dict.get('volumeInfo', {}).get('pageCount')
                
                book = Book(isbn = isbn,
                            title = title,
                            thumbnail_url = thumbnail,
                            description = description,
                            publication_date = publishedDate,
                            preview_link = previewLink,
                            page_count = pageCount)
                isbn_list.append(book.isbn)
                print "an instance of a book created"
                db.session.add(book)

                for name in bookauthors:
                    author = Author(author_name = name)
                    db.session.add(author)
                    book.authors.append(author)
                print "instances of author created"

                for item in categories:
                    category_instance = Category(category = item)
                    db.session.add(category_instance)
                    category_instance.books.append(book)
                
    
        # magic stuff --- something about an isntance of a book referencing the authors 
        # table in model.py and appending location/author to list.....

                        
        # magic stuff --- something about an isntance of a book referencing the authors table 
        # in model.py and appending location/author to list.....
        # book.authors.append(author)
        # book.locations.append(location)
    
    print isbn_list
    print "book instance creation complete"
    # import pdb; pdb.set_trace()
    return isbn_list                   
                

    

def get_LT_book_info(apikey, isbn_list):
    """This function takes a list of book instances, retrieves the isbn of a work (book), and returns the XML of the common knowledge from librarything.
    """
    #TO DO Next I'm going to determine how to parse the text and store important info to a table.
    #TO DO I also need to create a function for geting info by title, but for now, ISBN is pretty good...
    #maybe I will create a function that generates the ISBN of a book based on title
    list_tuples_commknow_isbn = []

    for work in isbn_list:
        work_info = {"method" : "librarything.ck.getwork", "isbn" : work, "apikey" : apikey}
        # creates a class 'requests.models.Response' - prints common work
        work_common_knowledge = requests.get('http://librarything.com/services/rest/1.1/', params=work_info)
        
        if work_common_knowledge:
            # turns common knowledge into a unicode
            work_common_knowledge_unicode = work_common_knowledge.text
            # print work_common_knowledge_unicode
            
            #unicode turned into utf8 in order to write into a file
            work_common_knowledge_utf8 = work_common_knowledge_unicode.encode('utf-8')
    
            list_tuples_commknow_isbn.append((work_common_knowledge_utf8, work))
            # print list_tuples_commknow_isbn
            # import pdb; pdb.set_trace()
    return list_tuples_commknow_isbn
    # print "got the cknowledge"

    # store_text_common_knowledge(work_common_knowledge_utf8, isbn)
    # print "it's been stored"

    # parse_common_knowledge_for_book_info(isbn)   
    # print "it's been parsed"
    # print work_common_knowledge_utf8
    # import pdb; pdb.set_trace()
    #save the common knowledge text to a file
    # store_text_common_knowledge(work_common_knowledge_utf8, isbn)

    # return work_common_knowledge_unicode


def create_location_instance(list_tuples_commknow_isbn):
    # file_to_parse = open(file_name).read()
    # tree = ET.parse(file_name)
    for item in list_tuples_commknow_isbn:
        root = ET.fromstring(item[0])
        ns={'lt':'http://www.librarything.com/'}
        
        #table attributes
        # for child in root:
            # book_title = root.find("lt:ltml", ns).find("lt:item", ns).find("lt:title", ns).text
            # book_copyright = root.find("lt:ltml", ns).find("lt:item", ns).find("lt:commonknowledge", ns).find("lt:fieldList", ns).find("lt:field[@name='originalpublicationdate']", ns).find("lt:versionList", ns).find("lt:version", ns).find("lt:factList",ns).find("lt:fact", ns).text
            # book_avg_rating = root.find("lt:ltml", ns).find("lt:item", ns).find("lt:rating", ns).text
        
        # import pdb; pdb.set_trace()
        #in the ET library, findall() returns a list of objects; iterating over them and extracting the text
        for child in root.findall("./lt:ltml/lt:item/lt:commonknowledge/lt:fieldList/lt:field[@name='placesmentioned']/lt:versionList/lt:version/lt:factList/*",ns):
            place = child.text
            # print place
            place_list = place.split(', ')
            print place_list
            # import pdb; pdb.set_trace()
            # import pdb; pdb.set_trace()
            #only pulling out places that have a city and state listed
            if len(place_list) == 2:
                location = Location(city_county = None,
                                    state = place_list[0],
                                    country = place_list[1])
            elif len(place_list) == 3:
                location = Location(city_county = place_list[0],
                                    state = place_list[1],
                                    country = place_list[2])
            elif len(place_list) == 4:
                location = Location(city_county = place_list[0] + ","+  place_list[1],
                                    state = place_list[2],
                                    country = place_list[3])

            db.session.add(location)
            book = Book.query.get(item[1])
            # import pdb; pdb.set_trace()
            book.locations.append(location)

        if root.find("lt:ltml", ns).find("lt:item", ns).find("lt:commonknowledge", ns).find("lt:fieldList", ns).get("lt:field[@name='firstwords']"):
            first_words = root.find("lt:ltml", ns).find("lt:item", ns).find("lt:commonknowledge", ns).find("lt:fieldList", ns).find("lt:field[@name='firstwords']", ns).find("lt:versionList", ns).find("lt:version", ns).find("lt:factList",ns).find("lt:fact", ns).text.lstrip("<![CDATA[").rstrip("]]>")
            print first_words
            book.first_words = first_words
        
            
            

        # author = root.find("lt:ltml", ns).find("lt:item", ns).find("lt:author", ns).text.split()
        # author_firstname, author_lastname = author[0], author[1]
        # summary = root.find("lt:ltml", ns).find("lt:item", ns).find("lt:commonknowledge", ns).find("lt:fieldList", ns).find("lt:field[@name='description']", ns).find("lt:versionList", ns).find("lt:version", ns).find("lt:factList",ns).find("lt:fact", ns).text.rstrip("]>").lstrip("<![CDATA[")

        # book = Book(isbn = isbn,
        #         book_title = book_title,
        #         book_copyright = book_copyright,
        #         book_avg_rating = book_avg_rating,
        #         summary = summary
        #         )
        # db.session.add(book)

        # author = Author(author_firstname = author_firstname,
        #                 author_lastname = author_lastname
        #                 )
        # #magic stuff --- something about an isntance of a book referencing the authors table in model.py and appending location/author to list.....
        # book.authors.append(author)
        # book.locations.append(location)

        # db.session.commit()

# def store_text_common_knowledge(work_common_knowledge_utf8, isbn):
    # """This function runs through the get_LT_book_info(),
    # takes the common knowledge of a work and saves it to a text file."""
    
    # file_name = str(isbn) + ".xml"
    # print file_name
    # # import pdb; pdb.set_trace()
    # file = open(file_name, "w")
    # file.write(work_common_knowledge_utf8)
    # file.close()

    # return file_name


if __name__ == "__main__":
    connect_to_db(app)

    db.create_all()

    script, query = argv
    book_database_seeding(google_api_key, apikey, query)
    # google_book_search(google_api_key, apikey, query)

    # get_LT_book_info(apikey, isbn)

    # store_text_common_knowledge(work_common_knowledge_utf8, isbn)

    # parse_common_knowledge_for_book_info(isbn)   