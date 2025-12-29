import sys
import os

# Add src to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from services.llm_service import LLMService
    print("Successfully imported LLMService")
except ImportError as e:
    print(f"Failed to import LLMService: {e}")
    # Try to debug imports
    try:
        import utils.config_manager
        print("Successfully imported utils.config_manager")
    except ImportError as e2:
        print(f"Failed to import utils.config_manager: {e2}")
    sys.exit(1)

def test_chat():
    service = LLMService()
    print("LLMService initialized")
    
    # Check config
    providers = service.config_manager.get_providers()
    print(f"Providers found: {list(providers.keys())}")
    
    # Mock a call (don't actually call OpenAI unless key is set, but check logic)
    # We will just check if we can get config
    model_name = "gpt-4" 
    config = service.get_provider_config(model_name)
    if config:
        print(f"Config found for {model_name}: {config.get('name')}")
    else:
        print(f"Config NOT found for {model_name}")

    # Test Prompt retrieval
    prompt = service.get_prompt_content("通用助手")
    print(f"Prompt '通用助手': {prompt[:20]}...")

if __name__ == "__main__":
    test_chat()
