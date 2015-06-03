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
import datetime

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
from pylab import *
#filter out books with no location and no description
#generate a dictionary of ALL token words and values => book_objs with those words in description
#do cosine similiarty only on books that only have tokens in common
	## TF threshold / TF-IDF threshold to weed out common, non-stopword words



def main_func():
	current_time = datetime.datetime.utcnow()
	onehund_weeks_ago = current_time - datetime.timedelta(weeks=100)
	list_of_book_objects = Book.query.filter(Book.publication_date > onehund_weeks_ago).all()
	list_of_book_objects = [book_obj for book_obj in list_of_book_objects if book_obj.locations]
	# list_of_book_objects = Book.query.filter(Book.title.ilike('war%')).all()
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
	# print "cosine sim, ", cosine_sim
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
	lemmatizer = nltk.WordNetLemmatizer()
	# stemmed_tokens = [stemmer.stem_word(word) for word in token_list_filtered]
	stemmed_tokens = [lemmatizer.lemmatize(word) for word in token_list_filtered]
	# print "STEMMED TOKENS,", stemmed_tokens
	stemmed_tokens = filter(None, stemmed_tokens)
	# print "STEMMED TOKENS 2", stemmed_tokens
	return stemmed_tokens

def cosine_similarity(bookobj_tokens_dict):
	
	#####################################
	### TFIDF and Document Similarity ###
	#####################################
	books_dict = bookobj_tokens_dict.items()
	
	titles = [book[0].title.encode('utf-8') for book in books_dict]
	
	description_tokens = [book[0].description for book in books_dict]

	# # max_df -- max frequency within document a fiven feaeture can have to be in matrix;
	# # if > 80% in a document, carries less meaning
	# # min_idf --if an integer, then the term has to be in at least 'X' integer documents to be 
	# # considerd. 0.2 means it needs to be in at least 20% of documents
	# # ngram)range -- means to look at unigrams, bigrams, and trigrams
	tfidf_vectorizer = TfidfVectorizer(max_df=0.8, max_features=200000,
                                 min_df=0.2, stop_words='english',
                                 use_idf=True, tokenizer=get_tokens, ngram_range=(1,3))
	
	
	tfidf_matrix = tfidf_vectorizer.fit_transform(description_tokens)

	# # terms is a list of features used in the tf-idf matrix
	terms = tfidf_vectorizer.get_feature_names()
	print "terms, ", terms

	######################
	### KMeans Cluster ###
	######################
	from sklearn.metrics.pairwise import cosine_similarity
	# # dist is defined as 1 - the cosine similarity of each document. Cosine similarity is measured against 
	# #the tf-idf matrix and can be used to generate a measure of similarity between each document and the 
	# #other documents in the corpus (each synopsis among the synopses). Subtracting it from 1 provides 
	# #cosine distance which I will use for plotting on a euclidean (2-dimensional) plane.
	dist = cosine_similarity(tfidf_matrix)
	
	num_clusters = 6 # if this number is changed, update the cluster_color dictionary
	km = KMeans(n_clusters = num_clusters)
	km.fit(tfidf_matrix)
	clusters = km.labels_.tolist()
	print "clusters, ", clusters
	joblib.dump(km, 'doc_cluster.pkl')
	km = joblib.load('doc_cluster.pkl')
	clusters = km.labels_.tolist()
	books = {'title':titles, 'synopsis':description_tokens,'cluster':clusters}
	print "books, ", books
	frame = pd.DataFrame(books,index=[clusters],columns=['title','cluster'])
	frame['cluster'].value_counts()
	grouped = frame['title'].groupby(frame['cluster'])
	

	#############################
	### Top Terms Per Cluster ###
	#############################
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
	# print [i for i in range(num_clusters)]
	# print [vocab_frame.ix[terms[index].split(' ')].values.tolist()[0][0].encode('utf-8','ignore') for index in order_centroids[i, :3] for i in range(num_clusters)]
	print order_centroids

	graph_keys = [i for i in range(num_clusters)]
	graph_values = []
	for i in range(num_clusters):
		print "Cluster %d words:" % i
		the_terms = []
		for ind in order_centroids[i, :5]: # top 5 words that are nearest to the cluster centroid
			
			graph_terms = vocab_frame.ix[terms[ind].split(' ')].values.tolist()[0][0].encode('utf-8','ignore')
			the_terms.append(graph_terms)
			print "graph terms ", graph_terms
		print "the terms, ", the_terms
		
		graph_values.append(the_terms)
		
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
	print "graph values ", graph_values

	#################################
	### Multi-Dimensional Scaling ###
	#################################

	# # convert the dist matrix into a 2-dimensional array using MDS
	MDS()

	# #convert two components while plotting points in 2-D plane
	# #'precomputed' because provide a distance matrix
	# #will also specify random_state so the plot is reproducible
	mds = MDS(n_components=2, dissimilarity="precomputed", random_state=1)
	print "mds, ", mds
	pos = mds.fit_transform(dist) # shape (n_compoents, n_samples)
	print "pos, ", pos
	xs, ys = pos[:, 0], pos[:, 1]

	#################################
	### Visualizing Book Clusters ###
	#################################

	# #set up colors per clusters using a dict
	cluster_colors = {0: '#1b9e77', 1: '#d95f02', 2: '#7570b3', 3: '#e7298a', 4: '#66a61e', 5:'#F7EC45'}

	# #set up cluster names using a dict
	graph_values = [", ".join(term_list) for term_list in graph_values]
	cluster_names = dict(zip(graph_keys, graph_values))
	print "cluster names dictionary, ", cluster_names

	df = pd.DataFrame(dict(x=xs, y=ys, label=clusters, title=titles))
	
	# #group by clusters
	groups = df.groupby('label')

	# #set up plot
	fig, ax = plt.subplots(figsize=(17,9)) #set size
	ax.margins(0.05) # optional, just adds 5% padding to auto scaling

	# #iterate through groups to layer the plot
	# #note the use of cluster_name and cluster_color dicts with the 'name' lookup to return 
	# #appropriate color/label
	for name, group in groups:
		ax.plot(group.x, group.y, marker='o', linestyle='', ms=12,
			label=cluster_names[name], color=cluster_colors[name],
			mec='none')
		ax.set_aspect('auto')
		ax.tick_params(axis='x',
			which='both',
			bottom='off',
			top='off',
			labelleft='off')

	ax.legend(numpoints=1)

	for i in range(len(df)):
		ax.text(df.ix[i]['x'], df.ix[i]['y'], df.ix[i]['title'],size=8)

	plt.show()

if __name__ == "__main__":
    connect_to_db(app)
    db.create_all()
    main_func()
    # cosine_similarity = cosine_similarity(bookobj_tokens_dict)