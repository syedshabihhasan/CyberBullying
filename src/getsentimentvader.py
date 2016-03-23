import argparse
import helper as hlp
from filterByField import filterfields
from basicInfo import privateInfo as pr
from vaderpolarity import vadersenti

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

    args = parser.parse_args()
    message_file = args.m
    message_types = args.mt
    filename_to_store = args.f
    location_to_store = args.s
    separate_polarity_score = args.p

    ff = filterfields(message_file)
    data = []
    for message_type in message_types:
        data.extend(ff.filterbyequality(pr.m_type, message_type))
    sentiment_analyzer = vadersenti(data[1:])
    returned_data = sentiment_analyzer.compilesentiment(pr.m_content, separate_sentiment_list=separate_polarity_score)
    if separate_polarity_score:
        hlp.dumpvariable(returned_data, filename_to_store+'.data')
    else:
        header = pr.message_header + ['pos', 'neg', 'neu', 'compound']
        final_data = [header] + returned_data
        hlp.writecsv(final_data, location_to_store + filename_to_store + '.csv')
    print 'done'

if __name__ == "__main__":
    main()