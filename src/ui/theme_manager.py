from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor

class ThemeManager:
    LIGHT_THEME = """
    QMainWindow, QWidget {
        background-color: #f5f5f5;
        color: #333333;
        font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
        font-size: 12px;
    }
    
    /* QTabWidget */
    QTabWidget::pane {
        border: 1px solid #dcdcdc;
        background: white;
        border-radius: 4px;
    }
    QTabBar::tab {
        background: #e0e0e0;
        border: 1px solid #c4c4c3;
        padding: 8px 20px;
        margin-right: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        color: #555;
    }
    QTabBar::tab:selected {
        background: white;
        border-bottom-color: white; 
        font-weight: bold;
        color: #0078d7;
    }
    QTabBar::tab:hover {
        background: #ececec;
    }

    /* QGroupBox */
    QGroupBox {
        border: 1px solid #dcdcdc;
        border-radius: 4px;
        margin-top: 24px;
        background-color: white;
        font-weight: bold;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 5px;
        left: 10px;
        color: #333;
    }

    /* QSplitter */
    QSplitter::handle {
        background-color: #dcdcdc;
    }
    QSplitter::handle:horizontal {
        width: 2px;
    }
    QSplitter::handle:vertical {
        height: 2px;
    }

    /* QTableWidget & QTreeWidget */
    QTableWidget, QTreeWidget, QListWidget {
        background-color: white;
        alternate-background-color: #f9f9f9;
        border: 1px solid #dcdcdc;
        gridline-color: #f0f0f0;
        selection-background-color: #0078d7;
        selection-color: white;
    }
    QHeaderView::section {
        background-color: #f0f0f0;
        padding: 4px;
        border: 1px solid #dcdcdc;
        font-weight: bold;
        color: #333;
    }

    /* QPushButton */
    QPushButton {
        background-color: #0078d7;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 6px 12px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #0063b1;
    }
    QPushButton:pressed {
        background-color: #004c87;
    }
    QPushButton:disabled {
        background-color: #cccccc;
        color: #666666;
    }

    /* QLineEdit, QTextEdit, QComboBox */
    QLineEdit, QTextEdit, QComboBox {
        border: 1px solid #ccc;
        border-radius: 4px;
        padding: 4px;
        background-color: white;
        selection-background-color: #0078d7;
    }
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
        border: 1px solid #0078d7;
    }
    
    /* ScrollBar */
    QScrollBar:vertical {
        border: none;
        background: #f0f0f0;
        width: 10px;
        margin: 0px 0px 0px 0px;
    }
    QScrollBar::handle:vertical {
        background: #cdcdcd;
        min-height: 20px;
        border-radius: 5px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        border: none;
        background: none;
    }
    """

    DARK_THEME = """
    QMainWindow, QWidget {
        background-color: #1e1e1e;
        color: #cccccc;
        font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
        font-size: 12px;
    }

    /* QTabWidget */
    QTabWidget::pane {
        border: 1px solid #333;
        background: #252526;
        border-radius: 4px;
    }
    QTabBar::tab {
        background: #2d2d2d;
        border: 1px solid #333;
        padding: 8px 20px;
        margin-right: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        color: #999;
    }
    QTabBar::tab:selected {
        background: #252526;
        border-bottom-color: #252526;
        font-weight: bold;
        color: #0078d7;
    }
    QTabBar::tab:hover {
        background: #3e3e42;
    }

    /* QGroupBox */
    QGroupBox {
        border: 1px solid #3e3e42;
        border-radius: 4px;
        margin-top: 24px;
        background-color: #252526;
        font-weight: bold;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 5px;
        left: 10px;
        color: #eee;
    }

    /* QSplitter */
    QSplitter::handle {
        background-color: #3e3e42;
    }

    /* QTableWidget & QTreeWidget */
    QTableWidget, QTreeWidget, QListWidget {
        background-color: #252526;
        alternate-background-color: #2d2d2d;
        border: 1px solid #3e3e42;
        gridline-color: #3e3e42;
        selection-background-color: #0078d7;
        selection-color: white;
        color: #cccccc;
    }
    QHeaderView::section {
        background-color: #2d2d2d;
        padding: 4px;
        border: 1px solid #3e3e42;
        font-weight: bold;
        color: #cccccc;
    }

    /* QPushButton */
    QPushButton {
        background-color: #0078d7;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 6px 12px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #0063b1;
    }
    QPushButton:pressed {
        background-color: #004c87;
    }

    /* QLineEdit, QTextEdit, QComboBox */
    QLineEdit, QTextEdit, QComboBox {
        border: 1px solid #3e3e42;
        border-radius: 4px;
        padding: 4px;
        background-color: #3c3c3c;
        color: #cccccc;
        selection-background-color: #0078d7;
    }
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
        border: 1px solid #0078d7;
    }
    
    /* ScrollBar */
    QScrollBar:vertical {
        border: none;
        background: #252526;
        width: 10px;
    }
    QScrollBar::handle:vertical {
        background: #424242;
        min-height: 20px;
        border-radius: 5px;
    }
    """

    @staticmethod
    def apply_theme(app: QApplication, theme_name: str):
        if theme_name == "Dark":
            app.setStyleSheet(ThemeManager.DARK_THEME)
        else:
            app.setStyleSheet(ThemeManager.LIGHT_THEME)
