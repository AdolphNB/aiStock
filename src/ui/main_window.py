import sys
from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QLabel, QVBoxLayout, QWidget, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal

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
    # Signal for favorites update
    favoritesUpdated = pyqtSignal(list)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("股票助手 (AiStockMonitor)")
        
        # Set initial window size (startup size)
        self.resize(1400, 900)
        
        # Initialize config manager
        self.config_manager = ConfigManager()
        
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
        
        # Connect favorites signals
        self.favoritesUpdated.connect(self.tab_trading.update_favorites)
        self.favoritesUpdated.connect(self.tab_selection.update_favorites)
        
        # Connect add/remove favorite signals from tabs
        self.tab_trading.favoriteAdded.connect(self.on_favorite_added)
        self.tab_trading.favoriteRemoved.connect(self.on_favorite_removed)
        self.tab_selection.favoriteAdded.connect(self.on_favorite_added)
        self.tab_selection.favoriteRemoved.connect(self.on_favorite_removed)
        
        # Load initial favorites
        initial_favorites = self.config_manager.get_favorites()
        self.favoritesUpdated.emit(initial_favorites)
    
    def on_favorite_added(self, code, name):
        """Handle favorite stock added"""
        if self.config_manager.add_favorite(code, name):
            favorites = self.config_manager.get_favorites()
            self.favoritesUpdated.emit(favorites)
    
    def on_favorite_removed(self, code):
        """Handle favorite stock removed"""
        self.config_manager.remove_favorite(code)
        favorites = self.config_manager.get_favorites()
        self.favoritesUpdated.emit(favorites)
