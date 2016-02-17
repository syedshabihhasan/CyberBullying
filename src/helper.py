def getuniqueparticipants(data):
    pid_dict = {'participant': {}, 'phone': {}}
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
    print 'Participant: ', len(pid_dict['participant']), 'Non: ', len(pid_dict['phone'])
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
