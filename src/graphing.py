import networkx as nx
import matplotlib.pyplot as plt

class creategraph:
    G = None
    is_directed = False

    def drawgraph(self):
        nx.draw(self.G)
        plt.show()

    def getdegrees(self, node_id):
        return [self.G.in_degree(node_id), self.G.out_degree(node_id)] \
            if self.is_directed \
            else self.G.degree(node_id)

    def getedgeweights(self, node_id):
        return [self.G.in_edges(node_id, data=True), self.G.out_edges(node_id, data=True)] \
        if self.is_directed \
        else self.G.edges(node_id, data=True)

    def getclosenesscentrality(self):
        closeness_centrality = {'in': {}, 'out': {}} if self.is_directed else {}
        if self.is_directed:
            closeness_centrality['in'] = nx.in_degree_centrality(self.G)
            closeness_centrality['out'] = nx.out_degree_centrality(self.G)
        else:
            closeness_centrality = nx.degree_centrality(self.G)
        return closeness_centrality

    def gettriadiccensus(self):
        return nx.triadic_census(self.G)

    def writegraph(self, filepath):
        print 'writing graph...'
        nx.write_gexf(self.G, filepath)
        print 'written'

    def addnodes(self, node_list, nodetype):
        print 'adding nodes...'
        self.G.add_nodes_from(node_list, ntype = nodetype)
        print 'added'

    def addedges(self, links):
        print 'adding edges...'
        self.G.add_edges_from(links)
        print 'added'

    def exportdynamicgraph(self, edge_list, node_dict):
        toWrite_edge = 'Source;Target;Type;Weight;Start;End;Id\n'
        for datum in edge_list:
            toWrite_edge += datum + '\n'
        toWrite_node = 'Id;nType\n'
        for prt in node_dict['participant'].values():
            toWrite_node += str(prt) + ';P\n'
        for nprt in node_dict['phone'].values():
            toWrite_node += str(nprt) + ';NP\n'
        return toWrite_edge, toWrite_node

    def getgraphobject(self):
        return self.G

    def __init__(self, is_directed = False):
        self.G = nx.DiGraph() if is_directed else nx.Graph()
        self.is_directed = is_directed