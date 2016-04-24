import argparse
from basicInfo import privateInfo as pr
import helper as hlp
import numpy as np

def __generate_dict(msg_types=None):
    if msg_types is None:
        msg_types = ['fb_activity', 'fb_comment', 'fb_like',
                     'fb_message', 'sms', 'twitter_message', 'twitter_status']
    basic_dict = {}
    for msg_type in msg_types:
        basic_dict[msg_type] = {'in': [0, 0, 0],
                                'out': [0, 0, 0],
                                'ind': [set(), set()],
                                'outd': [set(), set()]}

    basic_dict['overall'] = {'in': [0, 0, 0],
                             'out': [0, 0, 0],
                             'ind': [set(), set()],
                             'outd': [set(), set()]}

    return basic_dict

def distribution_polarity(labelled_data):
    complete_in_out = {'in': [0, 0, 0], 'out': [0, 0, 0]}
    to_return = {}
    for datum in labelled_data:
        if datum[pr.m_source_type] == 'participant':
            #outgoing
            if datum[pr.m_source] not in to_return:
                to_return[datum[pr.m_source]] = __generate_dict()
            if datum[-1] == 'P':
                to_return[datum[pr.m_source]][datum[pr.m_type]]['out'][0] += 1
                to_return[datum[pr.m_source]]['overall']['out'][0] += 1
                complete_in_out['out'][0] += 1
            elif datum[-1] == 'N':
                to_return[datum[pr.m_source]][datum[pr.m_type]]['out'][1] += 1
                to_return[datum[pr.m_source]]['overall']['out'][1] += 1
                complete_in_out['out'][1] += 1
            elif datum[-1] == 'U':
                to_return[datum[pr.m_source]][datum[pr.m_type]]['out'][2] += 1
                to_return[datum[pr.m_source]]['overall']['out'][2] += 1
                complete_in_out['out'][2] += 1
            if datum[pr.m_target_type] == 'participant':
                to_return[datum[pr.m_source]][datum[pr.m_type]]['outd'][0].add(datum[pr.m_target])
                to_return[datum[pr.m_source]]['overall']['outd'][0].add(datum[pr.m_target])
            else:
                to_return[datum[pr.m_source]][datum[pr.m_type]]['outd'][1].add(datum[pr.m_target])
                to_return[datum[pr.m_source]]['overall']['outd'][1].add(datum[pr.m_target])
        if datum[pr.m_target_type] == 'participant':
            #incoming
            if datum[pr.m_target] not in to_return:
                to_return[datum[pr.m_target]] = __generate_dict()
            if datum[-1] == 'P':
                to_return[datum[pr.m_target]][datum[pr.m_type]]['in'][0] += 1
                to_return[datum[pr.m_target]]['overall']['in'][0] += 1
                complete_in_out['in'][0] += 1
            elif datum[-1] == 'N':
                to_return[datum[pr.m_target]][datum[pr.m_type]]['in'][1] += 1
                to_return[datum[pr.m_target]]['overall']['in'][1] += 1
                complete_in_out['in'][1] += 1
            elif datum[-1] == 'U':
                to_return[datum[pr.m_target]][datum[pr.m_type]]['in'][2] += 1
                to_return[datum[pr.m_target]]['overall']['in'][2] += 1
                complete_in_out['in'][2] += 1
            if datum[pr.m_source_type] == 'participant':
                to_return[datum[pr.m_target]][datum[pr.m_type]]['ind'][0].add(datum[pr.m_source])
                to_return[datum[pr.m_target]]['overall']['ind'][0].add(datum[pr.m_source])
            else:
                to_return[datum[pr.m_target]][datum[pr.m_type]]['ind'][1].add(datum[pr.m_source])
                to_return[datum[pr.m_target]]['overall']['ind'][1].add(datum[pr.m_source])
    return to_return, complete_in_out

def __summarize_data(data_dict):
    incoming_polarity = data_dict['in']
    outgoing_polarity = data_dict['out']

    indegree_participant = len(data_dict['ind'][0])
    indegree_nonparticipant = len(data_dict['ind'][1])
    outdegree_participant = len(data_dict['outd'][0])
    outdegree_nonparticipant = len(data_dict['outd'][1])

    csv_line = []
    csv_line.extend(incoming_polarity)
    csv_line.extend(outgoing_polarity)
    csv_line.append(indegree_participant)
    csv_line.append(indegree_nonparticipant)
    csv_line.append(outdegree_participant)
    csv_line.append(outdegree_nonparticipant)

    return csv_line


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '-D', required=True,
                        help='labelled csv')
    parser.add_argument('-f', '-F', required=True,
                        help='folder to save the data in')
    args = parser.parse_args()
    data_file = args.d
    location_to_store = args.f

    all_afinn_data = hlp.readcsv(data_file)
    labelled_data = hlp.processafinnsentiment(all_afinn_data)
    csv_header = ['pid', 'm_type',
                  'in_pos', 'in_neg', 'in_neu',
                  'out_pos', 'out_neg', 'out_neu',
                  'in_deg_part', 'in_deg_nonpart',
                  'out_deg_part', 'out_deg_nonpart']

    pol_dist, complete_in_out = distribution_polarity(labelled_data)
    print '***For Complete Dataset***'
    print 'Incoming(P, N, U): ', complete_in_out['in']
    print 'Outgoing(P, N, U): ', complete_in_out['out']
    hlp.dumpvariable([pol_dist, complete_in_out], 'polarity_in_out.dict', location_to_store)

    to_store_csv = [csv_header]

    for pid in pol_dist:
        pid_data = pol_dist[pid]
        for m_type in pid_data:
            m_data = pid_data[m_type]
            csv_line = __summarize_data(m_data)
            final_csv_line = [pid, m_type]
            final_csv_line.extend(csv_line)
            to_store_csv.append(final_csv_line)
    hlp.writecsv(to_store_csv, location_to_store+'polarity_in_out.csv')

if __name__ == "__main__":
    main()