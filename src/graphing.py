import networkx as nx

class creategraph:
    G = None

    def getaverageCC(self):
        return nx.average_clustering(self.G)

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