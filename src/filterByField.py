import csv

class filterfields:
    data = []

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
            if to_equate == data_row[field_no]:
                filtered_data.append(data_row)
        return filtered_data

    def __init__(self, fname):
        self.data = self.__readfile(fname)