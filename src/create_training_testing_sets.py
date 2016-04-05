import argparse
import helper as hlp
from createweeklyinfo import weeklyinfo
from feature_extractor import raw_features
from filterByField import filterfields
from graphhelper import ghelper
from basicInfo import privateInfo as pr
from copy import deepcopy


def merge_bullying_data(bullying_overlay, pid_weekly_data, pid):
    data_with_label = {}
    if pid not in bullying_overlay:
        for week_no in pid_weekly_data:
            data_with_label[week_no] = {'data': pid_weekly_data[week_no], 'label': 'noEvent'}
    else:
        pid_bullying_info = bullying_overlay[pid]
        for week_no in pid_weekly_data:
            if not (len(pid_bullying_info[week_no]) == 0):
                data_with_label[week_no] = {'data': pid_weekly_data[week_no], 'label': 'bEvent'}
            else:
                data_with_label[week_no] = {'data': pid_weekly_data[week_no], 'label': 'noEvent'}
    return data_with_label


def flip_bullying_overlay(bullying_overlay, week_list):
    new_b_o = {}
    for pid in bullying_overlay:
        new_b_o[pid] = {}
        for week_no in week_list:
            new_b_o[pid][week_no] = []
        for category in bullying_overlay[pid]:
            weeks_with_category = bullying_overlay[pid][category]
            for week_no in weeks_with_category:
                new_b_o[pid][week_no].append(category)
    return new_b_o


def get_pid_level_features(data_to_use, weekly_info, ff, bullying_overlay, pid_dict, current_pid, fe):
    pid_weekly_data = hlp.divideintoweekly(data_to_use, weekly_info, ff)
    pid_weekly_w_bullying = merge_bullying_data(bullying_overlay, pid_weekly_data, pid_dict[current_pid])

    # get the total degree for the pid, in and out, global
    global_in_degree, global_out_degree = fe.get_week_degree(data_to_use, pid_dict[current_pid])

    # get the total incoming, and outgoing messages, global
    pid_total_incoming, pid_total_outgoing = fe.get_in_out_data(data_to_use, pid_dict[current_pid])
    global_in_ew = len(pid_total_incoming)
    global_out_ew = len(pid_total_outgoing)

    # weekly sentiment score
    weekly_sentiment_score = fe.get_sentiment_score(pid_weekly_data, pid_dict[current_pid],
                                                    separate_in_out=True)
    incoming_ss = {}
    outgoing_ss = {}
    for week_no in weekly_sentiment_score:
        incoming_ss[week_no] = weekly_sentiment_score[week_no]['In']
        outgoing_ss[week_no] = weekly_sentiment_score[week_no]['Out']
    return pid_weekly_w_bullying, global_in_degree, global_out_degree, global_in_ew, global_out_ew, incoming_ss, outgoing_ss


def get_week_features(pid_weekly_w_bullying, week_no, fe, global_in_degree, global_out_degree, global_in_ew,
                      global_out_ew,
                      incoming_ss, outgoing_ss, real_pid):
    week_in_d, week_out_d = fe.get_week_degree(pid_weekly_w_bullying[week_no]['data'],
                                               real_pid)
    week_in_m, week_out_m = fe.get_in_out_data(pid_weekly_w_bullying[week_no]['data'],
                                               real_pid)
    fr_in_degree = (week_in_d + 0.0) / global_in_degree
    fr_out_degree = (week_out_d + 0.0) / global_out_degree

    fr_in_ew = (len(week_in_m) + 0.0) / global_in_ew
    fr_out_ew = (len(week_out_m) + 0.0) / global_out_ew

    in_senti_count = fe.get_senti_dist(week_in_m)
    in_total = sum(in_senti_count) + 0.0
    fr_in_senti = [0., 0., 0.] if in_total == 0 else [in_senti_count[0] / in_total,
                                                      in_senti_count[1] / in_total,
                                                      in_senti_count[2] / in_total]

    out_senti_count = fe.get_senti_dist(week_out_m)
    out_total = sum(out_senti_count) + 0.0
    fr_out_senti = [0., 0., 0.] if out_total == 0 else [out_senti_count[0] / out_total,
                                                        out_senti_count[1] / out_total,
                                                        out_senti_count[2] / out_total]
    current_in_ss = fe.get_specific_week_ss(incoming_ss, week_no)
    current_out_ss = fe.get_specific_week_ss(outgoing_ss, week_no)

    return fr_in_degree, fr_out_degree, fr_in_ew, fr_out_ew, fr_in_senti, fr_out_senti, current_in_ss, current_out_ss


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-m', '-M', type=str, required=True,
                        help='Message list file')
    parser.add_argument('-r', '-R', type=str, required=True,
                        help='survey file')
    parser.add_argument('-p', '-P', type=str, required=True,
                        help='PID dict inverted')
    parser.add_argument('-b', '-B', type=str, required=True,
                        help='bullying dictionary')
    parser.add_argument('-o', '-O', type=str, required=True,
                        help='Output folder')
    parser.add_argument('-l', '-L', type=str, nargs='+',
                        help='Filters chosen')
    parser.add_argument('-f', '-f', type=str, nargs='+',
                        help='Filter files')

    args = parser.parse_args()

    output_folder = args.o

    message_data = hlp.recovervariable(args.m)
    pid_dict = hlp.recovervariable(args.p)

    filters_chosen = args.l
    filter_files = args.f
    catch_all_data = hlp.getfilterdata(filters_chosen, filter_files, catch_all=True)

    wi = weeklyinfo()
    weekly_info = wi.getweeklyfo(args.r)

    ff = filterfields()

    gh = ghelper()
    bullying_overlay = gh.createbullyingoverlay(catch_all_data, weekly_info, ff)
    bullying_overlay = flip_bullying_overlay(bullying_overlay, weekly_info.keys())

    pid_list = pid_dict.keys()
    pid_list.sort()
    for pid in pid_list:
        training_set_final = []
        testing_set_final = []
        pid_list_training = deepcopy(pid_list)
        pid_list_training.remove(pid)
        ff.setdata(message_data)
        testing_raw_data = ff.filterbyequality(pr.m_source, pid_dict[pid]) + \
                           ff.filterbyequality(pr.m_target, pid_dict[pid])
        ff.removebyequality(pr.m_source, pid_dict[pid])
        ff.removebyequality(pr.m_target, pid_dict[pid])
        training_raw_data = ff.getdata()
        fe = raw_features(data=None)
        _, _ = fe.get_scoring_factors(training_raw_data)

        training_weekly_data = {}

        for training_pid in pid_list_training:
            training_weekly_data[training_pid] = {}
            data_to_use = ff.filterbyequality(pr.m_source, pid_dict[training_pid]) + \
                          ff.filterbyequality(pr.m_target, pid_dict[training_pid])
            if 0 == len(data_to_use):
                print 'no data found, probably filtered into the testing set, Training PID: '+\
                      training_pid+', Testing PID: '+pid
                continue
            pid_weekly_w_bullying, global_in_degree, global_out_degree, global_in_ew, global_out_ew, incoming_ss, \
            outgoing_ss = get_pid_level_features(data_to_use, weekly_info, ff,
                                                 bullying_overlay, pid_dict,
                                                 training_pid, fe)
            for week_no in pid_weekly_w_bullying:
                fr_in_degree, fr_out_degree, fr_in_ew, \
                fr_out_ew, fr_in_senti, fr_out_senti, \
                current_in_ss, current_out_ss = get_week_features(pid_weekly_w_bullying, week_no, fe,
                                                                  global_in_degree, global_out_degree,
                                                                  global_in_ew, global_out_ew,
                                                                  incoming_ss, outgoing_ss,
                                                                  pid_dict[training_pid])
                training_set_final.append(
                        [training_pid, week_no,
                         fr_in_senti[0], fr_in_senti[1], fr_in_senti[2],
                         fr_out_senti[0], fr_out_senti[1], fr_out_senti[2],
                         fr_in_degree, fr_out_degree,
                         fr_in_ew, fr_out_ew,
                         current_in_ss, current_out_ss,
                         pid_weekly_w_bullying[week_no]['label']])

        # testing pid
        pid_weekly_w_bullying, global_in_degree, global_out_degree, \
        global_in_ew, global_out_ew, incoming_ss, outgoing_ss = get_pid_level_features(testing_raw_data, weekly_info,
                                                                                       ff, bullying_overlay, pid_dict,
                                                                                       pid, fe)
        for week_no in pid_weekly_w_bullying:
            fr_in_degree, fr_out_degree, fr_in_ew, \
            fr_out_ew, fr_in_senti, fr_out_senti, \
            current_in_ss, current_out_ss = get_week_features(pid_weekly_w_bullying, week_no, fe,
                                                              global_in_degree, global_out_degree,
                                                              global_in_ew, global_out_ew,
                                                              incoming_ss, outgoing_ss,
                                                              pid_dict[pid])
            testing_set_final.append(
                    [pid, week_no,
                     fr_in_senti[0], fr_in_senti[1], fr_in_senti[2],
                     fr_out_senti[0], fr_out_senti[1], fr_out_senti[2],
                     fr_in_degree, fr_out_degree,
                     fr_in_ew, fr_out_ew,
                     current_in_ss, current_out_ss,
                     pid_weekly_w_bullying[week_no]['label']])
        header = ['pid', 'wkno',
                  'frWInSenPos', 'frWInSenNeu', 'frWInSenNeg',
                  'frWOutSenPos', 'frWOutSenNeu', 'frWOutSenNeg',
                  'frInDegO', 'frOutDegO',
                  'frInEdgeO', 'frOutEdgeO',
                  'inSenSc', 'outSenSc',
                  'label']
        training_set_final = [header] + training_set_final
        testing_set_final = [header] + testing_set_final

        hlp.writecsv(training_set_final, output_folder+pid+'_tr.csv')
        hlp.writecsv(testing_set_final, output_folder+pid+'_ts.csv')


if __name__ == "__main__":
    main()
