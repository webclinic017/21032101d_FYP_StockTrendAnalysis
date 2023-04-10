import json
import backtrader as bt
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from plotly.subplots import make_subplots
import plotly.io as pio
import strategies as st
import os
import quantstats as qs
import warnings
import shutil

warnings.filterwarnings("ignore")
def extract_trade_analyzer_data(ta):
    def exists(obj, *keys):
        for key in keys:
            if key not in obj:
                return False
            obj = obj[key]
        return True
    totalTrade = ta.total.total if exists(ta, "total", "total") else None
    openTotal = ta.total.open if exists(ta, "total", "open") else None
    closedTotal = ta.total.closed if exists(ta, "total", "closed") else None
    wonTotal = ta.won.total if exists(ta, "won", "total") else None
    lostTotal = ta.lost.total if exists(ta, "lost", "total") else None

    streakWonLongest = (
        ta.streak.won.longest if exists(
            ta, "streak", "won", "longest") else None
    )
    streakLostLongest = (
        ta.streak.lost.longest if exists(
            ta, "streak", "lost", "longest") else None
    )

    pnlNetTotal = ta.pnl.net.total if exists(
        ta, "pnl", "net", "total") else None
    pnlNetAverage = (
        ta.pnl.net.average if exists(ta, "pnl", "net", "average") else None
    )
    if pnlNetTotal is not None:
        pnlNetTotal =  round(pnlNetTotal, 2)
        
    if pnlNetAverage is not None:
        pnlNetAverage = round(pnlNetAverage, 2)
    trade_analyzer_data = [
        {"label": "Total Trade", "value": totalTrade},
        {"label": "Open Total", "value": openTotal},
        {"label": "Sell Total", "value": closedTotal},
        {"label": "Won case", "value": wonTotal},
        {"label": "Lost case", "value": lostTotal},
        {"label": "Streak Won Longest", "value": streakWonLongest},
        {"label": "Streak Lost Longest", "value": streakLostLongest},
        {"label": "PnL Net Total", "value": pnlNetTotal},
        {"label": "PnL Net Average", "value":pnlNetAverage},
    ]

    return trade_analyzer_data


def get_buy_and_sell_markers(transactions_json):
    transactions = json.loads(transactions_json)
    buy_markers = []
    sell_markers = []
    for transaction in transactions:
        date = datetime.strptime(transaction['date'], '%Y-%m-%d %H:%M:%S')
        price = transaction['price']
        size = transaction['size']

        if size > 0:
            buy_markers.append({'Date': date, 'Price': price})
        elif size < 0:
            sell_markers.append({'Date': date, 'Price': price})
    buy_markers_df = pd.DataFrame(buy_markers).set_index('Date')
    sell_markers_df = pd.DataFrame(sell_markers).set_index('Date')
    return buy_markers_df, sell_markers_df


def plot_candlestick_chart(data_feed_df, buy_markers_df, sell_markers_df, ma_df, strategy):
    fig = make_subplots(rows=2, cols=1, row_heights=[
                        0.7, 0.3], vertical_spacing=0.1)
    # Add candlestick trace
    fig.add_trace(go.Candlestick(x=data_feed_df.index,
                                 open=data_feed_df['Open'],
                                 high=data_feed_df['High'],
                                 low=data_feed_df['Low'],
                                 close=data_feed_df['Close'],
                                 name='candlestick'), row=1, col=1)

    # Add volume trace
    fig.add_trace(go.Bar(x=data_feed_df.index,
                  y=data_feed_df['Volume'], name='Volume', marker_color='rgba(0,0,255,0.3)'), row=2, col=1)

    # Set the y-value for buy and sell markers using the 'High' column and add an offset

    buy_markers_df['MarkerY'] = buy_markers_df['Price']
    sell_markers_df['MarkerY'] = sell_markers_df['Price']
    
    # Add buy markers trace
    fig.add_trace(go.Scatter(x=buy_markers_df.index, y=buy_markers_df['MarkerY'], mode='markers',
                             marker_symbol='triangle-up', marker_size=15, marker_color='green', name='Buy'), row=1, col=1)

    # Add sell markers trace
    fig.add_trace(go.Scatter(x=sell_markers_df.index, y=sell_markers_df['MarkerY'], mode='markers',
                             marker_symbol='triangle-down', marker_size=15, marker_color='red', name='Sell'), row=1, col=1)
    
    
    if strategy == st.MovingAverageCrossover:
        fig.add_trace(go.Scatter(x=ma_df.index, y=ma_df['fast_ma'], mode='lines',
                                line=dict(width=1, color='blue'), name='Fast MA'), row=1, col=1)
        fig.add_trace(go.Scatter(x=ma_df.index, y=ma_df['slow_ma'], mode='lines',
                                line=dict(width=1, color='red'), name='Slow MA'), row=1, col=1)

    elif strategy == st.BollingerBandsMA:
        fig.add_trace(go.Scatter(x=ma_df.index, y=ma_df['ma'], mode='lines',
                                line=dict(width=1, color='blue'), name='MA'), row=1, col=1)
        fig.add_trace(go.Scatter(x=ma_df.index, y=ma_df['bb_top'], mode='lines',
                                line=dict(width=1, color='red'), name='BB Top'), row=1, col=1)
        fig.add_trace(go.Scatter(x=ma_df.index, y=ma_df['bb_bot'], mode='lines',
                                line=dict(width=1, color='red'), name='BB Bottom'), row=1, col=1)
    elif strategy == st.MACDGoldenCrossStrategy:
        # Add MACD line trace
        fig.add_trace(go.Scatter(x=ma_df.index, y=ma_df['macd'], mode='lines',
                                line=dict(width=1, color='blue'), name='MACD'), row=1, col=1)
        # Add Signal line trace
        fig.add_trace(go.Scatter(x=ma_df.index, y=ma_df['signal'], mode='lines',
                                line=dict(width=1, color='red'), name='Signal'), row=1, col=1)



    fig.update_layout(title='Candlestick Chart',
                      yaxis_title='Price')

    fig.update_xaxes(range=[data_feed_df.index.min(), data_feed_df.index.max()])

    pio.write_html(fig, 'templates/chart.html')


def run_backtest(strategy, symbol, start_date, end_date, commission, initial_cash, moving_average_type):

    cerebro = bt.Cerebro()

    # Get stock data
    yf.pdr_override()
    data = yf.download(symbol, start=start_date, end=end_date)

    # Add data to Cerebro
    data_feed = bt.feeds.PandasData(dataname=data)
    cerebro.adddata(data_feed)


    
    # Add strategy
    cerebro.addstrategy(strategy, moving_average_type=moving_average_type)

    # Add indicators


    # Set initial cash and commission
    cerebro.broker.setcash(initial_cash)
    cerebro.broker.setcommission(commission=commission)

    # Add analyzers
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')
    cerebro.addanalyzer(bt.analyzers.Transactions, _name='txn')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='ta')
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
    # Add observers
    cerebro.addobserver(bt.observers.BuySell)
    cerebro.addobserver(bt.observers.Value)

    start_portfolio_value = cerebro.broker.getvalue()
    
    # Run the backtest
    results = cerebro.run()

    # get transaction data
    transactions = results[0].analyzers.txn.get_analysis()
    transactions_dict = []

    for k, v in transactions.items():
        if len(v[0]) >= 5:
            transaction = {
                'date': str(k),
                'size': v[0][0],
                'price': v[0][1],
                'symbol': symbol,
                'value': v[0][4],

            }
        else:
            print("Skipping incomplete transaction:", k, v)
            continue

        transactions_dict.append(transaction)

    transactions_json = json.dumps(transactions_dict)

    if transactions_json == '[]':
        return {'NoTransactions': True}
    # Get Trade Analyzer data
    trade_analyzer_data = extract_trade_analyzer_data(
        results[0].analyzers.ta.get_analysis())
    trade_analyzer_data_json = json.dumps(trade_analyzer_data)

    # Get the buy and sell markers
    data_feed_df = data
    # Extract buy and sell transactions from transactions_dict
    buy_markers_df, sell_markers_df = get_buy_and_sell_markers(
        transactions_json)

    # get ma data
    strategy_instance = results[0]
    if strategy == st.MovingAverageCrossover:
        fast_ma, slow_ma = strategy_instance.get_moving_averages()  
        ma_df = pd.DataFrame({'fast_ma': fast_ma, 'slow_ma': slow_ma}, index=data_feed_df.index)
        # Plot the Candlestick chart with buy and sell markers
        plot_candlestick_chart(data_feed_df, buy_markers_df, sell_markers_df, ma_df, strategy)
        
    elif strategy == st.BollingerBandsMA:
        ma, bb_top, bb_bot = strategy_instance.get_bollinger_bands()
        ma_df = pd.DataFrame({'ma': ma, 'bb_top': bb_top, 'bb_bot': bb_bot}, index=data_feed_df.index)
        plot_candlestick_chart(data_feed_df, buy_markers_df, sell_markers_df, ma_df, strategy)
        
    elif strategy == st.MACDGoldenCrossStrategy:
        macd, signal = strategy_instance.get_macd()
        macd_df = pd.DataFrame({'macd': macd, 'signal': signal}, index=data_feed_df.index)
        plot_candlestick_chart(data_feed_df, buy_markers_df, sell_markers_df, macd_df, strategy)
    
    """
    elif strategy == st.VCPStrategy:
        ma50, ma150,ma200 = strategy_instance.get_moving_averages()  
        ma_df = pd.DataFrame({'ma50': ma50, 'ma150': ma150,'ma200': ma200}, index=data_feed_df.index)
        # Plot the Candlestick chart with buy and sell markers
        plot_candlestick_chart(data_feed_df, buy_markers_df, sell_markers_df, ma_df, strategy)
    """
    result_analysis = results[0].analyzers.returns.get_analysis()['rtot']
    if result_analysis == float('-inf'):
        result_analysis = -100
    else:
        result_analysis = round(result_analysis, 5) *100

    shape_ratio = results[0].analyzers.sharpe_ratio.get_analysis()['sharperatio']
    if shape_ratio != None:
        shape_ratio = round(shape_ratio, 2)
    else:
        shape_ratio = 0
        

     
    # Download SPY data for compare
#    spy_data = yf.download("SPY", start=start_date, end=end_date)

    # Calculate daily returns
#    spy_returns = spy_data['Adj Close'].pct_change().dropna()

    # Convert the index to a timezone-naive datetime index
#    spy_returns.index = spy_returns.index.tz_localize(None)  
    
    #get quantstats report
#    portfolio = results[0].analyzers.getbyname('pyfolio')
#    returns, positions, transactions, gross_lev = portfolio.get_pf_items()
#    returns.index = returns.index.tz_convert(None)

# Generate quantstats report 
#    qs.reports.html(returns, output='templates/', title='QuantStats Report (Strategy VS SPY)', benchmark=spy_returns)

    # Remove the existing file if it exists
#    if os.path.exists('templates/stats.html'):
#        os.remove('templates/stats.html')

    # Move the new file to the desired location and rename it
#    shutil.move('quantstats-tearsheet.html', 'templates/stats.html')


    return {
        'profit': round(cerebro.broker.getvalue() - start_portfolio_value, 2),
        'end_portfolio_value': round(cerebro.broker.getvalue(), 2),
        'sharpe_ratio': shape_ratio,
        'drawdown': round(results[0].analyzers.drawdown.get_analysis().max.drawdown, 2),
        'returns': result_analysis,
        'sqn': round(results[0].analyzers.sqn.get_analysis()['sqn'], 2),
        'transactions': transactions_json,
        'trade_analyzer_data': trade_analyzer_data_json,
        'NoTransactions' : False
    }
