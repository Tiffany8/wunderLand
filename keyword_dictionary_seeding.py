
from model import Book, connect_to_db, db
from flask_sqlalchemy import SQLAlchemy

from server import app
from sqlalchemy import exc
import pickle
import re

def seed_keywords():
    """ This function queries all of the books in my database
    and pulls out the descriptions and creates a dictionary of all words and 
    their occurance as key and value(s), respectively."""
    all_book_objs = Book.query.all()

    keyword_dictionary = {}

    #create a gigantic list of ALL of the book objects
    for book_obj in all_book_objs:
        print "Starting iteration through book: ", book_obj.title
        print "book obj: ", book_obj
        print 
        print
        #use regular expressions to remove all punctuation except ' and -
        #may check out NLTK
        title_string = book_obj.title
        title_string = title_string.replace("--", " ")
        print "done with title replacement", title_string
        print 
        print
        title_list = re.split(r"[^\w'-]", title_string)
        print "done with title regex", title_list
        print
        print
        #for each word in the description, add it as a key to the dictionary
        #and hold the tally as the value
        for word in title_list:
            print "title word", word
            print 
            print
            if word not in keyword_stopwords:
                keyword_dictionary[word.lower()] = keyword_dictionary.get(word.lower(), 0) + 1
        print "done with title words"


        firstwords_string = book_obj.first_words
        if firstwords_string:
            firstwords_string = firstwords_string.replace("--", " ")
            print "firstwords list after replacement: ", firstwords_string
            print 
            print
            firstwords_list = re.split(r"[^\w'-]", firstwords_string)
            print "firstword list after regex: ", firstwords_list
            print 
            print

            for word in firstwords_list:
                print "first word", word
                print
                print
                if word not in keyword_stopwords:
                    keyword_dictionary[word.lower()] = keyword_dictionary.get(word.lower(), 0) + 1
            print "done with first words"


        #pull out the descriptions for each book object
        description_string = book_obj.description
        print "book description: ", description_string
        print
        print
        if description_string:
            description_string = description_string.replace("--", " ")
            print "description string after replacement: ", description_string
            print
            print
            description_list = re.split(r"[^\w'-]", description_string)
            print "description list after regex: ", description_list
            print
            print

            #for each word in the description, add it as a key to the dictionary
            #and hold the tally as the value
            for word in description_list:
                print "description word", word
                print 
                print
                if word not in keyword_stopwords:
                    keyword_dictionary[word.lower()] = keyword_dictionary.get(word.lower(), 0) + 1
        print "Done with, ", book_obj.title
        print "#" * 40
        print "#" * 40
        print "#" * 40

    pickle.dump(keyword_dictionary, open( "keyword_dictionary.p", "wb" ))


# def sedding_words_quotes():keyword_stopwords = [u'i', u'me', u'my', u'myself', u'we', u'our', u'ours', u'ourselves', u'you', u'your', u'yours', u'yourself', 
u'yourselves', u'he', u'him', u'his', u'himself', u'she', u'her', u'hers', u'herself', u'it', u'its', u'itself', u'they', u'them', 
u'their', u'theirs', u'themselves', u'what', u'which', u'who', u'whom', u'this', u'that', u'these', u'those', u'am', u'is', u'are', 
u'was', u'were', u'be', u'been', u'being', u'have', u'has', u'had', u'having', u'do', u'does', u'did', u'doing', u'a', u'an', u'the', 
u'and', u'but', u'if', u'or', u'because', u'as', u'until', u'while', u'of', u'at', u'by', u'for', u'with', u'about', u'against', 
u'between', u'into', u'through', u'during', u'before', u'after', u'above', u'below', u'to', u'from', u'up', u'down', u'in', u'out', 
u'on', u'off', u'over', u'under', u'again', u'further', u'then', u'once', u'here', u'there', u'when', u'where', u'why', u'how', u'all', 
u'any', u'both', u'each', u'few', u'more', u'most', u'other', u'some', u'such', u'no', u'nor', u'not', u'only', u'own', u'same', u'so', 
u'than', u'too', u'very', u's', u't', u'can', u'will', u'just', u'don', u'should', u'now']
#     quotes_list = 

[u'a', u'about', u'above', u'after', u'again', u'against', u'all', u'am', u'an', u'and', u'any', u'are', u'as', u'at', u'be', u'because', 
u'been', u'before', u'being', u'below', u'between', u'both', u'but', u'by', u'can', u'did', u'do', u'does', u'doing', u'don', u'down', 
u'during', u'each', u'few', u'for', u'from', u'further', u'had', u'has', u'have', u'having', u'he', u'her', u'here', u'hers', u'herself', 
u'him', u'himself', u'his', u'how', u'i', u'if', u'in', u'into', u'is', u'it', u'its', u'itself', u'just', u'me', u'more', u'most', u'my', 
u'myself', u'no', u'nor', u'not', u'now', u'of', u'off', u'on', u'once', u'only', u'or', u'other', u'our', u'ours', u'ourselves', u'out', 
u'over', u'own', u's', u'same', u'she', u'should', u'so', u'some', u'such', u't', u'than', u'that', u'the', u'their', u'theirs', u'them', 
u'themselves', u'then', u'there', u'these', u'they', u'this', u'those', u'through', u'to', u'too', 'u"he\'s"', 'u"it\'s"', 'u"she\'s"', 
"u''", "u'-'", "u'000'", "u'1'", "u'a'", "u'about'", "u'account'", "u'across'", "u'after'", "u'again'", "u'against'", "u'all'", "u'along'", 
"u'also'", "u'always'", "u'among'", "u'an'", "u'and'", "u'another'", "u'any'", "u'anyone'", "u'are'", "u'around'", "u'as'", "u'at'", "u'author'", 
"u'available'", "u'away'", "u'back'", "u'based'", "u'be'", "u'because'", "u'become'", "u'becomes'", "u'been'", "u'before'", "u'begins'", "u'behind'", "u'being'", "u'best'", "u'better'", "u'between'", "u'beyond'", "u'big'", "u'book'", "u'books'", "u'both'", "u'bring'", "u'brings'", "u'brought'", "u'but'", "u'by'", "u'called'", "u'can'", "u'change'", "u'chapter'", "u'chapters'", "u'characters'", "u'come'", "u'comes'", "u'common'", "u'complete'", "u'contains'", "u'could'", "u'course'", "u'crime'", "u'd'", "u'days'", "u'de'", "u'do'", "u'does'", "u'down'", "u'during'", "u'each'", "u'early'", "u'edition'", "u'end'", "u'even'", "u'events'", "u'ever'", "u'every'", "u'everything'", "u'face'", "u'far'", "u'features'", "u'few'", "u'fight'", "u'finally'", "u'find'", "u'finds'", "u'first'", "u'for'", "u'found'", "u'four'", "u'from'", "u'full'", "u'get'", "u'gives'", "u'go'", "u'going'", "u'good'", "u'great'", "u'group'", "u'had'", "u'hardcover'", "u'has'", "u'have'", "u'he'", "u'her'", "u'here'", "u'herself'", "u'high'", "u'him'", "u'himself'", "u'his'", "u'how'", "u'i'", "u'if'", "u'important'", "u'in'", "u'includes'", "u'including'", "u'inside'", "u'into'", "u'introduction'", "u'is'", "u'issues'", "u'it'", "u'its'", "u'just'", "u'keep'", "u'key'", "u'know'", "u'known'", "u'knows'", "u'land'", "u'last'", "u'later'", "u'leading'", "u'left'", "u'life'", "u'like'", "u'list'", "u'literary'", "u'little'", "u'live'", "u'lives'", "u'long'", "u'look'", "u'made'", "u'major'", "u'make'", "u'makes'", "u'making'", "u'many'", "u'may'", "u'might'", "u'more'", "u'most'", "u'moving'", "u'much'", "u'must'", "u'my'", "u'named'", "u'need'", "u'never'", "u'new'", "u'next'", "u'no'", "u'not'", "u'nothing'", "u'novel'", "u'novels'", "u'now'", "u'of'", "u'off'", "u'offers'", "u'often'", "u'old'", "u'on'", "u'once'", "u'one'", "u'only'", "u'or'", "u'order'", "u'other'", "u'others'", "u'our'", "u'out'", "u'over'", "u'own'", "u'paperback'", "u'part'", "u'people'", "u'place'", "u'plan'", "u'post'", "u'practical'", "u'present'", "u'process'", "u'provides'", "u'published'", "u'questions'", "u'r'", "u'range'", "u'read'", "u'reader'", "u'readers'", "u'reading'", "u'real'", "u'really'", "u'reprint'", "u'reveals'", "u'right'", "u'role'", "u's'", "u'same'", "u'save'", "u'second'", "u'see'", "u'she'", "u'short'", "u'should'", "u'shows'", "u'side'", "u'since'", "u'small'", "u'so'", "u'some'", "u'something'", "u'soon'", "u'special'", "u'state'", "u'still'", "u'stop'", "u'stories'", "u'story'", "u'such'", "u'suddenly'", "u't'", "u'take'", "u'takes'", "u'tale'", "u'tales'", "u'tells'", "u'text'", "u'than'", "u'that'", "u'the'", "u'their'", "u'them'", "u'themselves'", "u'then'", "u'there'", "u'these'", "u'they'", "u'thing'", "u'things'", "u'think'", "u'this'", "u'those'", "u'thought'", "u'three'", "u'through'", "u'throughout'", "u'time'", "u'times'", "u'to'", "u'today'", "u'together'", "u'told'", "u'too'", "u'topics'", "u'true'", "u'truth'", "u'turn'", "u'turns'", "u'two'", "u'under'", "u'understand'", "u'understanding'", "u'until'", "u'up'", "u'upon'", "u'us'", "u'use'", "u'used'", "u'using'", "u'very'", "u'volume'", "u'want'", "u'wants'", "u'war'", "u'was'", "u'way'", "u'ways'", "u'we'", "u'well'", "u'were'", "u'what'", "u'when'", "u'where'", "u'whether'", "u'which'", "u'while'", "u'who'", "u'whose'", "u'why'", "u'will'", "u'with'", "u'within'", "u'without'", "u'work'", "u'working'", "u'works'", "u'would'", "u'writer'", "u'writers'", "u'writing'", "u'written'", "u'year'", "u'years'", "u'yet'", "u'you'", "u'your'", u'under', u'until', u'up', u'very', u'was', u'we', u'were', u'what', u'when', u'where', u'which', u'while', u'who', u'whom', u'why', u'will', u'with', u'you', u'your', u'yours', u'yourself', u'yourselves']


### Notes on how to access data:
### how to open the file:: keywords = pickle.load(open("keyword_dictionary.p", "rb"))
### sorted_ = sorted(keywords.items(), key=lambda (k,v):(v,k)) -- returns list of tuples with the word
### and number of instances of word

### file = open("top_keywords_above70.txt")
### for item in file:
file = open("top_keywords_above70.txt")
for item in file:
    if item[-1]:
        if item[-1] != "*":
            item = item.lstrip("(").rstrip(")").split(",")
            new_item =  item[0].lstrip(""").rstrip(""")
            print new_item


### stopwords:

if __name__ == "__main__":
    connect_to_db(app)
    seed_keywords()
