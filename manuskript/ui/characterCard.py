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

class ClickableLabel(QLabel):
    """A label that emits a signal when left-clicked."""

    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

        super().mousePressEvent(event)

class CharacterCard(QWidget):
    """Displays a character's name, portrait, and pin control."""

    pinToggled = pyqtSignal(object)
    characterClicked = pyqtSignal(object)

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

        # Character portrait
        self.portraitLabel = ClickableLabel()
        self.portraitLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
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
            alignment=Qt.AlignLeft
        )

        # Clicking the portrait opens the character's profile
        self.portraitLabel.clicked.connect(
            lambda: self.characterClicked.emit(self.character)
        )
