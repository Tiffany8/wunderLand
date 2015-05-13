from flask_sqlalchemy import SQLAlchemy

# This is the connection to the SQLite database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()

##############################################################################
# Part 1: Compose ORM



authors_ref = db.Table('authors_ref',
    db.Column('author_id', db.Integer, db.ForeignKey('authors.author_id')),
    db.Column('isbn', db.Integer, db.ForeignKey('books.isbn'))
)

# class Books(db.Model):
#     isbn = db.Column(db.Integer, primary_key=True)
#     authors = db.relationship('Author', secondary=authors,
#         backref=db.backref('books', lazy='dynamic'))

# class Author(db.Model):
#     id = db.Column(db.Integer, primary_key=True)





class Book(db.Model):

    __tablename__ = "books"
    isbn = db.Column(db.Integer, primary_key=True)
    book_title = db.Column(db.String(70), nullable=False)
    book_copyright =  db.Column(db.String(12), nullable=True)
    summary = db.Column(db.String(300), nullable=True)
    book_avg_rating = db.Column(db.Integer, nullable=True)

    authors = db.relationship('Author', secondary=authors_ref,
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


# class BookAuthor(db.Model):
# 	__tablename__ = "bookauthors"
# 	bookauthor_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
# 	isbn = db.Column(db.Integer, db.ForeignKey('books.isbn'))
# 	author_id = db.Column(db.Integer, db.ForeignKey('authors.author_id'))

# 	author = db.relationship("Author", backref=db.backref("book_authors", order_by=Book.book_title))	
# 	book = db.relationship("Book", backref=db.backref("book_authors", order_by=Author.author_lastname))

# 	def __repr__(self):
# 		"""Provide helpful representation when printed."""
# 		return "<BookAuthor bookauthor_id=%d isbn=%d author_id=%d>" % (self.bookauthor_id, self.isbn, self.author_id)




# End Part 1
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