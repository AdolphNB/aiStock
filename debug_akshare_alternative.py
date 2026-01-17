"""
Test alternative akshare APIs for real-time stock data
"""
import akshare as ak
import pandas as pd

def test_spot_em():
    """Test ak.stock_zh_a_spot_em() - East Money real-time data"""
    print("=" * 70)
    print("Testing: ak.stock_zh_a_spot_em()")
    print("=" * 70)
    
    try:
        # This returns all A-share stocks real-time data
        df = ak.stock_zh_a_spot_em()
        print(f"✓ Success! Got {len(df)} stocks")
        print(f"\nColumns: {list(df.columns)}")
        print(f"\nSample data (first 3 rows):")
        print(df.head(3))
        
        # Try to find specific stocks
        test_codes = ['600000', '000001', '301308', '688609']
        print(f"\n{'='*70}")
        print("Searching for specific stocks:")
        for code in test_codes:
            stock_data = df[df['代码'] == code]
            if not stock_data.empty:
                row = stock_data.iloc[0]
                print(f"\n✓ Found {code}:")
                print(f"  名称: {row['名称']}")
                print(f"  最新价: {row['最新价']}")
                print(f"  涨跌幅: {row['涨跌幅']}%")
                print(f"  涨跌额: {row['涨跌额']}")
            else:
                print(f"\n✗ Not found: {code}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_stock_bid_ask():
    """Test ak.stock_bid_ask_em() - Bid/Ask data"""
    print("\n" + "=" * 70)
    print("Testing: ak.stock_bid_ask_em()")
    print("=" * 70)
    
    test_codes = ['600000', '000001']
    
    for code in test_codes:
        try:
            df = ak.stock_bid_ask_em(symbol=code)
            print(f"\n✓ Success for {code}!")
            print(df)
        except Exception as e:
            print(f"\n✗ Error for {code}: {e}")

if __name__ == "__main__":
    # Test the most reliable API first
    success = test_spot_em()
    
    if success:
        print("\n" + "=" * 70)
        print("✓ Found working API: ak.stock_zh_a_spot_em()")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("Trying alternative API...")
        print("=" * 70)
        test_stock_bid_ask()
