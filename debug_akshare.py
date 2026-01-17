"""
Debug script to check akshare API response format
"""
import akshare as ak

def test_akshare_api():
    """Test akshare stock_individual_spot_xq API"""
    test_symbols = ["SH600000", "SZ000001", "SH301308", "SH688609"]
    
    print("=" * 70)
    print("Testing akshare stock_individual_spot_xq API")
    print("=" * 70)
    
    for symbol in test_symbols:
        print(f"\n{'='*70}")
        print(f"Testing: {symbol}")
        print(f"{'='*70}")
        
        try:
            result = ak.stock_individual_spot_xq(symbol=symbol)
            
            print(f"Result type: {type(result)}")
            print(f"\nResult content:")
            print(result)
            
            if isinstance(result, dict):
                print(f"\nAvailable keys: {list(result.keys())}")
                print(f"\nKey-Value pairs:")
                for key, value in result.items():
                    print(f"  {key}: {value} (type: {type(value).__name__})")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_akshare_api()
