"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/

This file creates your application.
"""

import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
import logging
from slackclient import SlackClient
import unicodedata
from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import client
from flask.ext.triangle import Triangle
import re
from fromdb import from_api


gdb = GraphDatabase(os.environ.get("GRAPHENEDB_URL"))
users = gdb.labels.create("User")
channels = gdb.labels.create("Channel")
links = gdb.labels.create("Link")
messages = gdb.labels.create("Message")

useridx = gdb.nodes.indexes.create("users")
channelidx = gdb.nodes.indexes.create("channels")
linkidx = gdb.nodes.indexes.create("links")
messageidx = gdb.nodes.indexes.create("messages")
byidx = gdb.relationships.indexes.create("By")
includesidx = gdb.relationships.indexes.create("Includes")
mentionsidx = gdb.relationships.indexes.create("Mentions")


# token = os.environ.get('SLACKTOKEN')
token = 'xoxp-48970123489-48964881879-50048816096-fd79da89e6'

# found at https://api.slack.com/web#authentication
sc = SlackClient(token)

app = Flask(__name__)
Triangle(app)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'this_should_be_configured')
app.register_blueprint(from_api)

###
# Routing for your application.
###

@app.route('/')
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


@app.route('/api/getchannels', methods=['GET', 'POST'])
def getchannels():
    # print("Got rest api")
    channels = sc.api_call("channels.list", token=token)
    # print channels
    # return jsonify({"list": "channels"})
    return jsonify(channels)


@app.route('/api/getcategories', methods=['GET', 'POST'])
def getcategories():
    print("Got categories")
    users = sc.api_call("users.list",token=token)
    # return jsonify({"list": "channels"})
    return jsonify(users)


# @app.route('/api/getexploredata', methods=['GET', 'POST'])
# def getexploredata():
#     query = "start n=node(*) MATCH (nodes)--> (user:User {value:" + request.data + "}) RETURN user, nodes"
#     result = gdb.query(q=query,data_contents=True)
#     print("Got explorer data", request.data, result)
#     print("DIR", dir(result))
#     # print result.graph
#     # graph = result.graph
#
#
#
#     # return jsonify({"list": "channels"})
#     return result

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
    for msg in msglist['messages']:
        msgencode = unicodedata.normalize('NFKD', msg['text']).encode('ascii', 'ignore')
        userencode = unicodedata.normalize('NFKD', msg['user']).encode('ascii', 'ignore')
        foundlinks.append(re.findall("<(.*?)>", msgencode))
        createnodes(re.findall("<(.*?)>", msgencode), msg, userencode)
    return render_template('home.html', channels=channels, msglist=msglist, foundlinks=foundlinks)


def createnodes(entitieslist, msg, originuser):
    for entity in entitieslist:
        if entity[:2] == "#C":
            # print "Channel: " + entity
            createrelationship(originuser, entity, "channel", msg)
        elif entity[:2] == "@U":
            # print "User: " + entity
            createrelationship(originuser, entity, "user", msg)
        elif entity[:1] == "!":
            specials()
        else:
            # print "Link: " + entity
            createrelationship(originuser, entity, "link", msg)

    if entitieslist == []:
        createrelationship(originuser, "", "text", msg)


def createRelEnt(relationship,relationshipidx, reltype, end, origin):

    interim = origin["value"].encode('ascii', 'ignore')
    rels = relationshipidx[reltype][interim]
    print "Created Relationship: " + str(len(rels)) + " " + reltype + " End: " + end['value'] + " Origin: " + origin['value']
    if len(rels) > 0:
        objectnode = rels[0]
        id = objectnode.id
        returnrel = gdb.relationships[id]
        count = returnrel.get("count") + 1
        print id, returnrel.get("count"), count
        returnrel.set("count", count)
    else:
        objectrel = relationship.create(reltype, end, value=end["value"].encode('ascii', 'ignore'), count=1)
        relationshipidx[reltype][interim] = objectrel

    return


def createEntity(type, object, idx, idxtext):
    # creates an entity in the database after checking if it exists
    nodes = idx[idxtext][object]
    print "Created Entity: " + str(len(nodes)) + " " + idxtext + ": " + str(object)
    if idxtext == "users":
        response = sc.api_call("users.info", user=str(object))
        img = response['user']['profile']['image_48']
    else:
        img = ''

    if len(nodes) > 0:

        objectnode = nodes[0]
        id = objectnode.id
        returnnode = gdb.node[id]
        count = returnnode.get("count") + 1
        returnnode.set("count", count)
    else:
        objectnode = type.create(value=object, count=1, type=idxtext, img=img)
        idx[idxtext][objectnode["value"]] = objectnode

    return objectnode


def createrelationship(originuser, object, nodetype, msg):
    # type: (str, str, str, str) -> none
    msgtext = unicodedata.normalize('NFKD', msg['text']).encode('ascii', 'ignore')
    idname = object.split('|', 1)
    # print idname

    if nodetype == 'channel':

        ch = createEntity(channels, object, channelidx, "channels")
        msg = createEntity(messages, msgtext, messageidx, "messages")
        user = createEntity(users, originuser, useridx, "users")
        createRelEnt(msg.relationships, byidx, "By", user, msg)
        createRelEnt(msg.relationships, includesidx, "Includes", ch, msg)
        createRelEnt(user.relationships, mentionsidx, "Mentions", ch, user)

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
        createRelEnt(msg.relationships, byidx, "By", user, msg)
        createRelEnt(msg.relationships, includesidx, "Includes", entuser, msg)
        if entuser != user:
            createRelEnt(user.relationships, mentionsidx, "Mentions", entuser, user)

    elif nodetype == 'link':
        lnk = createEntity(links, object, linkidx, "links")
        msg = createEntity(messages, msgtext, messageidx, "messages")
        user = createEntity(users, originuser, useridx, "users")
        createRelEnt(msg.relationships, byidx, "By", user, msg)
        createRelEnt(msg.relationships, includesidx, "Includes", lnk, msg)
        createRelEnt(user.relationships, mentionsidx, "Mentions", lnk, msg)

    else:
        msg = createEntity(messages, msgtext, messageidx, "messages")
        user = createEntity(users, originuser, useridx, "users")
        createRelEnt(msg.relationships, byidx, "By", user, msg)

    return


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


if __name__ == '__main__':
    app.run(debug=True)
