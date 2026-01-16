"""
Test script for stock search functionality with pypinyin
测试股票搜索功能（包括拼音搜索）
"""

try:
    from pypinyin import lazy_pinyin
    print("✓ pypinyin imported successfully")
except ImportError:
    print("✗ pypinyin not installed. Please run: uv pip install pypinyin")
    exit(1)

# Test data
test_stocks = [
    {"code": "601985", "name": "中国核电"},
    {"code": "601398", "name": "工商银行"},
    {"code": "000858", "name": "五粮液"},
    {"code": "601127", "name": "赛力斯"},
    {"code": "600519", "name": "贵州茅台"},
]

# Add pinyin data
for stock in test_stocks:
    pinyin_list = lazy_pinyin(stock['name'])
    stock['pinyin_full'] = ''.join(pinyin_list)
    stock['pinyin_initials'] = ''.join([p[0] for p in pinyin_list])
    print(f"{stock['code']} {stock['name']:<8} | 完整拼音: {stock['pinyin_full']:<20} | 首字母: {stock['pinyin_initials']}")

print("\n" + "="*80)
print("Search Tests:")
print("="*80)

def search_stocks(query):
    """Test search function"""
    query = query.lower()
    results = []
    
    for stock in test_stocks:
        code = stock['code']
        name = stock['name']
        
        # Code match
        if code.startswith(query):
            results.append((stock, "代码匹配"))
            continue
        
        # Name contains
        if query in name.lower():
            results.append((stock, "名称包含"))
            continue
        
        # Pinyin initials
        if query in stock['pinyin_initials']:
            results.append((stock, "拼音首字母"))
            continue
        
        # Full pinyin
        if query in stock['pinyin_full']:
            results.append((stock, "完整拼音"))
    
    return results

# Test cases
test_queries = [
    "zghd",      # 中国核电 (首字母)
    "核电",      # 中国核电 (名称)
    "601985",    # 中国核电 (代码)
    "yh",        # 银行 (首字母)
    "yinhang",   # 银行 (完整拼音)
    "slc",       # 赛力斯 (首字母)
    "maotai",    # 茅台 (完整拼音)
    "wly",       # 五粮液 (首字母)
]

for query in test_queries:
    results = search_stocks(query)
    print(f"\n查询: '{query}'")
    if results:
        for stock, match_type in results:
            print(f"  ✓ {stock['code']} {stock['name']} ({match_type})")
    else:
        print(f"  ✗ 未找到结果")

print("\n" + "="*80)
print("All tests completed!")
print("="*80)
