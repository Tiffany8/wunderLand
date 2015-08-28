import nltk
from nltk.corpus import stopwords
from collections import Counter
from model import Keyword, connect_to_db, db
import pprint
from nltk.stem.wordnet import WordNetLemmatizer


def extracting_keywords_from_text(list_of_book_objects):
    """ Takes a list of book objects, and if the book has a description, create
    keyword and keyword phrases and store the top twenty in the local database.
    Keyword and keyword phrases are stored in a keyword table as well as a
    keyword-book association table."""

    for book_obj in list_of_book_objects:
        if book_obj.description:
            print "book: ", book_obj.title, "description: ", book_obj.description
            tree = tokenize_tag_text(book_obj.description)
            print "tree:"
            pprint(tree)
            terms = get_terms(tree)
            print "terms:"
            pprint(terms)
            print "#" * 40
            print book_obj.title
            list_of_terms = []
            for term in terms:
                term_phrase = " ".join(term)
                print "term phrase, ", term_phrase
                list_of_terms.append(term_phrase)
            print list_of_terms
            count = Counter(list_of_terms)
            top_twenty_terms = count.most_common(20)
            print top_twenty_terms
            # print type(top_twenty_terms)
            print "#" * 40
            print "#" * 40
            print "#" * 40
            print "#" * 40
            for term in top_twenty_terms:
                keyword_instance = Keyword(keyword=term[0])
                if not Keyword.query.filter_by(keyword=term[0]).first():
                    db.session.add(keyword_instance)
                else:
                    print "the word, ", term[0], " already in database"
                keyword_instance.books.append(book_obj)


def tokenize_tag_text(description):
    """Removes some punctuation, tags each word by part-of-speech, and
    generates keyword and keyword prhases  based on noun phrases patterns
    using regexp."""

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

    chunker = nltk.RegexpParser(grammar)
    toks = nltk.regexp_tokenize(description, sentence_re)
    postoks = nltk.tag.pos_tag(toks)
    tree = chunker.parse(postoks)
    return tree


def get_terms(tree):
    """Returns acceptable, lemmatized keywords."""
    
    for leaf in leaves(tree):
        for word in leaf:
            if word[1] != 'NNP':
                term = [normalise(word) for word, tag in leaf if acceptable_word(word)]
            else:
                term = [word for word, tag in leaf]
        yield term


def leaves(tree):
    """Finds NP (nounphrase) leaf nodes of a chunk tree."""
    
    for subtree in tree.subtrees(filter=lambda t: t.label()=='NP'):
        yield subtree.leaves()


def normalise(word):
    """Normalises words to lowercase and lemmatizes it."""
    
    lemmatizer = WordNetLemmatizer()
    word = word.lower()
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
    extracting_keywords_from_text(list_of_book_objects)