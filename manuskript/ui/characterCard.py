from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QSizePolicy,
)


class CharacterCard(QWidget):
    """Displays a character's name and portrait."""

    def __init__(self, character, parent=None):
        super().__init__(parent)

        self.character = character

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 8, 5, 8)
        layout.setSpacing(5)

        # Character name
        self.nameLabel = QLabel(character.name())
        self.nameLabel.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.nameLabel)

        # Character portrait
        self.portraitLabel = QLabel()
        self.portraitLabel.setAlignment(Qt.AlignCenter)
        self.portraitLabel.setMinimumSize(120, 150)
        self.portraitLabel.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        if character.portraitData:
            pixmap = QPixmap()

            if pixmap.loadFromData(character.portraitData):
                self.portraitLabel.setPixmap(
                    pixmap.scaled(
                        180,
                        220,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                )
        else:
            self.portraitLabel.setText("No portrait")

        layout.addWidget(self.portraitLabel)
