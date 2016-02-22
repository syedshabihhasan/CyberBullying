import datetime as dt
import os
import pickle

from basicInfo import privateInfo as pr


def dumpvariable(data, fname):
    if not os.path.exists('./variables'):
        os.mkdir('./variables')
    pickle.dump(data, open('./variables/'+fname+'.p', 'wb'))

def recovervariable(fname):
    return pickle.load(open(fname, 'rb'))

def getuniqueparticipants(data, mtype):
    pid_dict = {pr.participant[mtype]: {}, pr.nparticipant[mtype]: {}}
    pid = 1
    for datum in data:
        temp = pid_dict[datum[-2]]
        if datum[2] not in temp:
            temp[datum[2]] = pid
            pid += 1
            pid_dict[datum[-2]] = temp
        temp = pid_dict[datum[-1]]
        if datum[3] not in temp:
            temp[datum[3]] = pid
            pid += 1
            pid_dict[datum[-1]] = temp
    print 'Participant: ', len(pid_dict[pr.participant[mtype]]), 'Non: ', len(pid_dict[pr.nparticipant[mtype]])
    return pid_dict


def getpid(pid_dict, pid):
    prt = pid_dict['participant']
    nprt = pid_dict['phone']
    if pid in prt:
        return prt[pid]
    else:
        return nprt[pid]


def getlinks(pid_dict, data):
    links = {}
    for datum in data:
        src = getpid(pid_dict, datum[2])
        dst = getpid(pid_dict, datum[3])
        if (src, dst) not in links:
            links[(src, dst)] = 0
        links[(src, dst)] += 1
    links_tuple = []
    for key in links.keys():
        src = key[0]
        dst = key[1]
        wt = links[key]
        links_tuple.append((src, dst, {'weight': wt}))
    print '# unique links: ', len(links_tuple)
    return links, links_tuple


def getdynamiclinks(pid_dict, data, start_datetime):
    links_tuple = []
    week_dict = {}
    for datum in data:
        src = getpid(pid_dict, datum[2])
        dst = getpid(pid_dict, datum[3])
        c_dt = dt.datetime.strptime(datum[-3], '%Y-%m-%d %H:%M:%S')
        td = c_dt - start_datetime
        week_of_study = (td.days // 7) + 1
        if week_of_study not in week_dict:
            week_dict[week_of_study] = {}
        temp = week_dict[week_of_study]
        if (src, dst) not in temp:
            temp[(src, dst)] = 0
        temp[(src, dst)] += 1
        week_dict[week_of_study] = temp
    idx = 0
    for week_no in week_dict.keys():
        week_data = week_dict[week_no]
        for src_dst in week_data.keys():
            toWrite = str(src_dst[0]) + ';' + str(src_dst[1]) + ';Directed;' + str(week_data[src_dst]) + ';' + \
                      str(week_no - 1) + ';' + str(week_no) + ';' + str(idx)
            links_tuple.append(toWrite)
            idx += 1
    return week_dict, links_tuple
