"""
Test script for price cache and auto-update functionality
Using akshare stock_zh_a_spot_em API
"""
import sys
import time
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from services.stock_data_service import StockDataService

def test_price_cache():
    """Test price cache functionality"""
    print("=" * 60)
    print("Testing Price Cache and Auto-Update")
    print("Using akshare stock_zh_a_spot_em API (East Money)")
    print("=" * 60)
    
    # Initialize service
    service = StockDataService()
    
    # Test stocks (使用您配置文件中的自选股)
    test_codes = ["301308", "688609"]
    
    print("\n1. Testing get_cached_price (should be empty initially)")
    for code in test_codes:
        cached = service.get_cached_price(code)
        print(f"   {code}: {cached}")
    
    print("\n2. Fetching realtime price for first time")
    for code in test_codes:
        print(f"   Fetching {code}...")
        price_data = service.fetch_realtime_price(code)
        if price_data:
            print(f"   ✓ {code} ({price_data.get('name', 'N/A')}): "
                  f"{price_data['current']:.2f} ({price_data['percent']:+.2f}%)")
        else:
            print(f"   ✗ Failed to fetch {code}")
    
    print("\n3. Testing get_cached_price (should return cached data)")
    for code in test_codes:
        cached = service.get_cached_price(code)
        if cached:
            print(f"   ✓ {code} ({cached.get('name', 'N/A')}): "
                  f"{cached['current']:.2f} (from cache: {cached.get('from_cache', False)})")
        else:
            print(f"   ✗ No cache for {code}")
    
    print("\n4. Testing batch fetch (fetch_multiple_realtime_prices)")
    results = service.fetch_multiple_realtime_prices(test_codes)
    for code, data in results.items():
        print(f"   {code} ({data.get('name', 'N/A')}): "
              f"{data['current']:.2f} ({data['percent']:+.2f}%)")
    
    print("\n5. Starting auto-update (10 second interval)")
    service.start_auto_update(test_codes, interval=10)
    print("   Auto-update started. Monitoring for 25 seconds...")
    
    # Monitor for 25 seconds (should see ~2 updates)
    for i in range(5):
        time.sleep(5)
        print(f"\n   --- After {(i+1)*5} seconds ---")
        for code in test_codes:
            cached = service.get_cached_price(code)
            if cached:
                print(f"   {code}: {cached['current']:.2f} "
                      f"(cached at: {cached.get('cached_at', 'unknown')[-8:]})")
    
    print("\n6. Stopping auto-update")
    service.stop_auto_update()
    print("   Auto-update stopped")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_price_cache()
