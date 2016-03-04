import argparse
import helper as hlp
from surveyprocessing import surveystats
from basicInfo import surveyInfo as sInfo


def filtersurvey(dict_path, to_store_path, qno, answers):
    data = hlp.recovervariable(dict_path)
    survey_obj = surveystats(data)
    if None == answers:
        res = survey_obj.processdict(sInfo.surveyQType[qno])
    else:
        res = {}
        for ans in answers:
            res[ans] = survey_obj.processdict(sInfo.surveyQType[qno], ans)
    hlp.dumpvariable(res, 'res_survey_stat.data', to_store_path)


def main():
    parser = argparse.ArgumentParser('Script to process the survey data')
    parser.add_argument('-i', '-I', type=str, required=True,
                        help='Path to the input dictionary')
    parser.add_argument('-q', '-Q', type=str, required=True,
                        help='Q Types - seenB: seen bullying, didB: did bullying, other: others used my account, '
                             'wasB: was bullied')
    parser.add_argument('-a', '-A', type=str, required=False, nargs='*',
                        help='optional, what answers to filter for')
    parser.add_argument('-s', '-S', type=str, required=True,
                        help='path to save the variables at, with leading /')
    args = parser.parse_args()

    ip_filepath = args.i
    qno = args.q
    answers = args.a
    filepath = args.s
    filtersurvey(ip_filepath, filepath, qno, answers)


if __name__ == "__main__":
    main()
