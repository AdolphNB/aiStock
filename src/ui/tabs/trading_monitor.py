from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
                             QTableWidget, QTableWidgetItem, QTextEdit, QPushButton, QLabel, 
                             QListWidget, QGroupBox, QHeaderView, QComboBox, QStyle, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
import markdown
try:
    from services.llm_service import LLMService
    from ui.utils.worker import LLMWorker
except ImportError:
    # Fallback for relative imports if run as package
    from ...services.llm_service import LLMService
    from ..utils.worker import LLMWorker

class TradingMonitorTab(QWidget):
    def __init__(self):
        super().__init__()
        self.current_stock_code = None
        self.current_stock_name = None
        self.llm_service = LLMService()
        self.init_ui()
        self.load_initial_config()

    def load_initial_config(self):
        """Load initial models and prompts"""
        if hasattr(self, 'llm_service') and self.llm_service:
            # Load models
            providers = self.llm_service.config_manager.get_providers()
            model_names = [config.get("model_name") for config in providers.values() if config.get("model_name")]
            self.update_models(model_names)
            
            # Load prompts
            prompts = self.llm_service.config_manager.get_prompts()
            prompt_names = list(prompts.keys())
            self.update_prompts(prompt_names)

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
        self.watchlist_table = QTableWidget(0, 4)
        self.watchlist_table.setHorizontalHeaderLabels(["代码", "名称", "现价", "涨跌幅"])
        self.watchlist_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.watchlist_table.verticalHeader().setVisible(False)
        self.watchlist_table.setAlternatingRowColors(True)
        # Fix: Select entire row, disable editing
        self.watchlist_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.watchlist_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.watchlist_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.watchlist_table.itemClicked.connect(self.on_stock_selected)
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
        left_splitter.addWidget(chart_group)
        left_splitter.addWidget(watchlist_group)
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
        self.prompt_selector = QComboBox()
        
        control_layout.addWidget(QLabel("模型:"))
        control_layout.addWidget(self.model_selector, 1)
        control_layout.addWidget(QLabel("提示词:"))
        control_layout.addWidget(self.prompt_selector, 1)
        
        # Current Stock Indicator
        control_layout.addStretch()
        self.current_stock_label = QLabel("未选择股票")
        self.current_stock_label.setStyleSheet("color: #888; font-style: italic;")
        control_layout.addWidget(self.current_stock_label)
        
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setPlaceholderText("对话历史将显示在这里...")
        
        self.chat_input = QTextEdit()
        self.chat_input.setMaximumHeight(100)
        self.chat_input.setPlaceholderText("输入您的问题，例如：分析平安银行的近期走势...")
        
        # Action Buttons Layout
        action_layout = QHBoxLayout()
        
        self.btn_send = QPushButton("发送指令")
        self.btn_send.setFixedHeight(35)
        self.btn_send.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.btn_accept = QPushButton("采纳")
        self.btn_accept.setFixedHeight(35)
        self.btn_accept.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_accept.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.btn_accept.setToolTip("采纳当前策略并加入监控列表")
        
        self.btn_reject = QPushButton("拒绝")
        self.btn_reject.setFixedHeight(35)
        self.btn_reject.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reject.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
        self.btn_reject.setToolTip("拒绝当前策略建议")

        self.btn_accept.clicked.connect(self.on_accept_strategy)
        self.btn_reject.clicked.connect(self.on_reject_strategy)
        self.btn_send.clicked.connect(self.on_send_message)

        action_layout.addWidget(self.btn_send, 3)
        action_layout.addWidget(self.btn_accept, 1)
        action_layout.addWidget(self.btn_reject, 1)
        
        chat_layout.addLayout(control_layout)
        chat_layout.addWidget(self.chat_history)
        chat_layout.addWidget(self.chat_input)
        chat_layout.addLayout(action_layout)
        
        middle_layout.addWidget(chat_group)

        # --- Right Area: Monitor & Logs ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Right Splitter (Top: Preview, Bottom: List)
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # 1. Top: Strategy Preview
        preview_group = QGroupBox("策略预览")
        preview_layout = QVBoxLayout(preview_group)
        
        self.strategy_details = QTextEdit()
        self.strategy_details.setReadOnly(True)
        self.strategy_details.setPlaceholderText("请在下方列表中选择一只股票以查看策略详情...")
        
        # Action Buttons
        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("启动")
        self.btn_stop = QPushButton("停止")
        self.btn_delete = QPushButton("删除")
        
        # Initial state: disabled
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.btn_delete.setEnabled(False)

        # Connect buttons
        self.btn_start.clicked.connect(self.on_start_strategy)
        self.btn_stop.clicked.connect(self.on_stop_strategy)
        self.btn_delete.clicked.connect(self.on_delete_strategy)
        
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_stop)
        btn_layout.addWidget(self.btn_delete)
        
        preview_layout.addWidget(self.strategy_details)
        preview_layout.addLayout(btn_layout)
        
        # 2. Bottom: Monitored Stocks List
        list_group = QGroupBox("监控列表")
        list_layout = QVBoxLayout(list_group)
        
        self.monitor_table = QTableWidget(0, 3)
        self.monitor_table.setHorizontalHeaderLabels(["代码", "名称", "状态"])
        self.monitor_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.monitor_table.verticalHeader().setVisible(False)
        self.monitor_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.monitor_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.monitor_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.monitor_table.itemClicked.connect(self.on_monitor_selected)
        
        list_layout.addWidget(self.monitor_table)
        
        right_splitter.addWidget(preview_group)
        right_splitter.addWidget(list_group)
        right_splitter.setSizes([300, 400])
        
        right_layout.addWidget(right_splitter)

        # Add widgets to main splitter
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(middle_widget)
        main_splitter.addWidget(right_widget)
        
        # Set initial sizes (approx 25%, 45%, 30%)
        main_splitter.setSizes([250, 450, 300])

        layout.addWidget(main_splitter)

    def update_models(self, model_names):
        """Update model selector options"""
        current_text = self.model_selector.currentText()
        self.model_selector.clear()
        self.model_selector.addItems(model_names)
        
        # Restore selection if possible
        index = self.model_selector.findText(current_text)
        if index >= 0:
            self.model_selector.setCurrentIndex(index)

    def update_prompts(self, prompt_names):
        """Update prompt selector options"""
        current_text = self.prompt_selector.currentText()
        self.prompt_selector.clear()
        self.prompt_selector.addItems(prompt_names)
        
        # Restore selection if possible
        index = self.prompt_selector.findText(current_text)
        if index >= 0:
            self.prompt_selector.setCurrentIndex(index)
        
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
            ("000001", "平安银行", "10.50", "+1.2%"),
            ("600519", "贵州茅台", "1750.00", "-0.5%"),
            ("000858", "五粮液", "150.00", "+0.8%"),
            ("300750", "宁德时代", "200.00", "+2.5%"),
            ("601127", "赛力斯", "88.88", "+5.2%"),
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

        # --- Add Monitor Sample Data ---
        monitor_data = [
            ("000001", "平安银行", "运行中"),
            ("600519", "贵州茅台", "已停止"),
            ("300750", "宁德时代", "运行中"),
        ]
        self.monitor_table.setRowCount(len(monitor_data))
        for row, item_data in enumerate(monitor_data):
            for col, value in enumerate(item_data):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if col == 2: # Status
                    if value == "运行中":
                        item.setForeground(QColor("#4CAF50")) # Green
                    else:
                        item.setForeground(QColor("#FF5252")) # Red
                self.monitor_table.setItem(row, col, item)
                
        # Mock strategy details
        self.mock_strategies = {
            "000001": "策略名称: 均线突破\n监控周期: 15分钟\n买入条件: MA5上穿MA20\n卖出条件: MA5下穿MA20\n止损: -2%\n止盈: +5%",
            "600519": "策略名称: 网格交易\n监控周期: 1小时\n网格大小: 1%\n单笔金额: 50000\n当前持仓: 200股",
            "300750": "策略名称: MACD背离\n监控周期: 30分钟\n底背离: 开启\n顶背离: 开启\n风险等级: 中",
        }

    def on_stock_selected(self, item):
        """Handle stock selection from watchlist"""
        row = item.row()
        code_item = self.watchlist_table.item(row, 0)
        name_item = self.watchlist_table.item(row, 1)
        
        if code_item and name_item:
            code = code_item.text()
            name = name_item.text()
            
            self.current_stock_code = code
            self.current_stock_name = name
            
            self.current_stock_label.setText(f"当前分析: {name} ({code})")
            # Update style to indicate active selection
            self.current_stock_label.setStyleSheet("""
                QLabel {
                    color: #4CAF50; 
                    font-weight: bold;
                    border: 1px solid #4CAF50;
                    border-radius: 4px;
                    padding: 2px 5px;
                }
            """)
            
            # Simulate LLM providing a strategy suggestion
            self.chat_history.append(f"<b>[系统]</b> 已选择 {name} ({code})。")
            # self.chat_history.append(f"<b>[LLM助手]</b> 针对 {name} 的建议策略：\n"
            #                          f"- 监控周期：30分钟\n"
            #                          f"- 建议买入：突破昨日高点\n"
            #                          f"- 建议卖出：跌破5日均线\n"
            #                          f"您可以点击“采纳”将此策略加入监控，或点击“拒绝”忽略。")

    def on_send_message(self):
        user_input = self.chat_input.toPlainText().strip()
        if not user_input:
            return
            
        context = f"[当前分析股票: {self.current_stock_name} ({self.current_stock_code})]\n" if self.current_stock_code else ""
        full_input = context + user_input
        
        # Display user message
        self.chat_history.append(f"<b>[用户]</b> {user_input}")
        self.chat_input.clear()
        
        # Get selected options
        model_name = self.model_selector.currentText()
        prompt_name = self.prompt_selector.currentText()
        
        if not model_name:
            self.chat_history.append(f"<span style='color: red;'><b>[系统]</b> 请先选择一个模型。</span>")
            return

        # Create and start worker
        self.btn_send.setEnabled(False)
        self.chat_history.append(f"<b>[系统]</b> 正在思考 ({model_name})...")
        
        # Prepare for streaming
        self.current_stream_response = ""
        self.chat_history.append("<b>[LLM助手]</b> ") # Start a new line for the assistant
        
        # Capture the start position for streaming updates
        cursor = self.chat_history.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.response_start_position = cursor.position()
        
        try:
            self.worker = LLMWorker(self.llm_service, full_input, model_name, prompt_name)
            self.worker.stream_updated.connect(self.on_llm_stream)
            self.worker.finished.connect(self.on_llm_response)
            self.worker.start()
        except Exception as e:
            self.btn_send.setEnabled(True)
            self.chat_history.append(f"<span style='color: red;'><b>[系统错误]</b> 启动 LLM 线程失败: {str(e)}</span>")
            QMessageBox.critical(self, "系统错误", f"无法启动 LLM 任务:\n{str(e)}")

    def on_llm_stream(self, chunk):
        """Handle streaming chunk with incremental Markdown rendering"""
        self.current_stream_response += chunk
        
        # Render current accumulated text to HTML
        try:
            html_response = markdown.markdown(self.current_stream_response)
        except Exception:
            # Fallback to raw text if markdown fails
            html_response = self.current_stream_response

        # Update the text area
        cursor = self.chat_history.textCursor()
        cursor.setPosition(self.response_start_position)
        cursor.movePosition(cursor.MoveOperation.End, cursor.MoveMode.KeepAnchor)
        
        # Replace the current content with the new rendered HTML
        # insertHtml will replace the selected text
        cursor.insertHtml(html_response)
        
        # Scroll to bottom
        scrollbar = self.chat_history.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def on_llm_response(self, response):
        """Handle response from LLM Worker"""
        # Check for error prefix from LLMService or Worker
        if response.startswith("Error:") or response.startswith("System Error:"):
             cursor = self.chat_history.textCursor()
             cursor.movePosition(cursor.MoveOperation.End)
             self.chat_history.append(f"<span style='color: red;'><b>[错误]</b> {response}</span>")
        
        # If not an error, the streaming handler has already rendered the final markdown.
        # We don't need to do anything else for the content.
        
        self.btn_send.setEnabled(True)

    def on_accept_strategy(self):
        """Accept current LLM strategy suggestion"""
        if not self.current_stock_code:
            QMessageBox.warning(self, "操作提示", "请先在左侧选择一只股票进行分析。")
            return
            
        code = self.current_stock_code
        name = self.current_stock_name
        
        # Check if already monitored
        for row in range(self.monitor_table.rowCount()):
            existing_code = self.monitor_table.item(row, 0).text()
            if existing_code == code:
                QMessageBox.information(self, "提示", f"{name} ({code}) 已经在监控列表中。")
                return

        # Add to monitor list
        row = self.monitor_table.rowCount()
        self.monitor_table.insertRow(row)
        
        self.monitor_table.setItem(row, 0, QTableWidgetItem(code))
        self.monitor_table.setItem(row, 1, QTableWidgetItem(name))
        
        status_item = QTableWidgetItem("待启动")
        status_item.setForeground(QColor("#FFA000")) # Orange
        status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.monitor_table.setItem(row, 2, status_item)
        
        # Generate and save mock strategy
        strategy_text = (f"策略名称: LLM智能推荐策略\n"
                         f"来源: {self.model_selector.currentText()}\n"
                         f"创建时间: 刚刚\n"
                         f"买入条件: 智能判定\n"
                         f"卖出条件: 智能判定\n"
                         f"风险偏好: {self.prompt_selector.currentText()}")
        
        self.mock_strategies[code] = strategy_text
        
        self.chat_history.append(f"<span style='color: green;'><b>[系统]</b> 已采纳 {name} 的策略建议，并加入监控列表。</span>")
        
        # Select the new item
        self.monitor_table.selectRow(row)
        self.on_monitor_selected(self.monitor_table.item(row, 0))

    def on_reject_strategy(self):
        """Reject current LLM strategy suggestion"""
        if not self.current_stock_code:
             return
             
        self.chat_history.append(f"<span style='color: red;'><b>[系统]</b> 已拒绝 {self.current_stock_name} 的策略建议。</span>")
        # Optionally clear selection or just log it


    def on_monitor_selected(self, item):
        row = item.row()
        code = self.monitor_table.item(row, 0).text()
        name = self.monitor_table.item(row, 1).text()
        status = self.monitor_table.item(row, 2).text()
        
        # Update details
        details = f"股票: {name} ({code})\n状态: {status}\n\n"
        details += self.mock_strategies.get(code, "暂无详细策略信息")
        self.strategy_details.setText(details)
        
        # Enable buttons based on status
        self.btn_delete.setEnabled(True)
        if status == "运行中":
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(True)
        else:
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)
            
    def on_start_strategy(self):
        row = self.monitor_table.currentRow()
        if row >= 0:
            self.monitor_table.item(row, 2).setText("运行中")
            self.monitor_table.item(row, 2).setForeground(QColor("#4CAF50"))
            self.on_monitor_selected(self.monitor_table.currentItem()) # Refresh UI
            self.strategy_details.append("\n[系统] 策略已启动")

    def on_stop_strategy(self):
        row = self.monitor_table.currentRow()
        if row >= 0:
            self.monitor_table.item(row, 2).setText("已停止")
            self.monitor_table.item(row, 2).setForeground(QColor("#FF5252"))
            self.on_monitor_selected(self.monitor_table.currentItem()) # Refresh UI
            self.strategy_details.append("\n[系统] 策略已停止")

    def on_delete_strategy(self):
        row = self.monitor_table.currentRow()
        if row >= 0:
            self.monitor_table.removeRow(row)
            self.strategy_details.clear()
            self.strategy_details.setPlaceholderText("策略已删除")
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(False)
            self.btn_delete.setEnabled(False)

