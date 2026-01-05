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
        sh_df = ak.stock_info_sh_name_code()
        # 统一列名，假设返回的是 '证券代码', '证券简称' 或类似的，需要标准化
        # 通常 stock_info_sh_name_code 返回: 证券代码, 证券简称, 公司全称, 上市日期
        if '证券代码' in sh_df.columns:
            sh_df = sh_df.rename(columns={'证券代码': 'code', '证券简称': 'name'})
        elif '代码' in sh_df.columns:
            sh_df = sh_df.rename(columns={'代码': 'code', '名称': 'name'})
            
        dfs.append(sh_df[['code', 'name']])
        print(f"沪A获取成功: {len(sh_df)} 条")
    except Exception as e:
        print(f"获取沪A失败: {e}")

    # 2. 深A
    try:
        print("正在获取深圳证券交易所股票代码...")
        sz_df = ak.stock_info_sz_name_code()
        # stock_info_sz_name_code 返回: A股代码, A股简称, A股上市日期, ...
        # 注意列名可能不同
        if 'A股代码' in sz_df.columns:
            sz_df = sz_df.rename(columns={'A股代码': 'code', 'A股简称': 'name'})
        elif '代码' in sz_df.columns:
            sz_df = sz_df.rename(columns={'代码': 'code', '名称': 'name'})
            
        dfs.append(sz_df[['code', 'name']])
        print(f"深A获取成功: {len(sz_df)} 条")
    except Exception as e:
        print(f"获取深A失败: {e}")

    # 3. 北交所
    try:
        print("正在获取北京证券交易所股票代码...")
        bj_df = ak.stock_info_bj_name_code()
        # 假设列名
        if '证券代码' in bj_df.columns:
            bj_df = bj_df.rename(columns={'证券代码': 'code', '证券简称': 'name'})
        elif '代码' in bj_df.columns:
            bj_df = bj_df.rename(columns={'代码': 'code', '名称': 'name'})
            
        dfs.append(bj_df[['code', 'name']])
        print(f"北交所获取成功: {len(bj_df)} 条")
    except Exception as e:
        print(f"获取北交所失败 (可能是网络或接口问题): {e}")

    if not dfs:
        print("未获取到任何股票数据。")
        return

    # 合并
    all_stocks = pd.concat(dfs, ignore_index=True)
    
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
