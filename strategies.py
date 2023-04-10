import backtrader as bt
import numpy as np
from scipy.stats import linregress


def get_moving_average(moving_average_type):
    if moving_average_type == 'SMA':
        ma = bt.indicators.SimpleMovingAverage
    elif moving_average_type == 'EMA':
        ma = bt.indicators.ExponentialMovingAverage
    elif moving_average_type == 'WMA':
        ma = bt.indicators.WeightedMovingAverage
    elif moving_average_type == 'HVIDYA':
        ma = HVIDYAIndicator
    else:
        raise ValueError(
            f"Invalid moving average type: {moving_average_type}")
    return ma

class HVIDYAIndicator(bt.Indicator):
    params = (
        ('period', 20),
        ('alpha', 1),
    )
    lines = ('hvidya',)

    def __init__(self):
        self.addminperiod(self.params.period)
        super(HVIDYAIndicator, self).__init__()

        # Calculate weighted moving averages for the period
        self.wma = bt.indicators.WeightedMovingAverage(self.data, period=self.params.period)

    def next(self):
        # Get the last 'period' values of the data
        data_array = self.data.get(size=self.params.period)

        # Ensure that the data_array has enough data points before calculating the historical volatility
        if len(data_array) < self.params.period:
            return

        close = self.data[-1]

        data_np = np.array(data_array)

        # Calculate the historical volatility
        returns = np.log(data_np[1:] / data_np[:-1])
        hv = np.std(returns) * np.sqrt(self.params.period)

        # Update hvidya line
        self.lines.hvidya[0] = self.wma[0] * (1 - self.params.alpha * hv) + close * (self.params.alpha * hv)



#MA CrossOver
class MovingAverageCrossover(bt.Strategy):
    params = (
        ('fast_period', 20),
        ('slow_period', 50),
        ('moving_average_type', ''),
    )

    def __init__(self):
        ma_fast = get_moving_average(self.params.moving_average_type)
        ma_slow = get_moving_average(self.params.moving_average_type)

        self.fast_ma = ma_fast(self.data.close, period=self.params.fast_period)
        self.slow_ma = ma_slow(self.data.close, period=self.params.slow_period)

    def next(self):
        order_size = 100
       
        #20 ma('fast_ma') cross above 50 ma (slow_ma)
        if self.fast_ma[0] > self.slow_ma[0] and self.fast_ma[-1] <= self.slow_ma[-1]:
                self.buy(size=order_size)
        
    
        elif self.fast_ma[0] < self.slow_ma[0] and self.fast_ma[-1] >= self.slow_ma[-1]:
                self.close()    

      
    def get_moving_averages(self):
        return self.fast_ma.array, self.slow_ma.array


#MACD
class MACDGoldenCrossStrategy(bt.Strategy):
    params = (
        ('fast_period', 12),
        ('slow_period', 26),
        ('signal_period', 9),
        ('moving_average_type', ''),
    )

    def __init__(self):
        ma = get_moving_average(self.params.moving_average_type)
        self.macd = bt.indicators.MACD(
            self.data.close,
            period_me1=self.params.fast_period,
            period_me2=self.params.slow_period,
            period_signal=self.params.signal_period,
            movav=ma,
        )

    def next(self):
        order_size = 100

            # Buy signal: current MACD line value is greater than the signal line value, and the previous MACD line value was less than the previous signal line value
        if self.macd.lines.macd[0] > self.macd.lines.signal[0] and self.macd.lines.macd[-1] <= self.macd.lines.signal[-1]:
                self.buy(size=order_size)     
            # Sell signal: current MACD line value is less than the signal line value, and the previous MACD line value was greater than the previous signal line value
        elif self.macd.lines.macd[0] < self.macd.lines.signal[0] and self.macd.lines.macd[-1] >= self.macd.lines.signal[-1]:
                self.close()

    def get_macd(self):
        return self.macd.lines.macd.array, self.macd.lines.signal.array

# Bollinger Bands
class BollingerBandsMA(bt.Strategy):
    params = (
        ('ma_period', 20),
        ('moving_average_type', ''),
        ('bb_period', 20),
        ('bb_std_dev', 2),
    )

    def __init__(self):
        ma = get_moving_average(self.params.moving_average_type)

        self.ma = ma(self.data.close, period=self.params.ma_period)
        self.bb = bt.indicators.BollingerBands(
            self.data, period=self.params.bb_period, devfactor=self.params.bb_std_dev)

    def next(self):
        order_size = 100
        
            # Buys when the closing price is above the lower Bollinger Band and the moving average
        if self.data.close[0] > self.bb.lines.bot[0] and self.data.close[0] > self.ma[0]:
                self.buy(size=order_size)
            # Sells when the closing price is below the upper Bollinger Band and the moving average
        elif self.data.close[0] < self.bb.lines.top[0] and self.data.close[0] < self.ma[0]:
                self.close()

    def get_bollinger_bands(self):
        return self.ma.array, self.bb.lines.top.array, self.bb.lines.bot.array












#VCP
""" VCP Strategy because of the vcp condition is too hard to fullfill if only testing one stock, so i decided to remove it from the web app
class VCPStrategy(bt.Strategy):
    params = (
        ("moving_average_type", "SMA"),
        ('trading_day_for_month', 21),
    )

    def __init__(self):
        if self.params.moving_average_type == 'SMA':
            ma = bt.indicators.SimpleMovingAverage
        elif self.params.moving_average_type == 'EMA':
            ma = bt.indicators.ExponentialMovingAverage
        elif self.params.moving_average_type == 'WMA':
            ma = bt.indicators.WeightedMovingAverage
        elif self.params.moving_average_type == 'HVIDYA':
            ma = HVIDYAIndicator

        self.ma50 = ma(self.data.close, period=50)
        self.ma150 = ma(self.data.close, period=150)
        self.ma200 = ma(self.data.close, period=200)

        self.slope_200 = SlopeIndicator(self.ma200, period=20)

        self.high52 = bt.indicators.Highest(self.data.close, period=5*52)
        self.low52 = bt.indicators.Lowest(self.data.close, period=5*52)

        # Buy Conditions
        buy_conditions = bt.And(
            self.data.close > self.ma200,
            self.data.close > self.ma150,
            self.ma150 > self.ma200,
            self.slope_200 > 0,
            self.ma50 > self.ma150,
            self.ma50 > self.ma200,
            self.data.close > self.ma50,
            (self.data.close - self.low52) / self.low52 > 0.3,
            (self.data.close - self.high52) / self.high52 > -0.15,
            (self.data.close - self.high52) / self.high52 < 0.15,
            # Condition 11 (RS_Rating) will be calculated in the next method
        )

        # Sell conditions
        sell_conditions = bt.And(
            self.data.close < self.ma200,
            self.slope_200 <= 0,
            self.data.close <= self.low52,
            self.data.close < self.data.close(-1),  # Lower low
            self.data.high < self.data.high(-1),  # Lower high
            self.ma50 < self.ma200,
        )

        self.buy_signal = bt.If(buy_conditions, 1, 0)
        self.sell_signal = bt.If(sell_conditions, -1, 0)

    def next(self):
            # Calculate RS_Rating (Condition 11) and update the buy signal
            rs_rating = (
                ((self.data.close[-1] - self.data.close[-(self.params.trading_day_for_month * 3 + 1)]) / self.data.close[-(self.params.trading_day_for_month * 3 + 1)]) * 0.4 +
                ((self.data.close[-1] - self.data.close[-(self.params.trading_day_for_month * 6 + 1)]) / self.data.close[-(self.params.trading_day_for_month * 6 + 1)]) * 0.2 +
                ((self.data.close[-1] - self.data.close[-(self.params.trading_day_for_month * 9 + 1)]) / self.data.close[-(self.params.trading_day_for_month * 9 + 1)]) * 0.2 +
                ((self.data.close[-1] - self.data.close[-(self.params.trading_day_for_month * 12 + 1)]) / self.data.close[-(self.params.trading_day_for_month * 12 + 1)]) * 0.2
            )
            self.buy_signal[0] = self.buy_signal[0] * (rs_rating > 0.70)

            if not self.position:
                if self.buy_signal[0] == 1:
                    self.buy()
            else:
                if self.sell_signal[0] == -1:
                    self.sell()

                
    def get_moving_averages(self):
            return self.ma50.array, self.ma150.array, self.ma200.array
                
class SlopeIndicator(bt.Indicator):
    lines = ('slope',)
    params = (('period', 20),)

    def __init__(self):
        self.addminperiod(self.params.period)

    def next(self):
        y = self.data.get(size=self.params.period)
        
        if len(y) > 0:
            x = np.arange(len(y))
            slope, intercept, r_value, p_value, std_err = linregress(x, y)
            self.lines.slope[0] = slope
        else:
            self.lines.slope[0] = np.nan
"""