import argparse
import helper as hlp
from basicInfo import privateInfo as pr

def getcodedinfo(srctrg, pid_dict, m_type='all'):
    if srctrg in pid_dict[pr.participant[m_type]]:
        return pid_dict[pr.participant[m_type]][srctrg]
    if srctrg in pid_dict[pr.nparticipant[m_type]]:
        return pid_dict[pr.nparticipant[m_type]][srctrg]
    return None

def getedgecount(data, pid_dict):
    edge_dict = {}
    for datum in data:
        source = getcodedinfo(datum[pr.m_source], pid_dict)
        target = getcodedinfo(datum[pr.m_target], pid_dict)
        if (source, target) not in edge_dict:
            edge_dict[(source, target)] = [0, 0, 0]
        if datum[pr.m_pos] > datum[pr.m_neu]:
            if datum[pr.m_pos] > datum[pr.m_neg]:
                edge_dict[(source, target)][0] += 1
            else:
                edge_dict[(source, target)][2] += 1
        else:
            if datum[pr.m_neu] > datum[pr.m_neg]:
                edge_dict[(source, target)][1] += 1
            else:
                edge_dict[(source, target)][2] += 1
    return edge_dict

def converttolist(edge_dict):
    all_edges = edge_dict.keys()
    all_edges.sort()
    edge_list = []
    for source, target in all_edges:
        senti_count = edge_dict[(source, target)]
        edge_list.append([source, target, senti_count[0], senti_count[1], senti_count[2]])
    return edge_list

def convertpiddicttolist(pid_dict, m_type='all'):
    pid_list = []
    p_list = pid_dict[pr.participant[m_type]]
    np_list = pid_dict[pr.nparticipant[m_type]]
    for pid in p_list:
        pid_list.append([pid, p_list[pid]])
    for pid in np_list:
        pid_list.append([pid, np_list[pid]])
    return pid_list

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-m', '-M', type=str, required=True,
                        help='Message file')
    parser.add_argument('-p', '-P', type=str, required=True,
                        help='pid_dict')
    parser.add_argument('-o', '-O', type=str, required=True,
                        help='output folder')
    parser.add_argument('-of', '-OF', type=str, required=True,
                        help='output file')

    args = parser.parse_args()

    message_data = hlp.recovervariable(args.m)
    pid_dict = hlp.recovervariable(args.p)

    output_folder = args.o
    output_file = args.of

    edge_dict = getedgecount(message_data, pid_dict)
    edge_list = converttolist(edge_dict)

    hlp.writecsv([['source', 'target', 'pos', 'neu', 'neg']]+edge_list, output_folder+output_file)
    hlp.writecsv([['PID', 'Coded ID']]+convertpiddicttolist(pid_dict), output_folder+'pid_dict_list.csv')


if __name__ == "__main__":
    main()