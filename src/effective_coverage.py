import argparse
import helper as hlp
from nltk.corpus import stopwords
from nltk.tokenize import wordpunct_tokenize
from basicInfo import privateInfo as pr

def per_message_coverage(lexicon_data, message_data):
    lexicon_set = set()
    for datum in lexicon_data:
        lexicon_set.add(datum.split('\t')[0].lower())

    per_message_coverage = []
    stop_words_list = stopwords.words()
    idx = 0
    for datum in message_data:
        message = datum[pr.m_content]
        tokenized_message = wordpunct_tokenize(message)
        tokenized_message = [x for x in tokenized_message if x not in stop_words_list]
        covered = 0
        total = 0
        for token in tokenized_message:
            if token in lexicon_set:
                covered += 1
            total += 1
        per_cov = (covered+0.0)/total if not total == 0 else 0
        per_message_coverage.append((idx, covered, total, per_cov))
        idx += 1
    return per_message_coverage

def get_effective_coverage(lexicon_data, message_data):
    lexicon_set = set()
    for datum in lexicon_data:
        lexicon_set.add(datum.split('\t')[0].lower())

    message_set = set()
    stop_words_list = stopwords.words()
    for datum in message_data:
        message = datum[pr.m_content]
        tokenized_message = wordpunct_tokenize(message)
        tokenized_message = [x for x in tokenized_message if x not in stop_words_list]
        for token in tokenized_message:
            message_set.add(token.lower())

    common_words = message_set.intersection(lexicon_set)
    words_not_present = message_set.difference(lexicon_set)

    print 'total message words: ', len(message_set)
    print 'found in lexicon: ', len(common_words)
    print 'common words: ', common_words

    pct_words_covered = (len(common_words) + 0.0) / len(message_set)

    return pct_words_covered, words_not_present, common_words


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-m', '-M', type=str, required=True)
    parser.add_argument('-l', '-L', type=str, required=True)
    parser.add_argument('-o', '-O', type=str, required=False)

    args = parser.parse_args()

    message_data = hlp.recovervariable(args.m)
    lexicon_file = args.l
    output_file = args.o

    f = open(lexicon_file, 'r')
    lexicon_data = f.readlines()
    f.close()

    pct_words_covered, words_not_present, common_words = get_effective_coverage(lexicon_data, message_data)

    print 'pct words covered by vader: ', pct_words_covered
    print 'words not present: ', words_not_present

    if output_file is not None:
        output_text = ''
        for word in words_not_present.__iter__():
            output_text += word + '\n'
        with open(output_file, 'w') as f:
            f.write(output_text)


if __name__ == "__main__":
    main()
