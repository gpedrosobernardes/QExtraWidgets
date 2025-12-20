import pytest
from PySide6.QtCore import QRegularExpression

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
def test_regular_expression_emojis(emoji):
    re_emoji = QRegularExpression(
        R"(?:\x{1F3F4}(?:\x{E0067}\x{E0062}\x{E0065}\x{E006E}\x{E0067}|\x{E0067}\x{E0062}\x{E0073}\x{E0063}\x{E0074}|\x{E0067}\x{E0062}\x{E0077}\x{E006C}\x{E0073})\x{E007F})|(?:[\x{0030}-\x{0039}\x{0023}\x{002A}]\x{FE0F}?\x{20E3})|(?:[\x{1F1E6}-\x{1F1FF}]{2})|(?:\p{Extended_Pictographic}\x{FE0F}?(?:[\x{1F3FB}-\x{1F3FF}])?(?:\x{200D}\p{Extended_Pictographic}\x{FE0F}?(?:[\x{1F3FB}-\x{1F3FF}])?)*)",
        QRegularExpression.PatternOption.UseUnicodePropertiesOption
    )

    iterator = re_emoji.globalMatch(emoji)
    assert iterator.hasNext()
    while iterator.hasNext():
        match = iterator.next()
        assert emoji == match.captured(0)