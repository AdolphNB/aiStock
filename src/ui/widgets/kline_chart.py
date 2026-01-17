"""
K-line chart widget using pyqtgraph
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QPixmap, QPainter, QPen, QBrush, QImage
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional

class KLineChartWidget(QWidget):
    """Compact K-line chart widget with thumbnail preview"""
    
    def __init__(self, parent=None, compact_mode=True):
        super().__init__(parent)
        self.kline_data = []
        self.stock_code = ""
        self.stock_name = ""
        self.compact_mode = compact_mode
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Title label
        self.title_label = QLabel("K线预览")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #333;")
        layout.addWidget(self.title_label)
        
        # Image label for static preview
        self.chart_label = QLabel()
        self.chart_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chart_label.setMinimumHeight(120)
        self.chart_label.setMaximumHeight(120)
        self.chart_label.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        self.chart_label.setText("未加载数据")
        
        layout.addWidget(self.chart_label)
        
    def calculate_ma(self, close_prices: np.ndarray, period: int) -> np.ndarray:
        """Calculate moving average"""
        ma = np.full(len(close_prices), np.nan)
        for i in range(period - 1, len(close_prices)):
            ma[i] = np.mean(close_prices[i - period + 1:i + 1])
        return ma
    
    def update_chart(self, stock_code: str, stock_name: str, kline_data: List[Dict]):
        """
        Update chart with new K-line data
        
        Args:
            stock_code: Stock code
            stock_name: Stock name
            kline_data: List of K-line data dictionaries with keys:
                        date, open, close, high, low, volume
        """
        self.stock_code = stock_code
        self.stock_name = stock_name
        self.kline_data = kline_data
        
        if not kline_data:
            self.clear_chart()
            return
        
        # Update title
        self.title_label.setText(f"{stock_name}({stock_code})")
        
        # Generate static chart image
        self.render_compact_chart(kline_data)
    
    def render_compact_chart(self, kline_data: List[Dict]):
        """Render a compact static K-line chart image"""
        # Prepare data
        n = len(kline_data)
        if n == 0:
            return
        
        # Limit to last 30 days for compact view
        if n > 30:
            kline_data = kline_data[-30:]
            n = 30
        
        opens = np.array([d['open'] for d in kline_data])
        closes = np.array([d['close'] for d in kline_data])
        highs = np.array([d['high'] for d in kline_data])
        lows = np.array([d['low'] for d in kline_data])
        
        # Calculate price range
        max_price = np.max(highs)
        min_price = np.min(lows)
        price_range = max_price - min_price
        if price_range == 0:
            price_range = max_price * 0.1 if max_price > 0 else 1
        
        # Calculate moving averages
        ma5 = self.calculate_ma(closes, 5)
        ma10 = self.calculate_ma(closes, 10)
        
        # Create image
        img_width = self.width() if self.width() > 100 else 400
        img_height = 120
        padding = 10
        chart_width = img_width - 2 * padding
        chart_height = img_height - 2 * padding
        
        image = QImage(img_width, img_height, QImage.Format.Format_RGB32)
        image.fill(Qt.GlobalColor.white)
        
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate bar width
        bar_width = max(2, chart_width // (n * 2))
        spacing = chart_width / n
        
        # Draw K-line candles
        for i in range(n):
            open_price = opens[i]
            close_price = closes[i]
            high_price = highs[i]
            low_price = lows[i]
            
            # Calculate positions
            x = padding + i * spacing + spacing / 2
            y_high = padding + chart_height - ((high_price - min_price) / price_range * chart_height)
            y_low = padding + chart_height - ((low_price - min_price) / price_range * chart_height)
            y_open = padding + chart_height - ((open_price - min_price) / price_range * chart_height)
            y_close = padding + chart_height - ((close_price - min_price) / price_range * chart_height)
            
            # Determine color (red for up, green for down in China)
            is_up = close_price >= open_price
            color = QColor(255, 0, 0) if is_up else QColor(0, 180, 0)
            
            # Draw high-low line
            painter.setPen(QPen(color, 1))
            painter.drawLine(int(x), int(y_high), int(x), int(y_low))
            
            # Draw open-close box
            box_height = abs(y_close - y_open)
            if box_height < 1:
                box_height = 1
            box_y = min(y_open, y_close)
            
            painter.setBrush(QBrush(color))
            painter.drawRect(int(x - bar_width/2), int(box_y), int(bar_width), int(box_height))
        
        # Draw moving average lines
        # MA5 - Yellow
        if not np.all(np.isnan(ma5)):
            painter.setPen(QPen(QColor(255, 200, 0), 1.5))
            for i in range(1, n):
                if not np.isnan(ma5[i-1]) and not np.isnan(ma5[i]):
                    x1 = padding + (i-1) * spacing + spacing / 2
                    y1 = padding + chart_height - ((ma5[i-1] - min_price) / price_range * chart_height)
                    x2 = padding + i * spacing + spacing / 2
                    y2 = padding + chart_height - ((ma5[i] - min_price) / price_range * chart_height)
                    painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        
        # MA10 - Blue
        if not np.all(np.isnan(ma10)):
            painter.setPen(QPen(QColor(0, 120, 255), 1.5))
            for i in range(1, n):
                if not np.isnan(ma10[i-1]) and not np.isnan(ma10[i]):
                    x1 = padding + (i-1) * spacing + spacing / 2
                    y1 = padding + chart_height - ((ma10[i-1] - min_price) / price_range * chart_height)
                    x2 = padding + i * spacing + spacing / 2
                    y2 = padding + chart_height - ((ma10[i] - min_price) / price_range * chart_height)
                    painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        
        painter.end()
        
        # Convert to pixmap and display
        pixmap = QPixmap.fromImage(image)
        self.chart_label.setPixmap(pixmap)
    
    def clear_chart(self):
        """Clear the chart"""
        self.chart_label.clear()
        self.chart_label.setText("未加载数据")
        self.title_label.setText("K线预览")
        self.stock_code = ""
        self.stock_name = ""
        self.kline_data = []
