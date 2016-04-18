import argparse
import helper as hlp
from vaderpolarity import vadersenti

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-m', '-M', required=True,
                        help='Message file')
    parser.add_argument('-p', '-P', action='store_true')
    parser.add_argument('-s', '-S', required=True,
                        help='filename to store polarity in, no extension needed')
    parser.add_argument('-f', '-F', required=True,
                        help='folder to store the files in, ending with /')

    args = parser.parse_args()
    messagefile = args.m
    location_to_store = args.f
    file_to_store = args.s
    separate_sentiment = args.p

    message_data = hlp.readcsv(messagefile)
    message_header = message_data[0]
    message_data = message_data[1:]

    vader = vadersenti(data=message_data)
    data = vader.compilesentiment(separate_sentiment_list=separate_sentiment)
    if separate_sentiment:
        hlp.dumpvariable(data, file_to_store+'.list', location_to_store)
    else:
        message_header.append('pos')
        message_header.append('neg')
        message_header.append('neu')
        message_header.append('compound')
        final_data = [message_header] + data
        hlp.writecsv(final_data, location_to_store + file_to_store + '.csv', delimiter_sym=',')


if __name__ == "__main__":
    main()