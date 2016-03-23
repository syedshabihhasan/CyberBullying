from basicInfo import privateInfo as pr
from basicInfo import surveyInfo as sr
from filterByField import filterfields
import helper as hlp
import datetime as dt


class ghelper:

    def liesinweeks(self, date_to_check, week_info):
        curr_start = date_to_check - dt.timedelta(days=7)
        curr_start = curr_start.replace(hour=0, minute=0, second=0)
        curr_end = date_to_check - dt.timedelta(days=1)
        curr_end = curr_end.replace(hour=23, minute=59, second=59)

        week_list = week_info.keys()
        week_list.sort()

        # extreme cases
        if curr_end < week_info[week_list[0]][0]:
            print 'curr_end is before the study starts, skipping'
            return []
        if curr_start > week_info[week_list[-1]][1]:
            print 'curr_start is after the study ends, skipping'
            return []
        if curr_start < week_info[week_list[0]][0] < curr_end:
            print 'curr_start is before study starts, but end is after, skipping'
            return []
        if curr_start < week_info[week_list[-1]][1] < curr_end:
            print 'curr_end is after the study ends, but start is before, skipping'
            return []
        # lets look the dates up
        to_return = set()
        for weekno in week_list:
            date_tuple = week_info[weekno]
            if date_tuple[0] <= curr_start <= date_tuple[1]:
                to_return.add(weekno)
            if date_tuple[0] <= curr_end <= date_tuple[1]:
                to_return.add(weekno)
        return list(to_return)


    def createbullyingoverlay(self, catch_all_data, week_info, ff_obj):
        bullying_overlay = {}
        for category in catch_all_data.keys():
            cat_pid_dict = catch_all_data[category]
            for pid in cat_pid_dict.keys():
                sno_dict = cat_pid_dict[pid]
                for sno in sno_dict.keys():
                    survey_time = sno_dict[sno][0][sr.s_time]
                    week_list = self.liesinweeks(ff_obj.converttodate(survey_time), week_info)
                    if [] == week_list:
                        continue
                    if pid not in bullying_overlay.keys():
                        bullying_overlay[pid] = {}
                    if category not in bullying_overlay[pid].keys():
                        bullying_overlay[pid][category] = []
                    bullying_overlay[pid][category] += week_list
                bullying_overlay[pid][category] = list(set(bullying_overlay[pid][category]))
        return bullying_overlay

    def getminmaxdates(self, message_data, ff_obj):
        curr_min = dt.datetime.max
        curr_max = dt.datetime.min
        for datum in message_data:
                to_consider_date = ff_obj.converttodate(datum[pr.m_time_sent])
                curr_min = to_consider_date if to_consider_date < curr_min else curr_min
                curr_max = to_consider_date if to_consider_date > curr_max else curr_max
        return curr_min, curr_max

    def __weeklygraphs(self, weekly_dict, pid_dict, message_type='sms'):
        weekly_graphs = {}
        for weekno in weekly_dict.keys():
            links, link_tuple, graph_obj, p_d = hlp.creategraph(weekly_dict[weekno], pid_dict=pid_dict,
                                                                filterType=message_type)
            weekly_graphs[weekno] = graph_obj
        return weekly_graphs

    def __perparticipantprocessing(self, pid, ff_obj, curr_min=None, curr_max=None,
                                   send_week_info=False, week_info=None):
        print 'per participant processing: ', pid
        week_info = {} if week_info is None else week_info
        pid_data = ff_obj.filterbyequality(pr.m_source, pid) + \
                   ff_obj.filterbyequality(pr.m_target, pid)
        if curr_min is None or curr_max is None:
            curr_min, curr_max = self.getminmaxdates(pid_data, ff_obj)
        curr_min = curr_min.replace(hour=0, minute=0, second=0)
        curr_max = curr_max.replace(hour=23, minute=59, second=59)
        loop_can_continue = True
        start_date = curr_min
        end_date = curr_min + dt.timedelta(days=7)
        weekly_data = {}
        if {} == week_info:
            idx = 1
            while loop_can_continue:
                if end_date > curr_max:
                    end_date = curr_max
                    loop_can_continue = False
                temp_data = ff_obj.filterbetweendates(start_date, end_date,
                                                      data_to_work=pid_data)
                weekly_data[idx] = temp_data
                week_info[idx] = (start_date, end_date)
                idx += 1
                start_date = end_date
                end_date = end_date + dt.timedelta(days=7)
        else:
            for weekno in week_info.keys():
                start_date = week_info[weekno][0]
                end_date = week_info[weekno][1]
                temp_data = ff_obj.filterbetweendates(start_date, end_date,
                                                      data_to_work=pid_data)
                weekly_data[weekno] = temp_data
        if send_week_info:
            return weekly_data, week_info
        else:
            return weekly_data

    def getweeklydistributions(self, pid_dict, message_list, message_type='sms',
                               is_degree=True, week_info=None):
        # is_degree = F --> edge weight distribution
        week_info = {} if week_info is None else week_info
        participant_dict = pid_dict[pr.participant[message_type]]
        ff_obj = filterfields('')
        ff_obj.setdata(message_list)
        if week_info is not None:
            min_week = min(week_info.keys())
            max_week = max(week_info.keys())
            min_date = week_info[min_week][0]
            max_date = week_info[max_week][1]
        else:
            min_date, max_date = self.getminmaxdates(message_list, ff_obj)
        weekly_dist = {}
        for pid in participant_dict.keys():
            weekly_dist[pid] = {}
            if week_info is None:
                weekly_dict, temp_week_info = self.__perparticipantprocessing(pid, ff_obj,
                                                                              curr_min=min_date, curr_max=max_date,
                                                                              send_week_info=True)
                week_info[pid] = temp_week_info
            else:
                weekly_dict = self.__perparticipantprocessing(pid, ff_obj, curr_min=min_date, curr_max=max_date,
                                                              send_week_info=False, week_info=week_info)
            weekly_graphs = self.__weeklygraphs(weekly_dict, pid_dict, message_type=message_type)
            for weekno in weekly_graphs.keys():
                go = weekly_graphs[weekno]
                if is_degree:
                    g_info = go.getdegrees(participant_dict[pid])
                else:
                    g_info_ew = go.getedgeweights(participant_dict[pid])
                    in_w = 0
                    out_w = 0
                    for e_tuple in g_info_ew[0]:
                        in_w += e_tuple[2]['weight']
                    for e_tuple in g_info_ew[1]:
                        out_w += e_tuple[2]['weight']
                    g_info = [in_w, out_w]
                weekly_dist[pid][weekno] = g_info
        return weekly_dist, week_info

    def getdegreedistribution(self, pid_dict, ip_list, graph_obj, is_list_coded=False,
                              m_type='sms', return_dict=False, is_degree=True):
        degree_distribution_in = {} if return_dict else []
        degree_distribution_out = {} if return_dict else []
        for pid in ip_list:
            pid_to_use = pid
            if not is_list_coded:
                if pid in pid_dict[pr.participant[m_type]]:
                    pid_to_use = pid_dict[pr.participant[m_type]][pid]
                else:
                    print 'degreedistribtion: could not find ', pid, ' ,skipping'
                    continue
            degrees = graph_obj.getdegrees(pid_to_use) if is_degree \
                else graph_obj.getedgeweights(pid_to_use)
            if not is_degree:
                in_ew = degrees[0]
                out_ew = degrees[1]
                inw = 0
                outw = 0
                for edge_tuple in in_ew:
                    inw += edge_tuple[2]['weight']
                for edge_tuple in out_ew:
                    outw += edge_tuple[2]['weight']
                degrees = [inw, outw]
            if return_dict:
                degree_distribution_in[pid] = degrees[0]
                degree_distribution_out[pid] = degrees[1]
            else:
                degree_distribution_in.append(degrees[0])
                degree_distribution_out.append(degrees[1])
        return degree_distribution_in, degree_distribution_out

    def generatedistributions(self, graph_obj, bullying_pid_dict, allP, other, pid_dict,
                              message_type, cumulative_pid_list, in_dist=False, is_degree=True):
        # remove all the participants who are not present
        deg_dist = {}
        for filter_type in bullying_pid_dict.keys():
            print filter_type
            pid_list = bullying_pid_dict[filter_type]
            degrees = self.getdegreedistribution(pid_dict, pid_list, graph_obj,
                                                 m_type=message_type, is_degree=is_degree)
            deg_dist[filter_type] = degrees[0] if in_dist else degrees[1]
        if allP:
            degrees = self.getdegreedistribution(pid_dict,
                                                 pid_dict[pr.participant[message_type]],
                                                 graph_obj, m_type=message_type, is_degree=is_degree)
            deg_dist['all'] = degrees[0] if in_dist else degrees[1]
        other_pid = []
        for pid in pid_dict[pr.participant[message_type]].keys():
            if pid not in cumulative_pid_list:
                other_pid.append(pid)
        if other:
            degrees = self.getdegreedistribution(pid_dict, other_pid,
                                                 graph_obj, m_type=message_type, is_degree=is_degree)
            deg_dist['none'] = degrees[0] if in_dist else degrees[1]
        return deg_dist

    def __init__(self):
        return
