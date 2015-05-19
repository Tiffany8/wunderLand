
from flask_sqlalchemy import SQLAlchemy
# This is the connection to the SQLite database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)
from datetime import datetime
db = SQLAlchemy()

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

books_quotes = db.Table("books_quotes", 
    db.Column('isbn', db.String(30), db.ForeignKey('books.isbn')),
    db.Column('quote_id', db.Integer, db.ForeignKey('quotes.quote_id')))

char_books = db.Table("char_books", 
    db.Column('character_id', db.String(100), db.ForeignKey('characters.character_id')),
    db.Column('isbn', db.String(30), db.ForeignKey('books.isbn')))

class Book(db.Model):

    __tablename__ = "books"
    isbn = db.Column(db.String(30), primary_key=True)
    title = db.Column(db.String(70), nullable=False)
    subtitle = db.Column(db.String(70), nullable=True)
    description = db.Column(db.String(500), nullable=True)
    thumbnail_url = db.Column(db.String(150), nullable=True)
    publication_date = db.Column(db.DateTime(20), nullable=True)
    preview_link = db.Column(db.String(150), nullable=True)
    page_count = db.Column(db.Integer, nullable=True)
    ratings_count = db.Column(db.Integer, nullable=True)
    average_ratings = db.Column(db.Float, nullable=True)
    main_category = db.Column(db.String(50), nullable=True)

    first_words = db.Column(db.String(500), nullable=True)

    authors = db.relationship('Author', secondary=authors_books,
        backref=db.backref('books', lazy='dynamic'))
    locations = db.relationship('Location', secondary=locations_books, 
    	backref=db.backref('books', lazy='dynamic'))
    characters = db.relationship('Character', secondary=char_books,
        backref=db.backref('books', lazy='dynamic'))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Book isbn=%s title=%s>" % (self.isbn, self.title)

class Author(db.Model):

	__tablename__ = "authors"
	author_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	author_name = db.Column(db.String(100), nullable=False)
	
	
	def __repr__(self):
		"""Provide helpful representation when printed."""
		return "<Author author_id=%d author=%s>" % (self.author_id, self.author_name)


class Location(db.Model):

	__tablename__ = "locations"
	location_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	city_county = db.Column(db.String(100), nullable=True)
	state = db.Column(db.String(100), nullable=True)
	country = db.Column(db.String(100), nullable=True)

	def __repr__(self):

		return "<Location location=%s, %s, %s>" % (self.city_county, self.state, self.country)


class Category(db.Model):

    __tablename__ = "categories"
    category_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    category = db.Column(db.String(40), nullable=True, unique=True)

    books = db.relationship("Book", secondary=books_cats,
        backref=db.backref('categories', lazy='dynamic'))

    def __repr__(self):

        return "<Category id: %d category: %s>" % (self.category_id, self.category)

class Event(db.Model):

    __tablename__ = "events"
    event_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    event = db.Column(db.String(100), nullable=False, unique=True)

    books = db.relationship("Book", secondary=books_events,
        backref=db.backref('events', lazy='dynamic'))

    def __repr__(self):

        return "<Important event id= %d, event= %s>" % (self.event_id, self.event)

class Quote(db.Model):

    __tablename__ = "quotes"
    quote_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    quote = db.Column(db.String(500), nullable=True)

    books = db.relationship("Book", secondary=books_quotes, 
        backref=db.backref('quotes', lazy='dynamic'))

    def __repr__(self):
        #how do I reference the book for this?
        return "<QUOTE ID: %d QUOTE: %s>" % (self.quote_id, self.quote)

class Character(db.Model):

    __tablename__ = "characters"
    character_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    character = db.Column(db.String(100), nullable=True)

    def __repr__(self):

        return "<CHARACTER ID: %d CHARACTER: %s>" % (self.character_id, self.character)

# End 
##############################################################################
# Helper functions


def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projectwun.db'
    app.config['SQLALCHEMY_ECHO'] = True
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