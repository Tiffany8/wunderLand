#install nltk (maxent_treebank...; punkt tokenizer; stopwords corpus), re, pprint, numpy
#tokenize all of the descriptions, first words, quotes
#remove stop words
#use stemmer (porter stemming algorithm)
#when adding to the dictionary, remove words that appear less than 2-3 times
import nltk
from nltk.corpus import stopwords
from collections import Counter
from server import app
from model import Book, Author, Location, Category, Event, Award, connect_to_db, db
import pprint
from flask_sqlalchemy import SQLAlchemy
import re

pp = pprint.PrettyPrinter(indent=4)

def extracting_keywords_from_text():
    list_of_book_objects = Book.query.filter(Book.title.ilike('war%')).all()

    for book_obj in list_of_book_objects:
        # description = book_obj.description
        if book_obj.description:
            print "book: ", book_obj.title, "description: ", book_obj.description
            tree = tokenize_tag_text(book_obj.description)
            print "tree:"
            pp.pprint(tree)
            terms = get_terms(tree)
            print "terms:"
            pp.pprint(terms)
            print "#" * 40
            print book_obj.title
            list_of_terms = []
            for term in terms:
                term_phrase = " ".join(term)
                print "term phrase, ", term_phrase
                list_of_terms.append(term_phrase)
                # for word in term:
                #     print word,
            print list_of_terms
            count = Counter(list_of_terms)
            print count.most_common(20)
            print "#" * 40
            print "#" * 40
            print "#" * 40
            print "#" * 40

        

       
    
        # first_words = book_obj.first_words
        # title = book_obj.title #may be useful for books w/ descrip, fw, quotes
        # for quote in book_obj.quotes:
        #   if [quote.quote for quote in abook.quotes] #if quote exist
        #       quote_obj = quote #the quote object
        #       quote = quote.quote #the quote itself
        #                   #pull out keywords from each quote
        #                   #should i pull out keywords from quotes? useful? biased?
        # if [event.event for event in abook.events]:
        #   event = event.event.upper() #uppercase to make event proper noun, if not already
        #                   #pull out keywords from event
        #                   #do i want to make the event apart of keywords or just add to the tag cloud?
        #                   #what to do if books have no descrip/quotes/firstwords?
        # #should I add each item to a list and then iterate through to extract KWs?
def tokenize_tag_text(description):
    # description = re.split(r"[^\w'-]", description)  
    sentence_re = r'''(?x)
    ([A-Z])(\.[A-Z])+\.? 
    | \w+(-\w+)*         
    | \$?\d+(\.\d+)?%?  
    | \.\.\.            
    | [][.,;"?():-_`]  
    '''

    # set flag to allow verbose regexps
    # words with optional internal hyphens
    # currency and percentages
    # ellipsis
    # separate tokens


    #Taken from Su Nam Kim paper (Evaluating n-gram based evaluation 
    #metrics for automatic keyphrase extraction.) 
    grammar = r"""
    NBAR:
        {<NN.*|JJ>*<NN.*>}  # Nouns and Adjectives, terminated with Nouns
        {<NNP|NNPS>+<IN>?<NNP|NNPS>+}
        {<DT|PP\$>?<JJ>*<NN|NNS>}
        {<NN>+}

    NP:
        {<NBAR>}
        {<NBAR><IN><NBAR>}  # Above, connected with in/of/etc...
    """

        # Nouns and Adjectives, terminated with Nouns
        # Above, connected with in/of/etc...

    chunker = nltk.RegexpParser(grammar)
    toks = nltk.regexp_tokenize(description, sentence_re)
    postoks = nltk.tag.pos_tag(toks)
    # import pdb; pdb.set_trace()
    # print postoks
    tree = chunker.parse(postoks)
    return tree 

def get_terms(tree):
    for leaf in leaves(tree):
        # print "leaf, ", leaf
        for word in leaf:
            if word[1] != 'NNP':
                term = [ normalise(word) for word,tag in leaf if acceptable_word(word) ]
            else:
                term = [word for word, tag in leaf]
        yield term
         
def leaves(tree):
    """Finds NP (nounphrase) leaf nodes of a chunk tree."""
    for subtree in tree.subtrees(filter = lambda t: t.label()=='NP'):
        yield subtree.leaves()

 
def normalise(word):
    """Normalises words to lowercase and stems and lemmatizes it."""

    lemmatizer = nltk.WordNetLemmatizer()
    stemmer = nltk.stem.porter.PorterStemmer()

    word = word.lower()
    # word = stemmer.stem_word(word)
    word = lemmatizer.lemmatize(word)
    return word
 
def acceptable_word(word):
    """Checks conditions for acceptable word: length, stopword."""
    stopwords1 = stopwords.words('english')
    accepted = bool(2 <= len(word) <= 40
        and word.lower() not in stopwords1)
    return accepted
 
 

 
if __name__ == "__main__":
    connect_to_db(app)
    db.create_all()
    extracting_keywords_from_text()



