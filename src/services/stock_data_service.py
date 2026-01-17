import random
import pandas as pd
import os
from pathlib import Path
import requests
from typing import List, Dict, Optional
import logging
import threading
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class StockDataService:
    def __init__(self, server_url: str = None):
        # Load stocks from CSV
        self.stocks = self._load_stocks_from_csv()
        self.stock_cache = {}  # Cache for stock data with indicators
        
        # Price cache: {stock_code: {price_data, timestamp}}
        self.price_cache = {}
        self.price_cache_lock = threading.Lock()
        
        # Auto-update control
        self.auto_update_running = False
        self.auto_update_thread = None
        self.watched_stocks = []  # List of stock codes to monitor
        
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

    def get_cached_price(self, stock_code: str) -> Optional[Dict]:
        """
        Get cached price data for a stock. Returns immediately.
        
        Args:
            stock_code: Stock code
            
        Returns:
            Cached price data or None if not cached
        """
        with self.price_cache_lock:
            if stock_code in self.price_cache:
                cache_entry = self.price_cache[stock_code]
                return {
                    **cache_entry['data'],
                    'cached_at': cache_entry['timestamp'],
                    'from_cache': True
                }
        return None

    def fetch_realtime_price(self, stock_code: str) -> Optional[Dict]:
        """
        Fetch realtime price for a single stock using akshare bid-ask API.
        Updates cache after fetching.
        
        Args:
            stock_code: Stock code (e.g., "600000" or "000001")
            
        Returns:
            Price data dictionary or None if error
        """
        try:
            import akshare as ak
            
            # Ensure stock code is 6 digits without prefix
            if len(stock_code) > 6:
                stock_code = stock_code[-6:]  # Remove SH/SZ prefix if present
            
            # Use stock_bid_ask_em for single stock (much faster)
            df = ak.stock_bid_ask_em(symbol=stock_code)
            
            if df is None or df.empty:
                logger.warning(f"Stock {stock_code} not found")
                # Return cached data if available
                with self.price_cache_lock:
                    if stock_code in self.price_cache:
                        cache_entry = self.price_cache[stock_code]
                        logger.info(f"Returning stale cache for {stock_code}")
                        return {
                            **cache_entry['data'],
                            'from_cache': True,
                            'stale': True
                        }
                return None
            
            # Extract data from the DataFrame
            # stock_bid_ask_em returns columns like: item, value
            data_dict = {}
            for _, row in df.iterrows():
                item = row.get('item', '')
                value = row.get('value', '')
                data_dict[item] = value
            
            # Safe conversion functions
            def safe_float(value, default=0.0):
                try:
                    if isinstance(value, str):
                        value = value.replace(',', '').replace('%', '')
                    return float(value) if value and str(value) != '-' else default
                except (ValueError, TypeError):
                    return default
            
            # Map fields to our format
            current_price = safe_float(data_dict.get('最新', data_dict.get('现价', 0)))
            last_close = safe_float(data_dict.get('昨收', 0))
            
            # Calculate change and percent if not provided
            if last_close > 0:
                chg = current_price - last_close
                percent = (chg / last_close) * 100
            else:
                chg = 0
                percent = 0
            
            price_data = {
                'code': stock_code,
                'name': str(data_dict.get('名称', stock_code)),
                'current': current_price,
                'percent': percent,
                'chg': chg,
                'volume': safe_float(data_dict.get('成交量', 0)),
                'amount': safe_float(data_dict.get('成交额', 0)),
                'turnover_rate': safe_float(data_dict.get('换手率', 0)),
                'open': safe_float(data_dict.get('今开', 0)),
                'high': safe_float(data_dict.get('最高', 0)),
                'low': safe_float(data_dict.get('最低', 0)),
                'last_close': last_close,
                'timestamp': datetime.now().isoformat(),
                'from_cache': False
            }
            
            # Update cache
            with self.price_cache_lock:
                self.price_cache[stock_code] = {
                    'data': price_data,
                    'timestamp': datetime.now().isoformat()
                }
            
            logger.info(f"Updated price for {stock_code}: {price_data['current']}")
            return price_data
                
        except Exception as e:
            logger.error(f"Error fetching realtime price for {stock_code}: {e}")
            # Return cached data if available even on error
            with self.price_cache_lock:
                if stock_code in self.price_cache:
                    cache_entry = self.price_cache[stock_code]
                    logger.info(f"Returning stale cache for {stock_code} due to fetch error")
                    return {
                        **cache_entry['data'],
                        'from_cache': True,
                        'stale': True
                    }
            return None

    def fetch_multiple_realtime_prices(self, stock_codes: List[str]) -> Dict[str, Dict]:
        """
        Fetch realtime prices for multiple stocks.
        Uses individual API calls for each stock.
        
        Args:
            stock_codes: List of stock codes
            
        Returns:
            Dictionary with stock code as key and price data as value
        """
        results = {}
        
        # Normalize stock codes
        normalized_codes = []
        for code in stock_codes:
            if len(code) > 6:
                normalized_codes.append(code[-6:])
            else:
                normalized_codes.append(code)
        
        # Fetch each stock individually
        for code in normalized_codes:
            try:
                price_data = self.fetch_realtime_price(code)
                if price_data:
                    results[code] = price_data
            except Exception as e:
                logger.error(f"Error fetching price for {code}: {e}")
                # Try to use cache
                with self.price_cache_lock:
                    if code in self.price_cache:
                        results[code] = {
                            **self.price_cache[code]['data'],
                            'from_cache': True,
                            'stale': True
                        }
        
        logger.info(f"Updated prices for {len(results)}/{len(normalized_codes)} stocks")
        return results

    def start_auto_update(self, stock_codes: List[str], interval: int = 10):
        """
        Start automatic price updates in background thread.
        
        Args:
            stock_codes: List of stock codes to monitor
            interval: Update interval in seconds (default: 10)
        """
        if self.auto_update_running:
            logger.warning("Auto-update already running")
            return
        
        self.watched_stocks = stock_codes.copy()
        self.auto_update_running = True
        
        def update_loop():
            logger.info(f"Starting auto-update loop for {len(self.watched_stocks)} stocks")
            while self.auto_update_running:
                try:
                    # Use batch update for efficiency
                    if self.watched_stocks:
                        self.fetch_multiple_realtime_prices(self.watched_stocks)
                    
                    # Sleep for interval seconds
                    for _ in range(interval):
                        if not self.auto_update_running:
                            break
                        time.sleep(1)
                        
                except Exception as e:
                    logger.error(f"Error in auto-update loop: {e}")
                    time.sleep(interval)
        
        self.auto_update_thread = threading.Thread(target=update_loop, daemon=True)
        self.auto_update_thread.start()
        logger.info(f"Auto-update started with {interval}s interval")

    def stop_auto_update(self):
        """Stop automatic price updates."""
        if self.auto_update_running:
            logger.info("Stopping auto-update")
            self.auto_update_running = False
            if self.auto_update_thread:
                self.auto_update_thread.join(timeout=5)
            logger.info("Auto-update stopped")

    def update_watched_stocks_list(self, stock_codes: List[str]):
        """
        Update the list of watched stocks for auto-update.
        
        Args:
            stock_codes: New list of stock codes to monitor
        """
        with self.price_cache_lock:
            self.watched_stocks = stock_codes.copy()
        logger.info(f"Updated watched stocks list: {stock_codes}")

    def get_price_with_cache(self, stock_code: str, force_refresh: bool = False) -> Dict:
        """
        Get price data with cache-first strategy.
        Returns cached data immediately, then fetches new data in background if needed.
        
        Args:
            stock_code: Stock code
            force_refresh: Force fetch new data regardless of cache
            
        Returns:
            Price data (from cache or fresh)
        """
        # Return cached data immediately if available and not forcing refresh
        if not force_refresh:
            cached = self.get_cached_price(stock_code)
            if cached:
                # Start background refresh if cache is old (>10 seconds)
                cache_time = datetime.fromisoformat(cached['cached_at'])
                age = (datetime.now() - cache_time).total_seconds()
                if age > 10:
                    # Trigger background update
                    threading.Thread(
                        target=self.fetch_realtime_price,
                        args=(stock_code,),
                        daemon=True
                    ).start()
                return cached
        
        # No cache or force refresh - fetch now
        return self.fetch_realtime_price(stock_code) or {
            'code': stock_code,
            'current': 0,
            'error': 'Failed to fetch price'
        }
