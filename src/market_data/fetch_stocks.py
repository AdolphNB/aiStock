import akshare as ak
import os
import pandas as pd

def fetch_and_save_stock_codes():
    """
    获取 A 股所有股票代码并保存为 CSV 文件
    分市场获取（沪、深、京），以提高稳定性
    """
    print("正在获取 A 股股票代码，请稍候...")
    
    dfs = []
    
    # 1. 沪A
    try:
        print("正在获取上海证券交易所股票代码...")
        all_stocks = ak.stock_info_a_code_name()
        print(f"获取成功！")
    except Exception as e:
        print(f"获取失败: {e}")

    # 去重（以防万一）
    all_stocks.drop_duplicates(subset=['code'], inplace=True)

    # 确保保存目录存在
    save_dir = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    file_path = os.path.join(save_dir, "all_stocks.csv")
    
    # 保存为 CSV
    all_stocks.to_csv(file_path, index=False, encoding='utf-8-sig')
    
    print(f"成功！股票代码已保存至: {file_path}")
    print(f"共获取到 {len(all_stocks)} 只股票。")
    print("前5行数据预览：")
    print(all_stocks.head())





if __name__ == "__main__":
    fetch_and_save_stock_codes()
