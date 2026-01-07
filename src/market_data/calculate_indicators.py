
import pandas as pd
import numpy as np

def calculate_ma(df, window_sizes=[5, 10, 20, 60]):
    """
    计算移动平均线 (Moving Average)
    :param df: 由于必须包含 '收盘' 列的 DataFrame
    :param window_sizes: 均线周期列表，默认 [5, 10, 20, 60]
    :return: 包含新增 MA 列的 DataFrame
    """
    if '收盘' not in df.columns:
         raise ValueError("DataFrame必须包含 '收盘' 列")

    for window in window_sizes:
        df[f'MA{window}'] = df['收盘'].rolling(window=window).mean()
    
    return df

def calculate_kdj(df, n=9, m1=3, m2=3):
    """
    计算 KDJ 指标
    :param df: 必须包含 '最高', '最低', '收盘' 列
    :param n: RSV 周期
    :param m1: K 值平滑周期
    :param m2: D 值平滑周期
    :return: 包含 K, D, J 列的 DataFrame
    """
    required_cols = ['最高', '最低', '收盘']
    if not all(col in df.columns for col in required_cols):
        raise ValueError(f"DataFrame必须包含 {required_cols}")

    # 计算 RSV
    low_list = df['最低'].rolling(window=n, min_periods=n).min()
    high_list = df['最高'].rolling(window=n, min_periods=n).max()
    rsv = (df['收盘'] - low_list) / (high_list - low_list) * 100
    
    # 填充 NaN 为 50 (或者前值，视具体需求) - 这里简单处理 fillna(0) 或者不处理
    # 为了计算的连贯性，通常使用 ewm 递归
    
    # 计算 K, D, J
    # pandas 的 ewm 不需要手动递归，直接设置 alpha 或 com
    # K = 2/3 * K_prev + 1/3 * RSV  => alpha=1/3 => com=2
    
    df['K'] = rsv.ewm(com=m1-1, adjust=False).mean()
    df['D'] = df['K'].ewm(com=m2-1, adjust=False).mean()
    df['J'] = 3 * df['K'] - 2 * df['D']
    
    return df

def calculate_macd(df, fast=12, slow=26, signal=9):
    """
    计算 MACD 指标
    :param df: 必须包含 '收盘' 列
    :return: 包含 DIF, DEA, MACD 列的 DataFrame
    """
    if '收盘' not in df.columns:
        raise ValueError("DataFrame必须包含 '收盘' 列")
        
    ema_fast = df['收盘'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['收盘'].ewm(span=slow, adjust=False).mean()
    
    df['DIF'] = ema_fast - ema_slow
    df['DEA'] = df['DIF'].ewm(span=signal, adjust=False).mean()
    df['MACD'] = (df['DIF'] - df['DEA']) * 2
    
    return df

def calculate_rsi(df, window=14):
    """
    计算 RSI 指标
    :param df: 必须包含 '收盘' 列
    :return: 包含 RSI 列的 DataFrame
    """
    if '收盘' not in df.columns:
        raise ValueError("DataFrame必须包含 '收盘' 列")

    delta = df['收盘'].diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    
    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()
    
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    return df

def calculate_boll(df, window=20, num_std=2):
    """
    计算布林线 (BOLL)
    :param df: 必须包含 '收盘' 列
    :return: 包含 BOLL_UPPER, BOLL_MID, BOLL_LOWER 列的 DataFrame
    """
    if '收盘' not in df.columns:
         raise ValueError("DataFrame必须包含 '收盘' 列")

    df['BOLL_MID'] = df['收盘'].rolling(window=window).mean()
    std = df['收盘'].rolling(window=window).std()
    
    df['BOLL_UPPER'] = df['BOLL_MID'] + (std * num_std)
    df['BOLL_LOWER'] = df['BOLL_MID'] - (std * num_std)
    
    return df

def calculate_short_term_signals(df):
    """
    一键计算所有常用短线指标
    """
    df = calculate_ma(df)
    df = calculate_kdj(df)
    df = calculate_macd(df)
    df = calculate_rsi(df)
    df = calculate_boll(df)
    return df

if __name__ == "__main__":
    # 创建模拟数据进行测试
    data = {
        '日期': pd.date_range(start='2023-01-01', periods=100),
        '收盘': np.random.normal(10, 1, 100).cumsum() + 100,
        '最高': np.random.normal(10, 1, 100).cumsum() + 102,
        '最低': np.random.normal(10, 1, 100).cumsum() + 98,
        '成交量': np.random.randint(1000, 5000, 100)
    }
    df_test = pd.DataFrame(data)
    
    # 确保 high >= close/open/low (简单修正模拟数据逻辑错误)
    df_test['最高'] = df_test[['收盘', '最高']].max(axis=1)
    df_test['最低'] = df_test[['收盘', '最低']].min(axis=1)

    print("开始计算指标...")
    try:
        df_result = calculate_short_term_signals(df_test)
        print("计算成功！")
        print("\n数据预览 (最后5行):")
        # 打印关键列
        cols_to_show = ['日期', '收盘', 'MA5', 'K', 'D', 'J', 'MACD', 'RSI', 'BOLL_UPPER']
        print(df_result[cols_to_show].tail())
        
    except Exception as e:
        print(f"计算出错: {e}")
