import csv
import datetime as dt
from basicInfo import privateInfo as pr

class filterfields:
    data = []

    def converttodate(self, string_date, dt_format = '%Y-%m-%d %H:%M:%S'):
        return dt.datetime.strptime(string_date, dt_format)

    def filterbetweendates(self, start_date, end_date, data_to_work = []):
        filtered_data = []
        data_to_work = self.data if [] == data_to_work else data_to_work
        for data_row in data_to_work:
            cur_date = self.converttodate(data_row[pr.m_time_sent])
            if start_date <= cur_date and cur_date <= end_date:
                filtered_data.append(data_row)
        return filtered_data

    def setdata(self, data):
        self.data = data

    def __readfile(self, fname):
        temp_data = []
        f = open(fname, 'r')
        csv_obj = csv.reader(f, delimiter = ',')
        for row in csv_obj:
            temp_data.append(row)
        f.close()
        return temp_data

    def filterbyequality(self, field_no, to_equate):
        filtered_data = []
        for data_row in self.data:
            if to_equate in data_row[field_no]:
                filtered_data.append(data_row)
        print 'Original data: ', len(self.data), ' filtered data:', len(filtered_data)
        return filtered_data

    def __init__(self, fname):
        self.data = self.__readfile(fname)