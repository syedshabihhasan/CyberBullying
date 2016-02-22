import sys
import helper as hlp

from graphing import creategraph
from basicInfo import privateInfo as pr

def getnodesedges(link_dict):
    link_tuple = []
    nodes = set()
    for sd_tuple in link_dict.keys():
        link_tuple.append((sd_tuple[0], sd_tuple[1], {'weight': link_dict[sd_tuple]}))
        nodes.add(sd_tuple[0])
        nodes.add(sd_tuple[1])
    return list(nodes), link_tuple

def checknodemembership(node_list, participant_list, non_participant_list):
    p_list = []
    np_list = []
    for node in node_list:
        if node in participant_list:
            p_list.append(node)
        elif node in non_participant_list:
            np_list.append(node)
    return p_list, np_list

def weekgraphs(week_dict, participant_list, non_participant_list):
    graph_objs = {}
    for week_no in week_dict.keys():
        print 'week no', week_no
        graph_obj = creategraph(True)
        nodes, link_tuple = getnodesedges(week_dict[week_no])
        p_nodes, np_nodes = checknodemembership(nodes, participant_list, non_participant_list)
        graph_obj.addnodes(p_nodes, 'P')
        graph_obj.addnodes(np_nodes, 'NP')
        graph_obj.addedges(link_tuple)
        print 'Calculating properties'
        toStore = {'object': graph_obj.getgraphobject(),
                   'triadic_census': graph_obj.gettriadiccensus(),
                   'closeness': graph_obj.getclosenesscentrality()}
        graph_objs[week_no] = toStore
    return graph_objs

def main():
    messages = hlp.recovervariable(sys.argv[1])
    pid_dict = hlp.recovervariable(sys.argv[2])
    week_dict = hlp.recovervariable(sys.argv[3])
    m_type = sys.argv[4]
    participants = pid_dict[pr.participant[m_type]]
    non_participants = pid_dict[pr.nparticipant[m_type]]
    graph_objs = weekgraphs(week_dict, participants, non_participants)
    hlp.dumpvariable(graph_objs, 'week_graph_objs')

if __name__ == "__main__":
    if not(5 == len(sys.argv)):
        print 'Usage: python perweekanalysis.py <path to message obj> <path to pid dict obj> ' \
              '<path to week by week dict obj> <message type, currently only supports sms>'
    else:
        main()