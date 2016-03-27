import argparse
from filterByField import filterfields
from createweeklyinfo import weeklyinfo
from basicInfo import privateInfo as pr
from graphhelper import ghelper
from plothelper import plots
import helper as hlp

def main():
    parser = argparse.ArgumentParser('Script to generate distribution '
                                     'of edge weights/degrees for all '
                                     'participants')
    parser.add_argument('-m', '-M', type=str, required=True,
                        help='location of the message file')
    parser.add_argument('-mt', '-MT', type=str, default='all',
                        help='types of messages to plot, currently supports '
                             'one of the following: sms, fb, twitter, or all')
    parser.add_argument('-r', '-R', type=str, required=True,
                        help='survey file')
    parser.add_argument('-s', '-S', type=str, required=True,
                        help='folder to store data in, leading / required')
    parser.add_argument('-p', '-P', action='store_true',
                        help='flag to generate plots')

    args = parser.parse_args()
    survey_file = args.r
    message_file = args.m
    m_type = args.mt
    folder_to_store = args.s
    generate_plots = args.p

    wi = weeklyinfo()
    week_info = wi.getweeklyfo(survey_file)

    ff = filterfields(message_file)
    filtered_data = []
    if m_type == 'all':
        for message_type in ['sms', 'fb_message']:
            filtered_data.extend(ff.filterbyequality(pr.m_type, message_type))
    else:
        filtered_data = ff.filterbyequality(pr.m_type, m_type)
    _, links_tuple, _, pid_dict = hlp.creategraph(filtered_data, filterType=args.mt)
    gh = ghelper()
    plt = plots()
    weekly_deg_dist, _ = gh.getweeklydistributions(pid_dict, filtered_data, message_type=args.mt,
                                                   is_degree=True, week_info=week_info)
    hlp.dumpvariable(weekly_deg_dist, 'weekly_deg_dist.dict', folder_to_store)
    weekly_ew_dist, _ = gh.getweeklydistributions(pid_dict, filtered_data, message_type=args.mt,
                                                  is_degree=False, week_info=week_info)
    hlp.dumpvariable(weekly_ew_dist, 'weekly_ew_dist.dict', folder_to_store)
    if generate_plots:
        plt.plotweeklyprogression(weekly_deg_dist, folder_to_store + 'deg_', 'No. of friends',
                                  'Week No.', 'Friends')
        plt.plotweeklyprogression(weekly_ew_dist, folder_to_store + 'ew_', 'No. of messages exhanged',
                                  'Week No.', 'Messages')

    print 'done...'

if __name__ == "__main__":
    main()