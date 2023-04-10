from flask import Flask, render_template, request, session, redirect
import strategies as st
from backtest import run_backtest
import matplotlib
matplotlib.use('Agg')


app = Flask(__name__)
app.secret_key = '21032101dFYP'

STRATEGY_MAP = {
    '20_50_MA_Crossover': st.MovingAverageCrossover,
    '12_26_MACD' : st.MACDGoldenCrossStrategy,
    'Bollinger_Band' : st.BollingerBandsMA
}



@app.route('/', methods=['GET'])
def index():
    error_message = session.pop('error_message', None)
    return render_template('index.html', error_message=error_message)

@app.route('/result', methods=['POST'])
def result():
    symbol = request.form['symbol']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    commission = float(request.form['commission'])
    selected_strategy = request.form['selected_strategy']
    initial_cash = float(request.form['initial_cash'])
    moving_average_type = request.form['moving_average_type']
    strategy = STRATEGY_MAP[selected_strategy]

    
    # perform backtesting
    error = False
    try:
        result = run_backtest(strategy, symbol, start_date,
                            end_date, commission, initial_cash, moving_average_type)
    except IndexError:
        error = True
        session['error_message'] = 'There was an error during backtesting. Please try other period. or make sure your input is correct. In cloud be the stock have not this date range'

    if error:
        return redirect('/')
    
    if result['NoTransactions'] == True:
        error = True
        session['error_message'] = 'There is no any trade during the backtesting period.'
        return redirect('/')
    
    # return the result page with the backtesting result data
    return render_template('result.html',
                           profit=result['profit'],
                           end_portfolio_value=result['end_portfolio_value'],
                           sharpe_ratio=result['sharpe_ratio'],
                           drawdown=result['drawdown'],
                           returns=result['returns'],
                           sqn=result['sqn'],
                           transactions=result['transactions'],
                           trade_analyzer_data=result['trade_analyzer_data'],
                           symbol=symbol,
                           start_date=start_date,
                           end_date=end_date,
                           commission=commission,
                           selected_strategy=selected_strategy,
                           initial_cash=initial_cash,
                           moving_average_type=moving_average_type,
                           )


@app.route('/chart')
def chart():
    return render_template("chart.html")

@app.route('/quantstat')
def quantstat():
    return render_template("stats.html")


if __name__ == '__main__':
    app.run(debug=True)
