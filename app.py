"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/

This file creates your application.
"""
from __future__ import division
import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
import logging
from slackclient import SlackClient
import unicodedata
from neo4jrestclient.client import GraphDatabase
from neo4jrestclient.constants import RAW
from neo4jrestclient import client
from flask.ext.triangle import Triangle
import re
from fromdb import from_api
# from simulator import simulator
import operator
from nltk import pos_tag
import nltk
import string

# gdb = GraphDatabase(os.environ.get("GRAPHENEDB_URL"))
graphurl = "http://app52089542-qMnWmY:PTPE2ka4DyL8PxESRfuR@app52089542qmnwmy.sb05.stations.graphenedb.com:24789"

gdb = GraphDatabase(graphurl)
users = gdb.labels.create("User")
channels = gdb.labels.create("Channel")
links = gdb.labels.create("Link")
messages = gdb.labels.create("Message")
Tags = gdb.labels.create("Tag")

useridx = gdb.nodes.indexes.create("users")
channelidx = gdb.nodes.indexes.create("channels")
linkidx = gdb.nodes.indexes.create("links")
messageidx = gdb.nodes.indexes.create("messages")
Tagsidx = gdb.nodes.indexes.create("Tags")

Byidx = gdb.relationships.indexes.create("By")
Includesidx = gdb.relationships.indexes.create("Includes")
Mentionsidx = gdb.relationships.indexes.create("Mentions")

# token = os.environ.get('SLACKTOKEN')
token = 'xoxp-48970123489-48964881879-50048816096-fd79da89e6'

# found at https://api.slack.com/web#authentication
sc = SlackClient(token)

app = Flask(__name__)
Triangle(app)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'this_should_be_configured')
app.register_blueprint(from_api)
# app.register_blueprint(simulator)

###
# Routing for your application.
###

@app.route('/demo')
def home():
    test = sc.api_call("api.test")
    channels = sc.api_call("channels.list", token=token)
    # print channels
    logging.debug(channels)
    # print sc.api_call(
    #     "chat.postMessage", channel="#general", text="Hello from Python! :tada:",
    #     username='pybot', icon_emoji=':robot_face:'
    # )
    """Render website's home page."""
    return render_template('home.html', test=test, channels=channels, msglist='')

@app.route('/thefeed')
def feedcrawler():
    test = sc.api_call("api.test")
    channels = sc.api_call("channels.list", token=token)
    # print channels
    logging.debug(channels)
    # print sc.api_call(
    #     "chat.postMessage", channel="#general", text="Hello from Python! :tada:",
    #     username='pybot', icon_emoji=':robot_face:'
    # )
    """Render website's feed page"""
    return render_template('feed.html')

@app.route('/')
def fronthome():

    return render_template('intro.html')


@app.route('/api/getchannels', methods=['GET', 'POST'])
def getchannels():
    # print("Got rest api")
    channels = sc.api_call("channels.list", token=token)
    # print channels
    # return jsonify({"list": "channels"})
    return jsonify(channels)


@app.route('/api/getcategories', methods=['GET', 'POST'])
def getcategories():
    print("Got categories/users")
    users = sc.api_call("users.list",token=token)
    # return jsonify({"list": "channels"})
    return jsonify(users)

@app.route('/api/batchprocess', methods=['GET', 'POST'])
def dailybatch():

    # Get list of channels
    channellist = sc.api_call("channels.list", token=token)

    # Check last processed time
    for achannel in channellist:
        createEntity(channels,achannel,channelidx,)
        msglist = sc.api_call("channels.history", token=token, channel=achannel.id)

        # For each channel run create node/rel process while process greater than channel time
        processMessages(msglist=msglist,lasttime=0)


    allnodequery = "MATCH (node:User) RETURN node"
    numnodesquery = "MATCH (node) "
    numrelsquery = ""
    betweenessquery = ""
    nummessagesquery = ""
    params = {}
    querySquenceObject = gdb.query(allnodequery, params=params, returns=RAW)
    for node in querySquenceObject:
        n = node.pop()
        uid = n.get('metadata').get('id')
        data = n.get('data')
        value = data.get('value')

    # Get all user nodes
    # Update stats for the nodes
    # Find a way to run this daily
    return

@app.route('/api/getteaminfo', methods=['GET', 'POST'])
def getteaminfo():
    print("Got team information")
    # return jsonify({"list": "channels"})
    return {"list": ["channels","ch"]}


@app.route('/switchmsg', methods=['GET', 'POST'])
def foo(x=None, y=None):
    # do something to send email
    id = request.form['id']
    channels = sc.api_call("channels.list", token=token)
    msglist = sc.api_call("channels.history", token=token, channel=id)
    foundlinks = []
    testtext = ""
    keywords = []
    for msg in msglist['messages']:
        msgencode = unicodedata.normalize('NFKD', msg['text']).encode('ascii', 'ignore')
        userencode = unicodedata.normalize('NFKD', msg['user']).encode('ascii', 'ignore')
        # foundlinks.append(re.findall("<(.*?)>", msgencode))
        # Parse msg for top 3 Tags
        # Check then Create Tag
        # Connect Message to Tag
        # Connect User to Ta
        entities = re.findall("<(.*?)>", msgencode)
        tagentities = re.findall("<.*?>", msgencode)

        cleanmsg = removeent(msgencode, tagentities)
        testtext = testtext + " " + cleanmsg.lower()
        createnodes(entities, msgencode, userencode)
        keywordray = parseTags(cleanmsg.lower())
        keywordray.sort(key=len)
        # print len(keywordray), cleanmsg, msgencode
        if len(keywordray) > 2 and keywordray != []:
            # print "inside if", keywordray
            keywordray.reverse()
            keywordray = keywordray[:2]
        for tag in keywordray:
            print "BOUTTA CREATE TAG", tag, keywordray
            createrelationship(userencode,tag,"tag",msgencode)
        keywords.append(keywordray)

    test(testtext)
    print "keywords" + str(keywords)
    return render_template('home.html', test=test, channels=channels, msglist='')

def createnodes(entitieslist, msg, originuser):

    #remove entitieslist from ms
    # noentitymsg = removeent(msg['text'], entitieslist)

    for entity in entitieslist:
        if entity[:2] == "#C": # Channel
            # print "Channel: " + entity
            createrelationship(originuser, entity, "channel", msg)
        elif entity[:2] == "@U": # User
            # print "User: " + entity
            createrelationship(originuser, entity, "user", msg)
        elif entity[:1] == "!": #Special?
            specials()
        elif entity[:4] == "http": #Link
            # print "Link: " + entity
            createrelationship(originuser, entity, "link", msg)

    if entitieslist == []:
        createrelationship(originuser, "", "text", msg)


def createRelEnt(relationship,relationshipidx, reltype, end, origin):

    interim = end["value"].encode('ascii', 'ignore')
    rels = relationshipidx[reltype][interim]
    print "Created Relationship: " + str(len(rels)) \
          + ", (Origin: " + origin['value'] +  "), (" + reltype + "), (End: " + end['value'] +") interim: " + interim
    # print "FROM TO" , origin, reltype, end
    if len(rels) > 0:
        objectnode = rels[0]
        id = objectnode.id
        returnrel = gdb.relationships[id]
        count = returnrel.get("count") + 1
        # print id, returnrel.get("count"), count
        returnrel.set("count", count)
        print "rel count increase", returnrel.get('value')
    else:
        objectrel = relationship.create(reltype, end, value=end["value"].encode('ascii', 'ignore'), count=1)
        relationshipidx[reltype][interim] = objectrel
        print "new rel:", interim, objectrel
    return


def createEntity(type, object, idx, idxtext):
    # creates an entity in the database after checking if it exists
    nodes = idx[idxtext][object]
    print "Created Entity: " + str(len(nodes)) + " " + idxtext + ": " + str(object)
    if idxtext == "users":
        response = sc.api_call("users.info", user=str(object))
        img = response['user']['profile']['image_48']
        name = response['user']
    else:
        img = ''
        dateTime = ''
        name = ''

    if len(nodes) > 0:
        objectnode = nodes[0]
        id = objectnode.id
        returnnode = gdb.node[id]
        count = returnnode.get("count") + 1
        returnnode.set("count", count)
        print "node count increase", object
    else:
        objectnode = type.create(value=object, count=1, type=idxtext, img=img, date="JULY 26, 2016")
        idx[idxtext][objectnode["value"]] = objectnode
        print "new node:", objectnode["value"]

    return objectnode


def createrelationship(originuser, object, nodetype, msgtext):
    # type: (str, str, str, str) -> none
    # msgtext = unicodedata.normalize('NFKD', msg['text']).encode('ascii', 'ignore')
    idname = object.split('|', 1)
    # print idname

    print nodetype, object
    if nodetype == 'channel':

        ch = createEntity(channels, object, channelidx, "channels")
        msg = createEntity(messages, msgtext, messageidx, "messages")
        user = createEntity(users, originuser, useridx, "users")
        createRelEnt(msg.relationships, Byidx, "By", user, msg)
        createRelEnt(msg.relationships, Includesidx, "Includes", ch, msg)
        createRelEnt(user.relationships, Mentionsidx, "Mentions", ch, user)

        # msg.relationships.create("By", user, count=1)
        # msg.relationships.create("Includes", ch, count=1)
        # user.relationships.create("Mentions", ch, count=1)
        # channelidx["channels"][ch["value"]] = ch
        # useridx["users"][user["value"]] = user
        # messageidx["messages"][msg["value"]] = msg
    elif nodetype == 'user':
        # if len(idname) > 1:
        #     use = idname[1]
        # else:
        use = idname[0].replace('@', '')

        entuser = createEntity(users, use, useridx, "users")
        msg = createEntity(messages, msgtext, messageidx, "messages")
        user = createEntity(users, originuser, useridx, "users")
        createRelEnt(msg.relationships, Byidx, "By", user, msg)
        createRelEnt(msg.relationships, Includesidx, "Includes", entuser, msg)
        if user != entuser:
            createRelEnt(user.relationships, Mentionsidx, "Mentions", entuser, user)

    elif nodetype == 'link':
        lnk = createEntity(links, object, linkidx, "links")
        msg = createEntity(messages, msgtext, messageidx, "messages")
        user = createEntity(users, originuser, useridx, "users")
        createRelEnt(msg.relationships, Byidx, "By", user, msg)
        createRelEnt(msg.relationships, Includesidx, "Includes", lnk, msg)
        createRelEnt(user.relationships, Mentionsidx, "Mentions", lnk, user)

    elif nodetype == 'tag':
        tag = createEntity(Tags, object, Tagsidx,"Tags")
        msg = createEntity(messages, msgtext, messageidx, "messages")
        user = createEntity(users, originuser, useridx, "users")
        createRelEnt(msg.relationships, Includesidx, "Includes", tag, msg)
        createRelEnt(user.relationships, Mentionsidx, "Mentions", tag, user)
        createRelEnt(msg.relationships, Byidx, "By", user, msg)
    else:
        msg = createEntity(messages, msgtext, messageidx, "messages")
        user = createEntity(users, originuser, useridx, "users")
        createRelEnt(msg.relationships, Byidx, "By", user, msg)

    return

def createNodeStats():
    nodestats = []
    return nodestats

def createGraphStats():
    graphstats = []
    return graphstats


def parseTags(msg):
    tagged_msg = pos_tag(msg.split())
    BAD_CHARS = ":.!?,\'\""
    allnouns = [word.strip(BAD_CHARS) for word, pos in tagged_msg if (pos == 'NNP' or pos == 'NN') and len(word) > 2]
    return allnouns


def processMessages(msglist, lasttime):
    for msg in msglist['messages']:
        print msg['ts']
        if msg['ts'] < lasttime:
            break
        else:

            msgencode = unicodedata.normalize('NFKD', msg['text']).encode('ascii', 'ignore')
            msgdate = unicodedata.normalize('NFKD', msg['ts']).encode('ascii', 'ignore')
            userencode = unicodedata.normalize('NFKD', msg['user']).encode('ascii', 'ignore')

            entities = re.findall("<(.*?)>", msgencode)
            tagentities = re.findall("<.*?>", msgencode)

            cleanmsg = removeent(msgencode, tagentities)
            keywordray = parseTags(cleanmsg.lower())
            keywordray.sort(key=len)

            # processes for entities and msgs
            createnodes(entities, msgencode, userencode)

            # print len(keywordray), cleanmsg, msgencode
            if len(keywordray) > 2 and keywordray != []:
                # print "inside if", keywordray
                # sort from big to small
                keywordray.reverse()
                # only use two tags per message
                keywordray = keywordray[:2]
            for tag in keywordray:
                print "BOUTTA CREATE TAG", tag, keywordray
                createrelationship(userencode, tag, "tag", msgencode)

    return

def removeent(msg, entities):
    query = msg
    stopwords = entities
    querywords = query.split()
    resultwords = [word for word in querywords if word not in stopwords]
    result = ' '.join(resultwords)
    # print "entities: ", str(entities), "querywords: ", str(querywords) + " result: " + result
    return result



def specials():
    return


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html')


###
# The functions below should be applicable to all Flask apps.
###

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=600'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404

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
        self.top_fraction = 1  # consider top third candidate keywords By score

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


def test(text):
    rake = RakeKeywordExtractor()
    keywords = rake.extract(text, incl_scores=True)
    print keywords, len(keywords)

if __name__ == '__main__':
    app.run(debug=True)
