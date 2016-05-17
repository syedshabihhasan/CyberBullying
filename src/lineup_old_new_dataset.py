import argparse
import helper as hlp
import numpy as np
import scipy.spatial.distance as dist
from collections import Counter
from basicInfo import new_dataset as nd
from basicInfo import privateInfo as pr
from filterByField import filterfields


def remove_punc(sentence, punc_to_remove=None):
    if punc_to_remove is None:
        punc_to_remove = {'.': ' ', ',': ' '}
    for punc in punc_to_remove:
        sentence = sentence.replace(punc, punc_to_remove[punc])
    return sentence


def word_vectors(sentence1, sentence2):
    word_count1 = Counter(sentence1.split(' '))
    word_count2 = Counter(sentence2.split(' '))
    word_set = set(word_count1.keys()).union(set(word_count2.keys()))
    vec1 = []
    vec2 = []
    for word in word_set:
        vec1.append(0 if word not in word_count1 else word_count1[word])
        vec2.append(0 if word not in word_count2 else word_count2[word])
    return vec1, vec2


def cosine_similarity(vec1, vec2):
    return 1 - dist.cosine(np.array(vec1), np.array(vec2))


def generate_new_dataset_dictionary(new_dataset, use_m_id=False):
    ff = filterfields()
    new_dataset_dictionary = {}
    for datum in new_dataset:
        if not use_m_id:
            src = datum[nd.m_source]
            trg = datum[nd.m_target]
            if (src, trg) not in new_dataset_dictionary:
                new_dataset_dictionary[(src, trg)] = {}
            message_type = datum[nd.m_type]
            if message_type not in new_dataset_dictionary[(src, trg)]:
                new_dataset_dictionary[(src, trg)][message_type] = {}
            create_time = datum[nd.m_timecreated]
            create_time_dt = ff.converttodate(create_time)
            if create_time_dt not in new_dataset_dictionary[(src, trg)][message_type]:
                new_dataset_dictionary[(src, trg)][message_type][create_time_dt] = []
            new_dataset_dictionary[(src, trg)][message_type][create_time_dt].append(datum)
        else:
            new_dataset_dictionary[datum[nd.msg_id]] = datum
    return new_dataset_dictionary


def message_exists(datum_to_check, new_dataset_dictionary, ff):
    src = datum_to_check[pr.m_source]
    dst = datum_to_check[pr.m_target]
    m_type = datum_to_check[pr.m_type]
    create_time = datum_to_check[pr.m_time_sent]
    create_time_dt = ff.converttodate(create_time)
    old_message = datum_to_check[pr.m_content]
    if 'twitter' in m_type:
        if dst == 'None':
            dst = str(hash('Twitter'))
    if (src, dst) in new_dataset_dictionary:
        if m_type in new_dataset_dictionary[(src, dst)]:
            if create_time_dt in new_dataset_dictionary[(src, dst)][m_type]:
                message_list = new_dataset_dictionary[(src, dst)][m_type][create_time_dt]
                best_cosine = []
                for message_datum in message_list:
                    new_message = message_datum[nd.m_content]
                    new_vec, old_vec = word_vectors(remove_punc(new_message), remove_punc(old_message))
                    cosine_sim_score = cosine_similarity(new_vec, old_vec)
                    best_cosine.append([cosine_sim_score, message_datum[nd.msg_id]])
                sorted_cosines = sorted(best_cosine, key=lambda cosine_id: cosine_id[0])
                return True, sorted_cosines[-1]
            else:
                return False, 'No message at the given time'
        else:
            return False, 'Message type does not exist for Source-Destination pair'
    else:
        return False, 'Source-Destination pair does not exist'


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-o', '-O', help='Old Dataset', required=True)
    parser.add_argument('-n', '-N', help='New Dataset', required=True)
    parser.add_argument('-f', '-F', help='Folder to store results in, ending with /', required=True)

    args = parser.parse_args()

    old_dataset_file = args.o
    new_dataset_file = args.n
    location_to_store = args.f

    print 'Reading data from arguments...'
    old_dataset = hlp.readcsv(old_dataset_file, delimiter_sym=',', remove_first=True)
    new_dataset = hlp.readcsv(new_dataset_file, delimiter_sym=',')
    new_dataset_dictionary = generate_new_dataset_dictionary(new_dataset[1:])
    new_dataset_msg_id_dictionary = generate_new_dataset_dictionary(new_dataset[1:], use_m_id=True)

    print 'Finding mapping...'
    mapping_dict = {}
    inverted_mapping_dict = {}
    missed_dict = {}
    ff = filterfields()
    for datum in old_dataset:
        m_result, msg_val = message_exists(datum, new_dataset_dictionary, ff)
        if m_result:
            mapping_dict[datum[pr.msg_id]] = msg_val
            if msg_val[1] not in inverted_mapping_dict:
                inverted_mapping_dict[msg_val[1]] = []
            inverted_mapping_dict[msg_val[1]].append(datum[pr.msg_id])
        else:
            missed_dict[datum[pr.msg_id]] = msg_val

    print 'Creating new dataset with mappings...'
    new_dataset_header = new_dataset[0]
    new_dataset_header.extend(['Old Message IDs'])
    final_dataset = [new_dataset_header]
    for new_msg_id in new_dataset_msg_id_dictionary.keys():
        datum = new_dataset_msg_id_dictionary[new_msg_id]
        old_msg_id = [''] if new_msg_id not in inverted_mapping_dict else inverted_mapping_dict[new_msg_id]
        datum.extend(old_msg_id)
        final_dataset.append(datum)

    print 'Writing data...'
    hlp.writecsv(final_dataset, location_to_store+'new_old_mapped_hashed_dataset.csv', delimiter_sym=',')
    mapping_dict_list = [[x, mapping_dict[x][0], mapping_dict[x][1]] for x in mapping_dict]
    mapping_header = [['old_id', 'cosine_val', 'new_id']]
    mapping_header.extend(mapping_dict_list)
    hlp.writecsv(mapping_header, location_to_store+'old_to_new_mapping.csv', delimiter_sym=',')
    missed_dict_list = [[x, missed_dict[x]] for x in missed_dict]
    missed_header = [['old_id', 'Reason']]
    missed_header.extend(missed_dict_list)
    hlp.writecsv(missed_header, location_to_store+'old_not_found.csv', delimiter_sym=',')
    print 'TADAA!!!'

if __name__ == "__main__":
    main()