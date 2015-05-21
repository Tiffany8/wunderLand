from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request as flaskrequest,\
        flash, session
from flask_debugtoolbar import DebugToolbarExtension
from model import Book, Author, Location, Category, Award, Event, Character,\
        connect_to_db, db
import os
from pw_utilities import get_books_associated_with_location

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



@app.route("/")
def index():
    """Display the homepage."""

    return render_template("index.html")

@app.route("/", methods=['POST'])
def search_for_books():
    """Search for books through the homepage by location."""

    user_location_query = flaskrequest.form.get('search-input')
    radius = flaskrequest.form.get('radius')
    radius = int(radius)
    print user_location_query

    # #assess user input
    # try:
    #     user_location_query_list = ", ".join(user_location_query)
    #     if len(user_location_query_list) == 2:
    #         city, state = user_location_query_list
    #     if len(user_location_query_list) == 3:
    #         city, state, country = user_location_query_list
    # except:
    #     city = user_location_query_list
    # else:
    #     print "Please enter a location (city, state)"

    #query for books associated with place within 100mi
    #returns a list of book objects
    book_obj_list = get_books_associated_with_location(radius, user_location_query)

    print "search complete"

    #determine query results list length
    #will use this for pagination
    query_result_length = len(book_obj_list)
    # search_results_list = []
    # for book in response.get('items', []):
    #     search_results_list.append((book['volumeInfo']['title'],
    #                                 book['volumeInfo']['authors']))
    # print response.get('items', [])
    # print 'Found %d books:' % len(response['items'])
    # maxResults=40
    # page_number = 1


    # return render_template("searchresults.html")
    return render_template("searchresults.html", query_result_length=query_result_length, book_obj_list=book_obj_list,
            user_location_query=user_location_query)

# @app.route('/moreresults/<int:page_number>', methods=['GET'])
# def search_results_pagination(page_number):
#     answer = flaskrequest.form.get('answer')
#     page_number = int(page_number) + 1
#     if answer:
#
#         request = service.volumes().list(source='public',
#                                     orderBy='newest',
#                                     printType='books',
#                                     q=user_location_query,
#                                     startIndex=(int(itemsPerPage) * int(page_number)) + 1,
#                                     maxResults=40,
#
#                                     fields="items(volumeInfo(description,pageCount,categories,publishedDate,imageLinks/thumbnail,industryIdentifiers,authors,mainCategory)),totalItems")
#         response = request.execute()
#
#
#
#     return redirect("/moreresults/<int:page_number>")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
