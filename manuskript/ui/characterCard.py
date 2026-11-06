from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
)


class CharacterCard(QWidget):
    """Displays a character's name, portrait, and pin control."""

    pinToggled = pyqtSignal(object)

    def __init__(self, character, parent=None):
        super().__init__(parent)

        self.character = character

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 8, 5, 8)
        layout.setSpacing(5)

        # Character name above portrait
        self.nameLabel = QLabel(character.name())
        self.nameLabel.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.nameLabel)

        # Portrait and pin button on the same row

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
                self.portraitLabel.setText("Invalid portrait")
        else:
            self.portraitLabel.setText("No portrait")

        layout.addWidget(self.portraitLabel)

        # Pin button
        self.pinButton = QPushButton("Pin")
        self.pinButton.setCheckable(True)
        self.pinButton.setFixedWidth(55)
        self.pinButton.setToolTip(
            "Keep this character at the top of the sidebar"
        )
        self.pinButton.clicked.connect(
            lambda: self.pinToggled.emit(self.character)
        )

        # Pin button underneath the portrait
        layout.addWidget(
            self.pinButton,
            alignment=Qt.AlignHCenter
        )
