import random

class StockDataService:
    def __init__(self):
        # Mock database of stocks
        self.stocks = self._generate_mock_stocks()

    def _generate_mock_stocks(self):
        """Generate a list of dummy stocks."""
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
                "turnover": round(random.uniform(0.5, 15.0), 2), # %
                "ma_bullish": random.choice([True, False]),
                "price": round(random.uniform(10, 2000), 2),
                "change": round(random.uniform(-5, 5), 2)
            })
        return data

    def filter_stocks(self, min_turnover=None, max_turnover=None, require_ma_bullish=False):
        """Filter stocks based on criteria."""
        results = []
        for stock in self.stocks:
            # Refresh mock data slightly for liveliness
            stock["turnover"] = round(random.uniform(0.5, 15.0), 2)
            if random.random() > 0.8: # Randomly flip status
                 stock["ma_bullish"] = not stock["ma_bullish"]

            # Filter Logic
            if min_turnover is not None and stock["turnover"] < min_turnover:
                continue
            if max_turnover is not None and stock["turnover"] > max_turnover:
                continue
            if require_ma_bullish and not stock["ma_bullish"]:
                continue
                
            results.append(stock)
        
        return results

    def get_stock_details(self, code):
        """Get details for a single stock."""
        for stock in self.stocks:
            if stock["code"] == code:
                return stock
        return None
