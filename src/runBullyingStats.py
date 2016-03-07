import argparse
import datetime as dt

import helper as hlp
from basicInfo import privateInfo as pr
from basicInfo import surveyInfo as sr
from filterByField import filterfields
from graphing import creategraph


def createstaticgraph(pid_dict, data_list):
    links, links_tuple = hlp.getlinks(pid_dict, data_list)
    graph_obj = creategraph(True)
    for p_type in pid_dict.keys():
        graph_obj.addnodes(pid_dict[p_type], p_type)
    graph_obj.addedges(links_tuple)
    return graph_obj


def processgraph(graph_obj, participant_id):
    degrees = graph_obj.getdegrees(participant_id)
    in_degrees = degrees[0]
    out_degrees = degrees[1]
    e_weights = graph_obj.getedgeweights(participant_id)
    in_e_weights = []
    out_e_weights = []
    for edge in e_weights[0]:
        in_e_weights.append(edge[2]['weight'])
    for edge in e_weights[1]:
        out_e_weights.append(edge[2]['weight'])
    return {'indegree': in_degrees, 'outdegree': out_degrees, 'inweights': in_e_weights, 'outweights': out_e_weights}


def graphstats(before_date_data_list, between_date_data_list, participant_id, p_type, original_start, p_start, ff_obj):
    if [] == before_date_data_list or [] == between_date_data_list:
        return [], []
    pid_dict = hlp.getuniqueparticipants(before_date_data_list)
    pid = 0
    for key in pid_dict.keys():
        if participant_id in pid_dict[key]:
            temp = pid_dict[key]
            pid = temp[participant_id]
            temp_ret = hlp.removekey(temp, participant_id)
            pid_dict[key] = temp_ret
            break
    pid_dict[p_type] = {participant_id: pid}
    # between date processing
    graph_obj_between = createstaticgraph(pid_dict, between_date_data_list)
    between_stats = processgraph(graph_obj_between, pid)
    between_stats['graph_obj'] = graph_obj_between.getgraphobject()
    # before date processing, this has to be done per week
    loop_can_continue = True
    curr_start = original_start
    before_stats = []
    while loop_can_continue:
        end_date = curr_start + dt.timedelta(days=7)
        if end_date > p_start:
            end_date = p_start
            loop_can_continue = False
        to_consider = ff_obj.filterbetweendates(curr_start, end_date, data_to_work=before_date_data_list)
        if [] == to_consider:
            curr_start = end_date
            continue
        graph_obj_before = createstaticgraph(pid_dict, to_consider)
        temp = processgraph(graph_obj_before, pid)
        temp['graph_obj'] = graph_obj_before.getgraphobject()
        before_stats.append((curr_start, end_date, temp))
        curr_start = end_date
    return between_stats, before_stats


def getstats(filepath, participant_dict, p_type, message_type='sms'):
    ff = filterfields(filepath)
    ff.setdata(ff.filterbyequality(pr.m_type, message_type))
    participant_stats = {}
    for participant_id in participant_dict:
        survey_no_list = participant_dict[participant_id]
        p_data = ff.filterbyequality(pr.m_source, participant_id) + \
                 ff.filterbyequality(pr.m_target, participant_id)
        if [] == p_data:
            print 'no data exists for pid: ' + participant_id
            continue
        for survey_no in survey_no_list:
            print 'Participant no.', participant_id, ' S.no.: ', survey_no
            idx = survey_no
            survey_no = survey_no_list[survey_no][0]
            end_date = ff.converttodate(survey_no[sr.s_time])
            start_date = end_date - dt.timedelta(days=7)
            data_between_dates = ff.filterbetweendates(start_date, end_date, data_to_work=p_data)
            original_start_date = ff.converttodate(pr.start_datetime)
            data_start_to_date = ff.filterbetweendates(original_start_date, start_date, data_to_work=p_data)
            between_stats, before_stats = graphstats(data_start_to_date, data_between_dates, participant_id, p_type,
                                                     original_start_date, start_date, ff)
            temp_dict = {'between': between_stats, 'before': before_stats}
            participant_stats[participant_id] = {idx: temp_dict}
    return participant_stats


def main():
    parse = argparse.ArgumentParser('Script to generate statistics on bullying data')
    parse.add_argument('-i', '-I', type=str, required=True,
                       help='Path to the input dictionary containing bullying information')
    parse.add_argument('-m', '-M', type=str, required=True,
                       help='Path to the messages file, should be a csv')
    parse.add_argument('-s', '-S', type=str, required=True,
                       help='Directory where results are stored, with a leading /')
    parse.add_argument('-f', '-F', type=str, required=True,
                       help='File name')
    parse.add_argument('-p', '-P', type=str, required=True,
                       help='Participant type')
    args = parse.parse_args()
    bullying_data = hlp.recovervariable(args.i)
    message_path = args.m
    save_dir = args.s
    save_f = args.f
    p_type = args.p
    res = {}
    for key in bullying_data.keys():
        res[key] = getstats(message_path, bullying_data[key], p_type)
    hlp.dumpvariable(res, save_f, save_dir)


if __name__ == "__main__":
    main()
