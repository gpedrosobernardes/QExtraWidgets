import pytest
from PySide6.QtGui import QValidator

from qextrawidgets.core.utils.emoji_finder import QEmojiFinder
from qextrawidgets.gui.validators import QEmojiValidator


# emoji test file: https://unicode.org/Public/emoji/latest/emoji-test.txt

def get_emoji_db():
    results = []
    with open('tests/emoji-test.txt', encoding="utf-8") as file:
        for row in file:
            if "; fully-qualified" in row:
                hex_seq = row.split(";")[0].strip()
                emoji = "".join(chr(int(h, 16)) for h in hex_seq.split())
                results.append(emoji)
    return results


emoji_db = get_emoji_db()


@pytest.mark.parametrize("emoji", emoji_db)
def test_emoji_finder_finds_all_emojis(emoji):
    matches = QEmojiFinder.findEmojis(emoji)
    assert len(matches) > 0
    for match in matches:
        assert emoji == match.captured(0)

def test_emoji_finder_mixed_content():
    text = "Hello 👋 World 🔥"
    matches = list(QEmojiFinder.findEmojis(text))
    assert len(matches) == 2
    assert matches[0].captured(0) == "👋"
    assert matches[1].captured(0) == "🔥"

def test_emoji_finder_no_emojis():
    text = "Hello World 123"
    matches = QEmojiFinder.findEmojis(text)
    assert len(matches) == 0

@pytest.mark.parametrize("emoji", emoji_db)
def test_emoji_validator_accepts_valid_emojis(emoji):
    validator = QEmojiValidator()
    state, _, _ = validator.validate(emoji, 0)
    assert state == QValidator.State.Acceptable


def test_emoji_validator_rejects_non_emojis():
    validator = QEmojiValidator()

    # Test simple text
    state, _, _ = validator.validate("Hello", 0)
    assert state == QValidator.State.Invalid

    # Test mixed text and emoji
    state, _, _ = validator.validate("Hello 👋", 0)
    assert state == QValidator.State.Invalid

    # Test numbers (without keycap sequence)
    state, _, _ = validator.validate("123", 0)
    assert state == QValidator.State.Invalid

def test_emoji_validator_accepts_multiple_emojis():
    validator = QEmojiValidator()
    # Test multiple emojis
    state, _, _ = validator.validate("👋🔥😂", 0)
    assert state == QValidator.State.Acceptable


def test_emoji_validator_accepts_empty():
    validator = QEmojiValidator()
    state, _, _ = validator.validate("", 0)
    assert state == QValidator.State.Acceptable
