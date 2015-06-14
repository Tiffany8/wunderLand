#![alt text](https://github.com/Tiffany8/Project_WunderLand/blob/master/static/img/wunderland_logo.png "Logo")underLand
wunderLand is a book discovery application that uses location as a means through which one can discover new books.
wunderLand employs natural language processing in order to enhance book discovery through the generation of keywords and keyword phrases in order to describe books.  NLP and machine learning are used in order to generate clusters of 'like' books based on book descriptions in order to aid users in an additional layer of book discovery.

####Technology Stack
Javascript, jQuery, HTML, CSS, AJAX, BootStrap, Python, Flask, SQLAlchemy, PostgresSQL, NLTK, MatPlotLibD3, SciKit Learn

####APIs
Google Books

LibraryThing 

Google Geolocation 

#### Book Discovery

From the home page, enter in a location (e.g. 'San Francisco, CA') and click "GET BOOKS".  

<p align='center'>
	<img align='center' src='https://github.com/Tiffany8/Project_WunderLand/blob/master/static/img/home-page.png' alt='home-page'>
</p>

Clicking "GET BOOKS" queries the database for books associated with the input location and within the radius set.  On the backend, the user's input location is run through the geocoder python library in order to determine the latitude and longitude of the location.  The radius that the user determines sets a perimeter around that location.  Locations in the database that are associated with a place that falls within the perimeter are queried.  These locations are associated with books in the database, and these books are returned to the user.

<p align='center'>
	<img align='center' src='/static/images/search-results.gif' alt='search-results'>
</p>

The user can click on a thumbnail in order to learn more about the book.

####Keyword Exploration

A user can deepen their book exploration experience by clicking on keywords, which queries the databse and returns other books that have been associated with that keyword.  Keywords were generated from each book's description using the Natural Language Toolkit (NLTK).  Each description was broken into 'tokens' or individual words, which were then tagged by part-of-speech (pos).  Regex was used to create noun phrase patterns based on pos in order to chunk keyword phrases.  The following code snippet from <kbd>keywords_from_books_using_nltk.py</kbd> illustrates the noun phrase patterns that were used to identify keywords and keyword phrases.

####Book Clusters

####How to run wunderLand

####Next Steps
