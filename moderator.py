import re
from fuzzywuzzy import fuzz

dict = {
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
    ' ': '[.|,|!|?|&|)|(|\\|\/|*|-|_|"|\'|;|®]'
}
# Регулярки для замены похожих букв и символов на русские


CWF = open('banned_words.txt', 'r', encoding='utf-8')
CurseWords = ''.join(CWF.readlines()).split(', ')


def replace_letters(word=None):
    word = word.lower()
    for key, value in dict.items():
        word = re.sub(value, key, word)
    return word


def filter_word(msg):
    msg = msg.split()
    for w in msg:
        w = ''.join([w[i] for i in range(len(w) - 1) if w[i + 1] != w[i]] + [w[-1]]).lower()  # Здесь убираю символы которые повторяються "Приииииивет" -> "Привет"
        w = replace_letters(w)
        for word in CurseWords:
            b = fuzz.token_sort_ratio(word,
                                      w)  # Проверяю сходство слов из списка
            if b >= 85:
                print(f'{w} | {b}% Матерное слово {word}')
                return True
            else:
                pass
