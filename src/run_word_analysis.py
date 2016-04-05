import argparse
import helper as hlp
from word_analysis import canonical_form

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-w', '-W', type=str, required=True)
    parser.add_argument('-o', '-O', type=str, required=True)

    args = parser.parse_args()

    word_file = args.w
    output_folder = args.o

    f = open(word_file, 'r')
    d = f.readlines()
    f.close()

    word_list = [x.strip() for x in d]

    cf = canonical_form(word_list)
    words_in_dict, words_not_in_dict = cf.words_in_dict()
    print 'Total word list: ', len(word_list), ' Words present in dict: ', len(words_in_dict), \
        ' Not in dict: ', len(words_not_in_dict)
    to_write_in_dict = ''
    for word in words_in_dict:
        to_write_in_dict += word +'\n'
    cf.set_word_list(words_not_in_dict)
    correct_form, missed_words = cf.get_canonical_form()
    print 'Could not find canonical forms for ', len(missed_words), ' out of a total of ', len(words_not_in_dict)
    to_write_canonical = ''
    to_substitute = {}
    for right_form, other_values in correct_form.iteritems():
        to_write_canonical += right_form
        for word in other_values:
            to_write_canonical += ' '+word
            to_substitute[word] = right_form
        to_write_canonical += '\n'
    to_write_missed = ''
    for word in missed_words:
        to_write_missed += word + '\n'

    with open(output_folder + 'found_in_dict.txt', 'w') as f:
        f.write(to_write_in_dict)

    with open(output_folder + 'cannonical_form.txt', 'w') as f:
        f.write(to_write_canonical)

    with open(output_folder + 'not_found_anywhere.txt', 'w') as f:
        f.write(to_write_missed)

    hlp.dumpvariable(to_substitute, 'substitution_dict.dict', output_folder)

    print 'Done writing...'

if __name__ == "__main__":
    main()