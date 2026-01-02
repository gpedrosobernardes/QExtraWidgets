from PySide6.QtGui import QPainter, Qt, QImage
from PySide6.QtWidgets import QApplication


def is_dark_mode() -> bool:
    style_hints = QApplication.styleHints()
    color_scheme = style_hints.colorScheme()
    return color_scheme.value == 2


def scale_inside(image: QImage, factor: float) -> QImage:
    # tamanho final (igual ao original)
    w, h = image.width(), image.height()

    # cria imagem com o mesmo tamanho, mas transparente
    out = QImage(w, h, QImage.Format.Format_ARGB32)

    out.fill(Qt.GlobalColor.transparent)

    # calcula tamanho reduzido
    new_w = int(w * factor)
    new_h = int(h * factor)

    # calcula posição para centralizar
    x = (w - new_w) // 2
    y = (h - new_h) // 2

    # desenha imagem menor dentro da maior
    p = QPainter(out)
    p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
    p.drawImage(x, y, image.scaled(new_w, new_h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
    p.end()

    return out