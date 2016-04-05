import helper as hlp
from collections import Counter

class pspell:

    def __getvalue(self, custom):
        return custom[1]

    def __keyboard_neighborhood(self):
        neighborhood = {
            'q': ['w', 'a'],
            'w': ['q', 'e', 'a', 's'],
            'e': ['w', 'r', 's', 'd'],
            'r': ['e', 't', 'd', 'f'],
            't': ['r', 'y', 'f', 'g'],
            'y': ['t', 'u', 'g', 'h'],
            'u': ['y', 'i', 'h', 'j'],
            'i': ['u', 'o', 'j', 'k'],
            'o': ['i', 'p', 'k', 'l'],
            'p': ['o', 'l'],
            'a': ['q', 'w', 's', 'z'],
            's': ['w', 'e', 'a', 'd', 'z', 'x'],
            'd': ['e', 'r', 's', 'f', 'x', 'c'],
            'f': ['r', 't', 'd', 'g', 'c', 'v'],
            'g': ['t', 'y', 'f', 'h', 'v', 'b'],
            'h': ['y', 'u', 'g', 'j', 'b', 'n'],
            'j': ['u', 'i', 'h', 'k', 'n', 'm'],
            'k': ['i', 'o', 'j', 'l', 'm'],
            'l': ['o', 'p', 'k'],
            'z': ['a', 's', 'x'],
            'x': ['s', 'd', 'z', 'c'],
            'c': ['d', 'f', 'x', 'v'],
            'v': ['f', 'g', 'c', 'b'],
            'b': ['g', 'h', 'v', 'n'],
            'n': ['h', 'j', 'b', 'm'],
            'm': ['j', 'k', 'n']
        }

        return neighborhood

    def edit_distance_1(self, word):
        deleted = []
        replaced = []
        swapped = []
        inserted = []
        for i in range(len(word)):
            # delete the current character
            deleted.append(word[0:i] + word[i+1:])
            if not i == len(word) - 1:
                # swap the current and the next character
                swapped.append(word[0:i] + word[i+1] + word[i] + word[i+2:])
            current_char = word[i]
            # replace the current character with one of its possible neighbors
            # if current_char in self.kb_neighbor:
            #     neighbors = self.kb_neighbor[current_char]
            # else:
            #     neighbors = self.kb_neighbor.keys()
            neighbors = self.kb_neighbor.keys()
            for neighbor in neighbors:
                temp = word
                replaced.append(temp[0:i]+neighbor+temp[i+1:])
            # insert an alphabet between the current and the next character
            for alphabet in self.kb_neighbor.keys():
                inserted.append(word[0:i] + alphabet + word[i:])
        return deleted + replaced + swapped + inserted

    def get_probability(self, counter_words, to_find):
        return (counter_words[to_find] + 0.)/sum(counter_words.values())

    def word_frequency(self, word_list):
        return Counter(word_list)

    def __create_word_len_dict(self):
        len_dict = {}
        for word in self.word_corpus:
            n = len(word)
            if n not in len_dict:
                len_dict[n] = []
            len_dict[n].append(word)
        return len_dict

    def __get_words_of_len(self, n):
        correct_words_list = []
        if n-1 in self.len_dict:
            correct_words_list.extend(self.len_dict[n-1])
        if n in self.len_dict:
            correct_words_list.extend(self.len_dict[n])
        if n+1 in self.len_dict:
            correct_words_list.extend(self.len_dict[n+1])
        return list(set(correct_words_list))

    def get_most_probable_word(self, error_word, n_to_return=1):
        if error_word in self.word_freq:
            return (error_word, 1)
        words_to_consider = self.__get_words_of_len(len(error_word))
        word_prob = []
        for word in words_to_consider:
            word_count = self.word_freq[word]
            p_ci = word_count/self.total_len
            edited_words = self.edit_distance_1(word)
            if error_word not in edited_words:
                if error_word not in edited_words:
                    continue
            edited_counts = self.word_frequency(edited_words)
            total_e = sum(edited_counts.values())+0.0
            n_e = edited_counts[error_word]
            p_e_ci = n_e/total_e
            p_ci_e = p_e_ci * p_ci
            word_prob.append((word, p_ci_e))
        if 0 == len(word_prob):
            return None
        else:
            word_prob.sort(key=self.__getvalue, reverse=True)
            return word_prob[0:n_to_return]

    def __init__(self, folder_to_look='./'):
        self.word_corpus = hlp.recovervariable(folder_to_look + 'all_words.list')
        self.total_len = len(self.word_corpus) + 0.0
        self.word_freq = self.word_frequency(self.word_corpus)
        self.kb_neighbor = self.__keyboard_neighborhood()
        self.len_dict = self.__create_word_len_dict()