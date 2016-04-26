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
from nltk.corpus import stopwords
from collections import Counter
from afinnpolarity import afinnsenti

def __get_message_type(datum):
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
    return key


def __get_basic_count():
    return {'P-P': 0, 'P-NP': 0, 'NP-P': 0, 'NP-NP': 0}

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
    pos = {}
    neg = {}
    neu = {}

    for m_type in filters:
        pos[m_type] = __get_basic_count()
        neg[m_type] = __get_basic_count()
        neu[m_type] = __get_basic_count()

    for datum in labelled_data:
        m_type = datum[pr.m_type]
        if m_type in filters:
            pairing = __get_message_type(datum)
            if datum[-1] == 'P':
                pos[m_type][pairing] += 1
            elif datum[-1] == 'N':
                neg[m_type][pairing] += 1
            elif datum[-1] == 'U':
                neu[m_type][pairing] += 1
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
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ecdf_in = ECDF(message_count[0])
    ecdf_out = ECDF(message_count[1])
    x_in = list(ecdf_in.x)
    y_in = list(ecdf_in.y)
    x_out = list(ecdf_out.x)
    y_out = list(ecdf_out.y)
    ax.plot(x_in, y_in, 'b-', linewidth=3.0, label='In')
    ax.plot(x_out, y_out, 'r-', linewidth=3.0, label='Out')
    if not is_degree:
        ax.set_xscale('log')
        plt.ylim([0, 1])
        plt.xlim(xmax=20000)
        plt.xticks(fontsize=20)
        plt.yticks(np.arange(0, 1.1, 0.1), fontsize=20)
    else:
        plt.ylim([0, 1])
        plt.yticks(np.arange(0, 1.1, 0.1), fontsize=20)
        plt.xticks(fontsize=20)
    plt.xlabel(xlabel, fontsize=20)
    plt.ylabel(ylabel, fontsize=20)
    plt.legend(loc=4, fontsize=20)
    plt.grid(True)
    plt.gcf().subplots_adjust(bottom=0.15)
    plt.savefig(path_to_store)
    plt.show()
    return


def summarize_message_by_src_trg(labelled_data):
    final_counts = {}
    for datum in labelled_data:
        m_type = datum[pr.m_type]
        key = __get_message_type(datum)
        if m_type not in final_counts:
            final_counts[m_type] = __get_basic_count()
        final_counts[m_type][key] += 1
    return final_counts

def word_count(labelled_data, m_type = ['sms', 'fb_message']):
    stop = stopwords.words('english')
    stop.append(u'')
    word_list = {}
    short_list = {}
    for mtype in m_type:
        word_list[mtype] = []
        short_list[mtype] = []
    word_list['overall'] = []
    short_list['overall'] = []
    for datum in labelled_data:
        message = datum[pr.m_content].lower()
        mtype = datum[pr.m_type]
        message = message.translate(None, ".,!'?")
        for word in message.split(' '):
            if word not in stop:
                if 3 >= len(word):
                    short_list[mtype].append(word)
                    short_list['overall'].append(word)
                else:
                    word_list[mtype].append(word)
                    word_list['overall'].append(word)
    return word_list, short_list

def create_word_count_csv(word_list, n=20, mtype_order = ['overall', 'sms', 'fb_message']):
    counters = {}
    toWrite = []
    toWrite.append(mtype_order)
    for mtype in mtype_order:
        counters[mtype] = Counter(word_list[mtype]).most_common(n)
    for idx in range(n):
        temp = []
        for mtype in mtype_order:
            c = counters[mtype]
            temp.append(''+c[idx][0]+'('+str(c[idx][1])+')')
        toWrite.append(temp)
    return toWrite

def __generate_color_matrix(month_data, colors_map):
    to_return = []
    pid_list = month_data.keys()
    pid_list.sort()
    for pid in pid_list:
        sentiment_dist = month_data[pid]
        if 0 == sum(sentiment_dist):
            to_return.append(colors_map['X'])
        elif 0 == sentiment_dist.index(max(sentiment_dist)):
            to_return.append(colors_map['P'])
        elif 1 == sentiment_dist.index(max(sentiment_dist)):
            to_return.append(colors_map['N'])
        elif 2 == sentiment_dist.index(max(sentiment_dist)):
            to_return.append(colors_map['U'])
    return to_return

def per_participant_sentiment(weekly_data, pid_dict):
    months2 = [[1, 2, 3, 4, 5, 6, 7, 8],
               [9, 10, 11, 12, 13, 14, 15, 16],
               [17, 18, 19, 20, 21, 22, 23, 24, 25]]
    weeks = [[i] for i in range(1, 26)]
    colors_map = {'P': [0, 1, 0], 'N': [1, 0, 0], 'U': [0, 0, 1], 'X': [1, 1, 1]}
    monthly_data_sentiment = {}
    monthly_data_sentiment_in = {}
    monthly_data_sentiment_out = {}
    pid_values = pid_dict.values()
    month_idx = 1
    final_overall_plot = []
    final_incoming_plot = []
    final_outgoing_plot = []
    xtick = []
    ytick = []
    for month in weeks:
        monthly_data = []
        for weekno in month:
            monthly_data.extend(weekly_data[weekno])
        monthly_data_sentiment[month_idx] = {}
        monthly_data_sentiment_in[month_idx] = {}
        monthly_data_sentiment_out[month_idx] = {}
        for pid in pid_values:
            # [pos, neg, neu]
            monthly_data_sentiment[month_idx][pid] = [0, 0, 0]
            monthly_data_sentiment_in[month_idx][pid] = [0, 0, 0]
            monthly_data_sentiment_out[month_idx][pid] = [0, 0, 0]
        for datum in monthly_data:
            if 'participant' == datum[pr.m_source_type]:
                if 'P' == datum[-1]:
                    monthly_data_sentiment_out[month_idx][pid_dict[datum[pr.m_source]]][0] += 1
                    monthly_data_sentiment[month_idx][pid_dict[datum[pr.m_source]]][0] += 1
                elif 'N' == datum[-1]:
                    monthly_data_sentiment_out[month_idx][pid_dict[datum[pr.m_source]]][1] += 1
                    monthly_data_sentiment[month_idx][pid_dict[datum[pr.m_source]]][1] += 1
                elif 'U' == datum[-1]:
                    monthly_data_sentiment_out[month_idx][pid_dict[datum[pr.m_source]]][2] += 1
                    monthly_data_sentiment[month_idx][pid_dict[datum[pr.m_source]]][2] += 1
            if 'participant' == datum[pr.m_target_type]:
                if 'P' == datum[-1]:
                    monthly_data_sentiment_in[month_idx][pid_dict[datum[pr.m_target]]][0] += 1
                    monthly_data_sentiment[month_idx][pid_dict[datum[pr.m_target]]][0] += 1
                elif 'N' == datum[-1]:
                    monthly_data_sentiment_in[month_idx][pid_dict[datum[pr.m_target]]][1] += 1
                    monthly_data_sentiment[month_idx][pid_dict[datum[pr.m_target]]][1] += 1
                elif 'U' == datum[-1]:
                    monthly_data_sentiment_in[month_idx][pid_dict[datum[pr.m_target]]][2] += 1
                    monthly_data_sentiment[month_idx][pid_dict[datum[pr.m_target]]][2] += 1
        final_overall_plot.append(__generate_color_matrix(monthly_data_sentiment[month_idx], colors_map))
        final_incoming_plot.append(__generate_color_matrix(monthly_data_sentiment_in[month_idx], colors_map))
        final_outgoing_plot.append(__generate_color_matrix(monthly_data_sentiment_out[month_idx], colors_map))
        month_idx += 1
    sorted_vals = pid_dict.values()
    sorted_vals.sort()
    for val in sorted_vals:
        xtick.append('P'+str(val))
    for i in range(1, 26):
        ytick.append(str(i))
    return final_overall_plot, final_incoming_plot, final_outgoing_plot, xtick, ytick



def __temp_testing_for_discrepancy(labelled_data, weekly_data):
    labelled_data_keys = set()
    labelled_data_dict = {}
    weekly_data_keys = set()
    for datum in labelled_data:
        labelled_data_keys.add(datum[pr.msg_id])
        labelled_data_dict[datum[pr.msg_id]] = datum
    for weekno in weekly_data:
        for datum in weekly_data[weekno]:
            weekly_data_keys.add(datum[pr.msg_id])
    not_present = labelled_data_keys.difference(weekly_data_keys)
    messages_not_present = []
    for msg_id in not_present:
        messages_not_present.append(labelled_data_dict[msg_id])
    print 'Messages not present'

def __plot_imshow(data, xlabel, ylabel, xticks, yticks, filepath):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.imshow(data, interpolation='nearest')
    plt.xticks(range(0, len(xticks)+1), xticks, rotation='vertical', fontsize=10)
    plt.yticks(range(0, len(yticks)+1), yticks, fontsize=10)
    plt.xlabel(xlabel, fontsize=20)
    plt.ylabel(ylabel, fontsize=20)
    plt.grid(True)
    plt.savefig(filepath)

def __get_top_word_sentiment(top_words):
    afinn = afinnsenti()
    word_senti_count = []
    for (word, count) in top_words:
        polarity = afinn.get_sentiment_label(word)
        if -1 == polarity:
            word_senti_count.append((word, 'N', count))
        elif 1 == polarity:
            word_senti_count.append((word, 'P', count))
        elif 0 == polarity:
            word_senti_count.append((word, 'U', count))
    return word_senti_count

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

    #__temp_testing_for_discrepancy(labelled_data, weekly_data)

    # get the pid_dict for easier handling
    pid_dict = hlp.getuniqueparticipants2(labelled_data)
    if survey_file is not None:
        over_sent, in_sent, out_sent, xtick, ytick = per_participant_sentiment(weekly_data, pid_dict['participants'])
        __plot_imshow(over_sent, 'Participant', 'Week #', xtick, ytick, location_to_store+'sent_imshow_over.pdf')
        __plot_imshow(in_sent, 'Participant', 'Week #', xtick, ytick, location_to_store+'sent_imshow_in.pdf')
        __plot_imshow(out_sent, 'Participant', 'Week #', xtick, ytick, location_to_store+'sent_imshow_out.pdf')

    print '***SMS***'
    print 'P: ', len(pid_dict_sms['participants'].values()), ' NP: ', len(pid_dict_sms['nonparticipants'].values())

    print '***FB***'
    print 'P: ', len(pid_dict_fb['participants'].values()), 'NP: ', len(pid_dict_fb['nonparticipants'].values())

    print '***OVERALL***'
    print 'P: ', len(pid_dict['participants'].values()), 'NP: ', len(pid_dict['nonparticipants'].values())

    summary_src_trg = summarize_message_by_src_trg(labelled_data)
    print '***Message Distribution***'
    for m_type_1 in summary_src_trg:
        print m_type_1, summary_src_trg[m_type_1]

    if survey_file is not None:
        week_list = weekly_data.keys()
        week_list.sort()
        # this is not good, as there aren't enough triads
        months = [[1, 2, 3, 4],
                  [5, 6, 7, 8],
                  [9, 10, 11, 12],
                  [13, 14, 15, 16],
                  [17, 18, 19, 20],
                  [21, 22, 23, 24, 25]]
        # this has at least 8 triads, always, use this
        months2 = [[1, 2, 3, 4, 5, 6, 7, 8],
                  [9, 10, 11, 12, 13, 14, 15, 16],
                  [17, 18, 19, 20, 21, 22, 23, 24, 25]]
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
            print 'len(LD): ', len(labelled_data)
            for summary in frac_triad:
                print summary, 'Study: ', frac_triad[summary], '(', len(summary_triad[summary]), ')', ' Random: ', \
                frac_triad_rand[summary], '(', len(summary_triad_rand[summary]), ')'
            words_list, short_list = word_count(labelled_data)
            toWrite_wl_csv = create_word_count_csv(words_list)
            hlp.writecsv(toWrite_wl_csv, location_to_store+'word_list_'+str(2*month_idx-1)+'-'+str(2*month_idx)+'.csv',
                         delimiter_sym=',')
            for mtype in words_list:
                counted_words = Counter(words_list[mtype])
                counted_short = Counter(short_list[mtype])
                print '***For '+mtype+' ***'
                print 'Top 20 words: ', __get_top_word_sentiment(counted_words.most_common(20))
                print 'Top 20 short: ', counted_short.most_common(20)
                print '\n\n'
            hlp.dumpvariable([general_graph, random_graph, labelled_data, pid_dict], 'month_'+str(month_idx)+'.list', location_to_store)
            month_idx += 1
    else:
        print 'len(LD): ', len(labelled_data)
        words_list, short_list = word_count(labelled_data)
        toWrite_wl_csv = create_word_count_csv(words_list)
        hlp.writecsv(toWrite_wl_csv, location_to_store+'word_list.csv', delimiter_sym=',')
        for mtype in words_list:
            counted_words = Counter(words_list[mtype])
            counted_short = Counter(short_list[mtype])
            print '***For '+mtype+' ***'
            print 'Top 20 words: ', __get_top_word_sentiment(counted_words.most_common(20))
            print 'Top 20 short: ', counted_short.most_common(20)
            print '\n\n'
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
        print '***Polarity Distribution***'
        print 'Positive: \n', pos
        print 'Negative: \n', neg
        print 'Neutral: \n', neu

        in_m, out_m, in_d, out_d = get_count_degrees_messages_directed(labelled_data, pid_dict['participants'])
        print '***Incoming Messages***'
        print 'Total: ', sum(in_m), 'Mean: ', np.mean(in_m), 'Std. dev.: ', np.std(in_m)
        print '***Outgoing Messages***'
        print 'Total: ', sum(out_m), 'Mean: ', np.mean(out_m), 'Std. dev.: ', np.std(out_m)
        print '***In Degree***'
        print 'Total: ', sum(in_d), 'Mean: ', np.mean(in_d), 'Std. dev.: ', np.std(in_d)
        print '***Out Degree***'
        print 'Total: ', sum(out_d), 'Mean: ', np.mean(out_d), 'Std. dev.: ', np.std(out_d)
        print '***COUNTS***'
        plot_messages_degree([in_m, out_m], '# of Messages', 'Cumulative Participant Prob.',
                      location_to_store+'in_out_messages.pdf')
        # plot_messages_degree(out_m, '# of Outgoing Messages', 'Cumulative Participant Prob.',
        #               location_to_store+'out_messages.pdf')
        plot_messages_degree([in_d, out_d], 'Degree', 'Cumulative Participant Prob.',
                      location_to_store+'in_out_degree.pdf', True)
        # plot_messages_degree(out_d, 'Out Degree', 'Cumulative Participant Prob.',
        #               location_to_store+'out_degree.pdf', True)
    print 'TADAA!!'


if __name__ == "__main__":
    main()