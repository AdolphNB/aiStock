"""
K-line chart widget using pyqtgraph
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
import pyqtgraph as pg
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional

class KLineChartWidget(QWidget):
    """K-line chart widget with volume bars and moving averages"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.kline_data = []
        self.stock_code = ""
        self.stock_name = ""
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Title label
        self.title_label = QLabel("K线预览")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
        layout.addWidget(self.title_label)
        
        # Create graphics layout widget
        self.graphics_layout = pg.GraphicsLayoutWidget()
        self.graphics_layout.setBackground('w')
        
        # K-line plot (main chart)
        self.kline_plot = self.graphics_layout.addPlot(row=0, col=0)
        self.kline_plot.showGrid(x=True, y=True, alpha=0.3)
        self.kline_plot.setLabel('left', '价格', units='元')
        
        # Volume plot
        self.volume_plot = self.graphics_layout.addPlot(row=1, col=0)
        self.volume_plot.showGrid(x=True, y=True, alpha=0.3)
        self.volume_plot.setLabel('left', '成交量', units='手')
        self.volume_plot.setLabel('bottom', '日期')
        
        # Link x-axis
        self.volume_plot.setXLink(self.kline_plot)
        
        layout.addWidget(self.graphics_layout)
        
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
        self.title_label.setText(f"{stock_name} ({stock_code}) - 最近{len(kline_data)}日K线")
        
        # Clear previous plots
        self.kline_plot.clear()
        self.volume_plot.clear()
        
        # Prepare data
        n = len(kline_data)
        x = np.arange(n)
        
        opens = np.array([d['open'] for d in kline_data])
        closes = np.array([d['close'] for d in kline_data])
        highs = np.array([d['high'] for d in kline_data])
        lows = np.array([d['low'] for d in kline_data])
        volumes = np.array([d['volume'] for d in kline_data])
        dates = [d['date'] for d in kline_data]
        
        # Draw K-line candles
        for i in range(n):
            open_price = opens[i]
            close_price = closes[i]
            high_price = highs[i]
            low_price = lows[i]
            
            # Determine color (red for up, green for down)
            is_up = close_price >= open_price
            color = (255, 0, 0, 200) if is_up else (0, 255, 0, 200)  # Red/Green
            
            # Draw high-low line
            line = pg.PlotDataItem([i, i], [low_price, high_price], 
                                  pen=pg.mkPen(color=color, width=1))
            self.kline_plot.addItem(line)
            
            # Draw open-close box
            box_height = abs(close_price - open_price)
            if box_height < 0.01:  # Avoid zero height
                box_height = 0.01
            
            box_y = min(open_price, close_price)
            box = pg.BarGraphItem(x=[i], height=[box_height], y0=[box_y], 
                                 width=0.6, brush=color, pen=color)
            self.kline_plot.addItem(box)
        
        # Calculate and draw moving averages
        ma5 = self.calculate_ma(closes, 5)
        ma10 = self.calculate_ma(closes, 10)
        ma20 = self.calculate_ma(closes, 20)
        ma60 = self.calculate_ma(closes, 60)
        
        # Plot MAs
        self.kline_plot.plot(x, ma5, pen=pg.mkPen(color=(255, 255, 0), width=1), name='MA5')
        self.kline_plot.plot(x, ma10, pen=pg.mkPen(color=(255, 0, 255), width=1), name='MA10')
        self.kline_plot.plot(x, ma20, pen=pg.mkPen(color=(0, 255, 255), width=1), name='MA20')
        self.kline_plot.plot(x, ma60, pen=pg.mkPen(color=(128, 128, 128), width=1), name='MA60')
        
        # Draw volume bars
        volume_colors = [(255, 0, 0, 150) if closes[i] >= opens[i] else (0, 255, 0, 150) 
                        for i in range(n)]
        
        for i in range(n):
            bar = pg.BarGraphItem(x=[i], height=[volumes[i]], width=0.6, 
                                 brush=volume_colors[i], pen=volume_colors[i])
            self.volume_plot.addItem(bar)
        
        # Set up x-axis labels (show dates at intervals)
        if n > 0:
            # Show labels at intervals
            interval = max(1, n // 10)
            ticks = []
            for i in range(0, n, interval):
                # Format date
                date_str = dates[i]
                if isinstance(date_str, str):
                    # Extract month-day if format is YYYY-MM-DD
                    try:
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        label = date_obj.strftime('%m-%d')
                    except:
                        label = date_str[-5:]  # Last 5 chars (MM-DD)
                else:
                    label = str(date_str)
                ticks.append((i, label))
            
            # Add last date
            if (n - 1) not in [t[0] for t in ticks]:
                date_str = dates[-1]
                if isinstance(date_str, str):
                    try:
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        label = date_obj.strftime('%m-%d')
                    except:
                        label = date_str[-5:]
                else:
                    label = str(date_str)
                ticks.append((n - 1, label))
            
            axis = self.volume_plot.getAxis('bottom')
            axis.setTicks([ticks])
        
        # Auto range
        self.kline_plot.enableAutoRange()
        self.volume_plot.enableAutoRange()
    
    def clear_chart(self):
        """Clear the chart"""
        self.kline_plot.clear()
        self.volume_plot.clear()
        self.title_label.setText("K线预览")
        self.stock_code = ""
        self.stock_name = ""
        self.kline_data = []
