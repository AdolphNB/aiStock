from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
                             QTableWidget, QTableWidgetItem, QTextEdit, QPushButton, 
                             QGroupBox, QHeaderView, QComboBox, QLabel, QDoubleSpinBox, 
                             QCheckBox, QAbstractItemView, QMessageBox, QTabWidget,
                             QScrollArea, QSpinBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
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
    # Signals for favorite stock management
    favoriteAdded = pyqtSignal(str, str)  # code, name
    favoriteRemoved = pyqtSignal(str)  # code
    
    def __init__(self):
        super().__init__()
        self.llm_service = LLMService()
        self.data_service = StockDataService()
        self.init_ui()
        self.load_initial_config()
        self.ai_analysis_queue = [] # Queue for auto-analysis
        
        # Load all stocks on initialization
        self.load_all_stocks()
        
        # Disable all controls (feature under development)
        self.disable_all_controls()

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
        
        # Create tab widget for short-term and mid-term filters
        filter_tabs = QTabWidget()
        
        # === Short-term Trading Filters ===
        short_term_widget = QWidget()
        short_term_layout = QVBoxLayout(short_term_widget)
        
        # Create scroll area for short-term filters
        short_scroll = QScrollArea()
        short_scroll.setWidgetResizable(True)
        short_scroll_widget = QWidget()
        short_scroll_layout = QVBoxLayout(short_scroll_widget)
        
        # Turnover Rate
        turnover_layout = QHBoxLayout()
        self.chk_turnover = QCheckBox("换手率(%):")
        turnover_layout.addWidget(self.chk_turnover)
        self.spin_turnover_min = QDoubleSpinBox()
        self.spin_turnover_min.setRange(0, 100)
        self.spin_turnover_min.setValue(3.0)
        self.spin_turnover_max = QDoubleSpinBox()
        self.spin_turnover_max.setRange(0, 100)
        self.spin_turnover_max.setValue(15.0)
        turnover_layout.addWidget(self.spin_turnover_min)
        turnover_layout.addWidget(QLabel("-"))
        turnover_layout.addWidget(self.spin_turnover_max)
        turnover_layout.addStretch()
        short_scroll_layout.addLayout(turnover_layout)
        
        # Price Change Range
        change_layout = QHBoxLayout()
        self.chk_change = QCheckBox("涨跌幅(%):")
        change_layout.addWidget(self.chk_change)
        self.spin_change_min = QDoubleSpinBox()
        self.spin_change_min.setRange(-100, 100)
        self.spin_change_min.setValue(-5.0)
        self.spin_change_max = QDoubleSpinBox()
        self.spin_change_max.setRange(-100, 100)
        self.spin_change_max.setValue(10.0)
        change_layout.addWidget(self.spin_change_min)
        change_layout.addWidget(QLabel("-"))
        change_layout.addWidget(self.spin_change_max)
        change_layout.addStretch()
        short_scroll_layout.addLayout(change_layout)
        
        # Volume Ratio
        volume_layout = QHBoxLayout()
        self.chk_volume_ratio = QCheckBox("量比 ≥")
        volume_layout.addWidget(self.chk_volume_ratio)
        self.spin_volume_ratio = QDoubleSpinBox()
        self.spin_volume_ratio.setRange(0, 10)
        self.spin_volume_ratio.setValue(1.5)
        self.spin_volume_ratio.setSingleStep(0.1)
        volume_layout.addWidget(self.spin_volume_ratio)
        volume_layout.addStretch()
        short_scroll_layout.addLayout(volume_layout)
        
        # KDJ Indicators
        short_scroll_layout.addWidget(QLabel("<b>KDJ指标:</b>"))
        self.chk_kdj_golden = QCheckBox("KDJ金叉 (K>D, 低位)")
        short_scroll_layout.addWidget(self.chk_kdj_golden)
        self.chk_kdj_death = QCheckBox("KDJ死叉 (K<D, 高位)")
        short_scroll_layout.addWidget(self.chk_kdj_death)
        self.chk_kdj_low = QCheckBox("KDJ低位区 (K<20)")
        short_scroll_layout.addWidget(self.chk_kdj_low)
        self.chk_kdj_high = QCheckBox("KDJ高位区 (K>80)")
        short_scroll_layout.addWidget(self.chk_kdj_high)
        
        # MACD Indicators
        short_scroll_layout.addWidget(QLabel("<b>MACD指标:</b>"))
        self.chk_macd_golden = QCheckBox("MACD金叉 (DIF>DEA)")
        short_scroll_layout.addWidget(self.chk_macd_golden)
        self.chk_macd_death = QCheckBox("MACD死叉 (DIF<DEA)")
        short_scroll_layout.addWidget(self.chk_macd_death)
        self.chk_macd_above_zero = QCheckBox("MACD>0 (多头市场)")
        short_scroll_layout.addWidget(self.chk_macd_above_zero)
        
        # RSI Indicators
        short_scroll_layout.addWidget(QLabel("<b>RSI指标:</b>"))
        self.chk_rsi_oversold = QCheckBox("RSI超卖 (<30)")
        short_scroll_layout.addWidget(self.chk_rsi_oversold)
        self.chk_rsi_overbought = QCheckBox("RSI超买 (>70)")
        short_scroll_layout.addWidget(self.chk_rsi_overbought)
        
        short_scroll_layout.addStretch()
        short_scroll_widget.setLayout(short_scroll_layout)
        short_scroll.setWidget(short_scroll_widget)
        short_term_layout.addWidget(short_scroll)
        
        # === Mid-term Trading Filters ===
        mid_term_widget = QWidget()
        mid_term_layout = QVBoxLayout(mid_term_widget)
        
        # Create scroll area for mid-term filters
        mid_scroll = QScrollArea()
        mid_scroll.setWidgetResizable(True)
        mid_scroll_widget = QWidget()
        mid_scroll_layout = QVBoxLayout(mid_scroll_widget)
        
        # MA Bullish
        self.chk_ma_bullish = QCheckBox("均线多头排列 (5<10<20<60)")
        mid_scroll_layout.addWidget(self.chk_ma_bullish)
        
        # Price vs MA
        mid_scroll_layout.addWidget(QLabel("<b>价格位置:</b>"))
        self.chk_price_above_ma20 = QCheckBox("价格站上MA20")
        mid_scroll_layout.addWidget(self.chk_price_above_ma20)
        self.chk_price_above_ma60 = QCheckBox("价格站上MA60")
        mid_scroll_layout.addWidget(self.chk_price_above_ma60)
        
        # Bollinger Bands
        mid_scroll_layout.addWidget(QLabel("<b>布林带:</b>"))
        self.chk_boll_lower = QCheckBox("突破下轨 (超跌反弹)")
        mid_scroll_layout.addWidget(self.chk_boll_lower)
        self.chk_boll_upper = QCheckBox("突破上轨 (强势突破)")
        mid_scroll_layout.addWidget(self.chk_boll_upper)
        
        mid_scroll_layout.addStretch()
        mid_scroll_widget.setLayout(mid_scroll_layout)
        mid_scroll.setWidget(mid_scroll_widget)
        mid_term_layout.addWidget(mid_scroll)
        
        # Add tabs
        filter_tabs.addTab(short_term_widget, "短线")
        filter_tabs.addTab(mid_term_widget, "中线")
        
        filter_layout.addWidget(filter_tabs)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_reset_filter = QPushButton("重置")
        self.btn_reset_filter.clicked.connect(self.on_reset_filter)
        self.btn_start_filter = QPushButton("开始筛选")
        self.btn_start_filter.clicked.connect(self.on_start_filter)
        self.btn_start_filter.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        btn_layout.addWidget(self.btn_reset_filter)
        btn_layout.addWidget(self.btn_start_filter)
        filter_layout.addLayout(btn_layout)
        
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
        
        # Set initial sizes: left panel ~320px, middle panel ~680px, right panel ~400px
        # These proportions will be maintained on maximize
        main_splitter.setSizes([320, 680, 400])
        
        # Set minimum widths to ensure reasonable display
        col1_widget.setMinimumWidth(280)
        col2_widget.setMinimumWidth(400)
        col3_widget.setMinimumWidth(280)
        
        # Make splitter handle more visible for easy adjustment
        main_splitter.setHandleWidth(2)
        
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

    def load_all_stocks(self):
        """Load all stocks when tab is first opened"""
        try:
            all_stocks = self.data_service.get_all_stocks()
            self.populate_table(all_stocks)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载股票列表失败: {str(e)}")
    
    def on_reset_filter(self):
        """Reset all filters and reload all stocks"""
        # Reset short-term filters
        self.chk_turnover.setChecked(False)
        self.spin_turnover_min.setValue(3.0)
        self.spin_turnover_max.setValue(15.0)
        
        self.chk_change.setChecked(False)
        self.spin_change_min.setValue(-5.0)
        self.spin_change_max.setValue(10.0)
        
        self.chk_volume_ratio.setChecked(False)
        self.spin_volume_ratio.setValue(1.5)
        
        self.chk_kdj_golden.setChecked(False)
        self.chk_kdj_death.setChecked(False)
        self.chk_kdj_low.setChecked(False)
        self.chk_kdj_high.setChecked(False)
        
        self.chk_macd_golden.setChecked(False)
        self.chk_macd_death.setChecked(False)
        self.chk_macd_above_zero.setChecked(False)
        
        self.chk_rsi_oversold.setChecked(False)
        self.chk_rsi_overbought.setChecked(False)
        
        # Reset mid-term filters
        self.chk_ma_bullish.setChecked(False)
        self.chk_price_above_ma20.setChecked(False)
        self.chk_price_above_ma60.setChecked(False)
        self.chk_boll_lower.setChecked(False)
        self.chk_boll_upper.setChecked(False)
        
        # Reload all stocks
        self.load_all_stocks()
    
    def on_start_filter(self):
        """Primary Selection Logic with enhanced filters"""
        criteria = {}
        
        # Short-term filters
        if self.chk_turnover.isChecked():
            criteria['min_turnover'] = self.spin_turnover_min.value()
            criteria['max_turnover'] = self.spin_turnover_max.value()
        
        if self.chk_change.isChecked():
            criteria['min_change'] = self.spin_change_min.value()
            criteria['max_change'] = self.spin_change_max.value()
        
        if self.chk_volume_ratio.isChecked():
            criteria['min_volume_ratio'] = self.spin_volume_ratio.value()
        
        # KDJ filters
        if self.chk_kdj_golden.isChecked():
            criteria['kdj_golden_cross'] = True
        if self.chk_kdj_death.isChecked():
            criteria['kdj_death_cross'] = True
        if self.chk_kdj_low.isChecked():
            criteria['kdj_low_area'] = True
        if self.chk_kdj_high.isChecked():
            criteria['kdj_high_area'] = True
        
        # MACD filters
        if self.chk_macd_golden.isChecked():
            criteria['macd_golden_cross'] = True
        if self.chk_macd_death.isChecked():
            criteria['macd_death_cross'] = True
        if self.chk_macd_above_zero.isChecked():
            criteria['macd_above_zero'] = True
        
        # RSI filters
        if self.chk_rsi_oversold.isChecked():
            criteria['rsi_oversold'] = True
        if self.chk_rsi_overbought.isChecked():
            criteria['rsi_overbought'] = True
        
        # Mid-term filters
        if self.chk_ma_bullish.isChecked():
            criteria['ma_bullish'] = True
        if self.chk_price_above_ma20.isChecked():
            criteria['price_above_ma20'] = True
        if self.chk_price_above_ma60.isChecked():
            criteria['price_above_ma60'] = True
        if self.chk_boll_lower.isChecked():
            criteria['boll_lower_break'] = True
        if self.chk_boll_upper.isChecked():
            criteria['boll_upper_break'] = True
        
        # If no criteria selected, show all stocks
        if not criteria:
            QMessageBox.information(self, "提示", "未选择任何筛选条件，显示所有股票")
            self.load_all_stocks()
            return
        
        # Apply filters
        try:
            results = self.data_service.filter_stocks(criteria)
            self.populate_table(results)
            
            # Show result count
            QMessageBox.information(self, "筛选完成", 
                                  f"共筛选出 {len(results)} 只符合条件的股票")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"筛选失败: {str(e)}")
    
    def populate_table(self, stocks):
        """Populate the primary table with stock data"""
        self.primary_table.setRowCount(0)
        self.primary_table.setRowCount(len(stocks))
        
        for row, data in enumerate(stocks):
            self.primary_table.setItem(row, 0, QTableWidgetItem(data["code"]))
            self.primary_table.setItem(row, 1, QTableWidgetItem(data["name"]))
            
            t_item = QTableWidgetItem(f"{data.get('turnover', 0):.2f}%")
            t_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.primary_table.setItem(row, 2, t_item)
            
            ma_val = "✓" if data.get("ma_bullish", False) else "✗"
            ma_item = QTableWidgetItem(ma_val)
            ma_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if data.get("ma_bullish", False):
                ma_item.setForeground(QColor("#4CAF50"))
            else:
                ma_item.setForeground(QColor("#999"))
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
            # Enable table extension and other useful extensions for markdown rendering
            html = markdown.markdown(
                self.current_stream_response, 
                extensions=['tables', 'fenced_code', 'nl2br', 'sane_lists']
            )
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
        """Add selected stock from AI results to favorites"""
        row = self.llm_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请先选择一只股票")
            return
        
        code = self.llm_table.item(row, 0).text()
        name = self.llm_table.item(row, 1).text()
        
        # Emit signal to add to favorites (MainWindow will handle duplicates)
        self.favoriteAdded.emit(code, name)

    def on_remove_favorites(self):
        """Remove selected stock from favorites"""
        row = self.fav_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请先选择要移除的股票")
            return
        
        code = self.fav_table.item(row, 0).text()
        name = self.fav_table.item(row, 1).text()
        
        reply = QMessageBox.question(self, "确认", 
                                    f"确定要从自选股中移除 {name} ({code}) 吗？",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.favoriteRemoved.emit(code)
    
    def update_favorites(self, favorites):
        """Update favorites table from config"""
        self.fav_table.setRowCount(0)
        self.fav_table.setRowCount(len(favorites))
        
        for row, fav in enumerate(favorites):
            code = fav.get('code', '')
            name = fav.get('name', '')
            
            code_item = QTableWidgetItem(code)
            code_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.fav_table.setItem(row, 0, code_item)
            
            name_item = QTableWidgetItem(name)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.fav_table.setItem(row, 1, name_item)
    
    def disable_all_controls(self):
        """Disable all controls in the smart selection tab"""
        # Disable all checkboxes (short-term filters)
        self.chk_turnover.setEnabled(False)
        self.chk_change.setEnabled(False)
        self.chk_volume_ratio.setEnabled(False)
        self.chk_kdj_golden.setEnabled(False)
        self.chk_kdj_death.setEnabled(False)
        self.chk_kdj_low.setEnabled(False)
        self.chk_kdj_high.setEnabled(False)
        self.chk_macd_golden.setEnabled(False)
        self.chk_macd_death.setEnabled(False)
        self.chk_macd_above_zero.setEnabled(False)
        self.chk_rsi_oversold.setEnabled(False)
        self.chk_rsi_overbought.setEnabled(False)
        
        # Disable all checkboxes (mid-term filters)
        self.chk_ma_bullish.setEnabled(False)
        self.chk_price_above_ma20.setEnabled(False)
        self.chk_price_above_ma60.setEnabled(False)
        self.chk_boll_lower.setEnabled(False)
        self.chk_boll_upper.setEnabled(False)
        
        # Disable all spinboxes
        self.spin_turnover_min.setEnabled(False)
        self.spin_turnover_max.setEnabled(False)
        self.spin_change_min.setEnabled(False)
        self.spin_change_max.setEnabled(False)
        self.spin_volume_ratio.setEnabled(False)
        
        # Disable all buttons
        self.btn_reset_filter.setEnabled(False)
        self.btn_start_filter.setEnabled(False)
        self.btn_send.setEnabled(False)
        self.btn_auto_analyze.setEnabled(False)
        self.btn_add_fav.setEnabled(False)
        self.btn_remove_fav.setEnabled(False)
        
        # Disable comboboxes
        self.model_selector.setEnabled(False)
        self.prompt_selector.setEnabled(False)
        
        # Disable text input
        self.chat_input.setEnabled(False)
        
        # Disable tables (set to no selection)
        self.primary_table.setEnabled(False)
        self.llm_table.setEnabled(False)
        self.fav_table.setEnabled(False)