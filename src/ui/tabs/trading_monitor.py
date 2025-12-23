from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
                             QTableWidget, QTableWidgetItem, QTextEdit, QPushButton, QLabel, 
                             QListWidget, QGroupBox, QHeaderView, QComboBox, QStyle)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class TradingMonitorTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Main Splitter (Left, Middle, Right)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # --- Left Area: Watchlist & Chart ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Watchlist
        watchlist_group = QGroupBox("自选股")
        watchlist_layout = QVBoxLayout(watchlist_group)
        self.watchlist_table = QTableWidget(0, 5)
        self.watchlist_table.setHorizontalHeaderLabels(["代码", "名称", "现价", "涨跌幅", "成交量"])
        self.watchlist_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.watchlist_table.verticalHeader().setVisible(False)
        self.watchlist_table.setAlternatingRowColors(True)
        # Fix: Select entire row, disable editing
        self.watchlist_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.watchlist_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.watchlist_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        watchlist_layout.addWidget(self.watchlist_table)
        
        # Mini Chart
        chart_group = QGroupBox("K线预览")
        chart_layout = QVBoxLayout(chart_group)
        self.chart_label = QLabel("K线图表区域\n(待集成)")
        self.chart_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chart_label.setStyleSheet("""
            QLabel {
                background-color: #2b2b2b; 
                color: #888; 
                border: 1px dashed #555; 
                border-radius: 4px;
                font-size: 14px;
            }
        """)
        chart_layout.addWidget(self.chart_label)
        
        # Splitter for Left Area
        left_splitter = QSplitter(Qt.Orientation.Vertical)
        left_splitter.addWidget(watchlist_group)
        left_splitter.addWidget(chart_group)
        left_layout.addWidget(left_splitter)
        
        # --- Middle Area: LLM Chat ---
        middle_widget = QWidget()
        middle_layout = QVBoxLayout(middle_widget)
        middle_layout.setContentsMargins(0, 0, 0, 0)
        
        chat_group = QGroupBox("LLM 智能助手")
        chat_layout = QVBoxLayout(chat_group)
        
        # LLM Control Bar (Model & Prompt Selector)
        control_layout = QHBoxLayout()
        self.model_selector = QComboBox()
        # self.model_selector.addItems(["OpenAI (Default)", "Local (Ollama)"]) 
        self.prompt_selector = QComboBox()
        self.prompt_selector.addItems(["通用助手", "短线交易员"]) 
        
        control_layout.addWidget(QLabel("模型:"))
        control_layout.addWidget(self.model_selector, 1)
        control_layout.addWidget(QLabel("提示词:"))
        control_layout.addWidget(self.prompt_selector, 1)
        
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setPlaceholderText("对话历史将显示在这里...")
        
        self.chat_input = QTextEdit()
        self.chat_input.setMaximumHeight(100)
        self.chat_input.setPlaceholderText("输入您的问题，例如：分析平安银行的近期走势...")
        
        send_btn = QPushButton("发送指令")
        send_btn.setFixedHeight(35)
        send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        # Add icon if available, or just text
        
        chat_layout.addLayout(control_layout)
        chat_layout.addWidget(self.chat_history)
        chat_layout.addWidget(self.chat_input)
        chat_layout.addWidget(send_btn)
        
        middle_layout.addWidget(chat_group)

        # --- Right Area: Monitor & Logs ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        monitor_group = QGroupBox("策略监控")
        monitor_layout = QVBoxLayout(monitor_group)
        
        self.monitor_list = QListWidget()
        self.monitor_list.addItem("系统初始化完成...")
        self.monitor_list.addItem("等待策略信号...")
        
        monitor_layout.addWidget(self.monitor_list)
        right_layout.addWidget(monitor_group)

        # Add widgets to main splitter
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(middle_widget)
        main_splitter.addWidget(right_widget)
        
        # Set initial sizes (approx 25%, 45%, 30%)
        main_splitter.setSizes([250, 450, 300])

        layout.addWidget(main_splitter)
        
        # Load sample data
        self.add_sample_data()

    def update_models(self, model_names):
        """Update model selector options"""
        current_text = self.model_selector.currentText()
        self.model_selector.clear()
        self.model_selector.addItems(model_names)
        
        # Restore selection if possible
        index = self.model_selector.findText(current_text)
        if index >= 0:
            self.model_selector.setCurrentIndex(index)

    def add_sample_data(self):
        data = [
            ("000001", "平安银行", "10.50", "+1.2%", "100万"),
            ("600519", "贵州茅台", "1750.00", "-0.5%", "5000"),
            ("000858", "五粮液", "150.00", "+0.8%", "20万"),
            ("300750", "宁德时代", "200.00", "+2.5%", "30万"),
            ("601127", "赛力斯", "88.88", "+5.2%", "50万"),
        ]
        self.watchlist_table.setRowCount(len(data))
        for row, item_data in enumerate(data):
            for col, value in enumerate(item_data):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if col == 3: # Change
                    if value.startswith("+"):
                        item.setForeground(QColor("#d32f2f")) # Red
                    elif value.startswith("-"):
                        item.setForeground(QColor("#388e3c")) # Green
                self.watchlist_table.setItem(row, col, item)

