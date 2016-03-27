import argparse
import matplotlib.pyplot as plt
from filterByField import filterfields
from basicInfo import privateInfo as pr
from basicInfo import plottingdetails as pld
import helper as hlp
import numpy as np
from math import ceil

def initiatestorage(participant_list, message_types):
    storage_dict = {}
    for pid in participant_list:
        temp = {}
        for message_type in message_types:
            temp[message_type] = [0, 0]
        storage_dict[pid] = temp
    return storage_dict

def getperparticipantinout(data, storage_dict, pid_dict, m_type='all'):
    for datum in data:
        source = datum[pr.m_source]
        target = datum[pr.m_target]
        msg_type = datum[pr.m_type]
        if source in pid_dict[pr.participant[m_type]]:
            # source is sending a message: outgoing
            coded_pid = pid_dict[pr.participant[m_type]][source]
            storage_dict[coded_pid][msg_type][1] += 1
        if target in pid_dict[pr.participant[m_type]]:
            # target is receiving a message: incoming
            coded_pid = pid_dict[pr.participant[m_type]][target]
            storage_dict[coded_pid][msg_type][0] += 1
    return storage_dict

def plotperparticipantbar(storage_dict, x_title, y_title, legend_labels, overall_title, location_to_store):
    #TODO:
    participant_list = storage_dict.keys()
    participant_list.sort()
    message_types = storage_dict[participant_list[0]].keys()
    message_types.sort()
    no_of_bars_per_pid = len(message_types)
    bar_width = 0.6/no_of_bars_per_pid
    ind = np.arange(len(participant_list))
    xtick_positions = ind + 0.3
    fig, (ax, ax1) = plt.subplots(2, 1, sharex=True)
    rects = []
    legend_info = []
    maxy = 0
    for idx in range(no_of_bars_per_pid):
        bar_positions = ind + idx*bar_width
        message_type = message_types[idx]
        incoming = []
        outgoing = []
        for pid in participant_list:
            pid_in_out_data = storage_dict[pid][message_type]
            incoming.append(pid_in_out_data[0])
            outgoing.append(pid_in_out_data[1])
        maxy = max(incoming)+max(outgoing) if max(incoming)+max(outgoing) > maxy else maxy
        plotting_color_in = pld.tableau20[2*idx]
        plotting_color_in = (plotting_color_in[0]/255., plotting_color_in[1]/255., plotting_color_in[2]/255.)
        plotting_color_out = pld.tableau20[2*idx + 1]
        plotting_color_out = (plotting_color_out[0]/255., plotting_color_out[1]/255., plotting_color_out[2]/255.)
        # rect_in = plt.bar(bar_positions, incoming, width=bar_width, color=plotting_color_in)
        # rect_out = plt.bar(bar_positions, outgoing, width=bar_width, color=plotting_color_out, bottom=incoming)
        rect_in = ax.bar(bar_positions, incoming, width=bar_width, color=plotting_color_in)
        rect_out = ax.bar(bar_positions, outgoing, width=bar_width, color=plotting_color_out, bottom=incoming)
        rect_in = ax1.bar(bar_positions, incoming, width=bar_width, color=plotting_color_in)
        rect_out = ax1.bar(bar_positions, outgoing, width=bar_width, color=plotting_color_out, bottom=incoming)
        # rects.append(rect_in)
        # rects.append(rect_out)
        legend_info.append(message_type + '(In)')
        legend_info.append(message_type + '(Out)')
    ax.set_ylim(11000, 25000)
    ax1.set_ylim(0, 4000)
    ax.spines['bottom'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax.xaxis.tick_top()
    ax.tick_params(labeltop='off')
    ax1.xaxis.tick_bottom()
    plt.xticks(xtick_positions, participant_list, fontsize=8, rotation='vertical')
    # plt.yticks(range(0, maxy+2000, 2000), fontsize=12)
    # plt.ylim((0, 3000))
    ax.legend(legend_info, loc='upper left', fontsize=20)
    ax.yaxis.grid(True)
    ax1.yaxis.grid(True)
    plt.xlabel(x_title, fontsize=20)
    plt.ylabel(y_title, fontsize=20)
    fig.suptitle(overall_title, fontsize=20)
    # plt.tight_layout()
    plt.savefig(location_to_store)

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '--messageFile', type=str, required=True)
    parser.add_argument('-mt', '--messageTypes', type=str, nargs='+')
    parser.add_argument('-o', '--outputFolder', type=str, required=True)
    parser.add_argument('-of', '--outputFile', type=str, required=True)
    parser.add_argument('-pd', '--participantDictionary', type=str)
    parser.add_argument('-i', '--ignoreParticipants', type=str)
    parser.add_argument('-mc', '--messageTypeConvert', type=str, nargs='*')

    args = parser.parse_args()

    message_file = args.messageFile
    message_types = args.messageTypes
    output_folder = args.outputFolder
    output_file = args.outputFile
    pid_dict = args.participantDictionary
    ignore_pids = args.ignoreParticipants
    message_type_conversions = args.messageTypeConvert

    ff = filterfields(message_file)
    ff.setdata(ff.getdata()[1:])

    to_set_data = []

    # extract the relevant data
    for message_type in message_types:
        to_set_data.extend(ff.filterbyequality(pr.m_type, message_type))

    ff.setdata(to_set_data)

    if ignore_pids is not None:
        ignore_pids = hlp.recovervariable(ignore_pids)
        for pid in ignore_pids:
            ff.removebyequality(pr.m_source, pid)
            ff.removebyequality(pr.m_target, pid)


    # set the pid to normal id dictionary
    if pid_dict is None:
        pid_dict = hlp.getuniqueparticipants(ff.getdata(), mtype='all', separate_pid_npid=True)

    # replace the message type names with the ones provided
    if message_type_conversions is not None:
        for idx in range(0, len(message_type_conversions), 2):
            message_to_convert = message_type_conversions[idx]
            to_convert_to = message_type_conversions[idx+1]
            ff.replacebyequality(pr.m_type, message_to_convert, to_convert_to)

    message_types = ff.getuniqueelements(pr.m_type)
    coded_participant_list = pid_dict[pr.participant['all']].values()
    storage_dict = initiatestorage(coded_participant_list, message_types)
    storage_dict = getperparticipantinout(ff.getdata(), storage_dict, pid_dict)
    plotperparticipantbar(storage_dict, 'Participant ID', '# of Messages', message_types, 'Per Participant Messages',
                          output_folder+output_file)
    hlp.dumpvariable(pid_dict, 'pid_dict.dict', output_folder)
    hlp.dumpvariable(ff.getdata(), 'messageData.list', output_folder)

if __name__ == "__main__":
    main()