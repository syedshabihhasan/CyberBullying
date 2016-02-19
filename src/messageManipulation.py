import sys
from filterByField import filterfields
from basicInfo import privateInfo as pr
import csv


def writecsv(filename, data):
    f = open(filename, 'w')
    csv_obj = csv.writer(f, delimiter=',')
    print 'writing...'
    csv_obj.writerows(data)
    print 'done'
    f.close()

def getmessages(kwd, filepath, f_idx):
    ff = filterfields(filepath)
    return ff.filterbyequality(f_idx, kwd)


def createpiddict(filepath):
    pid_dict = {}
    data =[]
    f = open(filepath, 'r')
    csv_obj = csv.reader(f, delimiter = ',')
    for row in csv_obj:
        data.append(row)
    f.close()
    for line in data:
        pid_dict[line[0]] = line[1]
    return pid_dict


def getpidinfo(pid, filepath):
    pid_dict = createpiddict(filepath)
    return pid_dict[pid]


if __name__ == "__main__":
    if not(6 == len(sys.argv)):
        print 'Usage: python messageManipulation.py <path to pid_dict> <path to data> ' \
              '<enter value to work with> <enter kwd <pinfo, source, target, mtype, stype, ttype>>' \
              '<path to store messages, enter - to for skipping> '
    else:
        if 'pinfo' == sys.argv[4]:
            print getpidinfo(sys.argv[3], sys.argv[1])
        else:
            filter_idx = pr.kwd_dict[sys.argv[4]]
            filtered_data = getmessages(getpidinfo(sys.argv[3], sys.argv[1]), sys.argv[2], filter_idx)
            if '-' is not sys.argv[5]:
                writecsv(sys.argv[5], filtered_data)