from server import app
from model import Book, Author, Location, Category, Event, Award, connect_to_db, db
from flask_sqlalchemy import SQLAlchemy

import nltk
import string
import re
from nltk.corpus import stopwords

import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# from __future__ import print_function
import numpy as np
import pandas as pd
import nltk
import re
import os
import codecs
from sklearn import feature_extraction
from sklearn.externals import joblib
import mpld3
import matplotlib.pyplot as plt
import matplotlib as mpl
from sklearn.manifold import MDS
from sklearn.metrics.pairwise import cosine_similarity
#filter out books with no location and no description
#generate a dictionary of ALL token words and values => book_objs with those words in description
#do cosine similiarty only on books that only have tokens in common
	## TF threshold / TF-IDF threshold to weed out common, non-stopword words



def main_func():
	list_of_book_objects = Book.query.filter(Book.title.ilike('war%')).all()
	print "NUMBER OF BOOKS, ", len(list_of_book_objects)
	bookobj_tokens_dict = {}
	for book_obj in list_of_book_objects:

		if book_obj.description:
			# print "book title: ", book_obj.title
			book_description = book_obj.description
			stemmed_tokens = get_tokens(book_description)
			# print "STEMMED-tokens ", stemmed_tokens
			# book_descrip_stripped = get_tokens(book_obj)
			# print "tokens list: ", len(book_descrip_stripped), book_descrip_stripped
			# print "#" * 20
			# print "#" * 20
			# stemmed_tokens = stem_tokens(book_descrip_stripped)

			# print "stemmed tokens", stemmed_tokens
			# print "#" * 20
			bookobj_tokens_dict[book_obj] = stemmed_tokens

	cosine_sim = cosine_similarity(bookobj_tokens_dict)
	print "cosine sim, ", cosine_sim
	return cosine_sim
	

def get_tokens(book_description):
	"""Take book description, strip of punctuation, lowercase, and split/token into individual
	words. """

	#remove all punctuation except ' and - and lowercases words
	book_descrip_no_punc = re.split(r"[^\w]", book_description.lower()) 
	# print "BOOK DESCRIP NO PUNC", book_descrip_no_punc
	token_list_filtered = remove_stopwords(book_descrip_no_punc)
	stemmed_tokens = stem_tokens(token_list_filtered)
	# return book_descrip_no_punc
	return stemmed_tokens

def remove_stopwords(book_descrip_stripped):
	"""Remove the stopwords from the list of tokens. """

	token_list_filtered = [word for word in book_descrip_stripped if not word in stopwords.words('english')]
	
	return token_list_filtered

def stem_tokens(token_list_filtered):
	"""Stem the tokens. """
	# print "TOKENS LIST", book_descrip_stripped
	# print "TOKENS LIST TYPE", type(book_descrip_stripped), len(book_descrip_stripped)
	# tokens_list_filtered = remove_stopwords(book_descrip_stripped)
	# print "TOKENS LIST FILTERED", tokens_list_filtered
	# print "TOKENS LIST FILTERED", type(tokens_list_filtered), len(tokens_list_filtered)
	stemmer = nltk.stem.porter.PorterStemmer()
	stemmed_tokens = [stemmer.stem_word(word) for word in token_list_filtered]
	# print "STEMMED TOKENS,", stemmed_tokens
	stemmed_tokens = filter(None, stemmed_tokens)
	# print "STEMMED TOKENS 2", stemmed_tokens
	return stemmed_tokens

def cosine_similarity(bookobj_tokens_dict):
	# print type(bookobj_tokens_dict)
	books_dict = bookobj_tokens_dict.items()
	# print books_dict
	# print type(books_dict)
	titles = [book[0].title.encode('utf-8') for book in books_dict]
	# print "titles, ", titles
	description_tokens = [book[0].description for book in books_dict]
	print "description tokens", description_tokens

	# print "description, ", description_tokens
	# # max_df -- max frequency within document a fiven feaeture can have to be in matrix;
	# # if > 80% in a document, carries less meaning
	# # min_idf --if an integer, then the term has to be in at least 'X' integer documents to be 
	# # considerd. 0.2 means it needs to be in at least 20% of documents
	# # ngram)range -- means to look at unigrams, bigrams, and trigrams
	tfidf_vectorizer = TfidfVectorizer(max_df=0.8, max_features=200000,
                                 min_df=0.2, stop_words='english',
                                 use_idf=True, tokenizer=get_tokens, ngram_range=(1,3))
	# print "tfidf vectorizer, ", tfidf_vectorizer
	# print "stemmed tokens", get_tokens
	# # tdidf = TfidfVectorizer(tokenizer=stem_tokens, stop_words='english')
	# # tfs = tfidf.fit_transform(token_dict.values())
	tfidf_matrix = tfidf_vectorizer.fit_transform(description_tokens)
	print "tfidf_matrix", tfidf_matrix
	print "tfidf matrix shape ", tfidf_matrix.shape
	# # return ((tfidf_vectorizer * tfidf_vectorizer.T).A)[0,1]
	# # terms is a list of features used in the tf-idf matrix
	terms = tfidf_vectorizer.get_feature_names()
	print "terms, ", terms
	from sklearn.metrics.pairwise import cosine_similarity
	# print cosine_similarity(tfidf_matrix)
	dist = cosine_similarity(tfidf_matrix)
	print "distance, ", dist
	num_clusters = 5
	km = KMeans(n_clusters = num_clusters)
	# # print "kmeans, ", km
	km.fit(tfidf_matrix)
	clusters = km.labels_.tolist()
	print "clusters, ", clusters
	joblib.dump(km, 'doc_cluster.pkl')
	km = joblib.load('doc_cluster.pkl')
	print "km joblib dump, ", km
	clusters = km.labels_.tolist()
	print "clusters after pkl dump, ", clusters
	books = {'title':titles, 'synopsis':description_tokens,'cluster':clusters}
	print "books, ", books
	frame = pd.DataFrame(books,index=[clusters],columns=['title','cluster'])
	print "frame, ", frame
	frame['cluster'].value_counts()
	grouped = frame['title'].groupby(frame['cluster'])
	# print "grouped, ", grouped

	print "Top terms per cluster:"
	print 
	order_centroids = km.cluster_centers_.argsort()[:, ::-1]
	print "order centroids, ", order_centroids

	##vocab frame --- don't understand yet
	totalvocab_tokenized_list = [word for token_sublist in bookobj_tokens_dict.values() for word in token_sublist]
	print "total vocab tokenized list, ", totalvocab_tokenized_list
	vocab_frame = pd.DataFrame({'words': totalvocab_tokenized_list}, index=totalvocab_tokenized_list)
	print 'there are ' + str(vocab_frame.shape[0]) + ' items in vocab_frame'
	print "num cluster, ", num_clusters
	print "values, ", frame.ix
	for i in range(num_clusters):
		print "Cluster %d words:" % i

		for ind in order_centroids[i, :6]:
			print ' %s' % vocab_frame.ix[terms[ind].split(' ')].values.tolist()[0][0].encode('utf-8','ignore')
		print
		print
		print "Cluster %d titles:" % i
		# import pdb; pdb.set_trace()
		df = frame.ix[i]['title']
		if type(df) is str:
			print ' %s,' % df
		else:
			for title in df.values.tolist():
				print ' %s,' % title
		print 
		print

		MDS()

		#convert two components while plotting points in 2-D plane
		#'precomputed' because provide a distance matrix
		#will also specify random_state so the plot is reproducible
		mds = MDS(n_components=2, dissimilarity="precomputed", random_state=1)
		print "mds, ", mds
		pos = mds.fit_transform(dist) # shape (n_compoents, n_samples)
		print "pos, ", pos
		xs, ys = pos[:, 0], pos[:, 1]
		print "xs, ", xs
		print "ys, ", ys
		print 
		print



if __name__ == "__main__":
    connect_to_db(app)
    db.create_all()
    main_func()
    # cosine_similarity = cosine_similarity(bookobj_tokens_dict)