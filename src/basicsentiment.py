from sentimentanalysis import sentiment
from filterByField import filterfields
from basicInfo import twitterdataset as td
from basicInfo import privateInfo as pr
import helper as hlp
import random

data = hlp.readcsv('../ignore_data/Sentiment_Twitter.csv')
data = data[1:]
ff = filterfields('../ignore_data/messages.csv')
smsdata = ff.filterbyequality(pr.m_type, 'sms')

k = len(data)
l = len(smsdata)
seed = 254
random.seed(seed)
tr_n = 1000000
ts_n = 30
idx = 0
tr_before = []
ts_before = []

while idx < tr_n:
    i = random.randint(0, k)
    datum = data[i]
    tweet_type = td.sentiment_dict[datum[td.sentiment]]
    tweet_content = datum[td.sentiment_text]
    tr_before.append((tweet_content, tweet_type))
    idx += 1

random.seed(seed)
# idx = 0
for datum in smsdata:
    #i = random.randint(0, l)
    ts_before.append(datum[pr.m_content])
    # tweet_type = td.sentiment_dict[datum[td.sentiment]]
    # tweet_content = datum[td.sentiment_text]
    # ts_before.append((tweet_content, tweet_type))
    # idx += 1

data = []

s_obj = sentiment()
tr_set = s_obj.createtrainingset(tr_before)
ts_set = s_obj.createtestingset(ts_before, testing_has_labels=False)
print 'classifier training'
s_obj.trainclassifier(tr_set)
predictions = []
feature_set = []
print 'making predictions'
# print 'Accuracy: ', s_obj.getaccuracy(ts_set)
idx = 1
for datum in ts_set:
    res = s_obj.individualprediction(datum)
    print idx, ts_before[idx-1], '***pos: ', res.prob('pos'), ' *** neg: ', res.prob('neg')
    smsdata[idx-1].append(res)
    idx += 1

hlp.dumpvariable(smsdata, 'results')
print 'woot!'