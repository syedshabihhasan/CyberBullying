import sys, pickle

def main():
    pid_dict = pickle.load(open(sys.argv[1], 'rb'))
    pid_dict = pid_dict[sys.argv[5]]
    hash_phone = pickle.load(open(sys.argv[2], 'rb'))
    phone_pid = pickle.load(open(sys.argv[3], 'rb'))
    toLookFor = ''
    notFound = []
    for h_val in pid_dict.keys():
        try:
            toLookFor += str(phone_pid[hash_phone[h_val]]) + '\n'
        except:
            print 'Error! looking for hash val: ', h_val, 'could not find anything in dict, moving on'
            notFound.append(h_val)
            continue
    print 'total not found: ', len(notFound), ' total looked: ', len(pid_dict.keys())
    print notFound
    f = open(sys.argv[4], 'w')
    f.write(toLookFor)
    f.close()
if __name__ == "__main__":
    if not (6 == len(sys.argv)):
        print 'Usage: python getpids.py <path to pid_dict> <path to hash_phone_dict> <path to phone_pid_dict> ' \
              '<path to store> <type of individual>'
    else:
        main()