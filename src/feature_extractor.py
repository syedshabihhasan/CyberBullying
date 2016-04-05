import numpy as np
from math import floor
from basicInfo import privateInfo as pr


class raw_features:
    def get_in_out_data(self, data, pid):
        in_data = []
        out_data = []
        for datum in data:
            if datum[pr.m_source] == pid:
                # outgoing
                out_data.append(datum)
            if datum[pr.m_target] == pid:
                # incoming
                in_data.append(datum)
        return in_data, out_data

    def __get_senti_count(self, datum, counts):
        if datum[pr.m_pos] > datum[pr.m_neu]:
            if datum[pr.m_pos] > datum[pr.m_neg]:
                counts[0] += 1
            else:
                counts[2] += 1
        else:
            if datum[pr.m_neu] > datum[pr.m_neg]:
                counts[1] += 1
            else:
                counts[2] += 1
        return counts

    def get_week_degree(self, week_data, pid):
        in_data, out_data = self.get_in_out_data(week_data, pid)
        in_degree = set()
        out_degree = set()
        for datum in in_data:
            in_degree.add(datum[pr.m_source])
        for datum in out_data:
            out_degree.add(datum[pr.m_target])
        return len(in_degree), len(out_degree)

    def get_all_week_degree(self, all_week_data, pid):
        all_degrees = {}
        week_list = all_week_data.keys()
        week_list.sort()
        for week_no in week_list:
            all_degrees[week_no] = self.get_week_degree(all_week_data[week_no], pid)
        return all_degrees

    def get_senti_dist(self, week_data):
        counts = [0.0, 0.0, 0.0]
        if 0 == len(week_data):
            return counts
        else:
            for datum in week_data:
                counts = self.__get_senti_count(datum, counts)
            return counts

    def get_specific_week_ss(self, sentiment_score, current_week_no):
        specific_week_score = sentiment_score[current_week_no]
        if 1 == current_week_no:
            return specific_week_score
        else:
            for week_no in range(current_week_no - 1, 0, -1):
                exponent = -1 * (current_week_no - week_no)
                specific_week_score += 2 ** exponent * sentiment_score[week_no]
            return specific_week_score

    def get_sentiment_score(self, all_week_data, pid, separate_in_out=False):
        week_list = all_week_data.keys()
        week_list.sort()

        sentiment_scores = {}

        for week_no in week_list:
            week_data = all_week_data[week_no]
            if separate_in_out:
                in_data, out_data = self.get_in_out_data(week_data, pid)

                in_senti = self.get_senti_dist(in_data)
                in_total = sum(in_senti)
                sentiment_scores[week_no] = {}
                sentiment_scores[week_no]['In'] = 0 if in_total == 0 else \
                    (in_senti[0] / in_total) * self.factors[0] + \
                    (in_senti[1] / in_total) * self.factors[1] + \
                    (in_senti[2] / in_total) * self.factors[2]

                out_senti = self.get_senti_dist(out_data)
                out_total = sum(out_senti)
                sentiment_scores[week_no]['Out'] = 0 if out_total == 0 else \
                    (out_senti[0] / out_total) * self.factors[0] + \
                    (out_senti[1] / out_total) * self.factors[1] + \
                    (out_senti[2] / out_total) * self.factors[2]
            else:
                senti = self.get_senti_dist(week_data)
                total = sum(senti)
                sentiment_scores[week_no] = 0 if total == 0 else \
                    (senti[0] / total) * self.factors[0] + \
                    (senti[1] / total) * self.factors[1] + \
                    (senti[2] / total) * self.factors[2]

        return sentiment_scores

    def get_scoring_factors(self, data=None, seed=100):
        np.random.seed(seed)
        data = self.data if data is None else data
        keep_loop_running = True
        n = len(data)
        attempt = 1
        while keep_loop_running:
            print 'Attempt #' + str(attempt)
            rand_indices = np.random.random_integers(0, n-1, floor(n / 10))
            counts = [0, 0, 0]
            for idx in rand_indices:
                datum = data[idx]
                counts = self.__get_senti_count(datum, counts)
            if counts[0] > 0 and counts[1] > 0 and counts[2] > 0:
                keep_loop_running = False
                print 'Found factors!'
            else:
                attempt += 1

        total = sum(counts) + 0.0
        counts = np.array(counts) / total
        factors = [1.0, 1.0, 1.0]
        for idx in range(3):
            factors[idx] /= counts[idx]
        self.factors = factors
        print 'Factors', factors
        return factors, rand_indices

    def __init__(self, data):
        self.factors = None
        self.data = data
