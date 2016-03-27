from __future__ import division
import argparse
import helper as hlp
import numpy as np

def flipdict(missing_week_dict):
    flipped_dict = {}
    for week_no in missing_week_dict.keys():
        incoming = missing_week_dict[week_no]['In']
        outgoing = missing_week_dict[week_no]['Out']
        for pid in incoming:
            if pid not in flipped_dict:
                flipped_dict[pid] = [-1, -1]
            flipped_dict[pid][0] = week_no
        for pid in outgoing:
            if pid not in flipped_dict:
                flipped_dict[pid] = [-1, -1]
            flipped_dict[pid][1] = week_no
    return flipped_dict

def printsummary(data_dict, tag_line, total_participants, per_week_msgs):
    print '***Summary starts***'
    print 'IN per week: Avg=', np.mean(per_week_msgs['In']), ' Median', np.median(per_week_msgs['In']), \
        ' Standard dev: ', np.std(per_week_msgs['In']), \
        ' Min:', min(per_week_msgs['In']), ' Max: ', max(per_week_msgs['In'])
    print 'OUT per week: Avg=', np.mean(per_week_msgs['Out']), ' Median', np.median(per_week_msgs['Out']), \
        ' Standard dev: ', np.std(per_week_msgs['Out']), \
        'Min: ', min(per_week_msgs['Out']), ' Max: ', max(per_week_msgs['Out'])
    print 'total # of participants: ', total_participants
    print tag_line
    week_list = data_dict.keys()
    week_list.sort()
    for week in week_list:
        in_per = 100.0*(len(data_dict[week]['In'])/total_participants)
        out_per = 100.0*(len(data_dict[week]['Out'])/total_participants)
        print '++++++'
        print week, ' weeks',\
            ' In: ', len(data_dict[week]['In']), '(', in_per, '%)', \
            ' Out: ', len(data_dict[week]['Out']), '(', out_per, '%)'
        print 'IN List', data_dict[week]['In']
        print 'OUT List', data_dict[week]['Out']
    print '***Summary ends***'

def main():
    parser = argparse.ArgumentParser('Script to generate statistics about message types')

    # add arguments
    parser.add_argument('-d', '-D', type=str, required=True,
                        help='location of file to work with')
    parser.add_argument('-s', '-S', type=str, required=True,
                        help='folder to store the results, ending with /')
    parser.add_argument('-f', '-F', type=str, required=True,
                        help='filename to store data in')
    parser.add_argument('-w', '-W', type=int, default=0,
                        help='what threshold to classify missing, default 0, Integer value needed')

    # get arguments
    args = parser.parse_args()
    filename = args.d
    threshold_missing = args.w
    location_to_store = args.s
    filepath = args.f

    data = hlp.recovervariable(filename)

    missing_week_dict, per_week_msgs = hlp.missingweeks(data, threshold_value=threshold_missing)
    flipped_dict = flipdict(missing_week_dict)
    printsummary(missing_week_dict, 'No. of participants with less than '+
                 str(threshold_missing)+' data points in ', len(data.keys()), per_week_msgs)
    hlp.dumpvariable(missing_week_dict, filepath, location_to_store)
    hlp.dumpvariable(flipped_dict, 'flipped_'+filepath, location_to_store)
if __name__ == "__main__":
    main()