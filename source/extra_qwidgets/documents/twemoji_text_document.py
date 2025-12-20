import typing

from PySide6.QtCore import QUrl, QSignalBlocker, QRegularExpression
from PySide6.QtGui import QTextDocument, QTextCursor, QTextImageFormat, QImage, QTextCharFormat, \
    QFontMetrics, QTextFragment
from emojis.db import Emoji, get_emoji_by_alias, get_emoji_by_code
from twemoji_api.api import get_all_emojis

from extra_qwidgets.utils import scale_inside


class QTwemojiTextDocument(QTextDocument):
    def __init__(self, parent = None, twemoji = True, alias_replacement = True):
        super().__init__(parent)
        self.setTwemoji(twemoji)
        self.setAliasReplacement(alias_replacement)
        self._load_emojis()

    def lineLimit(self):
        return self._line_limit

    def setLineLimit(self, line_limit: int):
        self._line_limit = line_limit

        if line_limit > 0:
            self.contentsChange.connect(self._limit_line)
        else:
            self.contentsChange.disconnect(self._limit_line)

    def _limit_line(self, position, chars_removed, chars_added):
        if self.blockCount() > self._line_limit:
            self.undo()

    def _load_emojis(self):
        for e in get_all_emojis("svg"):
            alias = e.emoji.aliases[0]
            url = QUrl(f"twemoji://{alias}")
            img = QImage(str(e.path))
            self.addResource(
                QTextDocument.ResourceType.ImageResource,
                url,
                scale_inside(img, 0.9)
            )

    def twemoji(self):
        return self._twemoji

    def setTwemoji(self, value):
        self._twemoji = value

        if value:
            self.contentsChanged.connect(self._twemojize)
            self._twemojize()
        else:
            self.contentsChanged.disconnect(self._twemojize)
            self._detwemojize()

    def aliasReplacement(self):
        return self._alias_replacement

    def setAliasReplacement(self, value):
        self._alias_replacement = value

        if value:
            self.contentsChanged.connect(self._replace_alias)
            self._replace_alias()
        else:
            self.contentsChanged.disconnect(self._replace_alias)

    def _localize_alias(self):
        text = self.toPlainText()
        re = QRegularExpression(R"(:\w+:)")
        global_match = re.globalMatch(text)
        matches = []
        while global_match.hasNext():
            match = global_match.next()
            words = match.captured(0)[1:-1]
            start = match.capturedStart(0)
            end = match.capturedEnd(0)
            emoji = get_emoji_by_alias(words)
            if emoji:
                matches.insert(0, (emoji, start, end))
        return matches

    def _replace_alias(self):
        cursor = QTextCursor(self)
        font_height = self._font_heigth(cursor)

        for emoji, start, end in self._localize_alias():
            cursor.setPosition(start, QTextCursor.MoveMode.MoveAnchor)
            cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)

            if self._twemoji:
                image = self.emoji_to_text_image(emoji, font_height)
                with QSignalBlocker(self):
                    cursor.removeSelectedText()
                    cursor.insertImage(image)
            else:
                with QSignalBlocker(self):
                    cursor.insertText(emoji.emoji)

    @staticmethod
    def _font_heigth(cursor):
        font = cursor.charFormat().font()
        font_metrics = QFontMetrics(font)
        return font_metrics.lineSpacing() + font_metrics.leading()

    def _twemojize(self):
        cursor = QTextCursor(self)

        font_height = self._font_heigth(cursor)

        for emoji, start, end in self._localize_emojis():
            cursor.setPosition(start, QTextCursor.MoveMode.MoveAnchor)
            cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
            emoji_without_color = self._remove_emoji_color(emoji)
            emoji_obj = get_emoji_by_code(emoji_without_color)
            image = self.emoji_to_text_image(emoji_obj, font_height)
            with QSignalBlocker(self):
                cursor.removeSelectedText()
                cursor.insertImage(image)

    def _localize_emojis(self):
        re_emoji = QRegularExpression(
            R"(?:\x{1F3F4}(?:\x{E0067}\x{E0062}\x{E0065}\x{E006E}\x{E0067}|\x{E0067}\x{E0062}\x{E0073}\x{E0063}\x{E0074}|\x{E0067}\x{E0062}\x{E0077}\x{E006C}\x{E0073})\x{E007F})|(?:[\x{0030}-\x{0039}\x{0023}\x{002A}]\x{FE0F}?\x{20E3})|(?:[\x{1F1E6}-\x{1F1FF}]{2})|(?:\p{Extended_Pictographic}\x{FE0F}?(?:[\x{1F3FB}-\x{1F3FF}])?(?:\x{200D}\p{Extended_Pictographic}\x{FE0F}?(?:[\x{1F3FB}-\x{1F3FF}])?)*)",
            QRegularExpression.PatternOption.UseUnicodePropertiesOption
        )

        iterator = re_emoji.globalMatch(self.toPlainText())
        matches = []
        while iterator.hasNext():
            match = iterator.next()
            matches.insert(0, (match.captured(0), match.capturedStart(0), match.capturedEnd(0)))
        return matches

    def _localize_emoji_images(self):
        block = self.begin()

        emojis_images = []
        while block.isValid():
            it = block.begin()
            while not it.atEnd():
                frag = it.fragment()
                if frag.isValid() and frag.charFormat().isImageFormat():
                    img_fmt = frag.charFormat().toImageFormat()
                    if img_fmt.name().startswith("twemoji://"):
                        start = frag.position()
                        emojis_images.insert(0, (img_fmt, start, start + frag.length()))
                it += 1
            block = block.next()
        return emojis_images

    def _detwemojize(self):
        cursor = QTextCursor(self)
        for img_fmt, start, end in self._localize_emoji_images():
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
            emoji = self.text_image_to_emoji(img_fmt)
            cursor.insertText(emoji.emoji)

    @staticmethod
    def _get_emoji_colors(emoji: str) -> typing.Set[str]:
        re_color = QRegularExpression(R"[\x{1F3FB}-\x{1F3FF}]")

        iterator = re_color.globalMatch(emoji)
        matches = []

        while iterator.hasNext():
            match = iterator.next()
            matches.append(match.captured(0))

        return set(matches)

    def _remove_emoji_color(self, emoji: str) -> str:
        for color in self._get_emoji_colors(emoji):
            emoji = emoji.replace(color, "")
        return emoji

    @staticmethod
    def emoji_to_text_image(emoji: Emoji, height: int) -> QTextImageFormat:
        image = QTextImageFormat()
        image.setName(f"twemoji://{emoji.aliases[0]}")
        image.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignMiddle)
        image.setHeight(height)
        return image

    @staticmethod
    def text_image_to_emoji(image: QTextImageFormat) -> Emoji:
        alias = image.name()[10:]
        return get_emoji_by_alias(alias)

    def toText(self, cursor: QTextCursor = None) -> str:
        result = ""

        block = self.firstBlock()

        while block.isValid():
            it = block.begin()
            while not it.atEnd():
                frag = it.fragment()

                is_selected = True
                if cursor:
                    is_selected = self._is_fragment_selected(cursor, frag)

                if frag.isValid() and is_selected:
                    char_format = frag.charFormat()

                    if char_format.isImageFormat():
                        image_format = char_format.toImageFormat()
                        image_name = image_format.name()

                        if image_name.startswith("twemoji://"):
                            emoji = self.text_image_to_emoji(image_format)
                            result += emoji.emoji
                    else:
                        result += frag.text()

                it.__iadd__(1)

            if block != self.lastBlock():
                result += '\n'

            block = block.next()

        return result

    @staticmethod
    def _is_fragment_selected(cursor: QTextCursor, fragment: QTextFragment) -> bool:
        if not cursor.hasSelection():
            return False

        sel_start = cursor.selectionStart()
        sel_end = cursor.selectionEnd()

        frag_start = fragment.position()
        frag_end = frag_start + fragment.length()

        return sel_end > frag_start and sel_start < frag_end