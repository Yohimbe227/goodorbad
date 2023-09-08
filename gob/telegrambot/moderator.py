import re

from aiogram import types

# from aiogram.dispatcher.filters import BoundFilter
from aiogram.filters import BaseFilter
from fuzzywuzzy import fuzz

from gob.settings import BASE_DIR
from telegrambot.costants import ALPHABET
from telegrambot.decorators import logger

STRICTNESS_FILTER = 75


class IsCurseMessage(BaseFilter):
    """Filter for curse words."""

    def __init__(
        self,
    ):
        with open(
            BASE_DIR / "data/banned_words.txt",
            "r",
            encoding="utf-8",
        ) as reader:
            self.curse_words = "".join(reader.readlines()).split("\n")[:-1]

    @staticmethod
    def replace_letters(word: str = None) -> str:
        """Taking into account the replacement of letters, symbols
        and their combinations when checking words.

        Args:
            word: checking word

        Returns:
            Word with substituted letters of the English alphabet in Russian
            words

        """
        word = word.lower()
        for key, value in ALPHABET.items():
            word = re.sub(re.escape(value), key, word)
        return word

    async def __call__(self, message: types.Message) -> bool:
        """
        Curse word filter.

        Accounts for repetitions of letters, different substitutions
        of letters, symbols and their combinations.
        The dictionary of bad words is taken from banned_words.txt

        Args:
            message: filtered message

        Returns:
            True if Curse word are done,
            False if word is normal.

        """
        if not message.text:
            return True
        punctuation = r'!|"|#|$|%|&|, |-|;|>|@|_|~| '
        for word in re.split(punctuation, message.text)[:-1]:
            word = "".join(
                [
                    word[index]
                    for index in range(len(word) - 1)
                    if word[index + 1] != word[index]
                ]
                + [word[-1]]
                if word
                else "",
            ).lower()
            word = self.replace_letters(word)
            for word_bad in self.curse_words:
                strictness = fuzz.token_sort_ratio(word_bad, word)
                if strictness >= STRICTNESS_FILTER:
                    logger.info(
                        f"{word_bad} | {strictness}% Матерное слово " f"{word_bad}",
                    )
                    await message.reply("А ну не матюкаться!")
                    await message.delete()
                    return False
        return True
