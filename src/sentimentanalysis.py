import re
import nltk
import string
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from collections import Counter


class sentiment:
    feature_word_list = None
    stop_word_list = None
    all_word_list = None
    local_stemmer = None
    local_classifier = None

    def trainclassifier(self, training_set):
        self.local_classifier = nltk.NaiveBayesClassifier.train(training_set)

    def getaccuracy(self, testing_set):
        return nltk.classify.accuracy(self.local_classifier, testing_set)

    def individualprediction(self, testing_feature):
        return self.local_classifier.prob_classify(testing_feature)

    def createmlset(self, data, labeled=True):
        return nltk.classify.apply_features(self.getmembership, data, labeled=labeled)

    def getmembership(self, tokenized_message):
        tokenized_message = set(tokenized_message)
        membership = {}
        for word in self.feature_word_list.__iter__():
            membership['%s' % word] = word in tokenized_message
        return membership

    def getfrequencydist(self, all_words):
        return Counter(all_words)

    def setwordlist(self, all_words):
        for word in all_words:
            self.feature_word_list.add(word)

    def stemwords(self, tokenized_message):
        return [self.local_stemmer.stem(x) for x in tokenized_message]

    def removestopwords(self, tokenized_message):
        return [x for x in tokenized_message if x not in self.stop_word_list]

    def tokenizedata(self, message):
        return [unicode(x, errors='replace') for x in nltk.word_tokenize(message)]

    def removepunctuation(self, string_line):
        return string_line.translate(None, string.punctuation)

    def cleanandcreatemlset(self, training_data, testing_data, testing_has_labels=True):
        cleaned_training_data = []
        cleaned_testing_data = []
        print 'training set'
        for (message, label) in training_data:
            message = message.lower()
            punctuation_removed_message = self.removepunctuation(message)
            tokenized_message = self.tokenizedata(punctuation_removed_message)
            stop_words_removed = self.removestopwords(tokenized_message)
            stemmed_words = self.stemwords(stop_words_removed)
            self.setwordlist(stemmed_words)
            cleaned_training_data.append((stemmed_words, label))

        print 'testing set'
        for maybe_tuple in testing_data:
            message = maybe_tuple[0] if testing_has_labels else maybe_tuple
            message = message.lower()
            punctuation_removed_message = self.removepunctuation(message)
            tokenized_message = self.tokenizedata(punctuation_removed_message)
            stop_words_removed = self.removestopwords(tokenized_message)
            stemmed_words = self.stemwords(stop_words_removed)
            cleaned_testing_data.append(
                    (stemmed_words, maybe_tuple[1]) if testing_has_labels else stemmed_words)

        print 'training set ML'
        training_set = self.createmlset(cleaned_training_data)
        print 'testing set ML'
        testing_set = self.createmlset(cleaned_testing_data, testing_has_labels)
        return training_set, testing_set

    def __init__(self):
        self.feature_word_list = set()
        self.stop_word_list = stopwords.words()
        self.all_word_list = []
        self.local_stemmer = PorterStemmer()
