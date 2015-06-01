import requests

import os #allows access to environmental variables

from bs4 import BeautifulSoup, SoupStrainer #beautifulsoup library parses html/xml documents

from model import Book, Author, Location, Category, Quote, Event, Character, Award, connect_to_db, db

from sys import argv

#not quite sure how this works, but it has aleviated my unicode errors!
#source - random forum: http://mypy.pythonblogs.com/12_mypy/archive/1253_workaround_for_python_bug_ascii_codec_cant_encode_character_uxa0_in_position_111_ordinal_not_in_range128.html
import sys;
reload(sys);
sys.setdefaultencoding("utf8")


from server import app

import xml.etree.ElementTree as ET

from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import exc

from datetime import datetime

#from Google Books
import pprint
import sys
from apiclient.discovery import build

import geocoder
from random_words import RandomWords


# Note: you must run `source secrets.sh` before running this file
# to make sure these environmental variables are set.

#Maximum number of results to return. (integer, 0-40)
MAX_RESULTS = 20
#Index of the first result to return (starts at 0) (integer, 0+)
START_INDEX = 0
## last stopped after seeding at index 220 for 'california subject:"fiction"'
# stopped after seeding at index 200 for
#sunday -- started at 160-400 'new york times bestseller books'
#books - 200
#subject:fiction -- 240
#pulitzer prize winning books -120
RW = RandomWords()

#remember to run source secrets.sh in order to access this environmental variable
# API provided from OS environment dictionary
apikey = os.environ['LIBRARYTHING_DEVELOP_KEY']
google_api_key = os.environ['GOOGLE_API_KEY']

def book_database_seeding(google_api_key, apikey, query):
    """Main fuction that runs the helper functions below to
    search for books and seed the database with information. """
    response = google_book_search(query)
    isbn_list = create_book_author_instance(response)
    list_tuples_commknow_isbn = get_LT_book_info(apikey, isbn_list)
    create_location_instance(list_tuples_commknow_isbn)
    get_longitude_latitude_of_location()
    db.session.commit()
    print "Querying and seeding complete"


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

                #TODO -- I don't really want this because some isbns have letters at the end
                #but don't want the non-isbn numbers "UCSC:..." or "STANFORD:..."
                #regular expressions -- or make sure doesn't contain a colon...
            if isbn:
                title = book_dict.get('volumeInfo', {}).get('title')
                print "The title: ", title
                subtitle = book_dict.get('volumeInfo', {}).get('subtitle')
                # print "subtitle: ", subtitle
                bookauthors = book_dict.get('volumeInfo', {}).get('authors')
                print "Authors: ", bookauthors
                if book_dict.get('volumeInfo').get('categories'):
                    categories = book_dict.get('volumeInfo').get('categories')
                else:
                    categories = None
                # print "Categories: ", categories
                mainCategory = book_dict.get('volumeInfo').get('mainCategory')
                # print "Main Category", mainCategory
                description = book_dict.get('volumeInfo', {}).get('description')
                # print "Description: ", description
                thumbnail = book_dict.get('volumeInfo', {}).get('imageLinks', {}).get('thumbnail')
                # print "Thumbnail link: ", thumbnail

                publishedDate_unformated = book_dict.get('volumeInfo', {}).get('publishedDate')
                if publishedDate_unformated:
                    try:
                        if len(publishedDate_unformated)  > 8:
                            publishedDate = datetime.strptime(publishedDate_unformated, "%Y-%m-%d")
                        elif len(publishedDate_unformated) < 5:
                            publishedDate = datetime.strptime(publishedDate_unformated, "%Y")
                        else:
                            publishedDate = datetime.strptime(publishedDate_unformated, "%Y-%m")
                    except:
    
                        print "Publication date formating errors for: ", title
                    # print "Publication Date: ", publishedDate
                else:
                    publishedDate = None

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
                            publication_date = publishedDate,
                            preview_link = previewLink,
                            page_count = pageCount,
                            ratings_count = ratingsCount,
                            average_ratings = averageRatings)

                if not Book.query.get(book.isbn):
                    db.session.add(book)
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
                            #some categories are longer than 40 characeters and causing breaks in seeding loop
                            if len(item) > 40:
                                item = item[:40]
                            category_instance = Category(category = item)
                            if not Category.query.filter_by(category = item).all():
                                db.session.add(category_instance)
                            category_instance.books.append(book)
                    # db.session.commit()
                else:
                    print "This book ", book.title, "isbn: ", book.isbn, " already exist in the database!"
    print isbn_list
    print "book instance creation complete"

    return isbn_list



def get_LT_book_info(apikey, isbn_list):
    """This function takes a list of book instances, retrieves the isbn of a work (book), and returns the XML of the common knowledge from librarything.
    """
    list_tuples_commknow_isbn = []

    for work in isbn_list:
        work_info = {"method" : "librarything.ck.getwork", "isbn" : work, "apikey" : apikey}
        # creates a class 'requests.models.Response' - prints common work
        work_common_knowledge = requests.get('http://librarything.com/services/rest/1.1/', params=work_info)

        if work_common_knowledge:
            # turns common knowledge into a unicode
            work_common_knowledge_unicode = work_common_knowledge.text

            list_tuples_commknow_isbn.append((work_common_knowledge_unicode, work))
            # print list_tuples_commknow_isbn
            # import pdb; pdb.set_trace()
    return list_tuples_commknow_isbn


def create_location_instance(list_tuples_commknow_isbn):
    #TO DO -- still get parsing errors -- try search "new york times bestselling 2014"
    # file_to_parse = open(file_name).read()
    # tree = ET.parse(file_name)
    print "I'm now in here"
    for item in list_tuples_commknow_isbn:
        try:
            commonknowledge = item[0]
            isbn = item[1]
            book = Book.query.get(isbn)
            print "book:", book
            print isbn
            root = ET.fromstring(commonknowledge)
            # root = ET.fromstring(commonknowledge_enc)
            ns={'lt':'http://www.librarything.com/'}
            # import pdb; pdb.set_trace()
            # import pdb; pdb.set_trace()
            #in the ET library, findall() returns a list of objects; iterating over them and extracting the text
            for child in root.findall("./lt:ltml/lt:item/lt:commonknowledge/lt:fieldList/lt:field[@name='placesmentioned']/lt:versionList/lt:version/lt:factList/*",ns):
                place = child.text
                # print place
                place_list = place.split(', ')
                print place_list
                # import pdb; pdb.set_trace()
                #only pulling out places that have a city and state listed
                #TO DO -- how can I make this code more efficient?
                #if I put the db.session.add() outside of the if loop, then there will be
                #instances where location does not exist and I will get an error
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

            #WARNING/FYI: FutureWarning: The behavior of this method will change in
            #future versions.  Use specific 'len(elem)' or 'elem is not None' test instead.
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
                                    # if not Character.query.filter_by(character=character).all():
                                    db.session.add(character_instance)
                                    # else:
                                        # print "character name already in database!"
                                    # character_instance.books.append(book)

                            if root.find("lt:ltml", ns).find("lt:item", ns).find("lt:commonknowledge", ns).find("lt:fieldList", ns).find("lt:field[@name='quotations']", ns) is not None:
                                for child in root.findall("./lt:ltml/lt:item/lt:commonknowledge/lt:fieldList/lt:field[@name='quotations']/lt:versionList/lt:version/lt:factList/*",ns):
                                    quotation = child.text.lstrip("<![CDATA[").rstrip("]]>")
                                    print quotation
                                    quote_instance = Quote(quote=quotation,
                                                            isbn=isbn)
                                    db.session.add(quote_instance)
                                    # quote_instance.books.append(book)

                            if root.find("lt:ltml", ns).find("lt:item", ns).find("lt:commonknowledge", ns).find("lt:fieldList", ns).find("lt:field[@name='awards']", ns) is not None:
                                for child in root.findall("./lt:ltml/lt:item/lt:commonknowledge/lt:fieldList/lt:field[@name='awards']/lt:versionList/lt:version/lt:factList/*",ns):
                                    award = child.text
                                    print award
                                    award_instance = Award(award=award,
                                                            isbn=isbn)
                                    db.session.add(award_instance)
                                    # quote_instance.books.append(book)

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

    #### To NOTE:::: geocoder.osm (Open Street Maps) returns a different library 
    #### than the geocoder.google -- take note of how the lat/longs are returned and
    #### the syntax needed to retrieve the info (https://geocoder.readthedocs.org/en/latest/)
    location_obj_list = Location.query.filter(Location.latitude.is_(None)).all()
    # print location_obj_list
    # dict_city_state = {l.state: l.city_county for l in usa_cities_obj_list}
    location_dict= {}

    for place in location_obj_list:
        # try:
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

        # except:
            # place.latitude = float('NaN')
            # place.longitude = float('NaN')
            # print "This location, ", location, "could not be found."

        # else:
        latlong = location_obj.geometry.get("coordinates", (float('NaN'), float('NaN')))
        place.latitude  = latlong[1]
        place.longitude = latlong[0]
    db.session.commit()




    #### For geocoder.google::
    # for place in location_obj_list:
        
    #     if not place.city_county:
    #         location = place.state + ", " + place.country
    #         print location
    #     else:
    #         location = place.city_county + ", " + place.state
    #         print location
            
    #     try:
    #         location_obj = geocoder.google(location)

    #     except:
    #         place.latitude = float('NaN')
    #         place.longitude = float('NaN')
    #         print "This location, ", location, "could not be found."

    #     else:
    #         latlong = location_obj.latlng
    #         if latlong:
    #             place.latitude  = latlong.[0]
    #             place.longitude = latlong.[1]
    #             db.session.commit()

    #### For geocoder.osm:::
       # for place in location_obj_list:
       #  # try:
       #  if not place.city_county:
       #      location = place.state + ", " + place.country
       #      print location
       #  else:
       #      location = place.city_county + ", " + place.state
       #      print location
       #  location_obj = geocoder.osm(location)
       #  print location, location_obj

       #  # except:
       #      # place.latitude = float('NaN')
       #      # place.longitude = float('NaN')
       #      # print "This location, ", location, "could not be found."

       #  # else:
       #  latlong = location_obj.geometry.get("coordinates", (float('NaN'), float('NaN')))
       #  place.latitude  = latlong[1]
       #  place.longitude = latlong[0]


    # usa_cities_obj_list = Location.query.filter_by(country='USA').filter(Location.city_county.isnot(None)).all()
    # print usa_cities_obj_list
    # # dict_city_state = {l.state: l.city_county for l in usa_cities_obj_list}
    # dict_city_state = {}

    # for place in usa_cities_obj_list:
    #     location = place.city_county + ", " + place.state
    #     # print location
    #     location_obj = geocoder.google(location)
    #     latlong = location_obj.latlng
    #     # print location,latlong
    #     # print type(latlong)
    #     if latlong:
    #         place.latitude  = latlong[0]
    #         place.longitude = latlong[1]
    #         db.session.commit()



        # location = place.city_county + ", " + place.state
        # # print location
        # location_obj = geocoder.google(location)
        # latlong = location_obj.latlng
        # # print location,latlong
        # # print type(latlong)
        # if latlong:
        #     place.latitude  = latlong[0]
        #     place.longitude = latlong[1]
        #     db.session.commit()

    # for location_obj in usa_cities_obj_list:
    #     dict_city_state[location_obj.state] = location_obj.city_county
    # # print dict_city_state
    # for state in dict_city_state:
    #     location = dict_city_state[state] +", " + state
    #     # print location
    #     # print "location type", type(location)
    #     # print location
    #     location_obj = geocoder.google(location)
    #     latlong = location_obj.latlng
    #     print location,latlong
    #     print type(latlong)
    #     location_obj.longitude  = latlong[0]
    #     location_obj.latitude = latlong[1]
        # db.session.commit()
        # import pdb; pdb.set_trace()


def command_line_query_loop():
    max_results = MAX_RESULTS
    total_query = 0
    queries = []
    file = open("listofbooks.txt").read()
    authors_list = file.split("\n")
    while total_query < 200:
        for author in authors_list:
            query = ""
            name = author[:-9].split()
            for a_name in name:
                query = query + "inauthor:" + a_name + " "
            print query
            book_database_seeding(google_api_key, apikey, query)
            total_query = total_query + max_results
            print total_query
            print "#" * 40
            print "#" * 40
            print "#" * 40
            queries.append(query)
        print queries


## Query I used to seed database by searching for random words::
# while total_query < 300:
#         query = RW.random_word()
#         book_database_seeding(google_api_key, apikey, query)
#         total_query = total_query + max_results
#         queries.append(query)
#     print queries

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
    # get_longitude_latitude_of_location()

    script = argv
    command_line_query_loop()
    # book_database_seeding(google_api_key, apikey, query)
