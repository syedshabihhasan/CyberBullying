import argparse
import helper as hlp
from basicInfo import privateInfo as pr
from basicInfo import plottingdetails as pld
from vaderpolarity import vadersenti
from filterByField import filterfields
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

def invertdict(dict_to_invert):
    return {v: k for k,v in dict_to_invert.iteritems()}

def separatesentiment(pid, pid_data, output_count=False):
    pos_senti = []
    neu_senti = []
    neg_senti = []

    senti_count = [0, 0, 0] if output_count else None

    for datum in pid_data:
        if not output_count:
            pos_senti.append(datum[pr.m_pos])
            neu_senti.append(datum[pr.m_neu])
            neg_senti.append(datum[pr.m_neg])
        else:
            if datum[pr.m_pos] > datum[pr.m_neu]:
                if datum[pr.m_pos] > datum[pr.m_neg]:
                    senti_count[0] += 1
                else:
                    senti_count[2] += 1
            else:
                if datum[pr.m_neu] > datum[pr.m_neg]:
                    senti_count[1] += 1
                else:
                    senti_count[2] += 1

    if output_count:
        return senti_count
    else:
        return pos_senti, neu_senti, neg_senti

def converttableaucolor(color_v):
    n_color_v = [0, 0, 0]
    for idx in range(3):
        n_color_v[idx] = color_v[idx]/255.
    return n_color_v

def setboxcolors(color_v, box_obj):
    to_change = ['boxes', 'whiskers', 'caps', 'fliers', 'medians']
    for chng in to_change:
        plt.setp(box_obj[chng], color=color_v)
        if chng == 'boxes':
            plt.setp(box_obj[chng], linewidth=1)
    return box_obj

def plotbar(pid_list, pos_senti, neu_senti, neg_senti, location_to_store,
            upper_lim=[6000, 18000], lower_lim=[0, 3000], upper_skip=2000, lower_skip=200):
    fig, (ax_upper, ax_lower) = plt.subplots(2,1, sharex=True)
    ind = np.arange(len(pid_list)) * 2
    xtick_position = ind + 0.45
    width = 0.3

    pos_color = converttableaucolor(pld.tableau20[0])
    neu_color = converttableaucolor(pld.tableau20[2])
    neg_color = converttableaucolor(pld.tableau20[4])

    ax_upper.bar(ind, pos_senti, width=width, color=pos_color)
    ax_lower.bar(ind, pos_senti, width=width, color=pos_color)
    ax_upper.bar(ind+0.3, neu_senti, width=width, color=neu_color)
    ax_lower.bar(ind+0.3, neu_senti, width=width, color=neu_color)
    ax_upper.bar(ind+0.6, neg_senti, width=width, color=neg_color)
    ax_lower.bar(ind+0.6, neg_senti, width=width, color=neg_color)

    ax_upper.set_ylim(upper_lim[0], upper_lim[1])
    ax_lower.set_ylim(lower_lim[0], lower_lim[1])

    ax_upper.spines['bottom'].set_visible(False)
    ax_lower.spines['top'].set_visible(False)

    ax_upper.xaxis.tick_top()
    ax_upper.tick_params(labeltop='off')
    ax_lower.xaxis.tick_bottom()

    ax_upper.legend(['Positive', 'Neutral', 'Negative'], loc=9, mode='expand', ncol=3, bbox_to_anchor=(0., 1.05, 1., .102))
    plt.xticks(xtick_position, pid_list, fontsize=8, rotation='vertical')
    plt.xlabel('Participant ID')
    plt.ylabel('# of Messages')

    ax_upper.set_yticks(range(upper_lim[0], upper_lim[1], upper_skip))
    ax_lower.set_yticks(range(lower_lim[0], lower_lim[1]+100, lower_skip))

    ax_upper.yaxis.grid(True)
    ax_lower.yaxis.grid(True)
    plt.savefig(location_to_store)


def plotbox(pid_list, pos_senti, neu_senti, neg_senti, location_to_store):
    pos_labels = ['' for d in pos_senti]
    pos_labels[0] = 'Positive'
    neu_labels = ['' for d in neu_senti]
    neu_labels[0] = 'Neutral'
    neg_labels = ['' for d in neg_senti]
    neg_labels[0] = 'Negative'

    fig, ax = plt.subplots()
    ind = np.arange(len(pid_list)) * 6
    xtick_positions = ind + 3
    width = 0.5
    pos_color = converttableaucolor(pld.tableau20[0])
    neu_color = converttableaucolor(pld.tableau20[2])
    neg_color = converttableaucolor(pld.tableau20[4])

    pos_plot = plt.boxplot(pos_senti, positions=ind+1, widths=width,
                           whiskerprops={'linestyle':'-', 'linewidth':1})
    pos_plot = setboxcolors(pos_color, pos_plot)

    neu_plot = plt.boxplot(neu_senti, positions=ind+2.5, widths=width,
                           whiskerprops={'linestyle':'-', 'linewidth':1})
    neu_plot = setboxcolors(neu_color, neu_plot)

    neg_plot = plt.boxplot(neg_senti, positions=ind+4, widths=width,
                           whiskerprops={'linestyle':'-', 'linewidth':1})
    neg_plot = setboxcolors(neg_color, neg_plot)

    h1 = plt.plot([0,0], color=pos_color, linestyle='-', label='Positive')
    h2 = plt.plot([0,0], color=neu_color, linestyle='-', label='Neutral')
    h3 = plt.plot([0,0], color=neg_color, linestyle='-', label='Negative')

    plt.legend(loc=9, mode='expand', ncol=3, bbox_to_anchor=(0., 1.02, 1., .102))
    plt.xlabel('Participant ID', fontsize=20)
    plt.ylabel('Sentiment', fontsize=20)
    plt.xlim(xmin=-1)
    plt.xticks(xtick_positions, pid_list, rotation='vertical', fontsize=8)
    # plt.yticks(range(0, 1.1, 0.1))
    plt.ylim((-0.01, 1.01))
    ax.yaxis.grid(True)
    plt.savefig(location_to_store)
    # plt.show()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-m', '-M', type=str, required=True,
                        help='message list file used in participantbar')
    parser.add_argument('-p', '-P', type=str, required=True,
                        help='PID dict from participantbar')
    parser.add_argument('-mt', '-MT', type=str,
                        help='specific message type to generate the stats about')
    parser.add_argument('-o', '-O', type=str, required=True,
                        help='Output folder')
    parser.add_argument('-of', '-OF', type=str, required=True,
                        help='Output file')

    args = parser.parse_args()

    message_data = hlp.recovervariable(args.m)
    pid_dict = hlp.recovervariable(args.p)
    output_folder = args.o
    output_file = args.of

    ff = filterfields()

    senti = vadersenti(message_data)
    ff.setdata(senti.compilesentiment(field_no=pr.m_content, separate_sentiment_list=False))
    participant_dict = invertdict(pid_dict[pr.participant['all']])
    participant_list = participant_dict.keys()
    participant_list.sort()

    #overall
    pos_senti = []
    neu_senti = []
    neg_senti = []
    pos_count = []
    neu_count = []
    neg_count = []

    for pid in participant_list:
        pid_data = ff.filterbyequality(pr.m_source, participant_dict[pid]) + \
                   ff.filterbyequality(pr.m_target, participant_dict[pid])
        p, u, n = separatesentiment(pid, pid_data)
        counts = separatesentiment(pid, pid_data, output_count=True)
        pos_senti.append(p)
        neu_senti.append(u)
        neg_senti.append(n)
        pos_count.append(counts[0])
        neu_count.append(counts[1])
        neg_count.append(counts[2])

    plotbox(participant_list, pos_senti, neu_senti, neg_senti, output_folder+'box_'+output_file)
    plotbar(participant_list, pos_count, neu_count, neg_count, output_folder+'bar_'+output_file)

    in_neg_count = None
    out_neg_count = None

    #outgoing
    pos_senti = []
    neu_senti = []
    neg_senti = []
    pos_count = []
    neu_count = []
    neg_count = []

    for pid in participant_list:
        pid_data = ff.filterbyequality(pr.m_source, participant_dict[pid])
        p, u, n = separatesentiment(pid, pid_data)
        counts = separatesentiment(pid, pid_data, output_count=True)
        pos_senti.append(p)
        neu_senti.append(u)
        neg_senti.append(n)
        pos_count.append(counts[0])
        neu_count.append(counts[1])
        neg_count.append(counts[2])

    out_neg_count = neg_count
    plotbox(participant_list, pos_senti, neu_senti, neg_senti, output_folder+'out_box_'+output_file)
    plotbar(participant_list, pos_count, neu_count, neg_count, output_folder+'out_bar_'+output_file,
            [2500, 10000], [0, 1600], 1000, 100)

    #incoming
    pos_senti = []
    neu_senti = []
    neg_senti = []
    pos_count = []
    neu_count = []
    neg_count = []

    for pid in participant_list:
        pid_data = ff.filterbyequality(pr.m_target, participant_dict[pid])
        p, u, n = separatesentiment(pid, pid_data)
        counts = separatesentiment(pid, pid_data, output_count=True)
        pos_senti.append(p)
        neu_senti.append(u)
        neg_senti.append(n)
        pos_count.append(counts[0])
        neu_count.append(counts[1])
        neg_count.append(counts[2])

    in_neg_count = neg_count

    for idx in range(len(in_neg_count)):
        total_neg = in_neg_count[idx]+out_neg_count[idx]+0.0
        in_neg_count[idx] /= total_neg
        out_neg_count[idx] /= total_neg

    t, p = stats.ttest_rel(in_neg_count, out_neg_count)
    w, p_w = stats.wilcoxon(in_neg_count, out_neg_count)

    plotbox(participant_list, pos_senti, neu_senti, neg_senti, output_folder+'in_box_'+output_file)
    plotbar(participant_list, pos_count, neu_count, neg_count, output_folder+'in_bar_'+output_file, [3000, 8000],
            [0, 1300], 1000, 100)

    hlp.dumpvariable({'pos': pos_senti, 'neg': neg_senti, 'neu': neu_senti},
                     'senti_vals.dict', output_folder)
    hlp.dumpvariable({'pos': pos_count, 'neg': neg_count, 'neu': neu_count},
                     'count_senti.dict', output_folder)
    hlp.dumpvariable(participant_dict, 'inverted_pid_dict.dict', output_folder)
    hlp.dumpvariable(ff.getdata(), 'messageData_senti.list', output_folder)

    print t, p
    print w, p_w


if __name__ == "__main__":
    main()