import argparse
import matplotlib.pyplot as plt
import helper as hlp
from basicInfo import privateInfo as pr
from filterByField import filterfields
from createweeklyinfo import weeklyinfo


def __get_weekly_counts(dataset, field_to_search, to_equate, weekly_info, ff_obj, sorted_week_list, pid_hash):
    out_in = ff_obj.filterbyequality(field_to_search, pid_hash, data=dataset)
    per_week = hlp.divideintoweekly(out_in, weekly_info, ff_obj)
    weekly_counts = [len(per_week[x]) for x in sorted_week_list]
    return weekly_counts, out_in, per_week


def get_message_counts(old_dataset, new_dataset, sorted_week_list, weekly_info, hash_to_pid_dict, ff_obj,
                       location_to_store):
    in_out_message_dict = {}
    for pid_hash in hash_to_pid_dict:
        old_pid_out_week_counts, old_out, old_out_week = __get_weekly_counts(old_dataset, pr.m_source, pid_hash,
                                                                             weekly_info, ff_obj, sorted_week_list,
                                                                             pid_hash)
        old_pid_in_weeks_counts, old_in, old_in_week = __get_weekly_counts(old_dataset, pr.m_target, pid_hash,
                                                                           weekly_info, ff_obj, sorted_week_list,
                                                                           pid_hash)
        new_pid_out_weeks_counts, new_out, new_out_week = __get_weekly_counts(new_dataset, pr.m_source, pid_hash,
                                                                              weekly_info, ff_obj,sorted_week_list,
                                                                              pid_hash)
        new_pid_in_weeks_counts, new_in, new_in_week = __get_weekly_counts(new_dataset, pr.m_target, pid_hash,
                                                                           weekly_info, ff_obj, sorted_week_list,
                                                                           pid_hash)
        in_out_message_dict[hash_to_pid_dict[pid_hash]] = [[old_pid_in_weeks_counts, old_pid_out_week_counts],
                                                           [new_pid_in_weeks_counts, new_pid_out_weeks_counts]]
        hlp.dumpvariable([old_out, old_out_week, old_in, old_in_week, new_out, new_out_week, new_in, new_in_week],
                         hash_to_pid_dict[pid_hash]+'.data', location_to_store)
    return in_out_message_dict


def plot_distribution(old_in, old_out, new_in, new_out, xticks, title, location_to_store):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax_in = fig.add_subplot(211)
    ax_out = fig.add_subplot(212)

    ax.spines['top'].set_color('none')
    ax.spines['bottom'].set_color('none')
    ax.spines['left'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.tick_params(labelcolor='w', top='off', bottom='off', left='off', right='off')

    ax_in.plot(xticks, old_in, 'ro-', linewidth=2, label='Old', markersize=5, markeredgecolor='k', markerfacecolor='r',
               markeredgewidth=2)
    ax_in.plot(xticks, new_in, 'bo-', linewidth=2, label='New', markersize=5, markeredgecolor='k', markerfacecolor='b',
               markeredgewidth=2)
    ax_in.set_title('Incoming Messages('+str(title)+')')
    ax_in.legend(loc=1)
    ax_in.grid(True)

    ax_out.plot(xticks, old_out, 'ro-', linewidth=2, label='Old', markersize=5, markeredgecolor='k', markerfacecolor='r'
                , markeredgewidth=2)
    ax_out.plot(xticks, new_out, 'bo-', linewidth=2, label='New', markersize=5, markeredgecolor='k', markerfacecolor='b'
                , markeredgewidth=2)
    ax_out.set_title('Outgoing Messages('+str(title)+')')
    ax_out.grid(True)

    ax.set_xlabel('Week #', fontsize=20)
    ax.set_ylabel('# of Messages', fontsize=20)

    plt.savefig(location_to_store+str(title)+'.pdf')


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-o', '-O', required=True, help='Old dataset csv')
    parser.add_argument('-n', '-N', required=True, help='New dataset csv')
    parser.add_argument('-s', '-S', required=True, help='Survey file')
    parser.add_argument('-p', '-P', required=True, help='folder to store figures in, should end with /')
    parser.add_argument('-m', '-M', required=True, help='Master hash mapping csv')
    parser.add_argument('-mt', '-MT', required=True, nargs='+', help='Types of messages to look for')

    args = parser.parse_args()

    old_dataset_file = args.o
    new_dataset_file = args.n
    survey_file = args.s
    location_to_store = args.p
    master_hash_csv = args.m
    message_types = args.mt

    print 'Reading data...'
    master_csv = hlp.readcsv(master_hash_csv, delimiter_sym=',', remove_first=True)
    master_dict = {datum[1]: datum[0] for datum in master_csv}

    ff = filterfields()

    filtered_old = []
    filtered_new = []

    old_dataset = hlp.readcsv(old_dataset_file, delimiter_sym=',', remove_first=True)
    new_dataset = hlp.readcsv(new_dataset_file, delimiter_sym=',', remove_first=True)

    print 'Filtering message types'
    for message_type in message_types:
        filtered_old.extend(ff.filterbyequality(pr.m_type, message_type, data=old_dataset))
        filtered_new.extend(ff.filterbyequality(pr.m_type, message_type, data=new_dataset))

    wi = weeklyinfo()
    weekly_info = wi.getweeklyfo(survey_file)
    week_list = weekly_info.keys()
    week_list.sort()

    print 'Creating in out dictionary'
    in_out_message_dict = get_message_counts(filtered_old, filtered_new, week_list, weekly_info, master_dict, ff,
                                             location_to_store)

    print 'Plotting...'
    for pid in in_out_message_dict:
        print pid
        plot_distribution(in_out_message_dict[pid][0][0], in_out_message_dict[pid][0][1],
                          in_out_message_dict[pid][1][0], in_out_message_dict[pid][1][1], week_list, pid,
                          location_to_store)
    print 'TADAA!!'

if __name__ == "__main__":
    main()
