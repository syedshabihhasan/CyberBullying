from nltk.sentiment.vader import SentimentIntensityAnalyzer

from basicInfo import privateInfo as pr


class vadersenti:
    sentiment_embedded = False

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
