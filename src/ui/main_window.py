import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QStackedWidget, QLabel)
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("股票助手 (Stock Assistant)")
        self.resize(1200, 800)
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main Layout
        main_layout = QHBoxLayout(central_widget)
        
        # Sidebar
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        sidebar_layout.setSpacing(10)
        
        self.btn_realtime = QPushButton("实时数据")
        self.btn_history = QPushButton("历史数据")
        self.btn_llm = QPushButton("LLM 分析")
        self.btn_strategy = QPushButton("交易策略")
        self.btn_monitor = QPushButton("策略监控")
        
        # Add buttons to sidebar
        buttons = [self.btn_realtime, self.btn_history, self.btn_llm, self.btn_strategy, self.btn_monitor]
        for btn in buttons:
            btn.setFixedSize(150, 40)
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            sidebar_layout.addWidget(btn)
            
        main_layout.addLayout(sidebar_layout)
        
        # Content Area
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack)
        
        # Initialize Pages
        self.init_pages()
        
        # Connect signals
        self.btn_realtime.clicked.connect(lambda: self.content_stack.setCurrentIndex(0))
        self.btn_history.clicked.connect(lambda: self.content_stack.setCurrentIndex(1))
        self.btn_llm.clicked.connect(lambda: self.content_stack.setCurrentIndex(2))
        self.btn_strategy.clicked.connect(lambda: self.content_stack.setCurrentIndex(3))
        self.btn_monitor.clicked.connect(lambda: self.content_stack.setCurrentIndex(4))
        
        # Default selection
        self.btn_realtime.click()
        
        # Stylesheet for simple look
        self.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding-left: 20px;
                border: none;
                background-color: #f0f0f0;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:checked {
                background-color: #0078d7;
                color: white;
            }
            QWidget {
                background-color: white;
            }
        """)

    def init_pages(self):
        # Placeholder pages
        pages = ["实时数据界面", "历史数据界面", "LLM 分析界面", "交易策略界面", "策略监控界面"]
        for page_name in pages:
            page = QWidget()
            layout = QVBoxLayout(page)
            label = QLabel(page_name)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("font-size: 24px; color: #555;")
            layout.addWidget(label)
            self.content_stack.addWidget(page)
