import helper as hlp
from basicInfo import privateInfo as pr
from basicInfo import new_dataset as nd
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '-D', help='Dataset', required=True)
    parser.add_argument('-n', '-N', help='Flag to indicate new dataset', action='store_true')
    args = parser.parse_args()
    dataset_file = args.d
    new_dataset = args.n
    dataset = hlp.readcsv(dataset_file, delimiter_sym=',', remove_first=True)
    type_dict = {}
    for datum in dataset:
        m_type = datum[nd.m_type] if new_dataset else datum[pr.m_type]
        if m_type not in type_dict:
            type_dict[m_type] = 0
        type_dict[m_type] += 1
    sorted_types = type_dict.keys()
    sorted_types.sort()
    total = sum(type_dict.values())
    for keyn in sorted_types:
        print keyn + ': ' + str(type_dict[keyn])
    print 'total: '+str(total)


if __name__ == "__main__":
    main()
