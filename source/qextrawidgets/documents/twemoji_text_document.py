import typing
from urllib.parse import urlparse, urlencode, urlunparse

from PySide6.QtCore import QSignalBlocker, QSize, Qt, QRegularExpressionMatch
from PySide6.QtGui import (QTextDocument, QTextCursor, QTextImageFormat,
                           QTextCharFormat, QFontMetrics, QTextFragment, QGuiApplication, QPixmap, QPainter, QTextBlock,
                           QFont)
from emojis.db import Emoji, get_emoji_by_alias

from qextrawidgets.emoji_utils import EmojiFinder, EmojiImageProvider

T = typing.TypeVar('T')


class QTwemojiTextDocument(QTextDocument):

    def __init__(self, parent=None, twemoji=True, alias_replacement=True, emoji_margin=1):
        super().__init__(parent)

        self._twemoji = False
        self._twemoji_contents_changed_signal = None
        self._alias_replacement = False
        self._alias_replacement_contents_changed_signal = None
        self._line_limit = 0
        self._limit_line_signal = None
        self._emoji_margin = emoji_margin
        self._emoji_size = -1  # -1 means auto (based on font size)

        # Variable to track where the edit occurred (Optimization B)
        self._last_change_pos = 0

        self.setTwemoji(twemoji)
        self.setAliasReplacement(alias_replacement)

        # Connects the 'Change' signal (before Changed) to capture the position
        self.contentsChange.connect(self._on_contents_change)

    # --- Configurations ---

    def lineLimit(self) -> int:
        return self._line_limit

    def setLineLimit(self, line_limit: int):
        if self._line_limit == line_limit:
            return

        self._line_limit = line_limit

        if line_limit > 0:
            self._limit_line_signal = self.contentsChange.connect(self._limit_line)
        elif self._limit_line_signal:
            self.contentsChanged.disconnect(self._limit_line_signal)
            self._limit_line_signal = None

    def twemoji(self) -> bool:
        return self._twemoji

    def setTwemoji(self, value: bool):
        if self._twemoji == value:
            return

        self._twemoji = value

        if value:
            self._twemoji_contents_changed_signal = self.contentsChanged.connect(self._twemojize)
            # On initial activation, process the entire document
            self._twemojize_full()
        elif self._twemoji_contents_changed_signal:
            self.contentsChanged.disconnect(self._twemoji_contents_changed_signal)
            self._twemoji_contents_changed_signal = None
            self._detwemojize()

    def aliasReplacement(self) -> bool:
        return self._alias_replacement

    def setAliasReplacement(self, value: bool):
        if self._alias_replacement == value:
            return

        self._alias_replacement = value

        if value:
            self._alias_replacement_contents_changed_signal = self.contentsChanged.connect(self._replace_alias)
            self._replace_alias()
        elif self._alias_replacement_contents_changed_signal:
            self.contentsChanged.disconnect(self._replace_alias)
            self._alias_replacement_contents_changed_signal = None

    def emojiMargin(self) -> int:
        return self._emoji_margin

    def setEmojiMargin(self, margin: int):
        if self._emoji_margin == margin:
            return
        self._emoji_margin = margin
        if self._twemoji:
            with QSignalBlocker(self):
                self.updateEmojiImages()

    def emojiSize(self) -> int:
        return self._emoji_size

    def setEmojiSize(self, size: int):
        if self._emoji_size == size:
            return
        self._emoji_size = size
        if self._twemoji:
            with QSignalBlocker(self):
                self.updateEmojiImages()

    # --- Main Logic (Optimization B applied) ---

    def _on_contents_change(self, position, *_):
        """Captures the change position before it is processed."""
        self._last_change_pos = position

    def _ensure_resource_loaded(self, emoji: Emoji, size: int, margin: int):
        """Lazy Loading via EmojiImageProvider."""
        if not emoji:
            return

        url = self._encode_url(emoji.aliases[0], margin, size)

        if self.resource(QTextDocument.ResourceType.ImageResource, url):
            return

        dpr = QGuiApplication.primaryScreen().devicePixelRatio()

        pixmap = EmojiImageProvider.get_pixmap(
            emoji_data=emoji,
            size=QSize(size, size),
            dpr=dpr
        )

        if margin > 0:
            total_size = size + (margin * 2)
            final_pixmap = QPixmap(int(total_size * dpr), int(total_size * dpr))
            final_pixmap.setDevicePixelRatio(dpr)
            final_pixmap.fill(Qt.GlobalColor.transparent)

            painter = QPainter(final_pixmap)
            painter.drawPixmap(margin, margin, pixmap)
            painter.end()
            pixmap = final_pixmap

        if not pixmap.isNull():
            self.addResource(QTextDocument.ResourceType.ImageResource, url, pixmap)

    @staticmethod
    def _encode_url(alias, margin=1, size=72, dpr=1.0) -> str:
        params = dict(margin=margin, size=size, dpr=dpr)
        query_string = urlencode(params)
        components = ('twemoji', alias, '', '', query_string, '')
        return str(urlunparse(components))

    def _calculate_emoji_size(self, cursor: QTextCursor) -> int:
        """Calculates the emoji size based on configuration or font."""
        if self._emoji_size != -1:
            return self._emoji_size

        font_height = self._font_height(cursor)
        return int(font_height * 0.9)

    def _twemojize(self):
        """
        OPTIMIZED version: Processes only the current block (paragraph).
        Called automatically on every text change.
        """
        # 1. Identifies the block where the edit occurred
        block = self.findBlock(self._last_change_pos)
        if not block.isValid():
            return

        text = block.text()
        block_pos = block.position()

        for emoji, match in self.__reverse_generator(EmojiFinder.find_all_emoji_objects(text, True)):
            image_fmt = self._emoji_to_text_image(emoji)
            self._replace_match(match, image_fmt, block_pos)

    def _twemojize_full(self):
        """Full version for use at initialization (total scan)."""
        for emoji, match in self.__reverse_generator(EmojiFinder.find_all_emoji_objects(super().toPlainText(), True)):
            image_fmt = self._emoji_to_text_image(emoji)
            self._replace_match(match, image_fmt)

    def updateEmojiImages(self):
        """Updates the margin and size of existing emoji images without converting to text."""
        for block in self.__reverse_generator(self._blocks()):
            for fragment in self.__reverse_generator(self.emoji_fragments(block)):
                emoji = self._text_image_to_emoji(fragment.charFormat().toImageFormat())
                new_img_fmt = self._emoji_to_text_image(emoji)
                self._replace_match(fragment, new_img_fmt)

    def _replace_alias(self):
        """
        Alias replacement - :smile: -> 😄
        Could also be optimized for _last_change_pos, but alias is less frequent.
        Kept global logic for safety, or the same logic as _twemojize could be applied.
        """
        for emoji, match in self.__reverse_generator(EmojiFinder.find_all_emoji_aliases(super().toPlainText())):
            if self._twemoji:
                image_fmt = self._emoji_to_text_image(emoji)
                self._replace_match(match, image_fmt)
            else:
                self._replace_match(match, emoji.emoji)

    def _replace_match(self, match: typing.Union[QRegularExpressionMatch, QTextFragment],
                       content: typing.Union[str, QTextImageFormat], offset: int = 0):
        cursor = QTextCursor(self)

        start = match.position() if isinstance(match, QTextFragment) else match.capturedStart(0)
        end = match.position() + match.length() if isinstance(match, QTextFragment) else match.capturedEnd(0)

        cursor.setPosition(start + offset)
        cursor.setPosition(end + offset, QTextCursor.MoveMode.KeepAnchor)

        with QSignalBlocker(self):
            if isinstance(content, QTextImageFormat):
                cursor.removeSelectedText()
                cursor.insertImage(content)
            else:
                cursor.insertText(content)

    # --- Helpers and Utilities ---

    def _limit_line(self, *_):
        if self._line_limit <= 0:
            return

        if self.blockCount() > self._line_limit:
            cursor = QTextCursor(self)
            cursor.movePosition(QTextCursor.MoveOperation.End)
            with QSignalBlocker(self):
                while self.blockCount() > self._line_limit:
                    cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
                    cursor.removeSelectedText()
                    cursor.deletePreviousChar()

    def toPlainText(self) -> str:
        return self._to_plain_text()

    def _to_plain_text(self, first_block: typing.Optional[QTextBlock] = None,
                       last_block: typing.Optional[QTextBlock] = None,
                       selection_cursor: typing.Optional[QTextCursor] = None) -> str:
        result = ""
        for block in self._blocks(first_block, last_block):
            for frag in self._fragments(block):
                if selection_cursor and not self._is_fragment_selected(selection_cursor, frag):
                    continue

                if self._is_emoji_frag(frag):
                    image_format = frag.charFormat().toImageFormat()
                    emoji = self._text_image_to_emoji(image_format)
                    if emoji:
                        result += emoji.emoji
                else:
                    result += frag.text()
            if block != self.lastBlock():
                result += '\n'
        return result

    # --- Regex and Color Helpers ---

    def emoji_fragments(self, block: QTextBlock) -> typing.Generator[QTextFragment, None, None]:
        for frag in self._fragments(block):
            if self._is_emoji_frag(frag):
                yield frag

    def _blocks(self, first_block: typing.Optional[QTextBlock] = None,
                last_block: typing.Optional[QTextBlock] = None) -> typing.Generator[QTextBlock, None, None]:
        if first_block is None:
            block = self.firstBlock()
        else:
            block = first_block
        while block.isValid():
            yield block
            if block == last_block:
                break
            block = block.next()

    @staticmethod
    def _fragments(block: QTextBlock) -> typing.Generator[QTextFragment, None, None]:
        it = block.begin()
        while not it.atEnd():
            frag = it.fragment()
            if frag.isValid():
                yield frag
            it += 1

    @staticmethod
    def _is_emoji_frag(frag):
        if frag.charFormat().isImageFormat():
            img_fmt = frag.charFormat().toImageFormat()
            if img_fmt.name().startswith("twemoji://"):
                return True
        return False

    def _detwemojize(self):
        for block in self.__reverse_generator(self._blocks()):
            for fragment in self.__reverse_generator(self.emoji_fragments(block)):
                emoji = self._text_image_to_emoji(fragment.charFormat().toImageFormat())
                self._replace_match(fragment, emoji.emoji)

    @staticmethod
    def __reverse_generator(generator: typing.Generator[T, None, None]) -> typing.List[T]:
        result = []
        for item in generator:
            result.insert(0, item)
        return result

    @staticmethod
    def _font_height(cursor: QTextCursor):
        font = cursor.charFormat().font()
        fm = QFontMetrics(font)
        return fm.height()

    def _emoji_to_text_image(self, emoji: Emoji) -> QTextImageFormat:
        cursor = QTextCursor(self)
        emoji_size = self._calculate_emoji_size(cursor)
        self._ensure_resource_loaded(emoji, emoji_size, self._emoji_margin)
        image = QTextImageFormat()
        if emoji and emoji.aliases:
            name = self._encode_url(emoji.aliases[0], self._emoji_margin, emoji_size)
            image.setName(name)
            image.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignMiddle)
            total_size = emoji_size + (self._emoji_margin * 2)
            image.setHeight(total_size)
            image.setWidth(total_size)
            image.setQuality(100)
        return image

    @staticmethod
    def _text_image_to_emoji(image: QTextImageFormat) -> typing.Optional[Emoji]:
        uri = urlparse(image.name())
        return get_emoji_by_alias(uri.netloc)

    @staticmethod
    def _is_fragment_selected(cursor: QTextCursor, fragment: QTextFragment) -> bool:
        if not cursor.hasSelection():
            return False
        sel_start = cursor.selectionStart()
        sel_end = cursor.selectionEnd()
        frag_start = fragment.position()
        frag_end = frag_start + fragment.length()
        return sel_end > frag_start and sel_start < frag_end

    def setDefaultFont(self, font: QFont) -> None:
        """Override setDefaultFont to trigger emoji resize when font changes."""
        super().setDefaultFont(font)
        if self._twemoji and self._emoji_size == -1:
            # We reuse updateEmojiImages logic which recalculates size based on font
            with QSignalBlocker(self):
                self.updateEmojiImages()

    def selectionToPlainText(self, cursor: QTextCursor) -> typing.Optional[str]:
        first_block = self.findBlock(cursor.selectionStart())
        last_block = self.findBlock(cursor.selectionEnd())
        return self._to_plain_text(first_block, last_block, cursor)
