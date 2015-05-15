import requests

import os #allows access to environmental variables

from bs4 import BeautifulSoup, SoupStrainer #beautifulsoup library parses html/xml documents

from model import Book, Author, Location, connect_to_db, db

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
apikey = os.environ['LIBRARYTHING_DEVELOP_KEY']
google_api_key = os.environ['GOOGLE_API_KEY']


def google_search_for_books(google_api_key, apikey, query):
    """Using the Google Books API to query for books and store information about them."""

    print query
    #!/usr/bin/python

    # API provided from OS environment
    

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
                                    fields="items(volumeInfo(description,pageCount,categories,publishedDate,imageLinks/thumbnail,previewLink,industryIdentifiers,authors,mainCategory)),totalItems")

    # # The execute() function on the HttpRequest object actually calls the API.
    # # It returns a Python object built from the JSON response. You can print this
    # # object or refer to the Books API documentation to determine its structure.
    
    response = request.execute()
   

    # # Accessing the response like a dict object with an 'items' key returns a list
    # # of item objects (books). The item object is a dict object with a 'volumeInfo'
    # # key. The volumeInfo object is a dict with keys 'title' and 'authors'.

    

    #add this stuff to database
    for book in response.get('items', []):
        if book.get('volumeInfo', {}).get('industryIdentifiers'):
            isbn_type = book.get('volumeInfo', {}).get('industryIdentifiers')[0].get('type')
            isbn = book.get('volumeInfo', {}).get("industryIdentifiers")[0].get('identifier')
            print isbn
            if isbn:
                title = book.get('volumeInfo', {}).get('title')
                # print "The title: ", title
                authors = ", ".join(book.get('volumeInfo').get('authors'))
                # print "Authors: ", authors
                if book.get('volumeInfo').get('categories'):
                    categories = ", ".join(book.get('volumeInfo').get('categories')) 
                else:
                    categories = None
                # print "Categories: ", categories
                description = book.get('volumeInfo', {}).get('description')
                # print "Description: ", description
                thumbnail = book.get('volumeInfo', {}).get('imageLinks', {}).get('thumbnail')
                # print "Thumbnail link: ", thumbnail
                publishedDate = book.get('volumeInfo', {}).get('publishedDate')
                # print "Publication Date: ", publishedDate
                previewLink = book.get('volumeInfo', {}).get("previewLink") 
                # print "PreviewLink: ", previewLink
                pageCount = book.get('volumeInfo', {}).get('pageCount')
                # print pageCount
                # print isbn_type, isbn   
                print "googled books"
                work_common_knowledge_utf8 = get_work_common_knowledge_by_isbn(apikey, isbn)
                print "got the cknowledge"
                file_name = store_text_common_knowledge(work_common_knowledge_utf8, isbn)
                print "it's been stored"

                parse_common_knowledge_for_book_info(file_name, isbn)   
                print "it's been parsed"


                # print "common knowledge retrieved"

                # store_text_common_knowledge(commknow_utf8,isbn)

                # print "text stored"
        
                # parse_common_knowledge_for_book_info(file_name)

                # print "info parsed"


    print "search complete"

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
    # print work_common_knowledge_unicode
    
    #unicode turned into utf8 in order to write into a file
    work_common_knowledge_utf8 = work_common_knowledge_unicode.encode('utf-8')
    return work_common_knowledge_utf8
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


def store_text_common_knowledge(work_common_knowledge_utf8, isbn):
    """This function runs through the get_work_common_knowledge_by_isbn(),
    takes the common knowledge of a work and saves it to a text file."""
    
    file_name = str(isbn) + ".xml"
    print file_name
    # import pdb; pdb.set_trace()
    file = open(file_name, "w")
    file.write(work_common_knowledge_utf8)
    file.close()

    return file_name


def parse_common_knowledge_for_book_info(file_name, isbn):
    file_to_parse = open(file_name).read()
    tree = ET.parse(file_name)
    root = tree.getroot()
    ns={'lt':'http://www.librarything.com/'}
    print "made it here"
    #table attributes
    # for child in root:
        # book_title = root.find("lt:ltml", ns).find("lt:item", ns).find("lt:title", ns).text
        # book_copyright = root.find("lt:ltml", ns).find("lt:item", ns).find("lt:commonknowledge", ns).find("lt:fieldList", ns).find("lt:field[@name='originalpublicationdate']", ns).find("lt:versionList", ns).find("lt:version", ns).find("lt:factList",ns).find("lt:fact", ns).text
        # book_avg_rating = root.find("lt:ltml", ns).find("lt:item", ns).find("lt:rating", ns).text

    #in the ET library, findall() returns a list of objects; iterating over them and extracting the text
    for child in root.findall("./lt:ltml/lt:item/lt:commonknowledge/lt:fieldList/lt:field[@name='placesmentioned']/lt:versionList/lt:version/lt:factList/*",ns):
        place = child.text
        # print place
        place_list = place.split(', ')
        print place_list
        # import pdb; pdb.set_trace()
        #only pulling out places that have a city and state listed
        # if len(place_list) == 3:
        #     location = Location(location_code=place,
        #                         location_city = place_list[0],
        #                         location_state = place_list[1],
        #                         location_country = place_list[2])
        # elif len(place_list) == 2:
        #     location = Location(location_code = place,
        #                         location_city = None,
        #                         location_state = place_list[1],
        #                         location_country = place_list[2])
        # db.session.add(location)
        # db.session.add(location)
            
            

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



if __name__ == "__main__":
    connect_to_db(app)

    # db.create_all()

    script, query = argv

    google_search_for_books(google_api_key, apikey, query)

    # get_work_common_knowledge_by_isbn(apikey, isbn)

    # store_text_common_knowledge(work_common_knowledge_utf8, isbn)

    # parse_common_knowledge_for_book_info(isbn)   