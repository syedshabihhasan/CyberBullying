import argparse
import sys
import helper as hlp

from basicInfo import privateInfo as pr

def getspecificdata(data, pid, week_id, separate_in_out):
    week_data = None
    try:
        week_data = data[pid][week_id]
        if separate_in_out:
            to_return = {'In': [], 'Out': []}
            for datum in week_data:
                if pid in datum[pr.m_source]:
                    to_return['Out'].append(datum)
                if pid in datum[pr.m_target]:
                    to_return['In'].append(datum)
            week_data = to_return
    except:
        print 'there was some error dealing with PID: ' + str(pid)+ ' , and week_no: '+str(week_id) + ', just skipping'
        print sys.exc_info()[0]
    return week_data

def ghostprint(data):
    temp_data = {}
    for datum in data:
        temp_data[datum[pr.msg_id]] = datum
    msg_id = temp_data.keys()
    msg_id.sort()
    for m_id in msg_id:
        datum = temp_data[m_id]
        print ''.join(str(x)+',' for x in datum)


def printmessages(data, separate_in_out, show_in_out=None):
    if separate_in_out:
        if show_in_out is None:
            print 'Incoming messages'
            ghostprint(data['In'])
            print 'Outgoing messages'
            ghostprint(data['Out'])
        elif show_in_out.lower() == 'in':
            print 'Incoming messages'
            ghostprint(data['In'])
        elif show_in_out.lower() == 'out':
            print 'Outgoing messages'
            ghostprint(data['Out'])
    else:
        ghostprint(data)

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '-F', type=str, required=True,
                        help='weekly dict')
    parser.add_argument('-p', '-P', type=str, required=True,
                        help='pid')
    parser.add_argument('-w', '-W', type=int, nargs='+',
                        help='list of weeks')
    parser.add_argument('-o', '-O', type=str,
                        help='folder to store the output')
    parser.add_argument('-s', '-S', action='store_true',
                        help='separate out the incoming and outgoing messages')
    parser.add_argument('-io', type=str)

    args = parser.parse_args()
    week_dict_file = args.f
    pid = args.p
    weeks = args.w
    location_to_store = args.o
    separate_in_out = args.s
    show_in_out = args.io

    week_data_dict = hlp.recovervariable(week_dict_file)
    participant_data = {pid: {}}
    for week_no in weeks:
        reduced_data = getspecificdata(week_data_dict, pid, week_no, separate_in_out)
        if reduced_data is None:
            print 'No data found, or some error occurred...'
            continue
        else:
            participant_data[pid] = reduced_data
            print '\n\n\n\n\nData summary for PID:', pid, ' week_no: ', week_no
            printmessages(reduced_data, separate_in_out, show_in_out)
    if location_to_store is not None:
        hlp.dumpvariable(participant_data, pid+'.data', location_to_store)

if __name__ == "__main__":
    main()