import re

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from fuzzywuzzy import fuzz

from gob.settings import BASE_DIR

STRICTNESS_FILTER = 75


class IsCurseMessage(BoundFilter):
    """Filter for curse words."""

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

    CWF = open(BASE_DIR / 'static/banned_words.txt', 'r', encoding='utf-8')
    CurseWords = ''.join(CWF.readlines()).split('\n')[:-1]

    def replace_letters(self, word: str = None) -> str:
        """
        Taking into account the replacement of letters, symbols
        and their combinations when checking words.
        Args:
            word: checking word
        Returns:
        """
        word = word.lower()
        for key, value in self.alphabet.items():
            word = re.sub(value, key, word)
        return word

    async def check(self, message: types.Message) -> bool:
        """
        Curse word filter.

        Accounts for repetitions of letters, different substitutions
        of letters, symbols and their combinations.
        The dictionary of bad words is taken from banned_words.txt
        Args:
            message: filtered message

        Returns:
            True if Curse word are done,
            False if word is normal
        """
        punctuation = r'!|"|#|$|%|&|, |-|;|>|@|_|~| '
        for word in re.split(punctuation, message.text)[:-1]:
            print(word)
            word = ''.join(
                [
                    word[i]
                    for i in range(len(word) - 1)
                    if word[i + 1] != word[i]
                ]
                + [word[-1]]
            ).lower()
            word = self.replace_letters(word)
            for word_bad in self.CurseWords:
                strictness = fuzz.token_sort_ratio(word_bad, word)
                if strictness >= STRICTNESS_FILTER:
                    print(
                        f'{word_bad} | {strictness}% Матерное слово {word_bad}'
                    )
                    await message.reply('А ну не матюкаться!')
                    await message.delete()
                    return False
        return True
