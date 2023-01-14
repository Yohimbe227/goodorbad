import re

from aiogram import types
from fuzzywuzzy import fuzz
from aiogram.dispatcher.filters import BoundFilter


class IsCurseMessage(BoundFilter):
    alphabet = {
        'а': '[@|а|а́|a]',
        'б': '[б|6|b]',
        'в': '[в|b|v]',
        'г': '[г|r|g]',
        'д': '[д|d]',
        'е': '[е|e|ё]',
        'ж': '[ж|z|*]',
        'з': '[з|3|z]',
        'и': '[и|u|i]',
        'й': '[й|u|i]',
        'к': '[к|k]',
        'л': '[л|l]',
        'м': '[м|m]',
        'н': '[н|h|n]',
        'о': '[о|o|0]',
        'п': '[п|n|p]',
        'р': '[р|r|p]',
        'с': '[с|c|s|5|$]',
        'т': '[т|m|t]',
        'у': '[у́|у|y|u]',
        'ф': '[ф|f]',
        'х': '[х|x|h]',
        'ц': '[ц|c|u]',
        'ч': '[ч|c|h]',
        'ш': '[ш|щ]',
        'ь': '[ь|b]',
        'ы': '[ы|i]',
        'ъ': '[ъ|ь]',
        'э': '[э|e]',
        'ю': '[ю|y|u]',
        'я': '[я|r]',
        ' ': '[.|,|!|?|&|)|(|\\|\/|*|-|_|"|\'|;|®]',
    }
    # Регулярки для замены похожих букв и символов на русские

    CWF = open('banned_words.txt', 'r', encoding='utf-8')
    CurseWords = ''.join(CWF.readlines()).split('\n')[:-1]

    def replace_letters(self, word: str = None) -> str:
        word = word.lower()
        for key, value in self.alphabet.items():
            word = re.sub(value, key, word)
        return word

    async def check(self, msg: str) -> bool:
        punctuation = r'!|"|#|$|%|&|,|-|;|>|@|_|~| '
        msg = re.split(punctuation, msg.text)

        for word in msg:
            # word = ''.join([word[i] for i in range(len(word) - 1) if
            #                 word[i + 1] != word[i]] + [word[
            #                                                -1]]).lower()  # Здесь убираю символы которые повторяються "Приииииивет" -> "Привет"
            word = self.replace_letters(word)
            for word_bad in self.CurseWords:
                b = fuzz.token_sort_ratio(
                    word_bad, word
                )  # Проверяю сходство слов из списка
                if b >= 75:
                    print(f'{word_bad} | {b}% Матерное слово {word_bad}')
                    # print(CurseWords)
                    return True
            #    print('тест', word, word_bad)
        return False
