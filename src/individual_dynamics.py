import argparse
import helper as hlp
from filterByField import filterfields
from basicInfo import privateInfo as pr
import datetime as dt
from createweeklyinfo import weeklyinfo


def get_reci_probability(rec_dict, produce_csv=False):
    withNull = ''
    withoutNull = ''
    csv_toWrite = []
    for sent_type in rec_dict:
        total_with_null = sum(rec_dict[sent_type].values())
        total_without_null = total_with_null - rec_dict[sent_type]['X']
        for recv_type in rec_dict[sent_type]:
            if total_with_null == 0:
                wn = 0.0
            else:
                wn = (rec_dict[sent_type][recv_type] + 0.0) / total_with_null
            if total_without_null == 0:
                wo_n = 0.0
            else:
                wo_n = (rec_dict[sent_type][recv_type] + 0.0) / total_without_null
            withNull += 'Pr(' + recv_type + '|' + sent_type + ') = ' + str(wn) + \
                        '(' + str(rec_dict[sent_type][recv_type]) + ')' + '\n'
            withoutNull += 'Pr(' + recv_type + '|' + sent_type + ') = ' + str(wo_n) + \
                           '(' + str(rec_dict[sent_type][recv_type]) + ')' + '\n' if not (
            recv_type == 'X') else 'null\n'
            csv_toWrite.append(str(wn) + '(' + str(rec_dict[sent_type][recv_type]) + ')')
    print 'With Null'
    print withNull
    print '***'
    print 'Without Null'
    print withoutNull
    if produce_csv:
        return csv_toWrite


def find_closest_message(message, message_to_participant, ff):
    message_datetime = hlp.convert_to_date(message[pr.m_time_sent])
    next_day_datetime = message_datetime + dt.timedelta(days=1)
    messages_within_a_day = ff.filterbetweendates(message_datetime, next_day_datetime,
                                                  data_to_work=message_to_participant, right_equality=True)
    if 0 == len(messages_within_a_day):
        return None
    messages_to_sender = ff.filterbyequality(pr.m_source, message[pr.m_target], data=messages_within_a_day)
    if 0 == len(messages_to_sender):
        return None
    time_diff = None
    message_to_consider = None
    first_iter = True
    for reply_message in messages_to_sender:
        reply_message_dt = hlp.convert_to_date(reply_message[pr.m_time_sent])
        if first_iter:
            first_iter = False
            time_diff = reply_message_dt - message_datetime
            message_to_consider = reply_message
        else:
            current_time_diff = reply_message_dt - message_datetime
            if current_time_diff < time_diff:
                time_diff = current_time_diff
                message_to_consider = reply_message
    return message_to_consider


def __basic_reciprocity_dict():
    reciprocity_dict = {'P': {'P': 0, 'U': 0, 'N': 0, 'X': 0},
                        'N': {'P': 0, 'U': 0, 'N': 0, 'X': 0},
                        'U': {'P': 0, 'U': 0, 'N': 0, 'X': 0}}
    return reciprocity_dict


def __get_polarity_composition(messages, pid):
    polarity = {}
    src_new = pid
    for message in messages:
        trg_new = message[pr.m_target] if not message[pr.m_target] == pid else message[pr.m_source]
        if (src_new, trg_new) not in polarity:
            polarity[(src_new, trg_new)] = [0, 0, 0]
        if 'P' == message[-1]:
            polarity[(src_new, trg_new)][0] += 1
        elif 'N' == message[-1]:
            polarity[(src_new, trg_new)][1] += 1
        elif 'U' == message[-1]:
            polarity[(src_new, trg_new)][2] += 1
    return polarity


def individual_reciprocity_analysis(labelled_data, pid_dict, location_to_store):
    reciprocity_info = {}
    ff = filterfields()
    ff.setdata(labelled_data)
    polarity_data = {}
    for pid in pid_dict:
        print 'Working with PID: ', pid, '(', pid_dict[pid], ')'
        messages_by_participant = ff.filterbyequality(pr.m_source, pid)
        messages_to_participant = ff.filterbyequality(pr.m_target, pid)
        polarity_data[pid] = __get_polarity_composition(messages_by_participant+messages_to_participant, pid)
        reciprocity_info[pid] = {}
        n = len(messages_by_participant)
        idx = 0
        for message in messages_by_participant:
            print 'idx=' + str(idx) + '/' + str(n)
            idx += 1
            closest_message = find_closest_message(message, messages_to_participant, ff)
            target_type = 'P' if message[pr.m_target_type] == 'participant' else 'NP'
            target = message[pr.m_target]
            if target_type not in reciprocity_info[pid]:
                reciprocity_info[pid][target_type] = {}
            if target not in reciprocity_info[pid][target_type]:
                reciprocity_info[pid][target_type][target] = __basic_reciprocity_dict()
            sent_message_type = message[-1]
            reply_message_type = 'X' if closest_message is None else closest_message[-1]
            reciprocity_info[pid][target_type][target][sent_message_type][reply_message_type] += 1
        print 'saving checkpoint...'
        hlp.dumpvariable([reciprocity_info, pid, pid_dict], 'checkpoint.chp', location_to_store)
        print 'saved!'
    return reciprocity_info, polarity_data


def analyze_info(reciprocity_dict, pid_dict, location_to_store, filename):
    final_csv_data = []
    for pid in reciprocity_dict:
        pid_new = hlp.getpid(pid_dict, pid)
        print '**** For PID: P' + str(pid_new) + ' ****'
        pid_data = reciprocity_dict[pid]
        for target_type in pid_data:
            target_data = pid_data[target_type]
            for target_pid in target_data:
                target_pid_new = hlp.getpid(pid_dict, target_pid)
                print 'P' + str(pid_new) + '-' + target_type + str(target_pid_new)
                temp = get_reci_probability(target_data[target_pid], True)
                starting_data = ['P' + str(pid_new), target_type + str(target_pid_new)]
                starting_data.extend(temp)
                final_csv_data.append(starting_data)
    header = ['source', 'target',
              'Pr(+|+)', 'Pr(-|+)', 'Pr(U|+)', 'Pr(X|+)',
              'Pr(+|U)', 'Pr(-|U)', 'Pr(U|U)', 'Pr(X|U)',
              'Pr(+|-)', 'Pr(-|-)', 'Pr(U|-)', 'Pr(X|-)']
    toWrite = [header] + final_csv_data
    hlp.writecsv(toWrite, location_to_store + filename, delimiter_sym=',')


def analyze_polarity(polarity_dict, pid_dict, location_to_store, filename):
    final_csv_data = [['source', 'target', 'Pos', 'Neg', 'Neu']]
    print '++++ POLARITY INFORMATION ++++'
    type_abr = {'participants': 'P', 'nonparticipants':'NP'}
    for pid in polarity_dict:
        src_new = hlp.getpid(pid_dict, pid)
        print '**** For PID: P' + str(src_new) + ' ****'
        for (src, trg) in polarity_dict[pid]:
            trg_new, trg_type = hlp.getpid(pid_dict, trg, return_p_type=True)
            print '(P'+str(src_new)+','+ type_abr[trg_type]+str(trg_new)+')'
            temp = ['P'+str(src_new), type_abr[trg_type]+str(trg_new)]
            for polarity in polarity_dict[pid][(src, trg)]:
                temp.append(polarity)
            final_csv_data.append(temp)
    hlp.writecsv(final_csv_data, location_to_store+filename, delimiter_sym=',')


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '-D', required=True,
                        help='labelled data from validate_balance_theory.py')
    parser.add_argument('-f', '-F', required=True,
                        help='folder to save the data in')
    parser.add_argument('-w', '-W', required=False,
                        help='survey file for weekly data processing')

    args = parser.parse_args()
    data_file = args.d
    location_to_store = args.f
    weekly_surveys = args.w

    all_data = hlp.recovervariable(data_file)
    labelled_data = all_data[2]
    pid_dict = all_data[3]
    if weekly_surveys is None:
        reciprocity_info, polarity_info = individual_reciprocity_analysis(labelled_data, pid_dict['participants'],
                                                                          location_to_store)
        analyze_info(reciprocity_info, pid_dict, location_to_store, 'pr_overall.csv')
        analyze_polarity(polarity_info, pid_dict, location_to_store, 'polarity_overall.csv')
        hlp.dumpvariable([reciprocity_info, labelled_data, pid_dict, polarity_info],
                         'reciprocity_info_overall.dict', location_to_store)
    else:
        # working with bimonthly data
        months2 = [[1, 2, 3, 4, 5, 6, 7, 8],
                   [9, 10, 11, 12, 13, 14, 15, 16],
                   [17, 18, 19, 20, 21, 22, 23, 24, 25]]
        wi = weeklyinfo()
        weekly_info = wi.getweeklyfo(weekly_surveys)
        ff = filterfields()
        weekly_data = hlp.divideintoweekly(labelled_data, weekly_info, ff)
        idx = 1
        for bi_month in months2:
            print 'For weeks: ', bi_month
            bi_month_data = []
            for weekno in bi_month:
                bi_month_data.extend(weekly_data[weekno])
            reciprocity_info, polarity_info = individual_reciprocity_analysis(bi_month_data, pid_dict['participants'],
                                                                              location_to_store)
            analyze_info(reciprocity_info, pid_dict, location_to_store, 'pr_bimonthly_'+str(idx)+'.csv')
            analyze_polarity(polarity_info, pid_dict, location_to_store, 'polarity_bimonthly_'+str(idx)+'.csv')
            hlp.dumpvariable([reciprocity_info, labelled_data, pid_dict, polarity_info],
                             'reciprocity_info_bimonthly_'+str(idx)+'.csv', location_to_store)
            idx += 1

    print 'tadaa!'


if __name__ == "__main__":
    main()
