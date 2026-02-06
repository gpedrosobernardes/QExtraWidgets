from PySide6.QtCore import QRegularExpression


class QEmojiRegex(QRegularExpression):
    def __init__(self):
        super().__init__(
            R"(?:\x{1F3F4}(?:\x{E0067}\x{E0062}\x{E0065}\x{E006E}\x{E0067}|\x{E0067}\x{E0062}\x{E0073}\x{E0063}\x{E0074}|\x{E0067}\x{E0062}\x{E0077}\x{E006C}\x{E0073})\x{E007F})|"
            R"(?:[\x{0030}-\x{0039}\x{0023}\x{002A}]\x{FE0F}?\x{20E3})|"
            R"(?:[\x{1F1E6}-\x{1F1FF}]{2})|"
            R"(?:\p{Extended_Pictographic}\x{FE0F}?(?:[\x{1F3FB}-\x{1F3FF}])?(?:\x{200D}\p{Extended_Pictographic}\x{FE0F}?(?:[\x{1F3FB}-\x{1F3FF}])?)*)",
            QRegularExpression.PatternOption.UseUnicodePropertiesOption
        )