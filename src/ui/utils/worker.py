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


class KLineWorker(QThread):
    """
    Worker thread to load K-line data asynchronously to avoid UI blocking.
    """
    finished = pyqtSignal(str, str, list)  # stock_code, stock_name, kline_data
    error = pyqtSignal(str, str)  # stock_name, error_message
    
    def __init__(self, data_service, stock_code, stock_name, period="daily", adjust="qfq", days=60):
        super().__init__()
        self.data_service = data_service
        self.stock_code = stock_code
        self.stock_name = stock_name
        self.period = period
        self.adjust = adjust
        self.days = days
        
    def run(self):
        try:
            # Fetch K-line data from server
            kline_data = self.data_service.fetch_kline_data(
                self.stock_code, 
                period=self.period, 
                adjust=self.adjust, 
                days=self.days
            )
            
            if kline_data:
                self.finished.emit(self.stock_code, self.stock_name, kline_data)
            else:
                self.error.emit(self.stock_name, "无法获取K线数据")
        except Exception as e:
            self.error.emit(self.stock_name, f"加载K线数据失败: {str(e)}")
