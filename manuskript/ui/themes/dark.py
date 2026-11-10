from PyQt5.QtGui import QColor, QPalette

__all__ = ("colors", "palette")

colors = {
    QPalette.Window: QColor(53, 53, 53),
    QPalette.WindowText: QColor("white"),
    QPalette.Base: QColor(25, 25, 25),
    QPalette.AlternateBase: QColor(53, 53, 53),
    QPalette.ToolTipBase: QColor("white"),
    QPalette.ToolTipText: QColor("white"),
    QPalette.Text: QColor("white"),
    QPalette.Button: QColor(53, 53, 53),
    QPalette.ButtonText: QColor("white"),
    QPalette.BrightText: QColor("red"),
    QPalette.Link: QColor(42, 130, 218),
    QPalette.Highlight: QColor(42, 130, 218),
    QPalette.HighlightedText: QColor("black"),
}

palette = QPalette()
for key, val in colors.items():
    palette.setColor(key, val)