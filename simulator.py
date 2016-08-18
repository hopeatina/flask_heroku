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
from datetime import datetime
import pandas as pd

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
class GraphingAgent():
    def __init__(self, random=True):
        self.intitsomething = []
        self.orig_gamma = .5
        self.orig_alpha = .75
        self.gamma, self.alpha = self.orig_gamma, self.orig_alpha
        self.orig_q_value = 3
        self.allactions = {"connect", "removenode", "disconnect"}
        self.states = []
        self.state = None
        self.info = []
        self.q = dict()
        self.orig_epsilon = .1
        self.epsilon = self.orig_epsilon
        self.old_graph_Stats, self.old_state, self.old_action, self.old_reward = None, None, None, 0
        self.saveGraphStats = {
            "iter": [],
            "radius": [],
            "density": [],
            "avgcluscoeff": [],
            "nodeconnectivity": [],
            "components": [],
            "avgpathlength": [],
            "reward": [],
            "nodecount": []
        }
        self.random = random

    def main(self, repeat, growrate, matchrate):
        # repeat = number of times to iterate throuhg // the number of days a moderator would work through
        # growrate = number of users added per day
        # matchrate = number of matches to consider
        # epsilon - used in the q value function
        # gamma = used in q value function

        # tagGraphObj, yserCount = getNodesFromDB(tagsq, nodecountq)
        # procTags = processNodes(tagGraphObj)
        # tagsq = " MATCH (x:User)-[*..2]-(y:Tag) RETURN id(x) as id, COLLECT(id(y)) as rels, count(y) as endcount LIMIT 5"
        # tagsq = " MATCH (x:User)-[*..2]-(y:User) RETURN id(x) as id, COLLECT(id(y)) as rels, count(y) as endcount LIMIT 5"
        # This is for the comparison data to current DB state
        graphq = " MATCH (x:User)-[*..2]-(y:User) MATCH (m:Message)-[]-(x:User) RETURN id(x) as id, COLLECT(id(y)) as rels, count(y) as endcount, count(m) as mcount LIMIT 20"
        nodecountq = "MATCH (x) RETURN count(x) as count LIMIT 1"

        seqGraphObj, startCount = self.getNodesFromDB(graphq, nodecountq)
        processFromDB, nodestatsDB = self.processNodes(seqGraphObj)
        fromDBgraphstats = self.updateGraphStats(nx.Graph(processFromDB))

        dBStats = {
            "nodeStats": nodestatsDB,
            "graphStats": fromDBgraphstats
        }
        dbGraph = nx.Graph(processFromDB)
        print len(dbGraph.nodes()), nodestatsDB
        x = pd.DataFrame(dBStats)
        x.to_csv("intialnodedata.csv")
        x.to_json("initialdatajson.json")

        # nx.draw(dbGraph, with_labels=True, font_color='w')
        # plt.show()

        # Generate perfect starting seed community of 5 people
        procNodes = {
            0: [1, 2, 3, 4],
            1: [2, 3, 4, 0],
            2: [3, 4, 0, 1],
            3: [4, 0, 1, 2],
            4: [0, 1, 2, 3]
        }
        startnodenum = len(procNodes)
        origin = repeat

        # Interactive graphing
        plt.ion()

        # TODO: Initialize variables
        counter = 0

        # for state in states:
        #     for action in self.allactions:
        #         transition = (state, action)
        #         a = random.uniform(0, 1)
        #         b = random.uniform(0, a)
        #         c = 1 - a - b
        #         probs = [a, b, c]
        #         transitionProb[transition] =[]
        #         rewards[transition] =[]
        #         for key, restate in enumerate(states):
        #             transitionProb[transition].append({restate: probs[key]})
        #             rewards[transition].append({restate: probs[key] * 5})
        #
        # print "super", transitionProb, rewards

        savestring = "Figures/"
        time = datetime.now().strftime("%Y-%m-%d%H.%M")
        updatedGraph = None

        while repeat > 0:
            print "# of states", len(self.states), "Q: ", len(self.q), self.q
            # TODO: GET INPUTS, graphStats, matches
            if repeat == origin:
                updatedGraph = self.updateStats(procNodes, [])
            else:
                updatedGraph = self.updateStats([], updatedGraph)

            graphStats = self.updateGraphStats(updatedGraph)
            updatedGraph, newnodes = self.addandConnect(updatedGraph,startnodenum,growrate)

            matches, newmatches = self.suggestMatches(updatedGraph, graphStats, matchrate, newnodes)

            # TODO: UPDATE STATE
            graphStats = self.normalizeStats(graphStats)
            temp = graphStats
            if self.old_graph_Stats != None:
                for attribute in graphStats:
                    print "compare", graphStats[attribute],self.old_graph_Stats[attribute]
                    if graphStats[attribute] > self.old_graph_Stats[attribute]:
                        graphStats[attribute] = 1
                    if graphStats[attribute] < self.old_graph_Stats[attribute]:
                        graphStats[attribute] = -1
                    if graphStats[attribute] == self.old_graph_Stats[attribute]:
                        graphStats[attribute] = 0
                self.state = (graphStats)
            else:
                for attribute in graphStats:
                    graphStats[attribute] = 0
                self.state =(graphStats)

            if self.state not in self.states and self.state != None:
                self.states.append(self.state)
                index = self.states.index(self.state)
                self.q[index] = dict({
                    None: self.orig_q_value,
                    "connect": self.orig_q_value,
                    "disconnect": self.orig_q_value,
                    "removenode": self.orig_q_value})

            print "HERE:", self.q, self.state, self.states
            if counter > 0:
                self.update_q(self.old_state, self.old_action, self.old_reward, self.state)
            else:
                # print trialnumber
                self.info.append({'penalty': [], 'reward': [], 'net reward': []})

            # TODO: Select action according to policy
            action = self.determineUtility(matches, self.state)

            # TODO: Execute action and get reward
            updatedGraph, reward = self.takeAction(action, updatedGraph, growrate, newmatches)

            # TODO: Learn policy based on state, action, and reward.

            # Growth rate is applied

            self.old_graph_Stats = temp
            for key, index in enumerate(self.saveGraphStats):
                if index != 'iter' and index != 'reward':
                    self.saveGraphStats[index].append(self.old_graph_Stats[index])
            self.saveGraphStats['iter'].append(counter)
            self.saveGraphStats['reward'].append(reward)

            self.old_reward = reward
            self.old_action = action
            self.old_state = self.state

            startnodenum += growrate
            repeat -= 1
            counter += 1

            print len(updatedGraph.nodes()), counter, repeat
            # Plot and stuff and save it to the file for gif creation later --- UNDO BELOW
            nx.draw(updatedGraph, with_labels=True, font_color='w')
            plt.show()
            # pop = savestring + time + str(origin - repeat) + ".png"
            # plt.savefig(pop)
            plt.pause(.5)
            plt.clf()            # Plot and stuff and save it to the file for gif creation later --- UNDO BELOW
            # nx.draw(updatedGraph, with_labels=True, font_color='w')
            # plt.show()
            # # pop = savestring + time + str(origin - repeat) + ".png"
            # # plt.savefig(pop)
            # plt.pause(1)
            # plt.clf()

        print self.saveGraphStats
        plt.figure(1)
        ax = plt.subplot(321)
        ax.set_title("Avg Path Length")
        ax.plot(self.saveGraphStats['iter'], self.saveGraphStats['avgpathlength'], 'ro')
        ax = plt.subplot(322)
        ax.set_title("Avg Clus Coeff")
        ax.plot(self.saveGraphStats['iter'], self.saveGraphStats['avgcluscoeff'], 'go')
        ax = plt.subplot(323)
        ax.set_title("Reward")
        ax.plot(self.saveGraphStats['iter'], self.saveGraphStats['reward'], 'bo')
        ax = plt.subplot(324)
        ax.set_title("Clustering Components")
        ax.plot(self.saveGraphStats['iter'], self.saveGraphStats['components'], 'yo')
        ax = plt.subplot(325)
        ax.set_title("Centrality")
        print "END GRAPH: ", [i for i in range(len(updatedGraph.nodes()))],
        centralrray = []
        boom = nx.get_node_attributes(updatedGraph, 'stats')
        for x in boom:
            centralrray.append(boom[x]['centrality'])
        #     print x, boom[x]
        # print "centrallry: ", centralrray
        ax.plot([i for i in range(len(centralrray))], centralrray, 'mo')
        ax = plt.subplot(326)
        title = "Number of Nodes +" + str(growrate)
        ax.set_title(title)
        ax.plot(self.saveGraphStats['iter'], self.saveGraphStats['nodecount'], 'co')
        plt.show()

        while True:
            plt.pause(0.05)
        #
        # print updatedGraph.order(), updatedGraph.size(), updatedGraph.nodes(data=True)
        # print graphStats

        return []

    def addandConnect(self, graph, startnum, growrate):
        addednodes = []
        for i in range(startnum, startnum + growrate):
            graph.add_node(i)
            addednodes.append(i)

        return graph, addednodes

    def normalizeStats(self, graphStats):

        return graphStats

    def removeDupes(self, list):
        newlist = []
        for item in list:
            if item not in newlist:
                newlist.append(item)

        return newlist

    # Get all nodes
    def getNodesFromDB(self, graphq, nodecount):
        # graphq = " MATCH (m:Message)-[]-(x:User)-[*..3]-(y:User) RETURN id(x),COLLECT(id(y)), COUNT(m) LIMIT 5"
        seqGraphObj = py2neograph.run(graphq).data()
        startCount = py2neograph.run(nodecount).data()
        return seqGraphObj, startCount

    # turn it into graph matrix
    def processNodes(self, nodes):
        redata = {}
        start = 0
        stats = {}

        for key, node in enumerate(nodes):
            # print key,node
            # redata[node['id']] = removeDupes(node['rels'])
            redata[node['id']] = self.removeDupes(node['rels'])
            stats[node['id']] = {
                "relcount": len(node['rels']),
                "msgcount": node['mcount'],
                "endcount": node['endcount']
            }
            start += 1

        return redata, stats

    def updateStats(self, firstnodes, oldgraph):
        # for each node update it's stats
        if firstnodes != []:
            graph = nx.Graph(firstnodes)
        else:
            graph = oldgraph
        centralities = nx.degree_centrality(graph)
        betweenness = nx.betweenness_centrality(graph)
        eigenvectors = nx.eigenvector_centrality(graph)
        closenesscentrality = nx.closeness_centrality(graph)
        # print "centralities", centralities
        for key, node in enumerate(graph.nodes()):
            graph.node[node]['stats'] = {
                "msg/day": key, "centrality": centralities[node],
                "betweeness": betweenness[node],
                "closeness": closenesscentrality[node],
                "eigenvector": eigenvectors[node]}
            # graph.node[node['id']]
            # Tags,
        return graph

    # update the networknx.degree_centrality(g) stats

    def updateGraphStats(self, graph):

        origgraph = graph
        if nx.is_connected(graph):
            random = 0
        else:
            connectedcomp = nx.connected_component_subgraphs(graph)
            graph = max(connectedcomp)

        if len(graph) > 1:
            pathlength = nx.average_shortest_path_length(graph)
        else:
            pathlength = 0

        print graph.nodes(), len(graph), nx.is_connected(graph), graph

        stats = {
            "radius": nx.radius(graph),
            "density": nx.density(graph),
            "nodecount": len(origgraph.nodes()),
            "center": nx.center(graph),
            "avgcluscoeff": nx.average_clustering(graph),
            "nodeconnectivity": nx.node_connectivity(graph),
            "components": nx.number_connected_components(graph),
            "avgpathlength": pathlength
        }

        print "updated graph stats", stats
        return stats

    def update_q(self, oldstate, actionlist, reward, newstate):
        qMax = self.maxqs(newstate)
        oldindex = self.states.index(oldstate)

        for action in actionlist:
            action = action[0]
            print "in updateq", self.q[oldindex][action], action
            if oldstate in self.states and self.q[oldindex][action] is not None:
                self.q[oldindex][action] += self.alpha * (reward + self.gamma * qMax - self.q[oldindex][action])
            else:
                self.states.append(oldstate)
                self.q[oldindex][action] = reward

    def maxqs(self, state):

        if state in self.states:
            index = self.states.index(state)
            qmax = max(self.q[index].values())
        else:
            qmax = self.orig_q_value
            # print "in maxqs", qmax, states, state, state in states

        return qmax

    # Recommend top 5
    ### identify biggest network holes
    ### identify most similar among the network hole matches
    ### score matches based on combined hole + tags + links/channel mentions + stats
    def suggestMatches(self, graph, graphstats, matchrate, newnodes):
        nodes = graph.nodes()

        suggs = []
        newsuggs = []
        for node in newnodes:
            friend = node
            if len(nodes) > 1:
                while friend == node:
                    friend = random.sample(nodes, 1)
                newsuggs.append(("connect", (node,friend[0]))) # DOING THE MOST RIGHT HERE

        while matchrate > 0:
            a = random.sample(nodes, 1)
            b = random.sample(nodes, 1)

            if b == a:
                b = random.sample(nodes, 1)
            suggs.append((a[0], b[0]))
            matchrate -= 1

        print "suggested matches", suggs, len(nodes)
        return suggs, newsuggs

    # Select match based on utility function
    def determineUtility(self, matches, state):
        actionpairs = []
        allactions = self.allactions

        if state in self.states and random.random() > self.epsilon:
            stateindex = self.states.index(state)


            allactions = [action for action, q in self.q[stateindex].iteritems()
                          if q == max(self.q[stateindex].values())]
            print "chose action", stateindex, self.q, self.q[stateindex], max(self.q[stateindex].values()), allactions

            for action, q in self.q[stateindex].iteritems():
                print action, q
        for match in matches:
            action = random.sample(allactions, 1)
            actionpairs.append((action[0], match))

        print "utility determined, action + match: ", actionpairs
        return actionpairs

    # Complete action
    ### Update graph matrix
    ### Add more members according to growth rate
    ### Increase node messages/connections
    ### Assign reward
    def takeAction(self, actionpairs, graph, growthrate, specpairs):
        reward = 0

        actionpairs = actionpairs + specpairs
        print actionpairs, "WHOO", specpairs

        for action in actionpairs:
            if action[0] == "removenode":
                chose = random.sample(action[1], 1)
                if graph.has_node(chose):
                    graph.remove_node(chose)
                reward += -10
            if action[0] == "connect":
                graph.add_edge(action[1][0], action[1][1])
                reward += +10
            if action[0] == "disconnect":
                if graph.has_edge(action[1][0], action[1][1]):
                    graph.remove_edge(action[1][0], action[1][1])
                    reward += -4
            if action[0] == None:
                reward += -1
        reward = reward - len(specpairs)*10

        print "took actions", reward
        return graph, reward


class User():
    def __init__(self, id):
        self.id = id
        self.tags = self.selectTags([1, 2, 3,4,5,6,7,8,9,10])
        self.msgrate = random.random()

    def selectTags(self, tagslist):

        selectedTags = random.sample(tagslist, 1)

        return selectedTags

def experiment():
    repeatrange = (1, 90, 10)
    growraterange = (1,10,1)
    matchraterange = (1,10,1)

theAgent = GraphingAgent(random=False)
# repeat, growrate, matchrate
theAgent.main(10, 2, 3)
