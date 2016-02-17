import sys
import csv
from filterByField import filterfields
import helper as hlp
from graphing import creategraph

def writecsv(filename, data):
    f = open(filename, 'w')
    csv_obj = csv.writer(f, delimiter=',')
    print 'writing...'
    csv_obj.writerows(data)
    print 'done'
    f.close()

def createandsavegraph(data, filepath):
    pid_dict = hlp.getuniqueparticipants(data)
    links, links_tuple = hlp.getlinks(pid_dict, data)
    graph_obj = creategraph(is_directed=True)
    graph_obj.addnodes(pid_dict['participant'].values(), 'P')
    graph_obj.addnodes(pid_dict['phone'].values(), 'NP')
    graph_obj.addedges(links_tuple)
    graph_obj.writegraph(filepath)

def main():
    ff = filterfields(sys.argv[1])
    print 'filtering...'
    sms_data = ff.filterbyequality(1, 'sms')
    print 'done'
    writecsv(sys.argv[2], sms_data)
    createandsavegraph(sms_data, sys.argv[3])

if __name__ == "__main__":
    if not (4 == len(sys.argv)):
        print 'Usage: python runMe.py <csv filename> <path for output filtered file> ' \
              '<path for graph file>'
    else:
        main()
