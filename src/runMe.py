import sys
import csv
from filterByField import filterfields
import helper as hlp
from graphing import creategraph as graph
import datetime as dt
from basicInfo import privateInfo as pr

def writetofile(filepath, data, isDict = False):
    print 'writing: ', filepath
    if isDict:
        toWrite = ''
        for key in data.keys():
            toWrite += str(data[key]) + ',' + str(key) + '\n'
        data = toWrite
    with open(filepath, 'w') as f:
        f.write(data)
    print 'done'

def writecsv(filename, data):
    f = open(filename, 'w')
    csv_obj = csv.writer(f, delimiter=',')
    print 'writing...'
    csv_obj.writerows(data)
    print 'done'
    f.close()

def creategraph(data, isStatic = True):
    pid_dict = hlp.getuniqueparticipants(data, sys.argv[6])
    graph_obj = graph(is_directed=True)
    if isStatic:
        links, link_tuple = hlp.getlinks(pid_dict, data)
        graph_obj.addnodes(pid_dict['participant'].values(), 'P')
        graph_obj.addnodes(pid_dict['phone'].values(), 'NP')
        graph_obj.addedges(link_tuple)
        return links, link_tuple, graph_obj
    else:
        start_datetime = dt.datetime.strptime(pr.start_datetime, '%Y-%m-%d %H:%M:%S')
        week_dict, link_tuple = hlp.getdynamiclinks(pid_dict, data, start_datetime)
        to_write_edge, to_write_node = graph_obj.exportdynamicgraph(link_tuple, pid_dict)
        return to_write_edge, to_write_node, week_dict

def main():
    ff = filterfields(sys.argv[1])
    print 'filtering...'
    filtered_data = ff.filterbyequality(pr.m_type, sys.argv[6])
    print 'done'
    if '-' is not sys.argv[2]:
        writecsv(sys.argv[2], filtered_data)
    if '-' is not sys.argv[3]:
        links, link_tuple, graph_obj = creategraph(filtered_data)
        graph_obj.writegraph(sys.argv[3])
    if '-' is not sys.argv[4]:
        to_write_edge, to_write_nodes, week_dict = creategraph(filtered_data, False)
        writetofile(sys.argv[4]+'_el.csv', to_write_edge)
        writetofile(sys.argv[4]+'_nl.csv', to_write_nodes)
    if '-' is not sys.argv[5]:
        pid_dict = hlp.getuniqueparticipants(filtered_data, sys.argv[6])
        complete_dict = pid_dict['participant']
        complete_dict.update(pid_dict['phone'])
        writetofile(sys.argv[5], complete_dict, True)

if __name__ == "__main__":
    if not (7 == len(sys.argv)):
        print 'Usage: python runMe.py <csv filename> <path for output filtered file, enter - for skipping> ' \
              '<path for graph file, enter - for skipping> <path for dynamic graph, enter - for skipping> ' \
              '<path for the pid_dict, enter - for skipping> <message type to filter, currently supported: sms>'
    else:
        main()
