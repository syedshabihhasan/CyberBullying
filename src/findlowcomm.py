import argparse
import helper as hlp

def main():
    parser = argparse.ArgumentParser('Filter out people who have 0 communication weeks greater than the threshold')

    parser.add_argument('-f', '-F', type=str, required=True)
    parser.add_argument('-ti', '-TI', type=int, required=True,
                        help='Incoming threshold')
    parser.add_argument('-to', '-TO', type=int, required=True,
                        help='Outgoing threshold')
    parser.add_argument('-s', '-S', type=str, required=True,
                        help='storage folder with /')
    parser.add_argument('-sf', '-SF', type=str, required=True,
                        help='file name for storage')

    args = parser.parse_args()

    flipped_dict = hlp.recovervariable(args.f)
    incoming_th = args.ti
    outgoing_th = args.to
    location_to_store = args.s
    filename = args.sf

    to_remove = []
    for pid in flipped_dict:
        if flipped_dict[pid][0] >= incoming_th and flipped_dict[pid][1] >= outgoing_th:
            to_remove.append(pid)
            print 'REMOVED: ', pid, flipped_dict[pid]
        else:
            print 'NOT REMOVED: ', pid, flipped_dict[pid]

    print 'Removed ', len(to_remove), ' out of a total of ', len(flipped_dict.keys()),  'participants'

    hlp.dumpvariable(to_remove, filename, location_to_store)
if __name__ == "__main__":
    main()