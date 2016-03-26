import argparse
import matplotlib.pyplot as plt
from filterByField import filterfields
from basicInfo import privateInfo as pr

def combineandconvert(counts, labels, to_combine, to_change_to):
    combined_dict = {}
    for idx in range(len(labels)):
        label = labels[idx]
        if label.lower() in to_combine:
            label = to_change_to[to_combine.index(label.lower())]
        if label not in combined_dict:
            combined_dict[label] = 0
        combined_dict[label] += counts[idx]
    inverted_dict = dict((count, label) for label, count in combined_dict.iteritems())
    counts = inverted_dict.keys()
    counts.sort()
    labels = []
    for count in counts:
        labels.append(inverted_dict[count])
    return counts, labels




def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '-F', type=str, required=True,
                        help='filepath for message file')
    parser.add_argument('-o', '-O', type=str, required=True,
                        help='path to store figure in')
    parser.add_argument('-mt', '-MT', type=str, nargs='*')
    parser.add_argument('-c', '-C', type=str, nargs='*')

    args = parser.parse_args()
    message_filename = args.f
    output_location = args.o
    message_types = args.mt
    combine_change = args.c
    to_combine = None if combine_change is None else []
    to_change_to = None if combine_change is None else []
    if combine_change is not None:
        for idx in range(0, len(combine_change), 2):
            to_combine.append(combine_change[idx].lower())
            to_change_to.append(combine_change[idx+1])

    ff = filterfields(message_filename)
    ff.setdata(ff.getdata()[1:])
    message_types = ff.getuniqueelements(pr.m_type) if message_types is None else message_types
    numbers = []
    for message_type in message_types:
        numbers.append(len(ff.filterbyequality(pr.m_type, message_type)))
    if to_combine is not None:
        numbers, message_types = combineandconvert(numbers, message_types, to_combine, to_change_to)
    for idx in range(len(numbers)):
        print message_types[idx], numbers[idx]
    fig = plt.figure(figsize=[12, 12])
    ax = fig.add_subplot(111)
    tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]
    for i in range(len(tableau20)):
        r, g, b = tableau20[i]
        tableau20[i] = (r / 255., g / 255., b / 255.)
    patches, texts, autotexts = ax.pie(numbers, labeldistance=1.05,
                                       colors=tableau20, autopct='%1.1f%%', startangle=90)
    for idx in range(len(texts)):
        texts[idx].set_fontsize(20)
    for idx in range(len(autotexts)):
         autotexts[idx].set_fontsize(20)
    plt.legend(labels=message_types, loc='upper right', fontsize=20, bbox_to_anchor=(1.05, 1))
    plt.savefig(output_location, bbox_inches='tight')

if __name__ == "__main__":
    main()