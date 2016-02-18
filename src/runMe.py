import sys
import csv
from filterByField import filterfields
import helper as hlp
from graphing import creategraph as graph
import datetime as dt

def writetofile(filepath, data):
    print 'writing: ', filepath
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
    pid_dict = hlp.getuniqueparticipants(data)
    graph_obj = graph(is_directed=True)
    if isStatic:
        links, link_tuple = hlp.getlinks(pid_dict, data)
        graph_obj.addnodes(pid_dict['participant'].values(), 'P')
        graph_obj.addnodes(pid_dict['phone'].values(), 'NP')
        graph_obj.addedges(link_tuple)
        return links, link_tuple, graph_obj
    else:
        start_datetime = dt.datetime.strptime('', '%Y-%m-%d %H:%M:%S')
        week_dict, link_tuple = hlp.getdynamiclinks(pid_dict, data, start_datetime)
        toWrite_edge, toWrite_node = graph_obj.exportdynamicgraph(link_tuple, pid_dict)
        return toWrite_edge, toWrite_node, week_dict

def main():
    ff = filterfields(sys.argv[1])
    print 'filtering...'
    sms_data = ff.filterbyequality(1, 'sms')
    print 'done'
    if '~' is not sys.argv[2]:
        writecsv(sys.argv[2], sms_data)
    if '~' is not sys.argv[3]:
        links, link_tuple, graph_obj = creategraph(sms_data)
        graph_obj.writegraph(sys.argv[3])
    if '~' is not sys.argv[4]:
        toWrite_edge, toWrite_node, week_dict = creategraph(sms_data, False)
        writetofile(sys.argv[4]+'_el.csv', toWrite_edge)
        writetofile(sys.argv[4]+'_nl.csv', toWrite_node)

if __name__ == "__main__":
    if not (5 == len(sys.argv)):
        print 'Usage: python runMe.py <csv filename> <path for output filtered file, enter ~ for skipping> ' \
              '<path for graph file, enter ~ for skipping> <path for dynamic graph, enter ~ for skipping>'
    else:
        main()
