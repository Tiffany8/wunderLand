import requests

import os # allows access to environmental variables

from bs4 import BeautifulSoup, SoupStrainer #beautifulsoup library parses html/xml documents

from model import Book, Author, Location, Category, Quote, Event, Character, Award, connect_to_db, db

from sys import argv

import sys;
reload(sys);
sys.setdefaultencoding("utf8")


from server import app

import xml.etree.ElementTree as ET

from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import exc

from datetime import datetime

import pprint
import sys
from apiclient.discovery import build

import geocoder
from random_words import RandomWords
from keyword_seeding_using_nltk import *



# Maximum number of results to return. (integer, 0-40)
MAX_RESULTS = 20
# Index of the first result to return (starts at 0) (integer, 0+)
START_INDEX = 0


# # Note: you must run `source secrets.sh` before running this file
# # to make sure these environmental variables are set.
apikey = os.environ['LIBRARYTHING_DEVELOP_KEY']
google_api_key = os.environ['GOOGLE_API_KEY']

def seed_database_from_list_of_authors():
    """This file parses through a text file containing a list of the top 1000 authors (according to LibraryThing), and 
    creates an 'in author' query that author's name in Google Books and return the top twenty relevant works by the author.  
    The query is run through the book_database_seeding function to seed the database and also through the extracting_keywords_from_text
    function (from the keyword_seeding_using_nltk.py file) in order to seed the database with keywords/keyword phrases 
    associated with the books."""

    max_results = MAX_RESULTS
    total_query = 0
    queries = []
    file = open("list_of_authors.txt").read()
    authors_list = file.split("\n")
    while total_query < 200:
        for author in authors_list:
            query = ""
            name = author[:-9].split()
            for a_name in name:
                query = query + "inauthor:" + a_name + " "
            print query
            list_of_book_objects = book_database_seeding(google_api_key, apikey, query)
            extracting_keywords_from_text(list_of_book_objects)
            db.session.commit()
            total_query = total_query + max_results
            print total_query
            print "#" * 40
            print "#" * 40
            print "#" * 40
            queries.append(query)
        print queries


def book_database_seeding(google_api_key, apikey, query):
    """Main fuction that runs the helper functions below to
    search for books and seed the database with information. """
    response = google_book_search(query)
    isbn_list, list_of_book_objects = create_book_author_instance(response)
    list_tuples_commknow_isbn = get_LT_book_info(apikey, isbn_list)
    create_location_instance(list_tuples_commknow_isbn)
    get_longitude_latitude_of_location()
    print "Querying and seeding complete"
    return list_of_book_objects


def google_book_search(query):
    """Using the Google Books API to query for books and store information about them."""

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
                                    langRestrict='en',
                                    q=query,
                                    startIndex=START_INDEX,
                                    maxResults=MAX_RESULTS,
                                    fields="items(volumeInfo(description,pageCount,categories,publishedDate,imageLinks/thumbnail,title,previewLink,industryIdentifiers,subtitle,authors,ratingsCount,mainCategory,averageRating))")


    # # The execute() function on the HttpRequest object actually calls the API.
    # # It returns a Python object built from the JSON response. You can print this
    # # object or refer to the Books API documentation to determine its structure.
    response = request.execute()
    print "googled books and results returned"
    return response


    # # Accessing the response like a dict object with an 'items' key returns a list
    # # of JSON objects for each book. The item object is a dict object with a 'volumeInfo'
    # # key. The volumeInfo object is a dict with keys 'title' and 'authors'.
def create_book_author_instance(response):
    """This function takes a list of JSON objects for each book from the Google Book query and retrieves
    information from the JSON (isbn, title, author(s), cateogry, description, thumbnail link, published date, 
    preview link, page count, ratings count, average ratings), and creates an instance of each book to store in 
    the database.  Categories and author information are also appended to separate association tables."""
    isbn_list = []
    list_of_book_objects = []
    # # this "for loop" iterates through the response dictionary, which consists of books and a
    # # dictionary of information about the books (volumeInfo) as the key and value pair
    for book_dict in response.get('items', []):
        # #I only want to store the book if it has an ISBN associated with it (could be an actual value
        # # or a None)
        if book_dict.get('volumeInfo', {}).get('industryIdentifiers'):
            isbn_type = book_dict.get('volumeInfo', {}).get('industryIdentifiers')[0].get('type')
            isbn = book_dict.get('volumeInfo', {}).get("industryIdentifiers")[0].get('identifier')
            print isbn

            # # Since the value could be "None", this "if" checks for an actual isbn value
            if isbn:
                title = book_dict.get('volumeInfo', {}).get('title')
                print "The title: ", title
                subtitle = book_dict.get('volumeInfo', {}).get('subtitle')

                bookauthors = book_dict.get('volumeInfo', {}).get('authors')
                print "Authors: ", bookauthors
                if book_dict.get('volumeInfo').get('categories'):
                    categories = book_dict.get('volumeInfo').get('categories')
                else:
                    categories = None

                mainCategory = book_dict.get('volumeInfo').get('mainCategory')

                description = book_dict.get('volumeInfo', {}).get('description')

                thumbnail = book_dict.get('volumeInfo', {}).get('imageLinks', {}).get('thumbnail')


                publishedDate_unformated = book_dict.get('volumeInfo', {}).get('publishedDate')
                if publishedDate_unformated:
                    try:
                        if len(publishedDate_unformated)  > 8:
                            published_Date = datetime.strptime(publishedDate_unformated, "%Y-%m-%d")
                        elif len(publishedDate_unformated) < 5:
                            published_Date = datetime.strptime(publishedDate_unformated, "%Y")
                        else:
                            published_Date = datetime.strptime(publishedDate_unformated, "%Y-%m")
                    except:
    
                        print "Publication date formating errors for: ", title

                else:
                    published_Date = None

                previewLink = book_dict.get('volumeInfo', {}).get("previewLink")
                print "PreviewLink: ", previewLink
                pageCount = book_dict.get('volumeInfo', {}).get('pageCount')
                ratingsCount = book_dict.get('volumeInfo', {}).get('ratingsCount')
                averageRatings = book_dict.get('volumeInfo', {}).get('averageRating')

                book = Book(isbn = isbn,
                            title = title,
                            subtitle = subtitle,
                            main_category = mainCategory,
                            thumbnail_url = thumbnail,
                            description = description,
                            publication_date = published_Date,
                            preview_link = previewLink,
                            page_count = pageCount,
                            ratings_count = ratingsCount,
                            average_ratings = averageRatings)

                if not Book.query.get(book.isbn):
                    db.session.add(book)
                    list_of_book_objects.append(book)
                    isbn_list.append(book.isbn)
                    print "an instance of a book created"
                    if bookauthors:
                        for name in bookauthors:
                            author = Author(author_name = name)
                            db.session.add(author)
                            book.authors.append(author)
                        print "instances of author created"
                    if categories:
                        for item in categories:
                            # some categories are longer than 40 characters and causing breaks in seeding loop
                            if len(item) > 40:
                                item = item[:40]
                            category_instance = Category(category = item)
                            if not Category.query.filter_by(category = item).all():
                                db.session.add(category_instance)
                            category_instance.books.append(book)

                else:
                    print "This book ", book.title, "isbn: ", book.isbn, " already exist in the database!"
    print isbn_list
    print "book instance creation complete"

    return isbn_list, list_of_book_objects



def get_LT_book_info(apikey, isbn_list):
    """This function takes a list of book instances, retrieves the isbn of a work (book), and returns the XML 
    of the common knowledge from librarything.
    """
    list_tuples_commknow_isbn = []

    for work in isbn_list:
        work_info = {"method" : "librarything.ck.getwork", "isbn" : work, "apikey" : apikey}

        work_common_knowledge = requests.get('http://librarything.com/services/rest/1.1/', params=work_info)

        if work_common_knowledge:
         
            work_common_knowledge_unicode = work_common_knowledge.text

            list_tuples_commknow_isbn.append((work_common_knowledge_unicode, work))

    return list_tuples_commknow_isbn


def create_location_instance(list_tuples_commknow_isbn):
    """This function takes a list of tuples containing the common knowledge for each book and its isbn.  Each common knowledge
    is parsed for the 'places mentioned'.  An instance of a location is created for each place mentioned and stored in the database
    in the locations table and the book-location association table. """
    

    for item in list_tuples_commknow_isbn:
        try:
            commonknowledge = item[0]
            isbn = item[1]
            book = Book.query.get(isbn)
            print "book:", book
            print isbn
            root = ET.fromstring(commonknowledge)
      
            ns={'lt':'http://www.librarything.com/'}
           
            for child in root.findall("./lt:ltml/lt:item/lt:commonknowledge/lt:fieldList/lt:field[@name='placesmentioned']/lt:versionList/lt:version/lt:factList/*",ns):
                place = child.text

                place_list = place.split(', ')
                print place_list
                
                if "D.C." in place_list:
                    location = Location(city_county = place_list[:-1],
                                        state = None,
                                        country = place_list[-1])
                else:
                    if len(place_list) == 2:
                        location = Location(city_county = None,
                                            state = place_list[0],
                                            country = place_list[1])
                        db.session.add(location)
                        book.locations.append(location)
                    elif len(place_list) == 3:
                        location = Location(city_county = place_list[0],
                                            state = place_list[1],
                                            country = place_list[2])
                        db.session.add(location)
                        book.locations.append(location)
                    elif len(place_list) == 4:
                        location = Location(city_county = place_list[0] + ", "+  place_list[1],
                                            state = place_list[2],
                                            country = place_list[3])
                    db.session.add(location)
                    book.locations.append(location)

            # WARNING/FYI: FutureWarning: The behavior of this method will change in
            # future versions.  Use specific 'len(elem)' or 'elem is not None' test instead.
            if root.find("lt:ltml", ns) is not None:
                if root.find("lt:ltml", ns).find("lt:item", ns) is not None:
                    if root.find("lt:ltml", ns).find("lt:item", ns).find("lt:commonknowledge", ns) is not None:
                        if root.find("lt:ltml", ns).find("lt:item", ns).find("lt:commonknowledge", ns).find("lt:fieldList", ns) is not None:

                            if root.find("lt:ltml", ns).find("lt:item", ns).find("lt:commonknowledge", ns).find("lt:fieldList", ns).find("lt:field[@name='events']", ns) is not None:
                                for child in root.findall("./lt:ltml/lt:item/lt:commonknowledge/lt:fieldList/lt:field[@name='events']/lt:versionList/lt:version/lt:factList/",ns):
                                    event = child.text
                                    event_instance = Event(event=event)
                                    if not Event.query.filter_by(event=event).first():
                                        db.session.add(event_instance)
                                    else:
                                        print "event already in database!"

                                    event_instance.books.append(book)

                            if root.find("lt:ltml", ns).find("lt:item", ns).find("lt:commonknowledge", ns).find("lt:fieldList", ns).find("lt:field[@name='characternames']", ns) is not None:
                                for child in root.findall("./lt:ltml/lt:item/lt:commonknowledge/lt:fieldList/lt:field[@name='characternames']/lt:versionList/lt:version/lt:factList/*",ns):
                                    character = child.text
                                    character_instance = Character(character=character,
                                                                    isbn=isbn)
                                    db.session.add(character_instance)

                            if root.find("lt:ltml", ns).find("lt:item", ns).find("lt:commonknowledge", ns).find("lt:fieldList", ns).find("lt:field[@name='quotations']", ns) is not None:
                                for child in root.findall("./lt:ltml/lt:item/lt:commonknowledge/lt:fieldList/lt:field[@name='quotations']/lt:versionList/lt:version/lt:factList/*",ns):
                                    quotation = child.text.lstrip("<![CDATA[").rstrip("]]>")
                                    print quotation
                                    quote_instance = Quote(quote=quotation,
                                                            isbn=isbn)
                                    db.session.add(quote_instance)

                            if root.find("lt:ltml", ns).find("lt:item", ns).find("lt:commonknowledge", ns).find("lt:fieldList", ns).find("lt:field[@name='awards']", ns) is not None:
                                for child in root.findall("./lt:ltml/lt:item/lt:commonknowledge/lt:fieldList/lt:field[@name='awards']/lt:versionList/lt:version/lt:factList/*",ns):
                                    award = child.text
                                    print award
                                    award_instance = Award(award=award,
                                                            isbn=isbn)
                                    db.session.add(award_instance)

                            if root.find("lt:ltml", ns).find("lt:item", ns).find("lt:commonknowledge", ns).find("lt:fieldList", ns).find("lt:field[@name='firstwords']", ns) is not None:
                                first_words = root.find("lt:ltml", ns).find("lt:item", ns).find("lt:commonknowledge", ns).find("lt:fieldList", ns).find("lt:field[@name='firstwords']", ns).find("lt:versionList", ns).find("lt:version", ns).find("lt:factList",ns).find("lt:fact", ns).text.lstrip("<![CDATA[").rstrip("]]>")
                                print "first words: ", first_words
                                book.first_words = first_words
        except:
            print "Error! Probably parsing..."
def get_longitude_latitude_of_location():
    """Query the database for locations with a latitude as None and 
    find use the geocoder location to get the longitude and latitude of the location.
    If the location does not exist or is fictional, then the lat/longs are set to
    float('Nan'). """

    #### the syntax needed to retrieve the info (https://geocoder.readthedocs.org/en/latest/)
    location_obj_list = Location.query.filter(Location.latitude.is_(None)).all()
  
    location_dict= {}

    for place in location_obj_list:

        if not place.city_county:
            location = place.state + ", " + place.country
            print location
        else:
            try:
                location = place.city_county + ", " + place.state
                print location
            except TypeError:
                location = place.city_county, ", ", place.state

        location_obj = geocoder.google(location)
        print location, location_obj

        latlong = location_obj.geometry.get("coordinates", (float('NaN'), float('NaN')))
        place.latitude  = latlong[1]
        place.longitude = latlong[0]
    db.session.commit()






if __name__ == "__main__":
    connect_to_db(app)
    db.create_all()
    script = argv
    seed_database_from_list_of_authors()

