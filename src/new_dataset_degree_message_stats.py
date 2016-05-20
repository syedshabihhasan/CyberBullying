import argparse
import helper as hlp
import validate_balance_theory as vbt
from filterByField import filterfields
from basicInfo import new_dataset as nd
from basicInfo import privateInfo as pr


def get_degree_message_count(dataset, pid_dict):
    ff = filterfields()
    ff.setdata(dataset)
    in_d = {}
    out_d = {}
    in_m = {}
    out_m = {}

    for pid in pid_dict:
        incoming_messages = ff.filterbyequality(nd.m_target, pid)
        outgoing_messages = ff.filterbyequality(nd.m_source, pid)
        people_sending_me_messages = ff.getuniqueelements(nd.m_source, data=incoming_messages)
        people_i_am_sending_messages = ff.getuniqueelements(nd.m_target, data=outgoing_messages)
        in_m[pid] = len(incoming_messages)
        out_m[pid] = len(outgoing_messages)
        in_d[pid] = len(people_sending_me_messages)
        out_d[pid] = len(people_i_am_sending_messages)

    return in_m, out_m, in_d, out_d


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '-D', required=True, help='the dataset')
    parser.add_argument('-m', '-M', required=True, help='mapping of the hashes')
    parser.add_argument('-f', '-F', required=True, help='folder to store the output in')
    parser.add_argument('-o', '-O', action='store_true', help='flag to indicate that we have the old dataset')

    args = parser.parse_args()

    dataset_file = args.d
    mapping_hash_file = args.m
    location_to_store = args.f
    #TODO: integrate the old dataset processing
    is_old = args.o

    new_dataset = hlp.readcsv(dataset_file, delimiter_sym=',', remove_first=True)
    mapping_hash = hlp.readcsv(mapping_hash_file, delimiter_sym=',', remove_first=True)

    pid_dict = {datum[1]: datum[0] for datum in mapping_hash}

    in_m, out_m, in_d, out_d = get_degree_message_count(new_dataset, pid_dict)
    vbt.plot_messages_degree([in_m.values(), out_m.values()], '# of Messages', 'Cumulative Participant Prob.',
                      location_to_store+'in_out_messages.pdf')
    vbt.plot_messages_degree([in_d.values(), out_d.values()], 'Degree', 'Cumulative Participant Prob.',
                      location_to_store+'in_out_degree.pdf', True)

if __name__ == "__main__":
    main()