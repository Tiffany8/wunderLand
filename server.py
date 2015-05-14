from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request as flaskrequest, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from model import Book, Author, Location, connect_to_db, db
import os

#from Google Books
import pprint
import sys
from apiclient.discovery import build

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined

google_api_key = os.environ['GOOGLE_API_KEY']

@app.route("/")
def index():
    """Display the homepage."""

    return render_template("homepage.html")

@app.route("/", methods=['POST'])
def search_for_books():
    """Search for books through the homepage."""
    
    user_book_query = flaskrequest.form.get('search-input')
    print user_book_query
    
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
                                    orderBy='newest', 
                                    printType='books', 
                                    q=user_book_query, 
                                    startIndex=0,
                                    maxResults=40,
                                    fields="items(volumeInfo(description,pageCount,categories,publishedDate,imageLinks/thumbnail,industryIdentifiers,authors,mainCategory)),totalItems")
    # import pdb; pdb.set_trace()
    # # The execute() function on the HttpRequest object actually calls the API.
    # # It returns a Python object built from the JSON response. You can print this
    # # object or refer to the Books API documentation to determine its structure.
    
    response = request.execute()
  
    # pprint.pprint(response)
   

    # # Accessing the response like a dict object with an 'items' key returns a list
    # # of item objects (books). The item object is a dict object with a 'volumeInfo'
    # # key. The volumeInfo object is a dict with keys 'title' and 'authors'.

    
    query_result_length = len(response['items'])
    # search_results_list = []
    # for book in response.get('items', []):
    #     search_results_list.append((book['volumeInfo']['title'], 
    #                                 book['volumeInfo']['authors']))
    # print response.get('items', [])
    # print 'Found %d books:' % len(response['items'])
    maxResults=40
   
    page_number = 1

    #add this stuff to database
    # response['itemsPerPage'] = 20
    # for book in response.get('items', []):
    #     title = book.get('volumeInfo', {}).get('title')
    #     # print "The title: ", title
    #     authors = book.get('volumeInfo', {}).get('authors')
    #     # print "Authors: ", authors
    #     categories = book.get('volumeInfo', {}).get('categories') 
    #     # print "Categories: ", categories
    #     description = book.get('volumeInfo', {}).get('description')
    #     # print "Description: ", description
    #     thumbnail = book.get('volumeInfo', {}).get('imageLinks', {}).get('thumbnail')
    #     # print "Thumbnail link: ", thumbnail
    #     publishedDate = book.get('volumeInfo', {}).get('publishedDate')
    #     # print "Publication Date: ", publishedDate
    #     previewLink = book.get('volumeInfo', {}).get("previewLink") 
        # print "PreviewLink: ", previewLink
        # isbn = book.get('volumeInfo').get('industryIdentifiers')[1].get('identifier')    
    print "search complete"
    # return render_template("searchresults.html")
    return render_template("searchresults.html", query_result_length=query_result_length,
                                            response=response, maxResults=40, page_number=1)

@app.route('/moreresults/<int:page_number>', methods=['GET'])
def search_results_pagination(page_number):
    answer = flaskrequest.form.get('answer')
    page_number = int(page_number) + 1
    if answer:

        request = service.volumes().list(source='public', 
                                    orderBy='newest', 
                                    printType='books', 
                                    q=user_book_query, 
                                    startIndex=(int(itemsPerPage) * int(page_number)) + 1,
                                    maxResults=40,
      
                                    fields="items(volumeInfo(description,pageCount,categories,publishedDate,imageLinks/thumbnail,industryIdentifiers,authors,mainCategory)),totalItems")
        response = request.execute()

    
    
    return redirect("/moreresults/<int:page_number>")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
