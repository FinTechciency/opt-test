import tushare as ts
import pandas as pd
import backtrader as bt

# 获取贵州茅台的日 K 线数据
def get_stock_data():
    ts.set_token('294b16d453c18ec44877c0753586866779d1956f463b49a6e3c5b6d8')  # 替换为你的 Tushare API Token
    pro = ts.pro_api()
    # 获取贵州茅台（600519.SH）的日线数据
    df = pro.daily(ts_code='600519.SH', start_date='20000101')
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df = df.sort_values('trade_date')  # 按日期升序排列
    return df

class Test(bt.Strategy):

    params = dict(
        pfast=10,  # period for the fast moving average
        pslow=30   # period for the slow moving average
    )

    def __init__(self):
        sma1 = bt.ind.SMA(period=self.p.pfast)  # fast moving average
        sma2 = bt.ind.SMA(period=self.p.pslow)  # slow moving average
        self.crossover = bt.ind.CrossOver(sma1, sma2)  # crossover signal

    def next(self):
        if not self.position:  # not in the market
            if self.crossover > 0:  # if fast crosses slow to the upside
                self.buy()  # enter long

        elif self.crossover < 0:  # in the market & cross to the downside
            self.close()  # close long position

    def stop(self):
        print('pfast: %2d pslow %2d 最终收益： %.2f' %
                 (self.p.pfast, self.p.pslow, self.broker.getvalue()))
        
def get_result(strategies):
    result = {
        "pfast": -1,
        "pslow": -1,
        "max_value": 0.0
    }
    for strategy in strategies:
        if ( result["max_value"] < strategy[0].broker.getvalue()):
            result["max_value"] = strategy[0].broker.getvalue()
            result["pfast"] = strategy[0].params.pfast
            result["pslow"] = strategy[0].params.pslow
    return result

# 主函数
def main():

    print('加载数据...')
    df = get_stock_data()
    print('加载完成！')

    print('配置数据...')
    data = bt.feeds.PandasData(dataname=df, datetime=1,
                           open=2, high=3, low=4, close=5, volume=9, openinterest=-1)
    cerebro = bt.Cerebro()
    cerebro.optstrategy(Test, pfast=range(1, 19), pslow=range(20, 40))
    cerebro.addsizer(bt.sizers.PercentSizer, percents = 100) 
    cerebro.adddata(data)  # 添加数据源
    print('配置完成！')

    print('运行策略：')
    strategies = cerebro.run(optreturn=False)  # 运行策略
    result = get_result(strategies)
    print('最优参数：pfast: %2d pslow %2d 最终收益： %.2f' %
          (result["pfast"], result["pslow"], result["max_value"]))
    print('运行完成！')

# 运行主函数
if __name__ == '__main__':
    main()