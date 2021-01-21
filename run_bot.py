# To differentiate between time-time and datetime-time
import time as true_time
import pprint
import pathlib
import operator
import pandas as pd

from datetime import datetime
from datetime import timedelta
from configparser import ConfigParser

from bot.bot import Bot
from bot.indicators import Indicators

# Grab the config file values.
config = ConfigParser()
config.read('configs/config.ini')

CLIENT_ID = config.get('main', 'CLIENT_ID')
REDIRECT_URI = config.get('main', 'REDIRECT_URI')
CREDENTIALS_PATH = config.get('main', 'JSON_PATH')
ACCOUNT_NUMBER = config.get('main', 'ACCOUNT_NUMBER')

# Initialize the robot.
trading_robot = Bot(
    client_id=CLIENT_ID,
    redirect_uri=REDIRECT_URI,
    crendentials_path=CREDENTIALS_PATH,
    trading_account=ACCOUNT_NUMBER,
    paper_trading=True
)

# Create a new portfolio.
trading_robot_portfolio = trading_robot.create_portfolio()

# Add multiple positions to our portfolio.
multi_position = [
    {
        'asset_type': 'equity',
        'quantity': 79,
        'purchase_price': 24.19,
        'symbol': 'WFC',
        'purchase_date': '2020-05-06'
    },
    {
        'asset_type': 'equity',
        'quantity': 4,
        'purchase_price': 96.44,
        'symbol': 'DVY',
        'purchase_date': '2020-11-25'
    }
]

# Add those positions to the Portfolio.
new_positions = trading_robot.portfolio.add_positions(positions=multi_position)

# Add a single position to the portfolio.
trading_robot.portfolio.add_position(
    symbol='ZSAN',
    quantity=55,
    purchase_price=0.91,
    asset_type='equity',
    purchase_date='2021-01-12'
)
pprint.pprint(trading_robot.portfolio.positions)

# Check to see if regular market is open.
if trading_robot.regular_market_open:
    pprint.pprint(trading_robot.grab_current_quotes())
else:
    print('Regular Market Not Open')

# Check to see if Pre market is open.
if trading_robot.pre_market_open:
    print('Pre Market Open')
else:
    print('Pre Market Not Open')

# Check to see if Post market is open.
if trading_robot.post_market_open:
    print('Post Market Open')
else:
    print('Post Market Not Open')

# Grab the current quotes in our portfolio.
current_quotes = trading_robot.grab_current_quotes()
#pprint.pprint(current_quotes)

# Define our date range.
start_date = datetime.today()
end_date = start_date - timedelta(days=30)

# Grab the historical prices.
historical_prices = trading_robot.grab_historical_prices(
    start=end_date,
    end=start_date,
    bar_size=1,
    bar_type='minute'
)

# Convert the data into a StockFrame.
stock_frame = trading_robot.create_stock_frame(
    data=historical_prices['aggregated']
)

# Print the head of the StockFrame.
#pprint.pprint(stock_frame.frame.head(n=20))

# Create a new Trade Object.
new_trade = trading_robot.create_trade(
    trade_id='long_msft',
    enter_or_exit='enter',
    long_or_short='long',
    order_type='lmt',
    price=150.0
)

# Make it Good Till Cancel.
new_trade.good_till_cancel(cancel_time=datetime.now() + timedelta(minutes=90))

# Change the session
new_trade.modify_session(session='am')

# Add an Order Leg.
new_trade.instrument(
    symbol='MSFT',
    quantity=2,
    asset_type='EQUITY'
)

# Add a Stop Loss Order with the Main Order.
new_trade.add_stop_loss(
    stop_size=.10,
    percentage=False
)

# Print out the order.
pprint.pprint(new_trade.order)

# Create a new indicator client.
indicator_client = Indicators(price_data_frame=stock_frame)

# Add the RSI indicator.
indicator_client.rsi(period=14)

# Add a 200-day simple moving average.
indicator_client.sma(period=200)

# Add a 200-day simple moving average.
indicator_client.sma(period=50)

# Add a 50-day exponential moving average.
indicator_client.ema(period=50)

# Add a signal to check for.
indicator_client.set_indicator_signals(
    indicator='rsi',
    buy=40.0,
    sell=20.0,
    condition_buy=operator.ge,
    condition_sell=operator.le
)

# Define a trade dictionary.
trade_dict = {
    'MSFT': {
        'trade_func': trading_robot.trades['long_msft'],
        'trade_id': trading_robot.trades['long_msft'].trade_id
    }
}

while True:
    # Grab the latest bar.
    latest_bars = trading_robot.get_latest_bar()

    # Add those bars to the StockFrame.
    stock_frame.add_rows(data=latest_bars)

    # Refresh the indicators.
    indicator_client.refresh()

    print('=' * 50)
    print('Current StockFrame')
    print('-' * 50)
    print(stock_frame.symbol_groups.tail())
    print('-' * 50)
    print('')

    # Check for signals.
    signals = indicator_client.check_signals()

    # Execute Trades.
    trading_robot.execute_signals(signals=signals, trades_to_execute=trade_dict)

    # Grab the last bar, keep in mind this is after adding the new rows.
    last_bar_timestamp = trading_robot.stock_frame.frame.tail(n=1).index.get_level_values(1)

    # Wait till the next bar.
    trading_robot.wait_till_next_bar(last_bar_timestamp=last_bar_timestamp)
