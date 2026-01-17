import random
import pandas as pd
import os
from pathlib import Path
import requests
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class StockDataService:
    def __init__(self, server_url: str = None):
        # Load stocks from CSV
        self.stocks = self._load_stocks_from_csv()
        self.stock_cache = {}  # Cache for stock data with indicators
        
        # Load server URL from config if not provided
        if server_url is None:
            try:
                from utils.config_manager import ConfigManager
                config_manager = ConfigManager()
                server_url = config_manager.get_server_url()
            except:
                server_url = "http://localhost:8000"
        
        self.server_url = server_url
        logger.info(f"StockDataService initialized with server URL: {server_url}")

    def _load_stocks_from_csv(self):
        """Load stock list from all_stocks.csv"""
        try:
            # Get the path to all_stocks.csv
            current_dir = Path(__file__).parent.parent
            csv_path = current_dir / "market_data" / "all_stocks.csv"
            
            if not csv_path.exists():
                print(f"Warning: {csv_path} not found, using mock data")
                return self._generate_mock_stocks()
            
            df = pd.read_csv(csv_path)
            stocks = []
            
            for _, row in df.iterrows():
                # Generate mock technical indicators for now
                # In production, these would come from real data
                stocks.append({
                    "code": str(row['code']).zfill(6),
                    "name": row['name'],
                    "turnover": round(random.uniform(0.5, 15.0), 2),
                    "ma_bullish": random.choice([True, False]),
                    "price": round(random.uniform(5, 300), 2),
                    "change": round(random.uniform(-10, 10), 2),
                    "volume_ratio": round(random.uniform(0.3, 5.0), 2),
                    "kdj_k": round(random.uniform(0, 100), 2),
                    "kdj_d": round(random.uniform(0, 100), 2),
                    "kdj_j": round(random.uniform(-20, 120), 2),
                    "macd": round(random.uniform(-2, 2), 3),
                    "dif": round(random.uniform(-2, 2), 3),
                    "dea": round(random.uniform(-2, 2), 3),
                    "rsi": round(random.uniform(20, 80), 2),
                    "ma5": round(random.uniform(5, 300), 2),
                    "ma10": round(random.uniform(5, 300), 2),
                    "ma20": round(random.uniform(5, 300), 2),
                    "ma60": round(random.uniform(5, 300), 2),
                    "boll_upper": round(random.uniform(10, 350), 2),
                    "boll_mid": round(random.uniform(5, 300), 2),
                    "boll_lower": round(random.uniform(1, 250), 2),
                })
            
            print(f"Loaded {len(stocks)} stocks from CSV")
            return stocks
            
        except Exception as e:
            print(f"Error loading stocks from CSV: {e}")
            return self._generate_mock_stocks()

    def _generate_mock_stocks(self):
        """Generate a list of dummy stocks as fallback"""
        base_stocks = [
            ("600519", "贵州茅台", "消费"),
            ("300750", "宁德时代", "新能源"),
            ("000858", "五粮液", "消费"),
            ("601127", "赛力斯", "汽车"),
            ("002594", "比亚迪", "汽车"),
            ("688111", "金山办公", "软件"),
            ("300418", "昆仑万维", "AI"),
            ("002230", "科大讯飞", "AI"),
            ("601318", "中国平安", "金融"),
            ("600036", "招商银行", "金融"),
            ("000001", "平安银行", "金融"),
            ("603259", "药明康德", "医药"),
            ("300015", "爱尔眼科", "医药"),
            ("601888", "中国中免", "消费"),
            ("600900", "长江电力", "电力"),
            ("600009", "上海机场", "交通"),
            ("600030", "中信证券", "金融"),
            ("300059", "东方财富", "金融"),
            ("002475", "立讯精密", "电子"),
            ("603501", "韦尔股份", "半导体"),
        ]
        
        data = []
        for code, name, sector in base_stocks:
            data.append({
                "code": code,
                "name": name,
                "sector": sector,
                "turnover": round(random.uniform(0.5, 15.0), 2),
                "ma_bullish": random.choice([True, False]),
                "price": round(random.uniform(10, 2000), 2),
                "change": round(random.uniform(-5, 5), 2),
                "volume_ratio": round(random.uniform(0.3, 5.0), 2),
                "kdj_k": round(random.uniform(0, 100), 2),
                "kdj_d": round(random.uniform(0, 100), 2),
                "kdj_j": round(random.uniform(-20, 120), 2),
                "macd": round(random.uniform(-2, 2), 3),
                "dif": round(random.uniform(-2, 2), 3),
                "dea": round(random.uniform(-2, 2), 3),
                "rsi": round(random.uniform(20, 80), 2),
                "ma5": round(random.uniform(10, 2000), 2),
                "ma10": round(random.uniform(10, 2000), 2),
                "ma20": round(random.uniform(10, 2000), 2),
                "ma60": round(random.uniform(10, 2000), 2),
                "boll_upper": round(random.uniform(10, 2200), 2),
                "boll_mid": round(random.uniform(10, 2000), 2),
                "boll_lower": round(random.uniform(5, 1800), 2),
            })
        return data
    
    def get_all_stocks(self):
        """Get all stocks without filtering"""
        return self.stocks.copy()

    def filter_stocks(self, criteria):
        """
        Filter stocks based on multiple criteria
        
        Args:
            criteria: dict with filter conditions like:
                {
                    'min_turnover': float,
                    'max_turnover': float,
                    'ma_bullish': bool,
                    'min_change': float,
                    'max_change': float,
                    'min_volume_ratio': float,
                    'kdj_golden_cross': bool,
                    'kdj_death_cross': bool,
                    'kdj_low_area': bool,  # K < 20
                    'kdj_high_area': bool,  # K > 80
                    'macd_golden_cross': bool,
                    'macd_death_cross': bool,
                    'macd_above_zero': bool,
                    'rsi_oversold': bool,  # RSI < 30
                    'rsi_overbought': bool,  # RSI > 70
                    'price_above_ma20': bool,
                    'price_above_ma60': bool,
                    'boll_lower_break': bool,  # Price near lower band
                    'boll_upper_break': bool,  # Price near upper band
                }
        """
        results = []
        
        for stock in self.stocks:
            # Refresh mock data slightly for demo
            self._refresh_mock_indicators(stock)
            
            # Apply filters
            if not self._check_stock_criteria(stock, criteria):
                continue
                
            results.append(stock.copy())
        
        return results
    
    def _refresh_mock_indicators(self, stock):
        """Refresh mock technical indicators"""
        # Randomly update some values to simulate real-time data
        if random.random() > 0.7:
            stock["turnover"] = round(random.uniform(0.5, 15.0), 2)
            stock["change"] = round(random.uniform(-10, 10), 2)
            stock["volume_ratio"] = round(random.uniform(0.3, 5.0), 2)
    
    def _check_stock_criteria(self, stock, criteria):
        """Check if a stock meets all criteria"""
        # Turnover rate
        if 'min_turnover' in criteria:
            if stock["turnover"] < criteria['min_turnover']:
                return False
        
        if 'max_turnover' in criteria:
            if stock["turnover"] > criteria['max_turnover']:
                return False
        
        # MA bullish arrangement
        if criteria.get('ma_bullish', False):
            if not stock.get("ma_bullish", False):
                return False
        
        # Price change
        if 'min_change' in criteria:
            if stock["change"] < criteria['min_change']:
                return False
        
        if 'max_change' in criteria:
            if stock["change"] > criteria['max_change']:
                return False
        
        # Volume ratio
        if 'min_volume_ratio' in criteria:
            if stock.get("volume_ratio", 0) < criteria['min_volume_ratio']:
                return False
        
        # KDJ indicators
        if criteria.get('kdj_golden_cross', False):
            # K crosses above D
            if not (stock.get("kdj_k", 0) > stock.get("kdj_d", 0) and 
                    stock.get("kdj_k", 0) < 80):
                return False
        
        if criteria.get('kdj_death_cross', False):
            # K crosses below D
            if not (stock.get("kdj_k", 0) < stock.get("kdj_d", 0) and 
                    stock.get("kdj_k", 0) > 20):
                return False
        
        if criteria.get('kdj_low_area', False):
            if stock.get("kdj_k", 100) >= 20:
                return False
        
        if criteria.get('kdj_high_area', False):
            if stock.get("kdj_k", 0) <= 80:
                return False
        
        # MACD indicators
        if criteria.get('macd_golden_cross', False):
            if not (stock.get("dif", 0) > stock.get("dea", 0) and 
                    stock.get("macd", 0) > 0):
                return False
        
        if criteria.get('macd_death_cross', False):
            if not (stock.get("dif", 0) < stock.get("dea", 0)):
                return False
        
        if criteria.get('macd_above_zero', False):
            if stock.get("macd", -1) <= 0:
                return False
        
        # RSI indicators
        if criteria.get('rsi_oversold', False):
            if stock.get("rsi", 50) >= 30:
                return False
        
        if criteria.get('rsi_overbought', False):
            if stock.get("rsi", 50) <= 70:
                return False
        
        # Price vs MA
        if criteria.get('price_above_ma20', False):
            if stock.get("price", 0) <= stock.get("ma20", 0):
                return False
        
        if criteria.get('price_above_ma60', False):
            if stock.get("price", 0) <= stock.get("ma60", 0):
                return False
        
        # Bollinger Bands
        if criteria.get('boll_lower_break', False):
            # Price near or below lower band
            if stock.get("price", 0) > stock.get("boll_lower", 0) * 1.02:
                return False
        
        if criteria.get('boll_upper_break', False):
            # Price near or above upper band
            if stock.get("price", 0) < stock.get("boll_upper", 0) * 0.98:
                return False
        
        return True

    def get_stock_details(self, code):
        """Get details for a single stock."""
        for stock in self.stocks:
            if stock["code"] == code:
                return stock
        return None

    def fetch_realtime_stocks(self, stock_codes: List[str]) -> Dict[str, Dict]:
        """
        Fetch realtime stock data from server.
        
        Args:
            stock_codes: List of stock codes to fetch
            
        Returns:
            Dictionary with stock code as key and stock data as value
        """
        try:
            response = requests.post(
                f"{self.server_url}/api/v1/data/realtime-stocks",
                json={"stock_codes": stock_codes},
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get("data", {})
        except Exception as e:
            logger.error(f"Error fetching realtime stocks from server: {e}")
            return {}

    def update_watched_stocks(self, stock_codes: List[str]) -> bool:
        """
        Update the list of watched stocks on the server.
        
        Args:
            stock_codes: List of stock codes to watch
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.post(
                f"{self.server_url}/api/v1/data/watch-stocks",
                json={"stock_codes": stock_codes},
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"Updated watched stocks: {stock_codes}")
            return True
        except Exception as e:
            logger.error(f"Error updating watched stocks on server: {e}")
            return False

    def fetch_kline_data(self, stock_code: str, period: str = "daily", 
                        adjust: str = "qfq", days: int = 60) -> Optional[List[Dict]]:
        """
        Fetch K-line data for a stock from server.
        
        Args:
            stock_code: Stock code
            period: Period type ('daily', 'weekly', 'monthly')
            adjust: Adjustment type ('qfq', 'hfq', '')
            days: Number of days to fetch
            
        Returns:
            List of K-line data dictionaries or None if error
        """
        try:
            response = requests.get(
                f"{self.server_url}/api/v1/data/kline/{stock_code}",
                params={
                    "period": period,
                    "adjust": adjust,
                    "days": days
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result.get("data", [])
        except Exception as e:
            logger.error(f"Error fetching K-line data for {stock_code}: {e}")
            return None
