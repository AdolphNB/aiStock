from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
                             QTableWidget, QTableWidgetItem, QTextEdit, QPushButton, 
                             QGroupBox, QHeaderView, QComboBox, QLabel, QDoubleSpinBox, 
                             QCheckBox, QAbstractItemView, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont
import markdown

try:
    from services.llm_service import LLMService
    from services.stock_data_service import StockDataService
    from ui.utils.worker import LLMWorker
except ImportError:
    # Fallback for relative imports
    from ...services.llm_service import LLMService
    from ...services.stock_data_service import StockDataService
    from ..utils.worker import LLMWorker

class SmartSelectionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.llm_service = LLMService()
        self.data_service = StockDataService()
        self.init_ui()
        self.load_initial_config()
        self.ai_analysis_queue = [] # Queue for auto-analysis

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

        # Main Horizontal Splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- Column 1: Primary Selection (Filter) ---
        col1_widget = QWidget()
        col1_layout = QVBoxLayout(col1_widget)
        col1_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create Vertical Splitter for Column 1
        col1_splitter = QSplitter(Qt.Orientation.Vertical)

        # Filter Controls Group
        filter_group = QGroupBox("初选条件")
        filter_layout = QVBoxLayout(filter_group)
        
        # Turnover Rate
        turnover_layout = QHBoxLayout()
        turnover_layout.addWidget(QLabel("换手率(%):"))
        self.spin_turnover_min = QDoubleSpinBox()
        self.spin_turnover_min.setRange(0, 100)
        self.spin_turnover_min.setValue(3.0)
        self.spin_turnover_max = QDoubleSpinBox()
        self.spin_turnover_max.setRange(0, 100)
        self.spin_turnover_max.setValue(15.0)
        turnover_layout.addWidget(self.spin_turnover_min)
        turnover_layout.addWidget(QLabel("-"))
        turnover_layout.addWidget(self.spin_turnover_max)
        filter_layout.addLayout(turnover_layout)
        
        # MA Bullish
        self.chk_ma_bullish = QCheckBox("均线多头排列 (5,10,20,60)")
        self.chk_ma_bullish.setChecked(True)
        filter_layout.addWidget(self.chk_ma_bullish)
        
        # Add stretch to push button to bottom
        filter_layout.addStretch()
        
        # Start Button
        self.btn_start_filter = QPushButton("开始初选")
        self.btn_start_filter.clicked.connect(self.on_start_filter)
        filter_layout.addWidget(self.btn_start_filter)
        
        col1_splitter.addWidget(filter_group)
        
        # Primary Result Table
        self.primary_table = QTableWidget(0, 4)
        self.primary_table.setHorizontalHeaderLabels(["代码", "名称", "换手%", "均线"])
        self.primary_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.primary_table.verticalHeader().setVisible(False)
        self.primary_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.primary_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.primary_table.itemClicked.connect(self.on_primary_item_clicked)
        
        col1_splitter.addWidget(self.primary_table)
        
        # Set initial sizes for splitter (50/50 roughly)
        col1_splitter.setStretchFactor(0, 1)
        col1_splitter.setStretchFactor(1, 1)
        
        col1_layout.addWidget(col1_splitter)
        
        # --- Column 2: LLM Assistant ---
        col2_widget = QWidget()
        col2_layout = QVBoxLayout(col2_widget)
        col2_layout.setContentsMargins(0, 0, 0, 0)
        
        chat_group = QGroupBox("AI 智能分析")
        chat_layout = QVBoxLayout(chat_group)
        
        # LLM Settings
        settings_layout = QHBoxLayout()
        self.model_selector = QComboBox()
        self.prompt_selector = QComboBox()
        
        settings_layout.addWidget(QLabel("模型:"))
        settings_layout.addWidget(self.model_selector, 1)
        settings_layout.addWidget(QLabel("提示词:"))
        settings_layout.addWidget(self.prompt_selector, 1)
        chat_layout.addLayout(settings_layout)
        
        # Chat Display
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setPlaceholderText("选择左侧股票进行分析，或点击“AI自动复选”批量分析...")
        chat_layout.addWidget(self.chat_history)
        
        # Input & Actions
        self.chat_input = QTextEdit()
        self.chat_input.setMaximumHeight(80)
        self.chat_input.setPlaceholderText("输入指令...")
        chat_layout.addWidget(self.chat_input)
        
        btn_layout = QHBoxLayout()
        self.btn_send = QPushButton("发送")
        self.btn_send.clicked.connect(self.on_send_message)
        
        self.btn_auto_analyze = QPushButton("✨ AI 自动复选")
        self.btn_auto_analyze.setToolTip("自动分析左侧初选池中的所有股票")
        self.btn_auto_analyze.clicked.connect(self.on_start_auto_analysis)
        self.btn_auto_analyze.setStyleSheet("background-color: #673AB7; color: white;")
        
        btn_layout.addWidget(self.btn_send, 2)
        btn_layout.addWidget(self.btn_auto_analyze, 1)
        chat_layout.addLayout(btn_layout)
        
        col2_layout.addWidget(chat_group)
        
        # --- Column 3: Results & Favorites ---
        col3_widget = QWidget()
        col3_layout = QVBoxLayout(col3_widget)
        col3_layout.setContentsMargins(0, 0, 0, 0)
        
        col3_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # TOP: LLM Selected
        llm_result_group = QGroupBox("AI 精选结果")
        llm_result_layout = QVBoxLayout(llm_result_group)
        self.llm_table = QTableWidget(0, 3)
        self.llm_table.setHorizontalHeaderLabels(["代码", "名称", "AI评分"])
        self.llm_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.llm_table.verticalHeader().setVisible(False)
        self.llm_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.llm_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        self.btn_add_fav = QPushButton("➕ 添加到自选")
        self.btn_add_fav.clicked.connect(self.on_add_to_favorites)
        
        llm_result_layout.addWidget(self.llm_table)
        llm_result_layout.addWidget(self.btn_add_fav)
        
        # BOTTOM: Favorites
        fav_group = QGroupBox("我的自选股池")
        fav_layout = QVBoxLayout(fav_group)
        self.fav_table = QTableWidget(0, 2)
        self.fav_table.setHorizontalHeaderLabels(["代码", "名称"])
        self.fav_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.fav_table.verticalHeader().setVisible(False)
        self.fav_table.setAlternatingRowColors(True)
        self.fav_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.fav_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        self.btn_remove_fav = QPushButton("❌ 移除自选")
        self.btn_remove_fav.clicked.connect(self.on_remove_favorites)
        
        fav_layout.addWidget(self.fav_table)
        fav_layout.addWidget(self.btn_remove_fav)
        
        col3_splitter.addWidget(llm_result_group)
        col3_splitter.addWidget(fav_group)
        
        col3_layout.addWidget(col3_splitter)
        
        # Add to Main Splitter
        main_splitter.addWidget(col1_widget)
        main_splitter.addWidget(col2_widget)
        main_splitter.addWidget(col3_widget)
        main_splitter.setSizes([300, 500, 300]) # Initial sizes
        
        layout.addWidget(main_splitter)

    # --- Logic ---

    def update_models(self, model_names):
        """Update model selector options"""
        current = self.model_selector.currentText()
        self.model_selector.clear()
        self.model_selector.addItems(model_names)
        if current:
            idx = self.model_selector.findText(current)
            if idx >= 0: self.model_selector.setCurrentIndex(idx)

    def update_prompts(self, prompt_names):
        """Update prompt selector options"""
        current = self.prompt_selector.currentText()
        self.prompt_selector.clear()
        self.prompt_selector.addItems(prompt_names)
        if current:
            idx = self.prompt_selector.findText(current)
            if idx >= 0: self.prompt_selector.setCurrentIndex(idx)

    def on_start_filter(self):
        """Primary Selection Logic"""
        min_t = self.spin_turnover_min.value()
        max_t = self.spin_turnover_max.value()
        ma_bull = self.chk_ma_bullish.isChecked()
        
        results = self.data_service.filter_stocks(min_t, max_t, ma_bull)
        
        self.primary_table.setRowCount(0)
        self.primary_table.setRowCount(len(results))
        
        for row, data in enumerate(results):
            self.primary_table.setItem(row, 0, QTableWidgetItem(data["code"]))
            self.primary_table.setItem(row, 1, QTableWidgetItem(data["name"]))
            
            t_item = QTableWidgetItem(f"{data['turnover']}%")
            t_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.primary_table.setItem(row, 2, t_item)
            
            ma_val = "是" if data["ma_bullish"] else "否"
            ma_item = QTableWidgetItem(ma_val)
            ma_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if data["ma_bullish"]:
                ma_item.setForeground(QColor("red"))
            self.primary_table.setItem(row, 3, ma_item)

    def on_primary_item_clicked(self, item):
        """Update chat context when clicking a stock"""
        row = item.row()
        code = self.primary_table.item(row, 0).text()
        name = self.primary_table.item(row, 1).text()
        
        self.chat_history.append(f"<b>[系统]</b> 已选中: {name} ({code})，准备分析...")
        self.chat_input.setText(f"请分析 {name} ({code}) 的近期走势及投资价值。")

    def on_send_message(self):
        """Standard Chat Send"""
        text = self.chat_input.toPlainText().strip()
        if not text: return
        self.process_chat_request(text)

    def process_chat_request(self, text, is_auto=False):
        """Process a chat request, potentially part of auto-analysis"""
        self.chat_history.append(f"<b>[用户]</b> {text}")
        self.chat_input.clear()
        self.btn_send.setEnabled(False)
        self.btn_auto_analyze.setEnabled(False) # Lock during process
        
        model_name = self.model_selector.currentText()
        prompt_name = self.prompt_selector.currentText()
        
        self.chat_history.append(f"<b>[系统]</b> 思考中 ({model_name})...")
        
        # Prepare streaming
        self.current_stream_response = ""
        self.chat_history.append("<b>[LLM]</b> ")
        cursor = self.chat_history.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.response_start_position = cursor.position()
        
        try:
            self.worker = LLMWorker(self.llm_service, text, model_name, prompt_name)
            self.worker.stream_updated.connect(self.on_llm_stream)
            # Pass is_auto flag via lambda if needed, but worker finished is generic.
            # We'll handle post-processing in finished.
            self.worker.finished.connect(lambda r: self.on_llm_finished(r, is_auto))
            self.worker.start()
        except Exception as e:
            self.chat_history.append(f"<span style='color:red'>启动失败: {str(e)}</span>")
            self.btn_send.setEnabled(True)
            self.btn_auto_analyze.setEnabled(True)

    def on_llm_stream(self, chunk):
        self.current_stream_response += chunk
        try:
            html = markdown.markdown(self.current_stream_response)
        except:
            html = self.current_stream_response
            
        cursor = self.chat_history.textCursor()
        cursor.setPosition(self.response_start_position)
        cursor.movePosition(cursor.MoveOperation.End, cursor.MoveMode.KeepAnchor)
        cursor.insertHtml(html)
        
        sb = self.chat_history.verticalScrollBar()
        sb.setValue(sb.maximum())

    def on_llm_finished(self, response, is_auto):
        self.btn_send.setEnabled(True)
        
        # If auto-analysis, maybe add to result list based on keyword?
        # Simulation: if "买入" or "推荐" in response, add to AI Results.
        if is_auto:
            # Simple heuristic for demo
            score = "High" if "买" in response or "高" in response else "Medium"
            
            # Find which stock we were analyzing
            # (In a real app, we'd track the current analyzing stock clearer)
            # For now, popping from queue
            if self.ai_analysis_queue:
                stock = self.ai_analysis_queue.pop(0)
                self.add_to_llm_results(stock["code"], stock["name"], score)
                
                # Check if we should continue queue
                if self.ai_analysis_queue:
                    QTimer.singleShot(1000, self.process_next_auto_analysis)
                else:
                    self.chat_history.append("<b>[系统]</b> 自动复选完成！")
                    self.btn_auto_analyze.setEnabled(True)
                    return

        self.btn_auto_analyze.setEnabled(True)

    # --- Auto Analysis Logic ---
    def on_start_auto_analysis(self):
        """Iterate through primary list and ask LLM"""
        count = self.primary_table.rowCount()
        if count == 0:
            QMessageBox.warning(self, "提示", "请先进行初选！")
            return
            
        self.ai_analysis_queue = []
        for row in range(count):
            code = self.primary_table.item(row, 0).text()
            name = self.primary_table.item(row, 1).text()
            self.ai_analysis_queue.append({"code": code, "name": name})
            
        self.chat_history.append(f"<b>[系统]</b> 开始对 {len(self.ai_analysis_queue)} 只股票进行自动复选...")
        self.process_next_auto_analysis()

    def process_next_auto_analysis(self):
        if not self.ai_analysis_queue: return
        
        stock = self.ai_analysis_queue[0] # Peek
        prompt = f"请简要评估股票 {stock['name']} ({stock['code']}) 的是否符合买入标准？"
        self.process_chat_request(prompt, is_auto=True)

    def add_to_llm_results(self, code, name, score):
        row = self.llm_table.rowCount()
        self.llm_table.insertRow(row)
        self.llm_table.setItem(row, 0, QTableWidgetItem(code))
        self.llm_table.setItem(row, 1, QTableWidgetItem(name))
        self.llm_table.setItem(row, 2, QTableWidgetItem(score))

    # --- Favorites Logic ---
    def on_add_to_favorites(self):
        row = self.llm_table.currentRow()
        if row < 0: return
        
        code = self.llm_table.item(row, 0).text()
        name = self.llm_table.item(row, 1).text()
        
        # Check duplicates
        for r in range(self.fav_table.rowCount()):
            if self.fav_table.item(r, 0).text() == code:
                return 
        
        fav_row = self.fav_table.rowCount()
        self.fav_table.insertRow(fav_row)
        self.fav_table.setItem(fav_row, 0, QTableWidgetItem(code))
        self.fav_table.setItem(fav_row, 1, QTableWidgetItem(name))

    def on_remove_favorites(self):
        row = self.fav_table.currentRow()
        if row >= 0:
            self.fav_table.removeRow(row)
