import argparse
import os
import helper as hlp
from basicInfo import exceptionstrings as e
from basicInfo import privateInfo as pr
from filterByField import filterfields
from graphhelper import ghelper
from plothelper import plots
from createweeklyinfo import weeklyinfo


def getfilterdata(filters_chosen, filter_files, cumulative_list=False, catch_all=False):
    data = {}
    cumulative_pid_list = []
    catch_all_data = {}
    for idx in range(len(filters_chosen)):
        loaded_data = hlp.recovervariable(filter_files[idx])
        temp = []
        for key in loaded_data.keys():
            temp += loaded_data[key].keys()
        data[filters_chosen[idx]] = temp
        catch_all_data[filters_chosen[idx]] = loaded_data[key]
        cumulative_pid_list += temp
    if cumulative_list:
        return cumulative_pid_list
    elif catch_all:
        return catch_all_data
    else:
        return data


def main():
    parser = argparse.ArgumentParser('Script to generate a CDF comparing the degrees of our participants')

    parser.add_argument('-l', '-L', type=str, nargs='+', required=True,
                        help='the filters to use, make one or more choices: seenB, wasB, didB')
    parser.add_argument('-f', '-F', type=str, nargs='+', required=True,
                        help='location of filtered data, from runSurveyStats.py, in the same order as -l/L flag')
    parser.add_argument('-m', '-M', type=str, required=True,
                        help='location of the message file')
    parser.add_argument('-mt', '-MT', type=str, default='sms',
                        help='type of message we are filtering, default: sms')
    parser.add_argument('-n', '-N', action='store_true',
                        help='flag indicates that processing should include participants which did not witness '
                             'anything mentioned in the values passed for flags -l/L')
    parser.add_argument('-a', '-A', action='store_true',
                        help='flag indicates that processing should include a plot of all participants')
    parser.add_argument('-s', '-S', type=str, required=True,
                        help='folder to store in, leading /')
    parser.add_argument('-r', '-R', type=str, required=True,
                        help='survey file')

    args = parser.parse_args()
    filters_chosen = args.l
    for filter_v in filters_chosen:
        if filter_v not in ['seenB', 'didB', 'wasB']:
            raise Exception('filter value was not from the ones specified')
    filter_files = args.f
    assert len(filter_files) == len(filters_chosen), e.len_filter_file_ne_len_filters_chosen
    include_other_participants = args.n
    include_all_participants = args.a
    location_to_store = args.s
    if not os.path.exists(location_to_store):
        os.mkdir(location_to_store)
    message_file = args.m
    message_type = args.mt
    survey_file = args.r

    wi = weeklyinfo()
    week_info = wi.getweeklyfo(survey_file)
    gh = ghelper()
    plt = plots()


    # get the filtered messages
    ff = filterfields(message_file)
    filtered_data = []
    if message_type == 'all':
        for message_type in ['sms', 'fb', 'twitter']:
            filtered_data.extend(ff.filterbyequality(pr.m_type, message_type))
    else:
        filtered_data = ff.filterbyequality(pr.m_type, message_type)

    # generate the links and the graph for the filtered data
    links, links_tuple, graph_obj, pid_dict = hlp.creategraph(filtered_data, filterType=message_type)

    # get the pids from the chosen filters
    bullying_pid_dict = getfilterdata(filters_chosen, filter_files)
    cumulative_bully_pid = getfilterdata(filters_chosen, filter_files, cumulative_list=True)

    # get all the information from the filters
    catch_all_data = getfilterdata(filters_chosen, filter_files, catch_all=True)

    # generate the distributions for in degree and plot them
    in_distributions = gh.generatedistributions(graph_obj, bullying_pid_dict, include_all_participants,
                                                include_other_participants, pid_dict, message_type,
                                                cumulative_bully_pid, in_dist=True)
    in_distributions_ew = gh.generatedistributions(graph_obj, bullying_pid_dict, include_all_participants,
                                                include_other_participants, pid_dict, message_type,
                                                cumulative_bully_pid, in_dist=True, is_degree=False)
    plt.generatetablehist(in_distributions, location_to_store + 'in_degree_table.csv', generate_totals=True)
    plt.generatetablehist(in_distributions_ew, location_to_store + 'in_edge_weight.csv', generate_totals=True)

    # generate the distributions for out degree and plot them
    out_distributions = gh.generatedistributions(graph_obj, bullying_pid_dict, include_all_participants,
                                                 include_other_participants, pid_dict, message_type,
                                                 cumulative_bully_pid, in_dist=False)
    out_distributions_ew = gh.generatedistributions(graph_obj, bullying_pid_dict, include_all_participants,
                                                 include_other_participants, pid_dict, message_type,
                                                 cumulative_bully_pid, in_dist=False)
    plt.generatetablehist(out_distributions, location_to_store + 'out_degree_table.csv', generate_totals=True)
    plt.generatetablehist(out_distributions_ew, location_to_store + 'out_edge_weight.csv', generate_totals=True)


    # line plot of degrees
    weekly_dist_degrees, _ = gh.getweeklydistributions(pid_dict, filtered_data,
                                                    message_type=message_type,
                                                    is_degree=True, week_info=week_info)
    overlay_info = gh.createbullyingoverlay(catch_all_data, week_info, ff)
    plt.plotweeklyprogression(weekly_dist_degrees, location_to_store+'deg_', 'No of friends',
                              'Week No', 'Friends', overlay_date=overlay_info)
    # line plot of weights
    weekly_dist_ew, _ = gh.getweeklydistributions(pid_dict, filtered_data,
                                                    message_type=message_type,
                                                    is_degree=False, week_info=week_info)
    overlay_info = gh.createbullyingoverlay(catch_all_data, week_info, ff)
    plt.plotweeklyprogression(weekly_dist_ew, location_to_store+'ew_', 'No. of messages exchanged',
                              'Week No', 'Messages', overlay_date=overlay_info)
    print 'TADAAA!'
if __name__ == "__main__":
    main()
