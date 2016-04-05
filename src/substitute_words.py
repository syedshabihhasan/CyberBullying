import argparse
import numpy as np
import time
import helper as hlp
from basicInfo import privateInfo as pr
import effective_coverage as ec
import matplotlib.pyplot as plt
from probabilistic_spellcheck import pspell

def substitute_words(message, sub_dict, words_used):
    # i know that the thing is inefficient, but this way I preserve the structure of the message
    n = 0
    for word in sub_dict.keys():
        if word in message:
            message.replace(word, sub_dict[word])
            n += 1
            words_used.add(sub_dict[word])
    return message, n, words_used

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-m', '-M', type=str, required=True)
    parser.add_argument('-b', '-B', type=str, required=True)
    parser.add_argument('-d', '-D', type=str, required=True)
    parser.add_argument('-l', '-L', type=str, required=True)
    parser.add_argument('-o', '-O', type=str, required=False)

    args = parser.parse_args()

    message_data = hlp.recovervariable(args.m)
    substitution_dict = hlp.recovervariable(args.d)
    lexicon_file = args.l
    output_folder = args.o

    f = open(lexicon_file, 'r')
    lexicon_data = f.readlines()
    f.close()

    # pct_words_covered_old, words_not_present_old, common_words_old = ec.get_effective_coverage(lexicon_data, message_data)
    # per_message_coverage_old = ec.per_message_coverage(lexicon_data, message_data)
    # box_old = [x[-1] for x in per_message_coverage_old]

    total_subs_made = 0
    words_used = set()
    for idx in range(len(message_data)):
        datum = message_data[idx]
        message = datum[pr.m_content]
        message, n, words_used = substitute_words(message, substitution_dict, words_used)
        datum[pr.m_content] = message
        message_data[idx] = datum
        total_subs_made += n
    print 'Made a total of ', total_subs_made, ' substitutions'
    print words_used
    print 'Calculating effective coverage'

    pct_words_covered, words_not_present, common_words = ec.get_effective_coverage(lexicon_data, message_data)
    per_message_coverage_new = ec.per_message_coverage(lexicon_data, message_data)
    # box_new = [x[-1] for x in per_message_coverage_new]

    print 'pct words covered by vader: ',  pct_words_covered
    print 'words not present: ', words_not_present
    if output_folder is not None:
        hlp.dumpvariable(words_not_present, 'words_not_present_after_canon.list', output_folder)

    # big_folder = args.b
    # psc = pspell(big_folder)
    # changes_found = []
    # time_taken = []
    # for word in words_not_present:
    #     start_time = time.time()
    #     mpw = psc.get_most_probable_word(word)
    #     time_taken.append(time.time() - start_time)
    #     changes_found.append([mpw, word])
    #
    # print 'Avg: ', np.mean(time_taken), ' std: ', np.std(time_taken)

    # plt.boxplot([box_old, box_new])
    # plt.show()

if __name__ == "__main__":
    main()