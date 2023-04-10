
import numpy as np
import pandas as pd
import yfinance as yf
from tqdm import tqdm
import concurrent.futures
from finviz.screener import Screener
import joblib 
from scipy.stats import linregress

pd.set_option('mode.chained_assignment', None)

def slope_reg(arr):
    y = np.array(arr)
    x = np.arange(len(y))
    slope, intercept, r_value, p_value, std_err = linregress(x,y)
    return slope

def Original_VCP_filter(df):
    df['SMA_50'] = df['Close'].rolling(window = 50).mean()
    df['SMA_150'] = df['Close'].rolling(window = 150).mean()
    df['SMA_200'] = df['Close'].rolling(window = 200).mean()
    df['SMA_slope_200'] = df['SMA_200'].rolling(window = 20).apply(slope_reg)
    df['52_week_high'] = df['Close'].rolling(window = 5*52).max()
    df['52_week_low'] = df['Close'].rolling(window = 5*52).min()
    
    # Trend Template criteria for the stage 2 uptrend in VCP
    # Condition 1: The current stock price is above both the 150-day (30-week) and the 200-day (40-week) moving average price lines.
    df['Condition1'] = (df['Close'] > df['SMA_200']) & (df['Close'] > df['SMA_150'])

    # Condition 2: The 150-day moving average is above the 200-day moving average.
    df['Condition2'] = df['SMA_150'] > df['SMA_200']

    # Condition 3: The 200-day moving average line is trending up for at least 1 month (preferably 4–5 months minimum in most cases).
    df['Condition3'] = df['SMA_slope_200'] >0.0
                        
    # Condition 4: The 50-day (10-week) moving average is above both the 150-day and 200-day moving averages.
    df['Condition4'] = (df['SMA_50'] > df['SMA_150']) & (df['SMA_50'] > df['SMA_200'])
    
    # Condition 5: The current stock price is trading above the 50-day moving average.
    df['Condition5'] = df['Close'] > df['SMA_50']

    # Condition 6: The current stock price is at least 30 percent above its 52-week low.
    df['Condition6'] = (df['Close'] - df['52_week_low']) / df['52_week_low'] > 0.3

    # Condition 7: The current stock price is within at least 25 percent of its 52-week high (the closer to a new high the better
    df['Condition7'] = ((df['Close'] - df['52_week_high']) / df['52_week_high'] > -0.15) & ((df['Close'] - df['52_week_high']) / df['52_week_high'] < 0.15) 

    # The relative strength ranking is no less than 70, and preferably in the 80s or 90s
    # Because it is difficult to obtain RS Ranking from ibd, the formula with the effect of RS Ranking is applied (weighting : 3 month = 40%, 6 month = 20%, 9 month = 20%, 12 month = 20%)
    trading_day_for_month = 21
    df['RS_Rating'] = ((df['Close'] - df['Close'].shift(periods = trading_day_for_month*3))/df['Close'].shift(periods = trading_day_for_month*3))* 0.4 + ((df['Close'] - df['Close'].shift(periods = trading_day_for_month*6))/df['Close'].shift(periods = trading_day_for_month*6))* 0.2 + ((df['Close'] - df['Close'].shift(periods = trading_day_for_month*9))/df['Close'].shift(periods = trading_day_for_month*9))* 0.2 + ((df['Close'] - df['Close'].shift(periods = trading_day_for_month*12))/df['Close'].shift(periods = trading_day_for_month*12))* 0.2
    
    df['Condition8'] = df['RS_Rating'] > 0.89

    df['isVCP'] = df[['Condition1','Condition2','Condition3','Condition4','Condition5','Condition6','Condition7','Condition8',]].all(axis='columns')

    return df[['Close','isVCP']]
    
def VCP_backtesting(df_input):
    df = pd.DataFrame()
    df['isVCP'] = df_input['isVCP']
    # Result_1 : Sell after 1 day, Result_3 : Sell after 3 days, Result_5 : Sell after 5 days, Result_7 : Sell after 7 days, Result_20 : Sell after 20 days
    df['Result_1'] = df_input['Close'].pct_change(periods = 1).shift(periods = -1)
    df['Result_3'] = df_input['Close'].pct_change(periods = 3).shift(periods = -3)
    df['Result_5'] = df_input['Close'].pct_change(periods = 5).shift(periods = -5)
    df['Result_7'] = df_input['Close'].pct_change(periods = 7).shift(periods = -7)
    df['Result_20'] = df_input['Close'].pct_change(periods = 20).shift(periods = -20)
    vcp_date = df[df['isVCP'] == True]
    return vcp_date

def VCPscan_Pack(stock_symbol):
    ticker = yf.Ticker(stock_symbol)
    ticker_history = ticker.history(start="2011-8-15", end="2015-5-18")
    data = Original_VCP_filter(ticker_history) 
    df = pd.DataFrame(data)
    if df.empty :
            return {'stock': None, 'analysis': None}
    if True in df['isVCP'].values:
            backtestData = VCP_backtesting(data) 
            return {'stock': stock_symbol, 'analysis': backtestData}
    return {'stock': stock_symbol, 'analysis': None}

def getStockListFromFinvizq(filters):
    stock_ls = Screener(filters=filters, table = 'Performance', order = 'Price')
    return stock_ls

def scanStockByFinviz():
    filters =  ['ipodate_more5']
    stock_ls = getStockListFromFinvizq(filters)
    stock_tb = pd.DataFrame(stock_ls.data)
    stock_ls = stock_tb['Ticker'].tolist()
    print('Total Scaned stock number  : ', len(stock_ls))
    return stock_ls
    
   
def multi_threading_scan(ticker_ls):
    print('Start OriginalVCP scanning')
    with concurrent.futures.ProcessPoolExecutor(max_workers = 12) as executor:
        data_ls =  list(tqdm(executor.map(VCPscan_Pack, ticker_ls), total = len(ticker_ls)))
    total_stock_get =len(data_ls) - data_ls.count({'stock': None, 'analysis': None})
    print(data_ls.count({'stock': None, 'analysis': None}))
    print('Total stock number : ', total_stock_get)
    print('Finish OriginalVCP scanning')
    return data_ls

    
if __name__ ==  '__main__':
    joblib.dump(multi_threading_scan(scanStockByFinviz()), 'Original_VCP_scan_result.pkl')
    