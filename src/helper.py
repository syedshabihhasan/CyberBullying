import datetime as dt
import os
import pickle
import csv

from basicInfo import privateInfo as pr

def writecsv(data, filepath, delimiter_sym = ','):
    print 'writing csv'
    f = open(filepath, 'w')
    csv_obj = csv.writer(f, delimiter = delimiter_sym)
    csv_obj.writerows(data)
    f.close()
    print 'done'

def readcsv(filepath, delimiter_sym = ','):
    print 'reading csv'
    f = open(filepath, 'r')
    csv_obj = csv.reader(f, delimiter = delimiter_sym)
    data = []
    for row in csv_obj:
        data.append(row)
    f.close()
    return data

def dumpvariable(data, fname, dpath = './variables/'):
    print 'writing variable'
    if not os.path.exists(dpath):
        os.mkdir(dpath)
    pickle.dump(data, open(dpath+fname, 'wb'))
    print 'done'

def recovervariable(fname):
    print 'reading variable'
    return pickle.load(open(fname, 'rb'))

def getuniqueparticipants(data, mtype='sms'):
    pid_dict = {pr.participant[mtype]: {}, pr.nparticipant[mtype]: {}}
    pid = 1
    for datum in data:
        temp = pid_dict[datum[pr.m_source_type]]
        if datum[pr.m_source] not in temp:
            temp[datum[pr.m_source]] = pid
            pid += 1
            pid_dict[datum[pr.m_source_type]] = temp
        temp = pid_dict[datum[pr.m_target_type]]
        if datum[pr.m_target] not in temp:
            temp[datum[pr.m_target]] = pid
            pid += 1
            pid_dict[datum[pr.m_target_type]] = temp
    print 'Participant: ', len(pid_dict[pr.participant[mtype]]), 'Non: ', len(pid_dict[pr.nparticipant[mtype]])
    return pid_dict


def getpid(pid_dict, pid, label_prt = 'participant', label_nprt = 'phone'):
    '''
    prt = pid_dict[label_prt]
    nprt = pid_dict[label_nprt]
    if pid in prt:
        return prt[pid]
    else:
        return nprt[pid]
    '''
    for p_type in pid_dict.keys():
        if pid in pid_dict[p_type]:
            return pid_dict[p_type][pid]
    return None


def getlinks(pid_dict, data):
    links = {}
    for datum in data:
        src = getpid(pid_dict, datum[pr.m_source])
        dst = getpid(pid_dict, datum[pr.m_target])
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
    week_content = {}
    week_dict = {}
    for datum in data:
        src = getpid(pid_dict, datum[pr.m_source])
        dst = getpid(pid_dict, datum[pr.m_target])
        c_dt = dt.datetime.strptime(datum[pr.m_time_sent], '%Y-%m-%d %H:%M:%S')
        td = c_dt - start_datetime
        week_of_study = (td.days // 7) + 1
        if week_of_study not in week_dict:
            week_dict[week_of_study] = {}
            week_content[week_of_study] = []
        temp = week_dict[week_of_study]
        week_content[week_of_study].append(datum)
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
    return week_dict, links_tuple, week_content

def removekey(v_dict, key):
    try:
        del v_dict[key]
    except:
        print 'there was an error...'
    return v_dict