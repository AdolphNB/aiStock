from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
                             QTreeWidget, QTreeWidgetItem, QTableWidget, QTableWidgetItem,
                             QTextEdit, QPushButton, QGroupBox, QHeaderView,
                             QComboBox, QLabel, QAbstractItemView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class SmartSelectionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- Left Area: Market Overview ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Market Tree (Sectors/Indices)
        market_group = QGroupBox("市场全景")
        market_layout = QVBoxLayout(market_group)
        
        self.market_tree = QTreeWidget()
        self.market_tree.setHeaderLabels(["板块/指数", "涨跌幅"])
        self.market_tree.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.market_tree.setAlternatingRowColors(True)
        
        # Dummy Data
        root_industry = QTreeWidgetItem(self.market_tree, ["行业板块", "+1.2%"])
        root_industry.setExpanded(True)
        self.add_tree_item(root_industry, "半导体", "+3.5%", "red")
        self.add_tree_item(root_industry, "医药", "-0.5%", "green")
        self.add_tree_item(root_industry, "新能源", "+1.8%", "red")
        
        root_concept = QTreeWidgetItem(self.market_tree, ["概念板块", "+0.8%"])
        root_concept.setExpanded(True)
        self.add_tree_item(root_concept, "AI算力", "+4.2%", "red")
        self.add_tree_item(root_concept, "低空经济", "+2.1%", "red")
        
        market_layout.addWidget(self.market_tree)
        
        # Component Table
        components_group = QGroupBox("板块成分股")
        components_layout = QVBoxLayout(components_group)
        self.component_table = QTableWidget(0, 4)
        self.component_table.setHorizontalHeaderLabels(["代码", "名称", "现价", "涨跌幅"])
        self.component_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.component_table.verticalHeader().setVisible(False)
        self.component_table.setAlternatingRowColors(True)
        self.component_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        components_layout.addWidget(self.component_table)
        
        # Add sample components
        self.add_sample_components()
        
        left_splitter = QSplitter(Qt.Orientation.Vertical)
        left_splitter.addWidget(market_group)
        left_splitter.addWidget(components_group)
        left_layout.addWidget(left_splitter)

        # --- Right Area: LLM Selection Assistant ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        chat_group = QGroupBox("选股助手")
        chat_layout = QVBoxLayout(chat_group)
        
        # LLM Control Bar
        control_layout = QHBoxLayout()
        self.model_selector = QComboBox()
        # self.model_selector.addItems(["OpenAI (Default)", "Local (Ollama)"]) 
        self.prompt_selector = QComboBox()
        self.prompt_selector.addItems(["通用助手", "选股专家"]) 
        
        control_layout.addWidget(QLabel("模型:"))
        control_layout.addWidget(self.model_selector, 1)
        control_layout.addWidget(QLabel("提示词:"))
        control_layout.addWidget(self.prompt_selector, 1)
        
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setPlaceholderText("LLM 选股建议将显示在这里...")
        
        self.chat_input = QTextEdit()
        self.chat_input.setMaximumHeight(100)
        self.chat_input.setPlaceholderText("请输入选股条件，例如：选出市盈率小于20且今日涨幅大于3%的科技股...")
        
        send_btn = QPushButton("开始筛选")
        send_btn.setFixedHeight(35)
        send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        chat_layout.addLayout(control_layout)
        chat_layout.addWidget(self.chat_history)
        chat_layout.addWidget(self.chat_input)
        chat_layout.addWidget(send_btn)
        
        right_layout.addWidget(chat_group)

        # Add to main splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([600, 400])

        layout.addWidget(splitter)

    def update_models(self, model_names):
        """Update model selector options"""
        current_text = self.model_selector.currentText()
        self.model_selector.clear()
        self.model_selector.addItems(model_names)
        
        # Restore selection if possible
        index = self.model_selector.findText(current_text)
        if index >= 0:
            self.model_selector.setCurrentIndex(index)

    def add_tree_item(self, parent, name, change, color_name):
        item = QTreeWidgetItem(parent, [name, change])
        if color_name == "red":
            item.setForeground(1, QColor("#d32f2f"))
        elif color_name == "green":
            item.setForeground(1, QColor("#388e3c"))
    
    def add_sample_components(self):
        data = [
            ("688981", "中芯国际", "50.50", "+3.5%"),
            ("603501", "韦尔股份", "95.20", "+1.2%"),
            ("002371", "北方华创", "280.00", "+2.8%"),
            ("300012", "华测检测", "12.50", "-0.3%"),
        ]
        self.component_table.setRowCount(len(data))
        for row, item_data in enumerate(data):
            for col, value in enumerate(item_data):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if col == 3:
                    if value.startswith("+"):
                        item.setForeground(QColor("#d32f2f"))
                    elif value.startswith("-"):
                        item.setForeground(QColor("#388e3c"))
                self.component_table.setItem(row, col, item)
