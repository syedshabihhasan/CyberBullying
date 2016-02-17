import networkx as nx

class creategraph:
    G = None

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

    def __init__(self, is_directed = False):
        self.G = nx.DiGraph() if is_directed else nx.Graph()