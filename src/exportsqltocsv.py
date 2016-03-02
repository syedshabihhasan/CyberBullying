import sqlite3, sys, csv


def main(f_sql_path, tablename, storage_path):
    print 'Connecting to the DB'
    conn = sqlite3.connect(f_sql_path)
    cursor = conn.execute('select * from '+tablename)
    print 'Extracting the table'
    fieldnames = [[desc[0] for desc in cursor.description]]
    data = []
    for datum in cursor:
        data.append(datum)
    data = fieldnames + data
    if '' is not storage_path:
        f = open(storage_path, 'w')
        csv_obj = csv.writer(f, delimiter = ',')
        print 'Writing...'
        csv_obj.writerows(data)
        f.close()
        print 'done!'
    else:
        return data

if __name__ == "__main__":
    if not (4 == len(sys.argv)):
        print 'Usage: python exportsqltocsv.py <path to sqlite db> <table name> <path to store csv file>'
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
