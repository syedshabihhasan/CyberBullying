from filterByField import filterfields
from basicInfo import privateInfo as pr
import datetime as dt
import helper as hlp
import argparse


def find_closest_message(message, ff):
    message_datetime = hlp.convert_to_date(message[pr.m_time_sent])
    next_day_datetime = message_datetime + dt.timedelta(days=1)
    messages_within_a_day = ff.filterbetweendates(message_datetime, next_day_datetime, right_equality=True)
    if 0 == len(messages_within_a_day):
        return None
    messages_to_sender = ff.filterbyequality(pr.m_target, message[pr.m_source], data=messages_within_a_day)
    messages_to_sender = ff.filterbyequality(pr.m_source, message[pr.m_target], data=messages_to_sender)
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

def find_reciprocity(labelled_data, location_to_store):
    ff = filterfields()
    ff.setdata(labelled_data)
    messages_sent_by_participants = ff.filterbyequality(pr.m_source_type, 'participant')
    reciprocity_dict = {'P': {'P': 0, 'U': 0, 'N': 0, 'X': 0},
                        'N': {'P': 0, 'U': 0, 'N': 0, 'X': 0},
                        'U': {'P': 0, 'U': 0, 'N': 0, 'X': 0}}
    n = len(messages_sent_by_participants)
    idx = 1
    message_pairs = []
    for message in messages_sent_by_participants:
        print 'at message ', idx, ' of ', n
        idx += 1
        reply_message = find_closest_message(message, ff)
        sent_message_type = message[-1]
        if reply_message is None:
            reply_message_type = 'X'
        else:
            reply_message_type = reply_message[-1]
        reciprocity_dict[sent_message_type][reply_message_type] += 1
        message_pairs.append((message, reply_message))
        if 0 == idx%500:
            print 'saving...'
            hlp.dumpvariable([idx, reciprocity_dict, message_pairs, messages_sent_by_participants],
                             'checkpoint.chp', location_to_store)
    print 'done... out of the loop'
    to_use = {'P': '+', 'N': '-', 'U': 'u', 'X': 'null'}
    for sent_type in reciprocity_dict:
        recvd_types = reciprocity_dict[sent_type]
        for recvd_type in recvd_types:
            print 'N('+to_use[recvd_type]+'|'+to_use[sent_type]+')=', recvd_types[recvd_type]

    return reciprocity_dict, message_pairs


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '-D', required=True,
                        help='labelled data from validate_balance_theory.py')
    parser.add_argument('-f', '-F', required=True,
                        help='folder to save the data in')

    args = parser.parse_args()
    data_file = args.d
    location_to_store = args.f

    all_data = hlp.recovervariable(data_file)
    labelled_data = all_data[2]
    pid_dict = all_data[3]

    reciprocity_dict, message_pairs = find_reciprocity(labelled_data, location_to_store)

    hlp.dumpvariable([reciprocity_dict, message_pairs], 'reciprocity_counts_msgPairs_overall', location_to_store)


if __name__ == "__main__":
    main()
