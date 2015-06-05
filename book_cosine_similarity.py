
from model import Book, Author, Location, Category, Event, Award, Keyword, connect_to_db, db
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



def main_func(list_of_book_objects):
	# current_time = datetime.datetime.utcnow()
	# onehund_weeks_ago = current_time - datetime.timedelta(weeks=200)
	# list_of_book_objects = Book.query.filter(Book.publication_date > onehund_weeks_ago).all()
	# list_of_book_objects = Book.query.filter(Book.title.ilike('war%')).all()
	# list_of_book_objects = Location.get_books_associated_with_location(100, "Los Angeles")
	list_of_book_objects = [book_obj for book_obj in list_of_book_objects if book_obj.description]
	
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

	kmeans_variables = tfidf_similarity(bookobj_tokens_dict)
	# km, dist, num_clusters = kmeans_cluster(*kmeans_variables)
	kmeans_cluster_graph_html = kmeans_cluster(*kmeans_variables)

	# graph_values, graph_keys = get_top_terms_per_cluster(km, bookobj_tokens_dict, num_clusters)
	# kmeans_cluster_graph_html = multi_diminsional_scaling_for_2D_array(dist, graph_values, graph_keys)
	return kmeans_cluster_graph_html

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
	lemmatizer = nltk.WordNetLemmatizer()
	my_stopwords = ['author', 'book', 'chapter', 'edition', 'read', 'novel']
	token_list_filtered = [word for word in book_descrip_stripped if not word in stopwords.words('english')]
	token_list_filtered = [word for word in token_list_filtered if not lemmatizer.lemmatize(word) in my_stopwords]

	
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

def tfidf_similarity(bookobj_tokens_dict):

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
	tfidf_vectorizer = TfidfVectorizer(max_df=0.5, max_features=200000,
                                 min_df=0.2, stop_words='english',
                                 use_idf=True, tokenizer=get_tokens, ngram_range=(1,3))
	
	
	tfidf_matrix = tfidf_vectorizer.fit_transform(description_tokens)

	# # terms is a list of features used in the tf-idf matrix
	terms = tfidf_vectorizer.get_feature_names()
	print "terms, ", terms
	return terms, description_tokens, tfidf_matrix, titles, bookobj_tokens_dict

def kmeans_cluster(terms, description_tokens, tfidf_matrix, titles, bookobj_tokens_dict):
	######################
	### KMeans Cluster ###
	######################
	from sklearn.metrics.pairwise import cosine_similarity
	# # dist is defined as 1 - the cosine similarity of each document. Cosine similarity is measured against 
	# #the tf-idf matrix and can be used to generate a measure of similarity between each document and the 
	# #other documents in the corpus (each synopsis among the synopses). Subtracting it from 1 provides 
	# #cosine distance which I will use for plotting on a euclidean (2-dimensional) plane.
	dist = 1 - cosine_similarity(tfidf_matrix)
	
	num_clusters = 8 # if this number is changed, update the cluster_color dictionary
	# km = KMeans(init='k-means++', t
	# 			max_iter=300, 
	# 			n_init=20,
 #                verbose=0, 
 #                n_clusters = num_clusters)
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

	# return km, dist, num_clusters

	
# def get_top_terms_per_cluster(km, bookobj_tokens_dict, num_clusters):
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

		for ind in order_centroids[i, :3]: # top 5 words that are nearest to the cluster centroid
			
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
	# return graph_values, graph_keys

	# def multi_diminsional_scaling_for_2D_array(dist, graph_values, graph_keys):
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
	cluster_colors = {0: '#1b9e77', 1: '#d95f02', 2: '#7570b3', 3: '#e7298a', 4: '#66a61e', 
					5:'#F7EC45', 6:'#2ee3b6', 7:'#cd82c0'}
	# cluster_colors = {0: '#1b9e77', 1: '#d95f02', 2: '#7570b3', 3: '#e7298a', 4: '#66a61e', , 8:'#a6efa4'}

	# #set up cluster names using a dict
	graph_values = [", ".join(term_list) for term_list in graph_values]
	cluster_names = dict(zip(graph_keys, graph_values))
	print "cluster names dictionary, ", cluster_names


	#create data frame that has the result of the MDS plus the cluster numbers and titles
	df = pd.DataFrame(dict(x=xs, y=ys, label=clusters, title=titles)) 

	#group by cluster
	groups = df.groupby('label')

	#define custom css to format the font and to remove the axis labeling
	css = """
	text.mpld3-text, div.mpld3-tooltip {
	  font-family:Arial, Helvetica, sans-serif;
	}

	g.mpld3-xaxis, g.mpld3-yaxis {
	display: none; }

	svg.mpld3-figure {
	margin-left: -200px;}
	"""

	# Plot 
	fig, ax = plt.subplots(figsize=(14,6)) #set plot size
	ax.margins(0.03) # Optional, just adds 5% padding to the autoscaling

	#iterate through groups to layer the plot
	#note that I use the cluster_name and cluster_color dicts with the 'name' lookup to return the appropriate color/label
	for name, group in groups:
	    points = ax.plot(group.x, group.y, marker='o', linestyle='', ms=18, 
	                     label=cluster_names[name], mec='none', 
	                     color=cluster_colors[name])
	    ax.set_aspect('auto')
	    labels = [i for i in group.title]
	    
	    #set tooltip using points, labels and the already defined 'css'
	    tooltip = mpld3.plugins.PointHTMLTooltip(points[0], labels,
	                                       voffset=10, hoffset=10, css=css)
	    #connect tooltip to fig
	    mpld3.plugins.connect(fig, tooltip, TopToolbar())    
	    
	    #set tick marks as blank
	    ax.axes.get_xaxis().set_ticks([])
	    ax.axes.get_yaxis().set_ticks([])
	    
	    #set axis as blank
	    ax.axes.get_xaxis().set_visible(False)
	    ax.axes.get_yaxis().set_visible(False)

	    
	ax.legend(numpoints=1) #show legend with only one dot

	mpld3.display() #show the plot

	#uncomment the below to export to html
	kmeans_cluster_graph_html = mpld3.fig_to_html(fig)
	
	return kmeans_cluster_graph_html


	#######################################################
	### Code for visualizing using matplotlib (minus d3)###
	#######################################################
	# df = pd.DataFrame(dict(x=xs, y=ys, label=clusters, title=titles))
	
	# # #group by clusters
	# groups = df.groupby('label')

	# # #set up plot
	# fig, ax = plt.subplots(figsize=(17,9)) #set size
	# ax.margins(0.05) # optional, just adds 5% padding to auto scaling

	# # #iterate through groups to layer the plot
	# # #note the use of cluster_name and cluster_color dicts with the 'name' lookup to return 
	# # #appropriate color/label
	# for name, group in groups:
	# 	ax.plot(group.x, group.y, marker='o', linestyle='', ms=12,
	# 		label=cluster_names[name], color=cluster_colors[name],
	# 		mec='none')
	# 	ax.set_aspect('auto')
	# 	ax.tick_params(axis='x',
	# 		which='both',
	# 		bottom='off',
	# 		top='off',
	# 		labelleft='off')

	# ax.legend(numpoints=1)

	# for i in range(len(df)):
	# 	ax.text(df.ix[i]['x'], df.ix[i]['y'], df.ix[i]['title'],size=8)

	# return plt.show()






#define custom toolbar location
class TopToolbar(mpld3.plugins.PluginBase):
    """Plugin for moving toolbar to top of figure"""

    JAVASCRIPT = """
    mpld3.register_plugin("toptoolbar", TopToolbar);
    TopToolbar.prototype = Object.create(mpld3.Plugin.prototype);
    TopToolbar.prototype.constructor = TopToolbar;
    function TopToolbar(fig, props){
        mpld3.Plugin.call(this, fig, props);
    };

    TopToolbar.prototype.draw = function(){
      // the toolbar svg doesn't exist
      // yet, so first draw it
      this.fig.toolbar.draw();

      // then change the y position to be
      // at the top of the figure
      this.fig.toolbar.toolbar.attr("x", 150);
      this.fig.toolbar.toolbar.attr("y", 400);

      // then remove the draw function,
      // so that it is not called again
      this.fig.toolbar.draw = function() {}
    }
    """
    def __init__(self):
        self.dict_ = {"type": "toptoolbar"}




if __name__ == "__main__":
    connect_to_db(app)
    db.create_all()
    main_func(list_of_book_objects)
    # cosine_similarity = cosine_similarity(bookobj_tokens_dict)