from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                             QDialogButtonBox, QTextEdit, QLabel)

class BaseDialog(QDialog):
    def __init__(self, parent=None, title="Dialog"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        self.layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()
        self.layout.addLayout(self.form_layout)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                           QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def add_input(self, label, widget):
        self.form_layout.addRow(label, widget)

class LLMProviderDialog(BaseDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent, "编辑大模型供应商" if data else "新增大模型供应商")
        self.data = data or {}
        
        self.name_input = QLineEdit(self.data.get("name", ""))
        self.api_key_input = QLineEdit(self.data.get("api_key", ""))
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.base_url_input = QLineEdit(self.data.get("base_url", ""))
        self.model_name_input = QLineEdit(self.data.get("model_name", ""))
        
        self.add_input("供应商名称:", self.name_input)
        self.add_input("API Key:", self.api_key_input)
        self.add_input("Base URL (可选):", self.base_url_input)
        self.add_input("模型名称:", self.model_name_input)

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "api_key": self.api_key_input.text(),
            "base_url": self.base_url_input.text(),
            "model_name": self.model_name_input.text()
        }

class PromptTemplateDialog(BaseDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent, "编辑提示词模板" if data else "新增提示词模板")
        self.data = data or {}
        self.resize(800, 600)
        
        self.name_input = QLineEdit(self.data.get("name", ""))
        self.content_input = QTextEdit()
        self.content_input.setPlainText(self.data.get("content", ""))
        
        self.add_input("模板名称:", self.name_input)
        self.layout.addWidget(QLabel("提示词内容:"))
        self.layout.addWidget(self.content_input)
        
        # Move buttons to bottom again since we added widgets directly to VBox
        self.layout.removeWidget(self.button_box)
        self.layout.addWidget(self.button_box)

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "content": self.content_input.toPlainText()
        }
