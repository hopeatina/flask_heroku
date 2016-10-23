from __future__ import division
from lxml import html
import requests
import urllib
from nltk import pos_tag, FreqDist
import operator
import nltk
import string

from flask import jsonify, request, Blueprint

crawlnews = Blueprint('crawlnews', __name__)


@crawlnews.route('/thenewsfeed', methods=['GET', 'POST'])
def newscrawler():

    requestedsite = request.json
    result = runCrawler(requestedsite)
    # result[1].plot(100, cumulative=False)
    # boom = result[1]

    return jsonify(result)


def isPunct(word):
    return len(word) == 1 and word in string.punctuation


def isNumeric(word):
    try:
        float(word) if '.' in word else int(word)
        return True
    except ValueError:
        return False

class RakeKeywordExtractor:
    def __init__(self):
        self.stopwords = set(nltk.corpus.stopwords.words())
        self.top_fraction = 1  # consider top third candidate keywords by score

    def _generate_candidate_keywords(self, sentences):
        phrase_list = []
        for sentence in sentences:
            words = map(lambda x: "|" if x in self.stopwords else x,
                        nltk.word_tokenize(sentence.lower()))
            phrase = []
            for word in words:
                if word == "|" or isPunct(word):
                    if len(phrase) > 0:
                        phrase_list.append(phrase)
                        phrase = []
                else:
                    phrase.append(word)
        return phrase_list

    def _calculate_word_scores(self, phrase_list):
        word_freq = nltk.FreqDist()
        word_degree = nltk.FreqDist()
        for phrase in phrase_list:
            degree = len(filter(lambda x: not isNumeric(x), phrase)) - 1
            for word in phrase:
                word_freq[word] += 1
                word_degree[word, degree] += 1  # other words
        for word in word_freq.keys():
            word_degree[word] = word_degree[word] + word_freq[word]  # itself
        # word score = deg(w) / freq(w)
        word_scores = {}
        for word in word_freq.keys():
            word_scores[word] = word_degree[word] / word_freq[word]
        return word_scores

    def _calculate_phrase_scores(self, phrase_list, word_scores):
        phrase_scores = {}
        for phrase in phrase_list:
            phrase_score = 0
            for word in phrase:
                phrase_score += word_scores[word]
            phrase_scores[" ".join(phrase)] = phrase_score
        return phrase_scores

    def extract(self, text, incl_scores=False):
        sentences = nltk.sent_tokenize(text)
        phrase_list = self._generate_candidate_keywords(sentences)
        word_scores = self._calculate_word_scores(phrase_list)
        phrase_scores = self._calculate_phrase_scores(
            phrase_list, word_scores)
        sorted_phrase_scores = sorted(phrase_scores.iteritems(),
                                      key=operator.itemgetter(1), reverse=True)
        n_phrases = len(sorted_phrase_scores)
        if incl_scores:
            return sorted_phrase_scores[0:int(n_phrases / self.top_fraction)]
        else:
            return map(lambda x: x[0],
                       sorted_phrase_scores[0:int(n_phrases / self.top_fraction)])

def test():
    rake = RakeKeywordExtractor()
    keywords = rake.extract("""
Compatibility of systems of linear constraints over the set of natural
numbers. Criteria of compatibility of a system of linear Diophantine
equations, strict inequations, and nonstrict inequations are considered.
Upper bounds for components of a minimal set of solutions and algorithms
of construction of minimal generating sets of solutions for all types of
systems are given. These criteria and the corresponding algorithms for
constructing a minimal supporting set of solutions can be used in solving
all the considered types of systems and systems of mixed types.
  """, incl_scores=True)
    # print keywords, len(keywords)

def returnbaseurl(requested):
    return {
        'Top': 'algorithm',
        'FierceBiotech': {
            'baseurl': 'http://www.fiercebiotech.com',
            'startpage': 'http://www.fiercebiotech.com/biotech',
            'nextpagefunc': 'caniputonehere?',
            'titlexpath': '//h2[@class="field-content list-title"]/a/text()',
            'linkxpath': '//h2[@class="field-content list-title"]/a',
            'timesxpath': '//span[@class="field-content"]/time/text()',
            'nextbuttonxpath': '//ul[@class="js-pager__items"]/li/a'},
        'Genomeweb': 2,
        'SynBioBeta': 2,
        'Labiotech': 2,
        'Xconomy': 2,
        'Twitter Lists': 2,
        'Biostars': 2,
        'Suggest a Source': 'algorithm'

    }[requested]


def runCrawler(requestedsite):
    siteitems = returnbaseurl(requestedsite)
    baseurllist = ['http://www.fiercebiotech.com/',
                   'https://www.statnews.com/',
                   'http://www.scientificamerican.com/medical-biotech/',
                   'http://www.xconomy.com/',
                   'http://www.sciencemag.org/news/latest-news',
                   'http://www.nature.com/nature/archive/category.html?code=archive_news',
                   ]
    baseurl = siteitems['baseurl']
    page = requests.get(siteitems['startpage'])
    tree = html.fromstring(page.content)
    count = 3
    alltitles = {
        "titles": [],
        "dates": []
    }
    nouns = []
    titleobject = { "objects": []}
    test()
    # This will create a list of buyers:
    while count > 0:
        titles = tree.xpath(siteitems['titlexpath'])
        # This will create a list of prices
        times = tree.xpath(siteitems['timesxpath'])
        links = tree.xpath(siteitems['linkxpath'])

        nextbutton = tree.xpath(siteitems['nextbuttonxpath'])
        if len(nextbutton)> 1:
            nextpage = nextbutton[1].get('href')
        else:
            nextpage = nextbutton[0].get('href')

        page = requests.get(baseurl + nextpage)
        tree = html.fromstring(page.content)
        print len(nextbutton), page
        for index, title in enumerate(titles):
            tagged_sent = pos_tag(title.encode('ascii', 'ignore').split())
            # [('Michael', 'NNP'), ('Jackson', 'NNP'), ('likes', 'VBZ'), ('to', 'TO'), ('eat', 'VB'), ('at', 'IN'), ('McDonalds', 'NNP')]

            propernouns = [word for word, pos in tagged_sent if (pos == 'NNP' or pos == 'NN')]
            nouns = nouns + propernouns
            # print propernouns, title.encode('ascii', 'ignore'), times[index]
            thisone = {
                "title": title.encode('ascii', 'ignore'),
                "date": times[index],
                "link": baseurl + links[index].get('href')
            }
            alltitles["titles"].append(title)
            alltitles["dates"].append(times[index])
            titleobject["objects"].append(thisone)
        count = count - 1

    # print len(nouns)


    frequencydist = FreqDist(nouns)
    # frequencydist.plot(100, cumulative=True)
    print titleobject
    # return frequencydist.most_common(100)
    return titleobject

# runCrawler()