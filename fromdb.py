
from neo4jrestclient.client import GraphDatabase
import os
from neo4jrestclient.constants import RAW
from urlparse import urlparse
import re

from flask import jsonify, request, Blueprint

from_api = Blueprint('from_api', __name__)
gdb = GraphDatabase(os.environ.get("GRAPHENEDB_URL"))


@from_api.route('/api/getexploredata', methods=['GET', 'POST'])
def getexploredata():
    nodequery = "MATCH (nodes)-[r]-> (user:User {value:" + request.data + "}) RETURN nodes"
    nodeoriginquery = "MATCH (nodes)-[r]-> (user:User {value:" + request.data + "}) RETURN user"
    relquery = "MATCH (nodes)-[r]-> (user:User {value:" + request.data + "}) RETURN r "
    # relquery = "start n=node(*) MATCH (
    # result = gdb.query(q=query,data_contents=True)
    print("Got explorer data", request.data, nodequery, nodeoriginquery, relquery)
    # print(nodequery)
    # print("DIR", dir(result))
    # print result.graph
    # graph = result.graph
    nodes = getNodes(gdb, nodequery)
    start = getNodes(gdb, nodeoriginquery)
    rels = getRels(gdb, relquery)

    finalnodes = []
    finalrels = []

    for node in nodes:
        if node not in finalnodes:
            finalnodes.append(node)

    for rel in rels:
        if rel not in finalnodes:
            finalrels.append(rel)

    # for node in start:
    #     if node not in finalnodes:
    #
    finalnodes.append(start[0])

    result = {
        'nodes': finalnodes,
        'rels': finalrels
    }

    # result = json.dumps(result)
    #
    # # GET Request Response
    # callbackWrapper = callbackArguments + "(" + result + ")"
    # resp = Response(callbackWrapper, status=200, mimetype='application/json')



    # return jsonify({"list": "channels"})
    return jsonify(result)


def createNodeJSON(value, uid):
    JSONObject = {
        'id': uid,
        'value': value,
        'caption': value
    }
    return JSONObject


def createRelsJSON(startNode, endNode, value,uid):
    JSONObject = {
        'source': int(startNode),
        'target': int(endNode),
        'caption': value,
        'id': uid
    }
    return JSONObject


def doRegEX(urlString):
    regex = re.compile("([^/]*)$")
    stripedURLComponent = regex.search(urlString.path)
    return stripedURLComponent.group(0)


def getNodes(db, query):
    # q = "START n=node(*) RETURN n"
    q = query
    params = {}
    querySquenceObject = db.query(q, params=params, returns=RAW)
    print "NODES"
    qgraph = querySquenceObject.graph
    print qgraph
        # for object in qgraph:
        #     o = object.pop()
        #     print object, o

    # Blank list to hold the JSON
    nodeJSON = []

    # Iterating over the resposes from the graph db
    # NOTE:Excluding the ROOT NODE from RETURN!!!!
    for node in querySquenceObject:
        n = node.pop()
        uid =  n.get('metadata').get('id')
        data = n.get('data')
        name = data.get('name')
        description = data.get('description')
        value = data.get('value')

        self = n.get('self')
        # print self
        # self = urlparse(self)
        # uid = doRegEX(self)

        nodeJSON.append(createNodeJSON(value, uid))

    return nodeJSON


def getRels(db, query):
    # q = "START n=node(*) MATCH (n)-[r]->() RETURN r"
    q = query
    params = {}
    querySquenceObject = db.query(q, params=params, returns=RAW)
    print "RELATIONS"
    qgraph = querySquenceObject.graph
    # for object in qgraph:
    #     o = object.pop()
    #     print object, o

    # Blank list to hold the JSON
    relsJSON = []

    for rel in querySquenceObject:
        r = rel.pop()
        uid =  r.get('metadata').get('id')
        start = r.get('start')
        end = r.get('end')
        value = r.get('type')
        # print(start, end, value )

        start = urlparse(start)
        end = urlparse(end)

        startNode = doRegEX(start)
        endNode = doRegEX(end)

        self = r.get('self')
        # print self
        self = urlparse(self)
        # uid = doRegEX(self)

        relsJSON.append(createRelsJSON(startNode, endNode, value, uid))

    return relsJSON