import sys
from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QLabel, QVBoxLayout, QWidget, QApplication)
from PyQt6.QtCore import Qt

# Import Tab Widgets
from .tabs.trading_monitor import TradingMonitorTab
from .tabs.smart_selection import SmartSelectionTab
from .tabs.configuration import ConfigTab
from .theme_manager import ThemeManager

try:
    from ..utils.config_manager import ConfigManager
except ImportError:
    from utils.config_manager import ConfigManager

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
        
        # Apply Initial Theme
        self.apply_initial_theme()

    def apply_initial_theme(self):
        config_manager = ConfigManager()
        appearance_config = config_manager.get_appearance()
        theme = appearance_config.get("theme", "Light")
        ThemeManager.apply_theme(QApplication.instance(), theme)

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

        # Connect signals for prompt synchronization
        self.tab_config.promptsUpdated.connect(self.tab_trading.update_prompts)
        self.tab_config.promptsUpdated.connect(self.tab_selection.update_prompts)

        # Initial synchronization
        initial_models = self.tab_config.get_model_names()
        self.tab_trading.update_models(initial_models)
        self.tab_selection.update_models(initial_models)

        # Initial prompt synchronization
        # We need to expose get_prompt_names in ConfigTab or access via manager, 
        # but ConfigTab manages the state so let's use its prompts dict.
        initial_prompts = list(self.tab_config.prompts.keys())
        self.tab_trading.update_prompts(initial_prompts)
        self.tab_selection.update_prompts(initial_prompts)
