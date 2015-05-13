import requests

import os #allows access to environmental variables

from bs4 import BeautifulSoup, SoupStrainer #beautifulsoup library parses html/xml documents

from model import Book, Author, Location, connect_to_db, db

from sys import argv

from server import app

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


def parse_common_knowledge_for_book_info(isbn):
    file_to_parse = open(str(isbn)+".xml").read()
    tree = ET.parse(str(isbn)+".xml")
    root = tree.getroot()
    ns={'lt':'http://www.librarything.com/'}

    #table attributes
    for child in root:
        book_title = root.find("lt:ltml", ns).find("lt:item", ns).find("lt:title", ns).text
        book_copyright = root.find("lt:ltml", ns).find("lt:item", ns).find("lt:commonknowledge", ns).find("lt:fieldList", ns).find("lt:field[@name='originalpublicationdate']", ns).find("lt:versionList", ns).find("lt:version", ns).find("lt:factList",ns).find("lt:fact", ns).text
        book_avg_rating = root.find("lt:ltml", ns).find("lt:item", ns).find("lt:rating", ns).text

        #in the ET library, findall() returns a list of objects; iterating over them and extracting the text
        for placesmentioned in root.findall("./lt:ltml/lt:item/lt:commonknowledge/lt:fieldList/lt:field[@name='placesmentioned']/lt:versionList/lt:version/lt:factList/*",ns):
            place = placesmentioned.text
            place_list = place.split(', ')
            # import pdb; pdb.set_trace()
            #only pulling out places that have a city and state listed
            if len(place_list) == 3:
                location = Location(location_code=place,
                                    location_city = place_list[0],
                                    location_state = place_list[1],
                                    location_country = place_list[2])
            db.session.add(location)
            
            

        author = root.find("lt:ltml", ns).find("lt:item", ns).find("lt:author", ns).text.split()
        author_firstname, author_lastname = author[0], author[1]
        summary = root.find("lt:ltml", ns).find("lt:item", ns).find("lt:commonknowledge", ns).find("lt:fieldList", ns).find("lt:field[@name='description']", ns).find("lt:versionList", ns).find("lt:version", ns).find("lt:factList",ns).find("lt:fact", ns).text.rstrip("]>").lstrip("<![CDATA[")

        book = Book(isbn = isbn,
                book_title = book_title,
                book_copyright = book_copyright,
                book_avg_rating = book_avg_rating,
                summary = summary
                )
        db.session.add(book)

        author = Author(author_firstname = author_firstname,
                        author_lastname = author_lastname
                        )
        #magic stuff --- something about an isntance of a book referencing the authors table in model.py and appending location/author to list.....
        book.authors.append(author)
        book.locations.append(location)

        db.session.commit()



if __name__ == "__main__":
    connect_to_db(app)

    db.create_all()

    script, isbn = argv

    # get_work_common_knowledge_by_isbn(apikey, isbn)

    parse_common_knowledge_for_book_info(isbn)   