import argparse
import helper as hlp
from filterByField import filterfields
from basicInfo import privateInfo as pr
from vaderpolarity import vadersenti
from createweeklyinfo import weeklyinfo
from graphhelper import ghelper
from plothelper import plots

def main():
    parser = argparse.ArgumentParser('Script to perform sentiment analysis using VADER')

    parser.add_argument('-m', '-M', type=str, required=True,
                        help='Location of the message file')
    parser.add_argument('-mt', '-MT', type=str, required=True, nargs='+',
                        help='types of messages to filter')
    parser.add_argument('-f', '-F', type=str, required=True,
                        help='filename where data is stored, no extension needed')
    parser.add_argument('-s','-S', type=str, required=True,
                        help='location of folder to store the file, ends with a /')
    parser.add_argument('-p', '-P', action='store_true',
                        help='flag to store polarities separately')
    parser.add_argument('-w', '-W', type=str, required=False,
                        help='conduct weekly analysis, path to the survey data for '
                             'creating week information')
    parser.add_argument('-l', '-L', type=str, nargs='+', required=True,
                        help='the filters to use, make one or more choices: seenB, wasB, didB')
    parser.add_argument('-lf', '-LF', type=str, nargs='+', required=True,
                        help='location of filtered data, from runSurveyStats.py, in same order as -l/L flag')


    args = parser.parse_args()
    message_file = args.m
    message_types = args.mt
    filename_to_store = args.f
    location_to_store = args.s
    separate_polarity_score = args.p
    survey_file = args.w
    filters_chosen = args.l
    filter_files = args.lf

    catch_all_data = hlp.getfilterdata(filters_chosen, filter_files, catch_all=True)

    if separate_polarity_score and survey_file is not None:
        print 'Cannot have separate polarity scores and weekly analysis together, ' \
              'please remove the -p/-P flag'
        return

    if survey_file is not None:
        wi = weeklyinfo()
        week_dates = wi.getweeklyfo(survey_file)
        gh = ghelper()
    ff = filterfields(message_file)
    data = []
    for message_type in message_types:
        data.extend(ff.filterbyequality(pr.m_type, message_type))
    pid_dict = hlp.getuniqueparticipants(data, 'all' if len(message_types) > 1 else message_types[0])
    sentiment_analyzer = vadersenti(data[1:])
    returned_data = sentiment_analyzer.compilesentiment(pr.m_content, separate_sentiment_list=separate_polarity_score)
    if separate_polarity_score:
        hlp.dumpvariable(returned_data, filename_to_store+'.data', location_to_store)
    else:
        header = pr.message_header + ['pos', 'neg', 'neu', 'compound']
        final_data = [header] + returned_data
        hlp.writecsv(final_data, location_to_store + filename_to_store + '.csv')
        weekly_data = gh.filterweeklydata(pid_dict, returned_data, week_dates,
                                          'all' if len(message_types) > 1 else message_types[0])
        hlp.dumpvariable(weekly_data, 'weekly_data.dict', location_to_store)
        summarized_sentiment = {}
        for pid in weekly_data:
            summarized_sentiment[pid] = {}
            participant_data = weekly_data[pid]
            for week_no in participant_data:
                summarized_sentiment[pid][week_no] = sentiment_analyzer.summarizesentiment(participant_data[week_no],
                                                                                           separate_in_out=True,
                                                                                           message_type=message_type)
        hlp.dumpvariable(summarized_sentiment, 'weekly_summarized_sentiment.dict', location_to_store)
        plt = plots()
        overlay_data = gh.createbullyingoverlay(catch_all_data, week_dates, ff)
        plt.plotweeklyprogression(summarized_sentiment, location_to_store, 'Sentiment Progress', 'Week',
                                  'Sentiment Value', sentiment_legend=['Positive', 'Negative', 'Neutral'],
                                  overlay_data=overlay_data)

    print 'done'

if __name__ == "__main__":
    main()