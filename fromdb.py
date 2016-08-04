
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
    result = {}
    print "REQUEST DATA", str(request.data[1:4]), "All"
    if str(request.data[1:4]) == "All":
        result = getAllNodes()
    else:
        result = getIndividualNR()

    # result = json.dumps(result)
    #
    # # GET Request Response
    # callbackWrapper = callbackArguments + "(" + result + ")"
    # resp = Response(callbackWrapper, status=200, mimetype='application/json')


    print "sent the results", result
    # return jsonify({"list": "channels"})
    return jsonify(result)


def getAllNodes():
    nodeq = "MATCH (nodes) RETURN nodes"
    relq = "MATCH () -[rel]-() RETURN rel"

    nodes = getNodes(gdb, nodeq)
    rels = getRels(gdb, relq)

    finalnodes = []
    finalrels = []
    for node in nodes:
        if node not in finalnodes:
            finalnodes.append(node)

    for rel in rels:
        if rel not in finalrels:
            finalrels.append(rel)

    result = {
        'nodes': finalnodes,
        'rels': finalrels
    }
    print "getting all nodes"

    return result


def getIndividualNR():
    nodequery = "MATCH (fof)-[r2]-(nodes)-[r]- (user:User {value:" + request.data + "}) RETURN nodes"
    fofquery = "MATCH (fof)-[r2]-(nodes)-[r]- (user:User {value:" + request.data + "}) RETURN fof"
    nodeoriginquery = "MATCH (user:User {value:" + request.data + "}) RETURN user"
    relquery = "MATCH (nodes)-[r]- (user:User {value:" + request.data + "}) RETURN r"
    rel2query = "MATCH (fof)-[r2]-(nodes)-[r]- (user:User {value:" + request.data + "}) RETURN r2"
    # nodequery = "MATCH (nodes)-[r]- (user:User {value:" + request.data + "}) RETURN nodes"
    # nodeoriginquery = "MATCH (nodes)-[r]- (user:User {value:" + request.data + "}) RETURN user"
    # relquery = "MATCH (nodes)-[r]- (user:User {value:" + request.data + "}) RETURN r"
    # relquery = "MATCH (fof)-[r2]-(nodes)-[r]- (user:User {value:" + request.data + "}) RETURN r, r2 "
    # relquery = "start n=node(*) MATCH (
    # result = gdb.query(q=query,data_contents=True)
    print("Got explorer data", request.data, nodequery, nodeoriginquery, relquery)
    # print(nodequery)
    # print("DIR", dir(result))
    # print result.graph
    # graph = result.graph
    nodes = getNodes(gdb, nodequery)
    fof = getNodes(gdb, fofquery)
    start = getNodes(gdb, nodeoriginquery)
    rels = getRels(gdb, relquery)
    rels2 = getRels(gdb, rel2query)

    finalnodes = []
    finalrels = []

    # print "START: " + str(start)
    # print "NODES: " + str(nodes)
    # print "RELS: " + str(rels)
    for node in nodes:
        if node not in finalnodes:
            finalnodes.append(node)
    for node in fof:
        if node not in finalnodes:
            finalnodes.append(node)

    for rel in rels:
        if rel not in finalrels:
            finalrels.append(rel)
    for rel in rels2:
        if rel not in finalrels:
            finalrels.append(rel)

    # for node in start:
    #     if node not in finalnodes:
    #
    if start != []:
        for x in start:
            if x not in finalnodes:
                finalnodes.append(x)

    result = {
        'nodes': finalnodes,
        'rels': finalrels
    }

    return result

def createNodeJSON(value, uid, nodetype, img, date, name):
    JSONObject = {
        'id': uid,
        'value': value,
        'caption': name,
        'type': nodetype,
        'image': img,
        'datetime': date
    }
    return JSONObject


def createRelsJSON(startNode, endNode, value,uid):
    JSONObject = {
        'source': int(startNode),
        'target': int(endNode),
        'caption': value,
        'type': value,
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
    # print "NODES"
    # qgraph = querySquenceObject.graph
    # print qgraph
        # for object in qgraph:
        #     o = object.pop()
        #     print object, o

    # Blank list to hold the JSON
    nodeJSON = []

    # Iterating over the resposes from the graph db
    # NOTE:Excluding the ROOT NODE from RETURN!!!!
    for node in querySquenceObject:
        n = node.pop()
        uid = n.get('metadata').get('id')
        data = n.get('data')
        name = data.get('name')
        description = data.get('description')
        value = data.get('value')
        nodetype = data.get('type')
        img = data.get('img')
        date = data.get('date')
        if name == None:
            name = value

        # print "FOR THE NODE GRAPH:", name, value, nodetype, img, date
        # self = urlparse(self)
        # uid = doRegEX(self)

        nodeJSON.append(createNodeJSON(value, uid, nodetype, img, date, name))

    return nodeJSON


def getRels(db, query):
    # q = "START n=node(*) MATCH (n)-[r]->() RETURN r"
    q = query
    params = {}
    querySquenceObject = db.query(q, params=params, returns=RAW)
    # print "RELATIONS"
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