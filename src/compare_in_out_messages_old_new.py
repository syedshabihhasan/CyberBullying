import argparse
import matplotlib.pyplot as plt
import helper as hlp
from basicInfo import privateInfo as pr
from filterByField import filterfields
from createweeklyinfo import weeklyinfo


def __old_new_compare(old_data, new_data):
    new_data_dict = {}
    for datum in new_data:
        src = datum[pr.m_source]
        dst = datum[pr.m_target]
        message_type = datum[pr.m_type]
        timestamp = datum[pr.m_time_sent]
        message = datum[pr.m_content]
        if message_type not in new_data_dict:
            new_data_dict[message_type] = {}
        if (src, dst) not in new_data_dict[message_type]:
            new_data_dict[message_type][(src, dst)] = {}
        if timestamp not in new_data_dict[message_type][(src, dst)]:
            new_data_dict[message_type][(src, dst)][timestamp] = []
        new_data_dict[message_type][(src, dst)][timestamp].append(message)
    # print new_data_dict
    n_old_data = len(old_data)
    no_dup_old_data = []
    no_dup_dict = {}
    for datum in old_data:
        if tuple(datum[1:]) not in no_dup_dict:
            no_dup_dict[tuple(datum[1:])] = datum
    for unique_msg in no_dup_dict:
        no_dup_old_data.append(no_dup_dict[unique_msg])
    n_no_dup_old_data = len(no_dup_old_data)
    print 'With duplicates: '+str(n_old_data)+', without: '+str(n_no_dup_old_data)
    old_data = no_dup_old_data
    for datum in old_data:
        src = datum[pr.m_source]
        dst = datum[pr.m_target]
        message_type = datum[pr.m_type]
        if 'twitter' in message_type:
            if dst == 'None':
                dst = str(hash('Twitter'))
        timestamp = datum[pr.m_time_sent]
        message = datum[pr.m_content]
        if message_type not in new_data_dict:
            print 'Message type not found. MT: ' + str(message_type) + ', old datum: ', datum
        elif (src, dst) not in new_data_dict[message_type]:
            print 'Source-Target pair not found, (src, dst): ', (src, dst), ' old datum: ', datum
        elif timestamp not in new_data_dict[message_type][(src, dst)]:
            print 'Timestamp not found, timestamp: ', timestamp, ' old datum: ', datum
        else:
            foundMessage = False
            for new_message in new_data_dict[message_type][(src, dst)][timestamp]:
                if message in new_message:
                    foundMessage = True
                    break
            if not foundMessage:
                print 'Everything matched except for message content, \nold message: ', message, \
                    '\n new message list: ', new_data_dict[message_type][(src, dst)][timestamp]
    # to help me stop and think, will remove later
    # throw_away = raw_input('Press enter to continue')
    return


def __get_weekly_counts(dataset, field_to_search, to_equate, weekly_info, ff_obj, sorted_week_list, pid_hash,
                        is_old=False):
    out_in = ff_obj.filterbyequality(field_to_search, pid_hash, data=dataset)
    per_week = hlp.divideintoweekly(out_in, weekly_info, ff_obj)
    weekly_counts = [len(per_week[x]) for x in sorted_week_list]
    return weekly_counts, out_in, per_week


def get_message_counts(old_dataset, new_dataset, sorted_week_list, weekly_info, hash_to_pid_dict, ff_obj,
                       location_to_store, do_debug):
    in_out_message_dict = {}
    do_debug = True
    for pid_hash in hash_to_pid_dict:
        print '\n\n'
        old_pid_out_week_counts, old_out, old_out_week = __get_weekly_counts(old_dataset, pr.m_source, pid_hash,
                                                                             weekly_info, ff_obj, sorted_week_list,
                                                                             pid_hash, True)
        old_pid_in_weeks_counts, old_in, old_in_week = __get_weekly_counts(old_dataset, pr.m_target, pid_hash,
                                                                           weekly_info, ff_obj, sorted_week_list,
                                                                           pid_hash, True)
        new_pid_out_weeks_counts, new_out, new_out_week = __get_weekly_counts(new_dataset, pr.m_source, pid_hash,
                                                                              weekly_info, ff_obj, sorted_week_list,
                                                                              pid_hash)
        new_pid_in_weeks_counts, new_in, new_in_week = __get_weekly_counts(new_dataset, pr.m_target, pid_hash,
                                                                           weekly_info, ff_obj, sorted_week_list,
                                                                           pid_hash)
        in_out_message_dict[hash_to_pid_dict[pid_hash]] = [[old_pid_in_weeks_counts, old_pid_out_week_counts],
                                                           [new_pid_in_weeks_counts, new_pid_out_weeks_counts]]
        print 'Sums: o_o, n_o, o_i, n_i: ', sum(old_pid_out_week_counts), sum(new_pid_out_weeks_counts), \
            sum(old_pid_in_weeks_counts), sum(new_pid_in_weeks_counts)
        print 'Checking the numbers for ' + hash_to_pid_dict[pid_hash] + '(' + str(pid_hash) + ')'
        for week in sorted_week_list:
            # TODO: remove the True
            if len(old_out_week[week]) > len(new_out_week[week]) or True:
                print '***For week ' + str(week) + ' found old_out_week > new_out_week: ', len(old_out_week[week]), \
                    len(new_out_week[week])
                if do_debug:
                    __old_new_compare(old_out_week[week], new_out_week[week])
            # TODO: remove the True
            if len(old_in_week[week]) > len(new_in_week[week]) or True:
                print '***For week ' + str(week) + ' found old_in_week > new_in_week: ', len(old_in_week[week]), \
                    len(new_in_week[week])
                if do_debug:
                    __old_new_compare(old_in_week[week], new_in_week[week])

        hlp.dumpvariable([old_out, old_out_week, old_in, old_in_week, new_out, new_out_week, new_in, new_in_week],
                         hash_to_pid_dict[pid_hash] + '.data', location_to_store)
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
    ax_in.set_title('Incoming Messages(' + str(title) + ')')
    ax_in.set_xticks(xticks)
    ax_in.legend(loc=2)
    ax_in.grid(True)

    ax_out.plot(xticks, old_out, 'ro-', linewidth=2, label='Old', markersize=5, markeredgecolor='k', markerfacecolor='r'
                , markeredgewidth=2)
    ax_out.plot(xticks, new_out, 'bo-', linewidth=2, label='New', markersize=5, markeredgecolor='k', markerfacecolor='b'
                , markeredgewidth=2)
    ax_out.set_title('Outgoing Messages(' + str(title) + ')')
    ax_out.legend(loc=2)
    ax_out.set_xticks(xticks)
    ax_out.grid(True)

    ax.set_xlabel('Week #', fontsize=20)
    ax.set_ylabel('# of Messages', fontsize=20)

    plt.savefig(location_to_store + str(title) + '.pdf')
    plt.close()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-o', '-O', required=True, help='Old dataset csv')
    parser.add_argument('-n', '-N', required=True, help='New dataset csv')
    parser.add_argument('-s', '-S', required=True, help='Survey file')
    parser.add_argument('-p', '-P', required=True, help='folder to store figures in, should end with /')
    parser.add_argument('-m', '-M', required=True, help='Master hash mapping csv')
    parser.add_argument('-mt', '-MT', required=True, nargs='+', help='Types of messages to look for')
    parser.add_argument('-d', '-D', action='store_true', help='Flag to debug')

    args = parser.parse_args()

    old_dataset_file = args.o
    new_dataset_file = args.n
    survey_file = args.s
    location_to_store = args.p
    master_hash_csv = args.m
    message_types = args.mt
    do_debug = args.d

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
                                             location_to_store, do_debug)

    print 'Plotting...'
    for pid in in_out_message_dict:
        print pid
        plot_distribution(in_out_message_dict[pid][0][0], in_out_message_dict[pid][0][1],
                          in_out_message_dict[pid][1][0], in_out_message_dict[pid][1][1], week_list, pid,
                          location_to_store)
    print 'TADAA!!'


if __name__ == "__main__":
    main()
