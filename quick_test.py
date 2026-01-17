"""
Quick test to verify akshare stock_bid_ask_em API works
"""
import sys
from pathlib import Path

src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from services.stock_data_service import StockDataService

def quick_test():
    print("Quick test of new API...")
    service = StockDataService()
    
    # Test with your favorite stocks
    test_codes = ["301308", "688609"]
    
    for code in test_codes:
        print(f"\nTesting {code}...")
        price = service.fetch_realtime_price(code)
        if price:
            print(f"[OK] Success!")
            print(f"  Name: {price.get('name')}")
            print(f"  Price: {price.get('current'):.2f}")
            print(f"  Change: {price.get('percent'):+.2f}%")
        else:
            print(f"[FAIL] Failed")

if __name__ == "__main__":
    quick_test()
