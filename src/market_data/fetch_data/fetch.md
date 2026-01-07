我在服务器中搭建了一个 server，定时会去获取一些股票异动和资金流动信息。
然后，在 pc 机上开发了一款软件，想去订阅这些信息。订阅成功后，PC 机 client 请求一次便会返回一次信息。
现在我遇到了订阅支付问题，我想使用微信支付，我应该怎么去实现这个功能.

创新高 
接口：stock_rank_cxg_ths

目标地址：https://data.10jqka.com.cn/rank/cxg/

描述：同花顺-数据中心-技术选股-创新高

限量：单次指定 symbol 的所有数据

输入参数

名称 类型 描述
symbol str symbol="创月新高"; choice of {"创月新高", "半年新高", "一年新高", "历史新高"}
输出参数

名称 类型 描述
序号 int64 -
股票代码 object -
股票简称 object -
涨跌幅 float64 注意单位: %
换手率 float64 注意单位: %
最新价 float64 注意单位: 元
前期高点 float64 -
前期高点日期 object -
接口示例：

import akshare as ak

stock_rank_cxg_ths_df = ak.stock_rank_cxg_ths(symbol="创月新高")
print(stock_rank_cxg_ths_df)

创新低
接口：stock_rank_cxd_ths

目标地址：https://data.10jqka.com.cn/rank/cxd/

描述：同花顺-数据中心-技术选股-创新低

限量：单次指定 symbol 的所有数据

输入参数

名称 类型 描述
symbol str symbol="创月新低"; choice of {"创月新低", "半年新低", "一年新低", "历史新低"}
输出参数

名称 类型 描述
序号 int64 -
股票代码 object -
股票简称 object -
涨跌幅 float64 注意单位: %
换手率 float64 注意单位: %
最新价 float64 注意单位: 元
前期低点 float64 -
前期低点日期 object -
接口示例：

import akshare as ak

stock_rank_cxd_ths_df = ak.stock_rank_cxd_ths(symbol="创月新低")
print(stock_rank_cxd_ths_df)

连续上涨 
接口：stock_rank_lxsz_ths

目标地址：https://data.10jqka.com.cn/rank/lxsz/

描述：同花顺-数据中心-技术选股-连续上涨

限量：单次返回所有数据

输入参数

名称 类型 描述

- - - 输出参数

名称 类型 描述
序号 int64 -
股票代码 object -
股票简称 object -
收盘价 float64 注意单位: 元
最高价 float64 注意单位: 元
最低价 float64 注意单位: 元
连涨天数 int64 -
连续涨跌幅 float64 注意单位: %
累计换手率 float64 注意单位: %
所属行业 object -
接口示例

import akshare as ak

stock_rank_lxsz_ths_df = ak.stock_rank_lxsz_ths()
print(stock_rank_lxsz_ths_df)

连续下跌 
接口：stock_rank_lxxd_ths

目标地址：https://data.10jqka.com.cn/rank/lxxd/

描述：同花顺-数据中心-技术选股-连续下跌

限量：单次返回所有数据

输入参数

名称 类型 描述

- - - 输出参数

名称 类型 描述
序号 int64 -
股票代码 object -
股票简称 object -
收盘价 float64 注意单位: 元
最高价 float64 注意单位: 元
最低价 float64 注意单位: 元
连涨天数 int64 -
连续涨跌幅 float64 注意单位: %
累计换手率 float64 注意单位: %
所属行业 object -
接口示例：

import akshare as ak

stock_rank_lxxd_ths_df = ak.stock_rank_lxxd_ths()
print(stock_rank_lxxd_ths_df)

持续放量 
接口: stock_rank_cxfl_ths

目标地址: https://data.10jqka.com.cn/rank/cxfl/

描述: 同花顺-数据中心-技术选股-持续放量

限量: 单次返回所有数据

输入参数

名称 类型 描述

- - - 输出参数

名称 类型 描述
序号 int64 -
股票代码 object -
股票简称 object -
涨跌幅 float64 注意单位: %
最新价 float64 注意单位: 元
成交量 object 注意单位: 股
基准日成交量 object 注意单位: 股
放量天数 int64 -
阶段涨跌幅 float64 注意单位: %
所属行业 object -
接口示例

import akshare as ak

stock_rank_cxfl_ths_df = ak.stock_rank_cxfl_ths()
print(stock_rank_cxfl_ths_df)

持续缩量
接口: stock_rank_cxsl_ths

目标地址: https://data.10jqka.com.cn/rank/cxsl/

描述: 同花顺-数据中心-技术选股-持续缩量

限量: 单次返回所有数据

输入参数

名称 类型 描述

- - - 输出参数

名称 类型 描述
序号 int64 -
股票代码 object -
股票简称 object -
涨跌幅 float64 注意单位: %
最新价 float64 注意单位: 元
成交量 object 注意单位: 股
基准日成交量 object 注意单位: 股
缩量天数 int64 -
阶段涨跌幅 float64 注意单位: %
所属行业 object -
接口示例

import akshare as ak

stock_rank_cxsl_ths_df = ak.stock_rank_cxsl_ths()
print(stock_rank_cxsl_ths_df)

向上突破 
接口: stock_rank_xstp_ths

目标地址: https://data.10jqka.com.cn/rank/xstp/

描述: 同花顺-数据中心-技术选股-向上突破

限量: 单次返回所有数据

输入参数

名称 类型 描述
symbol str symbol="500 日均线"; choice of {"5 日均线", "10 日均线", "20 日均线", "30 日均线", "60 日均线", "90 日均线", "250 日均线", "500 日均线"}
输出参数

名称 类型 描述
序号 int64 -
股票代码 object -
股票简称 object -
最新价 float64 注意单位: 元
成交额 object 注意单位: 元
成交量 object 注意单位: 股
涨跌幅 float64 注意单位: %
换手率 float64 注意单位: %
接口示例

import akshare as ak

stock_rank_xstp_ths_df = ak.stock_rank_xstp_ths(symbol="500 日均线")
print(stock_rank_xstp_ths_df)

向下突破 
接口: stock_rank_xxtp_ths

目标地址: https://data.10jqka.com.cn/rank/xxtp/

描述: 同花顺-数据中心-技术选股-向下突破

限量: 单次返回所有数据

输入参数

名称 类型 描述
symbol str symbol="500 日均线"; choice of {"5 日均线", "10 日均线", "20 日均线", "30 日均线", "60 日均线", "90 日均线", "250 日均线", "500 日均线"}
输出参数

名称 类型 描述
序号 int64 -
股票代码 object -
股票简称 object -
最新价 float64 注意单位: 元
成交额 object 注意单位: 元
成交量 object 注意单位: 股
涨跌幅 float64 注意单位: %
换手率 float64 注意单位: %
接口示例

import akshare as ak

stock_rank_xxtp_ths_df = ak.stock_rank_xxtp_ths(symbol="500 日均线")
print(stock_rank_xxtp_ths_df)

量价齐升 
接口: stock_rank_ljqs_ths

目标地址: https://data.10jqka.com.cn/rank/ljqs/

描述: 同花顺-数据中心-技术选股-量价齐升

限量: 单次返回所有数据

输入参数

名称 类型 描述

- - - 输出参数

名称 类型 描述
序号 int64 -
股票代码 object -
股票简称 object -
最新价 float64 注意单位: 元
量价齐升天数 int64 -
阶段涨幅 float64 注意单位: %
累计换手率 float64 注意单位: %
所属行业 object -
接口示例

import akshare as ak

stock_rank_ljqs_ths_df = ak.stock_rank_ljqs_ths()
print(stock_rank_ljqs_ths_df)

量价齐跌 
接口: stock_rank_ljqd_ths

目标地址: https://data.10jqka.com.cn/rank/ljqd/

描述: 同花顺-数据中心-技术选股-量价齐跌

限量: 单次返回所有数据

输入参数

名称 类型 描述

- - - 输出参数

名称 类型 描述
序号 int64 -
股票代码 object -
股票简称 object -
最新价 float64 注意单位: 元
量价齐跌天数 int64 -
阶段涨幅 float64 注意单位: %
累计换手率 float64 注意单位: %
所属行业 object -
接口示例

import akshare as ak

stock_rank_ljqd_ths_df = ak.stock_rank_ljqd_ths()
print(stock_rank_ljqd_ths_df)

险资举牌 
接口: stock_rank_xzjp_ths

目标地址: https://data.10jqka.com.cn/financial/xzjp/

描述: 同花顺-数据中心-技术选股-险资举牌

限量: 单次返回所有数据

输入参数

名称 类型 描述

- - - 输出参数

名称 类型 描述
序号 int64 -
举牌公告日 object -
股票代码 object -
股票简称 object -
现价 float64 注意单位: 元
涨跌幅 float64 注意单位: %
举牌方 object -
增持数量 object 注意单位: 股
交易均价 float64 注意单位: 元
增持数量占总股本比例 float64 注意单位: %
变动后持股总数 object 注意单位: 股
变动后持股比例 float64 注意单位: %
接口示例

import akshare as ak

stock_rank_xzjp_ths_df = ak.stock_rank_xzjp_ths()
print(stock_rank_xzjp_ths_df)

赚钱效应分析 
接口: stock_market_activity_legu

目标地址: https://www.legulegu.com/stockdata/market-activity

描述: 乐咕乐股网-赚钱效应分析数据

限量: 单次返回当前赚钱效应分析数据

说明：

涨跌比：即沪深两市上涨个股所占比例，体现的是市场整体涨跌，占比越大则代表大部分个股表现活跃。

涨停板数与跌停板数的意义：涨停家数在一定程度上反映了市场的投机氛围。当涨停家数越多，则市场的多头氛围越强。真实涨停是非一字无量涨停。真实跌停是非一字无量跌停。

输入参数

名称 类型 描述

- - - 输出参数

名称 类型 描述
item object -
value object -
接口示例

import akshare as ak

stock_market_activity_legu_df = ak.stock_market_activity_legu()
print(stock_market_activity_legu_df)
数据示例

        item                value

0 上涨 4770.0
1 涨停 119.0
2 真实涨停 101.0
3 st st*涨停 10.0
4 下跌 281.0
5 跌停 6.0
6 真实跌停 4.0
7 st st*跌停 4.0
8 平盘 39.0
9 停牌 10.0
10 活跃度 93.53%
11 统计日期 2024-10-14 15:00:00
