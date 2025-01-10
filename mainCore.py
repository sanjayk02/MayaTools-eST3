# -*- coding: utf-8 -*-
"""
This module provides a PySide2-based UI for controlling attributes in Autodesk Maya.

Classes:
    MyWindow(QMainWindow): Main UI window class that loads and displays the UI from a .ui file.
    CollapsibleTabManager: Utility class for managing collapsible tabs.

Functions:
    get_maya_window(): Retrieves Maya's main window as a PySide2 QWidget.
    load_ui(ui_file, parent=None): Loads a .ui file and returns the corresponding widget.
    show_window(): Displays the main UI window, ensuring only one instance is open at a time.

Constants:
    SCRIPT_LOC (str): Directory path of the current script.
    collapseMainUI (str): Path to the main UI .ui file.
"""

import os
from shiboken2 import wrapInstance
from PySide2.QtWidgets import (
    QWidget,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
)
from PySide2 import QtUiTools
from PySide2.QtCore import Qt, QFile

import collapsedWidget
import collapsible

# Reload for live development
reload(collapsible)
reload(collapsedWidget)

# Paths and Styles
SCRIPT_LOC = os.path.dirname(__file__)
collapseHeadUI = os.path.join(SCRIPT_LOC, 'ui', 'Head.ui')


def get_maya_window():
    """
    Get Maya's main window as a PySide2 object.

    Returns:
        QWidget: Maya's main window.

    Raises:
        RuntimeError: If Maya's main window cannot be obtained.
    """
    import maya.OpenMayaUI as omui  # type: ignore
    main_window_ptr = omui.MQtUtil.mainWindow()
    if not main_window_ptr:
        raise RuntimeError("Failed to obtain Maya's main window.")
    return wrapInstance(long(main_window_ptr), QWidget)  # Use long for Python 2.7


def load_ui(ui_file, parent=None):
    """
    Load a .ui file and return the corresponding widget.

    Args:
        ui_file (str): Path to the .ui file.
        parent (QWidget): Parent widget for the loaded UI.

    Returns:
        QWidget: The loaded UI widget.

    Raises:
        IOError: If the UI file does not exist.
        RuntimeError: If the UI file fails to load.
    """
    if not os.path.exists(ui_file):
        raise IOError("UI file not found: {}".format(ui_file))

    loader = QtUiTools.QUiLoader()
    file = QFile(ui_file)
    file.open(QFile.ReadOnly)
    try:
        ui_widget = loader.load(file, parent)
        if not ui_widget:
            raise RuntimeError("Failed to load UI file: {}".format(ui_file))
        return ui_widget
    finally:
        file.close()


class CollapsibleTabManager:
    """Manager for creating and managing collapsible tabs."""

    def __init__(self, parent_layout):
        self.parent_layout = parent_layout
        self.tabs = []

    def add_tab(self, title, content_widget):
        """
        Add a collapsible tab to the layout.

        Args:
            title (str): Title of the tab.
            content_widget (QWidget): Widget to display within the tab.
        """
        tab = collapsible.CollapsibleTab(title)
        tab.content_layout.addWidget(content_widget)
        self.parent_layout.addWidget(tab)
        tab.collapse()
        self.tabs.append(tab)


class MyWindow(QMainWindow):
    """Main UI Window."""

    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)

        self.main_ui = os.path.join(SCRIPT_LOC, "ui", "Main.ui")
        if not os.path.exists(self.main_ui):
            raise IOError("UI file not found: {}".format(self.main_ui))

        # Load UI
        try:
            self.ui = load_ui(self.main_ui, parent=self)
            self.setCentralWidget(self.ui)
        except Exception as e:
            QMessageBox.critical(self, "Error", "Failed to load UI: {}".format(e))
            raise

        self.setWindowTitle("Maya Attribute Controller")
        self.resize(350, 700)

        self.headUI = None
        self.add_widget()

    def add_widget(self):
        """Add collapsible tabs to the main layout."""
        self.headUI = collapsedWidget.UiWidgetLoader(ui_file_path=collapseHeadUI)._load_ui()

        # Initialize collapsible tab manager
        main_layout = QVBoxLayout()
        tab_manager = CollapsibleTabManager(main_layout)

        # Add tabs
        tab_manager.add_tab("Head-Tab", self.headUI)

        # Set the main layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)


# ============================================================================================================
_window_instance = None


def show_window():
    """
    Show the window.

    Ensures only one instance of the window is open at a time.
    """
    global _window_instance
    if _window_instance is not None:
        try:
            _window_instance.close()
            _window_instance.deleteLater()
        except AttributeError:
            pass

    # Initialize the new window instance
    try:
        _window_instance = MyWindow(parent=get_maya_window())
        _window_instance.show()
    except Exception as e:
        QMessageBox.critical(None, "Error", "Failed to show window: {}".format(e))
