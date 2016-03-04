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

    ndata_wR = s_obj.interpretanswers(data, True)
    hlp.dumpvariable(ndata_wR, 'survey_list_with_response_interpret.list', variable_path)
    hlp.writecsv(ndata_wR, variable_path+'survey_list_with_response_interpret.csv')

    data_dict = s_obj.datatodict(ndata)
    hlp.dumpvariable(data_dict, 'survey_dict_interpret.dict', variable_path)

    data_wR_dict = s_obj.datatodict(ndata_wR)
    hlp.dumpvariable(data_wR_dict, 'survey_dict_with_response_interpret.dict', variable_path)


if __name__ == "__main__":
    if not (3 == len(sys.argv)):
        print 'Usage: python runsurvey.py <path to sql db> <path to save variables, ending with />'
    else:
        main(sys.argv[1], sys.argv[2])
