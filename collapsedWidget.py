import os
from PySide2 import QtCore, QtUiTools, QtWidgets


class UiWidgetLoader(object):
    def __init__(self, ui_file_path=None, parent=None, geometry=None):
        """
        Initializes the widget loader with an optional parent and geometry.

        :param ui_file_path: Path to the .ui file (str)
        :param parent: Parent widget (optional)
        :param geometry: Tuple (x, y, width, height) for setting widget geometry (optional)
        """
        if not ui_file_path:
            raise ValueError("UI file path must be provided.")
        self.ui_file_path = ui_file_path
        self.parent = parent
        self.geometry = geometry

    def _load_ui(self):
        """
        Loads the .ui file and returns the widget.

        :return: Loaded widget
        :raises IOError: If the UI file does not exist or fails to load.
        """
        print("Loading UI from: %s" % self.ui_file_path)

        if not os.path.exists(self.ui_file_path):
            raise IOError("UI file %s not found." % self.ui_file_path)

        loader = QtUiTools.QUiLoader()
        ui_loader = QtCore.QFile(self.ui_file_path)

        try:
            ui_loader.open(QtCore.QFile.ReadOnly)
            widget = loader.load(ui_loader, parent=self.parent)
            if not widget:
                raise IOError("Failed to load UI from %s." % self.ui_file_path)
            print("UI loaded successfully.")
        finally:
            ui_loader.close()

        if self.geometry:
            try:
                x, y, width, height = self.geometry
                widget.setGeometry(x, y, width, height)
                print("Set geometry to: %d, %d, %d, %d" % (x, y, width, height))
            except (ValueError, TypeError):
                print("Invalid geometry provided. Skipping geometry setting.")

        return widget
