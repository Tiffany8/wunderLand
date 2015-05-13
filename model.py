from flask_sqlalchemy import SQLAlchemy

# This is the connection to the SQLite database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()

##############################################################################
# Part 1: Compose ORM


#these are association tables created for many-to-many tables (FlaskSQLAlchemy)
#books is the "lazy" table
authors_ref = db.Table('authors_ref',
    db.Column('author_id', db.Integer, db.ForeignKey('authors.author_id')),
    db.Column('isbn', db.Integer, db.ForeignKey('books.isbn')))

locations_ref = db.Table('locations_ref', 
	db.Column('locations_code', db.String(100), db.ForeignKey('locations.location_code')),
	db.Column('isbn', db.Integer, db.ForeignKey('books.isbn')))



class Book(db.Model):

    __tablename__ = "books"
    isbn = db.Column(db.Integer, primary_key=True)
    book_title = db.Column(db.String(70), nullable=False)
    book_copyright =  db.Column(db.String(12), nullable=True)
    summary = db.Column(db.String(300), nullable=True)
    book_avg_rating = db.Column(db.Integer, nullable=True)

    authors = db.relationship('Author', secondary=authors_ref,
        backref=db.backref('books', lazy='dynamic'))

    locations = db.relationship('Location', secondary=locations_ref, 
    	backref=db.backref('books', lazy='dynamic'))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Book isbn=%d book_title=%s author_id=%d>" % (self.isbn, self.book_title, self.author_id)

class Author(db.Model):

	__tablename__ = "authors"
	author_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	author_firstname = db.Column(db.String(50), nullable=False)
	author_lastname = db.Column(db.String(50), nullable=False)
	
	def __repr__(self):
		"""Provide helpful representation when printed."""
		return "<Author author_id=%d author=%s %s isbn=%d>" % (self.author_id, self.author_firstname, self.author_lastname, self.isbn)


class Location(db.Model):

	__tablename__ = "locations"
	location_code = db.Column(db.String(100), primary_key=True)
	location_city = db.Column(db.String(100), nullable=True)
	location_state = db.Column(db.String(100), nullable=True)
	location_country = db.Column(db.String(100), nullable=True)

	def __repr__(self):

		return "<Location location=%s>" % (self.location_code)



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