import sys
import csv
from filterByField import filterfields

def main():
    ff = filterfields(sys.argv[1])
    print 'filtering...'
    sms_data = ff.filterbyequality(1, 'sms')
    print('done')
    f = open(sys.argv[2], 'w')
    csv_obj = csv.writer(f, delimiter = ',')
    print 'writing...'
    csv_obj.writerows(sms_data)
    print 'done'
    f.close()

if __name__ == "__main__":
    if not (3 == len(sys.argv)):
        print 'Usage: python runMe.py <csv filename> <path for output file>'
    else:
        main()