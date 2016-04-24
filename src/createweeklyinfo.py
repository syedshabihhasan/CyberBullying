import datetime as dt
import helper as hlp
from filterByField import filterfields
from basicInfo import surveyInfo as sr
from basicInfo import privateInfo as pr


class weeklyinfo:
    def __getsurveyinstances(self, filepath, ff):
        survey_data = hlp.readcsv(filepath)
        survey_data = survey_data[1:]
        survey_dates = set()
        for datum in survey_data:
            survey_dates.add(ff.converttodate(datum[sr.s_time]))
        survey_dates = list(survey_dates)
        survey_dates.sort()
        return survey_dates

    def __createweeks(self, survey_dates, ff):
        weekno = 1
        week_info = {}
        first_l = True
        for idx in range(len(survey_dates)):
            if first_l:
                start_date = ff.resetdate(ff.converttodate(pr.start_datetime) - dt.timedelta(days=7),
                                          should_be_zero=True)
                end_date = ff.resetdate(survey_dates[idx] - dt.timedelta(days=1), should_be_zero=False)
                first_l = False
            else:
                start_date = ff.resetdate(survey_dates[idx - 1], should_be_zero=True)
                end_date = ff.resetdate(survey_dates[idx] - dt.timedelta(days=1), should_be_zero=False)
            week_info[weekno] = (start_date, end_date)
            weekno += 1
        start_date = ff.resetdate(survey_dates[-1], should_be_zero=True)
        end_date = ff.resetdate(ff.converttodate(pr.end_datetime), should_be_zero=False)
        week_info[weekno] = (start_date, end_date)
        return week_info

    def getweeklyfo(self, filepath):
        ff = filterfields()
        survey_dates = self.__getsurveyinstances(filepath, ff)
        week_info = self.__createweeks(survey_dates, ff)
        return week_info

    def __init__(self):
        pass
