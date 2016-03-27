import datetime as dt
import os
import pickle
import csv

from basicInfo import privateInfo as pr
from graphing import creategraph as graph


def writecsv(data, filepath, delimiter_sym=','):
    print 'writing csv'
    f = open(filepath, 'w')
    csv_obj = csv.writer(f, delimiter=delimiter_sym)
    csv_obj.writerows(data)
    f.close()
    print 'done'


def readcsv(filepath, delimiter_sym=','):
    print 'reading csv'
    f = open(filepath, 'r')
    csv_obj = csv.reader(f, delimiter=delimiter_sym)
    data = []
    for row in csv_obj:
        data.append(row)
    f.close()
    return data


def dumpvariable(data, fname, dpath='./variables/'):
    print 'writing variable'
    if not os.path.exists(dpath):
        os.mkdir(dpath)
    pickle.dump(data, open(dpath + fname, 'wb'))
    print 'done'


def recovervariable(fname):
    print 'reading variable'
    return pickle.load(open(fname, 'rb'))


def getuniqueparticipants(data, mtype='sms', separate_pid_npid = False):
    pid_dict = {pr.participant[mtype]: {}, pr.nparticipant[mtype]: {}} \
        if mtype != 'all' \
        else {'participant': {}, 'nonparticipant': {}}
    pid = 1 if not separate_pid_npid else [1, 1]
    p_np = -1
    for datum in data:
        #TODO: change the current to reflect the right option according to the message type in the datum
        if 'None' == datum[pr.m_source_type]:
            datum[pr.m_source_type] = 'facebook' if mtype == 'fb' else 'twitter'
        if 'None' == datum[pr.m_target_type]:
            datum[pr.m_target_type] = 'facebook' if mtype == 'fb' else 'twitter'

        if mtype == 'all':
            if datum[pr.m_source_type] in pid_dict:
                temp = pid_dict['participant']
                p_np = 0
            else:
                temp = pid_dict['nonparticipant']
                p_np = 1
        else:
            temp = pid_dict[pr.src_dst_maps[datum[pr.m_source_type]]]

        if datum[pr.m_source] not in temp:
            if not separate_pid_npid:
                temp[datum[pr.m_source]] = pid
                pid += 1
            else:
                if p_np == 0:
                    temp[datum[pr.m_source]] = 'P' + str(pid[0])
                    pid[0] += 1
                else:
                    temp[datum[pr.m_source]] = 'NP' + str(pid[1])
                    pid[1] += 1
                p_np = -1
            if mtype == 'all':
                if datum[pr.m_source_type] in pid_dict:
                    pid_dict['participant'] = temp
                else:
                    pid_dict['nonparticipant'] = temp
            else:
                pid_dict[pr.src_dst_maps[datum[pr.m_source_type]]] = temp

        if mtype == 'all':
            if datum[pr.m_target_type] in pid_dict:
                temp = pid_dict['participant']
                p_np = 0
            else:
                temp = pid_dict['nonparticipant']
                p_np = 1
        else:
            temp = pid_dict[pr.src_dst_maps[datum[pr.m_target_type]]]

        if datum[pr.m_target] not in temp:
            if not separate_pid_npid:
                temp[datum[pr.m_target]] = pid
                pid += 1
            else:
                if p_np == 0:
                    temp[datum[pr.m_target]] = 'P' + str(pid[0])
                    pid[0] += 1
                else:
                    temp[datum[pr.m_target]] = 'NP' + str(pid[1])
                    pid[1] += 1
                p_np = -1
            if mtype == 'all':
                if datum[pr.m_target_type] in pid_dict:
                    pid_dict['participant'] = temp
                else:
                    pid_dict['nonparticipant'] = temp
            else:
                pid_dict[pr.src_dst_maps[datum[pr.m_target_type]]] = temp
    if mtype is 'all':
        print 'Participant:', len(pid_dict['participant']), \
            'Non: ', len(pid_dict['nonparticipant'])
    else:
        print 'Participant: ', len(pid_dict[pr.participant[mtype]]), \
            'Non: ', len(pid_dict[pr.nparticipant[mtype]])

    return pid_dict


def getpid(pid_dict, pid):
    for p_type in pid_dict.keys():
        if pid in pid_dict[p_type]:
            return pid_dict[p_type][pid]
    return None


def getlinks(pid_dict, data, ignore_mtype=True):
    if [] == data:
        return {}, []
    links = {}
    for datum in data:
        src = getpid(pid_dict, datum[pr.m_source])
        dst = getpid(pid_dict, datum[pr.m_target])
        if ignore_mtype:
            if (src, dst) not in links:
                links[(src, dst)] = 0
            links[(src, dst)] += 1
        else:
            mtype = datum[pr.m_type].lower().split('_')[0]
            if (src, dst, mtype) not in links:
                links[(src, dst, mtype)] = 0
            links[(src, dst, mtype)] += 1
    links_tuple = []
    for key in links.keys():
        src = key[0]
        dst = key[1]
        if not ignore_mtype:
            mtype = key[2]
        wt = links[key]
        if ignore_mtype:
            links_tuple.append((src, dst, {'weight': wt}))
        else:
            links_tuple.append((src, dst, {'weight': wt, 'mtype': mtype}))
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


def creategraph(data, isStatic=True, filterType='sms', graph_directed=True, pid_dict=None):
    pid_dict = getuniqueparticipants(data, filterType) if None is pid_dict else pid_dict
    graph_obj = graph(is_directed=graph_directed, is_multigraph=filterType == 'all')
    if isStatic:
        ignore_mtype = filterType != 'all'
        links, link_tuple = getlinks(pid_dict, data, ignore_mtype)
        graph_obj.addnodes(pid_dict[pr.participant[filterType]].values(), 'P')
        graph_obj.addnodes(pid_dict[pr.nparticipant[filterType]].values(), 'NP')
        graph_obj.addedges(link_tuple)
        return links, link_tuple, graph_obj, pid_dict
    else:
        start_datetime = dt.datetime.strptime(pr.start_datetime, '%Y-%m-%d %H:%M:%S')
        week_dict, link_tuple, week_content = getdynamiclinks(pid_dict,
                                                              data, start_datetime)
        to_write_edge, to_write_node = graph_obj.exportdynamicgraph(link_tuple, pid_dict)
        return to_write_edge, to_write_node, week_dict, pid_dict, week_content


def missingweeks(data, threshold_value=0):
    no_of_weeks = max(data[data.keys()[0]].keys())
    per_week_msgs = {'In': [], 'Out': []}
    missing_weeks_dict = {}
    for idx in range(no_of_weeks + 1):
        temp = {'In': [], 'Out': []}
        missing_weeks_dict[idx] = temp

    for pid in data.keys():
        pid_data = data[pid]
        weeks_missing = {'In': 0, 'Out': 0}
        for week_no in pid_data.keys():
            per_week_msgs['In'].append(pid_data[week_no][0])
            per_week_msgs['Out'].append(pid_data[week_no][1])
            if threshold_value >= pid_data[week_no][0]:
                weeks_missing['In'] += 1
            if threshold_value >= pid_data[week_no][1]:
                weeks_missing['Out'] += 1
        missing_weeks_dict[weeks_missing['In']]['In'].append(pid)
        missing_weeks_dict[weeks_missing['Out']]['Out'].append(pid)

    return missing_weeks_dict, per_week_msgs


def getfilterdata(filters_chosen, filter_files, cumulative_list=False, catch_all=False):
    data = {}
    cumulative_pid_list = []
    catch_all_data = {}
    for idx in range(len(filters_chosen)):
        loaded_data = recovervariable(filter_files[idx])
        catch_all_data[filters_chosen[idx]] = {}
        temp = []
        for key in loaded_data.keys():
            temp += loaded_data[key].keys()
            category_data = loaded_data[key]
            for pid in category_data.keys():
                if pid not in catch_all_data[filters_chosen[idx]]:
                    catch_all_data[filters_chosen[idx]][pid] = category_data[pid]
                else:
                    for sno in category_data[pid].keys():
                        if sno not in catch_all_data[filters_chosen[idx]][pid]:
                            catch_all_data[filters_chosen[idx]][pid][sno] = category_data[pid][sno]
        data[filters_chosen[idx]] = temp
        # catch_all_data[filters_chosen[idx]] = loaded_data[key]
        cumulative_pid_list += temp
    if cumulative_list:
        return cumulative_pid_list
    elif catch_all:
        return catch_all_data
    else:
        return data
