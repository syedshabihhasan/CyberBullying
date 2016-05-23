import argparse
import helper as hlp
from createweeklyinfo import weeklyinfo
from surveyprocessing import surveys
from filterByField import filterfields
from basicInfo import surveyInfo as s_i
from basicInfo import privateInfo as pr
from basicInfo import new_dataset as nd


def __find_positive_survey(survey_file, week_info):
    week_no = week_info.keys()
    week_no.sort()

    ff = filterfields()
    s_obj = surveys()

    survey_data = hlp.readcsv(survey_file, delimiter_sym=',')
    n_data = s_obj.interpretanswers(survey_data, True)
    bullying_positives = ff.filterbyequality(s_i.s_qno, '4', data=n_data[1:])

    new_bullying_positives = []
    for datum in bullying_positives:
        datetime_of_survey = ff.converttodate(datum[s_i.s_time])
        found_match = False
        for week in week_no:
            (start_date, end_date) = week_info[week]
            if start_date <= datetime_of_survey <= end_date:
                datum.append(week)
                new_bullying_positives.append(datum)
                found_match = True
                break
        if not found_match:
            print 'Something funky happened...', datum
            return None
    return new_bullying_positives


def __define_process_parser(process=False, parser=None):
    if process:
        if parser is None:
            return None
        args = parser.parse_args()
        return args.o, args.n, args.m, args.s, args.f
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument('-o', '-O', help='old dataset', required=True)
        parser.add_argument('-n', '-N', help='new mapped dataset', required=True)
        parser.add_argument('-m', '-M', help='old data missing in new', required=True)
        parser.add_argument('-s', '-S', help='survey file', required=True)
        parser.add_argument('-f', '-F', help='folder to store in, ending in /', required=True)
        return parser

def __dictify(field_no, data, is_new=False):
    to_return = {}
    for datum in data:
        if not is_new:
            if datum[field_no] not in to_return:
                to_return[datum[field_no]] = []
            to_return[datum[field_no]] = datum
        else:
            for i in range(field_no, len(datum)):
                if datum[i] == '':
                    continue
                if datum[i] not in to_return:
                    to_return[datum[i]] = []
                to_return[datum[i]] = datum
    return to_return


def compare_old_new(old_data, new_data, old_missing, pid_hash, ff):
    old_data_pid = ff.filterbyequality(pr.m_source, pid_hash, data=old_data) + \
                   ff.filterbyequality(pr.m_target, pid_hash, data=old_data)
    new_data_pid = ff.filterbyequality(nd.m_source, pid_hash, data=new_data) + \
                   ff.filterbyequality(nd.m_target, pid_hash, data=new_data)
    old_data_filtered = ff.filterbyequality(pr.m_type, 'sms', data=old_data_pid) + \
                        ff.filterbyequality(pr.m_type, 'fb_message', data=old_data_pid) + \
                        ff.filterbyequality(pr.m_type, 'twitter_status', data=old_data_pid) + \
                        ff.filterbyequality(pr.m_type, 'twitter_message', data=old_data_pid)
    new_data_filtered = ff.filterbyequality(nd.m_type, 'sms', data=new_data_pid) + \
                        ff.filterbyequality(nd.m_type,'fb_message', data=new_data_pid) + \
                        ff.filterbyequality(nd.m_type, 'twitter_status', data=new_data_pid) + \
                        ff.filterbyequality(nd.m_type, 'twitter_message', data=new_data_pid)
    n_old_data = len(old_data_filtered)
    old_dict = __dictify(pr.msg_id, old_data_filtered)
    n_new_data = len(new_data_filtered)
    new_dict = __dictify(nd.m_old_id_start, new_data_filtered, is_new=True)
    not_found_reason = {'raw': 0, 'semi': 0, 'ordered': 0, 'other': 0}
    for id in old_dict.keys():
        if id not in new_dict:
            reason_datum = old_missing[id]
            reason = reason_datum[-1]
            if reason == '':
                reason = 'raw'
            elif 'semi' in reason:
                reason = 'semi'
            elif 'ordered' in reason:
                reason = 'ordered'
            else:
                reason = 'other'
            not_found_reason[reason] += 1
    return n_old_data, n_new_data, not_found_reason



def main():
    parser = __define_process_parser()
    old_dataset_file, new_dataset_mapped, missing_data, \
    survey_file, location_to_store = __define_process_parser(True, parser)

    old_dataset = hlp.readcsv(old_dataset_file, delimiter_sym=',', remove_first=True)
    new_dataset = hlp.readcsv(new_dataset_mapped, delimiter_sym=',', remove_first=True)
    old_data_missing = hlp.readcsv(missing_data, delimiter_sym=',', remove_first=True)
    old_missing = __dictify(0, old_data_missing)
    wi = weeklyinfo()
    week_info = wi.getweeklyfo(survey_file)
    week_list = week_info.keys()
    bullying_positives = __find_positive_survey(survey_file, week_info)
    if bullying_positives is None:
        print 'Exiting...'
        exit()

    ff = filterfields()
    old_data_weekly = hlp.divideintoweekly(old_dataset, week_info, ff, date_field=pr.m_time_sent)
    new_data_weekly = hlp.divideintoweekly(new_dataset, week_info, ff, date_field=nd.m_timecreated)
    bullying_res = [['pid_hash', 'survey_id', 'time_of_survey', 'n_old', 'n_new', 'raw', 'semi', 'ordered', 'other']]
    for datum in bullying_positives:
        bullying_week = datum[-1]
        prev_week = bullying_week - 1 if bullying_week > min(week_list) else min(week_list)
        next_week = bullying_week + 1 if bullying_week < max(week_list) else max(week_list)
        old_data_pos = old_data_weekly[prev_week] + old_data_weekly[bullying_week] + old_data_weekly[next_week]
        new_data_pos = new_data_weekly[prev_week] + new_data_weekly[bullying_week] + new_data_weekly[next_week]
        pid_hash = datum[s_i.s_participant]
        n_old, n_new, nfr_dict = compare_old_new(old_data_pos, new_data_pos, old_missing, pid_hash, ff)
        temp = [pid_hash, datum[s_i.s_id], datum[s_i.s_time], n_old, n_new, nfr_dict['raw'], nfr_dict['semi'],
                nfr_dict['ordered'], nfr_dict['other']]
        bullying_res.append(temp)
    hlp.writecsv(bullying_res, location_to_store+'bullying_res.csv', delimiter_sym=',')
if __name__ == "__main__":
    main()
