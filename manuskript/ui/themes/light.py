from PyQt5.QtGui import QColor, QPalette

__all__ = ("colors", "palette")

colors = {
    QPalette.Window: QColor("#f2f2f2"),
    QPalette.WindowText: QColor("black"),
    QPalette.Base: QColor("white"),
    QPalette.AlternateBase: QColor(202, 202, 202),
    QPalette.ToolTipBase: QColor("black"),
    QPalette.ToolTipText: QColor("black"),
    QPalette.Text: QColor("black"),
    QPalette.Button: QColor(202, 202, 202),
    QPalette.ButtonText: QColor("black"),
    QPalette.BrightText: QColor("red"),
    QPalette.Link: QColor(42, 130, 218),
    QPalette.Highlight: QColor(42, 130, 218),
    QPalette.HighlightedText: QColor("white"),
}

palette = QPalette()
for key, val in colors.items():
    palette.setColor(key, val)