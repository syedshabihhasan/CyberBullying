import sqlite3
from basicInfo import surveyInfo as sInfo


class surveys:
    def __normalizedata(self, data):
        ndata = []
        for row in data:
            temp = []
            for dVal in row:
                temp.append(str(dVal))
            ndata.append(temp)
        return ndata

    def importsqlascsv(self, f_sql_path, tablename):
        print 'Connecting to the DB'
        conn = sqlite3.connect(f_sql_path)
        cursor = conn.execute('select * from ' + tablename)
        print 'Extracting the table'
        fieldnames = [[desc[0] for desc in cursor.description]]
        data = []
        for datum in cursor:
            data.append(datum)
        data = fieldnames + data
        data = self.__normalizedata(data)
        print 'Done'
        return data

    def datatodict(self, data):
        data = data[1:]
        survey_dict = {}
        for datum in data:
            if datum[sInfo.s_participant] not in survey_dict:
                survey_dict[datum[sInfo.s_participant]] = {}
            if datum[sInfo.s_no] not in survey_dict[datum[sInfo.s_participant]]:
                survey_dict[datum[sInfo.s_participant]][datum[sInfo.s_no]] = []
            survey_dict[datum[sInfo.s_participant]][datum[sInfo.s_no]].append(datum)
        return survey_dict

    def interpretanswers(self, data, onlyWithResponse=False):
        columns = data[0]
        ndata = data[1:]
        toUse = []
        for datum in ndata:
            qInfo = sInfo.surveyQA[datum[sInfo.s_qno]]
            toAppend = []
            for idx in range(sInfo.s_ans1, sInfo.s_ans5 + 1):
                if '1' == datum[idx]:
                    toAppend.append(qInfo[idx - sInfo.s_ans1])
            if [] == toAppend:
                if onlyWithResponse:
                    continue
                toAppend.append('NA')
            toUse.append(datum[0:sInfo.s_ans1] + toAppend)
        data = [columns] + toUse
        return data

    def __init__(self):
        pass


class surveystats:
    data = {}

    def processdict(self, qno, ans='', toWork = []):
        toReturn = {} if [] == toWork else []
        if [] == toWork:
            for participant in self.data.keys():
                pdata = self.data[participant]
                for sno in pdata.keys():
                    for datum in pdata[sno]:
                        if datum[sInfo.s_qno] == qno:
                            if '' == ans:
                                #toReturn.append(datum)
                                if participant not in toReturn:
                                    toReturn[participant] = {}
                                if sno not in toReturn[participant]:
                                    toReturn[participant][sno] = []
                                toReturn[participant][sno] = pdata[sno]
                            else:
                                for idx in range(sInfo.s_ans1, len(datum)):
                                    if ans in datum[idx]:
                                        if participant not in toReturn:
                                            toReturn[participant] = {}
                                        if sno not in toReturn[participant]:
                                            toReturn[participant][sno] = []
                                        toReturn[participant][sno] = pdata[sno]
        else:
            for datum in toWork:
                if datum[sInfo.s_qno] == sInfo.surveyQType[qno]:
                    if '' == ans:
                        toReturn.append(datum)
                    else:
                        for idx in range(sInfo.s_ans1, len(datum)):
                            if ans in datum[idx]:
                                toReturn.append(datum)
        return toReturn

    def participantsreporting(self):
        return len(self.data.keys()), self.data.keys()

    def whowitnessedbullying(self, toWork=[]):
        if [] == toWork:
            witnesses = self.processdict(sInfo.surveyQType['seenB'])
        else:
            witnesses = self.processdict(sInfo.surveyQType['seenB'], toWork = toWork)
        return witnesses

    def whodidbullying(self, toWork=[]):
        if [] == toWork:
            who_bullied = self.processdict(sInfo.surveyQType['didB'], ans='yes')
        else:
            who_bullied = self.processdict(sInfo.surveyQType['didB'], ans='yes', toWork = toWork)
        return who_bullied

    def whowasbullied(self, toWork=[]):
        if [] == toWork:
            who_was_bullied = self.processdict(sInfo.surveyQType['wasB'])
        else:
            who_was_bullied = self.processdict(sInfo.surveyQType['wasB'], toWork = toWork)
        return who_was_bullied

    def updatedata(self, data):
        self.data = data

    def __init__(self, data):
        self.data = data
