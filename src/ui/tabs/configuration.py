from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox, 
                             QLineEdit, QComboBox, QPushButton, QScrollArea, QListWidget, 
                             QLabel, QSplitter, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from ..theme_manager import ThemeManager
from ..dialogs import LLMProviderDialog, PromptTemplateDialog
try:
    from ...utils.config_manager import ConfigManager
except ImportError:
    from utils.config_manager import ConfigManager

class ConfigTab(QWidget):
    # Signal emitted when model list changes, passing list of model names
    modelsUpdated = pyqtSignal(list)
    promptsUpdated = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.providers = self.config_manager.get_providers()
        self.prompts = self.config_manager.get_prompts()
        
        self.init_ui()

    def get_model_names(self):
        """Extract just the model names from providers"""
        return [p.get('model_name', '') for p in self.providers.values() if p.get('model_name')]

    def refresh_provider_list(self):
        """Update the UI list and emit signal"""
        self.provider_list.clear()
        # We display model_name in the list as requested, but store provider key in item data
        for key, data in self.providers.items():
            model_name = data.get('model_name', 'Unknown')
            # Create item
            item_text = f"{model_name}" 
            # Note: If we just show model_name, we might have duplicates visually if multiple providers use same model name.
            # But user asked for "only show model name".
            # We need to store the 'key' (provider name) to find the record later for editing.
            from PyQt6.QtWidgets import QListWidgetItem
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, key) 
            self.provider_list.addItem(item)
        
        # Emit signal with list of model names
        self.modelsUpdated.emit(self.get_model_names())

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # --- Left Column: LLM Configuration ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 5, 0)
        
        # 1. LLM Providers Manager
        left_layout.addWidget(self.create_llm_provider_group())
        
        # 2. Prompt Templates Manager
        left_layout.addWidget(self.create_prompt_manager_group())
        
        # --- Right Column: Strategy & Notification & Appearance ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(5, 0, 0, 0)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # 3. Appearance Config
        right_layout.addWidget(self.create_appearance_group())

        # 4. Strategy Config
        right_layout.addWidget(self.create_strategy_group())
        
        # 5. Notification Config
        right_layout.addWidget(self.create_notify_group())
        
        # Save Button
        self.save_btn = QPushButton("保存全部配置")
        self.save_btn.setFixedHeight(40)
        self.save_btn.setStyleSheet("background-color: #0078d7; color: white; font-weight: bold;")
        self.save_btn.clicked.connect(self.save_all_configs)
        right_layout.addStretch()
        right_layout.addWidget(self.save_btn)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        
        # Set initial sizes: left panel ~600px, right panel ~600px for balanced display
        # These proportions will be maintained on maximize
        splitter.setSizes([700, 700])
        
        # Set minimum widths to ensure reasonable display
        left_widget.setMinimumWidth(400)
        right_widget.setMinimumWidth(400)
        
        # Make splitter handle more visible for easy adjustment
        splitter.setHandleWidth(2)
        
        main_layout.addWidget(splitter)

    def save_all_configs(self):
        """Save all configurations from the right column"""
        # Save Strategy
        strategy_data = {
            "refresh_rate": self.refresh_rate.currentText(),
            "ma_period": self.ma_period.text()
        }
        self.config_manager.set_strategy(strategy_data)
        
        # Save Notification
        notify_data = {
            "feishu_webhook": self.feishu_webhook.text(),
            "wechat_webhook": self.wechat_webhook.text()
        }
        self.config_manager.set_notification(notify_data)
        
        # Theme is already saved on change, but we can save it again to be sure or if we change logic
        appearance_data = {
            "theme": self.theme_selector.currentText()
        }
        self.config_manager.set_appearance(appearance_data)
        
        # Show feedback (optional, maybe status bar or just console log)
        print("All configurations saved.")

    def create_list_manager_ui(self, title):
        group = QGroupBox(title)
        layout = QVBoxLayout(group)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        toolbar_layout.addStretch()
        btn_add = QPushButton("+")
        btn_add.setFixedSize(30, 30)
        btn_remove = QPushButton("-")
        btn_remove.setFixedSize(30, 30)
        toolbar_layout.addWidget(btn_add)
        toolbar_layout.addWidget(btn_remove)
        
        # List
        list_widget = QListWidget()
        # list_widget.setMaximumHeight(150) # Allow it to expand
        
        layout.addLayout(toolbar_layout)
        layout.addWidget(list_widget)
        
        return group, layout, list_widget, btn_add, btn_remove

    def create_llm_provider_group(self):
        group, _, self.provider_list, self.btn_add_provider, self.btn_del_provider = \
            self.create_list_manager_ui("大模型列表 (Large Model List)")
        
        # Load Data
        self.refresh_provider_list()
        
        # Connect Signals
        self.btn_add_provider.clicked.connect(self.add_provider)
        self.btn_del_provider.clicked.connect(self.del_provider)
        self.provider_list.itemDoubleClicked.connect(self.edit_provider)
        
        return group

    def create_prompt_manager_group(self):
        group, _, self.prompt_list, self.btn_add_prompt, self.btn_del_prompt = \
            self.create_list_manager_ui("提示词模板管理")
        
        # Load Data
        self.prompt_list.addItems(self.prompts.keys())
        
        # Connect Signals
        self.btn_add_prompt.clicked.connect(self.add_prompt)
        self.btn_del_prompt.clicked.connect(self.del_prompt)
        self.prompt_list.itemDoubleClicked.connect(self.edit_prompt)
        
        return group
    
    # --- Interaction Logic: Providers ---
    def add_provider(self):
        dialog = LLMProviderDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            name = data['name']
            if name and name not in self.providers:
                self.providers[name] = data
                self.config_manager.set_providers(self.providers)
                self.refresh_provider_list()

    def edit_provider(self, item):
        # Retrieve key from UserRole
        name = item.data(Qt.ItemDataRole.UserRole)
        # Fallback if UserRole not set (should not happen with new logic but safe to keep)
        if not name: 
            name = item.text() 
            
        data = self.providers.get(name)
        if not data:
            return

        dialog = LLMProviderDialog(self, data)
        if dialog.exec():
            new_data = dialog.get_data()
            new_name = new_data['name']
            # Update storage
            if new_name != name:
                del self.providers[name]
            self.providers[new_name] = new_data
            self.config_manager.set_providers(self.providers)
            self.refresh_provider_list()

    def del_provider(self):
        row = self.provider_list.currentRow()
        if row >= 0:
            item = self.provider_list.item(row)
            name = item.data(Qt.ItemDataRole.UserRole)
            if name and name in self.providers:
                del self.providers[name]
                self.config_manager.set_providers(self.providers)
                self.refresh_provider_list()

    # --- Interaction Logic: Prompts ---
    def add_prompt(self):
        dialog = PromptTemplateDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            name = data['name']
            if name and name not in self.prompts:
                self.prompts[name] = data
                self.config_manager.set_prompts(self.prompts)
                self.prompt_list.addItem(name)
                self.promptsUpdated.emit(list(self.prompts.keys()))

    def edit_prompt(self, item):
        name = item.text()
        data = self.prompts.get(name)
        dialog = PromptTemplateDialog(self, data)
        if dialog.exec():
            new_data = dialog.get_data()
            new_name = new_data['name']
            # Update storage
            if new_name != name:
                del self.prompts[name]
                item.setText(new_name)
            self.prompts[new_name] = new_data
            self.config_manager.set_prompts(self.prompts)
            self.promptsUpdated.emit(list(self.prompts.keys()))

    def del_prompt(self):
        row = self.prompt_list.currentRow()
        if row >= 0:
            item = self.prompt_list.takeItem(row)
            del self.prompts[item.text()]
            self.config_manager.set_prompts(self.prompts)
            self.promptsUpdated.emit(list(self.prompts.keys()))

    # --- Right Column Groups ---
    def create_appearance_group(self):
        group = QGroupBox("界面外观")
        layout = QFormLayout(group)
        
        self.theme_selector = QComboBox()
        self.theme_selector.addItems(["Light", "Dark"])
        
        # Load saved theme
        appearance_config = self.config_manager.get_appearance()
        current_theme = appearance_config.get("theme", "Light")
        self.theme_selector.setCurrentText(current_theme)
        
        self.theme_selector.currentTextChanged.connect(self.change_theme)
        
        layout.addRow("主题风格:", self.theme_selector)
        return group

    def change_theme(self, theme_name):
        # Save theme setting
        self.config_manager.set_appearance({"theme": theme_name})
        
        app = QApplication.instance()
        if app:
            # Delay the theme application to avoid crashing if called during signal emission
            # or inside an event handler that might be affected by style changes.
            QTimer.singleShot(0, lambda: ThemeManager.apply_theme(app, theme_name))

    def create_strategy_group(self):
        group = QGroupBox("策略监控配置")
        layout = QFormLayout(group)
        
        self.refresh_rate = QComboBox()
        self.refresh_rate.addItems(["3秒", "5秒", "10秒", "30秒", "1分钟"])
        
        self.ma_period = QLineEdit("20")
        
        # Load saved strategy config
        strategy_config = self.config_manager.get_strategy()
        self.refresh_rate.setCurrentText(strategy_config.get("refresh_rate", "5秒"))
        self.ma_period.setText(strategy_config.get("ma_period", "20"))
        
        layout.addRow("数据刷新频率:", self.refresh_rate)
        layout.addRow("均线周期 (MA):", self.ma_period)
        return group

    def create_notify_group(self):
        group = QGroupBox("通知设置")
        layout = QFormLayout(group)
        
        self.feishu_webhook = QLineEdit()
        self.wechat_webhook = QLineEdit()
        
        # Load saved notification config
        notify_config = self.config_manager.get_notification()
        self.feishu_webhook.setText(notify_config.get("feishu_webhook", ""))
        self.wechat_webhook.setText(notify_config.get("wechat_webhook", ""))
        
        test_btn_layout = QHBoxLayout()
        self.test_feishu = QPushButton("测试飞书")
        self.test_wechat = QPushButton("测试企微")
        test_btn_layout.addWidget(self.test_feishu)
        test_btn_layout.addWidget(self.test_wechat)
        
        layout.addRow("飞书 Webhook:", self.feishu_webhook)
        layout.addRow("企微 Webhook:", self.wechat_webhook)
        layout.addRow(test_btn_layout)
        return group
