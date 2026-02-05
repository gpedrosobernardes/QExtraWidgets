import typing

from PySide6.QtCore import QRegularExpressionMatch, QRegularExpression
from emoji_data_python import EmojiChar, find_by_shortname

from qextrawidgets.core.regexes.emoji_regex import QEmojiRegex


class QEmojiFinder:
    """Utility class for finding emojis and aliases in text using QRegularExpression."""
    @classmethod
    def findEmojis(cls, text: str) -> typing.Generator[QRegularExpressionMatch, None, None]:
        """Finds all Unicode emojis in the given text.

        Args:
            text (str): The text to scan.

        Yields:
            Generator[QRegularExpressionMatch]: Matches for each emoji found.
        """
        regex = QEmojiRegex()
        iterator = regex.globalMatch(text)
        while iterator.hasNext():
            yield iterator.next()

    @classmethod
    def findEmojiAliases(cls, text: str) -> typing.Generator[typing.Tuple[EmojiChar, QRegularExpressionMatch], None, None]:
        """Finds all text aliases (e.g., :smile:) in the given text.

        Args:
            text (str): The text to scan.

        Yields:
            Generator[Tuple[EmojiChar, QRegularExpressionMatch]]: Tuples of EmojiChar data and their matches.
        """
        regex = QRegularExpression(R"(:\w+:)")
        iterator = regex.globalMatch(text)
        while iterator.hasNext():
            match = iterator.next()
            first_captured = match.captured(0)
            alias = first_captured[1:-1]
            emoji = find_by_shortname(alias)
            if len(emoji) == 1:
                yield emoji[0], match
