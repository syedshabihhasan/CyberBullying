import argparse
import helper as hlp
from surveyprocessing import surveystats
from basicInfo import surveyInfo as sInfo


def filtersurvey(dict_path, qno, answers, is_data = False):
    data = dict_path if is_data else hlp.recovervariable(dict_path)
    survey_obj = surveystats(data)
    if None == answers:
        res = survey_obj.processdict(sInfo.surveyQType[qno])
    else:
        res = {}
        for ans in answers:
            res[ans] = survey_obj.processdict(sInfo.surveyQType[qno], ans)
    return res


def main():
    parser = argparse.ArgumentParser('Script to process the survey data')
    parser.add_argument('-i', '-I', type=str, required=True,
                        help='Path to the input dictionary')
    parser.add_argument('-q', '-Q', type=str, required=True, nargs=1,
                        help='Q Types - seenB: seen bullying, didB: did bullying, other: others used my account, '
                             'wasB: was bullied')
    parser.add_argument('-a', '-A', type=str, required=False, nargs='*',
                        help='optional, what answers to filter for')
    parser.add_argument('-s', '-S', type=str, required=True,
                        help='path to save the variables at, with leading /')
    parser.add_argument('-f', '-F', type=str)
    parser.add_argument('-f1q', '-F1Q', type=str, nargs = 1,
                        help='first level filter question')
    parser.add_argument('-f1a', '-F1A', type=str, nargs = '*',
                        help='first level filter answers', required=False)
    args = parser.parse_args()

    ip_filepath = args.i
    qno = args.q[0]
    answers = args.a
    op_filepath = args.s
    op_filename = args.f
    filterQ = args.f1q
    filterA = args.f1a
    print 'Processing...'
    res = filtersurvey(ip_filepath, qno, answers)
    to_save = {}
    print 'done'
    if not (None == filterQ):
        filterQ = filterQ[0]
        print 'second level filtering argument exists, filtering...'
        for ans in res.keys():
            temp = filtersurvey(res[ans], filterQ, filterA, is_data=True)
            for ans1 in temp.keys():
                to_save[(ans, ans1)] = temp[ans1]
        print 'done'
    else:
        to_save = res
    hlp.dumpvariable(to_save, op_filename, op_filepath)

if __name__ == "__main__":
    main()
