import json
import os

class ConfigManager:
    _instance = None
    # Calculate path: src/utils/config_manager.py -> src/utils -> src -> root -> config/config.json
    CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'config.json'))

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.load_config()
        self._initialized = True

    def load_config(self):
        # Default Configuration
        self.config = {
            "llm_providers": {
                "OpenAI (Default)": {"name": "OpenAI (Default)", "api_key": "sk-...", "base_url": "", "model_name": "gpt-4"},
                "Local (Ollama)": {"name": "Local (Ollama)", "api_key": "", "base_url": "http://localhost:11434", "model_name": "llama3"}
            },
            "prompts": {
                "通用助手": {"name": "通用助手", "content": "你是一个有用的助手..."},
                "短线交易员": {"name": "短线交易员", "content": "关注短期波动..."}
            },
            "appearance": {
                "theme": "Light"
            },
            "strategy": {
                "refresh_rate": "5秒",
                "ma_period": "20"
            },
            "notification": {
                "feishu_webhook": "",
                "wechat_webhook": ""
            }
        }
        
        if os.path.exists(self.CONFIG_PATH):
            try:
                with open(self.CONFIG_PATH, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Update config with loaded values
                    for key in ["llm_providers", "prompts", "appearance", "strategy", "notification"]:
                        if key in loaded_config:
                            self.config[key] = loaded_config[key]
            except Exception as e:
                print(f"Error loading config: {e}")
        else:
            # Save default config if it doesn't exist
            self.save_config()

    def save_config(self):
        try:
            os.makedirs(os.path.dirname(self.CONFIG_PATH), exist_ok=True)
            with open(self.CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get_providers(self):
        return self.config.get("llm_providers", {})

    def set_providers(self, providers):
        self.config["llm_providers"] = providers
        self.save_config()

    def get_prompts(self):
        return self.config.get("prompts", {})

    def set_prompts(self, prompts):
        self.config["prompts"] = prompts
        self.save_config()

    def get_appearance(self):
        return self.config.get("appearance", {})

    def set_appearance(self, appearance):
        self.config["appearance"] = appearance
        self.save_config()

    def get_strategy(self):
        return self.config.get("strategy", {})

    def set_strategy(self, strategy):
        self.config["strategy"] = strategy
        self.save_config()

    def get_notification(self):
        return self.config.get("notification", {})

    def set_notification(self, notification):
        self.config["notification"] = notification
        self.save_config()
    
    def get_model_names(self):
        providers = self.get_providers()
        return [p.get('model_name', '') for p in providers.values() if p.get('model_name')]

    def get_prompt_names(self):
        prompts = self.get_prompts()
        return list(prompts.keys())
