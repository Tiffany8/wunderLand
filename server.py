from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request as flaskrequest, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from model import Book, Author, Location, Category, Award, Event, Keyword, Character,\
        connect_to_db, db
import os
import json
from book_cosine_similarity import *
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

@app.route("/search", methods=["GET"])
def search_for_books():
    """Search for books through the homepage by location."""

    user_location_query = flaskrequest.args.get('search-input')
    print "user query, ", user_location_query
    radius = flaskrequest.args.get('radius')
    print "radius1, ", radius
    radius = int(radius)
    print "radius, ", radius
    print user_location_query

    #query for books associated with place within 100mi
    #returns a list of book objects
    jsonify_search_result_list = []

    ##hard code with LA cordinates due to quota limit:##
    book_obj_list = Location.get_books_associated_with_location(100, user_location_query)
    print book_obj_list
    #for loop to pull out the attributes

    # from the book_cosine_similarity file
    kmeans_cluster_html = main_func(book_obj_list)

    for book_object in book_obj_list:
        book_dict = {}
        author_list = [author.author_name for author in book_object.authors if book_object.authors]
        book_dict["title"] = book_object.title
        print book_dict["title"]
        book_dict["subtitle"] = book_object.subtitle
        book_dict["authors"] = ", ".join(author_list)
        book_dict["description"] = book_object.description
        book_dict["thumbnailUrl"] = book_object.thumbnail_url
        book_dict["previewLink"] = book_object.preview_link
        book_dict["keywords"] = [word.keyword for word in book_object.keywords]
        print book_dict["keywords"]
        jsonify_search_result_list.append(book_dict)
        # print book_dict
    # print jsonify_search_result_list
    print "search complete"
    # user_location_query, jsonify_search_result_list = jsonList_query


    return jsonify(name = jsonify_search_result_list, kmeans = kmeans_cluster_html)


@app.route("/search/kmeans")
def get_kmeans():
    kmeans_cluster_html = flaskrequest.args.get('kmeans_cluster_html')
    return kmeans_cluster_html

    
@app.route("/keyword/<keyword>")
def books_associated_with_keyword_page():
    pass

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
