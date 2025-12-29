from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os

# Try to import ConfigManager
try:
    # If running as part of the package (e.g. from main.py)
    from utils.config_manager import ConfigManager
except ImportError:
    try:
        # If running from within src (e.g. for testing) but src is not a package
        import sys
        import os
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        from utils.config_manager import ConfigManager
    except ImportError:
        # Fallback absolute import (last resort)
        from src.utils.config_manager import ConfigManager

class LLMService:
    def __init__(self):
        self.config_manager = ConfigManager()

    def get_provider_config(self, model_name_selection):
        """
        Find the provider configuration based on the selected model name.
        """
        providers = self.config_manager.get_providers()
        for _, config in providers.items():
            if config.get("model_name") == model_name_selection:
                return config
        return None

    def get_prompt_content(self, prompt_name):
        """
        Retrieve the prompt template content by name.
        """
        prompts = self.config_manager.get_prompts()
        prompt_data = prompts.get(prompt_name)
        if prompt_data:
            return prompt_data.get("content", "")
        return ""

    def chat_stream(self, user_input, model_name, prompt_name):
        """
        Execute the chat with the LLM in streaming mode.
        Returns a generator yielding response chunks.
        """
        # 1. Get Config
        provider_config = self.get_provider_config(model_name)
        if not provider_config:
            yield f"Error: Configuration for model '{model_name}' not found. Please check your configuration."
            return

        api_key = provider_config.get("api_key")
        base_url = provider_config.get("base_url")
        
        if not api_key:
             yield f"Error: API Key for model '{model_name}' is missing."
             return

        # 2. Get Prompt
        system_prompt = self.get_prompt_content(prompt_name)
        if not system_prompt:
             # Fallback if no prompt selected or found
             system_prompt = "You are a helpful assistant for stock analysis."
        
        # 3. Initialize LLM
        kwargs = {
            "model": model_name,
            "api_key": api_key,
            "temperature": 0.7,
            "streaming": True  # Enable streaming
        }
        
        # Only add base_url if it's provided and not empty
        if base_url and base_url.strip():
            kwargs["base_url"] = base_url
            
        try:
            llm = ChatOpenAI(**kwargs)
            
            # 4. Create Chain
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("user", "{input}")
            ])
            
            chain = prompt | llm | StrOutputParser()
            
            # 5. Stream
            for chunk in chain.stream({"input": user_input}):
                yield chunk
            
        except Exception as e:
            yield f"Error calling LLM: {str(e)}"
