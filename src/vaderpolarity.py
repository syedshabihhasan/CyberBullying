from __future__ import division
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from basicInfo import privateInfo as pr


class vadersenti:
    sentiment_embedded = False

    def summarizesentiment(self, data, separate_in_out=False, message_type='sms'):
        to_return = [0, 0, 0] if not separate_in_out else [[0, 0, 0], [0, 0, 0]]
        total_count = 0 if not separate_in_out else [0, 0]
        if 0 < len(data):
            for data_row in data:
                if not separate_in_out:
                    to_return[0] += data_row[pr.m_pos]
                    to_return[1] += data_row[pr.m_neg]
                    to_return[2] += data_row[pr.m_neu]
                    total_count += 1
                else:
                    if pr.participant[message_type] in data_row[pr.m_source_type]:
                        # participant is source, so outgoing
                        to_return[1][0] += data_row[pr.m_pos]
                        to_return[1][1] += data_row[pr.m_neg]
                        to_return[1][2] += data_row[pr.m_neu]
                        total_count[1] += 1
                    if pr.participant[message_type] in data_row[pr.m_target_type]:
                        # participant is target, so incoming
                        to_return[0][0] += data_row[pr.m_pos]
                        to_return[0][1] += data_row[pr.m_neg]
                        to_return[0][2] += data_row[pr.m_neu]
                        total_count[0] += 1
            if not separate_in_out:
                for idx in range(3):
                    total_count = 1 if total_count == 0 else total_count
                    to_return[idx] = to_return[idx]/total_count
            else:
                for idx in range(3):
                    total_count[0] = 1 if total_count[0] == 0 else total_count[0]
                    total_count[1] = 1 if total_count[1] == 0 else total_count[1]
                    to_return[0][idx] = to_return[0][idx]/total_count[0]
                    to_return[1][idx] = to_return[1][idx]/total_count[1]
        return to_return

    def compilesentiment(self, field_no=pr.m_content, separate_sentiment_list=True):
        if self.sentiment_embedded:
            return self.data
        sentiment_compilation = [] if separate_sentiment_list else None
        for idx in range(len(self.data)):
            datum = self.data[idx]
            temp_senti = self.senti_analyzer.polarity_scores(datum[field_no])
            if separate_sentiment_list:
                sentiment_compilation.append(temp_senti)
            else:
                datum.extend([temp_senti['pos'], temp_senti['neg'], temp_senti['neu'], temp_senti['compound']])
                self.data[idx] = datum
        self.sentiment_embedded = separate_sentiment_list == False
        return sentiment_compilation if separate_sentiment_list else self.data

    def setdata(self, data):
        self.data = data

    def __init__(self, data=None):
        self.senti_analyzer = SentimentIntensityAnalyzer()
        self.setdata(data)
