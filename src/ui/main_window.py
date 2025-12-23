import sys
from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QLabel, QVBoxLayout, QWidget, QApplication)
from PyQt6.QtCore import Qt

# Import Tab Widgets
from .tabs.trading_monitor import TradingMonitorTab
from .tabs.smart_selection import SmartSelectionTab
from .tabs.configuration import ConfigTab
from .theme_manager import ThemeManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("股票助手 (AiStockMonitor)")
        self.resize(1280, 800)
        
        # Central Widget - QTabWidget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Initialize Tabs
        self.init_tabs()
        
        # Apply Initial Theme (Light)
        ThemeManager.apply_theme(QApplication.instance(), "Light")

    def init_tabs(self):
        # 1. Trading Monitor Tab
        self.tab_trading = TradingMonitorTab()
        self.tabs.addTab(self.tab_trading, "交易监控")
        
        # 2. Smart Selection Tab
        self.tab_selection = SmartSelectionTab()
        self.tabs.addTab(self.tab_selection, "选股")
        
        # 3. Configuration Tab
        self.tab_config = ConfigTab()
        self.tabs.addTab(self.tab_config, "配置")

        # Connect signals for model synchronization
        self.tab_config.modelsUpdated.connect(self.tab_trading.update_models)
        self.tab_config.modelsUpdated.connect(self.tab_selection.update_models)

        # Initial synchronization
        initial_models = self.tab_config.get_model_names()
        self.tab_trading.update_models(initial_models)
        self.tab_selection.update_models(initial_models)
