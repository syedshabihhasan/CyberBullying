import argparse
import helper as hlp
from filterByField import filterfields
from basicInfo import privateInfo as pr
from graphing import creategraph
from scipy import stats
import numpy as np
from copy import deepcopy
from createweeklyinfo import weeklyinfo
import matplotlib.pyplot as plt
from statsmodels.distributions.empirical_distribution import ECDF

def get_degree_distribution(graph_obj, pids_to_consider):
    deg_dist = {}
    for node_id in pids_to_consider:
        deg = graph_obj.getdegrees(node_id)
        if deg not in deg_dist:
            deg_dist[deg] = 0
        deg_dist[deg] += 1
    return deg_dist

def check_triad_validity(first_node, second_node, third_node, pid_dict, min_participants):
    no_p = 0
    if first_node in pid_dict['participants'].values():
        no_p += 1
    if second_node in pid_dict['participants'].values():
        no_p += 1
    if third_node in pid_dict['participants'].values():
        no_p += 1
    return no_p >= min_participants, no_p

def find_triads(graph_obj, pid_dict, min_participants=1):
    triad_dict = {}
    if min_participants < 1:
        print 'Cannot have less than 1 participant in the triad'
        return None
    participants = pid_dict['participants'].values()
    for first_node in participants:
        first_node_nb = graph_obj.getneighbors(first_node)
        for second_node in first_node_nb:
            second_node_nb = graph_obj.getneighbors(second_node)
            try:
                second_node_nb.remove(first_node)
            except:
                print 'uh oh! first node: ', first_node, ' second node: ', second_node
            for third_node in second_node_nb:
                third_node_nb = graph_obj.getneighbors(third_node)
                if first_node in third_node_nb:
                    all_clear, no_p = check_triad_validity(first_node, second_node, third_node, pid_dict,
                                                           min_participants)
                    if all_clear:
                        triad = [first_node, second_node, third_node]
                        triad.sort()
                        triad_tuple = tuple(triad)
                        if triad_tuple not in triad_dict:
                            a_b_pol = graph_obj.get_edge_data(triad[0], triad[1])['polarity']
                            b_c_pol = graph_obj.get_edge_data(triad[1], triad[2])['polarity']
                            c_a_pol = graph_obj.get_edge_data(triad[2], triad[0])['polarity']
                            triad_dict[triad_tuple] = [a_b_pol, b_c_pol, c_a_pol, no_p]
    return triad_dict

def create_undirected_edges(data, pid_dict):
    edges_dict = {}
    for datum in data:
        node1 = hlp.getpid(pid_dict, datum[pr.m_source])
        node2 = hlp.getpid(pid_dict, datum[pr.m_target])
        if node1 < node2:
            edge_pair = (node1, node2)
        else:
            edge_pair = (node2, node1)
        if edge_pair not in edges_dict:
            edges_dict[edge_pair] = [0, [0,0,0]]
        temp = edges_dict[edge_pair]
        temp[0] += 1
        if datum[-1] == 'P':
            temp[1][0] += 1
        elif datum[-1] == 'U':
            temp[1][1] += 1
        elif datum[-1] == 'N':
            temp[1][2] += 1
        else:
            print 'Something fishy:', datum
        edges_dict[edge_pair] = temp

    networkx_edges = []
    pos_neg = [0, 0]
    for edge_pair in edges_dict:
        edge_values = edges_dict[edge_pair]
        polarity_count = edge_values[1]
        if 0 == polarity_count[0] and 0 == polarity_count[2]:
            # there are no + or - messages, ignore edge
            continue
        if polarity_count[0] >= polarity_count[2]:
            polarity = 'P'
            pos_neg[0] += 1
        else:
            polarity = 'N'
            pos_neg[1] += 1
        networkx_edges.append((edge_pair[0], edge_pair[1],
                               {'weight': edge_values[0], 'polarity': polarity,
                                'color': 'red' if polarity == 'N' else 'green'}))
    return networkx_edges, edges_dict, pos_neg


def summarize_triad(triad_dict):
    summary_triad = {('P', 'P', 'P'):[], ('P', 'P', 'N'):[], ('P', 'N', 'N'): [], ('N', 'N', 'N'): []}
    internal_use = {0: ('N', 'N', 'N'), 1: ('P', 'N', 'N'), 2: ('P', 'P', 'N'), 3: ('P', 'P', 'P')}
    total_triads = len(triad_dict.keys()) + 0.0
    for triad_nodes in triad_dict:
        triad_type = triad_dict[triad_nodes]
        no_p = 0
        for e_type in triad_type:
            if 'P' == e_type:
                no_p += 1
        summary_triad[internal_use[no_p]].append(triad_nodes)

    frac_triads = {}
    for summary in summary_triad:
        if 0 == total_triads:
            frac_triads[summary] = 0
        else:
            frac_triads[summary] = len(summary_triad[summary]) / total_triads
    return summary_triad, frac_triads

def create_graph_constructs(data, pid_dict):
    participant_nodes = pid_dict['participants'].values()
    non_participant_nodes = pid_dict['nonparticipants'].values()

    edges, ground_edges, polarity_count = create_undirected_edges(data, pid_dict)

    return participant_nodes, non_participant_nodes, edges, ground_edges, polarity_count

def get_random_edge_polarity(polarity_count, edges):
    total_count = sum(polarity_count) + 0.0
    xk = [1, -1]
    pk = [polarity_count[0]/total_count, polarity_count[1]/total_count]
    seed = 1989
    custom_dist = stats.rv_discrete(name='custom_dist', values=(xk, pk), seed=seed)
    polarity_dist_custm = custom_dist.rvs(size=len(edges))
    new_edges = []
    for idx in range(len(edges)):
        edge = deepcopy(edges[idx])
        edge[2]['polarity'] = 'P' if polarity_dist_custm[idx] == 1 else 'N'
        edge[2]['color'] = 'green' if polarity_dist_custm[idx] == 1 else 'red'
        new_edges.append(edge)
    return new_edges, custom_dist, polarity_dist_custm

def conduct_triad_analysis(labelled_data, pid_dict):
    # get the basic networkx graphing constructs
    p, np, edges, ground_edges, polarity_count = create_graph_constructs(labelled_data, pid_dict)

    # get a random distribution of polarity
    random_edges, random_dist, random_labels = get_random_edge_polarity(polarity_count, edges)

    # create graph
    graph = creategraph()
    graph.addnodes(p, 'P')
    graph.addnodes(np, 'NP')
    graph.addedges(edges)
    deg_dist = get_degree_distribution(graph, p)


    # create random graph
    graph_rand = creategraph()
    graph_rand.addnodes(p, 'P')
    graph_rand.addnodes(np, 'NP')
    graph_rand.addedges(random_edges)
    deg_dist_rand = get_degree_distribution(graph_rand, np)

    triad_dict = find_triads(graph, pid_dict, min_participants=2)
    triad_dict_rand = find_triads(graph_rand, pid_dict, min_participants=2)

    # summarize the types of edges
    summary_triad, frac_triad = summarize_triad(triad_dict)
    summary_triad_rand, frac_triad_rand = summarize_triad(triad_dict_rand)

    return [graph, triad_dict, summary_triad, frac_triad, deg_dist], \
           [graph_rand, triad_dict_rand, summary_triad_rand, frac_triad_rand, deg_dist_rand]


def get_polarity_directionality(labelled_data, filters = ['sms', 'fb_message']):
    pos = [0]
    neg = [0]
    neu = [0]
    for _ in filters:
        pos.append(0)
        neg.append(0)
        neu.append(0)

    for datum in labelled_data:
        m_type = datum[pr.m_type]
        if m_type in filters:
            idx = filters.index(m_type)
            if datum[-1] == 'P':
                pos[idx+1] += 1
                pos[0] += 1
            elif datum[-1] == 'N':
                neg[idx+1] += 1
                neg[0] += 1
            elif datum[-1] == 'U':
                neu[idx+1] += 1
                neu[0] += 1
    return pos, neg, neu

def get_count_degrees_messages_directed(labelled_data, pid_dict):
    fobj = filterfields()
    fobj.setdata(labelled_data)

    in_m = []
    out_m = []
    in_d = []
    out_d = []
    pid_order = []
    for pid in pid_dict:
        in_data = fobj.filterbyequality(pr.m_target, pid)
        out_data = fobj.filterbyequality(pr.m_source, pid)
        in_m.append(len(in_data))
        out_m.append(len(out_data))
        people_sending_me_messages = fobj.getuniqueelements(pr.m_source, data=in_data)
        people_i_am_sending_messages_to = fobj.getuniqueelements(pr.m_target, data=out_data)
        in_d.append(len(people_sending_me_messages))
        out_d.append(len(people_i_am_sending_messages_to))
        pid_order.append(pid)

    return in_m, out_m, in_d, out_d

def plot_messages_degree(message_count, xlabel, ylabel, path_to_store, is_degree=False):
    msg_dist = {}
    fig = plt.figure()
    ax = fig.add_subplot(111)
    if is_degree:
        for mc in message_count:
            if mc not in msg_dist:
                msg_dist[mc] = 0
            msg_dist[mc] += 1
        items = sorted(msg_dist.items())
        ecdf = ECDF(message_count)
        x = list(ecdf.x)
        y = list(ecdf.y)
        # ax.plot([k for (k, v) in items], [v for (k, v) in items], 'b-', linewidth=2.0, marker='o', markersize=10.0,
        #         markerfacecolor='r', markeredgecolor='k', markeredgewidth=2.0)
        ax.plot(x, y, 'b-', linewidth=2.0)
    else:
        ecdf = ECDF(message_count)
        x = list(ecdf.x)
        #x = x[1:]
        y = list(ecdf.y)
        #y = y[1:]
        ax.plot(x, y, 'b-', linewidth=2)
    if not is_degree:
        ax.set_xscale('log')
        #plt.ylim([1, 4])
        plt.ylim([0, 1])
        plt.xlim(xmax=20000)
        plt.xticks(fontsize=20)
        plt.yticks(np.arange(0, 1.1, 0.1), fontsize=20)
    else:
        #ax.set_xscale('log')
        #x.set_yscale('log')
        plt.ylim([0, 1])
        plt.yticks(np.arange(0, 1.1, 0.1), fontsize=20)
        # plt.ylim([1, 10])
        plt.xticks(fontsize=20)
        # plt.yticks(range(1, 11), fontsize=20)
    plt.xlabel(xlabel, fontsize=20)
    plt.ylabel(ylabel, fontsize=20)
    plt.grid(True)
    plt.savefig(path_to_store)
    plt.show()

def summarize_message_by_src_trg(labelled_data):
    counts = {'P-P': 0, 'P-NP': 0, 'NP-P': 0, 'NP-NP': 0}
    for datum in labelled_data:
        src_t = datum[pr.m_source_type]
        trg_t = datum[pr.m_target_type]
        key = ''
        if src_t == 'participant':
            key += 'P-'
        else:
            key += 'NP-'
        if trg_t == 'participant':
            key += 'P'
        else:
            key += 'NP'
        counts[key] += 1
    return counts

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-m', '-M', required=True,
                        help='Sentiment Message file')
    parser.add_argument('-t', '-T', action='store_true',
                        help='Sentiment type flag, if used then vader, else afinn')
    parser.add_argument('-f', '-F', required=True,
                        help='Folder to store checkpoints, and final result')
    parser.add_argument('-w', '-W', required=False,
                        help='Per week/month analysis')

    args = parser.parse_args()
    message_file = args.m
    sentiment_type = args.t
    location_to_store = args.f
    survey_file = args.w

    # get message data, only sms and fb_message
    ff = filterfields(message_file)
    ff.setdata(ff.getdata()[1:])
    sms_data = ff.filterbyequality(pr.m_type, 'sms')
    pid_dict_sms = hlp.getuniqueparticipants2(sms_data)
    fb_message_data = ff.filterbyequality(pr.m_type, 'fb_message')
    pid_dict_fb = hlp.getuniqueparticipants2(fb_message_data)
    message_data = sms_data + fb_message_data

    # put the labels on
    labelled_data = hlp.processvadersentiment(message_data, label_only=False) if sentiment_type else \
        hlp.processafinnsentiment(message_data, label_only=False)

    if survey_file is not None:
        wi = weeklyinfo()
        weekly_info = wi.getweeklyfo(survey_file)
        weekly_data = hlp.divideintoweekly(labelled_data, weekly_info, ff)

    # get the pid_dict for easier handling
    pid_dict = hlp.getuniqueparticipants2(labelled_data)

    print '***SMS***'
    print 'P: ', len(pid_dict_sms['participants'].values()), ' NP: ', len(pid_dict_sms['nonparticipants'].values())

    print '***FB***'
    print 'P: ', len(pid_dict_fb['participants'].values()), 'NP: ', len(pid_dict_fb['nonparticipants'].values())

    print '***OVERALL***'
    print 'P: ', len(pid_dict['participants'].values()), 'NP: ', len(pid_dict['nonparticipants'].values())

    if survey_file is not None:
        week_list = weekly_data.keys()
        week_list.sort()
        # this is not good, as there aren't enough triads
        months = [[1, 2, 3, 4],
                  [5, 6, 7, 8],
                  [9, 10, 11, 12],
                  [13, 14, 15, 16],
                  [17, 18, 19, 20],
                  [21, 22, 23, 24]]
        # this has at least 8 triads, always, use this
        months2 = [[1, 2, 3, 4, 5, 6, 7, 8],
                  [9, 10, 11, 12, 13, 14, 15, 16],
                  [17, 18, 19, 20, 21, 22, 23, 24],]
        month_idx = 1
        for month in months2:
            labelled_data = []
            for week in month:
                labelled_data.extend(weekly_data[week])
            general_graph, random_graph = conduct_triad_analysis(labelled_data, pid_dict)
            frac_triad = general_graph[3]
            summary_triad = general_graph[2]
            frac_triad_rand = random_graph[3]
            summary_triad_rand = random_graph[2]
            print '** Months ', 2*month_idx-1, 2*month_idx, ': ', month,' ***'
            for summary in frac_triad:
                print summary, 'Study: ', frac_triad[summary], '(', len(summary_triad[summary]), ')', ' Random: ', \
                frac_triad_rand[summary], '(', len(summary_triad_rand[summary]), ')'
            hlp.dumpvariable([general_graph, random_graph, labelled_data, pid_dict], 'month_'+str(month_idx)+'.list', location_to_store)
            month_idx += 1
    else:
        general_graph, random_graph = conduct_triad_analysis(labelled_data, pid_dict)
        frac_triad = general_graph[3]
        summary_triad = general_graph[2]
        frac_triad_rand = random_graph[3]
        summary_triad_rand = random_graph[2]
        for summary in frac_triad:
            print summary, 'Study: ', frac_triad[summary], '(', len(summary_triad[summary]), ')', ' Random: ', \
                frac_triad_rand[summary], '(', len(summary_triad_rand[summary]), ')'
        hlp.dumpvariable([general_graph, random_graph, labelled_data, pid_dict], 'Overall.list', location_to_store)
        # plot_degree_dist(general_graph[4], 'Degree(d)', '# of Participants with Degree d')
        pos, neg, neu = get_polarity_directionality(labelled_data)
        print 'Overall (P/N/U): ', pos[0], neg[0], neu[0]
        print 'SMS (P/N/U): ', pos[1], neg[1], neu[1]
        print 'FB (P/N/U): ', pos[2], neg[2], neu[2]
        in_m, out_m, in_d, out_d = get_count_degrees_messages_directed(labelled_data, pid_dict['participants'])
        print '***Incoming Messages***'
        print 'Total: ', sum(in_m), 'Mean: ', np.mean(in_m), 'Std. dev.: ', np.std(in_m)
        print '***Outgoing Messages***'
        print 'Total: ', sum(out_m), 'Mean: ', np.mean(out_m), 'Std. dev.: ', np.std(out_m)
        print '***In Degree***'
        print 'Total: ', sum(in_d), 'Mean: ', np.mean(in_d), 'Std. dev.: ', np.std(in_d)
        print '***Out Degree***'
        print 'Total: ', sum(out_d), 'Mean: ', np.mean(out_d), 'Std. dev.: ', np.std(out_d)
        summary_src_trg = summarize_message_by_src_trg(labelled_data)
        print '***COUNTS***'
        print summary_src_trg
        plot_messages_degree(in_m, '# of Incoming Messages', 'Cumulative Participant Prob.',
                      location_to_store+'in_messages.pdf')
        plot_messages_degree(out_m, '# of Outgoing Messages', 'Cumulative Participant Prob.',
                      location_to_store+'out_messages.pdf')
        plot_messages_degree(in_d, 'In Degree', 'Cumulative Participant Prob.',
                      location_to_store+'in_degree.pdf', True)
        plot_messages_degree(out_d, 'Out Degree', 'Cumulative Participant Prob.',
                      location_to_store+'out_degree.pdf', True)
    print 'TADAA!!'



if __name__ == "__main__":
    main()