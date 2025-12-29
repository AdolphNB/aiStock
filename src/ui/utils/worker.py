from PyQt6.QtCore import QThread, pyqtSignal

class LLMWorker(QThread):
    """
    Worker thread to handle LLM requests asynchronously.
    """
    finished = pyqtSignal(str)
    stream_updated = pyqtSignal(str)
    
    def __init__(self, service, user_input, model_name, prompt_name):
        super().__init__()
        self.service = service
        self.user_input = user_input
        self.model_name = model_name
        self.prompt_name = prompt_name
        
    def run(self):
        try:
            full_response = ""
            # Use chat_stream instead of chat
            for chunk in self.service.chat_stream(self.user_input, self.model_name, self.prompt_name):
                full_response += chunk
                self.stream_updated.emit(chunk)
                
            self.finished.emit(full_response)
        except Exception as e:
            self.finished.emit(f"System Error: {str(e)}")
