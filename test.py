import tushare as ts
import pandas as pd
import backtrader as bt
import random

def get_stock_data():
    ts.set_token('294b16d453c18ec44877c0753586866779d1956f463b49a6e3c5b6d8')
    pro = ts.pro_api()
    df = pro.daily(ts_code='601012.SH', start_date='20000101')
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df = df.sort_values('trade_date')
    return df

class Test(bt.Strategy):

    def __init__(self):
        self.isPositive = 0

    def next(self):

        self.isPositive = random.randint(0,1)
        print('%s 硬币：%s 持仓：%.2f' % (self.datas[0].datetime.date(0), bool(self.isPositive), self.position.size))
        
        if self.position:
            if not self.isPositive:
                self.close()
        elif self.isPositive:
            self.buy()

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                print('买入, %.2f' % order.executed.price)
            elif order.issell():
                print('卖出, %.2f' % order.executed.price)
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            print('交易取消')

        # Write down: no pending order
        self.order = None

# 主函数
def main():

    print('每天投掷硬币，以贵州茅台日线为标的，\n如果正面则以开盘价买入或持仓，如果反面则以开盘价卖出或者空仓')

    print('加载数据...')
    df = get_stock_data()
    print('加载完成！')

    print('配置数据...')
    data = bt.feeds.PandasData(dataname=df, datetime=1,
                           open=2, high=3, low=4, close=5, volume=9, openinterest=-1)
    cerebro = bt.Cerebro()
    cerebro.broker.set_coc(True)
    cerebro.addstrategy(Test)
    cerebro.addsizer(bt.sizers.PercentSizer, percents = 100) 
    cerebro.adddata(data)  # 添加数据源
    print('配置完成！')

    print('运行策略：')
    print('启动资金: %.2f' % cerebro.broker.getvalue())
    cerebro.run()  # run it all
    cerebro.plot()
    print('最终收益: %.2f' % cerebro.broker.getvalue())
    print('运行完成！')

# 运行主函数
if __name__ == '__main__':
    main()