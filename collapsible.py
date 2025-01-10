from PySide2.QtWidgets import QVBoxLayout, QHBoxLayout, QFrame, QPushButton, QLabel, QWidget
from PySide2.QtGui import QIcon
from PySide2.QtCore import Qt


class CollapsibleTab(QFrame):
    def __init__(self, title, icon_path=None, parent=None):
        super().__init__(parent)

        # Style the QFrame
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)

        # Main Layout for the collapsible tab
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Header Layout (for icon and toggle button)
        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(0, 0, 0, 0)

        # Icon (optional)
        if icon_path:
            self.icon_label = QLabel(self)
            self.icon_label.setPixmap(QIcon(icon_path).pixmap(16, 16))  # Adjust icon size
            self.icon_label.setAlignment(Qt.AlignLeft)
            self.header_layout.addWidget(self.icon_label)

        # Toggle Button
        self.toggle_button = QPushButton(title, self)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(True)
        self.toggle_button.setStyleSheet("text-align: left; padding-left: 5px;")  # Align text to the left
        self.toggle_button.clicked.connect(self.toggle_content)
        self.toggle_button.setFixedHeight(30)  # Fix the height of the button to 40 pixels

        # Set button dimensions
        # Make the button stretch
        self.header_layout.addWidget(self.toggle_button, stretch=1)

        # Spacer (optional, to balance the layout if needed)
        self.header_layout.addStretch()

        # Content Area
        self.content_area = QWidget(self)
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_area.setMaximumHeight(700)  # Optional: limit content area height

        # Add header layout and content area to the main layout
        self.main_layout.addLayout(self.header_layout)
        self.main_layout.addWidget(self.content_area)

    def toggle_content(self):
        """Toggle the visibility of the content area."""
        is_expanded = self.toggle_button.isChecked()
        self.content_area.setVisible(is_expanded)
        self.updateGeometry()  # Adjust size hints when collapsing/expanding

    def expand(self):
        """Expand the collapsible tab."""
        if not self.toggle_button.isChecked():
            self.toggle_button.setChecked(True)
            self.toggle_content()

    def collapse(self):
        """Collapse the collapsible tab."""
        if self.toggle_button.isChecked():
            self.toggle_button.setChecked(False)
            self.toggle_content()
