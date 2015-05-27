import pprint

from flask_sqlalchemy import SQLAlchemy
# from SQLAlchemy import Numberic
# This is the connection to the SQLite database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)
from datetime import datetime
db = SQLAlchemy()
import geocoder
from math import radians, sin, cos, sqrt, asin
import sys;
reload(sys);
sys.setdefaultencoding("utf8")

##############################################################################
# Part 1: Compose ORM


#these are association tables created for many-to-many tables (FlaskSQLAlchemy)
#books is the "lazy" table
authors_books = db.Table('authors_books',
    db.Column('author_id', db.Integer, db.ForeignKey('authors.author_id')),
    db.Column('isbn', db.String(30), db.ForeignKey('books.isbn')))
#TO DO -- change the location id to si
locations_books = db.Table('locations_books',
    db.Column('location_id', db.Integer, db.ForeignKey('locations.location_id')),
    db.Column('isbn', db.String(30), db.ForeignKey('books.isbn')))

books_cats = db.Table('books_cats',
    db.Column('isbn', db.String(30), db.ForeignKey('books.isbn')),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.category_id')))

books_events = db.Table('books_events',
    db.Column('isbn', db.String(30), db.ForeignKey('books.isbn')),
    db.Column('event_id', db.Integer, db.ForeignKey('events.event_id')))

# books_quotes = db.Table("books_quotes",
#     db.Column('isbn', db.String(30), db.ForeignKey('books.isbn')),
#     db.Column('quote_id', db.Integer, db.ForeignKey('quotes.quote_id')))

# char_books = db.Table("char_books",
#     db.Column('character_id', db.String(100), db.ForeignKey('characters.character_id')),
#     db.Column('isbn', db.String(30), db.ForeignKey('books.isbn')))

class Book(db.Model):

    __tablename__ = "books"
    isbn = db.Column(db.String(30), primary_key=True)
    title = db.Column(db.Text(), nullable=False)
    subtitle = db.Column(db.Text(), nullable=True)
    description = db.Column(db.Text(), nullable=True)
    thumbnail_url = db.Column(db.String(200), nullable=True)
    publication_date = db.Column(db.DateTime(20), nullable=True)
    preview_link = db.Column(db.String(200), nullable=True)
    page_count = db.Column(db.Integer, nullable=True)
    ratings_count = db.Column(db.Integer, nullable=True)
    average_ratings = db.Column(db.Float, nullable=True)
    main_category = db.Column(db.String(50), nullable=True)

    first_words = db.Column(db.Text(), nullable=True)

    authors = db.relationship('Author', secondary=authors_books,
        backref=db.backref('books', lazy='dynamic'))
    locations = db.relationship('Location', secondary=locations_books,
        backref=db.backref('books', lazy='dynamic'))
    # characters = db.relationship('Character', secondary=char_books,
    #     backref=db.backref('books', lazy='dynamic'))

    def get_other_books_within_radius(self, radius):
        """Returns a list of books that are within a determined radius of an instance of a book. """

        ####FYI:: Actually, this query along does not make sense, because a book can be associated with
        # more than one place...so maybe I should move this to the "category" and
        #"description/keyword" section

        books_within_radius_list = []


        #Sets the perimeter around a particular long/lat
        radius = float(radius)
        long_range = (self.longitude-(radius/69.0), self.longitude+(radius/69.0))
        lat_range = (self.latitude-(radius/49.0), self.latitude+(radius/49.0))

        #returns a list of location instances in the database that fall within the radius of the given long/lat
        range_list = Location.query\
            .filter(Location.longitude >= long_range[0], Location.longitude <= long_range[1] )\
            .filter(Location.latitude >= lat_range[0], Location.latitude <= lat_range[1])\
            .all()

        #for each location instance, return a list of books in db associated within the set range
        for location_object in range_list:
            books_obj_list = location_object.books
            for book_obj in books_obj_list:
                books_within_radius_list.append(book_obj.title)
        unique_books_list = list(set(books_within_radius_list))
            # books_within_radius_list.append(location_object.books.)
        return ", ".join(unique_books_list)
        # print range_list
        # for location_object in range_list:
        #     location_object
        # return

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Book isbn=%s title=%s>" % (self.isbn, self.title)

class Author(db.Model):

    __tablename__ = "authors"
    author_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    author_name = db.Column(db.Text(), nullable=False)


    def __repr__(self):
        """Provide helpful representation when printed."""
        return "<Author author_id=%d author=%s>" % (self.author_id, self.author_name)


class Location(db.Model):

    __tablename__ = "locations"
    location_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    city_county = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    @classmethod
    def get_books_associated_with_location(cls, radius,location):
        """Search by city and state and get back books associated with that location."""

        # location = city + ", " + state, + ", " + country

        ##Commenting out while at quota limit:
        # location_obj = geocoder.google(location)
        # latlong = location_obj.latlng
        # print latlong
        # latitude = latlong[0]
        # longitude = latlong[1]

        #hard coded LA cordinates for testing:
        latitude = 34.0500
        longitude = -118.2500

        #I'm setting the default radius to 100 miles
        radius = float(radius)

        #empty list for the books within a 50 mi radius
        books_within_radius_list = []

        long_range = (longitude-(radius/69.0), longitude+(radius/69.0))
        lat_range = (latitude-(radius/49.0), latitude+(radius/49.0))

        #returns a list of location instances in the database that fall within the radius of the given long/lat
        range_list = cls.query\
            .filter(cls.longitude >= long_range[0], cls.longitude <= long_range[1] )\
            .filter(cls.latitude >= lat_range[0], cls.latitude <= lat_range[1])\
            .all()
        loc_obj_dist_dict = {}
        #for each location instance, return a list of books in db associated within the set range
        for location_object in range_list:
            books_obj_list = location_object.books
            distance = Location.get_distance_between_two_locations(location_object.latitude, location_object.longitude, 
                latitude, longitude)
            #could also return a list of book objects -rather than a list of books
            #this will be more important to return for the server file, but for now
            #am just returning a list of book titles::

            for book_obj in books_obj_list:
                if book_obj not in loc_obj_dist_dict:
                    loc_obj_dist_dict[book_obj] = distance
                 
        #important to turn the list into a set in order to avoid getting book titles
        #multiple times when a book is associated with multiple places within a radius
        
        pprint.pprint(loc_obj_dist_dict)

        sorted_ = sorted(loc_obj_dist_dict, key=lambda b: (loc_obj_dist_dict[b], b.title))

        pprint.pprint(sorted_)

        return sorted_


    @classmethod   
    def get_distance_between_two_locations(cls, latitude1, longitude1, latitude2, longitude2):

        """Pass in a location2 to measure the distance between that location and 
        an instnace of a location.  This equation is the haversine formula.  Harversine is an equation 
        important in navigation, giving great-circle distances between two points on a sphere from their 
        longitudes and latitudes.  
        http://rosettacode.org/wiki/Haversine_formula
        """
        ## Since this is being used within the above class method (get_books_associated_with_location),
        ## I will have alrady calculated the lat and long for the location in question, so I won't need
        ## to use the geocoder library to find the lat/long (see below), but I'm saving the lines of code 
        ## as backup.
        # latlon2 = geocoder.google(location2).latlng #returns a list with the latitude and longitude, respectively
        # print latlon2
        # latitude2 = latlon2[0]
        # longitude2 = latlon2[1]
        R = float(3959) # This is Earth's radius in miles;radius in kilometers is 6372.8

        #convert decimal degress to radians
        deltaLat = radians(latitude2 - latitude1)
        deltaLon = radians(longitude2 - longitude1)
        #haversine formula
        latitude1 = radians(latitude1)
        latitude2 = radians(latitude2)

        a = sin(deltaLat/2)**2 + cos(latitude1)*cos(latitude2)*sin(deltaLon/2)**2
        c = float(2*asin(sqrt(a)))
        distance = R * c

        return distance #returns the distance in miles



    def __repr__(self):

        return "<Location location=%s, %s, %s>" % (self.city_county, self.state, self.country)


class Category(db.Model):

    __tablename__ = "categories"
    category_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    category = db.Column(db.String(40), nullable=True)

    books = db.relationship("Book", secondary=books_cats,
        backref=db.backref('categories', lazy='dynamic'))

    def get_books_associated_with_category_and_location(self, subject, city, state):

        category = Category.query.filter()

    def __repr__(self):

        return "<Category id: %d category: %s>" % (self.category_id, self.category)

class Event(db.Model):

    __tablename__ = "events"
    event_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    event = db.Column(db.Text(), nullable=False)
    books = db.relationship("Book", secondary=books_events,
        backref=db.backref('events', lazy='dynamic'))

    def __repr__(self):

        return "<Important event id= %d, event= %s>" % (self.event_id, self.event)

class Quote(db.Model):

    __tablename__ = "quotes"
    quote_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    quote = db.Column(db.Text(), nullable=True)
    isbn = db.Column(db.String(30), db.ForeignKey('books.isbn'))

    book = db.relationship("Book", backref=db.backref("quotes", order_by=quote_id))

    # books = db.relationship("Book", secondary=books_quotes,
    #     backref=db.backref('quotes', lazy='dynamic'))

    def __repr__(self):
        #how do I reference the book for this?
        return "<QUOTE ID: %d QUOTE: %s>" % (self.quote_id, self.quote)

class Character(db.Model):

    __tablename__ = "characters"
    character_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    character = db.Column(db.Text(), nullable=True)
    isbn = db.Column(db.String(30), db.ForeignKey('books.isbn'))

    book = db.relationship("Book", backref=db.backref("characters", order_by=character))

    def __repr__(self):

        return "<CHARACTER ID: %d CHARACTER: %s>" % (self.character_id, self.character)

class Award(db.Model):

    __tablename__ = "awards"
    award_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    award = db.Column(db.Text(), nullable=True)
    isbn = db.Column(db.String(30), db.ForeignKey('books.isbn'))

    book = db.relationship("Book", backref=db.backref("awards", order_by=award))

    def __repr__(self):

        return "<AWARD id: %d name: %s>" % (self.award_id, self.award)


# End
##############################################################################
# Helper functions


def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost:5432/projectwun'
    app.config['SQLALCHEMY_ECHO'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    # So that we can use Flask-SQLAlchemy, we'll make a Flask app
    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app)
    print "Connected to DB."
