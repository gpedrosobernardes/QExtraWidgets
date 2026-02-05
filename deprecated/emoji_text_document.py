import typing

from PySide6.QtCore import QSignalBlocker, QSize, QRegularExpressionMatch, QUrl
from PySide6.QtGui import (QTextDocument, QTextCursor, QTextImageFormat,
                           QTextCharFormat, QFontMetrics, QTextFragment, QTextBlock,
                           QFont)
from emoji_data_python import char_to_unified, unified_to_char

from qextrawidgets.core.utils.twemoji_image_provider import QTwemojiImageProvider
from qextrawidgets.core.utils.emoji_finder import QEmojiFinder

T = typing.TypeVar('T')


class QEmojiTextDocument(QTextDocument):
    """A QTextDocument extension that automatically renders Unicode emojis as Twemoji images."""

    def __init__(self, parent: typing.Optional[QTextDocument] = None, twemoji: bool = True,
                 alias_replacement: bool = True, emoji_margin: int = 1, dpr: float = 1.0) -> None:
        """Initializes the twemoji text document.

        Args:
            parent (QTextDocument, optional): Parent document. Defaults to None.
            twemoji (bool, optional): Whether to enable automatic twemojization. Defaults to True.
            alias_replacement (bool, optional): Whether to replace aliases like :smile: with emojis. Defaults to True.
            emoji_margin (int, optional): Margin around emoji images. Defaults to 1.
            dpr (float, optional): Device pixel ratio. Defaults to 1.0.
        """
        super().__init__(parent)

        self._twemoji = False
        self._twemoji_contents_changed_signal = None
        self._alias_replacement = False
        self._alias_replacement_contents_changed_signal = None
        self._line_limit = 0
        self._limit_line_signal = None
        self._emoji_margin = emoji_margin
        self._emoji_size = -1  # -1 means auto (based on font size)
        self._dpr = dpr

        # Variable to track where the edit occurred (Optimization B)
        self._last_change_pos = 0

        self.setTwemoji(twemoji)
        self.setAliasReplacement(alias_replacement)

        # Connects the 'Change' signal (before Changed) to capture the position
        self.contentsChange.connect(self._on_contents_change)

    # --- Configurations ---

    def devicePixelRatio(self) -> float:
        """Returns the current device pixel ratio.

        Returns:
            float: The device pixel ratio.
        """
        return self._dpr

    def setDevicePixelRatio(self, dpr: float) -> None:
        """Sets the device pixel ratio.

        Args:
            dpr (float): New device pixel ratio.
        """
        self._dpr = dpr

    def lineLimit(self) -> int:
        """Returns the maximum number of lines allowed in the document.

        Returns:
            int: The line limit (0 for unlimited).
        """
        return self._line_limit

    def setLineLimit(self, line_limit: int) -> None:
        """Sets the maximum number of lines allowed in the document.

        Args:
            line_limit (int): Maximum line count.
        """
        if self._line_limit == line_limit:
            return

        self._line_limit = line_limit

        if line_limit > 0:
            self._limit_line_signal = self.contentsChange.connect(self._limit_line)
        elif self._limit_line_signal:
            self.contentsChanged.disconnect(self._limit_line_signal)
            self._limit_line_signal = None

    def twemoji(self) -> bool:
        """Returns whether automatic twemojization is enabled.

        Returns:
            bool: True if enabled, False otherwise.
        """
        return self._twemoji

    def setTwemoji(self, value: bool) -> None:
        """Enables or disables automatic twemojization.

        Args:
            value (bool): True to enable, False to disable.
        """
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
        """Returns whether alias replacement is enabled.

        Returns:
            bool: True if enabled, False otherwise.
        """
        return self._alias_replacement

    def setAliasReplacement(self, value: bool) -> None:
        """Enables or disables automatic alias replacement (e.g., :smile: -> 😄).

        Args:
            value (bool): True to enable, False to disable.
        """
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
        """Returns the margin around emoji images.

        Returns:
            int: The margin in pixels.
        """
        return self._emoji_margin

    def setEmojiMargin(self, margin: int) -> None:
        """Sets the margin around emoji images.

        Args:
            margin (int): Margin in pixels.
        """
        if self._emoji_margin == margin:
            return
        self._emoji_margin = margin
        if self._twemoji:
            with QSignalBlocker(self):
                self.updateEmojiImages()

    def emojiSize(self) -> int:
        """Returns the explicit emoji size.

        Returns:
            int: Emoji size in pixels, or -1 for automatic calculation.
        """
        return self._emoji_size

    def setEmojiSize(self, size: int) -> None:
        """Sets an explicit size for emoji images.

        Args:
            size (int): Size in pixels. Use -1 for automatic calculation based on font size.
        """
        if self._emoji_size == size:
            return
        self._emoji_size = size
        if self._twemoji:
            with QSignalBlocker(self):
                self.updateEmojiImages()

    # --- Main Logic (Optimization B applied) ---

    def _on_contents_change(self, position: int, *args: typing.Any) -> None:
        """Captures the change position before it is processed.

        Args:
            position (int): Position where the change started.
            *args (Any): Other arguments from the signal.
        """
        self._last_change_pos = position

    def _ensure_resource_loaded(self, emoji: str, size: int, margin: int) -> None:
        """Ensures the emoji pixmap is loaded into the document resources.

        Args:
            emoji (str): Emoji character.
            size (int): Image size.
            margin (int): Image margin.
        """
        if not emoji:
            return

        size_obj = QSize(size, size)

        url = QTwemojiImageProvider.getUrl(char_to_unified(emoji), margin, size_obj, self._dpr, "png")

        if self.resource(QTextDocument.ResourceType.ImageResource, url):
            return

        pixmap = QTwemojiImageProvider.getPixmap(emoji, margin, size_obj, self._dpr)

        if not pixmap.isNull():
            self.addResource(QTextDocument.ResourceType.ImageResource, url, pixmap)

    def _calculate_emoji_size(self, cursor: QTextCursor) -> int:
        """Calculates the emoji size based on configuration or font metrics.

        Args:
            cursor (QTextCursor): The cursor to get font information from.

        Returns:
            int: Calculated size in pixels.
        """
        if self._emoji_size != -1:
            return self._emoji_size

        font_height = self._font_height(cursor)
        return int(font_height * 0.9)

    def _twemojize(self) -> None:
        """Processes the current block to convert Unicode emojis to images."""
        # 1. Identifies the block where the edit occurred
        block = self.findBlock(self._last_change_pos)
        if not block.isValid():
            return

        text = block.text()
        block_pos = block.position()

        for match in self.__reverse_generator(QEmojiFinder.findEmojis(text)):
            image_fmt = self._emoji_to_text_image(match.captured(0))
            self._replace_match(match, image_fmt, block_pos)

    def _twemojize_full(self) -> None:
        """Processes the entire document to convert Unicode emojis to images."""
        for match in self.__reverse_generator(QEmojiFinder.findEmojis(super().toPlainText())):
            image_fmt = self._emoji_to_text_image(match.captured(0))
            self._replace_match(match, image_fmt)

    def updateEmojiImages(self) -> None:
        """Updates the margin and size of existing emoji images in the document."""
        for block in self.__reverse_generator(self._blocks()):
            for fragment in self.__reverse_generator(self.emoji_fragments(block)):
                emoji = self._text_image_to_emoji(fragment.charFormat().toImageFormat())
                new_img_fmt = self._emoji_to_text_image(emoji)
                self._replace_match(fragment, new_img_fmt)

    def _replace_alias(self) -> None:
        """Replaces text aliases like :smile: with actual emojis or images."""
        for emoji, match in self.__reverse_generator(QEmojiFinder.findEmojiAliases(super().toPlainText())):
            if self._twemoji:
                image_fmt = self._emoji_to_text_image(emoji.char)
                self._replace_match(match, image_fmt)
            else:
                self._replace_match(match, emoji.char)

    def _replace_match(self, match: typing.Union[QRegularExpressionMatch, QTextFragment],
                       content: typing.Union[str, QTextImageFormat], offset: int = 0) -> None:
        """Replaces a matched range with the given content.

        Args:
            match (Union[QRegularExpressionMatch, QTextFragment]): The match to replace.
            content (Union[str, QTextImageFormat]): The replacement content.
            offset (int, optional): Position offset. Defaults to 0.
        """
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

    def _limit_line(self, *args: typing.Any) -> None:
        """Trims the document to stay within the line limit.

        Args:
            *args (Any): Signal arguments.
        """
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
        """Returns the document text with emojis converted back to characters.

        Returns:
            str: Plain text representation.
        """
        return self._to_plain_text()

    def _to_plain_text(self, first_block: typing.Optional[QTextBlock] = None,
                       last_block: typing.Optional[QTextBlock] = None,
                       selection_cursor: typing.Optional[QTextCursor] = None) -> str:
        """Internal helper to convert document blocks to plain text.

        Args:
            first_block (QTextBlock, optional): Start block. Defaults to None.
            last_block (QTextBlock, optional): End block. Defaults to None.
            selection_cursor (QTextCursor, optional): Cursor for selection limits. Defaults to None.

        Returns:
            str: The plain text.
        """
        result = ""
        for block in self._blocks(first_block, last_block):
            for frag in self._fragments(block):
                if selection_cursor and not self._is_fragment_selected(selection_cursor, frag):
                    continue

                if self._is_emoji_frag(frag):
                    image_format = frag.charFormat().toImageFormat()
                    emoji = self._text_image_to_emoji(image_format)
                    if emoji:
                        result += emoji
                else:
                    result += frag.text()
            if block != self.lastBlock():
                result += '\n'
        return result

    # --- Regex and Color Helpers ---

    def emoji_fragments(self, block: QTextBlock) -> typing.Generator[QTextFragment, None, None]:
        """Yields all emoji fragments in a given block.

        Args:
            block (QTextBlock): The block to scan.

        Yields:
            Generator[QTextFragment]: Emoji fragments.
        """
        for frag in self._fragments(block):
            if self._is_emoji_frag(frag):
                yield frag

    def _blocks(self, first_block: typing.Optional[QTextBlock] = None,
                last_block: typing.Optional[QTextBlock] = None) -> typing.Generator[QTextBlock, None, None]:
        """Yields blocks within the specified range.

        Args:
            first_block (QTextBlock, optional): Start block. Defaults to None.
            last_block (QTextBlock, optional): End block. Defaults to None.

        Yields:
            Generator[QTextBlock]: Blocks.
        """
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
        """Yields fragments within a block.

        Args:
            block (QTextBlock): The block to scan.

        Yields:
            Generator[QTextFragment]: Fragments.
        """
        it = block.begin()
        while not it.atEnd():
            frag = it.fragment()
            if frag.isValid():
                yield frag
            it += 1

    @staticmethod
    def _is_emoji_frag(frag: QTextFragment) -> bool:
        """Checks if a fragment represents a Twemoji image.

        Args:
            frag (QTextFragment): The fragment to check.

        Returns:
            bool: True if it's a Twemoji fragment, False otherwise.
        """
        if frag.charFormat().isImageFormat():
            img_fmt = frag.charFormat().toImageFormat()
            if img_fmt.name().startswith("twemoji:"):
                return True
        return False

    def _detwemojize(self) -> None:
        """Converts all Twemoji images back to their Unicode character equivalents."""
        for block in self.__reverse_generator(self._blocks()):
            for fragment in self.__reverse_generator(self.emoji_fragments(block)):
                emoji = self._text_image_to_emoji(fragment.charFormat().toImageFormat())
                self._replace_match(fragment, emoji)

    @staticmethod
    def __reverse_generator(generator: typing.Generator[T, None, None]) -> typing.List[T]:
        """Returns a reversed list from a generator.

        Args:
            generator (Generator): The generator to reverse.

        Returns:
            List[T]: Reversed items.
        """
        result = []
        for item in generator:
            result.insert(0, item)
        return result

    @staticmethod
    def _font_height(cursor: QTextCursor) -> int:
        """Returns the font height at the cursor position.

        Args:
            cursor (QTextCursor): The cursor.

        Returns:
            int: Font height.
        """
        font = cursor.charFormat().font()
        fm = QFontMetrics(font)
        return fm.height()

    def _emoji_to_text_image(self, emoji: str) -> QTextImageFormat:
        """Converts an emoji character to a QTextImageFormat.

        Args:
            emoji (str): Emoji character.

        Returns:
            QTextImageFormat: The formatted image.
        """
        cursor = QTextCursor(self)
        emoji_size = self._calculate_emoji_size(cursor)
        size = QSize(emoji_size, emoji_size)
        self._ensure_resource_loaded(emoji, emoji_size, self._emoji_margin)
        image = QTextImageFormat()
        if emoji:
            url = QTwemojiImageProvider.getUrl(char_to_unified(emoji), self._emoji_margin, size, self._dpr, "png")
            image.setName(url.toString())
            image.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignMiddle)
            total_size = emoji_size + (self._emoji_margin * 2)
            image.setHeight(total_size)
            image.setWidth(total_size)
            image.setQuality(100)
        return image

    @staticmethod
    def _text_image_to_emoji(image: QTextImageFormat) -> str:
        """Extracts the Unicode emoji character from a QTextImageFormat.

        Args:
            image (QTextImageFormat): The image format.

        Returns:
            str: Unicode character.
        """
        url = QUrl(image.name())
        return unified_to_char(url.path())

    @staticmethod
    def _is_fragment_selected(cursor: QTextCursor, fragment: QTextFragment) -> bool:
        """Checks if a fragment is within the cursor selection.

        Args:
            cursor (QTextCursor): The selection cursor.
            fragment (QTextFragment): The fragment to check.

        Returns:
            bool: True if selected, False otherwise.
        """
        if not cursor.hasSelection():
            return False
        sel_start = cursor.selectionStart()
        sel_end = cursor.selectionEnd()
        frag_start = fragment.position()
        frag_end = frag_start + fragment.length()
        return sel_end > frag_start and sel_start < frag_end

    def setDefaultFont(self, font: QFont) -> None:
        """Overrides setDefaultFont to trigger emoji resizing when the font changes.

        Args:
            font (QFont): New default font.
        """
        super().setDefaultFont(font)
        if self._twemoji and self._emoji_size == -1:
            # We reuse updateEmojiImages logic which recalculates size based on font
            with QSignalBlocker(self):
                self.updateEmojiImages()

    def selectionToPlainText(self, cursor: QTextCursor) -> typing.Optional[str]:
        """Returns the plain text of the selection, preserving emojis.

        Args:
            cursor (QTextCursor): The selection cursor.

        Returns:
            str, optional: Plain text of the selection.
        """
        first_block = self.findBlock(cursor.selectionStart())
        last_block = self.findBlock(cursor.selectionEnd())
        return self._to_plain_text(first_block, last_block, cursor)

    def setPlainText(self, text: str) -> None:
        """Overrides setPlainText to apply emoji processing to the new text.

        Args:
            text (str): New plain text.
        """
        super().setPlainText(text)
        if self._twemoji:
            self._twemojize_full()
        else:
            self._detwemojize()
        if self._alias_replacement:
            self._replace_alias()
