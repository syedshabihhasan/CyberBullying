from collections import Counter
import enchant

class canonical_form:
    '''
    based on
    @article{Brody:2011uf,
    author = {Brody, Samuel and Diakopoulos, Nicholas},
    title = {{Cooooooooooooooollllllllllllll!!!!!!!!!!!!!! Using Word Lengthening to Detect Sentiment in Microblogs.}},
    journal = {EMNLP},
    year = {2011},
    pages = {562--570}
    }

    and using enchant to weed out words that are already present
    '''

    def __is_word_in_dict(self, word):
        return self.chkr.check(word.lower()) or self.chkr.check(word.upper())

    def words_in_dict(self, data=None, just_present=False):
        data = self.word_list if data is None else data
        correct_words = []
        incorrect_words = []
        for word in data:
            if self.__is_word_in_dict(word):
                if just_present:
                    return True, word
                correct_words.append(word)
            else:
                if just_present:
                    continue
                incorrect_words.append(word)
        if just_present:
            return False, None
        else:
            return correct_words, incorrect_words

    def highest_frequency(self, expanded_list):
        data = Counter(expanded_list)
        return data.most_common(1)[0][0]

    def are_letters_repeated(self, word_list, n=3):
        for word in word_list:
            last_two_chars = ['', '']
            if len(word) < 3:
                continue
            for idx in range(len(word)):
                if 0 == idx or 1 == idx:
                    last_two_chars[idx] = word[idx]
                else:
                    current_char = word[idx]
                    if last_two_chars[0] == current_char and last_two_chars[1] == current_char:
                        return True
                    else:
                        last_two_chars[0] = last_two_chars[1]
                        last_two_chars[1] = current_char
        return False

    def get_condensed_word(self, word):
        root_word = []
        for idx in range(len(word)):
            if 0 == idx:
                root_word.append(word[idx])
            else:
                if not(root_word[-1] == word[idx]):
                    root_word.append(word[idx])
        return ''.join(root_word)

    def set_word_list(self, data):
        self.word_list = data

    def get_canonical_form(self):
        final_form = {}
        words_left = []
        for word in self.word_list:
            # step 1
            condensed_form = self.get_condensed_word(word)
            if condensed_form not in self.word_root:
                self.word_root[condensed_form] = []
            # step 2
            self.word_root[condensed_form].append(word)
        # step 3, step 4
        word_root_to_keep = {}
        for condensed_form, expanded_form_list in self.word_root.iteritems():
            if self.__is_word_in_dict(condensed_form):
                word_root_to_keep[condensed_form] = expanded_form_list
                final_form[condensed_form] = expanded_form_list
            else:
                expanded_form_list.sort(key=len)
                expanded_form_in_dict, which_word = self.words_in_dict(data=expanded_form_list, just_present=True)
                if expanded_form_in_dict:
                    word_root_to_keep[which_word] = expanded_form_list
                    final_form[which_word] = expanded_form_list
                else:
                    words_left += expanded_form_list
        return final_form, words_left



    def __init__(self, word_list):
        self.word_root = {}
        self.word_list = None
        self.set_word_list(word_list)
        self.chkr = enchant.Dict('en_US')