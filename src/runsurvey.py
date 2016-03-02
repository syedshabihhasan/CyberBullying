import sys
from surveyprocessing import surveys
import helper as hlp

def main(sql_path, variable_path):
    s_obj = surveys()
    data = s_obj.importsqlascsv(sql_path, 'survey')
    hlp.dumpvariable(data, 'survey_list.list', variable_path)
    hlp.writecsv(data, variable_path+'survey_list.csv')
    ndata = s_obj.interpretanswers(data)
    hlp.dumpvariable(ndata, 'survey_list_interpret.list', variable_path)
    hlp.writecsv(ndata, variable_path+'survey_list_interpret.csv')
    data_dict = s_obj.datatodict(ndata)
    hlp.dumpvariable(data_dict, 'survey_dict_interpret.dict', variable_path)
    print 'done'

if __name__ == "__main__":
    if not (3 == len(sys.argv)):
        print 'Usage: python runsurvey.py <path to sql db> <path to save variables, ending with />'
    else:
        main(sys.argv[1], sys.argv[2])
