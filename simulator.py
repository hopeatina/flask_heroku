
import networkx as nx
from neo4jrestclient.client import GraphDatabase
import os
from neo4jrestclient.constants import RAW
from urlparse import urlparse
from py2neo import Graph
import re
from pandas import DataFrame
import matplotlib.pyplot as plt
import random

from flask import jsonify, request, Blueprint

simulator = Blueprint('simulator', __name__)
# gdb = GraphDatabase(os.environ.get("GRAPHENEDB_URL"))
py2neograph = Graph(os.environ.get("GRAPHENEDB_URL"))

# main function
### Input Parameters:
### repeat = # of iterations/days
### alpha = growth rate of group, added members per day
###

@simulator.route('/api/runModel', methods=['GET', 'POST'])
def main(repeat, alpha):

    graphq = " MATCH (x:User)-[*..2]-(y:User) RETURN id(x) as id, COLLECT(id(y)) as rels, count(y) as endcount LIMIT 20"
    tagsq = " MATCH (x:User)-[*..2]-(y:Tag) RETURN id(x) as id, COLLECT(id(y)) as rels, count(y) as endcount LIMIT 5"
    # tagsq = " MATCH (x:User)-[*..2]-(y:User) RETURN id(x) as id, COLLECT(id(y)) as rels, count(y) as endcount LIMIT 5"
    nodecountq = "MATCH (x) RETURN count(x) as count LIMIT 1"

    seqGraphObj, startCount = getNodesFromDB(graphq, nodecountq)
    tagGraphObj, yserCount = getNodesFromDB(tagsq, nodecountq)
    procNodes = processNodes(seqGraphObj)
    procTags = processNodes(tagGraphObj)

    print "procNodes", procNodes, "startcount: ", startCount[0]
    g = nx.Graph(procNodes)
    while repeat > 0:
        updatedGraph = updateStats(procNodes)
        graphStats = updateGraphStats(updatedGraph)
        matches = suggestMatches(updatedGraph, graphStats)
        action = determineUtility(matches)
        updatedGraph, reward = takeAction(action, updatedGraph, alpha)
        repeat -= 1

    print updatedGraph.order(), updatedGraph.size(), updatedGraph.nodes(data=True)
    print graphStats
    nx.draw(updatedGraph)
    plt.show()

    return []

def removeDupes(list):
    newlist = []
    for item in list:
        if item not in newlist:
            newlist.append(item)

    return newlist
# Get all nodes
def getNodesFromDB(graphq,nodecount):
    # graphq = " MATCH (m:Message)-[]-(x:User)-[*..3]-(y:User) RETURN id(x),COLLECT(id(y)), COUNT(m) LIMIT 5"
    seqGraphObj = py2neograph.run(graphq).data()
    startCount = py2neograph.run(nodecount).data()
    return seqGraphObj, startCount

# turn it into graph matrix
def processNodes(nodes):
    redata = {}
    start = 0
    for key, node in enumerate(nodes):
        # redata[node['id']] = removeDupes(node['rels'])
        redata[node['id']] = removeDupes(node['rels'])
        start += 1

    return redata



def updateStats(nodes):
    # for each node update it's stats
    graph = nx.Graph(nodes)
    centralities = nx.degree_centrality(graph)
    betweenness = nx.betweenness_centrality(graph)
    eigenvectors = nx.eigenvector_centrality(graph)
    closenesscentrality = nx.closeness_centrality(graph)
    print centralities
    for key, node in enumerate(graph.nodes()):
        print key, node
        graph.node[node]['stats'] = {
            "msg/day": key, "centrality": centralities[node],
            "betweeness": betweenness[node],
            "closeness": closenesscentrality[node],
            "eigenvector": eigenvectors[node]}
        # graph.node[node['id']]
        # Tags,
    return graph

# update the networknx.degree_centrality(g) stats
def updateGraphStats(graph):
    radius = 0
    diameter = 0
    center = []
    if nx.is_connected(graph):
        radius = nx.radius(graph)
        diameter = nx.diameter(graph)
        center = nx.center(graph)
    else:
        connectedcomp = nx.connected_components(graph)

    stats = {
        "radius": radius,
        "diameter": diameter,
        "center": center,
        "avgcluscoeff": nx.average_clustering(graph),
        "nodeconnectivity": nx.node_connectivity(graph)
    }

    return stats

# Recommend top 5
### identify biggest network holes
### identify most similar among the network hole matches
### score matches based on combined hole + tags + links/channel mentions + stats
def suggestMatches(graph, graphstats):
    nodes = graph.nodes()
    suggs = []
    count = 5
    while count > 0:
        a =random.choice(nodes)
        b = random.choice(nodes)
        while b == a:
            b = random.choice(nodes)
        suggs.append((a, b))
    return suggs

# Select match based on utility function
def determineUtility(matches):
    options = [
        ["remove", random.choice(matches)],
        ["add", random.choice(matches)],
        ["nothing", random.choice(matches)]
    ]
    matches = random.choice(options)
    return matches

# Complete action
### Update graph matrix
### Add more members according to growth rate
### Increase node messages/connections
### Assign reward
def takeAction(action, graph, alpha):
    reward = 0
    if action[0] == "remove":
        graph.remove_node(action[1])
        reward = -10
    if action[0] == "add":
        graph.add_edge(action[1])
        reward = +5
    if action[0] == "nothing":
        reward = -2

    return graph, reward


# Add metrics to timeseries metric array

#Create Node Classes
### Type 1 - cooperativity (0-1), connectivity: .25

class User:
    def __init__(self):
        self.stats = []
        self.connections = []


main(1, 2)

