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

Clicking "GET BOOKS" queries the database for books associated with the input location and within the radius set.  On the backend, the user's input location is run through the geocoder python library in order to determine the latitude and longitude of the location.  The radius that the user determines sets a perimeter around that location.  Locations in the database that are associated with a place that falls within the perimeter are queried.  These locations are associated with books in the database, and these books are returned to the user.  In the demonstration below, the user searches for 25 mi around "San Francisco", and the query returns 55 books associated with "San Francisco".  The user can scroll though the results.  Clicking on the book thumbnails reveals additional information about each book (title, author, description, keywords).

<p align='center'>
	<img align='center' src='http://g.recordit.co/9BZcmZe7wQ.gif' alt='search-results'>
</p>



####Keyword Exploration

A user can deepen their book exploration experience by clicking on keywords, which queries the databse and returns other books that have been associated with that keyword.  Keywords were generated from each book's description using the Natural Language Toolkit (NLTK).  Each description was broken into 'tokens' or individual words, which were then tagged by part-of-speech (pos).  Regex was used to create noun phrase patterns based on pos in order to chunk keyword phrases.  The following code snippet from <kbd>keywords_from_books_using_nltk.py</kbd> illustrates the noun phrase patterns that were used to identify keywords and keyword phrases.

```python
sentence_re = r'''(?x)
    ([A-Z])(\.[A-Z])+\.?  # set flag to allow verbose regexps
    | \w+(-\w+)*          # words with optional internal hyphens
    | \$?\d+(\.\d+)?%?    # currency and percentages
    | \.\.\.              # ellipsis
    | [][.,;"?():-_`]     # separate tokens
    '''

grammar = r"""
    NBAR:
        {<NN.*|JJ>*<NN.*>}             # Nouns and Adjectives, terminated with Nouns
        {<NNP|NNPS>+<IN>?<NNP|NNPS>+}  # A sequence of proper nouns connected with zero or more prepositions
        {<DT|PP\$>?<JJ>*<NN|NNS>}      # Determiners (e.g. 'the', 'a') or possessive, followed by one or more adjective 
        {<NN>+}                        # A sequence of one or more nouns
    NP:
        {<NBAR>}
        {<NBAR><IN><NBAR>}  
    """
```

####Book Clusters

If a user enjoys one of the discovered books, they can discover similar books that have been associated with the same queired location.  Using kmeans algorithm, clusters of books were created.  The kmeans algorithm takes the number of books associated with a location and groups them into 8 clusters, in which each book belongs to a cluster with the closest mean.  For wunderLand, books were clustered using a bag-of-words approach to create vector representations of each book based on the words in the book description.  Each word was weighted using term frequency-inverse document frequency (tf-idf).  tf-idf is a numerical representation of a terms importance to a document or book in a collection.  Term frequency (tf) is a ratio of the frequency of the word in a document to the total number of words in the document.  The inverse document frequency (idf) is the log of the ratio of the number of documents or books in the collectino to the numbe rof documents with the given term.  Multiplying tf and idf yields the tf-idf.  This statistical method was employed using the Scikit Learn python library to create a tfidf vectorizing object to pass through a list of documents.  For wunderLand, book descriptions were used.  Below is a snippet of code from <kbd> book_cosine_similarity.py</kbd> demonstrating the creation of the tf-idf vectorizer with a set of parameters, and passing through a list of the descriptions for a given collection.

```python
tfidf_vectorizer = TfidfVectorizer(max_df=0.5, max_features=200000,
                             min_df=0.2, stop_words='english',
                             use_idf=True, tokenizer=get_tokens, ngram_range=(1,3))

tfidf_matrix = tfidf_vectorizer.fit_transform(description_tokens)
``` 


####How to run wunderLand on your machine

Clone or fork this repo:

```python
https://github.com/Tiffany8/Project_WunderLand.git
```

Create and activate a virtual environment inside your project directory:

```
virtualenv env

source env/bin/activate
```

Install the requirements:

```
pip install -r requirements.txt
```

Get your own keys for for [LibraryThing API] (http://www.librarything.com/services/keys.php) and [Google Developer API] (https://developers.google.com/api-client-library/python/guide/aaa_apikeys), save them to a file <kbd>secrets.sh</kbd>, and add this file to your <kbd>.gitignore</kbd>.  Your file should look something like this:

```
export LIBRARYTHING_API_KEY='YOURSECRETLIBRARYTHINGKEYHERE'
export GOOGLE_API_KEY='YOURSECRETGOOGLEKEYHERE'
```

Source your secret keys:

```
source secrets.sh
```

Run the app:

```
python server.py
```

Navigate to `localhost:5000` to start discoverying new books!


####Next Steps

Check out the [issues log for this project] (https://github.com/Tiffany8/Project_WunderLand/issues) to see what's next!
